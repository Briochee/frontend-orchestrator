from __future__ import annotations

import json
import shutil
import socket
import sys
import tempfile
import threading
import unittest
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from frontend_design_director.browser import BrowserUnavailable, capture_screenshots, probe_safe_interactions
from frontend_design_director.director import FrontendDesignDirector
from frontend_design_director.discovery import discover_project
from frontend_design_director.guided import _prompt_action, run_guided_workflow
from frontend_design_director.auditing import AuditResult, VISUAL_FINDINGS_SCHEMA, _apply_reviewed_finding_merges, _compact_project_intelligence, _interaction_probe_evidence_prompt, _interaction_probe_evidence_refs, _validated_challenge_response, _validated_response_findings, _validated_visual_analysis, run_codex_audit
from frontend_design_director.intelligence import attach_runtime_evidence, build_project_intelligence, contrast_ratio, intelligence_reports, renderable_route_candidates, runtime_findings
from frontend_design_director.models import AuditType, EvidenceReference, Finding, Phase, Severity
from frontend_design_director.reporting import audit_reports
from frontend_design_director.server import DevelopmentServerError, managed_development_server
from frontend_design_director.storage import WORKFLOW_STATE_DIRECTORY, WorkflowStore


REPO_ROOT = Path(__file__).resolve().parents[1]
SAMPLE = REPO_ROOT / "examples" / "sample-frontend"


