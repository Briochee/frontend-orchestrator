# Visual design audit

Audit completion status: **incomplete**
Screenshot states: captured 20; integrity-valid 14; attached to visual backend 0; interpreted False; evidence validated False.

## Rendered evidence

The following browser screenshots were captured from the explicitly supplied URL. Only routes and states present in these images were evaluated.

- `/` / `desktop` 1440×1129: `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/home-8a5eda-desktop.png` (HTTP 200)
- `/` / `desktop` 1440×1129: `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/home-8a5eda-desktop-keyboard-focus.png` (HTTP 200)
- `/` / `tablet` 768×1950: `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/home-8a5eda-tablet.png` (HTTP 200)
- `/` / `mobile` 390×2145: `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/home-8a5eda-mobile.png` (HTTP 200)
- `/analytics/` / `desktop` 1440×1000: `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/analytics-5e175e-desktop.png` (HTTP 200)
- `/analytics/` / `desktop` 1440×1000: `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/analytics-5e175e-desktop-keyboard-focus.png` (HTTP 200)
- `/customers/` / `desktop` 1440×1000: `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/customers-fdeb23-desktop.png` (HTTP 200)
- `/customers/` / `desktop` 1440×1000: `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/customers-fdeb23-desktop-keyboard-focus.png` (HTTP 200)
- `/customers/` / `tablet` 768×1024: `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/customers-fdeb23-tablet.png` (HTTP 200)
- `/customers/` / `mobile` 390×1473: `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/customers-fdeb23-mobile.png` (HTTP 200)
- `/orders/` / `desktop` 1440×1000: `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/orders-c6dc6d-desktop.png` (HTTP 200)
- `/orders/` / `desktop` 1440×1000: `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/orders-c6dc6d-desktop-keyboard-focus.png` (HTTP 200)
- `/settings/` / `desktop` 1440×1078: `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/settings-c325fa-desktop.png` (HTTP 200)
- `/settings/` / `desktop` 1440×1078: `/private/tmp/frontend-director-benchmark-20261114/demo-app/.agents/frontend-design-director/evidence/screenshots/settings-c325fa-desktop-keyboard-focus.png` (HTTP 200)
- Rejected capture `/analytics/` / `tablet`: Screenshot dimensions do not cover the requested viewport.
- Rejected capture `/analytics/` / `mobile`: Screenshot dimensions do not cover the requested viewport.
- Rejected capture `/orders/` / `tablet`: Screenshot dimensions do not cover the requested viewport.
- Rejected capture `/orders/` / `mobile`: Screenshot dimensions do not cover the requested viewport.
- Rejected capture `/settings/` / `tablet`: Screenshot dimensions do not cover the requested viewport.
- Rejected capture `/settings/` / `mobile`: Screenshot dimensions do not cover the requested viewport.

## Design identity

Not assessed by a visual reasoning backend. Screenshots, if listed above, are evidence for human review but are not automatically interpreted as design findings.

No screenshot interpretation was returned. The images remain available for human review; their content is not summarized by deterministic source analysis.

## Route and viewport coverage

- Source route candidates: 5
- Routes rendered: 5
- Screenshots: 20
- Rendered viewports: desktop, mobile, tablet

## Findings

No visual findings were produced. This does not establish that the views are free of visual or accessibility issues.

## Evidence gaps

- One non-activating Tab focus state is captured per route at desktop when available. Full keyboard order, hover, active, disabled, loading, empty, and error states were not exhaustively captured.
- Light and dark themes were not compared unless screenshots cover both themes.
- Browser runtime captured 0 console/page error(s); see `runtime-evidence.md` for route and viewport details.
- Audit status is incomplete. 6 requested route/viewport pair(s) lack a valid screenshot: /analytics/ / mobile, /analytics/ / tablet, /orders/ / mobile, /orders/ / tablet, /settings/ / mobile, /settings/ / tablet. Required specialist `frontend_code_auditor` did not complete both structured passes. Required specialist `frontend_ux_auditor` did not complete both structured passes. Required specialist `frontend_visual_auditor` did not complete both structured passes. No screenshot-backed visual analysis passed evidence validation.
- Review partial findings, correct the listed evidence or backend gaps, then retry with: frontend-director audit --project /private/tmp/frontend-director-benchmark-20261114/demo-app --url http://127.0.0.1:8765/ --depth deep --codex
- No project scripts, builds, dependency lifecycle hooks, or development servers were executed.
- No runtime, bundle-size, Web Vitals, network, or interaction measurements were collected.
- Source inspection cannot establish behavior on authenticated routes or runtime states.
- Screenshots were captured, but no visual evaluator was run; appearance findings remain unavailable.
- frontend_code_auditor did not return a valid structured result: BackendFailure: Codex exited with status 1: Error: turn/start: turn/start failed: Input exceeds the maximum length of 1048576 characters. (code -32602), data: {"input_error_code":"input_too_large","max_chars":1048576
- frontend_ux_auditor did not return a valid structured result: BackendFailure: Codex exited with status 1: Error: turn/start: turn/start failed: Input exceeds the maximum length of 1048576 characters. (code -32602), data: {"input_error_code":"input_too_large","max_chars":1048576
- frontend_visual_auditor did not return a valid structured result: BackendFailure: Codex exited with status 1: Error: turn/start: turn/start failed: Input exceeds the maximum length of 1048576 characters. (code -32602), data: {"input_error_code":"input_too_large","max_chars":1048576
