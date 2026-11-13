"""Best-effort checks for newer published Frontend Design Director versions."""

from __future__ import annotations

import json
import re
import urllib.request

from . import __version__

GITHUB_RELEASE_URL = "https://api.github.com/repos/Briochee/frontend-orchestrator/releases/latest"
GITHUB_MAIN_VERSION_SOURCE_URL = (
    "https://raw.githubusercontent.com/Briochee/frontend-orchestrator/main/"
    "src/frontend_design_director/__init__.py"
)
UPDATE_CHECK_TIMEOUT_SECONDS = 1.5
MAX_RESPONSE_BYTES = 64 * 1024
_VERSION_PATTERN = re.compile(r"^v?(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
_VERSION_DECLARATION_PATTERN = re.compile(r"(?m)^__version__\s*=\s*['\"]([^'\"]+)['\"]\s*$")


def check_for_update(current_version: str = __version__) -> dict[str, str | None]:
    """Return a JSON-safe update status without failing the caller when offline."""
    current = _parse_version(current_version)
    if current is None:
        return {
            "status": "unavailable",
            "current_version": current_version,
            "latest_version": None,
            "source": None,
        }

    latest_version, source = _latest_version()
    latest = _parse_version(latest_version) if latest_version else None
    if latest is None:
        return {
            "status": "unavailable",
            "current_version": current_version,
            "latest_version": latest_version,
            "source": source,
        }
    return {
        "status": "update_available" if latest > current else "up_to_date",
        "current_version": current_version,
        "latest_version": latest_version,
        "source": source,
    }


def _latest_version() -> tuple[str | None, str | None]:
    release_version = _release_version()
    if release_version is not None:
        return release_version, "github_release"
    branch_version = _main_branch_version()
    if branch_version is not None:
        return branch_version, "github_main"
    return None, None


def _release_version() -> str | None:
    try:
        payload = json.loads(_fetch(GITHUB_RELEASE_URL))
    except (OSError, ValueError, UnicodeDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    version = payload.get("tag_name")
    if not isinstance(version, str):
        return None
    normalized = version.removeprefix("v")
    return normalized if _parse_version(normalized) else None


def _main_branch_version() -> str | None:
    try:
        source = _fetch(GITHUB_MAIN_VERSION_SOURCE_URL).decode("utf-8")
    except (OSError, ValueError, UnicodeDecodeError):
        return None
    match = _VERSION_DECLARATION_PATTERN.search(source)
    version = match.group(1) if match else None
    return version if isinstance(version, str) and _parse_version(version) else None


def _fetch(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": f"frontend-design-director/{__version__}",
        },
    )
    with urllib.request.urlopen(request, timeout=UPDATE_CHECK_TIMEOUT_SECONDS) as response:
        payload = response.read(MAX_RESPONSE_BYTES + 1)
    if len(payload) > MAX_RESPONSE_BYTES:
        raise ValueError("Update metadata response exceeded the size limit.")
    return payload


def _parse_version(version: str) -> tuple[int, int, int] | None:
    match = _VERSION_PATTERN.fullmatch(version.strip())
    if not match:
        return None
    return int(match.group(1)), int(match.group(2)), int(match.group(3))
