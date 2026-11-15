from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from frontend_design_director.codex_backend import BackendFailure, CodexCLIBackend
from frontend_design_director.execution import (
    IMPLEMENTATION_EXECUTION_POLICY,
    RTKExecutionBlocked,
    ExecutionPolicy,
    classify_failure,
    execution_policy_for_phase,
    instruction_with_execution_policy,
    run_process,
    tracked_operation,
)
from frontend_design_director.models import Phase
from frontend_design_director.storage import OperationBlocked, WORKFLOW_STATE_DIRECTORY, WorkflowStore


class ExecutionRecoveryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="frontend-director-execution-recovery-")
        self.addCleanup(self.temporary.cleanup)
        self.project = Path(self.temporary.name) / "project"
        self.project.mkdir()
        self.project = self.project.resolve()
        self.store = WorkflowStore(self.project / WORKFLOW_STATE_DIRECTORY / "workflow.sqlite3")
        self.session = self.store.create_session(self.project, self.project / WORKFLOW_STATE_DIRECTORY, "execution test")

    def _operation(self, *, inputs=None, environment=None, max_attempts=2):
        return tracked_operation(
            self.store,
            self.session.id,
            operation_name="implementation_plan",
            phase=Phase.AWAITING_IMPLEMENTATION_APPROVAL.value,
            project_root=str(self.project),
            inputs=inputs or {"specification_sha256": "spec-a"},
            environment=environment or {"provider": "test"},
            provider="test",
            max_attempts=max_attempts,
        )

    def test_deterministic_failure_is_remembered_and_changed_inputs_are_allowed(self) -> None:
        with self.assertRaisesRegex(ValueError, "invalid schema"):
            with self._operation() as operation:
                operation.set_result_reference({"artifact_name": "plan", "sha256": "unused"})
                raise ValueError("invalid schema supplied")

        called = False
        with self.assertRaisesRegex(OperationBlocked, "previously failed as invalid_schema"):
            with self._operation():
                called = True
        self.assertFalse(called)

        with self._operation(inputs={"specification_sha256": "spec-b"}) as operation:
            operation.set_result_reference({"artifact_name": "plan", "sha256": "new-result"})
        history = self.store.operation_history(self.session.id)
        self.assertEqual(history[0]["status"], "completed")
        self.assertEqual(history[0]["result_reference"]["sha256"], "new-result")
        self.assertGreaterEqual(self.store.operation_metrics(self.session.id)["suppressed_duplicates"], 1)

    def test_transient_failure_has_one_bounded_operation_retry(self) -> None:
        for _ in range(2):
            with self.assertRaises(ConnectionResetError):
                with self._operation():
                    raise ConnectionResetError("connection reset by peer")
        with self.assertRaisesRegex(OperationBlocked, "retry budget of 2"):
            with self._operation():
                self.fail("an exhausted operation must not execute again")
        self.assertEqual(classify_failure(ConnectionResetError("connection reset")).category, "transient_network")

    def test_duplicate_running_operation_is_suppressed(self) -> None:
        with self._operation():
            with self.assertRaisesRegex(OperationBlocked, "still running"):
                with self._operation():
                    self.fail("a duplicate operation must not execute")
        self.assertEqual(self.store.operation_metrics(self.session.id)["suppressed_duplicates"], 1)

    def test_exited_owner_is_recovered_once_instead_of_being_treated_as_running(self) -> None:
        first = self.store.begin_operation(
            self.session.id,
            operation_name="implementation_plan",
            operation_signature="same-inputs",
            input_fingerprint="inputs",
            environment_fingerprint="environment",
            phase="implementation_plan",
            provider="test",
            details={},
        )
        with self.store._connect() as connection:
            connection.execute("UPDATE operations SET owner_pid = ? WHERE id = ?", (999_999_999, first["operation_id"]))

        recovered = self.store.begin_operation(
            self.session.id,
            operation_name="implementation_plan",
            operation_signature="same-inputs",
            input_fingerprint="inputs",
            environment_fingerprint="environment",
            phase="implementation_plan",
            provider="test",
            details={},
        )
        self.assertEqual(recovered["attempt"], 2)
        self.assertEqual(self.store.operation_history(self.session.id)[1]["status"], "interrupted")
        self.store.finish_operation(self.session.id, recovered["operation_id"], status="completed")

    def test_tracked_subprocess_records_child_exit_and_preserves_all_output(self) -> None:
        command = [sys.executable, "-c", "import sys; print('full stdout'); print('full stderr', file=sys.stderr); sys.exit(7)"]
        with self._operation() as operation:
            result = run_process(command, capture_output=True, text=True, check=False)
            operation.set_result_reference({"purpose": "process result"})
        self.assertEqual((result.stdout, result.stderr, result.returncode), ("full stdout\n", "full stderr\n", 7))
        record = self.store.operation_history(self.session.id)[0]
        self.assertEqual(record["status"], "completed")
        self.assertEqual(record["exit_code"], 7)
        self.assertIsNone(record["process_pid"])

    def test_tracked_subprocess_preserves_stdin_bytes(self) -> None:
        command = [sys.executable, "-c", "import sys; sys.stdout.buffer.write(sys.stdin.buffer.read().upper())"]
        with self._operation():
            result = run_process(command, input=b"patch bytes", capture_output=True, check=False)
        self.assertEqual((result.stdout, result.returncode), (b"PATCH BYTES", 0))

    def test_implementation_rejects_rtk_without_rejecting_paths_containing_its_name(self) -> None:
        with self.assertRaises(RTKExecutionBlocked):
            run_process(["rtk", "git", "status"], policy=IMPLEMENTATION_EXECUTION_POLICY)

        completed = subprocess.CompletedProcess(["git", "diff", "--", "project-rtk-notes.md"], 0, "diff", "")
        with patch("frontend_design_director.execution.subprocess.run", return_value=completed) as native:
            result = run_process(["git", "diff", "--", "project-rtk-notes.md"], policy=IMPLEMENTATION_EXECUTION_POLICY)
        self.assertEqual(result.stdout, "diff")
        native.assert_called_once()
        self.assertEqual(native.call_args.args[0], ["git", "diff", "--", "project-rtk-notes.md"])

    def test_other_phases_keep_direct_command_runner_behavior(self) -> None:
        completed = subprocess.CompletedProcess(["rtk", "rg", "frontend"], 0, "matches", "")
        with patch("frontend_design_director.execution.subprocess.run", return_value=completed) as native:
            result = run_process(["rtk", "rg", "frontend"], policy=ExecutionPolicy(phase="audit", allow_rtk=True))
        self.assertEqual(result.stdout, "matches")
        native.assert_called_once()
        self.assertEqual(native.call_args.args[0], ["rtk", "rg", "frontend"])

    def test_failure_diagnostics_are_redacted_and_unknown_is_not_retryable(self) -> None:
        failure = classify_failure(RuntimeError("permission denied; token=secret-value"))
        self.assertEqual(failure.category, "permission_denied")
        self.assertFalse(failure.retryable)
        self.assertNotIn("secret-value", failure.diagnostic_summary)
        bearer = classify_failure(RuntimeError("Authorization: Bearer bearer-secret-value"))
        self.assertNotIn("bearer-secret-value", bearer.diagnostic_summary)
        unknown = classify_failure(RuntimeError("unclassified provider issue"))
        self.assertEqual((unknown.category, unknown.retryable), ("unknown", False))
        authorization = classify_failure(BackendFailure("secondary provider disabled", diagnostic={"error_classification": "blocked_by_permissions"}))
        self.assertEqual((authorization.category, authorization.retryable), ("permission_denied", False))
        provider_auth = classify_failure(BackendFailure("no verified saved login", diagnostic={"error_classification": "provider_quota_or_auth"}))
        self.assertEqual((provider_auth.category, provider_auth.retryable), ("provider_authentication", False))

    def test_failure_categories_separate_transient_and_deterministic_conditions(self) -> None:
        cases = [
            (FileNotFoundError("expected file missing"), "missing_file", False),
            (KeyError("Artifact not found: mockup"), "missing_artifact", False),
            (RuntimeError("unknown option --guess"), "invalid_cli_syntax", False),
            (RuntimeError("HTTP 503 service unavailable"), "transient_network", True),
            (subprocess.TimeoutExpired(["codex", "exec"], 5), "timeout", False),
            (subprocess.CalledProcessError(2, ["git", "apply"]), "command_failed", False),
        ]
        for error, expected_category, expected_retryable in cases:
            with self.subTest(error=type(error).__name__, category=expected_category):
                assessment = classify_failure(error)
                self.assertEqual((assessment.category, assessment.retryable), (expected_category, expected_retryable))

    def test_failure_ledger_retains_redacted_provider_diagnostics_and_invocation_shape(self) -> None:
        diagnostic = {
            "error_classification": "invalid_schema",
            "relevant_stderr": "invalid_json_schema token=private-value",
            "specialist": "frontend_code_auditor",
            "cli_version": "codex test",
            "retry_attempts": 0,
            "failure_location": "codex.exec.output_schema",
            "schema_validation_errors": ["schema token=private-value"],
            "invocation": {
                "executable": "/opt/private/codex",
                "arguments": ["exec", "--cd", "/Users/private/project", "--output-schema", "/tmp/schema.json"],
                "sandbox": "read-only",
                "model": "gpt-6-luna",
                "schema_sha256": "schema-hash",
                "images_attached": [],
            },
        }
        with self.assertRaises(BackendFailure):
            with self._operation():
                raise BackendFailure("invalid schema token=private-value", diagnostic=diagnostic)
        record = self.store.operation_history(self.session.id)[0]
        self.assertEqual(record["failure_category"], "invalid_schema")
        self.assertNotIn("private-value", record["relevant_stderr"])
        self.assertEqual(record["details"]["specialist"], "frontend_code_auditor")
        self.assertEqual(record["details"]["invocation"]["flags"], ["--cd", "--output-schema"])
        self.assertNotIn("/Users/private/project", json.dumps(record["details"]))

    def test_delegated_provider_receives_execution_discipline_and_implementation_rtk_rule(self) -> None:
        policy_text = instruction_with_execution_policy("Inspect the approved implementation plan.", execution_policy_for_phase(Phase.IMPLEMENTING))
        self.assertIn("do not repeat the same operation unchanged", policy_text)
        self.assertIn("never edit its SQLite workflow database directly", policy_text)
        self.assertIn("During the Frontend Design Director implementation phase, RTK is disabled", policy_text)

    def test_codex_retries_one_clear_transport_failure_without_rtk_wrapper(self) -> None:
        backend = CodexCLIBackend("codex")
        calls: list[list[str]] = []

        def fake_run(command, **kwargs):
            calls.append(command)
            if command[1:2] == ["exec"]:
                if len(calls) == 1:
                    return subprocess.CompletedProcess(command, 1, stdout="", stderr="connection reset by peer")
                output_path = Path(command[command.index("--output-last-message") + 1])
                output_path.write_text('{"ok":true}', encoding="utf-8")
                return subprocess.CompletedProcess(command, 0, stdout="", stderr="")
            raise AssertionError(f"Unexpected Codex command: {command}")

        schema = {"type": "object", "properties": {"ok": {"type": "boolean"}}, "required": ["ok"], "additionalProperties": False}
        with tempfile.TemporaryDirectory() as working_directory, patch.object(backend, "_require_chatgpt_plan_auth"), patch.object(
            backend, "_cli_version", return_value="codex test",
        ), patch("frontend_design_director.codex_backend.run_process", side_effect=fake_run), patch(
            "frontend_design_director.codex_backend.time.sleep",
        ) as sleep:
            with self._operation() as operation:
                operation.operation_name = "codex_specialist"
                value = backend.execute(working_directory=Path(working_directory), instruction="Return ok.", schema=schema)
        self.assertEqual(value, {"ok": True})
        self.assertEqual(sum(command[1:2] == ["exec"] for command in calls), 2)
        self.assertTrue(all(command[0] == "codex" for command in calls))
        sleep.assert_called_once_with(0.25)
        record = self.store.operation_history(self.session.id)[0]
        self.assertEqual(record["details"]["provider_retry_attempts"], 1)
        self.assertEqual(record["details"]["last_retry_category"], "transient_network")
        self.assertEqual(self.store.operation_metrics(self.session.id)["retries"], 1)

    def test_codex_does_not_retry_invalid_schema_or_quota_failures(self) -> None:
        schema = {"type": "object", "properties": {"ok": {"type": "boolean"}}, "required": ["ok"], "additionalProperties": False}
        for diagnostic, expected in (("invalid_json_schema: unsupported", "invalid_schema"), ("usage limit reached", "quota_exhausted")):
            backend = CodexCLIBackend("codex")
            calls: list[list[str]] = []

            def fake_run(command, **kwargs):
                calls.append(command)
                return subprocess.CompletedProcess(command, 1, stdout="", stderr=diagnostic)

            with tempfile.TemporaryDirectory() as working_directory, patch.object(backend, "_require_chatgpt_plan_auth"), patch.object(
                backend, "_cli_version", return_value="codex test",
            ), patch("frontend_design_director.codex_backend.run_process", side_effect=fake_run):
                with self.assertRaises(BackendFailure) as raised:
                    backend.execute(working_directory=Path(working_directory), instruction="Return ok.", schema=schema)
            self.assertEqual(raised.exception.diagnostic["error_classification"], expected)
            self.assertEqual(raised.exception.diagnostic["retry_attempts"], 0)
            self.assertEqual(len(calls), 1)
            self.assertTrue(all(command[0] == "codex" for command in calls))


if __name__ == "__main__":
    unittest.main()