class AuditFindingConsolidationTests(unittest.TestCase):
    def test_behavioral_specialist_receives_only_structured_runtime_probe_outcomes(self) -> None:
        intelligence = {
            "project": {"name": "fixture"}, "routes": [], "coverage": {}, "runtime": [],
            "interaction_probe_artifact": "/tmp/evidence/interaction-probes.json",
            "interaction_probes": {
                "status": "completed",
                "scope": "loopback_only_reversible_controls",
                "limitations": ["Requests were blocked after readiness."],
                "route_results": [{
                    "route": "/settings/", "status": "completed",
                    "checks": [{"kind": "switch_state", "status": "tested", "state_changed": True, "restoration": "restored"}],
                    "blocked_post_readiness_requests": 2,
                }],
            },
        }

        compact = _compact_project_intelligence(intelligence, AuditType.BEHAVIORAL, [])

        self.assertEqual(compact["interaction_probes"]["status"], "completed")
        self.assertEqual(compact["interaction_probes"]["route_results"][0]["checks"][0]["restoration"], "restored")
        self.assertEqual(compact["interaction_probes"]["route_results"][0]["blocked_post_readiness_requests"], 2)
        self.assertEqual(
            compact["interaction_probes"]["route_results"][0]["checks"][0]["evidence_reference"],
            "/tmp/evidence/interaction-probes.json#/route_results/0/checks/0",
        )
        self.assertEqual(
            _interaction_probe_evidence_prompt(_interaction_probe_evidence_refs(intelligence))[0]["evidence_reference"],
            "/tmp/evidence/interaction-probes.json#/route_results/0/checks/0",
        )

    def test_behavioral_probe_citations_are_bound_and_invalid_first_pass_is_retried(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "index.html").write_text("<main>Fixture</main>\n", encoding="utf-8")
            artifact = root / ".agents" / "frontend-design-director" / "evidence" / "interaction-probes.json"
            artifact.parent.mkdir(parents=True)
            probes = {
                "status": "completed",
                "route_results": [{
                    "route": "/settings/", "status": "completed",
                    "checks": [{"kind": "switch_state", "status": "tested", "state_changed": True, "restoration": "restored"}],
                }],
            }
            artifact.write_text(json.dumps(probes), encoding="utf-8")
            intelligence = {
                "project": {"name": "fixture"}, "routes": [], "coverage": {}, "runtime": [],
                "interaction_probe_artifact": str(artifact), "interaction_probes": probes,
            }
            evidence_ref = f"{artifact}#/route_results/0/checks/0"
            source_evidence = {"kind": "source", "reference": "index.html", "description": "Fixture source.", "line": 1}
            probe_evidence = {"kind": "interaction_probe", "reference": evidence_ref, "description": "The switch changed state and was restored."}

            class FakeBackend:
                available = True
                provider_id = "codex"

                def __init__(self) -> None:
                    self.ux_first_pass_calls = 0

                def execute(self, *, specialist: str, **kwargs) -> dict:
                    behavioral = specialist.startswith("frontend_ux_auditor")
                    if behavioral:
                        if specialist == "frontend_ux_auditor":
                            self.ux_first_pass_calls += 1
                            evidence = {**probe_evidence, "reference": evidence_ref + "/invalid"} if self.ux_first_pass_calls == 1 else probe_evidence
                        else:
                            evidence = probe_evidence
                        finding = {
                            "id": "BEH-PROBE", "audit_type": "behavioral", "category": "switch",
                            "severity": "low", "title": "Switch state is local",
                            "description": "The tested switch toggles and restores in the isolated browser context.",
                            "evidence": [evidence],
                        }
                        assessment_evidence = [evidence]
                        findings = [finding]
                    else:
                        evidence = source_evidence
                        assessment_evidence = [evidence]
                        findings = []
                    return {
                        "findings": findings,
                        "assessment": "Evidence-backed fixture assessment.",
                        "assessment_evidence": assessment_evidence,
                        "recommendations": [],
                        "limitations": [],
                    }

            backend = FakeBackend()
            result = run_codex_audit(
                root,
                {"name": "fixture", "frameworks": []},
                backend=backend,
                intelligence=intelligence,
                collaboration_mode="focused",
            )

            ux_run = next(item for item in result.specialist_runs if item["specialist"] == "frontend_ux_auditor")
            self.assertEqual(ux_run["status"], "completed")
            self.assertEqual(ux_run["first_pass_retry_attempts"], 1)
            self.assertEqual(backend.ux_first_pass_calls, 2)
            self.assertEqual(result.findings[0].evidence[0].reference, evidence_ref)
            self.assertNotIn("unsupported evidence kind", " ".join(item.get("message", "") for item in result.diagnostics))

            invalid = {**probe_evidence, "reference": evidence_ref + "/invalid"}
            response = {
                "findings": [{
                    "id": "BEH-BAD", "audit_type": "behavioral", "category": "switch",
                    "severity": "low", "title": "Unverified switch claim", "description": "Unsupported citation.",
                    "evidence": [invalid],
                }],
                "recommendations": [], "limitations": [],
            }
            from frontend_design_director.snapshot import create_project_snapshot
            with create_project_snapshot(root) as snapshot:
                with self.assertRaisesRegex(ValueError, "interaction probe that was not tested"):
                    _validated_response_findings(
                        response, AuditType.BEHAVIORAL, "frontend_ux_auditor", snapshot, [],
                        interaction_probe_evidence=_interaction_probe_evidence_refs(intelligence),
                    )

    def test_cross_review_merge_targets_must_be_other_known_findings_with_valid_evidence(self) -> None:
        from frontend_design_director.snapshot import create_project_snapshot

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "index.html").write_text("<main>Fixture</main>\n", encoding="utf-8")
            primary = Finding(
                id="TECH-PRIMARY", audit_type=AuditType.TECHNICAL, category="dialog",
                severity=Severity.MEDIUM, title="Dialog focus issue", description="Focus is not moved.",
            )
            duplicate = Finding(
                id="BEH-DUPLICATE", audit_type=AuditType.BEHAVIORAL, category="dialog",
                severity=Severity.LOW, title="Dialog keyboard issue", description="Escape is ignored.",
            )
            response = {
                "challenges": [{
                    "target_finding_id": primary.id,
                    "assessment": "partially_agree",
                    "concerns": ["The two findings cover the same dialog behavior."],
                    "supporting_evidence": [{
                        "kind": "source", "reference": "index.html", "description": "Dialog markup is shared.", "line": 1,
                    }],
                    "merge_finding_ids": [duplicate.id],
                    "recommended_resolution": "Keep one finding and retain both details.",
                    "confidence": "high",
                }],
                "unresolved_questions": [],
                "limitations": [],
            }
            with create_project_snapshot(root, initialize_git=False) as snapshot:
                challenges, _, _ = _validated_challenge_response(response, [primary, duplicate], snapshot)
                self.assertEqual(challenges[0].merge_finding_ids, (duplicate.id,))
                response["challenges"][0]["merge_finding_ids"] = ["UNRELATED"]
                with self.assertRaises(ValueError):
                    _validated_challenge_response(response, [primary, duplicate], snapshot)

    def test_cross_review_can_cite_only_supplied_tested_interaction_probes(self) -> None:
        from frontend_design_director.snapshot import create_project_snapshot

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "index.html").write_text("<main>Fixture</main>\n", encoding="utf-8")
            behavior = Finding(
                id="BEH-SEARCH", audit_type=AuditType.BEHAVIORAL, category="search",
                severity=Severity.MEDIUM, title="Search has no empty state", description="No results are shown without feedback.",
                affected_routes=("/customers/",),
            )
            evidence_ref = "/tmp/probes.json#/route_results/0/checks/0"
            probe_evidence = {
                evidence_ref: {
                    "route": "/customers/",
                    "check": {"kind": "search_empty_state", "status": "tested", "empty_state_visible": False},
                },
            }
            response = {
                "challenges": [{
                    "target_finding_id": behavior.id,
                    "assessment": "partially_agree",
                    "concerns": ["The runtime check supports no empty state, but only for this tested route and query."],
                    "supporting_evidence": [{
                        "kind": "interaction_probe", "reference": evidence_ref,
                        "description": "The tested no-match search produced zero cards without an empty state.",
                    }],
                    "merge_finding_ids": [],
                    "recommended_resolution": "Limit the statement to the observed check.",
                    "confidence": "high",
                }],
                "unresolved_questions": [],
                "limitations": [],
            }
            with create_project_snapshot(root, initialize_git=False) as snapshot:
                challenges, _, _ = _validated_challenge_response(
                    response, [behavior], snapshot, interaction_probe_evidence=probe_evidence,
                )
                self.assertEqual(challenges[0].supporting_evidence[0]["reference"], evidence_ref)

                response["challenges"][0]["supporting_evidence"][0]["reference"] = evidence_ref + "/unverified"
                with self.assertRaisesRegex(ValueError, "interaction probe that was not tested and supplied"):
                    _validated_challenge_response(
                        response, [behavior], snapshot, interaction_probe_evidence=probe_evidence,
                    )

                response["challenges"][0]["supporting_evidence"][0]["reference"] = evidence_ref
                probe_evidence[evidence_ref]["route"] = "/orders/"
                with self.assertRaisesRegex(ValueError, "route does not match"):
                    _validated_challenge_response(
                        response, [behavior], snapshot, interaction_probe_evidence=probe_evidence,
                    )
                probe_evidence[evidence_ref]["route"] = "/customers/"

                technical = Finding(
                    id="TECH-SEARCH", audit_type=AuditType.TECHNICAL, category="search",
                    severity=Severity.MEDIUM, title="Search behavior issue", description="A technical finding.",
                )
                response["challenges"][0]["target_finding_id"] = technical.id
                response["challenges"][0]["supporting_evidence"][0]["reference"] = evidence_ref
                with self.assertRaisesRegex(ValueError, "only support behavioral findings"):
                    _validated_challenge_response(
                        response, [technical], snapshot, interaction_probe_evidence=probe_evidence,
                    )

    def test_only_explicit_high_confidence_duplicate_decisions_merge_findings(self) -> None:
        primary = Finding(
            id="TECH-PRIMARY", audit_type=AuditType.TECHNICAL, category="keyboard-accessibility",
            severity=Severity.MEDIUM, title="Dialog does not manage focus",
            description="Opening the dialog does not move focus into it.",
            affected_routes=("/orders/",), affected_components=("order-dialog",),
            evidence=(EvidenceReference("code", "src/orders.js", "The dialog is shown without focus entry.", line=20),),
            impact="Keyboard users may begin outside the dialog.",
            recommendation="Move focus into the dialog and restore it when closed.",
        )
        duplicate = Finding(
            id="BEH-DUPLICATE", audit_type=AuditType.BEHAVIORAL, category="dialog-keyboard",
            severity=Severity.LOW, title="Order overlay leaves focus outside",
            description="Escape does not close the order dialog.",
            affected_routes=("/orders/",), affected_components=("order-dialog",),
            evidence=(EvidenceReference("code", "src/app.js", "Escape only closes the mobile menu.", line=8),),
            impact="Keyboard users cannot dismiss the overlay through Escape.",
            recommendation="Handle Escape as a dialog close action.",
        )
        decisions = [{
            "subject": primary.id, "status": "accepted_with_modification", "confidence": "high",
            "merge_finding_ids": [duplicate.id],
        }]

        findings, consolidations = _apply_reviewed_finding_merges([primary, duplicate], decisions)

        self.assertEqual([item.id for item in findings], [primary.id])
        self.assertIn("Escape does not close", findings[0].description)
        self.assertEqual({item.reference for item in findings[0].evidence}, {"src/orders.js", "src/app.js"})
        self.assertIn("Escape", findings[0].recommendation)
        self.assertEqual(consolidations, [{"retained_finding_id": primary.id, "merged_finding_ids": [duplicate.id]}])
        self.assertEqual(decisions[0]["consolidated_finding_id"], primary.id)

        low_confidence = [{"subject": primary.id, "status": "accepted_with_modification", "confidence": "low", "merge_finding_ids": [duplicate.id]}]
        unchanged, no_consolidations = _apply_reviewed_finding_merges([primary, duplicate], low_confidence)
        self.assertEqual(len(unchanged), 2)
        self.assertEqual(no_consolidations, [])


