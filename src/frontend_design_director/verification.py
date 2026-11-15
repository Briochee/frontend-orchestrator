"""Explicit, user-selected verification commands and honest result reporting."""

from __future__ import annotations

import json
import shlex
import subprocess
import time
from pathlib import Path
from typing import Any

from .discovery import _clean_process_environment
from .execution import IMPLEMENTATION_EXECUTION_POLICY, ExecutionPolicy, RTKExecutionBlocked, run_process


def run_verification(
    project_root: Path,
    commands: list[str],
    *,
    timeout_seconds: int = 600,
    execution_policy: ExecutionPolicy | None = None,
) -> dict[str, Any]:
    """Run only exact commands explicitly supplied by the human and record pass/fail honestly."""
    execution_policy = execution_policy or IMPLEMENTATION_EXECUTION_POLICY
    if execution_policy.allow_rtk:
        raise ValueError("Implementation verification requires an execution policy with RTK disabled.")
    results: list[dict[str, Any]] = []
    for command in commands:
        arguments = shlex.split(command)
        if not arguments:
            raise ValueError("Verification command cannot be empty.")
        if any(token in {"&&", "||", ";", "|", ">", "<"} for token in arguments):
            raise ValueError("Use one executable invocation per --command; shell operators are not accepted.")
        start = time.monotonic()
        try:
            completed = run_process(
                arguments,
                policy=execution_policy,
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
                env=_clean_process_environment(),
            )
            status = "passed" if completed.returncode == 0 else "failed"
            return_code = completed.returncode
            stdout = _process_text(completed.stdout)
            stderr = _process_text(completed.stderr)
            error_category = None
            error_message = None
        except RTKExecutionBlocked as error:
            status, return_code = "failed", None
            stdout, stderr = "", ""
            error_category, error_message = "rtk_disabled", str(error)
        except subprocess.TimeoutExpired as error:
            status, return_code = "failed", None
            stdout = _process_text(getattr(error, "stdout", None) or getattr(error, "output", None))
            stderr = _process_text(getattr(error, "stderr", None))
            error_category, error_message = "timeout", f"Command exceeded {timeout_seconds} seconds."
        except OSError as error:
            status, return_code = "failed", None
            stdout, stderr = "", ""
            error_category, error_message = type(error).__name__, str(error)
        result = {
            "command": arguments[0],
            "status": status,
            "return_code": return_code,
            "duration_seconds": round(time.monotonic() - start, 3),
            "stdout": stdout,
            "stderr": stderr,
        }
        if error_category:
            result["error_category"] = error_category
        if error_message:
            result["error_message"] = error_message
        results.append(result)
    return {
        "schema_version": 1,
        "status": "not_verified" if not commands else "passed" if all(item["status"] == "passed" for item in results) else "failed",
        "commands_requested": len(commands),
        "results": results,
        "limitations": [] if commands else ["No verification commands were explicitly supplied; functional, accessibility, and performance verification remain unverified."],
    }


def _process_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    return value.decode("utf-8", errors="replace") if isinstance(value, bytes) else value


def verification_reports(result: dict[str, Any], *, changed_files: list[str], approved_scope: list[str]) -> dict[str, bytes]:
    """Create a structured final report with verified and unverified requirements separated."""
    lines = [
        "# Final frontend implementation report", "",
        f"Verification status: **{result['status'].replace('_', ' ')}**", "",
        "## Implemented changes", "",
    ]
    lines.extend(f"- `{path}`" for path in changed_files)
    if not changed_files:
        lines.append("No production file changes were applied.")
    outside = sorted(set(changed_files) - set(approved_scope))
    lines.extend(["", "## Approved scope compliance", ""])
    lines.append("All applied file paths are within the approved scope." if not outside else f"Files outside scope: {', '.join(outside)}")
    lines.extend(["", "## Tests and verification", ""])
    if result["results"]:
        for item in result["results"]:
            suffix = f" (exit {item['return_code']})" if item.get("return_code") is not None else ""
            lines.append(f"- `{item['command']}`: **{item['status']}**{suffix}; {item['duration_seconds']:.2f}s")
    else:
        lines.append("No test or verification commands were run.")
    collaboration = result.get("collaboration_review")
    if isinstance(collaboration, dict):
        lines.extend(["", "## Independent review", ""])
        lines.append(f"Codex review status: **{str(collaboration.get('status', 'unknown')).replace('_', ' ')}**")
        if collaboration.get("report_path"):
            lines.append(f"Structured review artifact: `{collaboration['report_path']}`")
        if collaboration.get("status") == "not_requested":
            lines.append("No model review was requested; the recorded command results remain the verification evidence.")
    lines.extend(["", "## Visual, accessibility, and performance verification", "", "These areas are verified only when a corresponding browser, accessibility, or performance command was explicitly supplied and its result is recorded. The orchestrator does not infer success from source changes."])
    if result["limitations"]:
        lines.extend(["", "## Remaining unverified work", ""])
        lines.extend(f"- {item}" for item in result["limitations"])
    report = "\n".join(lines) + "\n"
    return {"verification.json": json.dumps(result, indent=2, sort_keys=True).encode(), "final-report.md": report.encode()}
