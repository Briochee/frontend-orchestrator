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

from frontend_design_director.browser import BrowserUnavailable, capture_screenshots
from frontend_design_director.director import FrontendDesignDirector
from frontend_design_director.discovery import discover_project
from frontend_design_director.guided import _prompt_action, run_guided_workflow
from frontend_design_director.auditing import AuditResult, VISUAL_FINDINGS_SCHEMA, _validated_visual_analysis, run_codex_audit
from frontend_design_director.intelligence import attach_runtime_evidence, build_project_intelligence, contrast_ratio, intelligence_reports, renderable_route_candidates, runtime_findings
from frontend_design_director.models import AuditType, EvidenceReference, Finding, Phase, Severity
from frontend_design_director.reporting import audit_reports
from frontend_design_director.server import DevelopmentServerError, managed_development_server
from frontend_design_director.storage import WORKFLOW_STATE_DIRECTORY, WorkflowStore


REPO_ROOT = Path(__file__).resolve().parents[1]
SAMPLE = REPO_ROOT / "examples" / "sample-frontend"


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
