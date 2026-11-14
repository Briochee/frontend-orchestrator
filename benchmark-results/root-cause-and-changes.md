# Frontend director benchmark: root cause and changes

## Reproducible environment

- Repository checkout: `/Users/rio/Development/Local_Projects/frontend-orchestrator`; active package source is the editable checkout, not the separate pipx environment.
- Python 3.15.2; package 0.2.0; executable `/Users/rio/.local/bin/frontend-director`; Codex CLI 0.167.1.
- Host Playwright 1.65.1; Chromium, Firefox, and WebKit are available in the host browser cache. Playwright is not installed in the pipx environment; the active audit used the host Python environment.
- Baseline command syntax recorded in `baseline/manifest.json`: `python3 -m frontend_design_director --no-update-check audit --project <isolated-demo-app> --url http://127.0.0.1:8765/ --depth deep --codex --json`. Both installed CLI help commands were checked; the after runs used the supported `audit` flags.
- The baseline checkout suite had 70 passed, 3 skipped, and 17 subtests passed under `PYTHONPATH=src`; the final suite after changes had 93 passed and 19 subtests passed. The fixture's Node smoke tests passed 2/2.
- The original pipx installation was not overwritten. The copied project root supplied to Codex contained only `demo-app/`; the answer key was consulted only after the baseline attempt 6 artifacts had been frozen. No answer-key file was included in model input or production source/tests.
- The separately present, pre-existing `tests/frontend-audit-benchmark/demo-app/` copy has different file hashes from the isolated extraction in seven files. A read-only normalized comparison found identical markup across the five HTML routes, identical JavaScript tokens across the seven source modules, and CSS rule/value differences limited to whitespace formatting. The isolated, hash-frozen copy was the only project root used by the live audits; neither fixture copy was edited.

## Reproduced baseline

The baseline was run against the isolated `demo-app/` copy. The active `frontend-director` executable is from the editable checkout at this repository, so package version `0.2.0` was not a stale installed copy. Codex CLI was `0.167.1`.

- The baseline Codex code and UX calls failed because the generated strict JSON Schema left nested object properties optional. Codex rejected the schema at `findings.items.properties.evidence.items.required`, with `line` missing from `required`. This confirms a schema compatibility issue; the previous `Invalid sc...` excerpt was caused by truncation.
- The backend truncated stderr before preserving diagnostics, so the earlier run did not retain a useful full error.
- Route discovery produced a dot-segment route (`/analytics/../analytics`). Browser navigation rejected it and aborted the route batch. No routes rendered, no screenshots were captured, and the visual auditor was skipped.
- With no browser evidence, the report still represented the audit as completed and described a backend mode that did not reflect specialist success.
- Static security analysis reported `innerHTML` occurrences as generic sink findings without tracing callers and data sources. The findings did not distinguish synthetic records, constant templates, and editable settings data.
- The first code and UX prompts prohibited tools/source inspection too broadly. They have been changed to permit read-only inspection while prohibiting execution, builds, servers, dependency installation, network access, and modifications.

## Failures found during correction

- First corrected audit attempt: a missing screenshot-integrity helper raised `NameError`; the result was preserved as incomplete.
- Second attempt: all five routes rendered and 20 screenshots were saved, but six short-page images were falsely rejected because their full-page height was less than the viewport. Several specialist prompts exceeded the Codex app-server's 1,048,576-character request limit: code 1,718,449, UX 1,724,350, visual 1,722,770.
- The oversized requests came from copying almost all runtime/project intelligence into each specialist prompt. Role-specific project metadata is now compacted, and visual calls receive only the three viewport images for one route. The source runtime payload is kept out of technical prompts when it is not needed.
- Screenshot validation now compares the image against the rendered document height, so a valid short page is not rejected merely for being shorter than the viewport.
- A subsequent image review found a separate width issue: full-page screenshots used document scroll width, so responsive overflow produced images wider than the requested viewport (for example, the 390px Orders viewport produced an 886px image). Primary evidence now captures the viewport exactly and records scroll width / overflow pixels separately. This lets visual analysis see the actual 390px crop while still exposing page overflow.

## Implemented corrections

