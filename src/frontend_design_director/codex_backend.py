"""Codex CLI adapter using the signed-in account, restricted sandboxes, and JSON Schema."""

from __future__ import annotations

import json
import hashlib
import re
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .discovery import _clean_codex_environment
from .execution import ExecutionPolicy, codex_execution_rules, current_operation, instruction_with_execution_policy, run_process


class BackendUnavailable(RuntimeError):
    """Raised when a requested local Codex execution cannot be used safely."""

    def __init__(self, message: str, *, diagnostic: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.diagnostic = diagnostic or {}


class BackendFailure(RuntimeError):
    """Raised for a failed or malformed Codex response."""

    def __init__(self, message: str, *, diagnostic: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.diagnostic = diagnostic or {}


@dataclass(frozen=True)
class CodexSettings:
    model: str = "gpt-6-luna"
    reasoning_effort: str = "xhigh"
    verbosity: str = "high"
    summary: str = "detailed"
    timeout_seconds: int = 900


class CodexCLIBackend:
    """Run a local Codex CLI session without requiring or forwarding API keys."""

    provider_id = "codex"

    def __init__(self, executable: str | None = None, settings: CodexSettings | None = None) -> None:
        self.executable = executable or shutil.which("codex")
        self.settings = settings or CodexSettings()
        self._version: str | None = None

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
        specialist: str = "unspecified",
        execution_policy: ExecutionPolicy | None = None,
    ) -> dict[str, Any]:
        """Invoke ``codex exec`` and validate the schema-constrained final JSON."""
        if not self.executable:
            raise BackendUnavailable("Codex CLI was not found; install or expose `codex` on PATH.", diagnostic={
                "specialist": specialist,
                "error_classification": "backend_invocation_failed",
                "failure_location": "codex.discovery",
            })
        if sandbox not in {"read-only", "workspace-write"}:
            raise ValueError("Codex runs are limited to read-only or workspace-write sandboxes.")
        cwd = working_directory.resolve(strict=True)
        if not cwd.is_dir():
            raise ValueError("Codex working directory must be a directory.")
        compatible_schema = _codex_compatible_schema(schema)
        image_details = []
        for image in images:
            if not image.is_file():
                raise BackendFailure(f"Screenshot does not exist: {image}", diagnostic={
                    "specialist": specialist,
                    "error_classification": "missing_screenshot",
                    "failure_location": "image.preflight",
                    "invocation": {"working_directory": str(cwd), "image": str(image)},
                })
            content = image.read_bytes()
            image_format = _image_format(content)
            if image_format not in {"png", "jpeg"}:
                raise BackendFailure(f"Screenshot is empty or uses an unsupported image format: {image}", diagnostic={
                    "specialist": specialist,
                    "error_classification": "visual_analysis_unverified",
                    "failure_location": "image.format_preflight",
                    "retry_attempts": 0,
                    "invocation": {"working_directory": str(cwd), "image": str(image)},
                    "image_format": image_format,
                })
            image_details.append({
                "path": str(image.resolve()),
                "sha256": hashlib.sha256(content).hexdigest(),
                "byte_size": len(content),
                "format": image_format,
            })
        instruction = instruction_with_execution_policy(instruction, execution_policy)
        self._require_chatgpt_plan_auth(specialist=specialist, execution_policy=execution_policy)

        with tempfile.TemporaryDirectory(prefix="frontend-director-codex-") as temporary:
            temp_root = Path(temporary)
            schema_path = temp_root / "schema.json"
            output_path = temp_root / "response.json"
            schema_text = json.dumps(compatible_schema, indent=2)
            schema_path.write_text(schema_text, encoding="utf-8")
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
            invocation = {
                "executable": self.executable,
                "arguments": [item for item in command if item not in {str(schema_path), str(output_path)}],
                "working_directory": str(cwd),
                "model": self.settings.model,
                "reasoning_effort": self.settings.reasoning_effort,
                "verbosity": self.settings.verbosity,
                "reasoning_summary": self.settings.summary,
                "sandbox": sandbox,
                "schema_sha256": hashlib.sha256(schema_text.encode("utf-8")).hexdigest(),
                "images_attached": image_details,
            }
            base_diagnostic = {
                "specialist": specialist,
                "cli_version": self._cli_version(execution_policy=execution_policy),
                "invocation": invocation,
                "execution_policy": {
                    "phase": execution_policy.phase,
                    "allow_rtk": execution_policy.allow_rtk,
                } if execution_policy else None,
                "retry_attempts": 0,
            }
            retry_attempts = 0
            while True:
                try:
                    with codex_execution_rules(cwd, execution_policy):
                        result = run_process(
                            command,
                            policy=execution_policy,
                            input=instruction,
                            capture_output=True,
                            text=True,
                            cwd=cwd,
                            env=environment,
                            timeout=timeout_seconds or self.settings.timeout_seconds,
                            check=False,
                        )
                except subprocess.TimeoutExpired as error:
                    stderr = _safe_stderr(_decode_output(error.stderr))
                    raise BackendFailure("Codex execution exceeded its configured timeout.", diagnostic={
                        **base_diagnostic,
                        "error_classification": "model_timeout",
                        "exit_status": None,
                        "relevant_stderr": stderr,
                        "failure_location": "codex.exec.timeout",
                        "retry_attempts": retry_attempts,
                        "retryable": False,
                        "retry_condition": "Verify that the prior process ended, then change its timeout or provider availability before retrying.",
                    }) from error
                except OSError as error:
                    raise BackendUnavailable(f"Codex CLI could not be started: {type(error).__name__}.", diagnostic={
                        **base_diagnostic,
                        "error_classification": "backend_invocation_failed",
                        "exit_status": None,
                        "failure_location": "codex.exec.start",
                        "retry_attempts": retry_attempts,
                        "retryable": False,
                        "retry_condition": "Verify the executable path and local invocation permissions before retrying.",
                    }) from error
                if result.returncode == 0:
                    break
                message = _safe_stderr(result.stderr)
                delay = _transient_retry_delay(message, retry_attempts)
                if delay is None:
                    break
                retry_attempts += 1
                operation = current_operation()
                if operation is not None:
                    operation.record_details({
                        "provider_retry_attempts": retry_attempts,
                        "last_retry_category": "transient_network",
                    })
                time.sleep(delay)
            if result.returncode != 0:
                message = _safe_stderr(result.stderr)
                classification = _classify_codex_stderr(message)
                raise BackendFailure(f"Codex exited with status {result.returncode}: {message}", diagnostic={
                    **base_diagnostic,
                    "error_classification": classification,
                    "exit_status": result.returncode,
                    "relevant_stderr": message,
                    "schema_validation_errors": [message] if classification == "invalid_schema" else [],
                    "failure_location": "codex.exec.output_schema" if classification == "invalid_schema" else "codex.exec",
                    "retry_attempts": retry_attempts,
                    "retryable": classification == "transient_network",
                    "retry_condition": "Wait for network connectivity to recover; one immediate retry was used." if retry_attempts else "A single bounded retry is allowed after network connectivity is restored." if classification == "transient_network" else "Do not retry unchanged provider input or authorization.",
                })
            if not output_path.is_file():
                # The documented CLI normally writes the final message to -o; retain stdout as a compatible fallback.
                payload = result.stdout.strip()
            else:
                payload = output_path.read_text(encoding="utf-8").strip()
            try:
                value = json.loads(payload)
            except json.JSONDecodeError as error:
                raise BackendFailure("Codex returned a final message that was not valid JSON.", diagnostic={
                    **base_diagnostic,
                    "error_classification": "invalid_model_response",
                    "exit_status": result.returncode,
                    "schema_validation_errors": [str(error)],
                    "failure_location": "response.json_parse",
                }) from error
            try:
                _validate_schema(value, compatible_schema)
            except BackendFailure as error:
                raise BackendFailure(str(error), diagnostic={
                    **base_diagnostic,
                    "error_classification": "invalid_model_response",
                    "exit_status": result.returncode,
                    "schema_validation_errors": [str(error)],
                    "failure_location": "response.schema_validation",
                }) from error
            return value

    def _cli_version(self, *, execution_policy: ExecutionPolicy | None = None) -> str:
        if self._version is not None:
            return self._version
        try:
            result = run_process(
                [self.executable or "codex", "--version"], capture_output=True, text=True,
                timeout=5, check=False, env=_clean_codex_environment(),
                policy=execution_policy,
            )
            self._version = (result.stdout or result.stderr or "unknown").strip()[:120] if result.returncode == 0 else "unknown"
        except (OSError, subprocess.TimeoutExpired):
            self._version = "unknown"
        return self._version

    def _require_chatgpt_plan_auth(
        self,
        *,
        specialist: str = "unspecified",
        execution_policy: ExecutionPolicy | None = None,
    ) -> None:
        """Require saved ChatGPT sign-in so this adapter never falls back to API-key billing."""
        try:
            result = run_process(
                [self.executable, "login", "status"],
                policy=execution_policy,
                capture_output=True,
                text=True,
                timeout=12,
                check=False,
                env=_clean_codex_environment(),
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            raise BackendUnavailable("Could not verify saved Codex ChatGPT sign-in; no API key will be requested.", diagnostic={
                "specialist": specialist,
                "cli_version": self._cli_version(execution_policy=execution_policy),
                "error_classification": "backend_invocation_failed",
                "failure_location": "codex.login_status",
            }) from error
        status = (result.stdout + "\n" + result.stderr).casefold()
        if result.returncode != 0 or "logged in using chatgpt" not in status:
            raise BackendUnavailable("Sign in to Codex with your ChatGPT account (`codex login`). This backend does not use API-key billing.", diagnostic={
                "specialist": specialist,
                "cli_version": self._cli_version(),
                "error_classification": "backend_invocation_failed",
                "exit_status": result.returncode,
                "failure_location": "codex.login_status",
            })


def _codex_compatible_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Adapt optional object properties to strict Codex JSON Schema requirements."""
    if not isinstance(schema, dict):
        raise BackendFailure("Codex output schemas must have an object at the top level.", diagnostic={
            "error_classification": "invalid_schema",
            "failure_location": "schema.preflight",
            "schema_validation_errors": ["top-level schema must be an object"],
        })

    try:
        schema = _resolve_local_schema_refs(schema)
    except (TypeError, ValueError) as error:
        raise BackendFailure(f"Codex output schema is invalid: {error}", diagnostic={
            "error_classification": "invalid_schema",
            "failure_location": "schema.preflight",
            "schema_validation_errors": [str(error)],
        }) from error
    if schema.get("type") != "object":
        raise BackendFailure("Codex output schemas must have an object at the top level.", diagnostic={
            "error_classification": "invalid_schema",
            "failure_location": "schema.preflight",
            "schema_validation_errors": ["top-level type must be object"],
        })

    def adapt(node: dict[str, Any], path: str) -> dict[str, Any]:
        result = dict(node)
        kind = result.get("type")
        if kind == "object":
            properties = result.get("properties", {})
            if not isinstance(properties, dict):
                raise ValueError(f"{path}.properties must be an object")
            required = result.get("required", [])
            if not isinstance(required, list) or any(name not in properties for name in required):
                raise ValueError(f"{path}.required must contain declared property names")
            adapted = {}
            for name, child in properties.items():
                if not isinstance(child, dict):
                    raise ValueError(f"{path}.properties.{name} must be a schema object")
                child_schema = adapt(child, f"{path}.properties.{name}")
                if name not in required:
                    child_schema = _nullable_schema(child_schema)
                adapted[name] = child_schema
            result["properties"] = adapted
            result["required"] = list(properties)
            result["additionalProperties"] = False
        elif kind == "array":
            item_schema = result.get("items")
            if not isinstance(item_schema, dict):
                raise ValueError(f"{path}.items must be a schema object")
            result["items"] = adapt(item_schema, f"{path}.items")
        elif "anyOf" in result:
            if not isinstance(result["anyOf"], list) or not result["anyOf"]:
                raise ValueError(f"{path}.anyOf must be a non-empty array")
            result["anyOf"] = [adapt(option, f"{path}.anyOf[{index}]") for index, option in enumerate(result["anyOf"])]
        elif kind not in {"string", "integer", "number", "boolean", "null"}:
            raise ValueError(f"{path}.type is unsupported: {kind!r}")
        return result

    try:
        return adapt(schema, "$")
    except (TypeError, ValueError) as error:
        raise BackendFailure(f"Codex output schema is invalid: {error}", diagnostic={
            "error_classification": "invalid_schema",
            "failure_location": "schema.preflight",
            "schema_validation_errors": [str(error)],
        }) from error


def _resolve_local_schema_refs(schema: dict[str, Any]) -> dict[str, Any]:
    """Inline local JSON Schema definitions before sending the strict Codex schema."""
    def lookup(reference: str) -> Any:
        if not reference.startswith("#/"):
            raise ValueError(f"only local JSON Schema references are supported: {reference}")
        value: Any = schema
        for part in reference[2:].split("/"):
            key = part.replace("~1", "/").replace("~0", "~")
            if not isinstance(value, dict) or key not in value:
                raise ValueError(f"JSON Schema reference does not resolve: {reference}")
            value = value[key]
        return value

    def resolve(value: Any, stack: tuple[str, ...] = (), *, at_root: bool = False) -> Any:
        if isinstance(value, list):
            return [resolve(item, stack) for item in value]
        if not isinstance(value, dict):
            return value
        reference = value.get("$ref")
        if reference is not None:
            if not isinstance(reference, str):
                raise ValueError("JSON Schema $ref must be a string")
            if reference in stack:
                raise ValueError(f"recursive JSON Schema reference is not supported: {reference}")
            target = resolve(lookup(reference), (*stack, reference))
            siblings = {key: child for key, child in value.items() if key != "$ref"}
            if not isinstance(target, dict):
                raise ValueError(f"JSON Schema reference must point to a schema object: {reference}")
            return {**target, **resolve(siblings, stack)}
        resolved = {}
        for key, child in value.items():
            if at_root and key in {"$defs", "definitions", "$schema", "$id"}:
                continue
            if key in {"$defs", "definitions"}:
                continue
            resolved[key] = resolve(child, stack)
        return resolved

    return resolve(schema, at_root=True)


def _nullable_schema(schema: dict[str, Any]) -> dict[str, Any]:
    result = dict(schema)
    kind = result.get("type")
    if isinstance(kind, str):
        result["type"] = [kind, "null"]
    elif isinstance(kind, list) and "null" not in kind:
        result["type"] = [*kind, "null"]
    elif "anyOf" in result:
        result["anyOf"] = [*result["anyOf"], {"type": "null"}]
    else:
        result = {"anyOf": [result, {"type": "null"}]}
    if isinstance(result.get("enum"), list) and None not in result["enum"]:
        result["enum"] = [*result["enum"], None]
    return result


def _validate_schema(value: Any, schema: dict[str, Any]) -> None:
    """Validate the JSON Schema subset emitted by the orchestrator."""
    if "anyOf" in schema:
        failures = []
        for option in schema["anyOf"]:
            try:
                _validate_schema(value, option)
                return
            except BackendFailure as error:
                failures.append(str(error))
        raise BackendFailure(f"Codex JSON response did not match anyOf alternatives: {failures}")
    expected = schema.get("type")
    expected_types = expected if isinstance(expected, list) else [expected]
    if value is None and "null" in expected_types:
        if "enum" in schema and value not in schema["enum"]:
            raise BackendFailure("Codex JSON response value is outside the allowed enum: null")
        return
    matching_types = [kind for kind in expected_types if _matches_json_type(value, kind)]
    if expected is not None and not matching_types:
        raise BackendFailure(f"Codex JSON response property must match one of the allowed types: {expected!r}.")
    if "object" in matching_types:
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
    elif "array" in matching_types:
        if not isinstance(value, list):
            raise BackendFailure("Codex JSON response property must be an array.")
        item_schema = schema.get("items", {})
        for item in value:
            _validate_schema(item, item_schema)
    elif not matching_types and expected is not None:
        raise BackendFailure(f"Codex JSON response property has unsupported type: {expected!r}")
    if "enum" in schema and value not in schema["enum"]:
        raise BackendFailure(f"Codex JSON response value is outside the allowed enum: {value!r}")


def _matches_json_type(value: Any, expected: Any) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "null":
        return value is None
    return False


def _image_format(content: bytes) -> str:
    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if content.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if content.startswith((b"GIF87a", b"GIF89a")):
        return "gif"
    if content.startswith(b"RIFF") and content[8:12] == b"WEBP":
        return "webp"
    return "unknown"


def _decode_output(value: str | bytes | None) -> str:
    if value is None:
        return ""
    return value.decode("utf-8", errors="replace") if isinstance(value, bytes) else value


def _classify_codex_stderr(stderr: str) -> str:
    text = stderr.casefold()
    if any(token in text for token in ("usage limit", "quota exhausted", "billing limit", "insufficient quota")):
        return "quota_exhausted"
    if "429" in text or "rate limit" in text or "too many requests" in text:
        return "rate_limited"
    if any(token in text for token in ("permission denied", "operation not permitted", "not authorized")):
        return "permission_denied"
    if "invalid_json_schema" in text or "invalid schema" in text:
        return "invalid_schema"
    if any(token in text for token in ("unknown option", "unrecognized argument", "invalid choice", "usage: ")):
        return "invalid_cli_syntax"
    if any(token in text for token in (
        "connection reset", "connection refused", "temporary failure in name resolution", "network is unreachable",
        "service unavailable", "temporarily unavailable", "http 502", "http 503", "http 504",
    )):
        return "transient_network"
    if "backend_invocation_failed" in text:
        return "backend_invocation_failed"
    return "backend_invocation_failed"


def _transient_retry_delay(stderr: str, retry_attempts: int) -> float | None:
    """Retry only one clearly transient transport failure or a short stated retry window."""
    if retry_attempts >= 1:
        return None
    text = stderr.casefold()
    retry_after = re.search(r"retry[- ]after\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(?:s|seconds?)?", text)
    if retry_after and ("429" in text or "rate limit" in text or "too many requests" in text):
        delay = float(retry_after.group(1))
        return delay if 0 <= delay <= 5 else None
    if any(token in text for token in (
        "connection reset", "connection refused", "temporary failure in name resolution", "network is unreachable",
        "service unavailable", "temporarily unavailable", "http 502", "http 503", "http 504",
    )):
        return 0.25
    return None


def _safe_stderr(stderr: str) -> str:
    """Retain complete actionable error lines while dropping echoed prompts."""
    cleaned = re.sub(r"(?i)bearer\s+[a-z0-9._~+/-]+=*", "Bearer [REDACTED]", stderr)
    cleaned = re.sub(r"(?i)(authorization|api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret|token|password|secret)(\s*[=:]\s*)[^\s,;]+", r"\1\2[REDACTED]", cleaned)
    cleaned = re.sub(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{16,}", "[REDACTED_KEY]", cleaned)
    cleaned = re.sub(r"(https?://[^\s?]+)\?[^\s]+", r"\1?[query removed]", cleaned)
    lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
    error_lines = [line for line in lines if "error:" in line.casefold() or "invalid_json_schema" in line.casefold()]
    selected = error_lines or lines[-40:]
    result = "\n".join(selected)
    if len(result) > 24_000:
        result = result[:12_000] + "\n[diagnostic output truncated to 24000 characters]\n" + result[-12_000:]
    return result or "No diagnostic details were returned."
