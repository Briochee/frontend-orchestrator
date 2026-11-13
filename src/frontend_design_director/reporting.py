"""Human-readable audit, implementation, and verification reports."""

from __future__ import annotations

import json
from collections import Counter
from typing import Any

from .auditing import AuditResult
from .models import AuditType, Finding


def audit_reports(findings: list[Finding], result: AuditResult, discovery: dict[str, Any], intelligence: dict[str, Any] | None = None) -> dict[str, bytes]:
    """Render independent technical, behavioral, and visual reports plus a detailed summary."""
    technical = [item for item in findings if item.audit_type == AuditType.TECHNICAL]
    behavioral = [item for item in findings if item.audit_type == AuditType.BEHAVIORAL]
    visual = [item for item in findings if item.audit_type == AuditType.VISUAL]
    visual_evidence = [item for item in result.screenshots if item.get("evidence_type") == "rendered_browser_screenshot"]
    limitations = list(result.limitations)
    if not visual_evidence and not any("No rendered" in item for item in limitations):
        limitations.append("No rendered screenshots or equivalent browser evidence were available. The visual audit makes no claims about the application's appearance.")
    technical_md = _finding_report("Technical and architecture audit", technical, result, include_visual=False)
    behavioral_md = _finding_report("Behavior and accessibility audit", behavioral, result, include_visual=False)
    visual_md = _visual_report(visual, visual_evidence, limitations, intelligence, result.visual_analysis)
    summary_md = _summary_report(findings, discovery, result, limitations, intelligence)
    findings_json = json.dumps({"schema_version": 1, "findings": [item.to_dict() for item in findings], "evidence": list(result.screenshots), "coverage": intelligence.get("coverage", {}) if intelligence else {}, "limitations": limitations}, indent=2, sort_keys=True).encode()
    reports = {
        "technical-audit.md": technical_md.encode(),
        "behavioral-audit.md": behavioral_md.encode(),
        "visual-audit.md": visual_md.encode(),
        "audit-summary.md": summary_md.encode(),
        "findings.json": findings_json,
    }
    if intelligence:
        reports.update(_supplemental_reports(findings, result, discovery, intelligence, limitations))
    return reports


def _finding_report(title: str, findings: list[Finding], result: AuditResult, *, include_visual: bool) -> str:
    lines = [f"# {title}", "", f"Audit backend: `{result.backend_used}`", "", "## Findings", ""]
    if findings:
        for finding in findings:
            lines.extend(_finding_lines(finding))
    else:
        lines.append("No findings were produced for this audit type. This is not a guarantee that the area is defect-free.")
    lines.extend(["", "## Evidence and limitations", ""])
    lines.extend(f"- {item}" for item in result.limitations)
    if result.recommendations:
        lines.extend(["", "## Suggested next steps", ""])
        lines.extend(f"- {item}" for item in result.recommendations)
    return "\n".join(lines).rstrip() + "\n"