- Adapt strict Codex schemas recursively: object properties are required, optional values become nullable, and supported local definitions/references are expanded. Unsupported schemas fail explicitly as `invalid_schema`; response values remain validated.
- Preserve redacted backend diagnostics: specialist, CLI version, invocation configuration, schema hash, exit status, classification, stderr, validation details, retry count, failure location, and image artifact metadata.
- Normalize route paths and reject dot-segment traversal before browser navigation; one bad route no longer aborts other routes.
- Validate screenshot PNG integrity and record dimensions, hash, readiness, and browser errors. Track capture, validity, model attachment, interpretation, and evidence validation separately.
- Require route-specific visual observations tied to real screenshot references, then run a cross-screen visual comparison. Keep visual requests below the app-server request limit by scoping attached screenshots and route metadata.
- Gate exhaustive visual completion on required routes/viewports, specialist status, valid evidence, and visual interpretation. Incomplete audit state preserves partial evidence and offers retry; it cannot advance to design direction.
- Replace generic `innerHTML` pattern findings with source-to-sink data-flow tracing for benchmark source. The local report records the traced settings input, constant template, and fixed synthetic order records separately.
- Preserve detailed specialist assessments and emit execution, coverage, security data-flow, visual, technical, behavioral, responsive, and design-system artifacts.

## Verified completed run and latest retry

- `after/attempt-7/` is the immutable raw `audit-005` completed live Codex run. It exited 0, discovered/rendered all five routes, completed both code and UX passes, and completed the per-route visual interpretation and evidence-validation passes. Its reports contain 29 findings: 10 technical, 12 behavioral, and 7 visual.
- The raw `audit-005` capture has 20 valid PNGs: the 15 required route/viewport combinations plus five desktop passive-focus captures. Fifteen primary screenshots (all five routes at 1440×1000, 768×1024, and 390×844) were attached to the visual model, interpreted, and validated against route/viewport evidence. The backend diagnostics list is empty.
- `after/finalized-audit-005/` is a portable presentation copy of that frozen run. It applies the production limitation/recommendation reconciliation helper added after `audit-005` to remove stale static-only claims contradicted by confirmed browser evidence. It does not alter findings, specialist responses, screenshot bytes, or model results; `report-reconciliation.json` and `finalization-note.md` document this. The original run remains unchanged.
- The latest live retry, `after/attempt-8/` (`audit-006`), correctly exited 3 and is marked `incomplete`. Code and UX completed, but the Codex account usage limit blocked the remaining four route visual passes after the Home visual pass. Its partial browser evidence and diagnostics are preserved; the report explicitly requires retry. No further live Codex calls were made after the quota error.
- A direct browser capture verified 15/15 primary route/viewport pairs with viewport-sized PNGs, no page errors, no console errors, and no failed requests. Browser-measured horizontal overflow was 123px for Orders tablet, 496px for Orders mobile, 312px for Analytics tablet, 351px for Analytics mobile, 18px for Settings tablet, and 391px for Settings mobile.
- A separate same-origin Playwright session exercised the safe synthetic workflows and recorded observed results in `after/interaction-runtime-audit.md`. That session is explicitly separate from the orchestrator's model audit: the automated audit activates zero controls and labels those behaviors as source-inspected or untested rather than runtime-verified.
- The finalized package and its 20 screenshot hashes/dimensions were checked after the retry. All files validate. The report package includes architecture, routes, components, colors, typography, visual, technical, behavioral, responsive, security data-flow, performance, coverage, execution, and evidence artifacts.

## Remaining limitations

- Codex quota exhaustion prevented a complete newest run after the report-merging correction. The completed `audit-005` predates that source correction; its portable presentation copy was reconciled offline with the production helper, and the corrected incomplete path was demonstrated by `audit-006`.
- The automated browser is intentionally passive. Safe runtime interactions were exercised separately for this fixture but are not incorporated into the model's findings. General-purpose control activation still needs explicit safety constraints and a persisted interaction-state evidence format.
- The report contains overlapping technical/behavioral findings and a long, repetitive next-step list. Recommendations are evidence-linked, but prioritization and cross-category consolidation need further improvement.
- No human reviewer has scored the post-fix audit. The comparison document uses a clearly labeled provisional rubric score based on inspected artifacts and preserves the prior human-reported 20/100 as historical context.
- The project fixture smoke tests passed (2/2). The orchestrator's full test suite passed (93 tests and 19 subtests). The user-facing benchmark app was not modified.