class DeepProjectIntelligenceTests(unittest.TestCase):
    def test_architecture_routes_components_and_design_values_are_project_specific(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "package.json").write_text(json.dumps({"name": "admin-ui", "dependencies": {"react": "^19"}}), encoding="utf-8")
            (root / "src" / "pages").mkdir(parents=True)
            (root / "src" / "components").mkdir(parents=True)
            (root / "src" / "pages" / "index.tsx").write_text(
                'import { PrimaryAction } from "../components/PrimaryAction";\nexport default function Home(){ return <main><PrimaryAction /></main>; }\n',
                encoding="utf-8",
            )
            (root / "src" / "pages" / "settings.tsx").write_text(
                'import { PrimaryAction } from "../components/PrimaryAction";\nexport default function Settings(){ return <main><PrimaryAction /></main>; }\n',
                encoding="utf-8",
            )
            (root / "src" / "components" / "PrimaryAction.tsx").write_text(
                "export function PrimaryAction(){ return <button>Save</button>; }\n", encoding="utf-8"
            )
            (root / "src" / "styles.css").write_text(
                ":root { --color-accent: #176b55; --space-2: 0.5rem; }\nbody { color: #1b1b1b; background: #fff; font-family: Inter, sans-serif; font-size: 1rem; line-height: 1.5; padding: 1rem; }\n@media (max-width: 700px) { main { padding: 0.5rem; } }\n",
                encoding="utf-8",
            )

            project = discover_project(root)
            intelligence = build_project_intelligence(root, project)

        self.assertIn("React", intelligence["project"]["frameworks"])
        routes = {item["path"]: item for item in intelligence["routes"]}
        self.assertIn("/", routes)
        self.assertIn("/settings", routes)
        self.assertIn("PrimaryAction", routes["/"]["components"])
        component = next(item for item in intelligence["components"] if item["name"] == "PrimaryAction")
        self.assertEqual(component["routes"], ["/", "/settings"])
        self.assertEqual(intelligence["design_system"]["breakpoints"], ["700px"])
        self.assertIn("color-accent", [item["name"] for item in intelligence["design_system"]["color_tokens"]])
        self.assertIn("space-2", [item["name"] for item in intelligence["design_system"]["custom_properties"]])
        self.assertEqual(renderable_route_candidates(intelligence), ["/", "/settings"])
        self.assertIn("frontend-architecture-map.md", intelligence_reports(intelligence))
        self.assertIn("component-inventory.md", intelligence_reports(intelligence))

    def test_static_html_route_sources_scripts_manifests_and_tests_are_mapped(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "orders").mkdir()
            (root / "src").mkdir()
            (root / "tests").mkdir()
            (root / "package.json").write_text('{"name":"catalog-ui"}', encoding="utf-8")
            (root / "index.html").write_text(
                '<main class="overview"><a href="orders/">Orders</a></main><script src="src/app.js"></script>',
                encoding="utf-8",
            )
            (root / "orders" / "index.html").write_text(
                '<main class="orders"><h1>Orders</h1></main><script src="../src/orders.js"></script>',
                encoding="utf-8",
            )
            (root / "src" / "app.js").write_text("document.documentElement.dataset.ready = 'true';", encoding="utf-8")
            (root / "src" / "components.js").write_text("export function renderNotice() { return '<aside></aside>'; }", encoding="utf-8")
            (root / "src" / "orders.js").write_text("document.querySelector('.orders');", encoding="utf-8")
            (root / "tests" / "smoke.test.mjs").write_text("export const smoke = true;", encoding="utf-8")

            intelligence = build_project_intelligence(root, discover_project(root))

        routes = {item["path"]: item for item in intelligence["routes"]}
        self.assertEqual(routes["/"]["source"], "index.html")
        self.assertEqual(routes["/orders/"]["source"], "orders/index.html")
        self.assertEqual(routes["/"]["modules"], ["src/app.js"])
        self.assertEqual(routes["/orders/"]["modules"], ["src/orders.js"])
        architecture = intelligence["architecture"]
        self.assertIn("index.html", architecture["application_entry_and_routes"])
        self.assertIn("orders/index.html", architecture["application_entry_and_routes"])
        self.assertIn("src/components.js", architecture["shared_components"])
        self.assertIn("package.json", architecture["configuration_and_manifests"])
        self.assertIn("tests/smoke.test.mjs", architecture["tests_and_story_catalogs"])
        rendered = intelligence_reports(intelligence)["frontend-architecture-map.md"].decode()
        self.assertIn("modules: `src/orders.js`", rendered)

    def test_dynamic_route_patterns_are_not_selected_for_browser_navigation(self) -> None:
        self.assertEqual(renderable_route_candidates({"routes": [{"path": "/"}, {"path": "/users/:id"}, {"path": "/settings"}]}), ["/", "/settings"])

    def test_runtime_evidence_updates_source_inventory_without_reclassification(self) -> None:
        intelligence = {"runtime": [], "coverage": {"routes_discovered": 2, "routes_rendered": 0, "screenshots_captured": 0, "rendered_viewports": [], "rendered_evidence_available": False}}
        screenshots = [{"evidence_type": "rendered_browser_screenshot", "path": "/tmp/home.png", "route": "/", "viewport": "desktop", "computed_styles": {}}]
        enriched = attach_runtime_evidence(intelligence, screenshots)
        self.assertEqual(enriched["coverage"]["routes_rendered"], 1)
        self.assertEqual(enriched["coverage"]["screenshots_captured"], 1)
        self.assertEqual(intelligence["runtime"], [])

    def test_visual_narrative_requires_exact_rendered_route_and_viewport_references(self) -> None:
        screenshot = {"path": "/tmp/settings-desktop.png", "route": "/settings", "viewport": "settings:desktop", "evidence_type": "rendered_browser_screenshot"}
        analysis = {
            "design_identity": "A restrained settings interface with a compact form layout.",
            "design_identity_evidence": [{"claim": "The form is centered in a narrow content region.", "route": "/settings", "viewport": "settings:desktop", "screenshot_reference": "/tmp/settings-desktop.png"}],
            "experience_character": "The captured screen emphasizes configuration controls.",
            "strengths": [{"claim": "The page title is visually distinct.", "route": "/settings", "viewport": "settings:desktop", "screenshot_reference": "/tmp/settings-desktop.png"}],
            "concerns": [], "consistency_patterns": [],
            "route_assessments": [{"route": "/settings", "viewport": "settings:desktop", "hierarchy": "Title then form sections", "density": "Moderate", "responsive_notes": "One desktop capture only", "screenshot_reference": "/tmp/settings-desktop.png"}],
            "preserve": [], "refine": [], "reconsider_with_human_approval": [], "limitations": ["No mobile screenshot was supplied."]
        }
        validated = _validated_visual_analysis(analysis, [screenshot])
        self.assertEqual(validated["route_assessments"][0]["screenshot_reference"], screenshot["path"])
        self.assertIn("visual_analysis", VISUAL_FINDINGS_SCHEMA["required"])
        bad = {**analysis, "strengths": [{**analysis["strengths"][0], "route": "/other"}]}
        with self.assertRaises(ValueError):
            _validated_visual_analysis(bad, [screenshot])

    def test_supplemental_reports_label_unverified_checks_and_visual_analysis(self) -> None:
        project = discover_project(SAMPLE)
        intelligence = build_project_intelligence(SAMPLE, project)
        result = AuditResult((), (), (), (), "codex_cli", {
            "design_identity": "A compact task dashboard with a restrained accent palette.",
            "design_identity_evidence": [],
            "experience_character": "The screen foregrounds the current list and its primary action.",
            "strengths": [], "concerns": [], "consistency_patterns": [], "route_assessments": [],
            "preserve": [], "refine": [], "reconsider_with_human_approval": [], "limitations": [],
        })
        reports = audit_reports([], result, project, intelligence)
        self.assertIn("executive-summary.md", reports)
        self.assertIn("color-system-analysis.md", reports)
        self.assertIn("typography-analysis.md", reports)
        self.assertIn("Not a WCAG conformance certificate", reports["accessibility-audit.md"].decode())
        self.assertIn("not collected", reports["performance-audit.md"].decode())
        self.assertIn("compact task dashboard", reports["visual-audit.md"].decode())

    def test_supplemental_reports_bound_runtime_tables_and_preserve_full_evidence(self) -> None:
        project = discover_project(SAMPLE)
        intelligence = build_project_intelligence(SAMPLE, project)
        intelligence["design_system"]["colors"] = [
            {"value": f"#{index:06x}", "count": 1, "files": ["styles.css"]}
            for index in range(130)
        ]
        intelligence["runtime"] = [{
            "route": "/", "viewport": "desktop", "width": 1440,
            "document": {"width": 1440, "height": 1000}, "screenshot": "/tmp/dashboard.png",
            "computed_styles": {
                f".font-{index}": {"fontFamily": "Example Sans", "fontSize": "14px", "lineHeight": "20px"}
                for index in range(15)
            },
            "contrast_samples": [{
                "selector": f".contrast-{index}", "foreground": "#000", "background": "#fff",
                "ratio": 21, "threshold": 4.5, "classification": "pass",
            } for index in range(15)],
        }]
        result = AuditResult((), (), (), (), "static")

        reports = audit_reports([], result, project, intelligence)
        colors = reports["color-system-analysis.md"].decode()
        typography = reports["typography-analysis.md"].decode()

        self.assertIn("Showing the 120 most frequent color literals", colors)
        self.assertIn("additional values remain in `frontend-intelligence.json`", colors)
        self.assertEqual(colors.count("| `.contrast-"), 12)
        self.assertIn("3 additional sampled pairs in `frontend-intelligence.json`", colors)
        self.assertEqual(typography.count("`.font-"), 12)
        self.assertIn("3 additional computed samples are preserved in `frontend-intelligence.json`", typography)

    def test_accessibility_categories_and_specialist_limitations_keep_their_scope(self) -> None:
        project = discover_project(SAMPLE)
        intelligence = build_project_intelligence(SAMPLE, project)
        finding = Finding(
            id="BEH-1", audit_type=AuditType.BEHAVIORAL, category="accessible-name", severity=Severity.MEDIUM,
            title="Notification control has no accessible name", description="The icon button has no text name.",
            evidence=(EvidenceReference("source", "index.html", "The button has no accessible name.", line=1),),
        )
        screenshot = {
            "path": "/screens/home.png", "route": "/", "viewport": "desktop", "viewport_label": "desktop",
            "width": 1440, "height": 1000, "image_dimensions": {"width": 1440, "height": 1000},
            "evidence_type": "rendered_browser_screenshot", "visual_evidence_status": "valid",
        }
        result = AuditResult(
            findings=(finding,), limitations=(), recommendations=(), screenshots=(screenshot,), backend_used="codex_cli",
            visual_delivery={"screenshots_attached": 1, "interpreted": True, "validated": True},
            specialist_assessments=({
                "specialist": "frontend_ux_auditor", "audit_type": "behavioral", "pass": "first_pass",
                "assessment": "Source review only.", "evidence": [],
                "limitations": ["No rendered screenshots were attached to the UX specialist pass."],
            },),
        )
        reports = audit_reports([finding], result, project, intelligence)
        accessibility = reports["accessibility-audit.md"].decode()
        behavioral = reports["behavioral-audit.md"].decode()
        summary = reports["audit-summary.md"].decode()
        self.assertIn(finding.title, accessibility)
        self.assertNotIn("No accessibility-specific finding was produced", accessibility)
        self.assertIn("Pass-scoped limitations", behavioral)
        self.assertIn("No rendered screenshots were attached to the UX specialist pass", behavioral)
        self.assertNotIn("No rendered screenshots were attached to the UX specialist pass", summary)

    def test_visual_specialist_returns_schema_checked_screenshot_analysis(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "project"
            root.mkdir()
            (root / "index.html").write_text("<!doctype html><title>Fixture</title><main>Content</main>", encoding="utf-8")
            screenshot_path = Path(temporary) / "desktop.png"
            screenshot_path.write_bytes(b"not decoded by mock")
            screenshot = {"path": str(screenshot_path), "route": "/", "viewport": "desktop", "evidence_type": "rendered_browser_screenshot", "width": 1440, "height": 1000}
            analysis = {
                "design_identity": "A restrained single-column page, based on the supplied image.",
                "design_identity_evidence": [{"claim": "A single column dominates the captured frame.", "route": "/", "viewport": "desktop", "screenshot_reference": str(screenshot_path)}],
                "experience_character": "The page prioritizes its main content.",
                "strengths": [{"claim": "The main content is visually prominent.", "route": "/", "viewport": "desktop", "screenshot_reference": str(screenshot_path)}],
                "concerns": [], "consistency_patterns": [],
                "route_assessments": [{"route": "/", "viewport": "desktop", "hierarchy": "Main content first", "density": "Low", "responsive_notes": "Only desktop was captured", "screenshot_reference": str(screenshot_path)}],
                "preserve": [], "refine": [], "reconsider_with_human_approval": [], "limitations": ["No mobile evidence was attached."]
            }

            class VisualBackend:
                available = True
                image_calls: list[int] = []

                def execute(self, *, instruction, **kwargs):
                    images = kwargs.get("images", ())
                    self.image_calls.append(len(images))
                    if "cross-screen synthesizer" in instruction:
                        return analysis
                    response = {"findings": [], "recommendations": [], "limitations": []}
                    if "frontend_visual_auditor" in instruction:
                        response.update({
                            "assessment": "The supplied screenshot shows a focused, single-column content view.",
                            "assessment_evidence": [{"kind": "screenshot", "reference": str(screenshot_path), "description": "The assessment was checked against the attached desktop screenshot.", "viewport": "desktop"}],
                            "visual_analysis": analysis,
                        })
                    else:
                        response.update({
                            "assessment": "The inspected source defines a single static page.",
                            "assessment_evidence": [{"kind": "source", "reference": "index.html", "description": "The source contains the page main landmark.", "line": 1}],
                        })
                    return response

            result = run_codex_audit(root, discover_project(root), screenshots=[screenshot], backend=VisualBackend())
        self.assertEqual(result.visual_analysis["design_identity"], analysis["design_identity"])
        self.assertEqual(len(result.visual_analysis["route_assessments"]), 1)
        self.assertEqual(result.specialist_runs[-1]["status"], "completed")
        self.assertEqual(VisualBackend.image_calls, [0, 0, 0, 0, 1, 1, 0])

    def test_director_captures_static_routes_but_never_synthesizes_dynamic_parameters(self) -> None:
        with tempfile.TemporaryDirectory(prefix="frontend-director-route-audit-") as temporary:
            root = Path(temporary)
            (root / "src" / "app" / "settings").mkdir(parents=True)
            (root / "src" / "app" / "users" / "[id]").mkdir(parents=True)
            (root / "src" / "app" / "page.tsx").write_text("export default function Home(){ return <main>Home</main>; }", encoding="utf-8")
            (root / "src" / "app" / "settings" / "page.tsx").write_text("export default function Settings(){ return <main>Settings</main>; }", encoding="utf-8")
            (root / "src" / "app" / "users" / "[id]" / "page.tsx").write_text("export default function User(){ return <main>User</main>; }", encoding="utf-8")
            store = WorkflowStore(root / WORKFLOW_STATE_DIRECTORY / "workflow.sqlite3")
            director = FrontendDesignDirector(store)
            session = director.create_session(root)
            director.discover(session.id)
            seen: list[str] = []

            def capture(_url, _directory, **kwargs):
                seen.extend(kwargs["route_paths"])
                return []

            with patch("frontend_design_director.director.capture_screenshots", side_effect=capture):
                director.audit(session.id, browser_url="http://127.0.0.1:5173/", depth="standard")
            self.assertIn("/settings", seen)
            self.assertNotIn("/users/:id", seen)
            self.assertEqual(store.get_session(session.id).metadata["frontend_intelligence"]["capture_route_policy"], "all_static_candidates")

            seen.clear()
            with patch("frontend_design_director.director.capture_screenshots", side_effect=capture):
                director.audit(session.id, browser_url="http://127.0.0.1:5173/", route_paths=["/settings"], depth="standard")
            self.assertEqual(seen, ["/settings"])
            self.assertEqual(store.get_session(session.id).metadata["frontend_intelligence"]["capture_route_policy"], "operator_selected")

    def test_contrast_only_accepts_unambiguous_opaque_colors(self) -> None:
        self.assertEqual(contrast_ratio("rgb(0, 0, 0)", "rgb(255, 255, 255)"), 21.0)
        self.assertEqual(contrast_ratio("#000", "#fff"), 21.0)
        self.assertIsNone(contrast_ratio("rgba(0, 0, 0, 0.5)", "rgb(255, 255, 255)"))

    def test_runtime_observations_become_separate_evidence_linked_findings(self) -> None:
        intelligence = {
            "runtime": [{
                "route": "/settings", "viewport": "settings:mobile", "screenshot": "/evidence/settings.png", "width": 390,
                "document": {"width": 512}, "controls": {"inputs_without_associated_label": 1},
                "page_errors": ["TypeError: broken settings component"],
            }],
        }
        findings = runtime_findings(intelligence)
        self.assertEqual({item.audit_type for item in findings}, {AuditType.VISUAL, AuditType.BEHAVIORAL, AuditType.TECHNICAL})
        self.assertTrue(all(item.evidence and item.evidence[0].reference == "/evidence/settings.png" for item in findings))
        self.assertEqual({item.verification_status.value for item in findings}, {"observed"})


class GuidedWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="frontend-director-guide-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "project"
        shutil.copytree(SAMPLE, self.root)
        self.store = WorkflowStore(self.root / WORKFLOW_STATE_DIRECTORY / "workflow.sqlite3")
        self.director = FrontendDesignDirector(self.store)
        self.session = self.director.create_session(self.root)

    def test_guide_persists_instructions_continues_audit_then_explicitly_ends(self) -> None:
        responses = iter(["instructions", "Prioritize mobile navigation", "Keep the existing navigation structure", "END INSTRUCTIONS", "continue", "end"])
        output: list[str] = []
        result = run_guided_workflow(self.director, self.store, self.session.id, input_fn=lambda _: next(responses), output_fn=output.append)
        saved = self.store.get_session(self.session.id)
        self.assertEqual(result["status"], "ended")
        self.assertEqual(saved.phase, Phase.AUDIT_COMPLETED_WITH_LIMITATIONS)
        self.assertEqual(saved.metadata["guided_session"]["status"], "ended")
        self.assertEqual(saved.metadata["guided_instructions"][0]["stage"], "audit")
        self.assertEqual(saved.metadata["guided_instructions"][0]["instruction"], "Prioritize mobile navigation\nKeep the existing navigation structure")
        self.assertEqual(saved.metadata["audit"]["findings_count"], len(self.store.findings(self.session.id)))
        self.assertTrue(any("routes:" in item for item in output))

    def test_end_of_input_persists_pending_decision_and_can_resume(self) -> None:
        self.director.discover(self.session.id)
        interrupted = run_guided_workflow(self.director, self.store, self.session.id, input_fn=lambda _: (_ for _ in ()).throw(EOFError()), output_fn=lambda _: None)
        self.assertEqual(interrupted["status"], "waiting_for_input")
        self.assertEqual(self.store.get_session(self.session.id).metadata["guided_session"]["pending_action"], "review_discovery")
        resumed = run_guided_workflow(self.director, self.store, self.session.id, input_fn=lambda _: "end", output_fn=lambda _: None)
        self.assertEqual(resumed["status"], "ended")

    def test_guide_persists_collaboration_mode_and_explicit_secondary_provider_policy(self) -> None:
        result = run_guided_workflow(
            self.director,
            self.store,
            self.session.id,
            use_codex=True,
            collaboration_mode="exhaustive",
            allowed_secondary_providers=["claude"],
            exercise_safe_interactions=True,
            input_fn=lambda _: (_ for _ in ()).throw(EOFError()),
            output_fn=lambda _: None,
        )
        metadata = self.store.get_session(self.session.id).metadata
        self.assertEqual(result["status"], "waiting_for_input")
        self.assertEqual(metadata["collaboration_mode"], "exhaustive")
        self.assertEqual(metadata["allowed_secondary_providers"], ["claude"])
        self.assertTrue(metadata["exercise_safe_interactions"])

    def test_safe_interaction_probes_require_a_browser_url_or_approved_server(self) -> None:
        with self.assertRaisesRegex(ValueError, "require an explicit --url"):
            self.director.audit(self.session.id, exercise_safe_interactions=True)

    def test_guide_requires_codex_for_explicit_secondary_provider_authorization(self) -> None:
        with self.assertRaisesRegex(ValueError, "requires the primary Codex audit"):
            run_guided_workflow(
                self.director,
                self.store,
                self.session.id,
                allowed_secondary_providers=["claude"],
                input_fn=lambda _: "end",
                output_fn=lambda _: None,
            )

    def test_pending_workflow_phases_offer_additional_instructions(self) -> None:
        phases = [
            Phase.CAPABILITIES_REVIEW, Phase.AUDIT_COMPLETED, Phase.AWAITING_DIRECTION,
            Phase.DIRECTION_APPROVED, Phase.GENERATING_MOCKUPS, Phase.AWAITING_MOCKUP_REVIEW,
            Phase.MOCKUP_REVISION, Phase.MOCKUP_APPROVED, Phase.AWAITING_IMPLEMENTATION_APPROVAL,
            Phase.IMPLEMENTING, Phase.PATCH_READY, Phase.APPLYING, Phase.VERIFYING,
            Phase.COMPLETED, Phase.PAUSED, Phase.FAILED, Phase.CANCELLED,
        ]
        for phase in phases:
            with self.subTest(phase=phase):
                output: list[str] = []
                self.assertEqual(_prompt_action(phase, lambda _: "end", output.append), "end")
                self.assertIn("instructions", output[0])

    def test_direction_confirmation_does_not_authorize_implementation(self) -> None:
        self.director.discover(self.session.id)
        self.director.audit(self.session.id)
        responses = iter(["continue", "refine", "preserve", "screens", "CONFIRM DIRECTION", "end"])
        tty = SimpleNamespace(isatty=lambda: True)
        with patch("frontend_design_director.guided.sys.stdin", tty), patch("frontend_design_director.guided.sys.stdout", tty):
            run_guided_workflow(self.director, self.store, self.session.id, input_fn=lambda _: next(responses), output_fn=lambda _: None)
        self.assertEqual(self.store.get_session(self.session.id).phase, Phase.DIRECTION_APPROVED)
        self.assertIsNotNone(self.store.latest_valid_approval(self.session.id, "design_direction", "design-direction"))


class BrowserEvidenceTests(unittest.TestCase):
    def test_browser_capture_collects_explicit_routes_and_runtime_metadata(self) -> None:
        if not __import__("frontend_design_director.browser", fromlist=["playwright_available"]).playwright_available():
            self.skipTest("Playwright is not installed.")
        with tempfile.TemporaryDirectory(prefix="frontend-director-browser-test-") as temporary:
            root = Path(temporary)
            (root / "index.html").write_text(
                '<!doctype html><html lang="en"><head><title>Fixture</title></head><body><main style="width:900px"><h1>Home</h1><label for="email">Email</label><input id="email"><button onclick="console.error(\'test console error\')">Action</button><a href="/settings.html">Settings</a></main></body></html>',
                encoding="utf-8",
            )
            (root / "settings.html").write_text("<!doctype html><html><body><main><h1>Settings</h1><input><a href=\"/\">Home</a></main></body></html>", encoding="utf-8")
            try:
                server = ThreadingHTTPServer(("127.0.0.1", 0), lambda *args, **kwargs: SimpleHTTPRequestHandler(*args, directory=str(root), **kwargs))
            except PermissionError:
                self.skipTest("The sandbox does not allow binding a local HTTP test server.")
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            self.addCleanup(server.server_close)
            self.addCleanup(thread.join, 2)
            self.addCleanup(server.shutdown)
            output = root / "captures"
            try:
                evidence = capture_screenshots(f"http://127.0.0.1:{server.server_port}/index.html", output, route_paths=["/settings.html"], viewports=["desktop", "mobile"])
            except BrowserUnavailable as error:
                self.skipTest(str(error))
            self.assertTrue((output / "gallery.html").is_file())
            self.assertTrue((output / "screenshots.json").is_file())
        base_captures = [item for item in evidence if item.get("interaction_state") is None]
        focus_captures = [item for item in evidence if item.get("interaction_state") == "keyboard_focus_after_one_tab"]
        self.assertEqual(len(base_captures), 4)
        self.assertEqual(len(focus_captures), 2)
        self.assertTrue(all(item.get("focus_target") for item in focus_captures))
        self.assertEqual({item["route"] for item in evidence}, {"/index.html", "/settings.html"})
        self.assertTrue(all(item["readiness"]["dom_content_loaded"] for item in base_captures))
        self.assertTrue(all(item["document"]["title"] in {"Fixture", ""} for item in base_captures))
        self.assertTrue(all(item["image_dimensions"] == {"width": item["width"], "height": item["height"]} for item in base_captures))
        desktop = next(item for item in base_captures if item["route"] == "/index.html" and item["viewport_label"] == "desktop")
        mobile = next(item for item in base_captures if item["route"] == "/index.html" and item["viewport_label"] == "mobile")
        self.assertIn("main", desktop["computed_styles"])
        self.assertIn("/settings.html", desktop["internal_links"])
        self.assertGreater(mobile["document"]["horizontal_overflow_px"], 0)
        self.assertEqual(mobile["visual_evidence_status"], "valid")

    def test_opt_in_safe_probes_restore_controls_and_block_interaction_requests(self) -> None:
        if not __import__("frontend_design_director.browser", fromlist=["playwright_available"]).playwright_available():
            self.skipTest("Playwright is not installed.")
        with tempfile.TemporaryDirectory(prefix="frontend-director-probe-test-") as temporary:
            root = Path(temporary)
            (root / "index.html").write_text("""<!doctype html><html><head><title>Probe fixture</title></head><body>
              <input type="search" aria-label="Search records">
              <ul><li class="customer-card">Visible record</li></ul><p class="empty-state" hidden>No matches</p>
              <input id="range" type="range" min="1" max="101" step="1" value="10"><output for="range">10</output><span id="qualified-orders">1</span>
              <button type="button" role="switch" aria-checked="false" id="switch">Enable</button>
              <button data-open="record" type="button" id="view-record">View</button>
              <div role="dialog" hidden><button type="button" data-close>Close</button></div>
              <form><input type="text" value="Original" oninput="fetch('/blocked-edit', {method: 'POST'})"><button type="submit">Save</button></form>
              <script>
                const search = document.querySelector('input[type=search]');
                search.addEventListener('input', () => { const empty = search.value.includes('__frontend_director_no_match__'); document.querySelector('.customer-card').hidden = empty; document.querySelector('.empty-state').hidden = !empty; });
                const range = document.querySelector('#range');
                range.addEventListener('input', () => { document.querySelector('output').textContent = range.value; document.querySelector('#qualified-orders').textContent = range.value; });
                document.querySelector('#switch').addEventListener('click', event => event.currentTarget.setAttribute('aria-checked', String(event.currentTarget.getAttribute('aria-checked') !== 'true')));
                document.querySelector('#view-record').addEventListener('click', () => { document.querySelector('[role=dialog]').hidden = false; fetch('/blocked-write', {method: 'POST'}); });
                document.querySelector('[data-close]').addEventListener('click', () => { document.querySelector('[role=dialog]').hidden = true; });
              </script>
            </body></html>""", encoding="utf-8")
            reached_writes: list[str] = []

            class Handler(SimpleHTTPRequestHandler):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, directory=str(root), **kwargs)

                def do_POST(self):
                    reached_writes.append(self.path)
                    self.send_response(204)
                    self.end_headers()

                def log_message(self, _format, *_args):
                    return

            try:
                server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
            except PermissionError:
                self.skipTest("The sandbox does not allow binding a local HTTP test server.")
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            self.addCleanup(server.server_close)
            self.addCleanup(thread.join, 2)
            self.addCleanup(server.shutdown)
            try:
                result = probe_safe_interactions(f"http://127.0.0.1:{server.server_port}/index.html")
            except BrowserUnavailable as error:
                self.skipTest(str(error))

        self.assertEqual(result["status"], "completed")
        route = result["route_results"][0]
        checks = {item["kind"]: item for item in route["checks"]}
        self.assertEqual(set(checks), {"form_text_edit", "search_empty_state", "range_control", "switch_state", "read_only_dialog"})
        self.assertTrue(checks["form_text_edit"]["value_changed"])
        self.assertEqual(checks["form_text_edit"]["restoration"], "restored")
        self.assertEqual(checks["search_empty_state"]["restoration"], "restored")
        self.assertEqual(checks["search_empty_state"]["no_match_result_count"], 0)
        self.assertTrue(checks["search_empty_state"]["empty_state_visible"])
        self.assertTrue(checks["range_control"]["formatted_output_changed"])
        self.assertTrue(checks["range_control"]["related_metric_changed"])
        self.assertEqual(checks["range_control"]["restoration"], "restored")
        self.assertTrue(checks["switch_state"]["state_changed"])
        self.assertFalse(checks["switch_state"]["theme_effect_observed"])
        self.assertTrue(checks["switch_state"]["theme_effect_restored"])
        self.assertEqual(checks["switch_state"]["restoration"], "restored")
        self.assertTrue(checks["read_only_dialog"]["opened"])
        self.assertFalse(checks["read_only_dialog"]["focus_inside_on_open"])
        self.assertFalse(checks["read_only_dialog"]["escape_closed"])
        self.assertTrue(checks["read_only_dialog"]["closed"])
        self.assertGreater(route["blocked_post_readiness_requests"], 0)
        self.assertEqual(reached_writes, [])