def _visual_report(findings: list[Finding], screenshots: list[dict[str, Any]], limitations: list[str], intelligence: dict[str, Any] | None = None, visual_analysis: dict[str, Any] | None = None) -> str:
    lines = ["# Visual design audit", ""]
    if screenshots:
        lines.extend(["## Rendered evidence", "", "The following browser screenshots were captured from the explicitly supplied URL. Only routes and states present in these images were evaluated.", ""])
        lines.extend(f"- `{item.get('route', '/')}` / `{item['viewport']}` {item['width']}×{item['height']}: `{item['path']}` (HTTP {item.get('http_status') or 'unknown'})" for item in screenshots)
    else:
        lines.extend(["## Rendered evidence", "", "**Visual appearance was not audited.** No rendered screenshots or equivalent evidence were available. Source and CSS definitions are not used to invent claims about the rendered interface."])
    lines.extend(["", "## Design identity", ""])
    if findings:
        lines.append("Design observations below are limited to the attached rendered evidence. Source-defined design tokens are documented separately and are not treated as proof of rendered use.")
    else:
        lines.append("Not assessed by a visual reasoning backend. Screenshots, if listed above, are evidence for human review but are not automatically interpreted as design findings.")
    analysis = visual_analysis or {}
    if analysis:
        lines.extend(["", f"### Design identity", "", analysis["design_identity"], ""])
        lines.extend(_visual_observation_line(item) for item in analysis["design_identity_evidence"])
        lines.extend(["", "### Experience character", "", analysis["experience_character"], ""])
        for heading, key in (("Observed strengths", "strengths"), ("Observed concerns", "concerns"), ("Cross-screen consistency patterns", "consistency_patterns"), ("Patterns to preserve", "preserve"), ("Refinements supported by the evidence", "refine"), ("Options requiring human approval", "reconsider_with_human_approval")):
            lines.extend([f"### {heading}", ""])
            lines.extend(_visual_observation_line(item) for item in analysis[key])
            if not analysis[key]:
                lines.append("No screenshot-backed observations were returned for this category.")
            lines.append("")
        if analysis["route_assessments"]:
            lines.extend(["### Route and viewport reading", "", "| Route | Viewport | Hierarchy | Density | Responsive observation | Evidence |", "|---|---|---|---|---|---|"])
            for item in analysis["route_assessments"]:
                cells = [item[key].replace("|", "\\|").replace("\n", " ") for key in ("route", "viewport", "hierarchy", "density", "responsive_notes", "screenshot_reference")]
                lines.append("| " + " | ".join(f"`{cell}`" if index in {0, 1, 5} else cell for index, cell in enumerate(cells)) + " |")
        lines.extend(["", "Visual analysis limitations:", ""])
        lines.extend(f"- {item}" for item in analysis["limitations"])
    elif screenshots:
        lines.extend(["", "No screenshot interpretation was returned. The images remain available for human review; their content is not summarized by deterministic source analysis."])
    if intelligence:
        coverage = intelligence.get("coverage", {})
        lines.extend(["", "## Route and viewport coverage", "", f"- Source route candidates: {coverage.get('routes_discovered', 0)}", f"- Routes rendered: {coverage.get('routes_rendered', 0)}", f"- Screenshots: {coverage.get('screenshots_captured', 0)}", f"- Rendered viewports: {', '.join(coverage.get('rendered_viewports', [])) or 'none'}"])
    lines.extend(["", "## Findings", ""])
    if findings:
        for finding in findings:
            lines.extend(_finding_lines(finding))
    elif screenshots:
        lines.append("No visual findings were produced. This does not establish that the views are free of visual or accessibility issues.")
    else:
        lines.append("None. Visual findings require rendered evidence and a visual evaluator.")
    lines.extend(["", "## Evidence gaps", ""])
    if screenshots:
        lines.append("- One non-activating Tab focus state is captured per route at desktop when available. Full keyboard order, hover, active, disabled, loading, empty, and error states were not exhaustively captured.")
        lines.append("- Light and dark themes were not compared unless screenshots cover both themes.")
        if intelligence:
            console_count = sum(len(item.get("console_errors", [])) + len(item.get("page_errors", [])) for item in intelligence.get("runtime", []))
            lines.append(f"- Browser runtime captured {console_count} console/page error(s); see `runtime-evidence.md` for route and viewport details.")
    lines.extend(f"- {item}" for item in limitations)
    return "\n".join(lines).rstrip() + "\n"


def _visual_observation_line(item: dict[str, Any]) -> str:
    return f"- {item['claim']} — `{item['route']}` / `{item['viewport']}` (`{item['screenshot_reference']}`)."


