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

Visual appearance was not audited because rendered screenshots were unavailable. See `visual-audit.md` for the evidence boundary.

## Inspection coverage

- Source files profiled: 13
- Route candidates: 6
- Routes rendered: 0
- Component profiles: 228
- Screenshots captured / attached / interpreted / validated: 0 / 0 / False / False
- Viewports: none
- Application controls activated: none; one passive keyboard Tab focus state may be captured per route.

## Limitations

- Browser evidence was unavailable: NameError: name '_screenshot_integrity_error' is not defined
- Audit status is incomplete. 18 requested route/viewport pair(s) lack a valid screenshot: / / desktop, / / mobile, / / tablet, /analytics/ / desktop, /analytics/ / mobile, /analytics/ / tablet, /customers/ / desktop, /customers/ / mobile. Required specialist `frontend_visual_auditor` did not complete both structured passes. No screenshot-backed visual analysis passed evidence validation.
- Review partial findings, correct the listed evidence or backend gaps, then retry with: frontend-director audit --project /private/tmp/frontend-director-benchmark-20261114/demo-app --url http://127.0.0.1:8765/ --depth deep --codex
- No project scripts, builds, dependency lifecycle hooks, or development servers were executed.
- No runtime, bundle-size, Web Vitals, network, or interaction measurements were collected.
- Source inspection cannot establish behavior on authenticated routes or runtime states.
- No rendered screenshots or equivalent browser evidence were available. The visual audit makes no claims about the application's appearance.
- The supplied material contains a project evidence inventory and file paths, but not the contents of the listed source files. The requested source inspection and evidence-backed findings cannot be completed from file names and inventory metadata alone.
- No tools or commands were used, as instructed. No rendered evidence or measurements were supplied.
- No candidate technical findings were provided to cross-validate.
- The supplied material contains project inventory and static metadata, but no source file contents or screenshots. Because tool use was prohibited, route and component behavior could not be checked against the files themselves.
- The inventory lists included file paths but does not include their contents. Without source text, concrete navigation, form, asynchronous-action, state, keyboard/focus, touch-control, or feedback behavior cannot be established or cited.
- Tool use was prohibited, so the listed files could not be opened. No rendered evidence or screenshots were supplied; no rendered behavior was assessed.
- The supplied material contains a project inventory but no source-file contents or attached screenshots. The empty candidate findings list provides no behavioral claims to cross-validate. No behavioral finding can be supported from the available evidence.
- The visual auditor was not invoked because no rendered screenshots were available.

## Recommended next steps

1. Capture desktop (1440 px), tablet (768 px), and mobile (390 px) browser evidence for the routes in the approved audit scope.
2. Review findings against the rendered experience and the project's own interaction constraints before prioritizing changes.
3. Provide the contents of the listed source files in the audit context to support a source-level review of component boundaries, imports, state ownership, rendering paths, reliability, and performance.
4. Provide the snapshot source-file contents in the task context to enable a source-based interaction audit.

Technical defects, behavior changes, and subjective design recommendations remain separate. No design or implementation approval is implied by this report.
