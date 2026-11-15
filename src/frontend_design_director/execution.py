"""Phase-aware command execution safeguards."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import sqlite3
import subprocess
import tempfile
from contextlib import contextmanager
from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator, Sequence


IMPLEMENTATION_NO_RTK_INSTRUCTION = (
    "During the Frontend Design Director implementation phase, RTK is disabled. Do not invoke `rtk`, "
    "prefix terminal commands with `rtk`, or delegate work that does so. Run native executables directly. "
    "This applies to implementation, Git inspection, patch review, tests, retries, and verification. "
    "Preserve complete native stdout, stderr, structured JSON, and exit status without command wrappers or output transformations. "
    "This policy does not authorize extra commands or change existing permissions, scope, or approval requirements."
)
EXECUTION_DISCIPLINE_INSTRUCTION = (
    "Use supplied reports, artifacts, and command results before collecting them again. "
    "Every command must have a clear purpose and an observable expected result. After a failure, use its actual exit status and stderr to classify the cause; do not repeat the same operation unchanged or guess command syntax. "
    "Inspect the supported interface once and make one materially corrected attempt. Reattach to or await a recorded running operation instead of launching a duplicate. "
    "Use the public Frontend Design Director CLI for phase changes and artifact registration; never edit its SQLite workflow database directly. "
    "Run Frontend Design Director commands, JSON-producing commands, Codex/Claude, arbitrary Python, state changes, and commands requiring full diagnostics directly without RTK. "
    "RTK may be used only for supported read-only repository inspection when transformed output is sufficient; it is prohibited during implementation, patch application, and implementation verification."
)


@dataclass(frozen=True)
class ExecutionPolicy:
    """Execution constraints propagated through one workflow phase."""

    phase: str
    allow_rtk: bool = True


IMPLEMENTATION_EXECUTION_POLICY = ExecutionPolicy(phase="implement", allow_rtk=False)
IMPLEMENTATION_CODEX_RULE = '''prefix_rule(
    pattern = ["rtk"],
    decision = "forbidden",
    justification = "RTK is disabled during Frontend Design Director implementation; run the native command directly.",
)
'''


class RTKExecutionBlocked(RuntimeError):
    """Raised when a Frontend Design Director child process tries to launch RTK."""


@dataclass(frozen=True)
class FailureAssessment:
    category: str
    retryable: bool
    retry_condition: str
    diagnostic_summary: str
    relevant_stderr: str = ""


@dataclass
class OperationAttempt:
    """Persistent identity and process callbacks for one orchestrated operation."""

    store: Any = field(repr=False)
    session_id: str
    operation_id: str
    operation_name: str
    operation_signature: str
    attempt: int
    previous: dict[str, Any] | None = None
    result_reference: dict[str, Any] | None = None
    process_id: int | None = None
    result_reused: bool = False
    failure_assessment: FailureAssessment | None = None

    def process_started(self, process_id: int) -> None:
        self.process_id = process_id
        self.store.update_operation_process(self.session_id, self.operation_id, process_id)

    def process_finished(self, exit_code: int | None) -> None:
        self.process_id = None
        self.store.update_operation_process(self.session_id, self.operation_id, None, exit_code=exit_code)

    def process_interrupted(self, process_id: int) -> None:
        self.process_id = process_id
        self.store.update_operation_process(self.session_id, self.operation_id, process_id)

    def record_details(self, details: dict[str, Any]) -> None:
        self.store.update_operation_details(self.session_id, self.operation_id, details)

    def set_result_reference(self, reference: dict[str, Any]) -> None:
        self.result_reference = reference

    def mark_result_reused(self, reference: dict[str, Any]) -> None:
        self.result_reference = reference
        self.result_reused = True

    def mark_failed_result(self, category: str, summary: str, retry_condition: str, *, relevant_stderr: str = "") -> None:
        """Record a completed command whose requested outcome was unsuccessful."""
        self.failure_assessment = FailureAssessment(
            category=category,
            retryable=False,
            retry_condition=retry_condition,
            diagnostic_summary=_redact_diagnostic(summary)[:500],
            relevant_stderr=_redact_diagnostic(relevant_stderr),
        )


_ACTIVE_OPERATION: ContextVar[OperationAttempt | None] = ContextVar("frontend_director_operation", default=None)


@contextmanager
def tracked_operation(
    store: Any,
    session_id: str,
    *,
    operation_name: str,
    phase: str,
    project_root: str,
    inputs: Any,
    environment: Any,
    provider: str = "local",
    max_attempts: int = 2,
) -> Iterator[OperationAttempt]:
    """Persist bounded operation attempts and suppress unchanged deterministic failures."""
    input_fingerprint = _fingerprint(inputs)
    environment_fingerprint = _fingerprint(environment)
    operation_signature = _fingerprint({
        "operation_name": operation_name,
        "phase": phase,
        "project_root": str(Path(project_root).resolve()),
        "session_id": session_id,
        "input_fingerprint": input_fingerprint,
        "environment_fingerprint": environment_fingerprint,
    })
    started = store.begin_operation(
        session_id,
        operation_name=operation_name,
        operation_signature=operation_signature,
        input_fingerprint=input_fingerprint,
        environment_fingerprint=environment_fingerprint,
        phase=phase,
        provider=provider,
        details={"input_fields": sorted(inputs) if isinstance(inputs, dict) else []},
        max_attempts=max_attempts,
    )
    row = OperationAttempt(
        store=store,
        session_id=session_id,
        operation_id=started["operation_id"],
        operation_name=operation_name,
        operation_signature=operation_signature,
        attempt=started["attempt"],
        previous=started.get("previous"),
    )
    token = _ACTIVE_OPERATION.set(row)
    try:
        yield row
    except BaseException as error:
        assessment = classify_failure(error)
        status = "interrupted" if isinstance(error, (KeyboardInterrupt, SystemExit)) else "failed"
        if status == "interrupted" and row.process_id is not None:
            row.process_interrupted(row.process_id)
        store.finish_operation(
            session_id,
            row.operation_id,
            status=status,
            failure_category=assessment.category,
            diagnostic_summary=assessment.diagnostic_summary,
            relevant_stderr=assessment.relevant_stderr,
            retryable=assessment.retryable,
            retry_condition=assessment.retry_condition,
            exit_code=_error_exit_code(error),
            details=_failure_details(error),
        )
        raise
    else:
        assessment = row.failure_assessment
        store.finish_operation(
            session_id,
            row.operation_id,
            status="failed" if assessment else "reused" if row.result_reused else "completed",
            result_reference=row.result_reference,
            details={"result_reused": row.result_reused},
            exit_code=None,
            failure_category=assessment.category if assessment else None,
            diagnostic_summary=assessment.diagnostic_summary if assessment else None,
            relevant_stderr=assessment.relevant_stderr if assessment else None,
            retryable=assessment.retryable if assessment else False,
            retry_condition=assessment.retry_condition if assessment else "",
        )
    finally:
        _ACTIVE_OPERATION.reset(token)


def classify_failure(error: BaseException) -> FailureAssessment:
    """Classify an operation failure without treating unknown errors as transient."""
    diagnostic = getattr(error, "diagnostic", {})
    diagnostic = diagnostic if isinstance(diagnostic, dict) else {}
    raw_stderr = diagnostic.get("relevant_stderr") or getattr(error, "stderr", None)
    if isinstance(raw_stderr, bytes):
        raw_stderr = raw_stderr.decode("utf-8", errors="replace")
    stderr = _redact_diagnostic(str(raw_stderr or ""))
    message = _redact_diagnostic(str(error))
    text = f"{message}\n{stderr}".casefold()
    supplied = str(diagnostic.get("error_classification", "")).casefold()

    if any(token in text for token in ("quota exhausted", "usage limit", "insufficient quota", "billing limit")) or supplied == "quota_exhausted":
        category, retryable, condition = "quota_exhausted", False, "Wait for the provider quota to reset or select an explicitly authorized alternative."
    elif "429" in text or "rate limit" in text or "too many requests" in text or supplied == "rate_limited":
        category = "rate_limited"
        retryable = bool(re.search(r"retry[- ]after\s*[:=]?\s*\d+", text))
        condition = "Retry only after the provider's stated retry window; never retry immediately." if retryable else "Wait for the provider's retry window or quota state to change."
    elif supplied in {"blocked_by_permissions", "permission_denied"} or isinstance(error, PermissionError) or any(token in text for token in ("permission denied", "operation not permitted", "not authorized")):
        category, retryable, condition = "permission_denied", False, "Retry only after the relevant authorization or file permission has changed."
    elif supplied in {"provider_quota_or_auth", "provider_authentication"} or any(token in text for token in ("authentication required", "no verified saved login", "not logged in")):
        category, retryable, condition = "provider_authentication", False, "Retry only after provider authentication has been verified."
    elif supplied == "missing_screenshot":
        category, retryable, condition = "missing_screenshot", False, "Provide the referenced screenshot before retrying visual analysis."
    elif supplied == "visual_analysis_unverified":
        category, retryable, condition = "visual_analysis_unverified", False, "Restore compatible rendered evidence or use a verified image-capable provider."
    elif any(token in text for token in ("invalid_json_schema", "invalid schema", "schema is invalid", "schema validation")) or supplied == "invalid_schema":
        category, retryable, condition = "invalid_schema", False, "Correct the schema or compatible invocation before retrying."
    elif any(token in text for token in ("unknown option", "unrecognized argument", "invalid choice", "usage: ")) or supplied == "invalid_cli_syntax":
        category, retryable, condition = "invalid_cli_syntax", False, "Inspect the supported CLI interface and change the invocation before retrying."
    elif isinstance(error, FileNotFoundError) or "no such file or directory" in text or "does not exist" in text:
        category, retryable, condition = "missing_file", False, "Retry only after the expected file or artifact exists and its reference is updated."
    elif isinstance(error, KeyError) and ("artifact not found" in text or "missing artifact" in text):
        category, retryable, condition = "missing_artifact", False, "Register or select the expected artifact through the public workflow API before retrying."
    elif isinstance(error, (TimeoutError, subprocess.TimeoutExpired)) or "timeout" in supplied or "timed out" in text:
        category, retryable, condition = "timeout", False, "Verify that the prior process ended, then change its timeout or provider availability before retrying."
    elif supplied == "transient_network" or isinstance(error, (ConnectionError, ConnectionResetError, ConnectionRefusedError)) or any(token in text for token in (
        "connection reset", "connection refused", "temporary failure in name resolution", "network is unreachable", "service unavailable", "http 502", "http 503", "http 504",
    )):
        category, retryable, condition = "transient_network", True, "A single bounded retry is allowed after the connection is available."
    elif isinstance(error, sqlite3.OperationalError) and any(token in text for token in ("locked", "busy")):
        category, retryable, condition = "resource_contention", True, "Retry once after the database lock or resource contention clears."
    elif isinstance(error, subprocess.CalledProcessError):
        category, retryable, condition = "command_failed", False, "Inspect the recorded exit status and diagnostics; change the command or relevant input before retrying."
    elif supplied == "invalid_model_response":
        category, retryable, condition = "invalid_model_response", False, "Correct the provider response or output contract before retrying."
    elif supplied == "invalid_session_or_artifact" or isinstance(error, KeyError):
        category, retryable, condition = "invalid_session_or_artifact", False, "Resolve the authoritative session or artifact reference before retrying."
    elif "backend_invocation_failed" in supplied or isinstance(error, OSError):
        category, retryable, condition = "backend_invocation_failed", False, "Verify provider availability and invocation permissions before retrying."
    elif type(error).__name__ in {"WorkflowBlocked", "InvalidTransition"}:
        category, retryable, condition = "workflow_precondition", False, "Satisfy the recorded workflow prerequisite before retrying."
    elif type(error).__name__ == "RTKExecutionBlocked":
        category, retryable, condition = "rtk_disabled", False, "Invoke the native command directly; RTK is not allowed in this phase."
    else:
        category, retryable, condition = "unknown", False, "Perform a targeted diagnosis and change a relevant condition before retrying."
    return FailureAssessment(category, retryable, condition, message[:500], stderr[:2_000])


def current_operation() -> OperationAttempt | None:
    """Return the operation scope receiving subprocess lifecycle callbacks, if any."""
    return _ACTIVE_OPERATION.get()


def _fingerprint(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _error_exit_code(error: BaseException) -> int | None:
    value = getattr(error, "returncode", None)
    if value is None:
        value = getattr(error, "exit_status", None)
    return value if isinstance(value, int) else None


def _failure_details(error: BaseException) -> dict[str, Any]:
    diagnostic = getattr(error, "diagnostic", {})
    if not isinstance(diagnostic, dict):
        return {}
    details: dict[str, Any] = {}
    for key in ("specialist", "provider", "cli_version", "failure_location", "retry_attempts", "exit_status"):
        value = diagnostic.get(key)
        if isinstance(value, (str, int, float, bool)):
            details[key] = _redact_diagnostic(str(value)) if isinstance(value, str) else value
    schema_errors = diagnostic.get("schema_validation_errors")
    if isinstance(schema_errors, list):
        details["schema_validation_error_count"] = len(schema_errors)
        details["schema_validation_errors"] = [_redact_diagnostic(str(item))[:500] for item in schema_errors[:5]]
    invocation = diagnostic.get("invocation")
    if isinstance(invocation, dict):
        arguments = invocation.get("arguments")
        details["invocation"] = {
            "executable": Path(str(invocation.get("executable", ""))).name or None,
            "flags": [str(value) for value in arguments if isinstance(value, str) and value.startswith("-")][:40] if isinstance(arguments, list) else [],
            "argument_count": len(arguments) if isinstance(arguments, list) else None,
            "sandbox": invocation.get("sandbox"),
            "permission_mode": invocation.get("permission_mode"),
            "model": invocation.get("model"),
            "reasoning_effort": invocation.get("reasoning_effort"),
            "schema_sha256": invocation.get("schema_sha256"),
            "image_count": len(invocation.get("images_attached", [])) if isinstance(invocation.get("images_attached"), list) else invocation.get("image_count"),
        }
    return details


def _redact_diagnostic(value: str) -> str:
    value = re.sub(r"(?i)(authorization\s*[:=]\s*)bearer\s+[^\s,;]+", r"\1Bearer [REDACTED]", value)
    value = re.sub(r"(?i)\bbearer\s+[^\s,;]+", "Bearer [REDACTED]", value)
    value = re.sub(r"(?i)(authorization|api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret|token|password|secret)(\s*[=:]\s*)[^\s,;]+", r"\1\2[REDACTED]", value)
    value = re.sub(r"\b(?:sk-[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9]{16,}|xox[baprs]-[A-Za-z0-9-]{16,})\b", "[REDACTED]", value)
    return value[:2_000]


def execution_policy_for_phase(phase: object, *, paused_from: object | None = None) -> ExecutionPolicy:
    """Return the implementation policy for implementation and its verification stages."""
    value = getattr(phase, "value", phase)
    name = str(value).strip().casefold()
    if name == "paused" and paused_from is not None:
        name = str(getattr(paused_from, "value", paused_from)).strip().casefold()
    implementation_phases = {
        "implement", "implementation", "implementing", "apply", "applying", "verify", "verification", "verifying",
    }
    if name in implementation_phases:
        return IMPLEMENTATION_EXECUTION_POLICY
    return ExecutionPolicy(phase=name or "unspecified", allow_rtk=True)


def instruction_with_execution_policy(instruction: str, policy: ExecutionPolicy | None) -> str:
    """Attach operational discipline and any phase-specific command restriction."""
    sections = [instruction.rstrip()]
    if EXECUTION_DISCIPLINE_INSTRUCTION not in instruction:
        sections.append(f"Execution discipline:\n{EXECUTION_DISCIPLINE_INSTRUCTION}")
    if policy is not None and not policy.allow_rtk and IMPLEMENTATION_NO_RTK_INSTRUCTION not in instruction:
        sections.append(f"Implementation command policy:\n{IMPLEMENTATION_NO_RTK_INSTRUCTION}")
    return "\n\n".join(sections)


@contextmanager
def codex_execution_rules(working_directory: Path, policy: ExecutionPolicy | None) -> Iterator[Path | None]:
    """Add a temporary Codex rule for RTK-free phases inside the disposable workspace."""
    if policy is None or policy.allow_rtk:
        yield None
        return

    root = working_directory.resolve(strict=True)
    codex_directory = root / ".codex"
    rules_directory = codex_directory / "rules"
    if codex_directory.is_symlink() or rules_directory.is_symlink():
        raise ValueError("Cannot place the implementation command policy through a symbolic link.")
    codex_existed = codex_directory.exists()
    rules_existed = rules_directory.exists()
    rules_directory.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix="frontend-director-no-rtk-", suffix=".rules", dir=rules_directory)
    rule_path = Path(name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(IMPLEMENTATION_CODEX_RULE)
        rule_path.chmod(0o400)
        yield rule_path
    finally:
        rule_path.chmod(0o600)
        rule_path.unlink(missing_ok=True)
        if not rules_existed:
            try:
                rules_directory.rmdir()
            except OSError:
                pass
        if not codex_existed:
            try:
                codex_directory.rmdir()
            except OSError:
                pass


def run_process(
    arguments: Sequence[str | os.PathLike[str]],
    *,
    policy: ExecutionPolicy | None = None,
    **kwargs: Any,
) -> subprocess.CompletedProcess[Any]:
    """Run an argument-array command unchanged, with an implementation-scoped RTK guard."""
    command = [os.fspath(item) for item in arguments]
    if not command or not command[0]:
        raise ValueError("A process command must include an executable.")
    operation = current_operation()
    if policy is None or policy.allow_rtk:
        return _run_observed(command, kwargs, operation) if operation else subprocess.run(command, **kwargs)

    if _command_invokes_rtk(command):
        raise RTKExecutionBlocked(
            f"RTK is disabled during the {policy.phase} phase; invoke the native command directly."
        )

    # A PATH-first deny shim also blocks bare `rtk` calls made by shell tools inside a
    # provider process. It leaves every other executable and the rest of PATH intact.
    original_environment = kwargs.get("env")
    environment = dict(os.environ if original_environment is None else original_environment)
    with tempfile.TemporaryDirectory(prefix="frontend-director-no-rtk-") as temporary:
        shim_directory = Path(temporary)
        path = shim_directory / ("rtk.cmd" if os.name == "nt" else "rtk")
        if os.name == "nt":
            path.write_text(
                "@echo off\r\necho RTK is disabled during Frontend Design Director implementation. 1>&2\r\nexit /b 126\r\n",
                encoding="utf-8",
            )
        else:
            path.write_text(
                "#!/bin/sh\nprintf '%s\\n' 'RTK is disabled during Frontend Design Director implementation.' >&2\nexit 126\n",
                encoding="utf-8",
            )
            path.chmod(0o700)
        prior_path = environment.get("PATH", "")
        environment["PATH"] = os.pathsep.join(part for part in (str(shim_directory), prior_path) if part)
        kwargs["env"] = environment
        return _run_observed(command, kwargs, operation) if operation else subprocess.run(command, **kwargs)


def _run_observed(
    command: list[str],
    kwargs: dict[str, Any],
    operation: OperationAttempt,
) -> subprocess.CompletedProcess[Any]:
    """Use Popen only inside a tracked operation so its child can be recovered safely."""
    options = dict(kwargs)
    timeout = options.pop("timeout", None)
    check = options.pop("check", False)
    input_value = options.pop("input", None)
    capture_output = options.pop("capture_output", False)
    if input_value is not None:
        if options.get("stdin") is not None:
            raise ValueError("stdin and input arguments may not both be used.")
        options["stdin"] = subprocess.PIPE
    if capture_output:
        if options.get("stdout") is not None or options.get("stderr") is not None:
            raise ValueError("stdout and stderr arguments may not be used with capture_output.")
        options["stdout"] = subprocess.PIPE
        options["stderr"] = subprocess.PIPE
    with subprocess.Popen(command, **options) as process:
        operation.process_started(process.pid)
        try:
            stdout, stderr = process.communicate(input_value, timeout=timeout)
        except subprocess.TimeoutExpired as error:
            process.kill()
            stdout, stderr = process.communicate()
            operation.process_finished(process.returncode)
            raise subprocess.TimeoutExpired(command, timeout, output=stdout, stderr=stderr) from error
        except BaseException:
            if process.poll() is None:
                operation.process_interrupted(process.pid)
            else:
                operation.process_finished(process.returncode)
            raise
        operation.process_finished(process.returncode)
        result = subprocess.CompletedProcess(command, process.returncode, stdout, stderr)
    if check:
        result.check_returncode()
    return result


def _command_invokes_rtk(command: Sequence[str]) -> bool:
    executable = command[0]
    if _is_rtk_executable(executable):
        return True
    if Path(executable).name.casefold() in {"python", "python3", "python.exe", "python3.exe"}:
        return any(command[index] == "-m" and index + 1 < len(command) and command[index + 1].casefold() == "rtk" for index in range(1, len(command)))
    if Path(executable).name.casefold() in {"env", "env.exe"}:
        return _env_command_invokes_rtk(command)
    return False


def _env_command_invokes_rtk(command: Sequence[str]) -> bool:
    index = 1
    while index < len(command):
        token = command[index]
        if token == "--":
            index += 1
            break
        if token in {"-i", "--ignore-environment", "-0", "--null"}:
            index += 1
            continue
        if token in {"-u", "--unset", "-C", "--chdir"}:
            index += 2
            continue
        if token.startswith(("--unset=", "--chdir=")):
            index += 1
            continue
        if token in {"-S", "--split-string"}:
            if index + 1 >= len(command):
                return False
            try:
                split = shlex.split(command[index + 1])
            except ValueError:
                return False
            return bool(split and _is_rtk_executable(split[0]))
        if token.startswith("-"):
            # Unknown env options are left to PATH protection rather than guessed at.
            return False
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", token):
            index += 1
            continue
        break
    return index < len(command) and _is_rtk_executable(command[index])


def _is_rtk_executable(value: str) -> bool:
    return Path(value).name.casefold() in {"rtk", "rtk.exe", "rtk.cmd", "rtk.bat"}
