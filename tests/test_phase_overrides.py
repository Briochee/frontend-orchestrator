from __future__ import annotations

import json
import io
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from contextlib import redirect_stdout

from frontend_design_director.director import FrontendDesignDirector, WorkflowBlocked, _validate_mockup_manifest
from frontend_design_director.cli import main
from frontend_design_director.guided import _parse_phase_override, run_guided_workflow
from frontend_design_director.models import Phase
from frontend_design_director.mockups import _validate_mockup
from frontend_design_director.storage import WORKFLOW_STATE_DIRECTORY, WorkflowStore


REPO_ROOT = Path(__file__).resolve().parents[1]
SAMPLE = REPO_ROOT / "examples" / "sample-frontend"


class MockupBackend:
    available = True

    def __init__(self) -> None:
        self.initial_files: set[str] | None = None

    def execute(self, *, working_directory, instruction, schema, **kwargs):
        root = Path(working_directory)
        self.initial_files = {item.name for item in root.iterdir() if item.is_file() and item.name != "approved-context.json"}
        (root / "index.html").write_text(
            "<!doctype html><html lang='en'><head><title>Orders</title></head><body>"
            "<nav aria-label='Primary'><a href='#orders'>Orders</a></nav><main id='orders'>"
            "<header><h1>Orders</h1><p>Track recent customer orders and fulfillment status.</p></header>"
            "<section aria-label='Order summary'><article><h2>Open orders</h2><p>24 orders need fulfillment.</p></article>"
            "<article><h2>Completed today</h2><p>18 orders shipped.</p></article></section>"
            "<section><h2>Recent orders</h2><table><thead><tr><th>Order</th><th>Status</th></tr></thead>"
            "<tbody><tr><td>#1042</td><td>Processing</td></tr></tbody></table>"
            "<button type='button'>View order</button></section></main></body></html>",
            encoding="utf-8",
        )
        (root / "styles.css").write_text(
            "body{font-family:system-ui}main{max-width:72rem;margin:auto}section{display:grid;gap:1rem}"
            "@media(max-width:768px){section{grid-template-columns:1fr}}"
            "@media(max-width:390px){main{padding:1rem}}",
            encoding="utf-8",
        )
        (root / "design-tokens.json").write_text(json.dumps({"schema_version": 1, "colors": {"accent": "#234"}}), encoding="utf-8")
        (root / "change-summary.md").write_text("Created an orders screen with summary cards and a recent-orders table.", encoding="utf-8")
        return {"status": "complete", "summary": "Created an orders interface mockup."}


class PhaseOverrideTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="frontend-director-phase-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "project"
        shutil.copytree(SAMPLE, self.root)
        self.store = WorkflowStore(self.root / WORKFLOW_STATE_DIRECTORY / "workflow.sqlite3")
        self.backend = MockupBackend()
        self.director = FrontendDesignDirector(self.store, self.backend)
        self.session = self.director.create_session(self.root)

    def _direction(self) -> None:
        result = self.director.override_phase(self.session.id, "direction", reason="User already selected a design direction.", source="cli")
        self.assertEqual(result["status"], "proceeding")
        self.director.record_direction(
            self.session.id, visual="refine", behavior="preserve", scope="screens",
            constraints="Keep the orders table and navigation.", human_confirmation=True,
        )

    def _mockup_files(self, folder: Path) -> None:
        folder.mkdir()
        (folder / "index.html").write_text(
            "<!doctype html><html lang='en'><head><title>Orders</title></head><body><nav>Orders</nav><main>"
            "<header><h1>Orders</h1><p>Track customer orders and fulfillment status across the workspace.</p></header>"
            "<section><article><h2>Open</h2><p>24 orders</p></article><article><h2>Shipped</h2><p>18 today</p></article></section>"
            "<section><h2>Recent orders</h2><table><tr><th>Order</th></tr><tr><td>#1042</td></tr></table></section>"
            "</main></body></html>", encoding="utf-8",
        )
        (folder / "styles.css").write_text(
            "main{max-width:72rem;margin:auto}@media(max-width:768px){main{padding:1rem}}"
            "@media(max-width:390px){main{padding:.5rem}}", encoding="utf-8",
        )

    def test_direction_can_be_entered_without_running_discovery_or_audit_and_is_typed(self) -> None:
        self._direction()
        direction = json.loads(Path(self.store.artifact(self.session.id, "design-direction")["path"]).read_text())
        self.assertEqual(self.store.get_session(self.session.id).phase, Phase.DIRECTION_APPROVED)
        self.assertEqual(direction["artifact_type"], "design_direction")
        self.assertEqual(direction["format"], "json")
        self.assertEqual(direction["source"], "human")
        override = self.store.get_session(self.session.id).metadata["phase_overrides"][-1]
        self.assertEqual(override["requested_phase"], "direction")
        self.assertEqual(override["override_source"], "cli")

    def test_direct_audit_entry_performs_only_required_discovery(self) -> None:
        result = self.director.override_phase(self.session.id, "audit", reason="Run the audit now.", source="cli")
        saved = self.store.get_session(self.session.id)
        self.assertEqual(result["current_phase"], Phase.AUDITING.value)
        self.assertIn("discovery", saved.metadata)
        self.assertNotIn("audit", saved.metadata)

    def test_verification_override_cannot_skip_patch_application(self) -> None:
        result = self.director.override_phase(self.session.id, "verification", reason="Verify the implementation.", source="cli")
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(self.store.get_session(self.session.id).phase, Phase.INITIALIZED)

    def test_mockup_generation_without_opted_in_generator_does_not_create_a_placeholder_or_advance(self) -> None:
        self._direction()
        with self.assertRaises(WorkflowBlocked):
            self.director.generate_mockup(self.session.id)
        self.assertEqual(self.store.get_session(self.session.id).phase, Phase.DIRECTION_APPROVED)
        self.assertFalse(list((Path(self.session.state_dir) / "mockups").rglob("*.html")))

    def test_codex_receives_direction_as_context_without_a_seed_html_scaffold(self) -> None:
        self._direction()
        self.director.override_phase(self.session.id, "mockup", reason="Generate the approved direction.", source="cli")
        with patch("frontend_design_director.browser.capture_mockup_screenshots", return_value=[]), patch.object(
            self.director, "_phase_collaboration",
            return_value=({"status": "completed", "plan": {"selected_experts": []}}, {"path": "mockup-review.json"}),
        ):
            manifest = self.director.generate_mockup(self.session.id, use_codex=True)
        self.assertEqual(self.backend.initial_files, set())
        self.assertIn("artifact_type", manifest)
        self.assertEqual(manifest["artifact_type"], "mockup")
        self.assertEqual(manifest["status"], "ready_for_review")
        self.assertEqual(manifest["source"], "codex_cli_isolated")
        self.assertEqual(manifest["direction_reference"]["name"], "design-direction")

    def test_scaffold_or_direction_summary_cannot_pass_mockup_validation(self) -> None:
        scaffold = {
            "index.html": b"<html><body><h1>Design Direction</h1><p>Improve typography and hierarchy.</p></body></html>",
            "styles.css": b"@media(max-width:768px){} @media(max-width:390px){}",
            "design-tokens.json": b'{"schema_version":1}',
            "change-summary.md": b"Design direction summary",
        }
        with self.assertRaisesRegex(ValueError, "actual interface"):
            _validate_mockup(scaffold)

    def test_legacy_template_artifact_is_preserved_but_cannot_be_reused_as_a_mockup(self) -> None:
        self._direction()
        state = Path(self.session.state_dir)
        legacy_html = state / "mockups" / "revision-001" / "index.html"
        legacy_html.parent.mkdir(parents=True)
        legacy_html.write_text("<html><body>Legacy direction scaffold</body></html>", encoding="utf-8")
        direction = self.store.artifact(self.session.id, "design-direction")
        self.store.write_artifact(self.session.id, "mockup-manifest", "mockups/manifest.json", json.dumps({
            "generation_mode": "template",
            "design_direction_sha256": direction["sha256"],
            "files": {},
        }).encode())

        with self.assertRaisesRegex(ValueError, "not explicitly identified"):
            _validate_mockup_manifest(self.store, self.session.id, json.loads(
                Path(self.store.artifact(self.session.id, "mockup-manifest")["path"]).read_text(encoding="utf-8")
            ))
        self.assertTrue(legacy_html.is_file())

    def test_existing_user_mockup_is_imported_for_review_not_auto_approved(self) -> None:
        self._direction()
        supplied = Path(self.temporary.name) / "supplied-mockup"
        self._mockup_files(supplied)
        result = self.director.override_phase(
            self.session.id, "planning", reason="Reuse my existing mockup.", source="cli",
            mockup_dir=supplied, human_confirmation=True,
        )
        self.assertEqual(result["status"], "awaiting_mockup_review")
        self.assertEqual(self.store.get_session(self.session.id).phase, Phase.AWAITING_MOCKUP_REVIEW)
        manifest = json.loads(Path(self.store.artifact(self.session.id, "mockup-manifest")["path"]).read_text())
        self.assertEqual(manifest["artifact_type"], "mockup")
        self.assertEqual(manifest["source"], "user_supplied")
        self.assertFalse(self.store.latest_valid_approval(self.session.id, "mockup", "mockup-manifest"))
        self.director.review_mockup(self.session.id, action="approve", human_confirmation=True)
        self.assertEqual(self.store.get_session(self.session.id).phase, Phase.AWAITING_IMPLEMENTATION_APPROVAL)
        self.assertIsNotNone(self.store.latest_valid_approval(self.session.id, "mockup", "mockup-manifest"))
        with self.assertRaises(KeyError):
            self.store.latest_valid_approval(self.session.id, "implementation", "implementation-plan")

    def test_registering_same_mockup_is_idempotent_and_changed_contents_create_a_new_revision(self) -> None:
        self._direction()
        supplied = Path(self.temporary.name) / "supplied-mockup"
        self._mockup_files(supplied)
        first = self.director.override_phase(
            self.session.id, "planning", reason="Select this existing mockup.", source="cli", mockup_dir=supplied,
        )
        self.assertEqual(first["status"], "awaiting_mockup_review")
        first_manifest = json.loads(Path(self.store.artifact(self.session.id, "mockup-manifest")["path"]).read_text())
        self.assertEqual(first_manifest["revision"], 1)

        repeated = self.director.override_phase(
            self.session.id, "planning", reason="Select the same existing mockup.", source="cli", mockup_dir=supplied,
        )
        self.assertEqual(repeated["status"], "awaiting_mockup_review")
        unchanged = json.loads(Path(self.store.artifact(self.session.id, "mockup-manifest")["path"]).read_text())
        self.assertEqual(unchanged["revision"], 1)
        self.director.review_mockup(self.session.id, action="approve", human_confirmation=True)

        approved_reuse = self.director.override_phase(
            self.session.id, "planning", reason="Reuse the approved mockup for planning.", source="cli", mockup_dir=supplied,
        )
        self.assertEqual(approved_reuse["status"], "proceeding")
        self.assertTrue(self.store.latest_valid_approval(self.session.id, "mockup", "mockup-manifest"))
        self.assertEqual(self.store.get_session(self.session.id).metadata["mockup_revision"], 1)

        (supplied / "index.html").write_text(
            (supplied / "index.html").read_text(encoding="utf-8").replace("Track customer orders", "Track priority customer orders"),
            encoding="utf-8",
        )
        changed = self.director.override_phase(
            self.session.id, "planning", reason="Use the revised existing mockup.", source="cli", mockup_dir=supplied,
        )
        self.assertEqual(changed["status"], "awaiting_mockup_review")
        revised = json.loads(Path(self.store.artifact(self.session.id, "mockup-manifest")["path"]).read_text())
        self.assertEqual(revised["revision"], 2)
        self.assertTrue((Path(self.session.state_dir) / "mockups" / "revision-001" / "index.html").is_file())
        self.assertFalse(self.store.latest_valid_approval(self.session.id, "mockup", "mockup-manifest"))

    def test_user_supplied_direction_is_typed_and_keeps_structured_specification(self) -> None:
        path = Path(self.temporary.name) / "direction.json"
        path.write_text(json.dumps({
            "artifact_type": "design_direction",
            "design_direction": {
                "intent": "Clarify the order management interface.",
                "visual_identity": {"tone": "calm and precise"},
                "layout": {"priority": "order queue"},
                "scope": "screens",
            },
        }), encoding="utf-8")
        result = self.director.override_phase(
            self.session.id, "mockup", reason="Use my supplied direction.", source="cli",
            direction_file=path, human_confirmation=True,
        )
        direction = json.loads(Path(self.store.artifact(self.session.id, "design-direction")["path"]).read_text())
        self.assertEqual(result["status"], "proceeding")
        self.assertEqual(direction["source"], "user_supplied")
        self.assertEqual(direction["artifact_type"], "design_direction")
        self.assertEqual(direction["specification"]["intent"], "Clarify the order management interface.")
        self.assertEqual(self.store.get_session(self.session.id).phase, Phase.DIRECTION_APPROVED)

    def test_implementation_override_cannot_bypass_human_approval(self) -> None:
        result = self.director.override_phase(self.session.id, "implementation", reason="Skip to implementation.", source="cli")
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(self.store.get_session(self.session.id).phase, Phase.INITIALIZED)
        self.assertTrue(result["approval_required"])

    def test_guided_explicit_overrides_are_parsed_and_ambiguous_mentions_are_ignored(self) -> None:
        self.assertEqual(_parse_phase_override("Skip the audit and go straight to mockup"), "mockup")
        self.assertEqual(_parse_phase_override("Skip the audit. Go directly to mockup."), "mockup")
        self.assertEqual(_parse_phase_override("Go back to design direction"), "direction")
        self.assertEqual(_parse_phase_override("Use my existing mockup and move to implementation planning"), "planning")
        self.assertEqual(_parse_phase_override("Override the current phase. Go to mockup generation now using what we already know."), "mockup")
        self.assertIsNone(_parse_phase_override("The mockup needs stronger typography"))

    def test_guided_override_uses_the_director_transition_and_persists_the_instruction(self) -> None:
        responses = iter(["Go directly to design direction", "end"])
        result = run_guided_workflow(self.director, self.store, self.session.id, input_fn=lambda _: next(responses), output_fn=lambda _: None)
        saved = self.store.get_session(self.session.id)
        self.assertEqual(result["status"], "ended")
        self.assertEqual(saved.phase, Phase.AWAITING_DIRECTION)
        override = saved.metadata["phase_overrides"][-1]
        self.assertEqual(override["override_source"], "guided")
        self.assertEqual(override["user_instruction"], "go directly to design direction")

    def test_phase_cli_emits_only_machine_readable_json(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            status = main([
                "--no-update-check", "phase", "--project", str(self.root), "--session", self.session.id,
                "--to", "direction", "--reason", "Use the supplied direction without an audit.", "--json",
            ])
        self.assertEqual(status, 0)
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["requested_phase"], "direction")
        self.assertTrue(payload["override_applied"])
        self.assertEqual(payload["current_phase"], Phase.AWAITING_DIRECTION.value)

    def test_phase_override_survives_pause_and_resume(self) -> None:
        self.director.override_phase(self.session.id, "direction", reason="Continue from known decisions.", source="cli")
        self.director.pause(self.session.id)
        resumed = self.director.resume(self.session.id)
        self.assertEqual(resumed.phase, Phase.AWAITING_DIRECTION)
        self.assertEqual(resumed.metadata["phase_overrides"][-1]["current_phase"], Phase.AWAITING_DIRECTION.value)


if __name__ == "__main__":
    unittest.main()
