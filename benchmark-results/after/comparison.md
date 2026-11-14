# Frontend audit benchmark: before and after

## Run selection and scoring method

The baseline is the frozen source-only/failed-backend run in `../baseline/`. The successful after run is `attempt-7/` (`audit-005`), presented with the post-run limitation merge in `finalized-audit-005/`. The newest live run, `attempt-8/` (`audit-006`), is incomplete because the Codex account usage limit stopped the remaining visual calls; it is not scored as a completed audit.

Scores below apply the requested six-dimension rubric to the frozen baseline and the completed after-run artifacts. They are a post-hoc evaluator estimate, not a human review. The earlier human-reported 20/100 has no dimension scores or preserved reviewer worksheet, so it is recorded as historical context rather than substituted into this dimensioned comparison.

| Dimension | Weight | Baseline (0–5) | After (0–5) | After evidence and rationale |
|---|---:|---:|---|
| Rendered accuracy | 25% | 0 | 4.0 | All five routes have route-specific descriptions tied to viewport screenshots. The report identifies actual clipping and cross-screen variations. Some design issues remain unreported and several responsive descriptions are repeated. |
| Design intelligence | 20% | 0.5 | 3.5 | It describes the navy rail, pale workspace, white panels, teal accents, Settings’ serif/violet variation, typography, color samples, and responsive hierarchy. Some style analysis is too verbose to review efficiently. |
| Component understanding | 15% | 1.0 | 3.5 | It maps static HTML routes, shared modules, feature scripts, CSS-class patterns, tests, and 228 profiled elements without claiming a React component tree. The inventory is noisy and contains low-level repeated profiles. |
| Behavioral depth | 15% | 0.5 | 3.0 | The model audit identifies behavior from source and labels it `static_analysis`; it does not activate controls. A separate safe Playwright session verified several fixture workflows, but those observations are not merged into the model’s findings. |
| Evidence and coverage | 15% | 0.5 | 4.5 | The completed run covers 5/5 routes and 15/15 required route/viewport pairs. Twenty PNGs pass path, hash, format, and dimension checks; 15 images were attached, interpreted, and validated. No browser navigation failures or backend diagnostics were recorded. |
| Recommendations | 10% | 1.0 | 2.5 | Recommendations generally follow from identified issues, but the report has a long list of overlapping next steps and duplicates some issues across technical, behavioral, and visual areas. |
| **Weighted score** | **100%** | **10/100** | **72/100** | `sum((score / 5) × weight)`; after score is provisional and below the 80/100 target. |

The baseline 10/100 is this document’s post-hoc rubric score: no browser screenshots, no interpreted visual evidence, and failed code/UX specialists cap the evidence-dependent dimensions. The supplied historical human score of 20/100 is retained separately. The after score is not a human evaluation and should not be described as one.

## Benchmark finding review

The private answer key was opened only after the initial benchmark attempt's reports, screenshots, diagnostics, and coverage were frozen under `attempt-6/`. The later Codex audits used the same general prompts and the key was not included in model input, production logic, or prose-matching tests. The post-key runs are model-isolated, though the operator's later evaluation was no longer blind.

| Result | Findings |
|---|---|
| Supported (16) | F01 shared visual identity and route variation; F02 heading/font differences; F03 route-level accent colors; F06 Orders overflow; F07 Settings fixed-width form row; F08 Analytics chart width; F09 suppressed focus outlines; F11 dialog focus lifecycle; F12 theme toggle mismatch; F13 delayed save failure from source; F14 editable value traced into the toast HTML sink; F15 constant/synthetic HTML use distinguished; F19 inert controls; F20 narrow smoke-test scope; F21 shared shell and class-based components; F22 unmeasured performance limits stated without invented Web Vitals. |
| Partial (4) | F04 actual colors and contrast samples are present, but the report does not clearly elevate every seeded muted-text concern; F05 the customer-card radius exception is called out, while other seeded radius exceptions are not; F16 the hardcoded bucket behavior is found, but the 1–100,000 linear step-1 precision tradeoff is not developed; F18 the Orders toolbar and responsive composition are described, but task prioritization is limited. |
| Missed (2) | F10 the notification icon’s missing accessible name; F17 the continuous beacon/transitions lack a reduced-motion fallback. |

The report also makes legitimate findings beyond the key, including no-match feedback, false export confirmation, closed mobile navigation remaining keyboard reachable, and duplicate feedback paths. No clearly unsupported vulnerability or fabricated performance measurement was found in this review. The HTML-sink findings are source traced and distinguish the editable Settings value from constant toast markup and fixed order records. The same Settings flow is nevertheless represented in both technical and behavioral findings, reducing signal.

## Reproducible execution comparison

| Evidence | Frozen baseline | Completed after run (`audit-005`) | Latest retry (`audit-006`) |
|---|---|---|---|
| CLI result | Audit reported complete despite specialist failures and no rendered evidence | Exit 0; `completed` | Exit 3; `incomplete` |
| Routes | 5 primary routes among 26 candidates, 0 rendered | 5 rendered | 5 rendered |
| Required screenshots | 0 | 15 primary plus 5 passive-focus captures | 15 primary plus 5 passive-focus captures |
| Screenshot model delivery | None | 15 attached, interpreted, and evidence-validated across 5 routes | Home’s 3 attached; remaining visual routes blocked by usage limit |
| Code / UX specialist passes | Both failed | Both completed first and cross-validation passes | Both completed first and cross-validation passes |
| Visual specialist | Skipped | Per-route passes and cross-validation completed | Partial; remaining passes blocked by Codex account limit |
| Backend diagnostics | Truncated `Invalid sc...` excerpts | Empty | Classified `backend_invocation_failed` quota errors preserved with stderr |

For `audit-006`, the saved diagnostic says the account usage limit was reached and gives a later retry time. This is an external quota blocker, not evidence that the corrected visual schema or screenshot attachment failed. Its incomplete status correctly prevents it from being presented as a successful exhaustive audit.

## Remaining quality work

- Add an explicitly safety-bounded interaction pass that records observed control states in the orchestrated evidence package. Until then, the audit remains passive and must not claim interaction testing.
- Add checks for accessible names on buttons and reduced-motion declarations; these two seeded issues were missed despite otherwise strong browser/source coverage.
- Consolidate overlapping findings and prioritize a short action list while retaining detailed evidence under each finding. The 161 KB typography artifact and recommendation list numbered through 40 are too cumbersome for efficient review.
- Re-run the same live audit after Codex quota resets, using the current source and the same fixture/routes/viewports. A human reviewer should then score the reports using the rubric before claiming the 80/100 quality target.

## Artifact links

- Completed report package: [`finalized-audit-005/reports/audit-005/audit-index.md`](finalized-audit-005/reports/audit-005/audit-index.md)
- Screenshot gallery: [`finalized-audit-005/evidence/screenshot-gallery.html`](finalized-audit-005/evidence/screenshot-gallery.html)
- Coverage and limitations: [`finalized-audit-005/reports/audit-005/coverage-and-limitations.md`](finalized-audit-005/reports/audit-005/coverage-and-limitations.md)
- Independent runtime interactions: [`interaction-runtime-audit.md`](interaction-runtime-audit.md)
- Incomplete quota-limited retry: [`attempt-8/reports/audit-006/audit-summary.md`](attempt-8/reports/audit-006/audit-summary.md)
