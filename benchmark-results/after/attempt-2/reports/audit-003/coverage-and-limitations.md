# Coverage and limitations

Audit completion status: **incomplete**
Requested depth: `deep`
Backend: `codex_cli_plus_static`

- Source and style files: 13
- Route candidates discovered: 5
- Routes rendered: 5
- Screenshots captured / attached / interpreted / validated: 20 / 0 / False / False
- Browser navigation failures: 0
- Component profiles: 228
- Viewports: desktop, mobile, tablet
- Passive keyboard focus screenshots: 5
- Browser controls activated: 0

## Known limits

- Audit status is incomplete. 6 requested route/viewport pair(s) lack a valid screenshot: /analytics/ / mobile, /analytics/ / tablet, /orders/ / mobile, /orders/ / tablet, /settings/ / mobile, /settings/ / tablet. Required specialist `frontend_code_auditor` did not complete both structured passes. Required specialist `frontend_ux_auditor` did not complete both structured passes. Required specialist `frontend_visual_auditor` did not complete both structured passes. No screenshot-backed visual analysis passed evidence validation.
- Review partial findings, correct the listed evidence or backend gaps, then retry with: frontend-director audit --project /private/tmp/frontend-director-benchmark-20261114/demo-app --url http://127.0.0.1:8765/ --depth deep --codex
- No project scripts, builds, dependency lifecycle hooks, or development servers were executed.
- No runtime, bundle-size, Web Vitals, network, or interaction measurements were collected.
- Source inspection cannot establish behavior on authenticated routes or runtime states.
- Screenshots were captured, but no visual evaluator was run; appearance findings remain unavailable.
- frontend_code_auditor did not return a valid structured result: BackendFailure: Codex exited with status 1: Error: turn/start: turn/start failed: Input exceeds the maximum length of 1048576 characters. (code -32602), data: {"input_error_code":"input_too_large","max_chars":1048576
- frontend_ux_auditor did not return a valid structured result: BackendFailure: Codex exited with status 1: Error: turn/start: turn/start failed: Input exceeds the maximum length of 1048576 characters. (code -32602), data: {"input_error_code":"input_too_large","max_chars":1048576
- frontend_visual_auditor did not return a valid structured result: BackendFailure: Codex exited with status 1: Error: turn/start: turn/start failed: Input exceeds the maximum length of 1048576 characters. (code -32602), data: {"input_error_code":"input_too_large","max_chars":1048576
