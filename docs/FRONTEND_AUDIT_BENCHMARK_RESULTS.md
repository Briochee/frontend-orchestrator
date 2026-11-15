# Frontend audit benchmark results

## Scope and isolation

The audited input was a separate copy of `tests/frontend-audit-benchmark/demo-app/`. The original fixture was not modified. The audit provider received only that application copy and its filtered source snapshot; `evaluator-private/` was excluded. The private scorecard and answer key were read only after the completed run and its reports, screenshots, execution data, and 92-entry SHA-256 manifest had been frozen and verified.

## Verified local environment

- Python used for the regression suite: 3.15.2.
- Installed package and CLI: `frontend-design-director` 0.3.0; executable `/Users/rio/.local/bin/frontend-director`.
- The executable's pipx environment imports `/Users/rio/Development/Local_Projects/frontend-orchestrator/src/frontend_design_director/` through an editable installation (`direct_url.json`), so it uses the active source checkout without replacing the pipx environment.
- Codex CLI: 0.167.1, authenticated with the ChatGPT account plan.
- Playwright and Chromium were available; the full browser audit produced valid screenshots, and browser integration tests passed.

The completed run used `frontend-director` 0.3.0, Codex CLI 0.167.1, model `gpt-6-luna`, deep audit depth, comprehensive collaboration, and the explicit `--exercise-safe-interactions` option. The local HTTP server used an ephemeral loopback port so the runner could safely choose an available port. It served only the fixture copy.

## Baseline diagnosis

The earlier saved runs confirm that the failures were real and had different causes:

- `audit-001` recorded both source and UX specialist calls exiting with status 1. Its stored report contained a truncated CLI error. A controlled reproduction recovered the complete schema error: Codex strict output rejected `schema.properties.findings.items.properties.evidence.items.required` because `line`, although declared in `properties`, was absent from `required`. The issue was a nested optional property in the Pydantic-derived schema; the adapter now normalizes optional properties for Codex strict output and has schema regression tests.
- `audit-002` discovered six route candidates but rendered none. Browser evidence collection raised `NameError: name '_screenshot_integrity_error' is not defined`; no screenshots were produced. The visual specialist was correctly skipped by the evidence gate, and the audit was marked incomplete.
- `audit-003` saved screenshots but supplied none to the visual backend. All three specialist results were invalid. Their recorded inputs were about 1.72 million characters; the size correlated with the failures, but the original diagnostics do not prove that size alone caused them. Source inventory and report samples have since been bounded.
- `audit-004` attached and interpreted 15 images, but the code specialist returned an invalid structured response, so the audit remained incomplete.
- The preserved `audit-005` bundle completed with five rendered routes, 20 captured images, 15 screenshots attached and interpreted, all required route/viewport pairs, and 29 findings. Its coverage report nevertheless said no visual evaluator ran, and no runtime controls were exercised. That stale limitation contradicted its own execution metadata and visual report; report generation now removes the obsolete static-only limitation when validated visual evidence exists.
- `audit-006` had only three of 15 required screenshots interpreted after a provider limit. It was correctly marked incomplete.
- The first interaction-enabled collaborative rerun was also correctly marked incomplete: the UX auditor cited `interaction_probe`, which the evidence validator did not yet support. The validator now accepts only an exact reference to a tested interaction check for a behavioral finding, retries one invalid specialist response, and records retry/failure status.

The repetitive earlier technical output came from component occurrence inventory being treated too much like a component architecture map, plus broad source-pattern results without enough route, caller, and data-flow context. The source intelligence now maps static HTML routes and JavaScript modules, resolves local imports, bounds report samples, and traces straightforward DOM-input-to-HTML-sink paths. It labels constant markup and local synthetic data separately; it does not execute payloads or claim exploitability from a sink alone.

## Completed collaborative audit

The final frozen run is at:

```text
/private/tmp/frontend-director-collaboration-after-uxfix/frozen-audit/
```

The artifact index is `project-state/reports/audit-index.md`. The visual report is `project-state/reports/visual-audit.md`; it links the screenshot set. Browser and interaction manifests are in `project-state/evidence/`, and `SHA256SUMS.json` verifies the frozen artifact set. The run completed with exit code 0, 26 findings, and no backend diagnostics.

| Coverage item | Result |
|---|---|
| Routes | `/`, `/orders/`, `/analytics/`, `/customers/`, `/settings/` (5/5 rendered) |
| Required viewport pairs | 15/15: 1440×1000, 768×1024, and 390×844 on every route |
| Screenshots | 20 valid PNGs captured: 15 route/viewport images plus five desktop keyboard-focus states |
| Visual delivery | 15 required images attached, interpreted, and evidence-validated; 15 route/viewport assessments |
| Browser outcome | 0 navigation failures, 0 page errors, 0 failed requests in the recorded capture |
| Interaction probes | 6 tested checks across 4 routes, with reversible state restored and no post-readiness requests allowed |
| Findings | 8 behavioral, 8 technical, and 10 visual; 14 observed, 9 static-analysis, and 3 hypothesis findings |