class DevelopmentServerTests(unittest.TestCase):
    def test_authorized_server_starts_readies_and_only_its_process_is_stopped(self) -> None:
        with tempfile.TemporaryDirectory(prefix="frontend-director-server-test-") as temporary:
            root = Path(temporary)
            (root / "index.html").write_text("<main>ok</main>", encoding="utf-8")
            with socket.socket() as probe:
                try:
                    probe.bind(("127.0.0.1", 0))
                except PermissionError:
                    self.skipTest("The sandbox does not allow binding a local HTTP test server.")
                port = probe.getsockname()[1]
            url = f"http://127.0.0.1:{port}/"
            command = [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1", "--directory", str(root)]
            with managed_development_server(root, command, url, readiness_timeout_seconds=8) as server_run:
                self.assertIsNotNone(server_run.process_id)
                self.assertEqual(server_run.ready_status, 200)
                self.assertEqual(server_run.details["command"]["executable"], Path(sys.executable).name)
            self.assertIsNone(__import__("frontend_design_director.server", fromlist=["_http_status"])._http_status(url, 0.2))
            self.assertTrue(server_run.details["owned_process_group"])

    def test_existing_server_is_not_duplicated_and_remote_start_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            with managed_development_server(Path.cwd(), [sys.executable, "-c", "pass"], "http://192.0.2.1:8000/"):
                self.fail("remote server must not start")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            try:
                server = ThreadingHTTPServer(("127.0.0.1", 0), SimpleHTTPRequestHandler)
            except PermissionError:
                self.skipTest("The sandbox does not allow binding a local HTTP test server.")
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                url = f"http://127.0.0.1:{server.server_port}/"
                with self.assertRaises(DevelopmentServerError):
                    with managed_development_server(root, [sys.executable, "-m", "http.server"], url):
                        self.fail("an existing server must be left alone")
            finally:
                server.shutdown()
                server.server_close()
                thread.join(2)


if __name__ == "__main__":
    unittest.main()
