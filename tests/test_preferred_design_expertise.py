from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from frontend_design_director.codex_backend import CodexCLIBackend
from frontend_design_director.collaboration import (
    CapabilityStatus,
    CollaborationMode,
    ResourceKind,
    assemble_expert_team,
    build_capability_registry,
    load_design_expertise_preferences,
    preferred_design_expertise_report,
    run_phase_collaboration,
)
from frontend_design_director.auditing import _preferred_design_synthesis, run_codex_audit
from frontend_design_director.discovery import discover_skills


def _codex_state(*, images: bool = True) -> dict[str, object]:
    return {
        "cli": {
            "installed": True,
            "authenticated": True,
            "auth_mode": "chatgpt_plan",
            "codex_exec_supported": True,
            "structured_output_supported": True,
            "image_input_supported": images,
        },
        "plugins": [],
        "mcp_servers": [],
    }


class PreferredSkillDiscoveryTests(unittest.TestCase):
    def _write_skill(self, root: Path, folder: str, name: str, description: str) -> Path:
        skill_dir = root / ".agents" / "skills" / folder
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: {description}\n---\n\nAdvisory instructions.\n",
            encoding="utf-8",
        )
        return skill_dir / "SKILL.md"

    def test_discovery_records_fingerprint_scope_and_actual_commands(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            impeccable = self._write_skill(root, "impeccable", "impeccable", "Frontend design review and polish.")
            scripts = impeccable.parent / "scripts"
            scripts.mkdir()
            (scripts / "command-metadata.json").write_text(json.dumps({"audit": {}, "polish": {}}), encoding="utf-8")
            taste = self._write_skill(root, "design-taste-frontend", "design-taste-frontend", "Frontend art direction and responsive review.")
            taste_scripts = taste.parent / "scripts"
            taste_scripts.mkdir()
            (taste_scripts / "draw.mjs").write_text("// not executed", encoding="utf-8")

            with patch("frontend_design_director.discovery.skill_roots", return_value=[root / ".agents" / "skills"]):
                skills, errors = discover_skills(root)

        self.assertFalse(any(str(root) in item.get("path", "") for item in errors))
        by_name = {item["name"]: item for item in skills}
        self.assertRegex(by_name["impeccable"]["content_sha256"], r"^[0-9a-f]{64}$")
        self.assertEqual(by_name["impeccable"]["available_commands"], ["audit", "polish"])
        self.assertIn("Node.js >=22", " ".join(by_name["design-taste-frontend"]["required_dependencies"]))
        self.assertNotIn("inspect.mjs", by_name["design-taste-frontend"]["available_commands"])
        self.assertEqual(by_name["design-taste-frontend"]["installation_scope"], "project")

    def test_preferences_allow_project_override_and_user_disable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = root / ".frontend-design-director" / "config.toml"
            config.parent.mkdir()
            config.write_text(
                "[design_expertise]\n"
                "enabled = true\n"
                "[design_expertise.impeccable]\n"
                "enabled = false\n",
                encoding="utf-8",
            )
            with patch.dict("os.environ", {"XDG_CONFIG_HOME": str(root / "user-config")}):
                preferences = load_design_expertise_preferences(root)

        self.assertFalse(preferences["prefer_impeccable"])
        self.assertTrue(preferences["prefer_taste_skill"])
        self.assertEqual(len(preferences["config_paths"]), 1)

    def test_registry_and_report_separate_installed_from_native_plugin_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            paths = [
                self._write_skill(root, "impeccable", "impeccable", "Frontend design critique."),
                self._write_skill(root, "design-taste-frontend", "design-taste-frontend", "Frontend art direction."),
            ]
            taste_scripts = paths[1].parent / "scripts"
            taste_scripts.mkdir()
            (taste_scripts / "inspect.mjs").write_text("// metadata only; never executed", encoding="utf-8")
            taste_references = paths[1].parent / "references"
            taste_references.mkdir()
            (taste_references / "app-screens.md").write_text("App screen review guidance.", encoding="utf-8")
            skills, _ = discover_skills(root)
            registry = build_capability_registry(
                {"project_root": str(root), "frameworks": ["Static HTML/CSS/JavaScript"]},
                skills,
                [],
                _codex_state(),
            )

        preferred = [item for item in registry if item.kind == ResourceKind.PROVIDER_ROLE and item.id.startswith("codex:preferred-design:")]
        self.assertEqual(len(preferred), 2)
        self.assertTrue(all(item.status == CapabilityStatus.CALLABLE for item in preferred))
        report = preferred_design_expertise_report(registry)
        self.assertEqual(report["ready_count"], 2)
        impeccable_report = next(item for item in report["capabilities"] if item["canonical_name"] == "impeccable")
        self.assertFalse(impeccable_report["native_plugin_invoked"])
        self.assertIn("fallback", impeccable_report["recommendation"].casefold())
        taste_report = next(item for item in report["capabilities"] if item["canonical_name"] == "design-taste-frontend")
        self.assertTrue(taste_report["app_screen_workflow_ready"])
        self.assertTrue(any(
            "inspect.mjs" in installation["available_scripts"]
            for installation in taste_report["installations"]
        ))

    def test_missing_skills_get_prominent_install_recommendations(self) -> None:
        registry = build_capability_registry({"project_root": "/tmp/project"}, [], [], _codex_state())
        report = preferred_design_expertise_report(registry)
        self.assertEqual(report["ready_count"], 0)
        self.assertTrue(all(item["status"] == "not_installed" for item in report["capabilities"]))
        self.assertTrue(all(item["recommendation"] for item in report["capabilities"]))


class PreferredSkillSelectionTests(unittest.TestCase):
    def _registry(self, root: Path):
        skills = []
        for folder, name, description in (
            ("impeccable", "impeccable", "Frontend design audit and typography polish."),
            ("design-taste-frontend", "design-taste-frontend", "Frontend art direction and visual composition."),
        ):
            directory = root / ".agents" / "skills" / folder
            directory.mkdir(parents=True)
            (directory / "SKILL.md").write_text(
                f"---\nname: {name}\ndescription: {description}\n---\n\nUse evidence.\n",
                encoding="utf-8",
            )
            skills.append({"name": name, "description": description, "source_path": str(directory / "SKILL.md"), "capabilities": ["frontend", "visual"]})
        return build_capability_registry(
            {"project_root": str(root), "frameworks": ["Static HTML/CSS/JavaScript"]},
            skills,
            [],
            _codex_state(),
        )

    def test_comprehensive_visual_work_prefers_both_and_technical_phase_does_not(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            registry = self._registry(Path(temporary))
            plan = assemble_expert_team(
                phase="audit", mode=CollaborationMode.COMPREHENSIVE, capabilities=registry,
                frameworks=("Static HTML/CSS/JavaScript",), screenshot_available=True, primary_provider="codex",
            )
            technical = assemble_expert_team(
                phase="implementation", mode=CollaborationMode.COMPREHENSIVE, capabilities=registry,
                frameworks=("Static HTML/CSS/JavaScript",), primary_provider="codex",
                design_task=False,
            )

        selected = {item["role"] for item in plan["selected_experts"]}
        self.assertIn("impeccable_design_quality", selected)
        self.assertIn("taste_art_direction", selected)
        self.assertNotIn("impeccable_design_quality", {item["role"] for item in technical["selected_experts"]})
        self.assertEqual(plan["preferred_design_expertise"]["ready_count"], 2)

    def test_focused_mode_selects_one_preferred_role_but_considers_both(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            registry = self._registry(Path(temporary))
            plan = assemble_expert_team(
                phase="mockup", mode=CollaborationMode.FOCUSED, capabilities=registry,
                frameworks=("Static HTML/CSS/JavaScript",), primary_provider="codex",
            )

        selected = [item["role"] for item in plan["selected_experts"]]
        self.assertEqual(len([item for item in selected if item in {"impeccable_design_quality", "taste_art_direction"}]), 1)
        considered = {item["role"] for item in plan["considered"]}
        self.assertIn("impeccable_design_quality", considered)
        self.assertIn("taste_art_direction", considered)

    def test_disabled_preferred_skill_is_not_recruited(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            registry = self._registry(Path(temporary))
            plan = assemble_expert_team(
                phase="mockup", mode="comprehensive", capabilities=registry,
                frameworks=("Static HTML/CSS/JavaScript",), primary_provider="codex",
                design_preferences={"prefer_impeccable": False},
            )

        roles = {item["role"] for item in plan["selected_experts"]}
        self.assertNotIn("impeccable_design_quality", roles)
        self.assertIn("taste_art_direction", roles)


class PreferredSkillExecutionTests(unittest.TestCase):
    def test_codex_backend_declares_its_provider_for_persisted_contributions(self) -> None:
        self.assertEqual(CodexCLIBackend.provider_id, "codex")

    def test_director_synthesis_preserves_exact_shared_and_unique_evidence(self) -> None:
        review = {
            "contributions": [
                {"contributor_id": "impeccable_design_quality", "preferred_design_profile": "impeccable", "observations": [
                    {"title": "Align metric labels", "description": "The label baselines differ.", "recommendation": "Use one baseline token.", "evidence_references": ["screenshot:000"], "confidence": "high"},
                    {"title": "Clarify settings group", "description": "One section is visually isolated.", "recommendation": "Add a group heading.", "evidence_references": ["screenshot:001"], "confidence": "medium"},
                ]},
                {"contributor_id": "taste_art_direction", "preferred_design_profile": "design-taste-frontend", "observations": [
                    {"title": " align metric labels ", "description": "The metrics do not share a baseline.", "recommendation": "use one baseline token.", "evidence_references": ["screenshot:002"], "confidence": "medium"},
                ]},
            ],
            "decisions": [{"status": "investigate_further", "subject": "taste_art_direction:color"}],
            "cross_review": {"unresolved_questions": ["Does the mobile page preserve the same grouping?"]},
        }

        synthesis = _preferred_design_synthesis(review)

        self.assertEqual(len(synthesis["shared_findings"]), 1)
        self.assertEqual(synthesis["shared_findings"][0]["contributors"], ["design-taste-frontend", "impeccable"])
        self.assertEqual(len(synthesis["unique_findings"]), 1)
        self.assertEqual(len(synthesis["conflicting_or_unresolved_decisions"]), 1)
        self.assertIn("semantic overlap is not inferred", synthesis["agreement_basis"])

    def test_preferred_roles_receive_skill_guidance_and_screenshot_files(self) -> None:
        class Backend:
            available = True
            provider_id = "codex"

            def __init__(self) -> None:
                self.calls = []

            def execute(self, **kwargs):
                self.calls.append(kwargs)
                return {
                    "summary": "Evidence-based contribution.",
                    "observations": [{
                        "id": "finding-1", "title": "Observed hierarchy", "description": "The primary action is visually distinct.",
                        "evidence_references": ["screenshot:desktop"], "confidence": "high", "impact": "Clearer task entry.",
                        "recommendation": "Preserve the hierarchy.", "tradeoffs": [],
                    }],
                    "limitations": [], "unresolved_questions": [],
                }

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            skill = root / "SKILL.md"
            skill.write_text(
                "---\nname: impeccable\ndescription: critique\n---\n\n"
                "Audit typography, layout and hierarchy.\n"
                "Run `/impeccable init` for project initialization.\n"
                "```bash\nnpx impeccable install\n```\n",
                encoding="utf-8",
            )
            image = root / "screen.png"
            image.write_bytes(b"fake image for adapter contract")
            backend = Backend()
            plan = {"selected_experts": [{
                "role": "impeccable_design_quality", "provider": "codex", "capability_id": "codex:preferred-design:impeccable",
                "preferred_design_profile": "impeccable", "skill_path": str(skill), "supports_images": True,
            }]}
            result = run_phase_collaboration(
                phase="audit", mode="focused", plan=plan,
                evidence={"screenshot:desktop": {"path": str(image), "route": "/", "viewport": "desktop"}},
                backend=backend, working_directory=root, images=[image],
            )

        self.assertEqual(result["status"], "completed")
        self.assertEqual(len(backend.calls), 1)
        self.assertEqual(backend.calls[0]["images"], (image,))
        self.assertIn("Audit typography", backend.calls[0]["instruction"])
        contribution = result["contributions"][0]
        self.assertTrue(contribution["skill_guidance_attached"])
        self.assertEqual(contribution["invocation_method"], "skill_guided_role")
        self.assertFalse(contribution["native_plugin_invoked"])
        self.assertNotIn("impeccable init", backend.calls[0]["instruction"])
        self.assertNotIn("npx impeccable install", backend.calls[0]["instruction"])

    def test_preferred_role_failure_is_persisted_as_failed_execution(self) -> None:
        class Backend:
            available = True
            provider_id = "codex"

            def execute(self, **kwargs):
                raise RuntimeError("bounded backend failure")

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            skill = root / "SKILL.md"
            skill.write_text("---\nname: impeccable\ndescription: critique\n---\n\nReview typography.\n", encoding="utf-8")
            image = root / "screen.png"
            image.write_bytes(b"screenshot")
            result = run_phase_collaboration(
                phase="mockup", mode="focused",
                plan={"selected_experts": [{
                    "role": "impeccable_design_quality", "provider": "codex", "preferred_design_profile": "impeccable",
                    "skill_path": str(skill), "supports_images": True,
                }]},
                evidence={"mockup:screenshot": {"path": str(image)}},
                backend=Backend(), working_directory=root, images=[image],
            )

        self.assertEqual(result["status"], "failed")
        execution = result["specialist_executions"][0]
        self.assertEqual(execution["status"], "failed")
        self.assertEqual(execution["invocation_method"], "skill_guided_role")
        self.assertFalse(execution["native_plugin_invoked"])
        self.assertEqual(execution["error_type"], "RuntimeError")

    def test_cross_review_gets_exact_observation_ids_and_records_provider(self) -> None:
        class Backend:
            available = True
            provider_id = "codex"

            def __init__(self) -> None:
                self.review_instruction = ""
                self.invalid_target = False

            def execute(self, *, specialist, instruction, **kwargs):
                if "cross_disciplinary_reviewer" in specialist:
                    self.review_instruction = instruction
                    if self.invalid_target:
                        return {
                            "challenges": [{
                                "target_finding_id": "chart-scale", "assessment": "partially_agree",
                                "concerns": ["This target uses an unprefixed id."],
                                "supporting_evidence_references": ["screenshot:desktop"], "merge_finding_ids": [],
                                "recommended_resolution": "Use the exact supplied target id.", "confidence": "high",
                            }],
                            "unresolved_questions": [], "limitations": [],
                        }
                    return {"challenges": [], "unresolved_questions": [], "limitations": []}
                return {
                    "summary": "A screenshot-grounded observation.",
                    "observations": [{
                        "id": "chart-scale", "title": "Chart scale", "description": "The plot has no labeled value axis.",
                        "evidence_references": ["screenshot:desktop"], "confidence": "high", "impact": "Limits precision.",
                        "recommendation": "Add a compact currency scale.", "tradeoffs": [],
                    }],
                    "limitations": [], "unresolved_questions": [],
                }

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            skills = []
            for name, role, profile in (
                ("impeccable", "impeccable_design_quality", "impeccable"),
                ("design-taste-frontend", "taste_art_direction", "design-taste-frontend"),
            ):
                skill = root / f"{name}.md"
                skill.write_text(f"---\nname: {name}\ndescription: design review\n---\n\nUse evidence.\n", encoding="utf-8")
                skills.append({
                    "role": role, "provider": "codex", "preferred_design_profile": profile,
                    "skill_path": str(skill), "supports_images": True,
                })
            image = root / "screen.png"
            image.write_bytes(b"rendered image bytes")
            backend = Backend()
            plan = {"selected_experts": [
                *skills,
                {"role": "cross_disciplinary_reviewer", "provider": "codex"},
            ], "limits": {"max_independent_specialists": 2}}
            result = run_phase_collaboration(
                phase="audit", mode=CollaborationMode.COMPREHENSIVE, plan=plan,
                evidence={"screenshot:desktop": {"path": str(image), "route": "/", "viewport": "desktop"}},
                backend=backend, working_directory=root, images=[image],
            )
            backend.invalid_target = True
            invalid_result = run_phase_collaboration(
                phase="audit", mode=CollaborationMode.COMPREHENSIVE, plan=plan,
                evidence={"screenshot:desktop": {"path": str(image), "route": "/", "viewport": "desktop"}},
                backend=backend, working_directory=root, images=[image],
            )

        self.assertIn("Allowed observation IDs", backend.review_instruction)
        self.assertIn("impeccable_design_quality:chart-scale", backend.review_instruction)
        self.assertIn("taste_art_direction:chart-scale", backend.review_instruction)
        self.assertEqual(result["cross_review"]["status"], "completed")
        self.assertEqual(result["cross_review"]["provider"], "codex")
        self.assertTrue(all(item["provider"] == "codex" for item in result["contributions"]))
        self.assertEqual(invalid_result["cross_review"]["status"], "failed")
        diagnostic = " ".join(invalid_result["cross_review"]["limitations"])
        self.assertIn("chart-scale", diagnostic)
        self.assertIn("impeccable_design_quality:chart-scale", diagnostic)

    def test_live_audit_passes_valid_rendered_image_to_preferred_skill_role(self) -> None:
        class Backend:
            available = True
            provider_id = "codex"

            def __init__(self) -> None:
                self.calls = []

            def execute(self, *, specialist, schema, images=(), **kwargs):
                self.calls.append({"specialist": specialist, "images": tuple(images)})
                if specialist in {
                    "frontend_audit_impeccable_design_quality_reviewer",
                    "frontend_audit_taste_art_direction_reviewer",
                }:
                    return {
                        "summary": "The captured view has a readable hierarchy.",
                        "observations": [{
                            "id": "visual-1", "title": "Primary action hierarchy", "description": "The main action is visually distinct in the captured view.",
                            "evidence_references": ["screenshot:000"], "confidence": "high", "impact": "Supports task discovery.",
                            "recommendation": "Preserve the current hierarchy.", "tradeoffs": [],
                        }],
                        "limitations": [], "unresolved_questions": [],
                    }
                return {
                    "assessment": f"Reviewed {specialist} against the source snapshot.",
                    "assessment_evidence": [{"kind": "source", "reference": "index.html", "description": "Entry document inspected."}],
                    "findings": [], "recommendations": [], "limitations": [],
                }

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "index.html").write_text("<!doctype html><main>Fixture</main>", encoding="utf-8")
            skill = root / "SKILL.md"
            skill.write_text("---\nname: impeccable\ndescription: critique\n---\n\nUse clear visual hierarchy.\n", encoding="utf-8")
            taste_skill = root / "taste-SKILL.md"
            taste_skill.write_text("---\nname: design-taste-frontend\ndescription: art direction\n---\n\nReview composition.\n", encoding="utf-8")
            screenshot = root / "desktop.png"
            screenshot.write_bytes(b"captured screenshot bytes")
            backend = Backend()
            rendered = [{
                "path": str(screenshot), "route": "/", "viewport_label": "desktop",
                "evidence_type": "rendered_browser_screenshot", "visual_evidence_status": "valid",
                "interaction_state": "default",
            }]
            plan = {"preferred_design_expertise": {"ready_count": 2}, "selected_experts": [
                {
                    "role": "impeccable_design_quality", "provider": "codex", "preferred_design_profile": "impeccable",
                    "skill_path": str(skill), "supports_images": True,
                },
                {
                    "role": "taste_art_direction", "provider": "codex", "preferred_design_profile": "design-taste-frontend",
                    "skill_path": str(taste_skill), "supports_images": True,
                },
            ]}
            mocked_visual = (
                {"specialist": "frontend_visual_auditor", "status": "completed", "first_pass": "valid", "images_attached": 1},
                [], [], [], [], [], {},
            )
            with patch("frontend_design_director.auditing._run_visual_audit_by_route", return_value=mocked_visual):
                result = run_codex_audit(
                    root, {"root": str(root), "frameworks": []}, screenshots=rendered,
                    backend=backend, collaboration_mode="focused", collaboration_plan=plan,
                    preferred_design_preferences={"cross_review": False},
                )

        preferred_calls = [
            item for item in backend.calls
            if item["specialist"].startswith("frontend_audit_") and "reviewer" in item["specialist"]
            and "cross_disciplinary" not in item["specialist"]
        ]
        self.assertEqual(len(preferred_calls), 2)
        self.assertTrue(all(item["images"] == (screenshot.resolve(),) for item in preferred_calls))
        preferred_executions = [item for item in result.specialist_runs if item.get("preferred_design_profile")]
        self.assertEqual({item["preferred_design_profile"] for item in preferred_executions}, {"impeccable", "design-taste-frontend"})
        self.assertTrue(all(item["status"] == "completed" for item in preferred_executions))
        self.assertTrue(all(item["skill_guidance_attached"] for item in preferred_executions))
        self.assertTrue(all(item["provider"] == "codex" for item in result.collaboration["preferred_design_review"]["contributions"]))


if __name__ == "__main__":
    unittest.main()