def _supplemental_reports(
    findings: list[Finding],
    result: AuditResult,
    discovery: dict[str, Any],
    intelligence: dict[str, Any],
    limitations: list[str],
) -> dict[str, bytes]:
    """Create deeper reports from collected evidence without presenting gaps as passes."""
    project = intelligence["project"]
    design = intelligence["design_system"]
    runtime = intelligence["runtime"]
    focus_captures = sum(item.get("interaction_state") == "keyboard_focus_after_one_tab" for item in runtime)
    coverage = intelligence["coverage"]
    counts = Counter(item.audit_type.value for item in findings)
    top_findings = sorted((item for item in findings if item.severity.value in {"critical", "high", "medium"}), key=lambda item: ({"critical": 0, "high": 1, "medium": 2}[item.severity.value], item.id))[:8]

    executive = ["# Executive summary", "", f"Project: `{project['name']}`", f"Description: {project.get('description') or 'Not documented in inspected project metadata.'}", f"Framework signals: {', '.join(project.get('frameworks', [])) or 'not detected'}", "", f"The audit contains {counts.get('technical', 0)} technical, {counts.get('behavioral', 0)} behavioral, and {counts.get('visual', 0)} visual finding(s).", "", "## Coverage", "", f"- Source/style files: {coverage['source_files_inspected']}", f"- Route candidates: {coverage['routes_discovered']}", f"- Routes rendered: {coverage['routes_rendered']}", f"- Screenshots: {coverage['screenshots_captured']}", f"- Browser navigation failures: {coverage.get('browser_navigation_failures', 0)}", f"- Component profiles: {coverage['component_profiles']}", f"- Analysis backend: `{result.backend_used}`; requested profile `{intelligence.get('audit_depth', 'see audit summary')}`", "", "## Highest-priority findings", ""]
    executive.extend(f"- **{item.severity.value.upper()} · {item.id}: {item.title}.** {item.impact}" for item in top_findings)
    if not top_findings:
        executive.append("No medium-or-higher findings were produced. This is not a defect-free guarantee.")
    executive.extend(["", "## Visual design identity", "", result.visual_analysis.get("design_identity", "Not interpreted by a screenshot-capable visual reasoning pass."), "", "## Important coverage limits", "", *[f"- {item}" for item in limitations], "", "Human decisions about design, behavior, and implementation remain pending at their existing approval gates."])

    color = ["# Color-system analysis", "", "Source declarations are distinguished from actual computed browser samples. Contrast is calculated only for opaque foreground/background pairs with an unambiguous computed background; it is not a complete WCAG audit.", "", "## Source color palette", "", "| Color | Declarations | Source files |", "|---|---:|---|"]
    color.extend(f"| `{item['value']}` | {item['count']} | {', '.join(f'`{path}`' for path in item['files'])} |" for item in design["colors"])
    if not design["colors"]:
        color.append("| No explicit CSS color literals found | 0 | — |")
    color.extend(["", "## Color tokens", "", "| Token | Value | File |", "|---|---|---|"])
    color.extend(f"| `--{item['name']}` | `{item['value']}` | `{item['file']}` |" for item in design["color_tokens"])
    color.extend(["", "## Rendered contrast samples", ""])
    contrast_samples = [(screen, sample) for screen in runtime for sample in screen.get("contrast_samples", [])]
    if contrast_samples:
        color.extend(["| Route / viewport | Selector | Foreground / background | Ratio | Sampled threshold |", "|---|---|---|---:|---:|"])
        color.extend(f"| `{screen['route']}` / `{screen['viewport']}` | `{sample['selector']}` | `{sample['foreground']}` / `{sample['background']}` | {sample['ratio']}:1 | {sample['threshold']}:1 ({sample['classification']}) |" for screen, sample in contrast_samples)
    else:
        color.append("No reliable computed opaque foreground/background pairs were collected. Contrast remains unverified.")

    typography = ["# Typography analysis", "", "## Source-defined families", ""]
    typography.extend(f"- `{item['value']}` — {item['count']} declaration(s) in {', '.join(f'`{path}`' for path in item['files'])}" for item in design["font_families"])
    if not design["font_families"]:
        typography.append("No font-family declarations were found in inspected stylesheets.")
    typography.extend(["", f"Source font-size values: {', '.join(f'`{item}`' for item in design['font_sizes']) or 'none detected'}", "", f"Source line-height values: {', '.join(f'`{item}`' for item in design['line_heights']) or 'none detected'}", "", "## Runtime samples", ""])
    if runtime:
        typography.extend(f"- `{screen['route']}` / `{screen['viewport']}`: {', '.join(f'`{selector}` {style.get("fontFamily", "unknown")} at {style.get("fontSize", "unknown")} / {style.get("lineHeight", "unknown")}' for selector, style in screen.get('computed_styles', {}).items() if style.get('fontFamily'))}." for screen in runtime)
    else:
        typography.append("No browser-computed typography samples were collected; actual font loading and rendered typography are unverified.")

    layout = ["# Layout and density analysis", "", "## Repeated source dimensions", ""]
    layout.extend(f"- `{value}` appears {count} times in inspected CSS declarations." for value, count in design["repeated_dimensions"][:120])
    if not design["repeated_dimensions"]:
        layout.append("No repeated dimensional values were identified in inspected stylesheets.")
    layout.extend(["", "## Breakpoint declarations", "", f"Observed media-query widths: {', '.join(f'`{item}`' for item in design['breakpoints']) or 'none identified'}", "", "## Captured layout dimensions", ""])
    if runtime:
        layout.extend(f"- `{screen['route']}` / `{screen['viewport']}`: document {screen.get('document', {}).get('width', 'unknown')} × {screen.get('document', {}).get('height', 'unknown')} CSS pixels; viewport width {screen.get('width', 'unknown')} px." for screen in runtime)
    else:
        layout.append("No rendered dimensions were collected. Composition and congestion were not visually assessed.")
    layout.extend(["", "Visual density and congestion require a screenshot interpretation; this inventory does not infer them from CSS values alone."])

    responsive = ["# Responsive design analysis", "", f"Audit profile: `{intelligence.get('audit_depth', 'unknown')}`", "", "| Route | Viewport | Document width | Viewport width | Overflow signal | Screenshot |", "|---|---|---:|---:|---|---|"]
    if runtime:
        responsive.extend(f"| `{screen['route']}` | {screen['viewport']} | {screen.get('document', {}).get('width', 'unknown')} | {screen.get('width', 'unknown')} | {'possible horizontal overflow' if isinstance(screen.get('document', {}).get('width'), int) and isinstance(screen.get('width'), int) and screen['document']['width'] > screen['width'] else 'none detected at document width'} | `{screen['screenshot']}` |" for screen in runtime)
    else:
        responsive.append("| No routes rendered | — | — | — | Not verified | — |")
    route_policy = intelligence.get("capture_route_policy", "not_rendered")
    if route_policy == "operator_selected":
        responsive_note = "The operator limited browser capture to the explicitly selected exact paths plus the supplied base URL."
    elif route_policy == "all_static_candidates":
        responsive_note = "Browser capture targeted source-discovered static route candidates plus the supplied base URL."
    else:
        responsive_note = "No browser routes were rendered during this audit."
    responsive.extend(["", responsive_note, "Dynamic route patterns are never synthesized. Captures do not exercise hover, dialogs, loading/error states, or themes automatically; one passive desktop Tab focus state may be recorded when available."])

    behavior_findings = [item for item in findings if item.audit_type == AuditType.BEHAVIORAL]
    interactions = _finding_report("Interaction and behavior audit", behavior_findings, result, include_visual=False)
    interactions = interactions.rstrip() + "\n\n## Runtime action coverage\n\nBrowser collection inspected structural controls and accessible-name signals. It captured one passive Tab focus state per route at desktop when a focusable target was available; it did not activate application controls, submit forms, or claim workflow outcomes. Review source-derived journeys above; unexecuted behavior remains unverified.\n"

    accessibility = ["# Accessibility audit", "", "Not a WCAG conformance certificate; this is a partial code and browser evidence review.", "", "## Findings", ""]
    accessibility_findings = [item for item in behavior_findings if item.category.casefold() in {"accessibility", "form_labels", "keyboard", "contrast", "landmarks", "focus"}]
    for item in accessibility_findings:
        accessibility.extend(_finding_lines(item))
    if not accessibility_findings:
        accessibility.append("No accessibility-specific finding was produced; this does not establish conformance.")
    accessibility.extend(["", "## Rendered label and contrast evidence", ""])
    for screen in runtime:
        controls = screen.get("controls", {})
        focus = screen.get("focus_target", {})
        state = f" Keyboard focus landed on `{focus.get('tag', 'unknown')}` (role `{focus.get('role') or 'none'}`); outline {focus.get('outlineStyle', 'unknown')} {focus.get('outlineWidth', 'unknown')}." if screen.get("interaction_state") == "keyboard_focus_after_one_tab" else ""
        accessibility.append(f"- `{screen['route']}` / `{screen['viewport']}`: {controls.get('inputs', 0)} inputs; {controls.get('inputs_without_associated_label', 0)} without an associated label/ARIA name in the captured DOM.{state}")
        for sample in screen.get("contrast_samples", []):
            accessibility.append(f"  - `{sample['selector']}` computed opaque pair is {sample['ratio']}:1 (sample threshold {sample['threshold']}:1).")
    if not runtime:
        accessibility.append("No browser accessibility observations were collected.")
    accessibility.extend(["", "Keyboard order, assistive-technology output, zoom/reflow, and stateful announcements were not fully verified by this browser pass."])

    performance = ["# Performance audit", "", "Navigation timing values below are single-run browser laboratory observations. They are not field Core Web Vitals and are not comparable across different browsers, networks, routes, cache states, or machine load.", "", "| Route | Viewport | Response (ms) | DOM content loaded (ms) | Load event (ms) | Transfer size (bytes) |", "|---|---|---:|---:|---:|---:|"]
    default_runtime = [screen for screen in runtime if screen.get("interaction_state", "default") == "default"]
    if default_runtime:
        performance.extend(f"| `{screen['route']}` | {screen['viewport']} | {screen.get('navigation_timing', {}).get('responseMs', 'unknown')} | {screen.get('navigation_timing', {}).get('domContentLoadedMs', 'unknown')} | {screen.get('navigation_timing', {}).get('loadMs', 'unknown')} | {screen.get('navigation_timing', {}).get('transferSizeBytes', 'unknown')} |" for screen in default_runtime)
    else:
        performance.append("| No rendered route | — | — | — | — | — |")
    performance.extend(["", "LCP, INP, CLS, bundle analysis, long tasks, and comparative before/after measurements were not collected by this pass."])

    coverage_report = ["# Coverage and limitations", "", f"Requested depth: `{intelligence.get('audit_depth', 'unknown')}`", f"Backend: `{result.backend_used}`", "", f"- Source and style files: {coverage['source_files_inspected']}", f"- Route candidates discovered: {coverage['routes_discovered']}", f"- Routes rendered: {coverage['routes_rendered']}", f"- Screenshots: {coverage['screenshots_captured']}", f"- Browser navigation failures: {coverage.get('browser_navigation_failures', 0)}", f"- Component profiles: {coverage['component_profiles']}", f"- Viewports: {', '.join(coverage['rendered_viewports']) or 'none'}", f"- Passive keyboard focus screenshots: {focus_captures}", "- Browser controls activated: 0", "", "## Known limits", "", *[f"- {item}" for item in limitations]]
    names = ["executive-summary.md", "application-overview.md", "frontend-architecture-map.md", "route-and-screen-inventory.md", "component-inventory.md", "design-system-analysis.md", "color-system-analysis.md", "typography-analysis.md", "layout-and-density-analysis.md", "responsive-design-analysis.md", "interaction-behavior-audit.md", "accessibility-audit.md", "performance-audit.md", "visual-audit.md", "technical-audit.md", "behavioral-audit.md", "runtime-evidence.md", "coverage-and-limitations.md", "findings.json"]
    index = ["# Audit artifact index", "", "Each report is bounded by the recorded evidence and coverage. See coverage-and-limitations before interpreting an unverified area.", "", *[f"- [{name}]({name})" for name in names]]
    return {
        "executive-summary.md": ("\n".join(executive).rstrip() + "\n").encode(),
        "application-overview.md": _application_overview(project, discovery, intelligence),
        "color-system-analysis.md": ("\n".join(color).rstrip() + "\n").encode(),
        "typography-analysis.md": ("\n".join(typography).rstrip() + "\n").encode(),
        "layout-and-density-analysis.md": ("\n".join(layout).rstrip() + "\n").encode(),
        "responsive-design-analysis.md": ("\n".join(responsive).rstrip() + "\n").encode(),
        "interaction-behavior-audit.md": interactions.encode(),
        "accessibility-audit.md": ("\n".join(accessibility).rstrip() + "\n").encode(),
        "performance-audit.md": ("\n".join(performance).rstrip() + "\n").encode(),
        "coverage-and-limitations.md": ("\n".join(coverage_report).rstrip() + "\n").encode(),
        "audit-index.md": ("\n".join(index).rstrip() + "\n").encode(),
    }


