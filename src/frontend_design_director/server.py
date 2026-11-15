"""Explicitly authorized, process-owned local development-server lifecycle."""

from __future__ import annotations

import os
import re
import shutil
import signal
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator
from urllib.parse import urlsplit

from .browser import _validate_url
from .execution import current_operation


@dataclass
class DevelopmentServerRun:
    command: tuple[str, ...]
    url: str
    process_id: int | None = None
    started_at: str | None = None
    ready_at: str | None = None
    ready_status: int | None = None
    stdout_excerpt: str = ""
    stderr_excerpt: str = ""
    _process: subprocess.Popen[bytes] | None = field(default=None, repr=False)
    _temporary_directory: tempfile.TemporaryDirectory[str] | None = field(default=None, repr=False)
    _stdout_path: Path | None = field(default=None, repr=False)
    _stderr_path: Path | None = field(default=None, repr=False)

    @property
    def details(self) -> dict[str, Any]:
        return {
            "command": {"executable": Path(self.command[0]).name, "argument_count": len(self.command) - 1},
            "url": _safe_url(self.url),
            "process_id": self.process_id,
            "started_at": self.started_at,
            "ready_at": self.ready_at,
            "ready_status": self.ready_status,
            "owned_process_group": True,
            "stdout_logged": bool(self.stdout_excerpt),
            "stderr_logged": bool(self.stderr_excerpt),
            "logs_redacted": True,
        }


class DevelopmentServerError(RuntimeError):
    """Raised when an authorized local server cannot be safely started or readied."""


@contextmanager
def managed_development_server(
    project_root: Path,
    command: list[str] | tuple[str, ...],
    url: str,
    *,
    readiness_timeout_seconds: float = 30,
    request_timeout_seconds: float = 0.75,
) -> Iterator[DevelopmentServerRun]:
    """Start one human-authorized command, wait for HTTP readiness, and stop only its process group."""
    root = project_root.resolve(strict=True)
    command_tuple = tuple(item for item in command if isinstance(item, str))
    if not root.is_dir() or not command_tuple or any(not item.strip() for item in command_tuple):
        raise ValueError("Server startup requires a project directory and a non-empty argument vector.")
    if readiness_timeout_seconds <= 0 or readiness_timeout_seconds > 120:
        raise ValueError("Readiness timeout must be between 0 and 120 seconds.")
    _validate_url(url, allow_remote=False)
    parsed = urlsplit(url)
    if parsed.query or parsed.fragment:
        raise ValueError("Local server readiness URL cannot include a query or fragment.")
    if _http_status(url, request_timeout_seconds) is not None:
        raise DevelopmentServerError("A server is already responding at the requested URL. Attach with --url instead of starting a duplicate.")

    environment = _server_environment()
    executable = command_tuple[0]
    if os.sep not in executable and (os.altsep is None or os.altsep not in executable):
        if shutil.which(executable, path=environment.get("PATH")) is None:
            raise DevelopmentServerError(f"Server executable is not available in the restricted PATH: {executable}")

    temporary = tempfile.TemporaryDirectory(prefix="frontend-director-server-")
    temporary_root = Path(temporary.name)
    stdout_path = temporary_root / "stdout.log"
    stderr_path = temporary_root / "stderr.log"
    run = DevelopmentServerRun(command_tuple, url, _temporary_directory=temporary, _stdout_path=stdout_path, _stderr_path=stderr_path)
    stdout_file = stdout_path.open("wb")
    stderr_file = stderr_path.open("wb")
    stdout_path.chmod(0o600)
    stderr_path.chmod(0o600)
    try:
        kwargs: dict[str, Any] = {
            "cwd": root,
            "env": environment,
            "stdin": subprocess.DEVNULL,
            "stdout": stdout_file,
            "stderr": stderr_file,
            "shell": False,
            "close_fds": True,
        }
        if os.name == "nt":
            kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            kwargs["start_new_session"] = True
        run._process = subprocess.Popen(command_tuple, **kwargs)
        run.process_id = run._process.pid
        operation = current_operation()
        if operation is not None:
            operation.process_started(run._process.pid)
        run.started_at = _now()
        deadline = time.monotonic() + readiness_timeout_seconds
        while time.monotonic() < deadline:
            status = _http_status(url, request_timeout_seconds)
            if status is not None:
                run.ready_status = status
                run.ready_at = _now()
                break
            if run._process.poll() is not None:
                break
            time.sleep(min(0.2, max(0.0, deadline - time.monotonic())))
        if run.ready_at is None:
            run.stdout_excerpt = _redacted_tail(stdout_path)
            run.stderr_excerpt = _redacted_tail(stderr_path)
            if run._process.poll() is not None:
                raise DevelopmentServerError(f"The authorized server command exited before HTTP readiness (exit {run._process.returncode}).")
            raise DevelopmentServerError(f"The authorized server command did not become ready within {readiness_timeout_seconds:g} seconds.")
        yield run
    finally:
        _stop_owned_process(run)
        operation = current_operation()
        if operation is not None and run._process is not None:
            operation.process_finished(run._process.returncode)
        stdout_file.close()
        stderr_file.close()
        run.stdout_excerpt = _redacted_tail(stdout_path)
        run.stderr_excerpt = _redacted_tail(stderr_path)
        temporary.cleanup()


def _server_environment() -> dict[str, str]:
    allow = {
        "PATH", "HOME", "USER", "LOGNAME", "SHELL", "TMPDIR", "TMP", "TEMP", "LANG", "LC_ALL", "LC_CTYPE", "TERM",
        "SYSTEMROOT", "WINDIR", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "SSL_CERT_FILE", "NODE_EXTRA_CA_CERTS",
    }
    environment = {key: value for key, value in os.environ.items() if key in allow}
    environment.setdefault("PATH", os.defpath)
    environment.setdefault("HOME", str(Path.home()))
    return environment


def _http_status(url: str, timeout: float) -> int | None:
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, request, file_pointer, code, message, headers, new_url):
            return None

    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    request = urllib.request.Request(url, method="GET", headers={"User-Agent": "frontend-design-director-readiness/1"})
    try:
        with opener.open(request, timeout=timeout) as response:
            return response.status
    except urllib.error.HTTPError as error:
        return error.code
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        return None


def _stop_owned_process(run: DevelopmentServerRun) -> None:
    process = run._process
    if process is None or process.poll() is not None:
        return
    try:
        if os.name == "nt":
            process.terminate()
        else:
            os.killpg(process.pid, signal.SIGTERM)
        process.wait(timeout=3)
    except (OSError, subprocess.TimeoutExpired):
        try:
            if os.name == "nt":
                process.kill()
            else:
                os.killpg(process.pid, signal.SIGKILL)
            process.wait(timeout=3)
        except (OSError, subprocess.TimeoutExpired):
            pass


def _redacted_tail(path: Path, maximum_bytes: int = 60_000) -> str:
    try:
        with path.open("rb") as stream:
            stream.seek(max(0, path.stat().st_size - maximum_bytes))
            value = stream.read().decode("utf-8", errors="replace")
    except OSError:
        return ""
    value = re.sub(r"(?i)(bearer\s+)[a-z0-9._~+/-]+=*", r"\1[REDACTED]", value)
    value = re.sub(r"(?i)([A-Z0-9_]*(?:API[_-]?KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL)[A-Z0-9_]*\s*[=:]\s*)[^\s,;]+", r"\1[REDACTED]", value)
    return value[-maximum_bytes:]


def _safe_url(value: str) -> str:
    parsed = urlsplit(value)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
