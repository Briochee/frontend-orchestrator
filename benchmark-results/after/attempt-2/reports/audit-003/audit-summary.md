# Frontend audit summary

Project: `northstar-ops-audit-fixture`
Framework signals: Static HTML/CSS/JavaScript (detected from files)
Audit mode: `codex_cli_plus_static`

Audit completion status: **incomplete**

## Scope and evidence

Inspected 16 repository files; 7 frontend source files and 1 stylesheets were detected.
The source audit did not execute project code, install dependencies, or run scripts.

## Findings by area

- Technical and architecture: 1
- Behavior and accessibility: 0
- Visual design: 0

## Highest-priority findings

- **MEDIUM · TECH-45E0725A — User-controlled content reaches an HTML rendering sink.** Markup supplied through the editable value can be parsed as HTML in the current page context.

## Visual audit status

Rendered screenshots are registered as evidence. Any appearance conclusions are limited to those rendered views and states.

## Inspection coverage

- Source files profiled: 13
- Route candidates: 5
- Routes rendered: 5
- Component profiles: 228
- Screenshots captured / attached / interpreted / validated: 20 / 0 / False / False
- Viewports: desktop, mobile, tablet
- Application controls activated: none; one passive keyboard Tab focus state may be captured per route.

## Limitations

- Audit status is incomplete. 6 requested route/viewport pair(s) lack a valid screenshot: /analytics/ / mobile, /analytics/ / tablet, /orders/ / mobile, /orders/ / tablet, /settings/ / mobile, /settings/ / tablet. Required specialist `frontend_code_auditor` did not complete both structured passes. Required specialist `frontend_ux_auditor` did not complete both structured passes. Required specialist `frontend_visual_auditor` did not complete both structured passes. No screenshot-backed visual analysis passed evidence validation.
- Review partial findings, correct the listed evidence or backend gaps, then retry with: frontend-director audit --project /private/tmp/frontend-director-benchmark-20261114/demo-app --url http://127.0.0.1:8765/ --depth deep --codex
- No project scripts, builds, dependency lifecycle hooks, or development servers were executed.
- No runtime, bundle-size, Web Vitals, network, or interaction measurements were collected.
- Source inspection cannot establish behavior on authenticated routes or runtime states.
- Screenshots were captured, but no visual evaluator was run; appearance findings remain unavailable.
- frontend_code_auditor did not return a valid structured result: BackendFailure: Codex exited with status 1: Error: turn/start: turn/start failed: Input exceeds the maximum length of 1048576 characters. (code -32602), data: {"input_error_code":"input_too_large","max_chars":1048576
- frontend_ux_auditor did not return a valid structured result: BackendFailure: Codex exited with status 1: Error: turn/start: turn/start failed: Input exceeds the maximum length of 1048576 characters. (code -32602), data: {"input_error_code":"input_too_large","max_chars":1048576
- frontend_visual_auditor did not return a valid structured result: BackendFailure: Codex exited with status 1: Error: turn/start: turn/start failed: Input exceeds the maximum length of 1048576 characters. (code -32602), data: {"input_error_code":"input_too_large","max_chars":1048576

## Recommended next steps

1. Capture desktop (1440 px), tablet (768 px), and mobile (390 px) browser evidence for the routes in the approved audit scope.
2. Review findings against the rendered experience and the project's own interaction constraints before prioritizing changes.

Technical defects, behavior changes, and subjective design recommendations remain separate. No design or implementation approval is implied by this report.
