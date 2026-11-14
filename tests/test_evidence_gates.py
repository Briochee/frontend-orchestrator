from __future__ import annotations

import json
import sys
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch

from frontend_design_director.auditing import (
    FINDINGS_SCHEMA,
    _execute_validated_with_retry,
    _analyze_html_sinks,
    _compact_project_intelligence,
    _validate_visual_assessment_coverage,
    _visual_findings_schema,
    _validated_response_findings,
    run_static_audit,
)
from frontend_design_director.codex_backend import (
    BackendFailure,
    CodexCLIBackend,
    CodexSettings,
    _codex_compatible_schema,
    _validate_schema,
)
from frontend_design_director.models import AuditType, Confidence, EvidenceReference, Finding, Severity, VerificationStatus
from frontend_design_director.browser import capture_screenshots
from frontend_design_director.director import FrontendDesignDirector, WorkflowBlocked, _codex_audit_limitations, _codex_audit_recommendations, _screenshot_integrity_error, _visual_review_covers_expected_pairs
from frontend_design_director.discovery import discover_project
from frontend_design_director.intelligence import build_project_intelligence, renderable_route_candidates
from frontend_design_director.auditing import AuditResult
from frontend_design_director.snapshot import create_project_snapshot
from frontend_design_director.storage import WORKFLOW_STATE_DIRECTORY, WorkflowStore


class CodexSchemaTests(unittest.TestCase):
    def test_optional_fields_become_required_nullable_recursively(self) -> None:
        schema = {
            "type": "object",
            "properties": {
                "person": {
                    "type": "object",
                    "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
                    "required": ["name"],
                },
                "items": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["person"],
        }
        compatible = _codex_compatible_schema(schema)
        self.assertEqual(compatible["required"], ["person", "items"])
        self.assertEqual(compatible["properties"]["person"]["required"], ["name", "age"])
        self.assertEqual(compatible["properties"]["person"]["properties"]["age"]["type"], ["integer", "null"])
        self.assertEqual(compatible["properties"]["items"]["type"], ["array", "null"])
        self.assertNotIn("$defs", compatible)

    def test_local_defs_refs_and_nested_refs_are_inlined(self) -> None:
        schema = {
            "$defs": {"Address": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}},
            "type": "object",
            "properties": {"address": {"$ref": "#/$defs/Address"}},
            "required": ["address"],
        }
        compatible = _codex_compatible_schema(schema)
        self.assertEqual(compatible["properties"]["address"]["properties"]["city"]["type"], "string")
        self.assertNotIn("$defs", compatible)

    def test_unresolvable_and_remote_refs_fail_with_schema_diagnostics(self) -> None:
        for reference in ("#/$defs/Missing", "https://example.invalid/schema.json"):
            with self.subTest(reference=reference), self.assertRaises(BackendFailure) as raised:
                _codex_compatible_schema({"type": "object", "properties": {"x": {"$ref": reference}}, "required": ["x"]})
            self.assertEqual(raised.exception.diagnostic["error_classification"], "invalid_schema")
            self.assertEqual(raised.exception.diagnostic["failure_location"], "schema.preflight")

    def test_compiled_production_findings_schema_validates_strict_response(self) -> None:
        compatible = _codex_compatible_schema(FINDINGS_SCHEMA)
        _validate_schema({"assessment": "Reviewed the output schema.", "assessment_evidence": [], "findings": [], "recommendations": [], "limitations": []}, compatible)
        with self.assertRaises(BackendFailure):
            _validate_schema({"assessment": "Reviewed.", "assessment_evidence": [], "findings": [], "recommendations": []}, compatible)
        with self.assertRaises(BackendFailure):
            _validate_schema({"assessment": "Reviewed.", "assessment_evidence": [], "findings": [], "recommendations": [], "limitations": [], "extra": True}, compatible)

    def test_invalid_top_level_schema_is_classified_before_invocation(self) -> None:
        backend = CodexCLIBackend("codex", CodexSettings())
        with tempfile.TemporaryDirectory() as temporary, patch.object(backend, "_require_chatgpt_plan_auth") as auth:
            with self.assertRaises(BackendFailure) as raised:
                backend.execute(working_directory=Path(temporary), instruction="return JSON", schema={"type": "string"})
        auth.assert_not_called()
        self.assertEqual(raised.exception.diagnostic["error_classification"], "invalid_schema")

    def test_image_argument_is_attached_and_recorded_in_invocation(self) -> None:
        backend = CodexCLIBackend("codex", CodexSettings())
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            image = root / "capture.png"
            image.write_bytes(b"\x89PNG\r\n\x1a\nimage bytes")
            with patch.object(backend, "_require_chatgpt_plan_auth"), patch.object(backend, "_cli_version", return_value="codex 1.2.3"), patch(
                "frontend_design_director.codex_backend.subprocess.run",
                return_value=CompletedProcess([], 0, stdout='{"ok": true}', stderr=""),
            ) as run:
                response = backend.execute(
                    working_directory=root,
                    instruction="Describe the attached screen.",
                    schema={"type": "object", "properties": {"ok": {"type": "boolean"}}, "required": ["ok"]},
                    images=(image,),
                    specialist="visual",
                )
        self.assertEqual(response, {"ok": True})
        command = run.call_args.args[0]
        self.assertIn("--image", command)
        self.assertIn(str(image), command)

    def test_backend_failure_preserves_redacted_complete_stderr(self) -> None:
        backend = CodexCLIBackend("codex", CodexSettings())
        complete_error = "ERROR: invalid_json_schema at properties.result.required: missing key `value`\n"
        with tempfile.TemporaryDirectory() as temporary, patch.object(backend, "_require_chatgpt_plan_auth"), patch.object(
            backend, "_cli_version", return_value="codex 1.2.3"
        ), patch("frontend_design_director.codex_backend.subprocess.run", return_value=CompletedProcess([], 1, stdout="", stderr=complete_error)):
            with self.assertRaises(BackendFailure) as raised:
                backend.execute(working_directory=Path(temporary), instruction="return JSON", schema={"type": "object", "properties": {}, "required": []}, specialist="code")
        self.assertEqual(raised.exception.diagnostic["error_classification"], "invalid_schema")
        self.assertEqual(raised.exception.diagnostic["relevant_stderr"], complete_error.strip())
        self.assertEqual(raised.exception.diagnostic["exit_status"], 1)

    def test_unsupported_image_is_rejected_before_model_invocation(self) -> None:
        backend = CodexCLIBackend("codex", CodexSettings())
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            image = root / "capture.gif"
            image.write_bytes(b"GIF89a data")
            with patch.object(backend, "_require_chatgpt_plan_auth") as auth:
                with self.assertRaises(BackendFailure) as raised:
                    backend.execute(working_directory=root, instruction="return JSON", schema={"type": "object", "properties": {}, "required": []}, images=(image,))
        auth.assert_not_called()
        self.assertEqual(raised.exception.diagnostic["error_classification"], "visual_analysis_unverified")


