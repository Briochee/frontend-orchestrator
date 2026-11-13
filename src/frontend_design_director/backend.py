"""Minimal contract for structured local or remote specialist execution."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol


class AgentBackend(Protocol):
    """A backend that returns JSON-compatible results constrained by a schema."""

    @property
    def available(self) -> bool: ...

    def execute(
        self,
        *,
        working_directory: Path,
        instruction: str,
        schema: dict[str, Any],
        sandbox: str = "read-only",
        images: tuple[Path, ...] = (),
        timeout_seconds: int | None = None,
    ) -> dict[str, Any]: ...
