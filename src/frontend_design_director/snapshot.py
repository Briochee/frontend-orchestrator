"""Create secret-filtered, symlink-free temporary project snapshots for Codex."""

from __future__ import annotations

import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .discovery import _clean_process_environment
from .execution import ExecutionPolicy, run_process


IGNORED_DIRECTORIES = {
    ".git", ".frontend-design-director", ".agents", ".codex", ".claude", "node_modules", "vendor", "dist", "build", "coverage", ".next", ".nuxt",
    ".svelte-kit", ".venv", "venv", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "logs", "tmp", "temp",
}
SENSITIVE_NAMES = {
    ".env", ".env.local", ".env.development", ".env.production", ".npmrc", ".pypirc", ".netrc", "credentials", "id_rsa", "id_ed25519",
}
SENSITIVE_SUFFIXES = {".pem", ".key", ".p12", ".pfx", ".sqlite", ".sqlite3", ".db"}
PROJECT_INSTRUCTION_FILES = {"agents.md", "claude.md", "skill.md"}
TEXT_SUFFIXES = {
    ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".css", ".scss", ".sass", ".less", ".html", ".vue", ".svelte",
    ".json", ".jsonc", ".toml", ".yaml", ".yml", ".md", ".mdx", ".py", ".go", ".rs", ".java", ".kt", ".swift",
    ".xml", ".txt", ".graphql", ".gql", ".sql", ".sh", ".bash", ".ini", ".cfg", ".conf", ".properties",
}
TEXT_FILENAMES = {"dockerfile", "makefile", "justfile", "license", "notice", "readme", "changes", "changelog", ".gitignore", ".gitattributes", ".editorconfig", ".prettierrc", ".eslintrc"}
SECRET_PATTERNS = (
    re.compile(rb"AKIA[0-9A-Z]{16}"),
    re.compile(rb"sk-[A-Za-z0-9_-]{24,}"),
    re.compile(rb"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(rb"xox[baprs]-[A-Za-z0-9-]{20,}"),
    re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(rb"(?i)[\"']?[A-Z0-9_-]*(?:API[_-]?KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL|PRIVATE[_-]?KEY)[A-Z0-9_-]*[\"']?\s*[:=]\s*[\"'][^\"']{6,}[\"']"),
    re.compile(rb"\b[A-Z0-9_]*(?:API[_-]?KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL|PRIVATE[_-]?KEY)[A-Z0-9_]*\s*=\s*[^\s;&|]{8,}"),
)


@dataclass
class ProjectSnapshot:
    """A temporary Git repository containing a bounded, filtered project copy."""

    temporary_directory: tempfile.TemporaryDirectory[str]
    root: Path
    included_files: tuple[str, ...]
    skipped_files: tuple[str, ...]

    def close(self) -> None:
        self.temporary_directory.cleanup()

    def __enter__(self) -> ProjectSnapshot:
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.close()


def create_project_snapshot(
    source_root: Path,
    *,
    max_files: int = 5_000,
    max_file_bytes: int = 2_000_000,
    max_total_bytes: int = 100_000_000,
    initialize_git: bool = True,
    execution_policy: ExecutionPolicy | None = None,
) -> ProjectSnapshot:
    """Copy ordinary source/config files while omitting credentials and instructions."""
    source = source_root.resolve(strict=True)
    temporary = tempfile.TemporaryDirectory(prefix="frontend-director-snapshot-")
    destination = Path(temporary.name) / "project"
    destination.mkdir(mode=0o700)
    included: list[str] = []
    skipped: list[str] = []
    copied_bytes = 0

    for base, directories, filenames in os.walk(source, followlinks=False):
        directories[:] = sorted(
            name for name in directories
            if name not in IGNORED_DIRECTORIES and not (Path(base) / name).is_symlink()
        )
        for filename in sorted(filenames):
            path = Path(base) / filename
            try:
                relative = path.relative_to(source)
                size = path.stat(follow_symlinks=False).st_size
            except OSError:
                skipped.append(str(path.relative_to(source)))
                continue
            if path.is_symlink() or _is_sensitive(path) or filename.casefold() in PROJECT_INSTRUCTION_FILES:
                skipped.append(relative.as_posix())
                continue
            if not _is_text_candidate(path):
                skipped.append(relative.as_posix())
                continue
            if size > max_file_bytes or len(included) >= max_files or copied_bytes + size > max_total_bytes:
                skipped.append(relative.as_posix())
                continue
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            try:
                content = path.read_bytes()
                if any(pattern.search(content) for pattern in SECRET_PATTERNS):
                    skipped.append(relative.as_posix())
                    continue
                target.write_bytes(content)
            except OSError:
                skipped.append(relative.as_posix())
                continue
            included.append(relative.as_posix())
            copied_bytes += size

    if initialize_git:
        install_trusted_agents(destination)
        _initialize_git(destination, execution_policy=execution_policy)
    return ProjectSnapshot(temporary, destination, tuple(included), tuple(skipped))


def _is_sensitive(path: Path) -> bool:
    lowered = path.name.casefold()
    return lowered in SENSITIVE_NAMES or path.suffix.casefold() in SENSITIVE_SUFFIXES or lowered.startswith(".env.") or "credential" in lowered or "secret" in lowered


def _is_text_candidate(path: Path) -> bool:
    return path.suffix.casefold() in TEXT_SUFFIXES or path.name.casefold() in TEXT_FILENAMES


def _initialize_git(directory: Path, *, execution_policy: ExecutionPolicy | None = None) -> None:
    environment = _git_environment()
    environment.update({"GIT_AUTHOR_NAME": "Frontend Design Director", "GIT_AUTHOR_EMAIL": "frontend-director@localhost", "GIT_COMMITTER_NAME": "Frontend Design Director", "GIT_COMMITTER_EMAIL": "frontend-director@localhost"})
    commands = [
        ["git", "init", "--quiet"],
        ["git", "add", "--all"],
        ["git", "-c", f"core.hooksPath={os.devnull}", "commit", "--quiet", "--allow-empty", "-m", "Filtered project snapshot"],
    ]
    for command in commands:
        result = run_process(
            command,
            policy=execution_policy,
            cwd=directory,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
            timeout=20,
        )
        if result.returncode != 0:
            output = "\n".join(part for part in (result.stdout, result.stderr) if part)
            detail = f"\n{output}" if output else ""
            raise RuntimeError(f"Could not prepare isolated Codex workspace ({command[1]}), exit {result.returncode}.{detail}")


def _git_environment() -> dict[str, str]:
    """Keep Git child processes local to their explicit working directory."""
    environment = _clean_process_environment()
    environment.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_TERMINAL_PROMPT": "0"})
    return environment


def install_trusted_agents(directory: Path) -> None:
    """Add only this package's reviewed specialist definitions to a Codex snapshot."""
    from importlib.resources import files

    target = directory / ".codex" / "agents"
    target.mkdir(parents=True, exist_ok=True)
    resource_dir = files("frontend_design_director").joinpath("data", "agents")
    for resource in resource_dir.iterdir():
        if resource.name.endswith(".toml"):
            (target / resource.name).write_text(resource.read_text(encoding="utf-8"), encoding="utf-8")
