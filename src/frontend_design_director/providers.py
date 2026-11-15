"""Provider-specific structured execution adapters with explicit sharing boundaries."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

from .codex_backend import BackendFailure, BackendUnavailable, _validate_schema
from .execution import ExecutionPolicy, instruction_with_execution_policy, run_process


class ClaudeCodeBackend:
    """Run a schema-constrained Claude Code review only after explicit secondary-provider consent."""

    provider_id = "claude_code"

    def __init__(self, executable: str | None = None, *, authorized_secondary_provider: bool = False) -> None:
        self.executable = executable or shutil.which("claude")
        self.authorized_secondary_provider = authorized_secondary_provider

    @property
    def available(self) -> bool:
        return bool(self.executable)

    def execute(
        self,
        *,
        working_directory: Path,
        instruction: str,
        schema: dict[str, Any],
        sandbox: str = "read-only",
        images: tuple[Path, ...] = (),
        timeout_seconds: int | None = None,
        specialist: str = "unspecified",
        execution_policy: ExecutionPolicy | None = None,
    ) -> dict[str, Any]:
        if not self.authorized_secondary_provider:
            raise BackendUnavailable("Claude Code is a secondary provider; explicit data-sharing authorization is required.", diagnostic={
                "specialist": specialist,
                "provider": self.provider_id,
                "error_classification": "blocked_by_permissions",
                "failure_location": "provider.authorization",
            })
        if not self.executable:
            raise BackendUnavailable("Claude Code CLI was not found.", diagnostic={
                "specialist": specialist,
                "provider": self.provider_id,
                "error_classification": "backend_invocation_failed",
                "failure_location": "claude.discovery",
            })
        if sandbox != "read-only":
            raise ValueError("Claude Code collaboration is limited to read-only execution.")
        if images:
            raise BackendUnavailable("The Claude Code adapter does not attach images; visual tasks must use a verified image-capable provider.", diagnostic={
                "specialist": specialist,
                "provider": self.provider_id,
                "error_classification": "visual_analysis_unverified",
                "failure_location": "claude.image_preflight",
            })
        cwd = working_directory.resolve(strict=True)
        if not cwd.is_dir():
            raise ValueError("Claude Code working directory must be a directory.")
        if not isinstance(schema, dict) or schema.get("type") != "object":
            raise BackendFailure("Claude Code requires an object JSON Schema.", diagnostic={
                "specialist": specialist,
                "provider": self.provider_id,
                "error_classification": "invalid_schema",
                "failure_location": "schema.preflight",
            })
        instruction = instruction_with_execution_policy(instruction, execution_policy)
        try:
            help_result = run_process(
                [self.executable, "--help"], capture_output=True, text=True,
                check=False, timeout=12, env=_claude_environment(include_api_key=False),
                policy=execution_policy,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            raise BackendUnavailable("Claude Code invocation capabilities could not be verified.", diagnostic={
                "specialist": specialist,
                "provider": self.provider_id,
                "error_classification": "backend_invocation_failed",
                "failure_location": "claude.interface_preflight",
                "retry_attempts": 0,
            }) from error
        help_text = help_result.stdout + "\n" + help_result.stderr
        required_flags = (
            "-p", "--output-format", "--json-schema", "--permission-mode", "--tools",
            "--disallowedTools", "--setting-sources", "--strict-mcp-config", "--mcp-config",
        )
        missing_flags = [flag for flag in required_flags if flag not in help_text]
        if help_result.returncode != 0 or missing_flags:
            raise BackendUnavailable("Claude Code does not document every flag required for the bounded review invocation.", diagnostic={
                "specialist": specialist,
                "provider": self.provider_id,
                "error_classification": "backend_invocation_failed",
                "failure_location": "claude.interface_preflight",
                "unsupported_flags": missing_flags,
                "retry_attempts": 0,
            })
        try:
            auth = run_process(
                [self.executable, "auth", "status", "--json"], capture_output=True, text=True,
                check=False, timeout=12, env=_claude_environment(include_api_key=True),
                policy=execution_policy,
            )
        except subprocess.TimeoutExpired as error:
            raise BackendFailure("Claude Code authentication preflight timed out.", diagnostic={
                "specialist": specialist,
                "provider": self.provider_id,
                "error_classification": "model_timeout",
                "failure_location": "claude.authentication_preflight",
                "retry_attempts": 0,
            }) from error
        except OSError as error:
            raise BackendUnavailable("Claude Code authentication could not be verified.", diagnostic={
                "specialist": specialist,
                "provider": self.provider_id,
                "error_classification": "backend_invocation_failed",
                "failure_location": "claude.authentication_preflight",
                "retry_attempts": 0,
            }) from error
        try:
            auth_state = json.loads(auth.stdout) if auth.returncode == 0 else {}
        except json.JSONDecodeError:
            auth_state = {}
        if auth_state.get("loggedIn") is not True and not os.environ.get("ANTHROPIC_API_KEY"):
            raise BackendUnavailable("Claude Code has no verified saved login or explicitly configured API key.", diagnostic={
                "specialist": specialist,
                "provider": self.provider_id,
                "error_classification": "provider_quota_or_auth",
                "failure_location": "claude.authentication_preflight",
                "retry_attempts": 0,
            })
        schema_text = json.dumps(schema, separators=(",", ":"), sort_keys=True)
        schema_digest = hashlib.sha256(schema_text.encode()).hexdigest()
        mcp_config = json.dumps({"mcpServers": {}}, separators=(",", ":"))
        command = [
            self.executable, "-p", instruction,
            "--output-format", "json",
            "--json-schema", schema_text,
            "--permission-mode", "plan",
            "--tools", "Read,Glob,Grep",
            "--disallowedTools", "Bash,Edit,Write",
            "--setting-sources", "project",
            "--strict-mcp-config",
            "--mcp-config", mcp_config,
        ]
        invocation = {
            "provider": self.provider_id,
            "executable": self.executable,
            "working_directory": str(cwd),
            "permission_mode": "plan",
            "tools": ["Read", "Glob", "Grep"],
            "disallowed_tools": ["Bash", "Edit", "Write"],
            "mcp_servers": 0,
            "image_count": 0,
            "max_execution_seconds": timeout_seconds or 900,
            "schema_sha256": schema_digest,
        }
        try:
            result = run_process(
                command, cwd=cwd, capture_output=True, text=True, check=False,
                timeout=timeout_seconds or 900, env=_claude_environment(include_api_key=True),
                policy=execution_policy,
            )
        except subprocess.TimeoutExpired as error:
            raise BackendFailure("Claude Code review timed out.", diagnostic={
                "specialist": specialist,
                "provider": self.provider_id,
                "error_classification": "model_timeout",
                "failure_location": "claude.print_mode",
                "retry_attempts": 0,
                "invocation": invocation,
            }) from error
        except OSError as error:
            raise BackendFailure(f"Claude Code could not be started: {type(error).__name__}.", diagnostic={
                "specialist": specialist,
                "provider": self.provider_id,
                "error_classification": "backend_invocation_failed",
                "failure_location": "claude.process_start",
                "invocation": invocation,
            }) from error

        if result.returncode != 0:
            excerpt = _redact(result.stderr or result.stdout)
            classification = "provider_quota_or_auth" if re.search(r"rate.?limit|quota|usage limit|authentication|not logged in", excerpt, re.I) else "backend_invocation_failed"
            raise BackendFailure(f"Claude Code exited with status {result.returncode}: {excerpt[:1_200]}", diagnostic={
                "specialist": specialist,
                "provider": self.provider_id,
                "error_classification": classification,
                "exit_status": result.returncode,
                "relevant_stderr": excerpt[-4_000:],
                "schema_validation_errors": [],
                "retry_attempts": 0,
                "failure_location": "claude.print_mode",
                "invocation": invocation,
            })
        try:
            envelope = json.loads(result.stdout)
            if not isinstance(envelope, dict) or envelope.get("is_error") is True:
                raise ValueError("Claude Code returned an error envelope.")
            value = envelope.get("structured_output")
            if not isinstance(value, dict):
                message = envelope.get("result")
                value = json.loads(message) if isinstance(message, str) else None
            if not isinstance(value, dict):
                raise ValueError("Claude Code output did not contain a structured object.")
            _validate_schema(value, schema)
        except (json.JSONDecodeError, ValueError, BackendFailure) as error:
            detail = str(error)
            raise BackendFailure("Claude Code returned an invalid structured response.", diagnostic={
                "specialist": specialist,
                "provider": self.provider_id,
                "error_classification": "invalid_model_response",
                "exit_status": result.returncode,
                "schema_validation_errors": [detail[:800]],
                "retry_attempts": 0,
                "failure_location": "claude.response_validation",
                "invocation": invocation,
            }) from error
        return value


def _claude_environment(*, include_api_key: bool) -> dict[str, str]:
    allowed = {
        "PATH", "HOME", "USER", "LOGNAME", "SHELL", "TMPDIR", "TMP", "TEMP", "LANG", "LC_ALL", "LC_CTYPE", "TERM",
        "SYSTEMROOT", "WINDIR", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "CLAUDE_CONFIG_DIR", "SSL_CERT_FILE", "NODE_EXTRA_CA_CERTS",
    }
    if include_api_key:
        allowed.add("ANTHROPIC_API_KEY")
    return {key: value for key, value in os.environ.items() if key in allowed}


def _redact(value: str) -> str:
    value = re.sub(r"(?i)(bearer\s+)[A-Za-z0-9._~+/-]+=*", r"\1[REDACTED]", value)
    value = re.sub(r"(?i)(sk-ant-[A-Za-z0-9_-]{8})[A-Za-z0-9_-]+", r"\1[REDACTED]", value)
    value = re.sub(r"(?i)(api[_-]?key\s*[:=]\s*)\S+", r"\1[REDACTED]", value)
    return value
