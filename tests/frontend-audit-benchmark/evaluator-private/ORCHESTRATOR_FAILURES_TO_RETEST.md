# Known orchestrator failures from previous audit reports — private evaluator

The earlier user's reports (not from this fixture) showed:

- `frontend_code_auditor` and `frontend_ux_auditor` failed with exit status 1. Diagnostics were truncated at `Invalid sc...`; exact underlying schema fault is unknown until full redacted error is retrieved.
- `frontend_visual_auditor` was not invoked because no screenshots were available.
- Browser evidence was not collected because no explicit `--url` was passed.
- A supposed audit emitted near-duplicate HTML sink pattern findings without tracing data flow and misled by completion semantics.

Regression checks:

1. All enabled backend adapters must work with the *installed* Codex CLI; JSON schema and output format must be accepted.
2. Capture full, safely redacted diagnostic errors instead of unhelpful truncated strings.
3. Guided deep audit must prompt to attach/start the target app, then pass the verified URL automatically after authorization.
4. Never silently mark deep visual audit complete with 0 screenshots or 0 rendered routes.
5. Validate actual screenshot bytes were attached and model interpretation produced grounded screen-specific observations.
6. If a specialist fails, preserve partial results and mark incomplete; offer targeted retry after correction.
