"""Single-line local activity and request logging with append-only rollover."""

from __future__ import annotations

import json
import hashlib
import logging
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class JsonLineFormatter(logging.Formatter):
    """Serialize each log record to one normalized JSON line."""

    def format(self, record: logging.LogRecord) -> str:
        return json.dumps({
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
            "channel": getattr(record, "channel", "activity"),
            "level": record.levelname.lower(),
            "message": record.getMessage().replace("\n", " "),
            "context": _safe_context(getattr(record, "context", {})),
        }, sort_keys=True)


class LineRolloverHandler(logging.Handler):
    """Keep append-only log files below a configured number of lines."""

    def __init__(self, directory: Path, channel: str, max_lines: int = 10_000) -> None:
        super().__init__()
        self.directory = directory
        self.channel = channel
        self.max_lines = max_lines
        self._lock = threading.RLock()
        self._path: Path | None = None
        self._line_count = 0
        self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        self._select_active_file()

    def _select_active_file(self) -> None:
        candidates = sorted(self.directory.glob(f"{self.channel}*.log"), key=lambda item: item.stat().st_mtime_ns)
        if candidates:
            latest = candidates[-1]
            try:
                count = sum(1 for _ in latest.open("rb"))
            except OSError:
                count = self.max_lines
            if count < self.max_lines:
                self._path, self._line_count = latest, count
                return
        self._path = self.directory / f"{self.channel}.log" if not candidates else self._rollover_path()
        self._line_count = 0
        self._path.touch(mode=0o600, exist_ok=True)

    def _rollover_path(self) -> Path:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        candidate = self.directory / f"{self.channel}-{stamp}.log"
        suffix = 1
        while candidate.exists():
            candidate = self.directory / f"{self.channel}-{stamp}-{suffix}.log"
            suffix += 1
        return candidate

    def emit(self, record: logging.LogRecord) -> None:
        try:
            line = self.format(record)
            with self._lock:
                if self._path is None or self._line_count >= self.max_lines:
                    self._path = self._rollover_path()
                    self._line_count = 0
                with self._path.open("a", encoding="utf-8") as stream:
                    stream.write(line + "\n")
                self._line_count += 1
        except Exception:
            self.handleError(record)


class _ChannelAdapter(logging.LoggerAdapter):
    def process(self, msg: Any, kwargs: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        extra = kwargs.setdefault("extra", {})
        extra.setdefault("channel", self.extra["channel"])
        extra.setdefault("context", kwargs.pop("context", {}))
        return str(msg), kwargs


def configure_logging(directory: Path) -> tuple[logging.LoggerAdapter, logging.LoggerAdapter]:
    """Create activity and request loggers in the session's private log directory."""
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    scope = hashlib.sha256(str(directory.resolve()).encode("utf-8")).hexdigest()[:12]
    loggers: list[logging.LoggerAdapter] = []
    for channel in ("activity", "requests"):
        logger = logging.getLogger(f"frontend_design_director.{scope}.{channel}")
        logger.setLevel(logging.INFO)
        logger.propagate = False
        if not logger.handlers:
            handler = LineRolloverHandler(directory, channel)
            handler.setFormatter(JsonLineFormatter())
            logger.addHandler(handler)
        loggers.append(_ChannelAdapter(logger, {"channel": channel}))
    return loggers[0], loggers[1]


def _safe_context(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _safe_context(item) for key, item in value.items() if not _is_secret_key(str(key))}
    if isinstance(value, (list, tuple)):
        return [_safe_context(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        if isinstance(value, str):
            return _redact(value)
        return value
    return str(value)


def _is_secret_key(value: str) -> bool:
    return any(token in value.casefold() for token in ("authorization", "cookie", "password", "secret", "token", "api_key", "apikey", "private_key"))


def _redact(value: str) -> str:
    import re

    return re.sub(r"(?i)(bearer\s+|api[_-]?key\s*[=:]\s*)[^\s,;]+", r"\1[REDACTED]", value)