def _application_overview(project: dict[str, Any], discovery: dict[str, Any], intelligence: dict[str, Any]) -> bytes:
    lines = ["# Application overview", "", f"Name: `{project['name']}`", f"Purpose: {project.get('description') or 'Not inferred from the available project description.'}", f"Framework signals: {', '.join(project.get('frameworks', [])) or 'not detected'}", f"Language signals: {', '.join(project.get('languages', [])) or 'not detected'}", "", "## User-facing route candidates", ""]
    lines.extend(f"- `{route['path']}` — {route['classification']} (from `{route['source']}`; methods: {', '.join(route['methods'])})." for route in intelligence["routes"])
    if not intelligence["routes"]:
        lines.append("No route candidates were identified from source conventions or local links.")
    lines.extend(["", "## Detected frontend infrastructure", "", f"- Build tools: {', '.join(project.get('build_tools', [])) or 'not detected'}", f"- Styling: {json.dumps(project.get('styling', {}), sort_keys=True)}", f"- Component libraries: {', '.join(project.get('component_libraries', [])) or 'not detected'}", f"- State/data libraries: {', '.join(project.get('state_management', [])) or 'not detected'}", f"- Test infrastructure: {', '.join(project.get('test_infrastructure', [])) or 'not detected'}", "", "The route list and infrastructure are repository-derived signals. They do not prove that a route is reachable or describe application intent beyond the recorded project description."])
    return ("\n".join(lines).rstrip() + "\n").encode()


