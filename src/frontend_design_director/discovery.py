"""Read-only discovery of Codex capabilities and frontend project conventions."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import tomllib
from pathlib import Path
from typing import Any

from .models import Capability


FRONTEND_TERMS = {
    "frontend": (
        "frontend", "front-end", "front end", "web application", "web app", "website", "web interface",
        "user interface", "ui design", "ui component", "component library", "react", "vue", "angular", "svelte", "astro",
    ),
    "visual": (
        "visual design", "web design", "design system", "visual hierarchy", "visual styling", "typography",
        "color palette", "color system", "layout design", "mockup", "figma", "visual regression",
    ),
    "accessibility": ("accessibility", "a11y", "wcag", "keyboard navigation", "screen reader"),
    "ux": ("ux", "user experience", "interaction design", "responsive design", "mobile interface", "usability"),
    "browser": (
        "browser automation", "browser testing", "playwright", "cypress", "puppeteer", "end-to-end testing",
        "e2e testing", "screenshot testing", "visual regression",
    ),
    "performance": (
        "web performance", "frontend performance", "front-end performance", "web vitals", "bundle size",
        "render performance", "lighthouse",
    ),
}

FRAMEWORK_DEPENDENCIES: dict[str, tuple[str, ...]] = {
    "Next.js": ("next",),
    "React": ("react",),
    "Vue": ("vue",),
    "Nuxt": ("nuxt",),
    "Angular": ("@angular/core",),
    "Svelte": ("svelte",),
    "SvelteKit": ("@sveltejs/kit",),
    "Astro": ("astro",),
    "Solid": ("solid-js",),
    "Remix": ("@remix-run/react", "@remix-run/dev"),
    "Expo / React Native": ("expo", "react-native"),
}

SKILL_LIMIT_BYTES = 96_000
MAX_SKILLS = 1_000


def discover_project(project_root: Path) -> dict[str, Any]:
    """Inspect manifests, source layout, and relevant conventions without executing project code."""
    root = project_root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Project path must be a directory.")

    files = _project_files(root)
    manifests = _read_package_manifests(root)
    dependencies: dict[str, str] = {}
    scripts: dict[str, str] = {}
    for manifest in manifests:
        dependencies.update(manifest.get("dependencies", {}))
        dependencies.update(manifest.get("devDependencies", {}))
        scripts.update(manifest.get("scripts", {}))
    frameworks = [name for name, packages in FRAMEWORK_DEPENDENCIES.items() if any(package in dependencies for package in packages)]
    if not frameworks and any(path.suffix.lower() in {".html", ".css", ".js"} for path in files):
        frameworks.append("Static HTML/CSS/JavaScript (detected from files)")

    pyproject = _read_toml(root / "pyproject.toml")
    python_dependencies = _python_dependencies(pyproject)
    if not frameworks:
        for candidate, package_names in (("Django", ("django",)), ("Flask", ("flask",)), ("FastAPI", ("fastapi",))):
            if any(name in python_dependencies for name in package_names):
                frameworks.append(f"{candidate} (Python-rendered web application)")

    relevant = {**dependencies, **python_dependencies}
    css_files = [path for path in files if path.suffix.lower() in {".css", ".scss", ".sass", ".less"}]
    js_files = [path for path in files if path.suffix.lower() in {".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte"}]
    token_count = 0
    media_rule_count = 0
    focus_rule_count = 0
    reduced_motion_count = 0
    for path in css_files[:400]:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")[:2_000_000]
        except OSError:
            continue
        token_count += len(re.findall(r"--[\w-]+\s*:", text))
        media_rule_count += len(re.findall(r"@media\b", text))
        focus_rule_count += len(re.findall(r":focus(?:-visible)?\b", text))
        reduced_motion_count += len(re.findall(r"prefers-reduced-motion", text))

    return {
        "project_root": str(root),
        "project_name": _project_name(root, manifests, pyproject),
        "application_description": _application_description(root, manifests, pyproject),
        "frameworks": frameworks,
        "languages": _languages(files),
        "build_tools": _detected_tools(relevant, ("vite", "webpack", "rollup", "parcel", "esbuild", "turbo", "nx", "lerna")),
        "styling": _styling_summary(relevant, css_files, token_count, media_rule_count, focus_rule_count, reduced_motion_count),
        "component_libraries": [name for package, name in (("@mui/material", "MUI"), ("antd", "Ant Design"), ("@chakra-ui/react", "Chakra UI"), ("@radix-ui/react", "Radix UI"), ("shadcn", "shadcn/ui"), ("bootstrap", "Bootstrap")) if package in relevant],
        "routing": _detected_tools(relevant, ("react-router", "react-router-dom", "@tanstack/react-router", "next", "vue-router", "@sveltejs/kit", "@remix-run/react")),
        "state_management": _detected_tools(relevant, ("redux", "@reduxjs/toolkit", "zustand", "jotai", "recoil", "mobx", "pinia", "@tanstack/react-query", "swr")),
        "test_infrastructure": _test_tools(relevant, scripts, files),
        "browser_automation": _detected_tools(relevant, ("playwright", "@playwright/test", "cypress", "puppeteer")),
        "application_commands": scripts,
        "manifest_paths": [str(path.relative_to(root)) for path in files if path.name in {"package.json", "pyproject.toml", "vite.config.js", "vite.config.ts", "next.config.js", "next.config.ts", "next.config.mjs"}],
        "documentation_paths": [str(path.relative_to(root)) for path in files if path.name in {"AGENTS.md", "CLAUDE.md", "README.md", "ARCHITECTURE.md", "SETUP.md"}],
        "route_files": _route_files(files, root),
        "source_file_count": len(js_files),
        "css_file_count": len(css_files),
        "file_count": len(files),
        "inspection_boundary": "Manifest and source-file inspection only. No project script, build, server, or dependency lifecycle was executed.",
    }


def discover_skills(project_root: Path, extra_roots: tuple[Path, ...] = ()) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    """Read skill metadata only; external instructions are never loaded or executed."""
    skills: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for root in skill_roots(project_root) + list(extra_roots):
        if not root.exists():
            continue
        try:
            files = sorted(root.rglob("SKILL.md"))
        except OSError as error:
            errors.append({"path": str(root), "error": type(error).__name__})
            continue
        for path in files[:MAX_SKILLS]:
            try:
                resolved = path.resolve(strict=True)
                if not resolved.is_file() or resolved.stat().st_size > SKILL_LIMIT_BYTES:
                    errors.append({"path": str(path), "error": "not a regular file or exceeds metadata read limit"})
                    continue
                text = resolved.read_text(encoding="utf-8", errors="replace")
                metadata = _skill_frontmatter(text[:4_096])
                if not metadata.get("name") or not metadata.get("description"):
                    errors.append({"path": str(path), "error": "missing name or description frontmatter"})
                    continue
                capabilities = classify_skill(str(metadata["name"]), str(metadata["description"]))
                if not capabilities:
                    continue
                skill = {
                    "name": str(metadata["name"]),
                    "description": str(metadata["description"]),
                    "source_path": str(resolved),
                    "capabilities": capabilities,
                    "compatibility_confidence": "documented_location" if _is_documented_skill_location(resolved) else "observed_install_location",
                    "metadata_only": True,
                }
                if str(metadata["name"]).casefold() in {"impeccable", "design-taste-frontend"}:
                    skill.update(_preferred_skill_metadata(resolved, text, project_root, metadata))
                skills.append(skill)
            except (OSError, UnicodeError) as error:
                errors.append({"path": str(path), "error": type(error).__name__})
    unique = {item["source_path"]: item for item in skills}
    return sorted(unique.values(), key=lambda item: item["name"].casefold()), errors


def discover_agents(project_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    """Inspect documented Codex custom-agent files without executing their instructions."""
    codex_home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))).expanduser()
    roots = [project_root / ".codex" / "agents", codex_home / "agents"]
    found: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    seen: set[Path] = set()
    for root in roots:
        if not root.is_dir():
            continue
        for path in sorted(root.glob("*.toml")):
            try:
                resolved = path.resolve(strict=True)
                if resolved in seen or resolved.stat().st_size > 128_000:
                    continue
                seen.add(resolved)
                value = tomllib.loads(resolved.read_text(encoding="utf-8"))
                name = value.get("name")
                description = value.get("description")
                instructions = value.get("developer_instructions")
                if not isinstance(name, str) or not isinstance(description, str) or not isinstance(instructions, str):
                    raise ValueError("custom agent requires name, description, and developer_instructions")
                found.append({
                    "name": name,
                    "description": description,
                    "source_path": str(resolved),
                    "capabilities": classify_skill(name, description + " " + instructions[:400]),
                    "tool_permissions": {
                        "sandbox_mode": value.get("sandbox_mode", "inherited from parent session"),
                        "approval_policy": value.get("approval_policy", "inherited from parent session"),
                        "features": value.get("features", {}),
                    },
                    "compatibility_confidence": "documented_codex_agent_format",
                    "instructions_loaded": False,
                })
            except (OSError, UnicodeError, tomllib.TOMLDecodeError, ValueError) as error:
                errors.append({"path": str(path), "error": str(error)[:240]})
    return sorted(found, key=lambda item: item["name"].casefold()), errors


def discover_codex(project_root: Path, codex_executable: str | None = None) -> dict[str, Any]:
    """Report Codex CLI, auth mode, configured MCPs, and cached plugin state conservatively."""
    executable = codex_executable or shutil.which("codex")
    if not executable:
        cli = {
            "installed": False, "version": None, "authenticated": False, "auth_mode": "unavailable",
            "codex_exec_supported": False, "structured_output_supported": False, "image_input_supported": False,
        }
    else:
        version_result = _safe_probe([executable, "--version"])
        auth_result = _safe_probe([executable, "login", "status"])
        exec_help = _safe_probe([executable, "exec", "--help"], stdout_limit=32_000)
        version_text = (version_result.get("stdout") or "").strip().splitlines()
        auth_text = ((auth_result.get("stdout") or "") + (auth_result.get("stderr") or "")).casefold()
        exec_help_text = (exec_help.get("stdout") or "") + "\n" + (exec_help.get("stderr") or "")
        required_exec_flags = (
            "--ephemeral", "--skip-git-repo-check", "--ignore-user-config", "--cd", "--sandbox",
            "--model", "--config", "--output-schema", "--output-last-message",
        )
        exec_supported = exec_help.get("returncode") == 0 and all(flag in exec_help_text for flag in required_exec_flags)
        chatgpt_auth = "logged in using chatgpt" in auth_text or "chatgpt account" in auth_text
        api_auth = "api key" in auth_text or "apikey" in auth_text
        cli = {
            "installed": version_result.get("returncode") == 0,
            "path": executable,
            "version": version_text[0] if version_text else None,
            "authenticated": auth_result.get("returncode") == 0 and (chatgpt_auth or api_auth),
            "auth_mode": "chatgpt_plan" if chatgpt_auth else "api_key" if api_auth else "unknown_or_signed_out",
            "codex_exec_supported": exec_supported,
            "structured_output_supported": exec_supported and "--output-schema" in exec_help_text and "--output-last-message" in exec_help_text,
            "image_input_supported": exec_supported and "--image" in exec_help_text,
            "sandbox_modes": ["read-only", "workspace-write"],
            "probe_errors": [item for item in (version_result.get("error"), auth_result.get("error"), exec_help.get("error")) if item],
        }
    config = _codex_config()
    mcps: list[dict[str, Any]] = []
    for name, raw in config.get("mcp_servers", {}).items():
        if not isinstance(raw, dict):
            continue
        mcps.append({"name": name, "configured": True, "enabled": raw.get("enabled", True) is not False, "callable": "not_probed", "transport": "url" if raw.get("url") else "stdio" if raw.get("command") else "unknown"})
    project_config = _read_toml(project_root / ".codex" / "config.toml")
    for name, raw in project_config.get("mcp_servers", {}).items():
        if not any(item["name"] == name for item in mcps) and isinstance(raw, dict):
            mcps.append({"name": name, "configured": True, "enabled": raw.get("enabled", True) is not False, "callable": "not_probed", "transport": "url" if raw.get("url") else "stdio" if raw.get("command") else "unknown", "source": "project_config"})
    plugins = _cached_plugins(config)
    return {
        "cli": cli,
        "custom_agents": "documented .codex/agents/*.toml and ~/.codex/agents/*.toml formats are supported",
        "agent_delegation": "Codex custom agents are available to an interactive or exec parent when multi-agent tools are enabled; agents inherit parent permissions.",
        "mcp_servers": sorted(mcps, key=lambda item: item["name"]),
        "plugins": plugins,
        "plugin_live_catalog": "not queried; Codex plugin listing may make a network request",
    }


def build_capability_matrix(discovery: dict[str, Any], skills: list[dict[str, Any]], agents: list[dict[str, Any]], codex: dict[str, Any], *, rendered_screenshots: list[str] | None = None) -> list[Capability]:
    """Choose usable tools from discovered evidence and explain capability gaps."""
    kinds = {capability for item in skills for capability in item["capabilities"]}
    agent_kinds = {capability for item in agents for capability in item.get("capabilities", [])}
    codex_cli = codex.get("cli", {})
    codex_ready = bool(
        codex_cli.get("installed") and codex_cli.get("authenticated")
        and codex_cli.get("auth_mode") == "chatgpt_plan"
        and codex_cli.get("codex_exec_supported") and codex_cli.get("structured_output_supported")
    )
    codex_images_ready = bool(codex_ready and codex_cli.get("image_input_supported"))
    browser_installed = bool(importlib.util.find_spec("playwright"))
    screenshots = rendered_screenshots or []
    browser_ready = bool(browser_installed and screenshots)
    source_audit_ready = bool(discovery.get("source_file_count") or discovery.get("frameworks"))
    return [
        Capability(
            name="frontend_auditing",
            available=codex_ready or source_audit_ready,
            selected_tool="Codex CLI read-only structured audit" if codex_ready else "Static source audit" if source_audit_ready else None,
            status="ready" if codex_ready or source_audit_ready else "missing",
            recommendation="Use the local evidence-based audit without specialist skills. Codex-assisted structured roles are optional and use saved ChatGPT sign-in." if not codex_ready else "Codex and local source auditing are available; discovered skills are hints, not trusted instructions.",
            details={"codex_ready_with_chatgpt_sign_in": codex_ready, "frontend_skill_or_agent_detected": "frontend" in kinds or "frontend" in agent_kinds},
        ),
        Capability(
            name="browser_testing",
            available=browser_ready,
            selected_tool="Playwright Python" if browser_ready else "Playwright Python (unverified)" if browser_installed else None,
            status="ready" if browser_ready else "installed_unverified" if browser_installed else "missing",
            recommendation="Playwright and Chromium were exercised by screenshot capture; the user still supplies and authorizes each URL." if browser_ready else "The Python package is present but Chromium has not been verified. Request a local capture; install browser binaries only after review if capture reports them missing." if browser_installed else "After review, install the optional `browser` extra and Chromium. This adds screenshot capture and browser automation; it overlaps with other screenshot tools, so a second browser plugin is unnecessary.",
            details={"python_package_installed": browser_installed, "browser_binary": "capture_confirmed" if browser_ready else "not_probed", "approval_required_before_install": True, "references": ["https://playwright.dev/python/docs/intro", "https://playwright.dev/python/docs/browsers"]},
        ),
        Capability(
            name="visual_auditing",
            available=bool(codex_images_ready and screenshots),
            selected_tool="Codex CLI plus rendered screenshots" if codex_images_ready and screenshots else None,
            status="ready" if codex_images_ready and screenshots else "missing",
            recommendation="Capture representative views with the browser-testing capability before making appearance claims. The same screenshots can be used for visual review; do not install an overlapping screenshot tool." if not screenshots else "Rendered screenshots are available, but the installed Codex CLI does not have a verified image input interface." if not codex_images_ready else "Rendered screenshots are available for review; claims must stay limited to the captured routes and states.",
            details={"rendered_evidence_count": len(screenshots), "codex_ready_with_chatgpt_sign_in": codex_ready, "image_input_supported": bool(codex_cli.get("image_input_supported"))},
        ),
        Capability(
            name="accessibility",
            available=bool(source_audit_ready),
            selected_tool="Static semantic checks" if source_audit_ready else None,
            status="ready" if source_audit_ready else "missing",
            recommendation="Static checks are available. If the project already has browser tests, consider axe-core for automated WCAG rule coverage; it complements rather than replaces keyboard, screen-reader, and manual checks.",
            details={"references": ["https://github.com/dequelabs/axe-core"], "approval_required_before_install": True},
        ),
        Capability(
            name="mockup_creation",
            available=bool(codex_ready),
            selected_tool="Codex CLI isolated interface generator" if codex_ready else None,
            status="ready" if codex_ready else "missing",
            recommendation="An opted-in Codex call is required to generate a new interface mockup. You can also supply an existing mockup for review; direction documents and generic scaffolds are never treated as mockups.",
            details={"codex_generation_available": codex_ready, "user_supplied_mockup_supported": True},
        ),
    ]


def skill_roots(project_root: Path) -> list[Path]:
    roots: list[Path] = []
    current = project_root.resolve()
    while True:
        roots.extend([current / ".agents" / "skills", current / ".codex" / "skills"])
        if (current / ".git").exists() or current.parent == current:
            break
        current = current.parent
    roots.extend([Path.home() / ".agents" / "skills", Path("/etc/codex/skills")])
    codex_home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    roots.extend([codex_home / "skills", codex_home / "plugins" / "cache"])
    return roots


def classify_skill(name: str, description: str) -> list[str]:
    text = f"{name} {description}".casefold()
    return [
        category for category, terms in FRONTEND_TERMS.items()
        if any(re.search(rf"(?<!\w){re.escape(term)}(?!\w)", text) for term in terms)
    ]


def _skill_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    metadata: dict[str, str] = {}
    for line in text[3:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, separator, value = line.partition(":")
        if not separator:
            continue
        cleaned = value.strip().strip("\"'")
        if cleaned:
            metadata[key.strip()] = cleaned
    return metadata


def _preferred_skill_metadata(
    skill_path: Path,
    content: str,
    project_root: Path,
    frontmatter: dict[str, str],
) -> dict[str, Any]:
    """Collect bounded provenance and installed-file metadata without running skill code."""
    name = frontmatter.get("name", "").casefold()
    skill_directory = skill_path.parent
    scripts_directory = skill_directory / "scripts"
    available_scripts: list[str] = []
    if scripts_directory.is_dir() and not scripts_directory.is_symlink():
        try:
            available_scripts = sorted(
                item.name for item in scripts_directory.iterdir()
                if item.is_file() and not item.is_symlink() and item.suffix in {".mjs", ".js", ".cjs"}
            )[:100]
        except OSError:
            pass

    available_commands: list[str] = []
    command_metadata = scripts_directory / "command-metadata.json"
    if command_metadata.is_file() and not command_metadata.is_symlink():
        try:
            if command_metadata.stat().st_size <= 64_000:
                value = json.loads(command_metadata.read_text(encoding="utf-8"))
                if isinstance(value, dict):
                    available_commands = sorted(str(key)[:100] for key in value if isinstance(key, str))[:100]
        except (OSError, UnicodeError, json.JSONDecodeError):
            pass
    commands_directory = skill_directory / "commands"
    if not available_commands and commands_directory.is_dir() and not commands_directory.is_symlink():
        try:
            available_commands = sorted(
                item.stem for item in commands_directory.glob("*.md")
                if item.is_file() and not item.is_symlink()
            )[:100]
        except OSError:
            pass

    version = frontmatter.get("version")
    version_source = "skill frontmatter" if version else None
    plugin_manifest: dict[str, Any] = {}
    for ancestor in (skill_directory, *list(skill_directory.parents)[:6]):
        for relative in (".codex-plugin/plugin.json", ".claude-plugin/plugin.json", ".claude-plugin/marketplace.json"):
            candidate = ancestor / relative
            if candidate.is_symlink() or not candidate.is_file():
                continue
            try:
                if candidate.stat().st_size > 64_000:
                    continue
                parsed = json.loads(candidate.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError):
                continue
            if isinstance(parsed, dict):
                plugin_manifest = parsed
                if isinstance(parsed.get("version"), (str, int, float)):
                    version = str(parsed["version"])
                    version_source = str(candidate)
                break
        if plugin_manifest:
            break

    try:
        resolved_path = skill_path.resolve(strict=True)
        if resolved_path.is_relative_to(project_root.resolve()):
            scope = "project"
        elif resolved_path.is_relative_to(Path.home().resolve()):
            scope = "user"
        elif resolved_path.is_relative_to(Path("/etc")):
            scope = "system"
        elif "/plugins/cache/" in resolved_path.as_posix():
            scope = "provider_plugin_cache"
        else:
            scope = "other"
    except (OSError, ValueError):
        scope = "unknown"
    path_text = skill_path.as_posix()
    source = (
        "provider_plugin_cache" if "/plugins/cache/" in path_text
        else "claude_code_skill_directory" if "/.claude/skills/" in path_text
        else "shared_agent_skills_directory" if "/.agents/skills/" in path_text
        else "codex_skill_directory" if "/.codex/skills/" in path_text
        else "observed_skill_directory"
    )
    hooks_directory = skill_directory / "hooks"
    hooks_present = bool(hooks_directory.is_dir() and not hooks_directory.is_symlink())
    if not hooks_present:
        hooks_present = bool(re.search(r"(?im)^hooks\s*:", content[:4_096]))

    taste_inspector = scripts_directory / "inspect.mjs"
    app_screen_reference = skill_directory / "references" / "app-screens.md"
    required_dependencies = (
        ["Node.js >=22 and Chrome, Edge, or Chromium for the documented browser inspector"]
        if name == "design-taste-frontend"
        else ["Node.js >=18.19 for the documented installer/update CLI"]
    )
    return {
        "version": version,
        "version_source": version_source,
        "content_sha256": hashlib.sha256(content.encode("utf-8", errors="replace")).hexdigest(),
        "installation_scope": scope,
        "installation_source": source,
        "installation_status": "installed",
        "available_commands": available_commands,
        "available_scripts": available_scripts,
        "required_dependencies": required_dependencies,
        "hooks_present": hooks_present,
        "hooks_require_approval": hooks_present,
        "app_screen_workflow_ready": (
            bool(taste_inspector.is_file() and app_screen_reference.is_file())
            if name == "design-taste-frontend" else None
        ),
        "plugin_manifest_version": plugin_manifest.get("version"),
    }


def _is_documented_skill_location(path: Path) -> bool:
    text = str(path)
    return "/.agents/skills/" in text or text.startswith("/etc/codex/skills/")


def _project_files(root: Path) -> list[Path]:
    ignored = {".git", ".agents", "node_modules", "vendor", "dist", "build", "coverage", ".next", ".nuxt", ".svelte-kit", ".venv", "venv", "__pycache__", ".frontend-design-director"}
    result: list[Path] = []
    for base, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(name for name in dirs if name not in ignored and not (Path(base) / name).is_symlink())
        for name in sorted(files):
            path = Path(base) / name
            if path.is_symlink() or path.name in {".DS_Store"}:
                continue
            try:
                if path.stat().st_size > 5_000_000:
                    continue
            except OSError:
                continue
            result.append(path)
            if len(result) >= 20_000:
                return result
    return result


def _read_package_manifests(root: Path) -> list[dict[str, Any]]:
    manifests: list[dict[str, Any]] = []
    candidates = [root / "package.json"]
    for path in sorted(root.glob("packages/*/package.json"))[:100]:
        candidates.append(path)
    for path in candidates:
        if path.is_symlink():
            continue
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeError):
            continue
        manifests.append({
            "name": value.get("name"),
            "description": value.get("description") if isinstance(value.get("description"), str) else "",
            "dependencies": value.get("dependencies", {}) if isinstance(value.get("dependencies", {}), dict) else {},
            "devDependencies": value.get("devDependencies", {}) if isinstance(value.get("devDependencies", {}), dict) else {},
            "scripts": {key: _redact_command(command) for key, command in value.get("scripts", {}).items() if isinstance(key, str) and isinstance(command, str)} if isinstance(value.get("scripts", {}), dict) else {},
        })
    return manifests


def _read_toml(path: Path) -> dict[str, Any]:
    if path.is_symlink():
        return {}
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError, UnicodeError):
        return {}


def _python_dependencies(pyproject: dict[str, Any]) -> dict[str, str]:
    project = pyproject.get("project", {})
    if not isinstance(project, dict):
        return {}
    names: dict[str, str] = {}
    for item in project.get("dependencies", []):
        if isinstance(item, str):
            match = re.match(r"([A-Za-z0-9_.-]+)", item)
            if match:
                names[match.group(1).casefold()] = "declared"
    return names


def _redact_command(command: str) -> str:
    """Retain useful script hints while removing common inline secret values."""
    value = re.sub(
        r"(?i)([A-Z0-9_]*(?:API[_-]?KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL|PRIVATE[_-]?KEY)[A-Z0-9_]*\s*=\s*)(?:\"[^\"]*\"|'[^']*'|[^\s;&]+)",
        r"\1[REDACTED]",
        command,
    )
    value = re.sub(r"(?i)(--(?:api[-_]?key|token|secret|password)(?:=|\s+))[^\s;&]+", r"\1[REDACTED]", value)
    value = re.sub(r"(?i)\bBearer\s+[^\s;&]+", "Bearer [REDACTED]", value)
    value = re.sub(r"(https?://)[^/@\s:]+:[^/@\s]+@", r"\1[REDACTED]@", value)
    return value[:500]


def _project_name(root: Path, manifests: list[dict[str, Any]], pyproject: dict[str, Any]) -> str:
    if manifests and isinstance(manifests[0].get("name"), str):
        return manifests[0]["name"]
    name = pyproject.get("project", {}).get("name") if isinstance(pyproject.get("project"), dict) else None
    return name if isinstance(name, str) else root.name


def _application_description(root: Path, manifests: list[dict[str, Any]], pyproject: dict[str, Any]) -> str:
    for description in [*(item.get("description", "") for item in manifests), pyproject.get("project", {}).get("description", "") if isinstance(pyproject.get("project"), dict) else ""]:
        if isinstance(description, str) and description.strip():
            return description.strip()[:600]
    for candidate in (root / "README.md", root / "readme.md"):
        try:
            lines = candidate.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        paragraph: list[str] = []
        for line in lines:
            value = line.strip()
            if not value or value.startswith(("#", "```", "[!", "<")):
                if paragraph:
                    break
                continue
            paragraph.append(value)
        if paragraph:
            return " ".join(paragraph)[:600]
    return ""


def _languages(files: list[Path]) -> list[str]:
    ext_map = {".ts": "TypeScript", ".tsx": "TypeScript", ".js": "JavaScript", ".jsx": "JavaScript", ".py": "Python", ".css": "CSS", ".scss": "SCSS", ".html": "HTML", ".vue": "Vue SFC", ".svelte": "Svelte"}
    return sorted({ext_map[path.suffix.lower()] for path in files if path.suffix.lower() in ext_map})


def _detected_tools(dependencies: dict[str, Any], packages: tuple[str, ...]) -> list[str]:
    return [name for name in packages if name in dependencies]


def _test_tools(dependencies: dict[str, Any], scripts: dict[str, str], files: list[Path]) -> list[str]:
    found = _detected_tools(dependencies, ("pytest", "jest", "vitest", "@playwright/test", "playwright", "cypress", "@testing-library/react", "@testing-library/vue"))
    if any("test" in key.casefold() for key in scripts):
        found.append("package.json test script")
    if any("test" in part.casefold() or "spec" in part.casefold() for path in files for part in path.parts[-2:-1]):
        found.append("test/spec source paths")
    return sorted(set(found))


def _styling_summary(dependencies: dict[str, Any], css_files: list[Path], token_count: int, media: int, focus: int, reduced_motion: int) -> dict[str, Any]:
    methods = []
    for package, label in (("tailwindcss", "Tailwind CSS"), ("styled-components", "styled-components"), ("@emotion/react", "Emotion"), ("sass", "Sass"), ("less", "Less"), ("postcss", "PostCSS")):
        if package in dependencies:
            methods.append(label)
    if css_files:
        methods.append("CSS / CSS modules")
    return {"methods": sorted(set(methods)), "css_file_count": len(css_files), "custom_property_count": token_count, "media_query_count": media, "focus_selector_count": focus, "reduced_motion_rule_count": reduced_motion}


def _route_files(files: list[Path], root: Path) -> list[str]:
    route_markers = {"app", "pages", "routes", "router"}
    return sorted(str(path.relative_to(root)) for path in files if any(part.casefold() in route_markers for part in path.relative_to(root).parts[:-1]) and path.suffix.lower() in {".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte", ".html"})[:300]


def _codex_config() -> dict[str, Any]:
    home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    return _read_toml(home / "config.toml")


def _safe_probe(command: list[str], *, stdout_limit: int = 4_000) -> dict[str, Any]:
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=12, check=False, env=_clean_codex_environment())
        return {"returncode": result.returncode, "stdout": result.stdout[:stdout_limit], "stderr": result.stderr[:2_000]}
    except (OSError, subprocess.TimeoutExpired) as error:
        return {"returncode": 1, "error": type(error).__name__}


def _clean_codex_environment() -> dict[str, str]:
    """Pass only the small process environment Codex needs for saved-account execution."""
    environment = _clean_process_environment()
    allowed = {
        "PATH", "HOME", "USER", "LOGNAME", "SHELL", "CODEX_HOME", "TMPDIR", "TMP", "TEMP", "LANG", "LC_ALL", "LC_CTYPE", "TERM",
        "SYSTEMROOT", "WINDIR", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "XDG_CONFIG_HOME", "XDG_DATA_HOME", "SSL_CERT_FILE",
        "NODE_EXTRA_CA_CERTS",
    }
    return {name: value for name, value in environment.items() if name in allowed}


def _clean_process_environment() -> dict[str, str]:
    """Remove Git redirection variables while preserving explicit local command configuration."""
    environment = os.environ.copy()
    for name in tuple(environment):
        if name.startswith("GIT_"):
            environment.pop(name, None)
    return environment


def discover_claude_code(project_root: Path, claude_executable: str | None = None) -> dict[str, Any]:
    """Discover Claude Code metadata and supported interfaces without running skills or agents."""
    executable = claude_executable or shutil.which("claude")
    if executable:
        version = _safe_probe([executable, "--version"])
        auth = _safe_probe([executable, "auth", "status", "--json"])
        help_result = _safe_probe([executable, "--help"], stdout_limit=20_000)
        try:
            auth_data = json.loads(auth.get("stdout", ""))
        except json.JSONDecodeError:
            auth_data = {}
        logged_in = auth_data.get("loggedIn") is True
        environment_auth = bool(os.environ.get("ANTHROPIC_API_KEY"))
        version_lines = [line.strip() for line in version.get("stdout", "").splitlines() if line.strip()]
        help_text = help_result.get("stdout", "")
        cli = {
            "installed": version.get("returncode") == 0,
            "path": executable,
            "version": version_lines[0] if version_lines else None,
            "authenticated": logged_in or environment_auth,
            "auth_mode": "account" if logged_in else "api_key_environment" if environment_auth else "unknown_or_signed_out",
            "print_mode_supported": "--print" in help_text or "-p, --print" in help_text,
            "structured_output_supported": "--json-schema" in help_text and "--output-format" in help_text,
            "named_agent_supported": "--agent" in help_text,
            "tool_allowlist_supported": "--tools" in help_text,
            "strict_mcp_config_supported": "--strict-mcp-config" in help_text,
            "permission_mode_supported": "--permission-mode" in help_text,
            "disallowed_tools_supported": "--disallowedTools" in help_text,
            "setting_sources_supported": "--setting-sources" in help_text,
            "mcp_config_supported": "--mcp-config" in help_text,
        }
    else:
        cli = {"installed": False, "version": None, "authenticated": False, "auth_mode": "unavailable"}

    config_home = Path(os.environ.get("CLAUDE_CONFIG_DIR", str(Path.home() / ".claude")))
    project_roots: list[Path] = []
    current = project_root.resolve()
    while True:
        project_roots.append(current)
        if (current / ".git").exists() or current.parent == current:
            break
        current = current.parent
    skills = _discover_claude_markdown(project_roots, config_home, "skills", "SKILL.md")
    agents = _discover_claude_markdown(project_roots, config_home, "agents", "*.md")
    plugins = _discover_claude_plugins(executable, project_roots, config_home) if executable else []
    mcp_servers = _discover_claude_mcp(project_roots, config_home)
    return {
        "cli": cli,
        "skills": skills,
        "agents": agents,
        "plugins": plugins,
        "mcp_servers": mcp_servers,
        "discovery_boundary": "Metadata and local CLI capability checks only; skill/agent instructions and MCP tools were not executed.",
    }


def _discover_claude_markdown(project_roots: list[Path], config_home: Path, kind: str, pattern: str) -> list[dict[str, Any]]:
    resources: list[dict[str, Any]] = []
    roots = [root / ".claude" / kind for root in project_roots]
    roots.append(config_home / kind)
    seen: set[Path] = set()
    count = 0
    for root in roots:
        if not root.is_dir():
            continue
        try:
            files = sorted(root.rglob(pattern))
        except OSError:
            continue
        for path in files:
            count += 1
            if count > MAX_SKILLS:
                return resources
            try:
                resolved = path.resolve(strict=True)
                if resolved in seen or not resolved.is_file() or resolved.stat().st_size > SKILL_LIMIT_BYTES:
                    continue
                seen.add(resolved)
                text = resolved.read_text(encoding="utf-8", errors="replace")
                metadata = _skill_frontmatter(text[:4_096])
                name = metadata.get("name") or (resolved.parent.name if resolved.name == "SKILL.md" else resolved.stem)
                description = metadata.get("description", "")
                capabilities = classify_skill(name, description)
                if not capabilities:
                    continue
                resource = {
                    "name": name,
                    "description": description,
                    "source_path": str(resolved),
                    "capabilities": capabilities,
                    "metadata_only": True,
                    "compatibility_confidence": "documented_claude_code_location",
                    "metadata_valid": bool(description),
                }
                if str(name).casefold() in {"impeccable", "design-taste-frontend"} and resolved.name == "SKILL.md":
                    resource.update(_preferred_skill_metadata(resolved, text, project_roots[0], metadata))
                resources.append(resource)
            except (OSError, UnicodeError):
                continue
    return sorted(resources, key=lambda item: (item["name"].casefold(), item["source_path"]))


def _discover_claude_plugins(executable: str, project_roots: list[Path], config_home: Path) -> list[dict[str, Any]]:
    probe = _safe_probe([executable, "plugin", "list", "--json"], stdout_limit=100_000)
    try:
        payload = json.loads(probe.get("stdout", "")) if probe.get("returncode") == 0 else None
    except json.JSONDecodeError:
        payload = None
    entries = payload if isinstance(payload, list) else payload.get("plugins", []) if isinstance(payload, dict) else []
    installed = {str(item.get("id") or item.get("name")): item for item in entries if isinstance(item, dict)}

    configured: dict[str, dict[str, Any]] = {}
    settings_paths = [config_home / "settings.json"]
    for root in project_roots:
        settings_paths.extend([root / ".claude" / "settings.json", root / ".claude" / "settings.local.json"])
    for path in settings_paths:
        data = _read_json_object(path)
        plugins = data.get("enabledPlugins", {})
        if isinstance(plugins, dict):
            for name, enabled in plugins.items():
                configured[str(name)] = {"enabled": enabled is not False, "settings_path": str(path)}

    result: dict[str, dict[str, Any]] = {}
    for name, details in installed.items():
        record = {"name": name, "installed": True, "configured": name in configured, "callable": "not_probed"}
        record.update({key: details.get(key) for key in ("version", "scope", "status") if isinstance(details.get(key), (str, int, bool))})
        if name in configured:
            record["enabled"] = configured[name]["enabled"]
        result[name] = record
    for name, settings in configured.items():
        result.setdefault(name, {"name": name, "installed": "unknown", "configured": True, "enabled": settings["enabled"], "callable": "not_probed"})
    return sorted(result.values(), key=lambda item: item["name"].casefold())


def _discover_claude_mcp(project_roots: list[Path], config_home: Path) -> list[dict[str, Any]]:
    paths = [config_home.parent / ".claude.json", config_home / "settings.json"]
    for root in project_roots:
        paths.extend([root / ".mcp.json", root / ".claude" / "settings.json", root / ".claude" / "settings.local.json"])
    found: dict[str, dict[str, Any]] = {}
    for path in paths:
        data = _read_json_object(path)
        servers = data.get("mcpServers", {})
        if not isinstance(servers, dict):
            continue
        for name, raw in servers.items():
            if not isinstance(raw, dict):
                continue
            found.setdefault(str(name), {
                "name": str(name),
                "configured": True,
                "callable": "not_probed",
                "transport": "url" if raw.get("url") else "stdio" if raw.get("command") else "unknown",
                "source_scope": "project" if path.is_relative_to(project_roots[0]) else "user",
            })
    return sorted(found.values(), key=lambda item: item["name"].casefold())


def _read_json_object(path: Path) -> dict[str, Any]:
    try:
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 1_000_000:
            return {}
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _cached_plugins(config: dict[str, Any]) -> list[dict[str, Any]]:
    """Inspect local manifests only; do not query a remote plugin catalog."""
    codex_home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    roots = [codex_home / ".tmp" / "plugins", codex_home / "plugins" / "cache", Path.home() / ".cache" / "codex-runtimes"]
    plugins: dict[str, dict[str, Any]] = {}
    plugin_settings = config.get("plugins", {}) if isinstance(config.get("plugins", {}), dict) else {}
    scanned = 0
    for root in roots:
        if not root.exists():
            continue
        for manifest in root.rglob("plugin.json"):
            scanned += 1
            if scanned > 2_000:
                break
            try:
                value = json.loads(manifest.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError, UnicodeError):
                continue
            name = value.get("name")
            if not isinstance(name, str):
                continue
            key = f"{name}@{manifest.parent.parent.name}"
            settings = next((entry for configured_name, entry in plugin_settings.items() if configured_name.split("@", 1)[0] == name and isinstance(entry, dict)), {})
            plugins[key] = {
                "name": name,
                "manifest_path": str(manifest.resolve()),
                "local_manifest_observed": True,
                "installed": "unknown_without_codex_plugin_list",
                "configured": bool(settings),
                "enabled": settings.get("enabled", "unknown_without_codex_plugin_list") if settings else "unknown_without_codex_plugin_list",
                "callable": "not_probed",
            }
    return sorted(plugins.values(), key=lambda item: item["name"].casefold())