class HtmlSinkDataFlowTests(unittest.TestCase):
    def test_untrusted_flow_is_reported_while_constant_html_is_not(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "components.js").write_text(
                "export function show(message) {\n const node = document.querySelector('#notice');\n node.innerHTML = message;\n}\n"
                "export function fixedNotice() {\n const node = document.querySelector('#fixed');\n node.innerHTML = '<strong>Ready</strong>';\n}\n",
                encoding="utf-8",
            )
            (root / "settings.js").write_text(
                "const name = document.querySelector('#name').value;\nshow(`<strong>${name}</strong>`);\n",
                encoding="utf-8",
            )
            (root / "package.json").write_text('{"name":"flow-fixture"}', encoding="utf-8")
            traces = _analyze_html_sinks(root, list(root.glob("*.js")))
            result = run_static_audit(root, {"test_infrastructure": ["unit tests"], "styling": {}})

        self.assertEqual({item["assessment"] for item in traces}, {"user_controlled_unescaped", "constant_markup"})
        findings = [item for item in result.findings if item.category == "security_and_rendering"]
        self.assertEqual(len(findings), 1)
        self.assertTrue(any(item.reference == "settings.js" for item in findings[0].evidence))
        self.assertTrue(any(item.reference == "components.js" for item in findings[0].evidence))

    def test_local_literal_data_flow_is_documented_without_exploit_finding(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "data.js").write_text("export const records = [{name:'Example'}];\n", encoding="utf-8")
            (root / "list.js").write_text(
                "import {records} from './data.js';\nconst filtered = records.filter(item => item.name);\n"
                "function render() {\n body.innerHTML = filtered.map(item => `<span>${item.name}</span>`).join('');\n}\n",
                encoding="utf-8",
            )
            traces = _analyze_html_sinks(root, list(root.glob("*.js")))
        self.assertEqual(len(traces), 1)
        self.assertEqual(traces[0]["assessment"], "local_static_data")