def _summary_report(findings: list[Finding], discovery: dict[str, Any], result: AuditResult, limitations: list[str], intelligence: dict[str, Any] | None = None) -> str:
    counts = Counter(item.audit_type.value for item in findings)
    high_priority = sorted((item for item in findings if item.severity.value in {"critical", "high", "medium"}), key=lambda item: ({"critical": 0, "high": 1, "medium": 2}[item.severity.value], item.id))[:8]
    lines = [
        "# Frontend audit summary", "",
        f"Project: `{discovery.get('project_name', 'Unknown')}`", f"Framework signals: {', '.join(discovery.get('frameworks', [])) or 'not detected'}", f"Audit mode: `{result.backend_used}`", "",
        "## Scope and evidence", "",
        f"Inspected {discovery.get('file_count', 0)} repository files; {discovery.get('source_file_count', 0)} frontend source files and {discovery.get('css_file_count', 0)} stylesheets were detected.",
        "The source audit did not execute project code, install dependencies, or run scripts.", "",
        "## Findings by area", "",
        f"- Technical and architecture: {counts.get('technical', 0)}", f"- Behavior and accessibility: {counts.get('behavioral', 0)}", f"- Visual design: {counts.get('visual', 0)}", "",
        "## Highest-priority findings", "",
    ]
    if high_priority:
        for finding in high_priority:
            lines.append(f"- **{finding.severity.value.upper()} · {finding.id} — {finding.title}.** {finding.impact}")
    else:
        lines.append("No medium-or-higher findings were produced; this is not proof of defect-free behavior.")
    lines.extend(["", "## Visual audit status", ""])
    if any(item.get("evidence_type") == "rendered_browser_screenshot" for item in result.screenshots):
        lines.append("Rendered screenshots are registered as evidence. Any appearance conclusions are limited to those rendered views and states.")
    else:
        lines.append("Visual appearance was not audited because rendered screenshots were unavailable. See `visual-audit.md` for the evidence boundary.")
    if intelligence:
        coverage = intelligence.get("coverage", {})
        lines.extend(["", "## Inspection coverage", "", f"- Source files profiled: {coverage.get('source_files_inspected', 0)}", f"- Route candidates: {coverage.get('routes_discovered', 0)}", f"- Routes rendered: {coverage.get('routes_rendered', 0)}", f"- Component profiles: {coverage.get('component_profiles', 0)}", f"- Screenshots: {coverage.get('screenshots_captured', 0)}", f"- Viewports: {', '.join(coverage.get('rendered_viewports', [])) or 'none'}", "- Application controls activated: none; one passive keyboard Tab focus state may be captured per route."])
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in limitations)
    if result.recommendations:
        lines.extend(["", "## Recommended next steps", ""])
        lines.extend(f"{number}. {item}" for number, item in enumerate(result.recommendations, start=1))
    lines.extend(["", "Technical defects, behavior changes, and subjective design recommendations remain separate. No design or implementation approval is implied by this report."])
    return "\n".join(lines) + "\n"


def _finding_lines(finding: Finding) -> list[str]:
    lines = [
        f"### {finding.id} · {finding.title}", "",
        f"- Severity: **{finding.severity.value}**; confidence: **{finding.confidence.value}**; verification: `{finding.verification_status.value}`",
        f"- Category: `{finding.category}`", f"- Description: {finding.description}", f"- Impact: {finding.impact or 'Not specified.'}", f"- Recommendation: {finding.recommendation or 'No recommendation provided.'}",
    ]
    if finding.evidence:
        lines.append("- Evidence:")
        for item in finding.evidence:
            suffix = f":{item.line}" if item.line else ""
            viewport = f" ({item.viewport})" if item.viewport else ""
            lines.append(f"  - `{item.reference}{suffix}`{viewport} — {item.description}")
    lines.append("")
    return lines
