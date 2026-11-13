"""Read-only discovery of Codex capabilities and frontend project conventions."""

from __future__ import annotations

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
    "frontend": ("frontend", "front-end", "web", "ui", "interface", "component"),
    "visual": ("visual", "design", "styling", "typography", "color", "layout", "figma", "screenshot"),
    "accessibility": ("accessibility", "a11y", "wcag", "keyboard", "screen reader"),
    "ux": ("ux", "interaction", "responsive", "mobile", "behavior", "user experience"),
    "browser": ("browser", "playwright", "cypress", "screenshot", "visual regression"),
    "performance": ("performance", "web vitals", "bundle", "rendering", "lighthouse"),
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
                with resolved.open("r", encoding="utf-8", errors="replace") as stream:
                    text = stream.read(4_096)
                metadata = _skill_frontmatter(text)
                if not metadata.get("name") or not metadata.get("description"):
                    errors.append({"path": str(path), "error": "missing name or description frontmatter"})
                    continue
                capabilities = classify_skill(str(metadata["name"]), str(metadata["description"]))
                if not capabilities:
                    continue
                skills.append({
                    "name": str(metadata["name"]),
                    "description": str(metadata["description"]),
                    "source_path": str(resolved),
                    "capabilities": capabilities,
                    "compatibility_confidence": "documented_location" if _is_documented_skill_location(resolved) else "observed_install_location",
                    "metadata_only": True,
                })
            except (OSError, UnicodeError) as error:
                errors.append({"path": str(path), "error": type(error).__name__})
    unique = {item["source_path"]: item for item in skills}
    return sorted(unique.values(), key=lambda item: item["name"].casefold()), errors


def discover_agents(project_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    """Inspect documented Codex custom-agent files without executing their instructions."""
    roots = [project_root / ".codex" / "agents", Path.home() / ".codex" / "agents"]
    codex_home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    if codex_home != roots[-1]:
        roots.append(codex_home / "agents")
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
        cli = {"installed": False, "version": None, "authenticated": False, "auth_mode": "unavailable"}
    else:
        version_result = _safe_probe([executable, "--version"])
        auth_result = _safe_probe([executable, "login", "status"])
        version_text = (version_result.get("stdout") or "").strip().splitlines()
        auth_text = ((auth_result.get("stdout") or "") + (auth_result.get("stderr") or "")).casefold()
        chatgpt_auth = "logged in using chatgpt" in auth_text or "chatgpt account" in auth_text
        api_auth = "api key" in auth_text or "apikey" in auth_text
        cli = {
            "installed": version_result.get("returncode") == 0,
            "path": executable,
            "version": version_text[0] if version_text else None,
            "authenticated": auth_result.get("returncode") == 0 and (chatgpt_auth or api_auth),
            "auth_mode": "chatgpt_plan" if chatgpt_auth else "api_key" if api_auth else "unknown_or_signed_out",
            "codex_exec_supported": version_result.get("returncode") == 0,
            "structured_output_supported": version_result.get("returncode") == 0,
            "sandbox_modes": ["read-only", "workspace-write"],
            "probe_errors": [item for item in (version_result.get("error"), auth_result.get("error")) if item],
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
    codex_ready = bool(codex.get("cli", {}).get("installed") and codex.get("cli", {}).get("authenticated") and codex.get("cli", {}).get("auth_mode") == "chatgpt_plan")
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
            available=bool(codex_ready and screenshots),
            selected_tool="Codex CLI plus rendered screenshots" if codex_ready and screenshots else None,
            status="ready" if codex_ready and screenshots else "missing",
            recommendation="Capture representative views with the browser-testing capability before making appearance claims. The same screenshots can be used for visual review; do not install an overlapping screenshot tool." if not screenshots else "Rendered screenshots are available, but Codex visual analysis is unavailable without saved ChatGPT sign-in." if not codex_ready else "Rendered screenshots are available for review; claims must stay limited to the captured routes and states.",
            details={"rendered_evidence_count": len(screenshots), "codex_ready_with_chatgpt_sign_in": codex_ready},
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
            available=True,
            selected_tool="Codex CLI isolated prototype" if codex_ready else "Built-in responsive HTML/CSS scaffold",
            status="ready",
            recommendation="Codex refinement is optional; the local responsive template works without credentials or model calls.",
            details={"codex_refinement_available": codex_ready},
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
    return [category for category, terms in FRONTEND_TERMS.items() if any(term in text for term in terms)]


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


def _safe_probe(command: list[str]) -> dict[str, Any]:
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=12, check=False, env=_clean_codex_environment())
        return {"returncode": result.returncode, "stdout": result.stdout[:4_000], "stderr": result.stderr[:2_000]}
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
