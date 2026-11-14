# Technical and architecture audit

Audit backend: `codex_cli_plus_static`

## Findings

### TECH-45E0725A · User-controlled content reaches an HTML rendering sink

- Severity: **medium**; confidence: **high**; verification: `static_analysis`
- Category: `security_and_rendering`
- Description: `toast` writes `message` to `innerHTML`. A caller passes a value derived from editable value `team`; the inspected path contains no recognized HTML sanitizer.
- Impact: Markup supplied through the editable value can be parsed as HTML in the current page context.
- Recommendation: Render user-provided values with `textContent` or DOM nodes; if authored markup is required, sanitize it with a reviewed allowlist sanitizer.
- Evidence:
  - `src/components.js:8` — HTML sink receives the traced value.
  - `src/settings.js:18` — Call site supplies the value written to the HTML sink.
  - `src/settings.js:13` — `team` is read from a DOM or browser-provided value.


## Evidence and limitations

- Audit status is incomplete. 6 requested route/viewport pair(s) lack a valid screenshot: /analytics/ / mobile, /analytics/ / tablet, /orders/ / mobile, /orders/ / tablet, /settings/ / mobile, /settings/ / tablet. Required specialist `frontend_code_auditor` did not complete both structured passes. Required specialist `frontend_ux_auditor` did not complete both structured passes. Required specialist `frontend_visual_auditor` did not complete both structured passes. No screenshot-backed visual analysis passed evidence validation.
- Review partial findings, correct the listed evidence or backend gaps, then retry with: frontend-director audit --project /private/tmp/frontend-director-benchmark-20261114/demo-app --url http://127.0.0.1:8765/ --depth deep --codex
- No project scripts, builds, dependency lifecycle hooks, or development servers were executed.
- No runtime, bundle-size, Web Vitals, network, or interaction measurements were collected.
- Source inspection cannot establish behavior on authenticated routes or runtime states.
- Screenshots were captured, but no visual evaluator was run; appearance findings remain unavailable.
- frontend_code_auditor did not return a valid structured result: BackendFailure: Codex exited with status 1: Error: turn/start: turn/start failed: Input exceeds the maximum length of 1048576 characters. (code -32602), data: {"input_error_code":"input_too_large","max_chars":1048576
- frontend_ux_auditor did not return a valid structured result: BackendFailure: Codex exited with status 1: Error: turn/start: turn/start failed: Input exceeds the maximum length of 1048576 characters. (code -32602), data: {"input_error_code":"input_too_large","max_chars":1048576
- frontend_visual_auditor did not return a valid structured result: BackendFailure: Codex exited with status 1: Error: turn/start: turn/start failed: Input exceeds the maximum length of 1048576 characters. (code -32602), data: {"input_error_code":"input_too_large","max_chars":1048576

## Suggested next steps

- Capture desktop (1440 px), tablet (768 px), and mobile (390 px) browser evidence for the routes in the approved audit scope.
- Review findings against the rendered experience and the project's own interaction constraints before prioritizing changes.
