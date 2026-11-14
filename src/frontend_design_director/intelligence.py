"""Deterministic source and rendered-evidence inventories for frontend audits.

These inventories describe what was observed and where. They intentionally do
not infer visual quality from stylesheet definitions alone.
"""

from __future__ import annotations

import json
import hashlib
import os
import posixpath
import re
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

from .models import AuditType, Confidence, EvidenceReference, Finding, Severity, VerificationStatus


SOURCE_SUFFIXES = {".html", ".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx", ".vue", ".svelte", ".astro"}
STYLE_SUFFIXES = {".css", ".scss", ".sass", ".less"}
ANALYSIS_SUFFIXES = SOURCE_SUFFIXES | STYLE_SUFFIXES | {".json", ".toml", ".yaml", ".yml"}
IGNORED_DIRECTORIES = {
    ".git", ".agents", ".codex", ".frontend-design-director", "node_modules", "vendor",
    "dist", "build", "coverage", ".next", ".nuxt", ".svelte-kit", ".venv", "venv", "__pycache__",
}
MAX_INSPECTED_FILES = 20_000
MAX_FILE_BYTES = 2_000_000

COLOR_VALUE = re.compile(r"(?i)(#[0-9a-f]{3,8}\b|(?:rgb|hsl|hwb|oklch|lab|lch)a?\([^)]{1,100}\))")
DIMENSION_VALUE = re.compile(r"(?<![\w.-])(?:\d+(?:\.\d+)?|\.\d+)(?:px|rem|em|vh|vw|ch|%)(?![\w-])", re.I)
FONT_FAMILY = re.compile(r"(?i)font-family\s*:\s*([^;{}]+)")
FONT_SIZE = re.compile(r"(?i)font-size\s*:\s*([^;{}]+)")
LINE_HEIGHT = re.compile(r"(?i)line-height\s*:\s*([^;{}]+)")
CSS_VARIABLE = re.compile(r"--([\w-]+)\s*:\s*([^;{}]+)")
IMPORT_SPECIFIER = re.compile(r"(?m)^\s*import\s+(?:[^\n]*?\s+from\s+)?[\"']([^\"']+)[\"']")
EXPORT_NAME = re.compile(r"\bexport\s+(?:default\s+)?(?:function|class|const|let|var)\s+([A-Z][\w$]*)")
FUNCTION_NAME = re.compile(r"\bfunction\s+([A-Z][\w$]*)\s*\(")
ROUTE_LITERAL = re.compile(r"(?:path|to|href)\s*[:=]\s*[\"'](/[^\"']*)[\"']")
ROUTE_RELATIVE_LITERAL = re.compile(r"(?i)path\s*:\s*[\"']([^/\"'][^\"']*)[\"']")
HTML_ANCHOR_HREF = re.compile(r"<a\b[^>]*\bhref\s*=\s*[\"']([^\"']+)[\"']", re.I)
HTML_SCRIPT_SRC = re.compile(r"<script\b[^>]*\bsrc\s*=\s*[\"']([^\"']+)[\"']", re.I)


