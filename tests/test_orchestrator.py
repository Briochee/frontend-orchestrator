from __future__ import annotations

import hashlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from frontend_design_director.auditing import _validate_finding_evidence, run_codex_audit, run_static_audit
from frontend_design_director.browser import VIEWPORTS, BrowserUnavailable, capture_mockup_screenshots, capture_screenshots
from frontend_design_director.codex_backend import CodexCLIBackend, CodexSettings
from frontend_design_director.execution import execution_policy_for_phase
from frontend_design_director.cli import _install_codex, _install_skill, _store_for, _uninstall_codex, main
from frontend_design_director.director import FrontendDesignDirector, WorkflowBlocked
from frontend_design_director.discovery import build_capability_matrix, discover_agents, discover_codex, discover_project, discover_skills
from frontend_design_director.implementation import ScopeViolation, apply_implementation_patch, create_implementation_plan
from frontend_design_director.models import Approval, AuditType, EvidenceReference, Finding, Phase
from frontend_design_director.reporting import audit_reports
from frontend_design_director.snapshot import create_project_snapshot
from frontend_design_director.state_machine import InvalidTransition, validate_transition
from frontend_design_director.storage import LEGACY_WORKFLOW_STATE_DIRECTORY, WORKFLOW_STATE_DIRECTORY, WorkflowStore
from frontend_design_director.snapshot import _git_environment
from frontend_design_director.verification import run_verification


REPO_ROOT = Path(__file__).resolve().parents[1]
SAMPLE = REPO_ROOT / "examples" / "sample-frontend"


class FakeBackend:
    """Deterministic Codex-shaped backend that edits only the isolated test snapshot."""

    available = True

    def __init__(self) -> None:
        self.execution_policies = []

    def execute(self, *, working_directory, instruction, schema, sandbox="read-only", images=(), timeout_seconds=None, execution_policy=None):
        self.execution_policies.append(execution_policy)
        if schema.get("properties", {}).get("status", {}).get("enum") == ["complete"]:
            page = Path(working_directory) / "index.html"
            page.write_text("<!doctype html><html lang=\"en\"><title>Approved update</title><body>Approved update</body></html>\n", encoding="utf-8")
            return {"status": "complete", "summary": "Updated the approved sample page."}
        raise AssertionError("Unexpected backend task in this deterministic workflow.")


class WorkflowTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="frontend-director-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "project"
        shutil.copytree(SAMPLE, self.root)
        self.store = WorkflowStore(self.root / WORKFLOW_STATE_DIRECTORY / "workflow.sqlite3")
        self.director = FrontendDesignDirector(self.store, FakeBackend())

    def make_audited_session(self) -> str:
        session = self.director.create_session(self.root)
        self.director.discover(session.id)
        self.director.audit(session.id)
        return session.id

    def approve_direction_and_mockup(self, session_id: str) -> None:
        self.director.record_direction(session_id, visual="refine", behavior="preserve", scope="screens", human_confirmation=True)
        self.director.generate_mockup(session_id)
        self.director.review_mockup(session_id, action="approve", human_confirmation=True)