The audit describes an actual five-page static HTML/CSS/JavaScript application, its shared `app.js` and `components.js` helpers, route-specific modules, synthetic data, and CSS-class-based interface patterns. It does not invent a React component tree. The reports include source-defined color and typography inventories, browser-computed style samples, route-by-route visual assessments, responsive document-width measurements, and explicitly limited single-run performance timings. LCP, INP, and CLS were not measured.

The safe probes observed the analytics range and its dependent value, a no-match customer search, an orders no-match search and dialog keyboard behavior, and reversible settings text/switch changes. They found zero customer results without an empty state, an order dialog that does not receive focus and stays open on Escape, and a dark-mode switch with no observed page-theme effect. The settings form was not submitted: the delayed save failure remains a source-inspected behavior, not a runtime observation. The probe never submits forms or activates save/delete/archive/confirmation actions.

## Expert assembly and review

The comprehensive plan considered and selected four callable Codex role-based specialists: technical architecture, UX/accessibility, visual design, and cross-disciplinary review. The three primary specialists completed their independent and verification passes; the cross-disciplinary reviewer completed a challenge pass. There were no backend diagnostics. Native named-subagent delegation was not claimed. Claude capabilities were excluded because cross-provider evidence transfer was not authorized; installed Codex/Claude skill and agent metadata remained distinct from executable specialist roles.

The initial frozen audit's cross-reviewer could see only source files and therefore described runtime probe observations as unavailable. After the audit was frozen, the review contract was improved to supply compact tested probe evidence separately and validate exact JSON-pointer references. A focused live Codex cross-review on the customer-search finding then returned a high-confidence, evidence-backed qualification using the exact tested interaction reference and `src/customers.js:5`. Its resolution correctly narrows the runtime claim to the one tested query. This supplemental call is recorded separately at `/private/tmp/frontend-director-cross-review-regression-20261114.json`; it does not alter the frozen full-audit bundle. A full audit was not repeated after this narrow cross-review-only change.

The frozen audit's cross-review made five challenges and five decisions, including one high-confidence duplicate consolidation for the dark-mode behavior. Its stale limitation about probes not being in the source snapshot remains visible in that immutable report; the later focused review verifies the corrected evidence handoff.

## Benchmark evaluation

The previous `audit-005` score of 72/100 was reported as provisional, and its saved bundle contains no per-dimension scorecard or human review. The earlier 20/100 result belongs to an older failed audit. The following after-score is a new, provisional self-assessment against the requested rubric, not a human evaluation:

| Dimension | Weight | After score (0–5) | Weighted points | Evidence and limit |
|---|---:|---:|---:|---|
| Rendered accuracy | 25% | 4.5 | 22.5 | All routes and viewport pairs were rendered; findings cite screen-specific screenshots. A few below-the-fold observations are low-impact rather than demonstrated usability failures. |
| Design intelligence | 20% | 4.0 | 16.0 | The audit explains the shared palette, surface/navigation identity, responsive shifts, and route-level differences; it misses some contrast and motion-accessibility concerns. |
| Component understanding | 15% | 3.5 | 10.5 | Static architecture, shared helpers, route modules, data sources, and UI patterns are described accurately. The 228-entry occurrence inventory is noisy and is not a count of implemented components. |
| Behavioral depth | 15% | 4.0 | 12.0 | Six runtime checks are distinguished from source inspection. Form submission, notification controls, and many secondary actions were not exercised. |
| Evidence and coverage | 15% | 4.5 | 13.5 | 15 required images were interpreted, all 15 screen assessments are present, probe citations resolve, and the capture had no browser errors. The immutable full run retains the earlier cross-review limitation. |
| Recommendations | 10% | 3.5 | 7.0 | Most findings have concrete impacts and scoped actions. A few low-severity fold observations are less actionable, and some related security observations remain duplicated. |
| **Provisional total** | **100%** |  | **81.5/100** | `sum((score / 5) × weight)`; not human-reviewed. |

Compared with the previously reported provisional 72/100, the independently rerun audit adds actual interaction observations, more route-specific visual findings, validated source-to-sink analysis, collaborative challenge/adjudication, and explicit evidence status. The dimensional score for 72 was not preserved, so only the aggregate can be compared. This does not establish that every seeded issue was found.

Post-freeze answer-key comparison confirmed supported coverage of the major cross-screen identity, responsive overflow, order-dialog keyboard behavior, dark-mode mismatch, customer empty-state behavior, slider range, source-traced editable value reaching `innerHTML`, fake controls, and the distinction between measured browser timings and unmeasured Web Vitals. The report did not fully cover low-contrast text, the notification button's accessible name, reduced-motion behavior, all typography/radius differences, or orders-toolbar density. The constant toast markup was distinguished from the editable-value flow, but the fixed order templates were not discussed as explicitly as the answer key recommends. These are remaining analysis gaps, not claims of a security exploit or conformance failure.

## Verification and remaining limitations

The final Python regression suite passed **135 tests**. Focused evidence-contract tests also passed, and a real Codex CLI cross-review completed and passed application-level citation validation. The benchmark's two dependency-free Node smoke tests passed. The original benchmark application remained unchanged.

The complete report bundle and gallery remain in the frozen directory above. The capture is a single Chromium run on one host; it is not cross-browser validation. Probe coverage is deliberately bounded, settings save failure was not exercised at runtime, no automated accessibility engine was run, and no field performance metrics were collected.