def build_project_intelligence(project_root: Path, project: dict[str, Any], screenshots: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Build route, component, styling, and runtime inventories from local evidence."""
    root = project_root.resolve(strict=True)
    files = _project_files(root)
    source_files = [path for path in files if path.suffix.casefold() in SOURCE_SUFFIXES]
    style_files = [path for path in files if path.suffix.casefold() in STYLE_SUFFIXES]
    relative_source = {path.relative_to(root).as_posix(): path for path in source_files}
    file_text = {key: _read_text(path) for key, path in relative_source.items()}
    routes = _discover_routes(root, source_files, file_text)
    components = _discover_components(root, source_files, file_text, routes)
    components.extend(_discover_html_components(root, source_files, file_text))
    component_by_path = {item["source"]: item for item in components if item.get("evidence_kind") != "static_html_structure"}
    for route in routes:
        source_path = route["source"]
        source_file = root / source_path
        linked: list[str] = []
        modules: list[str] = []
        if source_file.suffix.casefold() == ".html":
            linked.extend(item["name"] for item in components if item.get("evidence_kind") == "static_html_structure" and item["source"] == source_path)
            for module in HTML_SCRIPT_SRC.findall(file_text.get(source_path, "")):
                parsed = urlsplit(module)
                if parsed.scheme or parsed.netloc or module.startswith(("#", "javascript:")):
                    continue
                if parsed.path.startswith("/"):
                    candidate = (root / unquote(parsed.path).lstrip("/")).resolve()
                    resolved = candidate if candidate.is_relative_to(root) and candidate.is_file() and not candidate.is_symlink() else None
                else:
                    resolved = _resolve_import(source_file, unquote(parsed.path), root) if parsed.path else None
                if resolved:
                    modules.append(resolved.relative_to(root).as_posix())
        for module in IMPORT_SPECIFIER.findall(file_text.get(source_path, "")):
            if module.startswith("."):
                resolved = _resolve_import(source_file, module, root)
                if resolved:
                    target = resolved.relative_to(root).as_posix()
                    if target in component_by_path:
                        linked.append(component_by_path[target]["name"])
                        component_by_path[target]["routes"].append(route["path"])
        route["components"] = sorted(set(linked))
        route["modules"] = sorted(set(modules))
    for component in components:
        component["routes"] = sorted(set(component.get("routes", [])))
    design_system = _discover_design_system(root, style_files)
    groups = _architecture_groups(root, files)
    runtime = _runtime_records(screenshots or [])
    return {
        "schema_version": 1,
        "project": {
            "name": project.get("project_name", root.name),
            "root": str(root),
            "description": project.get("application_description", ""),
            "frameworks": project.get("frameworks", []),
            "languages": project.get("languages", []),
            "build_tools": project.get("build_tools", []),
            "routing_signals": project.get("routing", []),
            "source_file_count": len(source_files),
            "stylesheet_count": len(style_files),
        },
        "architecture": groups,
        "routes": routes,
        "components": components,
        "design_system": design_system,
        "runtime": runtime,
        "coverage": {
            "source_files_inspected": len(source_files) + len(style_files),
            "routes_discovered": len(routes),
            "routes_rendered": len({item["route"] for item in runtime}),
            "screenshots_captured": len(runtime),
            "screenshots_valid": sum(item.get("visual_evidence_status", "valid") == "valid" for item in runtime),
            "rendered_viewports": sorted({item.get("viewport_label", item["viewport"]) for item in runtime if item.get("viewport")}),
            "component_profiles": len(components),
            "rendered_evidence_available": bool(runtime),
            "evidence_boundary": "Source inventories are static observations. Visual appearance claims require linked rendered screenshots.",
        },
    }


def renderable_route_candidates(intelligence: dict[str, Any]) -> list[str]:
    """Return deduplicated static route paths; dynamic parameter patterns are never invented."""
    routes = set()
    for route in intelligence.get("routes", []):
        value = route.get("path")
        if not isinstance(value, str) or not value.startswith("/") or "\\" in value or "?" in value or "#" in value:
            continue
        decoded = unquote(value)
        segments = decoded.split("/")
        if any(segment in {".", ".."} for segment in segments) or any(segment.startswith(":") for segment in segments):
            continue
        routes.add(value)
    return sorted(routes)


def attach_runtime_evidence(intelligence: dict[str, Any], screenshots: list[dict[str, Any]]) -> dict[str, Any]:
    """Attach browser evidence to a source inventory without re-reading the project."""
    result = json.loads(json.dumps(intelligence))
    runtime = _runtime_records(screenshots)
    result["runtime"] = runtime
    coverage = result["coverage"]
    valid_default = [
        item for item in runtime
        if item.get("visual_evidence_status", "valid") == "valid"
        and item.get("interaction_state", "default") == "default"
    ]
    coverage.update({
        "routes_rendered": len({item["route"] for item in valid_default}),
        "screenshots_captured": len(runtime),
        "screenshots_valid": sum(item.get("visual_evidence_status", "valid") == "valid" for item in runtime),
        "rendered_viewports": sorted({item.get("viewport_label", item["viewport"]) for item in valid_default if item.get("viewport")}),
        "rendered_evidence_available": bool(valid_default),
        "valid_route_viewport_pairs": len({(item["route"], item.get("viewport_label", item["viewport"])) for item in valid_default}),
    })
    return result


def _runtime_records(screenshots: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "route": item.get("route", "/"),
            "viewport": item.get("viewport"),
            "viewport_label": item.get("viewport_label", item.get("viewport")),
            "interaction_state": item.get("interaction_state", "default"),
            "focus_target": item.get("focus_target", {}),
            "focus_capture_error": item.get("focus_capture_error"),
            "width": item.get("width"),
            "height": item.get("height"),
            "route_slug": item.get("route_slug"),
            "screenshot": item.get("path"),
            "rendered_url": item.get("rendered_url"),
            "captured_at": item.get("captured_at"),
            "capture_status": item.get("capture_status"),
            "visual_evidence_status": item.get("visual_evidence_status", "valid"),
            "image_format": item.get("image_format"),
            "image_dimensions": item.get("image_dimensions"),
            "image_byte_size": item.get("image_byte_size"),
            "image_sha256": item.get("image_sha256"),
            "http_status": item.get("http_status"),
            "readiness": item.get("readiness", {}),
            "page_errors": item.get("page_errors", []),
            "console_errors": item.get("console_errors", []),
            "failed_requests": item.get("failed_requests", []),
            "document": item.get("document", {}),
            "landmarks": item.get("landmarks", {}),
            "controls": item.get("controls", {}),
            "computed_styles": item.get("computed_styles", {}),
            "contrast_samples": _contrast_samples(item.get("computed_styles", {})),
            "navigation_timing": item.get("navigation_timing", {}),
        }
        for item in screenshots
        if item.get("evidence_type") == "rendered_browser_screenshot"
    ]


def runtime_findings(intelligence: dict[str, Any]) -> list[Finding]:
    """Turn objective browser observations into scoped, evidence-linked findings."""
    observations: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for item in intelligence.get("runtime", []):
        if item.get("visual_evidence_status", "valid") != "valid":
            continue
        route = item.get("route", "/")
        screenshot = item.get("screenshot")
        viewport = item.get("viewport")
        if not screenshot or not viewport:
            continue
        document = item.get("document", {})
        viewport_width = item.get("width")
        if isinstance(viewport_width, int) and isinstance(document.get("width"), int) and document["width"] > viewport_width:
            key = ("visual", route)
            observations.setdefault(key, []).append({**item, "detail": f"document scroll width {document['width']}px exceeds viewport width {viewport_width}px"})
        controls = item.get("controls", {})
        unlabeled = controls.get("inputs_without_associated_label", 0)
        if isinstance(unlabeled, int) and unlabeled > 0:
            key = ("accessibility", route)
            observations.setdefault(key, []).append({**item, "detail": f"{unlabeled} input control(s) had no associated label, aria-label, or aria-labelledby in the captured DOM"})
        for error in item.get("page_errors", []):
            key = ("runtime", route + "\0" + str(error))
            observations.setdefault(key, []).append({**item, "detail": f"uncaught browser exception: {error}"})

    findings: list[Finding] = []
    for (kind, identity), items in sorted(observations.items()):
        first = items[0]
        route = first.get("route", "/")
        detail = first["detail"]
        if kind == "visual":
            audit_type, category, title, severity = AuditType.VISUAL, "responsive_overflow", "Rendered document exceeds the viewport width", Severity.MEDIUM
            impact = "Content may be clipped or require unintended horizontal scrolling at this captured viewport."
            recommendation = "Inspect the cited route and breakpoint to identify which rendered element causes the overflow before changing the layout."
        elif kind == "accessibility":
            audit_type, category, title, severity = AuditType.BEHAVIORAL, "form_labels", "Rendered inputs lack a programmatic label", Severity.MEDIUM
            impact = "Screen-reader users may not receive a reliable accessible name for the captured form controls."
            recommendation = "Associate each affected input with a visible label or an appropriate accessible name, then verify with assistive technology."
        else:
            audit_type, category, title, severity = AuditType.TECHNICAL, "runtime_exception", "Uncaught browser exception observed", Severity.MEDIUM
            impact = "An uncaught exception can interrupt the affected route's rendering or interactions."
            recommendation = "Trace the exception to its source and verify the affected route's loading and error-recovery behavior."
        evidence = tuple(
            EvidenceReference("runtime_observation", item["screenshot"], item["detail"], viewport=item["viewport"])
            for item in items[:6]
        )
        findings.append(Finding(
            id=_finding_id(audit_type.value, category, title + identity),
            audit_type=audit_type,
            category=category,
            severity=severity,
            title=title,
            description=detail,
            affected_routes=(route,),
            evidence=evidence,
            impact=impact,
            recommendation=recommendation,
            confidence=Confidence.HIGH,
            verification_status=VerificationStatus.OBSERVED,
            requires_human_decision=False,
        ))
    return findings


def intelligence_reports(intelligence: dict[str, Any]) -> dict[str, bytes]:
    """Render navigable, source-linked architecture and design evidence reports."""
    routes = intelligence["routes"]
    components = intelligence["components"]
    design = intelligence["design_system"]
    coverage = intelligence["coverage"]
    project = intelligence["project"]
    runtime = intelligence["runtime"]

    architecture = [
        "# Frontend architecture map", "",
        f"Project: `{project['name']}`", f"Root: `{project['root']}`",
        f"Application description: {project.get('description') or 'Not documented in inspected package metadata or README.'}",
        f"Framework signals: {', '.join(project['frameworks']) or 'not detected'}",
        f"Languages: {', '.join(project['languages']) or 'not detected'}", "",
        "This map is derived from repository structure, package metadata, and route/import declarations. It does not execute application code.",
        "", "## Application structure", "",
    ]
    for group, paths in intelligence["architecture"].items():
        architecture.extend([f"### {group.replace('_', ' ').title()}", ""])
        architecture.extend(f"- `{path}`" for path in paths) if paths else architecture.append("- No files detected.")
        architecture.append("")
    architecture.extend(["## Runtime evidence", ""])
    if runtime:
        architecture.append(f"Rendered {coverage['routes_rendered']} route(s) at {', '.join(coverage['rendered_viewports']) or 'unknown viewports'} using an explicitly supplied browser URL.")
    else:
        architecture.append("No rendered browser evidence was collected. Runtime behavior and actual appearance remain unverified.")
    architecture.extend(["", "## Route relationships", ""])
    for route in routes:
        linked = ", ".join(f"`{item}`" for item in route.get("components", [])) or "no component relationship inferred"
        modules = ", ".join(f"`{item}`" for item in route.get("modules", [])) or "no local script module linked"
        architecture.append(f"- `{route['path']}` ← `{route['source']}` ({route['classification']}; {route['confidence']} confidence); components: {linked}; modules: {modules}.")
    if not routes:
        architecture.append("No route declarations or link targets were recognized in the inspected source.")

    screen_lines = ["# Route and screen inventory", "", f"Discovered {len(routes)} route candidate(s) from source conventions, router literals, and local links. Dynamic segments are documented as patterns and were not navigated automatically.", ""]
    screen_lines.extend(["| Route | Type | Source | Discovery | Confidence | Rendered |", "|---|---|---|---|---|---|"])
    rendered_routes = {item["route"] for item in runtime}
    for route in routes:
        rendered = "Yes" if route["path"] in rendered_routes else "No"
        source = route["source"].replace("|", "\\|")
        screen_lines.append(f"| `{route['path']}` | {route['classification']} | `{source}` | {', '.join(route['methods'])} | {route['confidence']} | {rendered} |")
    if not routes:
        screen_lines.append("| No routes identified | — | — | — | — | No |")
    screen_lines.extend(["", "## Coverage boundary", "", "The browser visits only the supplied base URL and any exact paths explicitly provided by the operator. A source route candidate is not proof that a route is reachable or authenticated."])

    component_lines = ["# Component inventory", "", f"Profiles are source-derived and link imports to route candidates where a local module path can be resolved. Rendered appearance is described only when browser evidence exists.", ""]
    if not components:
        component_lines.append("No component-like source modules were identified by the current framework-neutral heuristics.")
    for item in components:
        source_location = ", ".join(str(line) for line in item.get("source_lines", [])) or f"1–{item['line_count']}"
        component_lines.extend([
            f"## {item['name']}", "",
            f"- Source: `{item['source']}` (lines {item['line_count']})",
            f"- Classification: {item['classification']} ({item['confidence']} confidence)",
            f"- Exported symbols: {', '.join(f'`{name}`' for name in item['exports']) or 'not statically identified'}",
            f"- Public signature: `{item.get('signature') or 'not statically identified'}`",
            f"- Imported local modules: {', '.join(f'`{name}`' for name in item['local_imports']) or 'none resolved'}",
            f"- Route candidates: {', '.join(f'`{name}`' for name in item['routes']) or 'none linked'}",
            f"- Source evidence: `{item['source']}` lines {source_location}",
            f"- Static occurrences: {item.get('occurrence_count', 1)}; element: `{item.get('element', 'module')}`; role: `{item.get('role') or 'not declared'}`", "",
        ])

    design_lines = [
        "# Design-system analysis", "",
        "## Evidence boundary", "",
        "The inventories below describe source-defined CSS values. They do not establish that a value is used in the rendered interface. Runtime samples are listed separately and are limited to captured routes and viewports.", "",
        "## Color inventory", "",
        f"Found {len(design['colors'])} distinct color literals and {len(design['custom_properties'])} custom-property definitions across {len(design['stylesheet_files'])} stylesheet(s).", "",
        "| Value | Occurrences | Source files |", "|---|---:|---|",
    ]
    design_lines.extend(f"| `{item['value']}` | {item['count']} | {', '.join(f'`{path}`' for path in item['files'])} |" for item in design["colors"][:120])
    if not design["colors"]:
        design_lines.append("| No color literals identified | 0 | — |")
    design_lines.extend(["", "## CSS custom properties", "", "| Token | Defined value | File |", "|---|---|---|"])
    design_lines.extend(f"| `--{item['name']}` | `{item['value']}` | `{item['file']}` |" for item in design["custom_properties"][:300])
    design_lines.extend(["", "## Typography", "", "### Font families", ""])
    design_lines.extend(f"- `{item['value']}` — {item['count']} declaration(s) in {', '.join(f'`{path}`' for path in item['files'])}" for item in design["font_families"])
    if not design["font_families"]:
        design_lines.append("No `font-family` declarations found in inspected stylesheets.")
    design_lines.extend(["", "### Font sizes and line heights", "", f"Font-size values: {', '.join(f'`{item}`' for item in design['font_sizes']) or 'none found'}", "", f"Line-height values: {', '.join(f'`{item}`' for item in design['line_heights']) or 'none found'}", "", "## Spacing and breakpoints", "", f"Repeated dimensional values (count ≥ 2): {', '.join(f'`{value}` ({count})' for value, count in design['repeated_dimensions'][:60]) or 'none identified'}", "", f"Media-query breakpoints: {', '.join(f'`{item}`' for item in design['breakpoints']) or 'none identified'}", "", "## Runtime computed-style samples", ""])
    if runtime:
        for item in runtime:
            design_lines.append(f"- `{item['route']}` / `{item['viewport']}`: `{item['screenshot']}`; sampled {len(item.get('computed_styles', {}))} selectors. These values are browser-observed, not inferred from source tokens.")
            for sample in item.get("contrast_samples", []):
                design_lines.append(f"  - `{sample['selector']}` text contrast {sample['ratio']}:1 ({sample['classification']}); computed {sample['foreground']} on {sample['background']}.")
    else:
        design_lines.append("No computed styles were captured; actual color, font, and layout usage is not verified.")

    runtime_lines = ["# Runtime and responsive evidence", "", f"Captured {coverage['screenshots_captured']} screenshot(s) across {coverage['routes_rendered']} route(s).", ""]
    if runtime:
        runtime_lines.extend(["| Route | Viewport | Screenshot | HTTP | Page errors | Console errors | Failed requests |", "|---|---|---|---:|---:|---:|---:|"])
        for item in runtime:
            runtime_lines.append(f"| `{item['route']}` | {item['viewport']} ({item.get('interaction_state', 'default')}) | `{item['screenshot']}` | {item.get('http_status') or 'unknown'} | {len(item.get('page_errors', []))} | {len(item.get('console_errors', []))} | {len(item.get('failed_requests', []))} |")
        runtime_lines.extend(["", "## Observations", ""])
        for item in runtime:
            document = item.get("document", {})
            runtime_lines.append(f"### `{item['route']}` at {item['viewport']}")
            runtime_lines.append(f"- Document: {document.get('width', 'unknown')} × {document.get('height', 'unknown')} CSS pixels; title `{document.get('title') or 'empty'}`.")
            runtime_lines.append(f"- Readiness: {json.dumps(item.get('readiness', {}), sort_keys=True)}")
            runtime_lines.append(f"- Landmarks: {json.dumps(item.get('landmarks', {}), sort_keys=True)}")
            if item.get("page_errors"):
                runtime_lines.append(f"- Page errors: {json.dumps(item['page_errors'], ensure_ascii=False)}")
            if item.get("console_errors"):
                runtime_lines.append(f"- Console errors: {json.dumps(item['console_errors'], ensure_ascii=False)}")
            if item.get("failed_requests"):
                runtime_lines.append(f"- Failed requests: {json.dumps(item['failed_requests'], ensure_ascii=False)}")
            runtime_lines.append("")
    else:
        runtime_lines.extend(["No browser was connected. Rendered layout, runtime errors, computed styles, and responsive behavior were not verified.", ""])
    focus_count = sum(item.get("interaction_state") == "keyboard_focus_after_one_tab" for item in runtime)
    runtime_lines.extend(["## Audit completeness", "", f"- Source files inspected: {coverage['source_files_inspected']}", f"- Route candidates: {coverage['routes_discovered']}", f"- Route candidates rendered: {coverage['routes_rendered']}", f"- Browser navigation failures: {len(intelligence.get('browser_navigation_failures', []))}", f"- Component profiles: {coverage['component_profiles']}", f"- Rendered viewports: {', '.join(coverage['rendered_viewports']) or 'none'}", f"- Keyboard focus screenshots: {focus_count}", "- Application controls: not activated; stateful interactions remain unverified."])

    return {
        "frontend-architecture-map.md": _markdown_bytes(architecture),
        "route-and-screen-inventory.md": _markdown_bytes(screen_lines),
        "component-inventory.md": _markdown_bytes(component_lines),
        "design-system-analysis.md": _markdown_bytes(design_lines),
        "runtime-evidence.md": _markdown_bytes(runtime_lines),
        "frontend-intelligence.json": json.dumps(intelligence, indent=2, ensure_ascii=False, sort_keys=True).encode("utf-8"),
    }


def _project_files(root: Path) -> list[Path]:
    found: list[Path] = []
    for base, directories, filenames in os.walk(root, followlinks=False):
        directories[:] = sorted(name for name in directories if name not in IGNORED_DIRECTORIES and not (Path(base) / name).is_symlink())
        for name in sorted(filenames):
            path = Path(base) / name
            if path.is_symlink() or path.suffix.casefold() not in ANALYSIS_SUFFIXES:
                continue
            try:
                if path.stat().st_size <= MAX_FILE_BYTES:
                    found.append(path)
            except OSError:
                continue
            if len(found) >= MAX_INSPECTED_FILES:
                return found
    return found


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _discover_routes(root: Path, source_files: list[Path], contents: dict[str, str]) -> list[dict[str, Any]]:
    routes: dict[str, dict[str, Any]] = {}

    def add(path: str, source: Path, method: str, confidence: str, classification: str | None = None) -> None:
        value = path.strip()
        value = re.sub(r"[?#].*$", "", value)
        if not value.startswith("/") or value.startswith("//") or "\\" in value or "{" in value or "}" in value or len(value) > 240:
            return
        value = _normalize_route_path(value, root)
        if value is None:
            return
        source_priority = {"html_file": 3, "file_route": 3, "router_literal": 2, "internal_link": 1}
        entry = routes.get(value)
        if entry is None:
            entry = {
                "path": value,
                "source": source.relative_to(root).as_posix(),
                "methods": [],
                "confidence": confidence,
                "classification": classification or _classify_route(value, source),
                "_source_priority": source_priority.get(method, 0),
            }
            routes[value] = entry
        elif source_priority.get(method, 0) > entry["_source_priority"]:
            entry["source"] = source.relative_to(root).as_posix()
            entry["classification"] = classification or _classify_route(value, source)
            entry["_source_priority"] = source_priority.get(method, 0)
        if method not in entry["methods"]:
            entry["methods"].append(method)
        if confidence == "high":
            entry["confidence"] = confidence

    for source in source_files:
        relative = source.relative_to(root)
        parts = relative.parts
        folded = [part.casefold() for part in parts[:-1]]
        if source.suffix.casefold() == ".html":
            html_route = relative.as_posix()
            if html_route == "index.html":
                html_route = ""
            elif html_route.endswith("/index.html"):
                html_route = html_route[: -len("index.html")]
            add("/" + html_route.strip("/"), source, "html_file", "high", "static page")
        if "app" in folded and (source.stem.casefold() == "page" or source.suffix.casefold() == ".html"):
            route_parts = []
            app_index = folded.index("app")
            for part in parts[app_index + 1 : -1]:
                if part.startswith("(") and part.endswith(")"):
                    continue
                route_parts.append(_dynamic_segment(part))
            add("/" + "/".join(route_parts), source, "file_route", "high")
        elif "routes" in folded and source.stem.casefold() in {"+page", "page", "index"}:
            marker = folded.index("routes")
            route_parts = [_dynamic_segment(part) for part in parts[marker + 1 : -1] if not (part.startswith("(") and part.endswith(")"))]
            add("/" + "/".join(route_parts), source, "file_route", "high")
        elif "pages" in folded and source.suffix.casefold() in SOURCE_SUFFIXES:
            marker = folded.index("pages")
            route_parts = [_dynamic_segment(part) for part in parts[marker + 1 :]]
            if route_parts and route_parts[-1].casefold() in {"index", "index.tsx", "index.jsx", "index.js", "index.vue", "index.svelte"}:
                route_parts.pop()
            elif route_parts:
                route_parts[-1] = re.sub(r"\.[^.]+$", "", route_parts[-1])
            add("/" + "/".join(route_parts), source, "file_route", "high")
        text = contents.get(relative.as_posix(), "")
        for match in ROUTE_LITERAL.finditer(text):
            add(match.group(1), source, "router_literal", "medium")
        if any(term in source.name.casefold() for term in ("route", "router")) or any(part in {"routes", "router"} for part in folded):
            for match in ROUTE_RELATIVE_LITERAL.finditer(text):
                add("/" + match.group(1).strip("/"), source, "router_literal", "low")
        if source.suffix.casefold() == ".html":
            for match in HTML_ANCHOR_HREF.finditer(text):
                href = match.group(1).strip()
                parsed = urlsplit(href)
                if parsed.scheme or parsed.netloc or href.startswith(("#", "?", "mailto:", "tel:", "javascript:")):
                    continue
                if href.startswith("/"):
                    add(href, source, "internal_link", "medium")
                elif not parsed.scheme and not href.startswith(("#", "?")):
                    resolved_href = posixpath.join(relative.parent.as_posix(), unquote(parsed.path))
                    normalized = _normalize_route_path("/" + resolved_href, root)
                    if normalized:
                        add(normalized, source, "internal_link", "low")
    return sorted((dict({key: value for key, value in item.items() if not key.startswith("_")}, methods=sorted(item["methods"])) for item in routes.values()), key=lambda item: (item["path"].count("/"), item["path"], item["source"]))


def _normalize_route_path(value: str, root: Path) -> str | None:
    """Resolve dot segments, reject paths that escape the project, and canonicalize static indexes."""
    decoded = unquote(value)
    if not decoded.startswith("/") or "\\" in decoded:
        return None
    segments: list[str] = []
    for segment in decoded.split("/"):
        if segment in {"", "."}:
            continue
        if segment == "..":
            if not segments:
                return None
            segments.pop()
        else:
            segments.append(segment)
    if segments and segments[-1].casefold() in {"index.html", "index.htm"}:
        segments.pop()
        if not segments:
            return "/"
        return "/" + "/".join(segments) + "/"
    normalized = "/" + "/".join(segments)
    if normalized == "/":
        return normalized
    target = root.joinpath(*segments)
    if target.is_dir() and (target / "index.html").is_file():
        return normalized.rstrip("/") + "/"
    if decoded.endswith("/"):
        return normalized.rstrip("/") + "/"
    return normalized


def _discover_components(root: Path, source_files: list[Path], contents: dict[str, str], routes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    route_files = {item["source"] for item in routes}
    component_paths: dict[str, dict[str, Any]] = {}
    for path in source_files:
        relative = path.relative_to(root).as_posix()
        if path.suffix.casefold() not in {".js", ".jsx", ".ts", ".tsx", ".vue", ".svelte", ".astro"}:
            continue
        text = contents.get(relative, "")
        stem = path.stem
        is_named_component = bool(re.search(r"\b(?:export\s+default\s+)?(?:function|class)\s+[A-Z][\w$]*|\bexport\s+(?:default\s+)?const\s+[A-Z][\w$]*|<[A-Z][\w.]*\b", text))
        in_component_directory = any(part.casefold() in {"components", "component", "widgets", "ui"} for part in path.parts[:-1])
        is_page = path.name.casefold() in {"page.tsx", "page.jsx", "page.js", "page.vue", "page.svelte", "index.html"} or relative in route_files
        if is_page or not (is_named_component or in_component_directory):
            continue
        exports = sorted(set(EXPORT_NAME.findall(text) + FUNCTION_NAME.findall(text)))
        imports = []
        for module in IMPORT_SPECIFIER.findall(text):
            if not module.startswith("."):
                continue
            resolved = _resolve_import(path, module, root)
            if resolved:
                imports.append(resolved.relative_to(root).as_posix())
        name = exports[0] if exports else re.sub(r"[-_]+", " ", stem).title()
        signature, source_lines = _component_signature(text, name)
        component_paths[relative] = {
            "name": name,
            "source": relative,
            "line_count": len(text.splitlines()),
            "exports": exports,
            "signature": signature,
            "source_lines": source_lines,
            "local_imports": sorted(set(imports)),
            "routes": [],
            "classification": _classify_component(name, relative),
            "confidence": "high" if exports else "medium",
        }
    return sorted(component_paths.values(), key=lambda item: (item["classification"], item["name"].casefold(), item["source"]))


def _discover_html_components(root: Path, source_files: list[Path], contents: dict[str, str]) -> list[dict[str, Any]]:
    """Profile semantic HTML structures and repeated class-based patterns by source line."""
    profiles: list[dict[str, Any]] = []
    important_tags = {"header", "nav", "main", "aside", "footer", "form", "dialog", "button", "table", "section", "article"}

    class ElementParser(HTMLParser):
        def __init__(self) -> None:
            super().__init__(convert_charrefs=True)
            self.counts: Counter[tuple[str, str, str]] = Counter()
            self.lines: dict[tuple[str, str, str], list[int]] = {}

        def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
            attributes = dict(attrs)
            classes = " ".join(sorted(set((attributes.get("class") or "").split())))
            role = attributes.get("role") or ""
            if tag not in important_tags and not classes and not role:
                return
            key = (tag, classes, role)
            self.counts[key] += 1
            self.lines.setdefault(key, []).append(self.getpos()[0])

    for path in source_files:
        if path.suffix.casefold() != ".html":
            continue
        relative = path.relative_to(root).as_posix()
        parser = ElementParser()
        try:
            parser.feed(contents.get(relative, ""))
        except Exception:
            continue
        for (tag, classes, role), count in parser.counts.most_common(80):
            label = classes or role or tag
            profiles.append({
                "name": label.replace(" ", "."),
                "source": relative,
                "line_count": len(contents.get(relative, "").splitlines()),
                "exports": [],
                "local_imports": [],
                "routes": [],
                "classification": _classify_component(label, tag),
                "confidence": "high",
                "element": tag,
                "role": role or None,
                "occurrence_count": count,
                "source_lines": parser.lines[(tag, classes, role)],
                "evidence_kind": "static_html_structure",
            })
    return profiles


def _resolve_import(source: Path, module: str, root: Path) -> Path | None:
    target = (source.parent / module).resolve()
    if not target.is_relative_to(root):
        return None
    candidates = [target, *(target.with_suffix(suffix) for suffix in SOURCE_SUFFIXES), *(target / f"index{suffix}" for suffix in SOURCE_SUFFIXES)]
    for candidate in candidates:
        if candidate.is_file() and not candidate.is_symlink():
            return candidate
    return None


def _discover_design_system(root: Path, style_files: list[Path]) -> dict[str, Any]:
    color_counts: Counter[str] = Counter()
    color_files: dict[str, set[str]] = {}
    token_values: dict[tuple[str, str, str], int] = Counter()
    all_tokens: dict[tuple[str, str, str], int] = Counter()
    font_counts: Counter[str] = Counter()
    font_files: dict[str, set[str]] = {}
    font_sizes: set[str] = set()
    line_heights: set[str] = set()
    dimensions: Counter[str] = Counter()
    breakpoints: set[str] = set()
    for path in style_files:
        relative = path.relative_to(root).as_posix()
        text = _read_text(path)
        for match in CSS_VARIABLE.finditer(text):
            name, value = match.group(1).strip(), match.group(2).strip()
            all_tokens[(name, value, relative)] += 1
            if COLOR_VALUE.search(value) or name.casefold().startswith(("color", "bg", "surface", "border", "text")):
                token_values[(name, value, relative)] += 1
        for block in re.finditer(r"(?is)(?:^|[;{}])\s*(?:color|background(?:-color)?|border(?:-[\w-]+)?-color|outline-color|fill|stroke)\s*:\s*([^;{}]+)", text):
            for match in COLOR_VALUE.finditer(block.group(1)):
                color = match.group(1).strip().lower()
                color_counts[color] += 1
                color_files.setdefault(color, set()).add(relative)
        for match in FONT_FAMILY.finditer(text):
            family = " ".join(match.group(1).strip().split())
            font_counts[family] += 1
            font_files.setdefault(family, set()).add(relative)
        font_sizes.update(" ".join(item.strip().split()) for item in FONT_SIZE.findall(text))
        line_heights.update(" ".join(item.strip().split()) for item in LINE_HEIGHT.findall(text))
        dimensions.update(match.group(0).lower() for match in DIMENSION_VALUE.finditer(text))
        for media in re.finditer(r"(?is)@media\s*\(([^)]*)\)", text):
            for width in re.finditer(r"(?i)(?:min|max)-width\s*:\s*([^\s)]+)", media.group(1)):
                breakpoints.add(width.group(1))
    return {
        "stylesheet_files": [path.relative_to(root).as_posix() for path in style_files],
        "colors": [{"value": value, "count": count, "files": sorted(color_files[value])} for value, count in sorted(color_counts.items(), key=lambda item: (-item[1], item[0]))],
        "color_tokens": [{"name": name, "value": value, "file": file} for (name, value, file), _ in sorted(token_values.items())],
        "custom_properties": [{"name": name, "value": value, "file": file, "occurrences": count} for (name, value, file), count in sorted(all_tokens.items())],
        "font_families": [{"value": value, "count": count, "files": sorted(font_files[value])} for value, count in sorted(font_counts.items(), key=lambda item: (-item[1], item[0].casefold()))],
        "font_sizes": sorted(font_sizes),
        "line_heights": sorted(line_heights),
        "repeated_dimensions": [[value, count] for value, count in dimensions.most_common() if count >= 2],
        "breakpoints": sorted(breakpoints),
    }


def _architecture_groups(root: Path, files: list[Path]) -> dict[str, list[str]]:
    groups: dict[str, set[str]] = {
        "application_entry_and_routes": set(), "layouts_and_features": set(), "shared_components": set(),
        "hooks_and_composables": set(), "services_and_api_clients": set(), "state_and_models": set(),
        "styles_and_themes": set(), "tests_and_story_catalogs": set(), "configuration_and_manifests": set(),
    }
    route_markers = {"app", "pages", "routes", "router"}
    for path in files:
        relative = path.relative_to(root)
        name = path.name.casefold()
        parts = {part.casefold() for part in relative.parts[:-1]}
        value = relative.as_posix()
        if name in {"package.json", "pyproject.toml", "vite.config.js", "vite.config.ts", "next.config.js", "next.config.ts", "next.config.mjs", "angular.json", "astro.config.mjs", "svelte.config.js"}:
            groups["configuration_and_manifests"].add(value)
        if path.suffix.casefold() in SOURCE_SUFFIXES and (parts & route_markers or path.suffix.casefold() == ".html" or name in {"main.ts", "main.js", "main.mjs", "main.tsx", "index.ts", "index.js", "index.mjs", "index.tsx", "app.js", "app.mjs", "app.tsx", "app.vue"}):
            groups["application_entry_and_routes"].add(value)
        if parts & {"layout", "layouts", "features", "modules"} or name in {"layout.tsx", "layout.vue", "layout.svelte"}:
            groups["layouts_and_features"].add(value)
        component_filename = path.stem.casefold() in {"component", "components"}
        if parts & {"components", "component", "widgets", "ui"} or name.startswith(("component.", "components.")) or component_filename:
            groups["shared_components"].add(value)
        if parts & {"hooks", "composables"}:
            groups["hooks_and_composables"].add(value)
        if parts & {"services", "api", "clients", "repositories"} or any(term in name for term in ("api-client", "service")):
            groups["services_and_api_clients"].add(value)
        if parts & {"store", "stores", "state", "models", "model", "types", "data"} or name.startswith(("data.", "model.")):
            groups["state_and_models"].add(value)
        if path.suffix.casefold() in STYLE_SUFFIXES or "theme" in name or "token" in name:
            groups["styles_and_themes"].add(value)
        if parts & {"test", "tests", "__tests__", "stories", "storybook"} or name.endswith((".test.tsx", ".spec.tsx", ".stories.tsx")):
            groups["tests_and_story_catalogs"].add(value)
    return {key: sorted(values) for key, values in groups.items()}


def _dynamic_segment(value: str) -> str:
    if (value.startswith("[") and value.endswith("]")) or (value.startswith(":") and len(value) > 1):
        return ":" + value.strip("[]:")
    return value


def _classify_route(route: str, source: Path) -> str:
    name = source.stem.casefold()
    if "settings" in route.casefold() or "settings" in name:
        return "settings screen"
    if any(term in route.casefold() for term in ("search", "query")):
        return "search screen"
    if any(term in route.casefold() for term in ("login", "signin", "auth")):
        return "authentication screen"
    if route == "/":
        return "home or overview screen"
    if ":" in route:
        return "dynamic detail route pattern"
    return "page"


def _classify_component(name: str, path: str) -> str:
    value = (name + " " + path).casefold()
    for category, terms in (
        ("navigation", ("nav", "sidebar", "menu", "breadcrumb", "header")),
        ("form control", ("input", "select", "field", "form", "button", "checkbox", "switch", "slider")),
        ("overlay or feedback", ("modal", "dialog", "toast", "alert", "tooltip", "popover")),
        ("data display", ("table", "chart", "list", "card", "badge", "stat")),
        ("layout", ("layout", "shell", "container", "panel")),
    ):
        if any(term in value for term in terms):
            return category
    return "shared or feature component"


def _component_signature(source: str, name: str) -> tuple[str, list[int]]:
    escaped = re.escape(name)
    candidates = (
        re.compile(rf"\b(?:function|class)\s+{escaped}\s*\(([^)]*)\)"),
        re.compile(rf"\b{escaped}\s*=\s*\(([^)]*)\)\s*=>"),
        re.compile(rf"\b{escaped}\s*=\s*\(([^)]*)\)\s*:")
    )
    for candidate in candidates:
        match = candidate.search(source)
        if match:
            return " ".join(match.group(0).split())[:240], [source.count("\n", 0, match.start()) + 1]
    return "", []


def _markdown_bytes(lines: list[str]) -> bytes:
    return ("\n".join(lines).rstrip() + "\n").encode("utf-8")


def contrast_ratio(foreground: str, background: str) -> float | None:
    """Calculate WCAG contrast for two opaque sRGB colors; reject ambiguous values."""
    fg = _opaque_rgb(foreground)
    bg = _opaque_rgb(background)
    if fg is None or bg is None:
        return None

    def luminance(rgb: tuple[float, float, float]) -> float:
        return sum(weight * _linear(channel) for weight, channel in zip((0.2126, 0.7152, 0.0722), rgb))

    light, dark = sorted((luminance(fg), luminance(bg)), reverse=True)
    return round((light + 0.05) / (dark + 0.05), 2)


def _contrast_samples(styles: dict[str, Any]) -> list[dict[str, Any]]:
    results = []
    for selector, style in styles.items():
        if not isinstance(style, dict) or style.get("backgroundImage") not in {None, "none"}:
            continue
        foreground = style.get("color")
        background = style.get("backgroundColor")
        ratio = contrast_ratio(str(foreground or ""), str(background or ""))
        if ratio is None:
            continue
        size = _font_size_px(style.get("fontSize"))
        try:
            weight = int(style.get("fontWeight", 400))
        except (TypeError, ValueError):
            weight = 400
        threshold = 3.0 if size >= 24 or (size >= 18.66 and weight >= 700) else 4.5
        results.append({
            "selector": selector,
            "foreground": foreground,
            "background": background,
            "ratio": ratio,
            "threshold": threshold,
            "classification": "meets sampled threshold" if ratio >= threshold else "below sampled threshold",
            "basis": "computed opaque foreground/background pair; images, transparency, and inherited compositing excluded",
        })
    return results


def _opaque_rgb(value: str) -> tuple[float, float, float] | None:
    value = value.strip().casefold()
    if value in {"transparent", "none", "currentcolor"}:
        return None
    if value.startswith("#"):
        digits = value[1:]
        if len(digits) in {3, 4}:
            digits = "".join(character * 2 for character in digits)
        if len(digits) not in {6, 8}:
            return None
        try:
            channels = [int(digits[index : index + 2], 16) for index in (0, 2, 4)]
            if len(digits) == 8 and int(digits[6:8], 16) != 255:
                return None
            return channels[0] / 255, channels[1] / 255, channels[2] / 255
        except ValueError:
            return None
    match = re.fullmatch(r"rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)(?:\s*[,/]\s*([\d.]+%?))?\s*\)", value)
    if not match:
        return None
    channels = [float(match.group(index)) for index in (1, 2, 3)]
    alpha = match.group(4)
    if alpha and alpha not in {"1", "100%"}:
        return None
    if any(channel < 0 or channel > 255 for channel in channels):
        return None
    return channels[0] / 255, channels[1] / 255, channels[2] / 255


def _linear(channel: float) -> float:
    return channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4


def _font_size_px(value: Any) -> float:
    match = re.match(r"^[\d.]+", str(value or ""))
    return float(match.group()) if match else 0.0


def _finding_id(audit_type: str, category: str, title: str) -> str:
    prefix = {"technical": "TECH", "behavioral": "BEH", "visual": "VIS"}[audit_type]
    digest = hashlib.sha256(f"{category.casefold()} {title.casefold()}".encode("utf-8")).hexdigest()[:8].upper()
    return f"{prefix}-{digest}"
