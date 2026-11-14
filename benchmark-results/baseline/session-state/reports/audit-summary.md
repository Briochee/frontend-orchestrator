# Frontend audit summary

Project: `northstar-ops-audit-fixture`
Framework signals: Static HTML/CSS/JavaScript (detected from files)
Audit mode: `codex_cli_plus_static`

## Scope and evidence

Inspected 16 repository files; 7 frontend source files and 1 stylesheets were detected.
The source audit did not execute project code, install dependencies, or run scripts.

## Findings by area

- Technical and architecture: 3
- Behavior and accessibility: 0
- Visual design: 0

## Highest-priority findings

- **MEDIUM · TECH-13ED89F2 — HTML injection sink requires data-flow review.** Unsanitized input can introduce script injection or markup integrity issues.
- **MEDIUM · TECH-B96A0E73 — HTML injection sink requires data-flow review.** Unsanitized input can introduce script injection or markup integrity issues.
- **MEDIUM · TECH-CC0A78BE — HTML injection sink requires data-flow review.** Unsanitized input can introduce script injection or markup integrity issues.

## Visual audit status

Visual appearance was not audited because rendered screenshots were unavailable. See `visual-audit.md` for the evidence boundary.

## Inspection coverage

- Source files profiled: 13
- Route candidates: 26
- Routes rendered: 0
- Component profiles: 228
- Screenshots: 0
- Viewports: none
- Application controls activated: none; one passive keyboard Tab focus state may be captured per route.

## Limitations

- No project scripts, builds, dependency lifecycle hooks, or development servers were executed.
- No runtime, bundle-size, Web Vitals, network, or interaction measurements were collected.
- Source inspection cannot establish behavior on authenticated routes or runtime states.
- No rendered screenshots or equivalent browser evidence were available. The visual audit makes no claims about the application's appearance.
- frontend_code_auditor did not return a valid structured result: BackendFailure: Codex exited with status 1: Return only JSON matching the supplied schema. Do not report visual appearance unless screenshot evidence is attached. ERROR: {"type":"error","error":{"message":"Invalid sc
- frontend_ux_auditor did not return a valid structured result: BackendFailure: Codex exited with status 1: Return only JSON matching the supplied schema. Do not report visual appearance unless screenshot evidence is attached. ERROR: {"type":"error","error":{"message":"Invalid sc
- The visual auditor was not invoked because no rendered screenshots were available.
- Browser evidence was unavailable: ValueError: Route must be an exact same-origin absolute path without query or traversal: '/analytics/../analytics'.

## Recommended next steps

1. Capture desktop (1440 px), tablet (768 px), and mobile (390 px) browser evidence for the routes in the approved audit scope.
2. Review findings against the rendered experience and the project's own interaction constraints before prioritizing changes.

Technical defects, behavior changes, and subjective design recommendations remain separate. No design or implementation approval is implied by this report.
