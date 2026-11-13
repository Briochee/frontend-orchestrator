"""Codex CLI adapter using the signed-in account, restricted sandboxes, and JSON Schema."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .discovery import _clean_codex_environment


class BackendUnavailable(RuntimeError):
    """Raised when a requested local Codex execution cannot be used safely."""


class BackendFailure(RuntimeError):
    """Raised for a failed or malformed Codex response."""


@dataclass(frozen=True)
class CodexSettings:
    model: str = "gpt-6-luna"
    reasoning_effort: str = "xhigh"
    verbosity: str = "high"
    summary: str = "detailed"
    timeout_seconds: int = 900


class CodexCLIBackend:
    """Run a local Codex CLI session without requiring or forwarding API keys."""

    def __init__(self, executable: str | None = None, settings: CodexSettings | None = None) -> None:
        self.executable = executable or shutil.which("codex")
        self.settings = settings or CodexSettings()

    @property
    def available(self) -> bool:
        return self.executable is not None

    def execute(
        self,
        *,
        working_directory: Path,
        instruction: str,
        schema: dict[str, Any],
        sandbox: str = "read-only",
        images: tuple[Path, ...] = (),
        timeout_seconds: int | None = None,
    ) -> dict[str, Any]:
        """Invoke ``codex exec`` and validate the schema-constrained final JSON."""
        if not self.executable:
            raise BackendUnavailable("Codex CLI was not found; install or expose `codex` on PATH.")
        self._require_chatgpt_plan_auth()
        if sandbox not in {"read-only", "workspace-write"}:
            raise ValueError("Codex runs are limited to read-only or workspace-write sandboxes.")
        cwd = working_directory.resolve(strict=True)
        if not cwd.is_dir():
            raise ValueError("Codex working directory must be a directory.")
        for image in images:
            if not image.is_file():
                raise ValueError(f"Screenshot does not exist: {image}")

        with tempfile.TemporaryDirectory(prefix="frontend-director-codex-") as temporary:
            temp_root = Path(temporary)
            schema_path = temp_root / "schema.json"
            output_path = temp_root / "response.json"
            schema_path.write_text(json.dumps(schema, indent=2), encoding="utf-8")
            command = [
                self.executable,
                "exec",
                "--ephemeral",
                "--skip-git-repo-check",
                "--ignore-user-config",
                "--cd",
                str(cwd),
                "--sandbox",
                sandbox,
                "--model",
                self.settings.model,
                "--config",
                f'model_reasoning_effort="{self.settings.reasoning_effort}"',
                "--config",
                f'model_verbosity="{self.settings.verbosity}"',
                "--config",
                f'model_reasoning_summary="{self.settings.summary}"',
                "--output-schema",
                str(schema_path),
                "--output-last-message",
                str(output_path),
            ]
            for image in images:
                command.extend(["--image", str(image)])
            command.append("-")
            environment = _clean_codex_environment()
            try:
                result = subprocess.run(
                    command,
                    input=instruction,
                    capture_output=True,
                    text=True,
                    cwd=cwd,
                    env=environment,
                    timeout=timeout_seconds or self.settings.timeout_seconds,
                    check=False,
                )
            except subprocess.TimeoutExpired as error:
                raise BackendFailure("Codex execution exceeded its configured timeout.") from error
            except OSError as error:
                raise BackendUnavailable(f"Codex CLI could not be started: {type(error).__name__}.") from error
            if result.returncode != 0:
                message = _safe_stderr(result.stderr)
                raise BackendFailure(f"Codex exited with status {result.returncode}: {message}")
            if not output_path.is_file():
                # The documented CLI normally writes the final message to -o; retain stdout as a compatible fallback.
                payload = result.stdout.strip()
            else:
                payload = output_path.read_text(encoding="utf-8").strip()
            try:
                value = json.loads(payload)
            except json.JSONDecodeError as error:
                raise BackendFailure("Codex returned a final message that was not valid JSON.") from error
            _validate_schema(value, schema)
            return value

    def _require_chatgpt_plan_auth(self) -> None:
        """Require saved ChatGPT sign-in so this adapter never falls back to API-key billing."""
        try:
            result = subprocess.run(
                [self.executable, "login", "status"],
                capture_output=True,
                text=True,
                timeout=12,
                check=False,
                env=_clean_codex_environment(),
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            raise BackendUnavailable("Could not verify saved Codex ChatGPT sign-in; no API key will be requested.") from error
        status = (result.stdout + "\n" + result.stderr).casefold()
        if result.returncode != 0 or "logged in using chatgpt" not in status:
            raise BackendUnavailable("Sign in to Codex with your ChatGPT account (`codex login`). This backend does not use API-key billing.")


def _validate_schema(value: Any, schema: dict[str, Any]) -> None:
    """Validate the JSON subset used by the orchestrator without a runtime dependency."""
    if schema.get("type") == "object":
        if not isinstance(value, dict):
            raise BackendFailure("Codex JSON response must be an object.")
        for key in schema.get("required", []):
            if key not in value:
                raise BackendFailure(f"Codex JSON response is missing required property: {key}")
        if schema.get("additionalProperties") is False:
            unexpected = set(value) - set(schema.get("properties", {}))
            if unexpected:
                raise BackendFailure(f"Codex JSON response contains unexpected properties: {sorted(unexpected)}")
        for key, item_schema in schema.get("properties", {}).items():
            if key in value:
                _validate_schema(value[key], item_schema)
        return
    if schema.get("type") == "array":
        if not isinstance(value, list):
            raise BackendFailure("Codex JSON response property must be an array.")
        item_schema = schema.get("items", {})
        for item in value:
            _validate_schema(item, item_schema)
        return
    expected = schema.get("type")
    if expected == "string" and not isinstance(value, str):
        raise BackendFailure("Codex JSON response property must be a string.")
    if expected == "boolean" and not isinstance(value, bool):
        raise BackendFailure("Codex JSON response property must be a boolean.")
    if expected == "integer" and (not isinstance(value, int) or isinstance(value, bool)):
        raise BackendFailure("Codex JSON response property must be an integer.")
    if expected == "number" and (not isinstance(value, (int, float)) or isinstance(value, bool)):
        raise BackendFailure("Codex JSON response property must be a number.")
    if "enum" in schema and value not in schema["enum"]:
        raise BackendFailure(f"Codex JSON response value is outside the allowed enum: {value!r}")


def _safe_stderr(stderr: str) -> str:
    import re

    cleaned = re.sub(r"(?i)(authorization|api[_-]?key|token|password)(\s*[=:]\s*)[^\s,;]+", r"\1\2[REDACTED]", stderr)
    lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
    return " ".join(lines[-3:])[:500] or "No diagnostic details were returned."
