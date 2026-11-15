from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from frontend_design_director.codex_backend import CodexCLIBackend
from frontend_design_director.collaboration import CollaborationMode, run_phase_collaboration
from frontend_design_director.execution import (
    IMPLEMENTATION_EXECUTION_POLICY,
    ExecutionPolicy,
    RTKExecutionBlocked,
    codex_execution_rules,
    execution_policy_for_phase,
    run_process,
)
from frontend_design_director.implementation import execute_implementation
from frontend_design_director.providers import ClaudeCodeBackend
from frontend_design_director.verification import run_verification


class ExecutionPolicyTests(unittest.TestCase):
    def test_policy_is_scoped_to_implementation_related_phases(self) -> None:
        for phase in ("implement", "IMPLEMENTING", "applying", "verifying", "paused"):
            kwargs = {"paused_from": "IMPLEMENTING"} if phase == "paused" else {}
            self.assertFalse(execution_policy_for_phase(phase, **kwargs).allow_rtk, phase)
        for phase in ("audit", "planning", "mockup", "discovery"):
            self.assertTrue(execution_policy_for_phase(phase).allow_rtk, phase)

    def test_direct_rtk_and_env_wrapped_rtk_are_rejected_before_launch(self) -> None:
        commands = (
            ["rtk", "git", "status"],
            ["/opt/homebrew/bin/rtk", "git", "diff"],
            ["env", "RTK_TEST=1", "rtk", "git", "status"],
            ["/usr/bin/env", "--", "/opt/homebrew/bin/rtk", "--help"],
            [sys.executable, "-m", "rtk", "git", "diff"],
        )
        with patch("frontend_design_director.execution.subprocess.run") as run:
            for command in commands:
                with self.subTest(command=command), self.assertRaises(RTKExecutionBlocked):
                    run_process(command, policy=IMPLEMENTATION_EXECUTION_POLICY)
        run.assert_not_called()

    @unittest.skipUnless(os.name != "nt" and Path("/bin/sh").exists(), "requires a POSIX shell")
    def test_path_shim_blocks_nested_bare_rtk_calls_and_preserves_native_output(self) -> None:
        blocked = run_process(
            ["/bin/sh", "-c", "rtk --version"],
            policy=IMPLEMENTATION_EXECUTION_POLICY,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(blocked.returncode, 126)
        self.assertIn("RTK is disabled", blocked.stderr)

        native = run_process(
            ["/bin/sh", "-c", "printf out; printf err >&2; exit 7"],
            policy=IMPLEMENTATION_EXECUTION_POLICY,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual((native.stdout, native.stderr, native.returncode), ("out", "err", 7))

    def test_codex_rule_is_temporary_and_does_not_change_other_phases(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with codex_execution_rules(root, IMPLEMENTATION_EXECUTION_POLICY) as rule_path:
                self.assertIsNotNone(rule_path)
                self.assertIn('pattern = ["rtk"]', rule_path.read_text(encoding="utf-8"))
                self.assertIn('decision = "forbidden"', rule_path.read_text(encoding="utf-8"))
            self.assertFalse((root / ".codex" / "rules").exists())

            with codex_execution_rules(root, execution_policy_for_phase("audit")) as rule_path:
                self.assertIsNone(rule_path)
            self.assertFalse((root / ".codex").exists())

    def test_rtk_text_in_paths_is_not_mistaken_for_the_executable(self) -> None:
        completed = subprocess.CompletedProcess(
            ["git", "diff", "--", "project-rtk-notes.md"], 0, stdout="native out", stderr="native err",
        )
        with patch("frontend_design_director.execution.subprocess.run", return_value=completed) as run:
            result = run_process(
                ["git", "diff", "--", "project-rtk-notes.md"],
                policy=IMPLEMENTATION_EXECUTION_POLICY,
                capture_output=True,
                text=True,
            )
        self.assertEqual(run.call_args.args[0], ["git", "diff", "--", "project-rtk-notes.md"])
        self.assertEqual((result.stdout, result.stderr, result.returncode), ("native out", "native err", 0))

    def test_audit_policy_keeps_existing_command_behavior(self) -> None:
        completed = subprocess.CompletedProcess(["rtk", "--version"], 0, stdout="RTK 1.2.0", stderr="")
        audit_policy = execution_policy_for_phase("audit")
        with patch("frontend_design_director.execution.subprocess.run", return_value=completed) as run:
            result = run_process(["rtk", "--version"], policy=audit_policy)
        run.assert_called_once_with(["rtk", "--version"])
        self.assertEqual(result.stdout, "RTK 1.2.0")

    def test_implementation_exec_uses_native_git_and_propagates_policy_to_backend(self) -> None:
        class Backend:
            available = True

            def __init__(self) -> None:
                self.call: dict[str, object] = {}

            def execute(self, **kwargs):
                self.call = kwargs
                target = kwargs["working_directory"] / "index.html"
                target.write_text("<!doctype html><title>updated</title>\n", encoding="utf-8")
                return {"status": "complete", "summary": "Updated the approved page."}

        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            original = project / "index.html"
            original.write_text("<!doctype html><title>before</title>\n", encoding="utf-8")
            plan = {
                "approved_scope": ["index.html"],
                "baseline_sha256": {"index.html": hashlib.sha256(original.read_bytes()).hexdigest()},
                "specification": {"sha256": "approved-spec"},
                "summary": "Update title",
                "files": [{"path": "index.html"}],
                "new_files": [],
            }
            backend = Backend()
            patch_bytes, manifest = execute_implementation(project, plan, backend=backend)

        self.assertIn(b"updated", patch_bytes)
        self.assertEqual(manifest["changed_files"], ["index.html"])
        self.assertIs(backend.call["execution_policy"], IMPLEMENTATION_EXECUTION_POLICY)
        self.assertIn("RTK is disabled", backend.call["instruction"])
        self.assertEqual(backend.call["sandbox"], "workspace-write")

    def test_codex_implementation_backend_runs_directly_with_guarded_child_path(self) -> None:
        backend = CodexCLIBackend("codex")
        calls: list[dict[str, object]] = []

        def fake_run(command, **kwargs):
            path = Path(kwargs["env"]["PATH"].split(os.pathsep)[0]) / "rtk"
            rule_files = list((Path(kwargs["cwd"]) / ".codex" / "rules").glob("frontend-director-no-rtk-*.rules"))
            calls.append({"command": command, "shim_exists": path.is_file(), "policy_rule_exists": len(rule_files) == 1, **kwargs})
            output_path = Path(command[command.index("--output-last-message") + 1])
            output_path.write_text('{"ok":true}', encoding="utf-8")
            return subprocess.CompletedProcess(command, 0, stdout="raw stdout", stderr="raw stderr")

        schema = {
            "type": "object",
            "properties": {"ok": {"type": "boolean"}},
            "required": ["ok"],
            "additionalProperties": False,
        }
        with tempfile.TemporaryDirectory() as temporary, patch.object(backend, "_require_chatgpt_plan_auth"), patch.object(
            backend, "_cli_version", return_value="codex test",
        ), patch("frontend_design_director.execution.subprocess.run", side_effect=fake_run):
            response = backend.execute(
                working_directory=Path(temporary),
                instruction="Implement the approved file.",
                schema=schema,
                sandbox="workspace-write",
                execution_policy=IMPLEMENTATION_EXECUTION_POLICY,
            )

        self.assertEqual(response, {"ok": True})
        self.assertEqual(len(calls), 1)
        command = calls[0]["command"]
        self.assertEqual(command[0:2], ["codex", "exec"])
        self.assertIn("RTK is disabled", calls[0]["input"])
        self.assertTrue(calls[0]["shim_exists"])
        self.assertTrue(calls[0]["policy_rule_exists"])
        self.assertFalse((Path(calls[0]["cwd"]) / ".codex" / "rules").exists())

    def test_claude_read_only_backend_receives_policy_without_enabling_shell_tools(self) -> None:
        backend = ClaudeCodeBackend("claude", authorized_secondary_provider=True)
        flags = "-p --output-format --json-schema --permission-mode --tools --disallowedTools --setting-sources --strict-mcp-config --mcp-config"
        results = [
            subprocess.CompletedProcess([], 0, stdout=flags, stderr=""),
            subprocess.CompletedProcess([], 0, stdout='{"loggedIn":true}', stderr=""),
            subprocess.CompletedProcess([], 0, stdout='{"structured_output":{"ok":true}}', stderr=""),
        ]
        calls: list[dict[str, object]] = []

        def fake_run(command, **kwargs):
            calls.append({"command": command, **kwargs})
            return results.pop(0)

        with tempfile.TemporaryDirectory() as temporary, patch(
            "frontend_design_director.providers.run_process", side_effect=fake_run,
        ):
            response = backend.execute(
                working_directory=Path(temporary),
                instruction="Review implementation evidence.",
                schema={"type": "object", "properties": {"ok": {"type": "boolean"}}, "required": ["ok"], "additionalProperties": False},
                sandbox="read-only",
                execution_policy=IMPLEMENTATION_EXECUTION_POLICY,
            )

        self.assertEqual(response, {"ok": True})
        self.assertEqual(len(calls), 3)
        self.assertTrue(all(call["policy"] is IMPLEMENTATION_EXECUTION_POLICY for call in calls))
        self.assertEqual(calls[-1]["command"][0], "claude")
        self.assertIn("RTK is disabled", calls[-1]["command"][2])
        self.assertIn("--disallowedTools", calls[-1]["command"])
        self.assertNotIn("Bash", calls[-1]["command"])

    def test_implementation_collaboration_passes_policy_to_specialist_and_reviewer(self) -> None:
        class Backend:
            available = True
            provider_id = "codex"

            def __init__(self) -> None:
                self.calls = []

            def execute(self, **kwargs):
                self.calls.append(kwargs)
                if "cross_disciplinary_reviewer" in kwargs["specialist"]:
                    return {"challenges": [], "unresolved_questions": [], "limitations": []}
                return {
                    "summary": "Reviewed implementation evidence.",
                    "observations": [{
                        "id": "scope", "title": "Scoped change", "description": "Only an approved file is represented.",
                        "evidence_references": ["patch:index.html"], "confidence": "high", "impact": "Preserves scope.",
                        "recommendation": "Keep the change scoped.", "tradeoffs": [],
                    }],
                    "limitations": [], "unresolved_questions": [],
                }

        with tempfile.TemporaryDirectory() as temporary:
            backend = Backend()
            result = run_phase_collaboration(
                phase="implementation",
                mode=CollaborationMode.COMPREHENSIVE,
                plan={
                    "selected_experts": [
                        {"role": "technical_architecture", "provider": "codex"},
                        {"role": "cross_disciplinary_reviewer", "provider": "codex"},
                    ],
                    "limits": {"max_independent_specialists": 1},
                },
                evidence={"patch:index.html": {"changed": True}},
                evidence_manifest={},
                backend=backend,
                working_directory=Path(temporary),
            )

        self.assertEqual(result["status"], "completed")
        self.assertEqual(len(backend.calls), 2)
        for call in backend.calls:
            self.assertIs(call["execution_policy"], IMPLEMENTATION_EXECUTION_POLICY)
            self.assertIn("RTK is disabled", call["instruction"])

    def test_verification_rejects_rtk_with_json_result_and_preserves_native_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary, patch("frontend_design_director.execution.subprocess.run") as run:
            blocked = run_verification(
                Path(temporary), ["rtk git status"],
            )
            run.assert_not_called()
        self.assertEqual(blocked["status"], "failed")
        self.assertEqual(blocked["results"][0]["error_category"], "rtk_disabled")
        self.assertIn("invoke the native command directly", blocked["results"][0]["error_message"])
        json.loads(json.dumps(blocked))

        command = (
            f'{sys.executable} -c '
            '"import sys; print(\'full stdout\'); print(\'full stderr\', file=sys.stderr); sys.exit(7)"'
        )
        with tempfile.TemporaryDirectory() as temporary:
            result = run_verification(Path(temporary), [command], execution_policy=IMPLEMENTATION_EXECUTION_POLICY)
        self.assertEqual(result["results"][0]["return_code"], 7)
        self.assertEqual(result["results"][0]["stdout"], "full stdout\n")
        self.assertEqual(result["results"][0]["stderr"], "full stderr\n")
        self.assertEqual(result["status"], "failed")


if __name__ == "__main__":
    unittest.main()