class DiscoveryTests(unittest.TestCase):
    def test_skills_are_classified_and_unrelated_or_malformed_skills_are_excluded(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            frontend = root / "frontend" / "SKILL.md"
            unrelated = root / "unrelated" / "SKILL.md"
            malformed = root / "malformed" / "SKILL.md"
            for path in (frontend, unrelated, malformed):
                path.parent.mkdir()
            frontend.write_text("---\nname: responsive UI review\ndescription: Evaluate accessibility and responsive visual interfaces\n---\nignored body", encoding="utf-8")
            unrelated.write_text("---\nname: invoice reconciliation\ndescription: Match freight invoice records\n---", encoding="utf-8")
            malformed.write_text("---\nname: incomplete\n---", encoding="utf-8")
            with patch("frontend_design_director.discovery.skill_roots", return_value=[]):
                skills, errors = discover_skills(root, (root,))
            self.assertEqual([item["name"] for item in skills], ["responsive UI review"])
            self.assertTrue({"frontend", "accessibility", "ux", "visual"}.intersection(skills[0]["capabilities"]))
            self.assertEqual(len(errors), 1)
            self.assertTrue(skills[0]["metadata_only"])

    def test_missing_skill_directories_are_handled_and_static_frontend_is_available(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "page.html").write_text("<main>Hi</main>", encoding="utf-8")
            with patch("frontend_design_director.discovery.skill_roots", return_value=[root / "missing"]):
                skills, errors = discover_skills(root)
            self.assertEqual(skills, [])
            self.assertEqual(errors, [])
            project = discover_project(root)
            matrix = build_capability_matrix(project, [], [], {"cli": {"installed": False}})
            source_audit = next(item for item in matrix if item.name == "frontend_auditing")
            self.assertTrue(source_audit.available)
            self.assertEqual(source_audit.selected_tool, "Static source audit")

    def test_framework_detection_does_not_assume_react(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "package.json").write_text(json.dumps({"dependencies": {"vue": "^3.0.0"}}), encoding="utf-8")
            self.assertEqual(discover_project(root)["frameworks"], ["Vue"])

    def test_inline_package_script_secrets_are_redacted(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "package.json").write_text(json.dumps({"scripts": {"dev": "API_TOKEN=super-secret vite"}}), encoding="utf-8")
            command = discover_project(root)["application_commands"]["dev"]
            self.assertNotIn("super-secret", command)
            self.assertIn("[REDACTED]", command)

    def test_missing_codex_executable_is_reported_as_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            codex = discover_codex(root, codex_executable=str(root / "missing-codex"))
            self.assertFalse(codex["cli"]["installed"])
            self.assertFalse(codex["cli"]["authenticated"])

    def test_capability_matrix_distinguishes_installed_browser_from_rendered_evidence(self) -> None:
        discovery = {"source_file_count": 1, "frameworks": ["Static HTML"]}
        codex = {"cli": {"installed": True, "authenticated": True, "auth_mode": "chatgpt_plan", "codex_exec_supported": True, "structured_output_supported": True, "image_input_supported": True}}
        with patch("frontend_design_director.discovery.importlib.util.find_spec", return_value=object()):
            initial = build_capability_matrix(discovery, [], [], codex)
            captured = build_capability_matrix(discovery, [], [], codex, rendered_screenshots=["desktop.png"])
        browser_initial = next(item for item in initial if item.name == "browser_testing")
        self.assertFalse(browser_initial.available)
        self.assertEqual(browser_initial.status, "installed_unverified")
        browser_captured = next(item for item in captured if item.name == "browser_testing")
        visual_captured = next(item for item in captured if item.name == "visual_auditing")
        self.assertTrue(browser_captured.available)
        self.assertTrue(visual_captured.available)

    def test_skill_installer_skips_existing_user_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = _install_skill(root)
            target = root / ".agents" / "skills" / "frontend-design-director" / "SKILL.md"
            self.assertTrue(first["installed"])
            self.assertIn("human-approved design direction", target.read_text(encoding="utf-8"))
            target.write_text("user-owned skill", encoding="utf-8")
            second = _install_skill(root)
            self.assertFalse(second["installed"])
            self.assertEqual(target.read_text(encoding="utf-8"), "user-owned skill")

    def test_install_codex_installs_skill_and_agents_for_project_and_user(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project = root / "project"
            user_home = root / "user-home"
            project.mkdir()
            user_home.mkdir()

            output = io.StringIO()
            with redirect_stdout(output):
                status = main(["--no-update-check", "install-codex", "--project", str(project), "--json"])
            self.assertEqual(status, 0)
            project_result = json.loads(output.getvalue())
            self.assertEqual(project_result["scope"], "project")
            self.assertTrue(project_result["skill"]["installed"])
            self.assertEqual(len(project_result["agents"]["installed"]), 5)
            self.assertTrue((project / ".agents" / "skills" / "frontend-design-director" / "SKILL.md").is_file())
            self.assertTrue((project / ".codex" / "agents" / "frontend-code-auditor.toml").is_file())
            skills, _ = discover_skills(project)
            agents, _ = discover_agents(project)
            self.assertTrue(any(item["name"] == "frontend-design-director" for item in skills))
            project_agents = [item for item in agents if Path(item["source_path"]).is_relative_to(project.resolve())]
            self.assertEqual(len(project_agents), 5)

            existing_skill = project / ".agents" / "skills" / "frontend-design-director" / "SKILL.md"
            existing_skill.write_text("keep project-owned instructions", encoding="utf-8")
            project_again = _install_codex(project, "project")
            self.assertFalse(project_again["skill"]["installed"])
            self.assertEqual(project_again["agents"]["installed"], [])
            self.assertEqual(existing_skill.read_text(encoding="utf-8"), "keep project-owned instructions")

            output = io.StringIO()
            with patch("pathlib.Path.home", return_value=user_home), redirect_stdout(output):
                status = main(["--no-update-check", "install-codex", "--scope", "user", "--json"])
            self.assertEqual(status, 0)
            user_result = json.loads(output.getvalue())
            self.assertEqual(user_result["root"], str(user_home.resolve()))
            self.assertTrue(user_result["skill"]["installed"])
            self.assertEqual(len(user_result["agents"]["installed"]), 5)
            self.assertTrue((user_home / ".agents" / "skills" / "frontend-design-director" / "SKILL.md").is_file())
            self.assertTrue((user_home / ".codex" / "agents" / "frontend-code-auditor.toml").is_file())
            with patch("pathlib.Path.home", return_value=user_home):
                global_skills, _ = discover_skills(project)
                global_agents, _ = discover_agents(project)
            self.assertTrue(any(item["name"] == "frontend-design-director" and Path(item["source_path"]).is_relative_to(user_home.resolve()) for item in global_skills))
            self.assertEqual(len([item for item in global_agents if Path(item["source_path"]).is_relative_to(user_home.resolve())]), 5)

            custom_codex_home = root / "custom-codex-home"
            output = io.StringIO()
            with patch("pathlib.Path.home", return_value=user_home), patch.dict(os.environ, {"CODEX_HOME": str(custom_codex_home)}), redirect_stdout(output):
                status = main(["--no-update-check", "install-codex", "--scope", "user", "--json"])
            self.assertEqual(status, 0)
            custom_result = json.loads(output.getvalue())
            self.assertEqual(custom_result["agents"]["path"], str((custom_codex_home / "agents").resolve()))
            self.assertEqual(len(custom_result["agents"]["installed"]), 5)
            self.assertFalse(custom_result["skill"]["installed"])
            with patch("pathlib.Path.home", return_value=user_home), patch.dict(os.environ, {"CODEX_HOME": str(custom_codex_home)}):
                custom_agents, _ = discover_agents(project)
            self.assertEqual(len([item for item in custom_agents if Path(item["source_path"]).is_relative_to(custom_codex_home.resolve())]), 5)

            with patch("pathlib.Path.home", return_value=user_home), patch.dict(os.environ, {"CODEX_HOME": str(custom_codex_home)}):
                custom_uninstall = _uninstall_codex(project, "user")
            self.assertEqual(len(custom_uninstall["removed"]), 5)
            self.assertTrue((user_home / ".agents" / "skills" / "frontend-design-director" / "SKILL.md").is_file())

            with patch("pathlib.Path.home", return_value=user_home):
                default_uninstall = _uninstall_codex(project, "user")
            self.assertEqual(len(default_uninstall["removed"]), 6)
            self.assertFalse((user_home / ".agents" / "skills" / "frontend-design-director" / "SKILL.md").exists())

    def test_codex_uninstall_only_removes_unchanged_managed_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            project.mkdir()
            agents_directory = project / ".codex" / "agents"
            agents_directory.mkdir(parents=True)
            preexisting = agents_directory / "frontend-ux-auditor.toml"
            preexisting.write_text("user-owned agent", encoding="utf-8")

            install = _install_codex(project, "project")
            self.assertEqual(len(install["agents"]["installed"]), 4)
            manifest = Path(install["install_manifest"])
            self.assertTrue(manifest.is_file())
            modified = agents_directory / "frontend-visual-auditor.toml"
            modified.write_text("user-customized agent", encoding="utf-8")

            output = io.StringIO()
            with redirect_stdout(output):
                status = main(["--no-update-check", "uninstall-codex", "--scope", "project", "--project", str(project), "--yes", "--json"])
            self.assertEqual(status, 0)
            result = json.loads(output.getvalue())
            self.assertEqual(result["status"], "uninstalled_with_preserved_files")
            self.assertEqual(len(result["removed"]), 4)
            self.assertIn(str(modified.resolve()), result["preserved_modified"])
            self.assertTrue(preexisting.is_file())
            self.assertEqual(preexisting.read_text(encoding="utf-8"), "user-owned agent")
            self.assertEqual(modified.read_text(encoding="utf-8"), "user-customized agent")
            self.assertFalse(manifest.exists())
            self.assertEqual(_uninstall_codex(project, "project")["status"], "not_managed")

    def test_codex_uninstall_preserves_pre_manifest_files_without_ownership_record(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            skill = _install_skill(project)
            self.assertTrue(skill["installed"])
            result = _uninstall_codex(project, "project")
            self.assertEqual(result["status"], "not_managed")
            self.assertTrue(Path(skill["path"]).is_file())

    def test_state_and_skill_installers_reject_symlink_escape(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            project = base / "project"
            outside = base / "outside"
            project.mkdir()
            outside.mkdir()
            (project / ".agents").symlink_to(outside, target_is_directory=True)
            with self.assertRaises(ValueError):
                _store_for(project)
            (project / ".agents").unlink()
            state = project / WORKFLOW_STATE_DIRECTORY
            state.mkdir(parents=True)
            (state / "workflow.sqlite3").symlink_to(outside / "database.sqlite3")
            with self.assertRaises(ValueError):
                _store_for(project)
            (state / "workflow.sqlite3").unlink()
            state.rmdir()
            (project / ".agents").rmdir()
            (project / ".agents").symlink_to(outside, target_is_directory=True)
            with self.assertRaises(ValueError):
                _install_skill(project)
            self.assertEqual(list(outside.iterdir()), [])


class AuditAndStateTests(WorkflowTestCase):
    def test_findings_keep_evidence_and_visual_report_discloses_missing_rendered_evidence(self) -> None:
        discovery = discover_project(self.root)
        result = run_static_audit(self.root, discovery)
        self.assertTrue(any(item.category == "accessibility" and item.audit_type.value == "behavioral" for item in result.findings))
        reports = audit_reports(list(result.findings), result, discovery)
        self.assertIn(b"Visual appearance was not audited", reports["visual-audit.md"])
        findings = json.loads(reports["findings.json"])
        self.assertTrue(any(item["evidence"] for item in findings["findings"]))

    def test_structured_finding_validation_rejects_unknown_severity(self) -> None:
        with self.assertRaises(ValueError):
            Finding.from_dict({"id": "T-1", "audit_type": "technical", "category": "x", "severity": "urgent", "title": "t", "description": "d"})

    def test_audit_evidence_is_bound_to_snapshot_files_and_rendered_viewports(self) -> None:
        with create_project_snapshot(self.root) as snapshot:
            technical = Finding("T-1", AuditType.TECHNICAL, "architecture", "low", "Example", "Evidence test", evidence=(EvidenceReference("source", "index.html", "Visible landmark", line=1),))
            self.assertEqual(_validate_finding_evidence(technical, AuditType.TECHNICAL, snapshot, []).evidence[0].reference, "index.html")
            inventory = Finding("T-3", AuditType.TECHNICAL, "architecture", "low", "Inventory citation", "An inventory label still cites an included source file.", evidence=(EvidenceReference("inventory", "index.html", "The supplied inventory maps this claim to the included HTML source.", line=1),))
            self.assertEqual(_validate_finding_evidence(inventory, AuditType.TECHNICAL, snapshot, []).evidence[0].kind, "inventory")
            outside = Finding("T-2", AuditType.TECHNICAL, "architecture", "low", "Example", "Evidence test", evidence=(EvidenceReference("source", "../outside", "Unsupported evidence"),))
            with self.assertRaises(ValueError):
                _validate_finding_evidence(outside, AuditType.TECHNICAL, snapshot, [])
            visual = Finding("V-1", AuditType.VISUAL, "layout", "low", "Example", "Evidence test", evidence=(EvidenceReference("image", "desktop", "Visible layout", viewport="desktop"),))
            result = _validate_finding_evidence(visual, AuditType.VISUAL, snapshot, [{"viewport": "desktop", "path": "/session/desktop.png"}])
            self.assertEqual(result.evidence[0].reference, "/session/desktop.png")
            with self.assertRaises(ValueError):
                _validate_finding_evidence(visual, AuditType.VISUAL, snapshot, [{"viewport": "mobile", "path": "/session/mobile.png"}])

    def test_malformed_specialist_output_is_recorded_as_a_limitation(self) -> None:
        class MalformedBackend:
            available = True

            def execute(self, **kwargs):
                return {"findings": "not-an-array", "recommendations": [], "limitations": []}

        result = run_codex_audit(self.root, discover_project(self.root), backend=MalformedBackend())
        self.assertEqual(result.findings, ())
        self.assertTrue(any("did not return a valid structured result" in item for item in result.limitations))

    def test_invalid_transition_and_pause_resume_persist(self) -> None:
        with self.assertRaises(InvalidTransition):
            validate_transition(Phase.AUDIT_COMPLETED, Phase.IMPLEMENTING)
        session_id = self.make_audited_session()
        paused = self.director.pause(session_id)
        self.assertEqual(paused.phase, Phase.PAUSED)
        reopened = WorkflowStore(self.root / WORKFLOW_STATE_DIRECTORY / "workflow.sqlite3")
        resumed = FrontendDesignDirector(reopened, FakeBackend()).resume(session_id)
        self.assertEqual(resumed.phase, Phase.AUDIT_COMPLETED_WITH_LIMITATIONS)

    def test_interrupted_audit_can_resume_and_retry(self) -> None:
        session = self.director.create_session(self.root)
        self.director.discover(session.id)
        self.store.transition(session.id, Phase.AUDITING)
        self.director.pause(session.id)
        self.assertEqual(self.director.resume(session.id).phase, Phase.AUDITING)
        self.director.audit(session.id)
        self.assertEqual(self.store.get_session(session.id).phase, Phase.AUDIT_COMPLETED_WITH_LIMITATIONS)

    def test_failed_mockup_generation_can_resume_from_a_safe_retry_point(self) -> None:
        session_id = self.make_audited_session()
        self.director.record_direction(session_id, visual="refine", behavior="preserve", scope="screens", human_confirmation=True)
        with patch("frontend_design_director.director.create_template_mockup", side_effect=RuntimeError("transient failure")):
            with self.assertRaises(RuntimeError):
                self.director.generate_mockup(session_id)
        self.assertEqual(self.store.get_session(session_id).phase, Phase.FAILED)
        resumed = self.director.resume(session_id)
        self.assertEqual(resumed.phase, Phase.MOCKUP_REVISION)
        self.director.generate_mockup(session_id, revision_note="retry")
        self.assertEqual(self.store.get_session(session_id).phase, Phase.AWAITING_MOCKUP_REVIEW)

    def test_visual_and_behavior_decisions_are_separate_and_mockup_does_not_authorize_implementation(self) -> None:
        session_id = self.make_audited_session()
        with self.assertRaises(WorkflowBlocked):
            self.director.plan_implementation(session_id, files=["index.html"])
        self.director.record_direction(session_id, visual="explore", behavior="preserve", scope="screens", human_confirmation=True)
        direction_artifact = self.store.artifact(session_id, "design-direction")
        direction = json.loads(Path(direction_artifact["path"]).read_text(encoding="utf-8"))
        self.assertEqual(direction["visual_appearance"], "explore")
        self.assertEqual(direction["behavior_and_interaction"], "preserve")
        with patch("frontend_design_director.browser.playwright_available", return_value=False):
            manifest = self.director.generate_mockup(session_id)
        self.assertEqual(manifest["responsive_targets_px"], [1440, 768, 390])
        self.assertEqual(manifest["screenshots"], [])
        self.assertTrue(any("Mockup screenshots were unavailable" in item for item in manifest["limitations"]))
        css_artifact = self.store.artifact(session_id, "mockup-r001-styles_css")
        self.assertIn("@media", Path(css_artifact["path"]).read_text(encoding="utf-8"))
        self.director.review_mockup(session_id, action="approve", human_confirmation=True)
        self.assertEqual(self.store.get_session(session_id).phase, Phase.AWAITING_IMPLEMENTATION_APPROVAL)
        with self.assertRaises((WorkflowBlocked, KeyError)):
            self.director.approve_implementation(session_id, human_confirmation=True)
        with self.assertRaises(ValueError):
            Approval(session_id, "implementation", "implementation-plan", "sha", ("index.html",), "now", False)

    def test_revised_mockup_invalidates_old_plan_and_implementation_approval(self) -> None:
        session_id = self.make_audited_session()
        self.approve_direction_and_mockup(session_id)
        old_plan = self.director.plan_implementation(session_id, files=["index.html"])
        self.assertEqual(old_plan["approved_scope"], ["index.html"])
        self.director.review_mockup(session_id, action="revise", note="Reduce the card density.", human_confirmation=True)
        self.director.generate_mockup(session_id)
        self.director.review_mockup(session_id, action="approve", human_confirmation=True)
        with self.assertRaises(WorkflowBlocked):
            self.director.approve_implementation(session_id, human_confirmation=True)
        new_plan = self.director.plan_implementation(session_id, files=["index.html"])
        self.assertEqual(new_plan["specification_sha256"], self.store.artifact(session_id, "implementation-spec")["sha256"])
        authorization = self.director.approve_implementation(session_id, human_confirmation=True)
        self.assertEqual(authorization["status"], "authorized")
        self.assertEqual(self.store.get_session(session_id).phase, Phase.IMPLEMENTING)

    def test_stale_file_baseline_blocks_implementation_authorization(self) -> None:
        session_id = self.make_audited_session()
        self.approve_direction_and_mockup(session_id)
        self.director.plan_implementation(session_id, files=["index.html"])
        (self.root / "index.html").write_text("changed after planning", encoding="utf-8")
        with self.assertRaises(WorkflowBlocked):
            self.director.approve_implementation(session_id, human_confirmation=True)
        self.assertEqual(self.store.get_session(session_id).phase, Phase.AWAITING_IMPLEMENTATION_APPROVAL)

    def test_end_to_end_workflow_generates_and_applies_only_approved_patch(self) -> None:
        original = (self.root / "index.html").read_text(encoding="utf-8")
        session_id = self.make_audited_session()
        self.approve_direction_and_mockup(session_id)
        self.director.plan_implementation(session_id, files=["index.html"])
        with self.assertRaises(WorkflowBlocked):
            self.director.implement(session_id)
        self.director.approve_implementation(session_id, human_confirmation=True)
        patch = self.director.implement(session_id)
        self.assertEqual((self.root / "index.html").read_text(encoding="utf-8"), original)
        self.assertEqual(patch["changed_files"], ["index.html"])
        self.director.approve_patch_application(session_id, human_confirmation=True)
        self.director.apply_patch(session_id)
        self.assertIn("Approved update", (self.root / "index.html").read_text(encoding="utf-8"))
        result = self.director.verify(session_id, [f'{sys.executable} -c "print(1)"'])
        self.assertEqual(result["status"], "passed")
        self.assertEqual(self.store.get_session(session_id).phase, Phase.COMPLETED)
        self.assertTrue(self.store.artifact(session_id, "final_report")["path"].endswith("final-report.md"))

    def test_implementation_rtk_policy_survives_session_pause_and_resume(self) -> None:
        session_id = self.make_audited_session()
        self.approve_direction_and_mockup(session_id)
        self.director.plan_implementation(session_id, files=["index.html"])
        self.director.approve_implementation(session_id, human_confirmation=True)
        self.assertEqual(self.store.get_session(session_id).phase, Phase.IMPLEMENTING)

        self.director.pause(session_id)
        resumed = self.director.resume(session_id)
        self.assertEqual(resumed.phase, Phase.IMPLEMENTING)
        self.assertFalse(execution_policy_for_phase(resumed.phase).allow_rtk)

        self.director.implement(session_id)
        self.assertTrue(any(
            policy is not None and not policy.allow_rtk
            for policy in self.director.backend.execution_policies
        ))

    def test_cli_json_init_discover_audit_and_status_vertical_slice(self) -> None:
        from frontend_design_director.cli import main

        output = io.StringIO()
        safe_codex = {"cli": {"installed": False, "authenticated": False, "auth_mode": "unavailable"}, "mcp_servers": [], "plugins": []}
        with patch("frontend_design_director.director.discover_skills", return_value=([], [])), patch("frontend_design_director.director.discover_agents", return_value=([], [])), patch("frontend_design_director.director.discover_codex", return_value=safe_codex), redirect_stdout(output):
            self.assertEqual(main(["--no-update-check", "init", str(self.root), "--json"]), 0)
            created = json.loads(output.getvalue())
            self.assertEqual(created["phase"], "INITIALIZED")
            self.assertEqual(Path(created["state_dir"]), (self.root / WORKFLOW_STATE_DIRECTORY).resolve())
            self.assertTrue((self.root / WORKFLOW_STATE_DIRECTORY / "workflow.sqlite3").is_file())
            output.seek(0)
            output.truncate(0)
            self.assertEqual(main(["--no-update-check", "discover", "--project", str(self.root), "--json"]), 0)
            self.assertIn("capabilities", json.loads(output.getvalue()))
            output.seek(0)
            output.truncate(0)
            self.assertEqual(main(["--no-update-check", "audit", "--project", str(self.root), "--json"]), 0)
            self.assertEqual(json.loads(output.getvalue())["backend"], "static")
            output.seek(0)
            output.truncate(0)
            self.assertEqual(main(["--no-update-check", "status", "--project", str(self.root), "--json"]), 0)
            self.assertEqual(json.loads(output.getvalue())["phase"], "AUDIT_COMPLETED_WITH_LIMITATIONS")

    def test_legacy_workflow_database_is_copied_to_agents_without_deleting_original(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary).resolve() / "project"
            project.mkdir()
            legacy_state = project / LEGACY_WORKFLOW_STATE_DIRECTORY
            legacy_store = WorkflowStore(legacy_state / "workflow.sqlite3")
            legacy_session = legacy_store.create_session(project, legacy_state, "Existing session")

            migrated_store = _store_for(project)
            migrated_session = migrated_store.get_session(legacy_session.id)

            self.assertEqual(migrated_session.title, "Existing session")
            self.assertEqual(Path(migrated_session.state_dir), legacy_state.resolve())
            self.assertTrue((legacy_state / "workflow.sqlite3").is_file())
            self.assertTrue((project / WORKFLOW_STATE_DIRECTORY / "workflow.sqlite3").is_file())

            new_session = FrontendDesignDirector(migrated_store, FakeBackend()).create_session(project)
            self.assertEqual(Path(new_session.state_dir), (project / WORKFLOW_STATE_DIRECTORY).resolve())


class ImplementationSafetyTests(unittest.TestCase):
    def test_out_of_scope_patch_is_rejected_before_git_apply(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "index.html").write_text("<main>old</main>", encoding="utf-8")
            plan = {"approved_scope": ["index.html"], "baseline_sha256": {"index.html": hashlib.sha256((root / "index.html").read_bytes()).hexdigest()}}
            patch = b"outside scope"
            manifest = {"patch_sha256": hashlib.sha256(patch).hexdigest(), "changed_files": ["secret.txt"]}
            with self.assertRaises(ScopeViolation):
                apply_implementation_patch(root, patch, manifest, plan)
            self.assertFalse((root / "secret.txt").exists())

    def test_scope_rejects_traversal_and_new_file_collisions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "index.html").write_text("original", encoding="utf-8")
            with self.assertRaises(ValueError):
                create_implementation_plan(root, {}, files=["../outside.txt"])
            with self.assertRaises(ValueError):
                create_implementation_plan(root, {}, new_files=["index.html"])

    def test_codex_snapshot_omits_files_with_common_hardcoded_secret_assignments(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "src" / "page.js"
            source.parent.mkdir()
            source.write_text('const API_TOKEN = "do-not-send-this-secret";\n', encoding="utf-8")
            with create_project_snapshot(root, initialize_git=False) as snapshot:
                self.assertNotIn("src/page.js", snapshot.included_files)
                self.assertIn("src/page.js", snapshot.skipped_files)


class BrowserAndVerificationTests(unittest.TestCase):
    def test_standard_responsive_viewports_and_browser_degradation(self) -> None:
        self.assertEqual(VIEWPORTS["desktop"]["width"], 1440)
        self.assertEqual(VIEWPORTS["tablet"]["width"], 768)
        self.assertEqual(VIEWPORTS["mobile"]["width"], 390)
        with patch("frontend_design_director.browser.playwright_available", return_value=False):
            with self.assertRaises(BrowserUnavailable):
                capture_screenshots("http://localhost:3000", Path(tempfile.gettempdir()) / "unused")
            with self.assertRaises(BrowserUnavailable):
                capture_mockup_screenshots(Path(__file__), Path(tempfile.gettempdir()) / "unused-mockup")

    def test_verification_distinguishes_pass_and_not_verified(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            no_commands = run_verification(root, [])
            self.assertEqual(no_commands["status"], "not_verified")
            passed = run_verification(root, [f'{sys.executable} -c "print(1)"'])
            self.assertEqual(passed["status"], "passed")

    def test_codex_adapter_uses_saved_chatgpt_auth_and_strips_api_key_environment(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            executable = root / "fake-codex"
            executable.write_text(
                f"#!{sys.executable}\n"
                "import json, os, pathlib, sys\n"
                "if sys.argv[1:3] == ['login', 'status']:\n"
                "    print('Logged in using ChatGPT')\n"
                "    raise SystemExit(0)\n"
                "if '--skip-git-repo-check' not in sys.argv:\n"
                "    raise SystemExit(4)\n"
                "if any(name in os.environ for name in ('OPENAI_API_KEY', 'CODEX_API_KEY', 'GIT_DIR')):\n"
                "    raise SystemExit(3)\n"
                "output = pathlib.Path(sys.argv[sys.argv.index('--output-last-message') + 1])\n"
                "output.write_text(json.dumps({'result': 'ok'}), encoding='utf-8')\n",
                encoding="utf-8",
            )
            executable.chmod(0o700)
            backend = CodexCLIBackend(str(executable), CodexSettings())
            schema = {"type": "object", "properties": {"result": {"type": "string"}}, "required": ["result"], "additionalProperties": False}
            with patch.dict(os.environ, {"OPENAI_API_KEY": "must-not-forward", "CODEX_API_KEY": "must-not-forward", "GIT_DIR": "/outside/repository"}):
                result = backend.execute(working_directory=root, instruction="Return a small result.", schema=schema)
            self.assertEqual(result, {"result": "ok"})
        with patch.dict(os.environ, {"GIT_DIR": "/outside/repository", "GIT_WORK_TREE": "/outside/tree"}):
            git_environment = _git_environment()
        self.assertNotIn("GIT_DIR", git_environment)
        self.assertNotIn("GIT_WORK_TREE", git_environment)
        self.assertEqual(git_environment["GIT_CONFIG_NOSYSTEM"], "1")


if __name__ == "__main__":
    unittest.main()
