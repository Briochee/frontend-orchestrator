# Executive summary

Project: `northstar-ops-audit-fixture`
Description: Dependency-free multi-route frontend audit benchmark with synthetic data
Framework signals: Static HTML/CSS/JavaScript (detected from files)

The audit contains 3 technical, 0 behavioral, and 0 visual finding(s).

## Coverage

- Source/style files: 13
- Route candidates: 26
- Routes rendered: 0
- Screenshots: 0
- Browser navigation failures: 0
- Component profiles: 228
- Analysis backend: `codex_cli_plus_static`; requested profile `deep`

## Highest-priority findings

- **MEDIUM · TECH-13ED89F2: HTML injection sink requires data-flow review.** Unsanitized input can introduce script injection or markup integrity issues.
- **MEDIUM · TECH-B96A0E73: HTML injection sink requires data-flow review.** Unsanitized input can introduce script injection or markup integrity issues.
- **MEDIUM · TECH-CC0A78BE: HTML injection sink requires data-flow review.** Unsanitized input can introduce script injection or markup integrity issues.

## Visual design identity

Not interpreted by a screenshot-capable visual reasoning pass.

## Important coverage limits

- No project scripts, builds, dependency lifecycle hooks, or development servers were executed.
- No runtime, bundle-size, Web Vitals, network, or interaction measurements were collected.
- Source inspection cannot establish behavior on authenticated routes or runtime states.
- No rendered screenshots or equivalent browser evidence were available. The visual audit makes no claims about the application's appearance.
- frontend_code_auditor did not return a valid structured result: BackendFailure: Codex exited with status 1: Return only JSON matching the supplied schema. Do not report visual appearance unless screenshot evidence is attached. ERROR: {"type":"error","error":{"message":"Invalid sc
- frontend_ux_auditor did not return a valid structured result: BackendFailure: Codex exited with status 1: Return only JSON matching the supplied schema. Do not report visual appearance unless screenshot evidence is attached. ERROR: {"type":"error","error":{"message":"Invalid sc
- The visual auditor was not invoked because no rendered screenshots were available.
- Browser evidence was unavailable: ValueError: Route must be an exact same-origin absolute path without query or traversal: '/analytics/../analytics'.

Human decisions about design, behavior, and implementation remain pending at their existing approval gates.