class StructuredFindingTests(unittest.TestCase):
    def test_production_schema_and_snapshot_evidence_reject_invalid_citations(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "index.html"
            source.write_text("<main>content</main>\n", encoding="utf-8")
            with create_project_snapshot(root) as snapshot:
                self.assertIn("index.html", snapshot.included_files)
                finding = Finding(
                    id="TECH-1",
                    audit_type=AuditType.TECHNICAL,
                    category="architecture",
                    severity=Severity.LOW,
                    title="Evidence-bound claim",
                    description="A test finding cites the captured source file.",
                    evidence=(EvidenceReference("source", "index.html", "The inspected source contains the cited element.", line=1),),
                    confidence=Confidence.HIGH,
                    verification_status=VerificationStatus.STATIC_ANALYSIS,
                )
                response = {"findings": [finding.to_dict()], "recommendations": [], "limitations": []}
                valid = _validated_response_findings(response, AuditType.TECHNICAL, "code", snapshot, [])
                self.assertEqual(len(valid), 1)
                invalid_finding = Finding(
                    **{**finding.__dict__, "evidence": (EvidenceReference("source", "../private.txt", "This path is outside the snapshot."),)}
                )
                with self.assertRaises(ValueError):
                    _validated_response_findings(
                        {**response, "findings": [invalid_finding.to_dict()]},
                        AuditType.TECHNICAL,
                        "code",
                        snapshot,
                        [],
                    )


class AuditCompletenessTests(unittest.TestCase):
    def test_visual_completeness_uses_the_actual_specialist_run_and_assessed_pairs(self) -> None:
        runs = ({"specialist": "frontend_visual_auditor", "status": "completed"},)
        analysis = {"route_assessments": [
            {"route": "/", "viewport": "desktop"},
            {"route": "/settings/", "viewport": "mobile"},
        ]}
        expected = [("/", "desktop"), ("/settings/", "mobile")]

        self.assertTrue(_visual_review_covers_expected_pairs(runs, analysis, expected))
        self.assertFalse(_visual_review_covers_expected_pairs(runs, analysis, [*expected, ("/orders/", "tablet")]))
        self.assertFalse(_visual_review_covers_expected_pairs(
            ({"specialist": "frontend_visual_auditor", "status": "incomplete"},), analysis, expected,
        ))

    def test_codex_reports_replace_stale_static_only_gaps_after_evidence_passes(self) -> None:
        static_limitations = (
            "No project scripts, builds, dependency lifecycle hooks, or development servers were executed.",
            "No runtime, bundle-size, Web Vitals, network, or interaction measurements were collected.",
            "Source inspection cannot establish behavior on authenticated routes or runtime states.",
            "Screenshots were captured, but no visual evaluator was run; appearance findings remain unavailable.",
        )
        limitations = _codex_audit_limitations(
            static_limitations, (), visual_analysis_validated=True, runtime_observations=True,
        )
        self.assertFalse(any("no visual evaluator was run" in item.casefold() for item in limitations))
        self.assertFalse(any(item.startswith("No runtime,") for item in limitations))
        self.assertTrue(any("navigation timing and request data are single-run" in item for item in limitations))
        self.assertTrue(any("authenticated routes" in item for item in limitations))
        recommendations = _codex_audit_recommendations(
            ("Capture desktop (1440 px), tablet (768 px), and mobile (390 px) screenshots.", "Review findings."),
            (), visual_evidence_complete=True,
        )
        self.assertEqual(recommendations, ("Review findings.",))

    def test_codex_reports_keep_unresolved_static_only_gaps_when_visual_gate_fails(self) -> None:
        limitation = "Screenshots were captured, but no visual evaluator was run; appearance findings remain unavailable."
        self.assertIn(limitation, _codex_audit_limitations((limitation,), (), visual_analysis_validated=False, runtime_observations=False))
        recommendation = "Capture desktop (1440 px), tablet (768 px), and mobile (390 px) screenshots."
        self.assertIn(recommendation, _codex_audit_recommendations((recommendation,), (), visual_evidence_complete=False))

    def test_codex_audit_without_browser_evidence_is_incomplete_and_cannot_advance(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "index.html").write_text("<!doctype html><title>Fixture</title><main>Fixture</main>", encoding="utf-8")
            store = WorkflowStore(root / WORKFLOW_STATE_DIRECTORY / "workflow.sqlite3")
            director = FrontendDesignDirector(store)
            session = director.create_session(root)
            director.discover(session.id)
            with patch("frontend_design_director.director.run_codex_audit", return_value=AuditResult((), (), (), backend_used="codex_cli")):
                summary = director.audit(session.id, use_codex=True)
            self.assertEqual(summary["completion_status"], "incomplete")
            self.assertEqual(store.get_session(session.id).phase.value, "AUDIT_INCOMPLETE")
            self.assertTrue(summary["retry_recommendation"])
            with self.assertRaises(WorkflowBlocked):
                director.record_direction(session.id, visual="refine", behavior="preserve", scope="screens", human_confirmation=True)


class StructuredResponseRetryTests(unittest.TestCase):
    def test_deterministic_response_validation_retries_once_with_correction_context(self) -> None:
        responses = iter([{"citation": "bad"}, {"citation": "src/app.js:4"}])
        prompts: list[str] = []

        def execute(prompt: str) -> dict[str, str]:
            prompts.append(prompt)
            return next(responses)

        def validate(response: dict[str, str]) -> str:
            if response["citation"] == "bad":
                raise ValueError("citation line is beyond the end of src/app.js")
            return response["citation"]

        response, validated, retries = _execute_validated_with_retry(
            execute=execute, validate=validate, instruction="Return an evidence-backed response.",
        )

        self.assertEqual(response["citation"], "src/app.js:4")
        self.assertEqual(validated, "src/app.js:4")
        self.assertEqual(retries, 1)
        self.assertEqual(len(prompts), 2)
        self.assertIn("beyond the end of src/app.js", prompts[1])

    def test_provider_failures_are_not_retried_as_response_corrections(self) -> None:
        calls = 0

        def execute(_: str) -> dict[str, str]:
            nonlocal calls
            calls += 1
            raise BackendFailure("provider quota reached", diagnostic={
                "error_classification": "provider_quota_or_auth",
            })

        with self.assertRaises(BackendFailure):
            _execute_validated_with_retry(
                execute=execute, validate=lambda response: response, instruction="Review evidence.",
            )

        self.assertEqual(calls, 1)

    def test_execution_configuration_errors_are_not_retried(self) -> None:
        calls = 0

        def execute(_: str) -> dict[str, str]:
            nonlocal calls
            calls += 1
            raise ValueError("invalid sandbox configuration")

        with self.assertRaisesRegex(ValueError, "invalid sandbox configuration"):
            _execute_validated_with_retry(
                execute=execute, validate=lambda response: response, instruction="Review evidence.",
            )

        self.assertEqual(calls, 1)

    def test_report_labels_uninterpreted_and_incomplete_visual_evidence(self) -> None:
        from frontend_design_director.reporting import audit_reports

        result = AuditResult((), ("The visual auditor did not run.",), (), completion_status="incomplete")
        reports = audit_reports([], result, {"project_name": "fixture"})
        visual = reports["visual-audit.md"].decode()
        summary = reports["audit-summary.md"].decode()
        self.assertIn("Audit completion status: **incomplete**", visual)
        self.assertIn("Visual appearance was not audited", visual)
        self.assertIn("Audit completion status: **incomplete**", summary)


class RouteAndBrowserEvidenceTests(unittest.TestCase):
    def test_source_route_discovery_normalizes_dot_segments(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "index.html").write_text(
                '<a href="/analytics/../analytics/">Analytics</a><a href="/orders/">Orders</a><a href="/index.html">Home</a>', encoding="utf-8"
            )
            intelligence = build_project_intelligence(root, discover_project(root))
        routes = renderable_route_candidates(intelligence)
        self.assertIn("/analytics/", routes)
        self.assertIn("/orders/", routes)
        self.assertEqual(routes.count("/"), 1)
        self.assertNotIn("/index.html", routes)
        self.assertFalse(any(".." in route.split("/") for route in routes))

    def test_bad_route_does_not_abort_valid_capture_and_capture_records_actual_content(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "captures"

            observation = {
                "document": {"title": "Fixture", "width": 390, "height": 700, "readyState": "complete", "body_text_characters": 17, "visible_content_nodes": 2},
                "landmarks": {"main": 1}, "internal_links": [], "controls": {"buttons": 1, "inputs": 0},
                "computed_styles": {}, "navigation_timing": {},
            }

            class FakePage:
                url = "http://127.0.0.1:8765/"

                def set_default_navigation_timeout(self, _timeout: int) -> None:
                    pass

                def on(self, *_args: object) -> None:
                    pass

                def route(self, *_args: object) -> None:
                    pass

                def goto(self, _url: str, **_kwargs: object) -> SimpleNamespace:
                    return SimpleNamespace(status=200)

                def wait_for_load_state(self, *_args: object, **_kwargs: object) -> None:
                    pass

                def evaluate(self, script: str) -> object:
                    return True if "document.fonts" in script else observation

                def screenshot(self, *, path: str, **_kwargs: object) -> None:
                    png = b"\x89PNG\r\n\x1a\n" + (13).to_bytes(4, "big") + b"IHDR" + (390).to_bytes(4, "big") + (700).to_bytes(4, "big") + b"\x08\x02\x00\x00\x00"
                    Path(path).write_bytes(png)

            class FakeContext:
                def new_page(self) -> FakePage:
                    return FakePage()

                def close(self) -> None:
                    pass

            class FakeBrowser:
                def new_context(self, **_kwargs: object) -> FakeContext:
                    return FakeContext()

                def close(self) -> None:
                    pass

            class FakePlaywright:
                chromium = SimpleNamespace(launch=lambda **_kwargs: FakeBrowser())

            class Manager:
                def __enter__(self) -> FakePlaywright:
                    return FakePlaywright()

                def __exit__(self, *_args: object) -> None:
                    pass

            api = ModuleType("playwright.sync_api")
            api.sync_playwright = lambda: Manager()
            package = ModuleType("playwright")
            package.sync_api = api
            with patch("frontend_design_director.browser.playwright_available", return_value=True), patch.dict(sys.modules, {"playwright": package, "playwright.sync_api": api}):
                evidence = capture_screenshots(
                    "http://127.0.0.1:8765/",
                    output,
                    route_paths=["/../private"],
                    viewports=["mobile"],
                )
            captured_path = next(item["path"] for item in evidence if item["evidence_type"] == "rendered_browser_screenshot")
            path_exists_before_cleanup = Path(captured_path).is_file()
            capture_record = next(item for item in evidence if item["evidence_type"] == "rendered_browser_screenshot")
            self.assertIsNone(_screenshot_integrity_error(capture_record, Path(captured_path)))
            Path(captured_path).write_bytes(Path(captured_path).read_bytes() + b"tampered")
            self.assertIn("SHA-256", _screenshot_integrity_error(capture_record, Path(captured_path)))

        failure = next(item for item in evidence if item["evidence_type"] == "browser_navigation_failure")
        capture = next(item for item in evidence if item["evidence_type"] == "rendered_browser_screenshot")
        self.assertEqual(failure["error_classification"], "invalid_route")
        self.assertEqual(capture["visual_evidence_status"], "valid")
        self.assertGreater(capture["document"]["body_text_characters"], 0)
        self.assertEqual(capture["image_dimensions"]["width"], 390)
        self.assertTrue(path_exists_before_cleanup)


class VisualEvidenceValidationTests(unittest.TestCase):
    def test_visual_schema_citations_are_limited_to_attached_route_viewport_images(self) -> None:
        screenshots = [
            {"path": "/evidence/home-desktop.png", "route": "/", "viewport_label": "desktop"},
            {"path": "/evidence/settings-mobile.png", "route": "/settings/", "viewport_label": "mobile"},
        ]
        schema = _visual_findings_schema(screenshots)
        self.assertEqual(schema["properties"]["visual_analysis"]["properties"]["route_assessments"]["items"]["properties"]["route"]["enum"], ["/", "/settings/"])
        with self.assertRaises(ValueError):
            _validate_visual_assessment_coverage(
                {"route_assessments": [{"route": "/", "viewport": "desktop"}]}, screenshots
            )

    def test_specialist_metadata_is_bounded_without_dropping_behavioral_runtime_signals(self) -> None:
        intelligence = {
            "project": {"name": "fixture", "frameworks": []},
            "routes": [{"path": "/", "source": "index.html", "components": ["nav", "main"]}],
            "coverage": {"source_files_inspected": 4, "routes_discovered": 1, "routes_rendered": 1, "screenshots_captured": 1, "component_profiles": 200},
            "components": [{"name": f"profile-{index}", "source": "index.html", "evidence_kind": "static_html_structure"} for index in range(500)],
            "architecture": {"shared_components": []},
            "design_system": {},
            "runtime": [{
                "route": "/", "viewport_label": "mobile", "interaction_state": "default", "screenshot": "/evidence/home.png",
                "document": {"width": 520, "height": 900, "title": "Fixture"},
                "controls": {"buttons": 3}, "computed_styles": {"selector": {"value": "x" * 1000}},
                "page_errors": [], "console_errors": [], "failed_requests": [],
            } for _ in range(100)],
        }
        behavioral = _compact_project_intelligence(intelligence, AuditType.BEHAVIORAL, [])
        technical = _compact_project_intelligence(intelligence, AuditType.TECHNICAL, [])
        self.assertLess(len(json.dumps(behavioral)), 50_000)
        self.assertEqual(len(behavioral["runtime"]), 30)
        self.assertEqual(behavioral["runtime"][0]["controls"]["buttons"], 3)
        self.assertNotIn("runtime", technical)
        self.assertLess(len(json.dumps(technical)), 50_000)


if __name__ == "__main__":
    unittest.main()
