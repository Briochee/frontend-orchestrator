# Coverage and limitations

Audit completion status: **incomplete**
Requested depth: `deep`
Backend: `codex_cli_plus_static`

- Source and style files: 13
- Route candidates discovered: 6
- Routes rendered: 0
- Screenshots captured / attached / interpreted / validated: 0 / 0 / False / False
- Browser navigation failures: 0
- Component profiles: 228
- Viewports: none
- Passive keyboard focus screenshots: 0
- Browser controls activated: 0

## Known limits

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
