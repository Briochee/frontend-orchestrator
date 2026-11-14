# Interaction and behavior audit

Audit backend: `codex_cli_plus_static`

## Findings

No findings were produced for this audit type. This is not a guarantee that the area is defect-free.

## Evidence and limitations

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

## Suggested next steps

- Capture desktop (1440 px), tablet (768 px), and mobile (390 px) browser evidence for the routes in the approved audit scope.
- Review findings against the rendered experience and the project's own interaction constraints before prioritizing changes.
- Provide the contents of the listed source files in the audit context to support a source-level review of component boundaries, imports, state ownership, rendering paths, reliability, and performance.
- Provide the snapshot source-file contents in the task context to enable a source-based interaction audit.

## Runtime action coverage

Browser collection inspected structural controls and accessible-name signals. It captured one passive Tab focus state per route at desktop when a focusable target was available; it did not activate application controls, submit forms, or claim workflow outcomes. Review source-derived journeys above; unexecuted behavior remains unverified.
