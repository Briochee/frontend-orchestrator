# Test, Diagnose, and Improve `frontend-design-director` Against a Realistic Frontend Benchmark

## Role and objective

You are a senior Python orchestration engineer, Codex CLI integration debugger, browser QA engineer, frontend architect, and design-systems reviewer. **Improve the existing `frontend-design-director` repository, not the benchmark app.** Diagnose root causes of failed or shallow audits and deliver an evidence-backed, functioning deep-audit workflow.

The attached `frontend-audit-benchmark.zip` contains:

- `frontend-audit-benchmark/demo-app/`: a self-contained five-screen app using static HTML/CSS/ES modules, with fully synthetic data and deliberate UX/design/behavior issues.
- `frontend-audit-benchmark/evaluator-private/`: a separate answer key and human rubric. **DO NOT READ, INDEX, PROVIDE TO CODEX, OR INCLUDE IT IN ANY AUDIT INPUT BEFORE THE FIRST AUDIT IS FROZEN.** Do not use it to train prompts, hard-code detectors, or manufacture findings. Only consult the key afterward for evaluation. The app's `--project` root must be `demo-app/` alone.

If the ZIP is not already accessible in the environment, ask the user to extract it and provide the project path. Do not invent paths.

## Known failure evidence from earlier user audit

Previously generated reports showed **4 source route candidates, 0 rendered routes, 0 screenshots**, no actual visual-design findings, and no runtime interaction/performance data. Both `frontend_code_auditor` and `frontend_ux_auditor` failed when Codex exited status 1 with an error truncated at `Invalid sc...`. The visual agent was skipped because the audit command had no `--url`. Static findings were multiple near-duplicate HTML injection sink warnings without data-flow analysis. The reported quality score was 20/100 across six dimensions. **Treat these as hypotheses to reproduce, not assumptions about the current revision.** The complete schema error is unknown until diagnostics recover it.

## Mandatory operating rules

1. Inspect existing code, tests, configuration, and repo instructions before editing. Preserve working architecture and approval/patch safeguards.
2. Make a focused plan and verify each stage. Prefer correcting upstream evidence/model execution over adding more agents or longer report templates.
3. Audit the benchmark as-is; **never edit the fixture to make the auditor pass**. Maintain a baseline fingerprint/clean copy.
4. Do not read the private evaluator key until after a frozen, independently generated baseline report. Do not supply that key to the auditing model, even after reviewing it.
5. Explicitly distinguish source-derived, browser-observed, model-inferred, and measured findings. No invented screenshots, page states, performance metrics, or WCAG certification.
6. Starting project code, invoking models, installing dependencies, or changing production files requires the normal permission/approval controls. Do not bypass the existing human gates.
7. Continue through diagnose → fix → test → re-audit → review. At meaningful phase boundaries, offer a next action with optional instructions; do not interpret ordinary “continue” as approval to modify production files or apply patches. Preserve session state. Only terminate a guided session on an explicit end action.
8. Build general-purpose improvements that work with unfamiliar projects/frameworks. Do not add benchmark-specific path names, magic findings, or special cases to production audit logic.

## Stage 1 — Establish the baseline and inspect the orchestrator

Inspect `pyproject.toml`, CLI help, `src/frontend_design_director/` modules for discovery/auditing/browser/Codex adapter/schema/reports/guidance/persistence, the installed Codex CLI, current skill/agent resources, and tests. Check the actual executable and source checkout used by the environment: editable pipx installations can have an unchanged `0.1.0` version while source files have changed. Do not reinstall the user's global environment without approval.

Run available tests and record results. Document actual audit flags (`--depth`, `--route`, `--url`, `--codex`, `--server-command`, etc.) from `frontend-director audit --help` rather than guessing. Produce a short diagnostic note identifying evidence collection boundaries, schema contracts, model invocation arguments, result parsing, fallback paths, and conditions under which an audit is labeled `completed` versus `incomplete`.

Record reproducible baseline metadata: Git revision (if any), package installation/source path, Python version, Codex version, browser version, and audit configuration, excluding credentials and private workspace content.

## Stage 2 — Prepare and run the benchmark without contaminating the audit

Extract the ZIP to a temporary location separate from the orchestrator source. Use the extracted `demo-app/` as the ONLY audit root. Do not let recursive discovery traverse the private evaluator directory.

From the ZIP's parent directory (adapt the path to reality):

```bash
cd /path/to/frontend-audit-benchmark
python3 -m http.server 8765 --bind 127.0.0.1 --directory demo-app
```

In a second terminal, confirm HTTP 200 for `/`, `/orders/`, `/analytics/`, `/customers/`, `/settings/`, and their CSS/JS resources. Use an explicitly authorized local browser session. Do not install npm packages: the fixture requires none. Optionally run `cd demo-app && npm test` for the fixture's deliberately narrow data smoke tests; they do not establish UI quality.

Read the current CLI help and launch an exhaustive **live browser + Codex** audit. An example, only if the flags exist:

```bash
frontend-director audit \
  --project /absolute/path/to/frontend-audit-benchmark/demo-app \
  --url http://127.0.0.1:8765 \
  --depth exhaustive \
  --codex
```

If `--depth` is unsupported, use the installed equivalent. If route discovery misses routes, supply exact `--route` paths using its documented syntax. Never fabricate CLI syntax.

Run a separate no-`--url` test to check graceful incomplete/degraded behavior; do not confuse it with the full visual baseline. Do not silently invoke remote URLs or install dependencies.

## Stage 3 — Prove that browser evidence is real

Minimum benchmark coverage is all FIVE routes at 1440px, 768px and 390px, ideally 15 route/viewport screenshots. Additional 320px tests are useful for overflow. Collect full-page or viewport images and an evidence manifest containing valid paths, route, viewport, dimensions, timestamp, page readiness, and browser errors. Verify each screenshot is nonempty, has plausible dimensions, and contains actual page content rather than an error page or blank page.

Inspect accessible/effective browser data where possible: computed fonts, key colors, spacing, layout bounding boxes, viewport overflow (`scrollWidth > innerWidth`), responsive menus, console/page errors, network failures, and interactive states. Test safe local-only interactions: order search/filter, order-details modal and keyboard focus, analytics slider, settings theme toggle and simulated save with threshold 85000, customer search and mobile navigation. Only use synthetic fixture data. Avoid injecting script payloads to test security.

**Critical checkpoint:** storing screenshot paths is NOT proof that Codex received image content. Verify the request attachment protocol, file existence, accepted media types, and backend response with a small one-image test. Require screen-specific descriptions that can be directly checked against the image. Do not claim visual reasoning when only CSS/source text was available.

If Playwright/browser tooling is absent, report a blocker and request authorized setup. Do not mark a purported exhaustive rendered audit as complete with zero screenshots.

## Stage 4 — Find and repair the Codex backend failure

Investigate `frontend_code_auditor` and `frontend_ux_auditor` independently and the visual auditor after screenshots exist. Recover the **full original redacted** Codex stderr/structured error instead of truncating it at `Invalid sc...`; protect secrets and cap log size with an accessible diagnostic artifact or full error ID. Inspect actual JSON Schema sent to the installed Codex CLI. Reproduce using a tiny, known-valid schema, then incrementally compare with the production schema.

Check, as applicable:

- Supported `codex exec` flags and output-schema behavior for the INSTALLED CLI version.
- Whether top-level schema is the required shape, `additionalProperties` constraints, `$ref`/`$defs`, optional fields, union types, nested arrays, and unsupported formats cause rejection.
- Whether Pydantic-generated schema is converted properly for Codex's structured output requirements.
- Whether the CLI is receiving a schema file/path in the correct location and format.
- stdout versus stderr handling, exit codes, timeouts, retries and cancellation.
- Model selection and authentication without assuming an API key is required.
- Whether malformed responses fail validation and preserve diagnostic evidence.

Fix the root cause with supported interfaces, not by hiding schema failures or turning off all validation. Add a contract test against the actual JSON Schema and a mocked CLI failure test. For a real Codex integration smoke test, use minimal authorized synthetic content; report separately if account/network restrictions prevent invocation.

Use error classifications such as `invalid_schema`, `invocation_failed`, `timed_out`, `invalid_response`, `screenshot_unavailable`, and `analysis_unverified`, with user-actionable recovery text. A model failure must never be silently reclassified as a successful full audit.

## Stage 5 — Deepen the actual audit, not its verbosity

Once execution works, ensure independently structured technical, visual and behavioral reports with cross-links to routes, screenshots and source. Avoid generic filler or findings that merely repeat sink patterns.

**Visual intelligence:** For each representative screen, describe actual layout, visual hierarchy, color roles (real token values and computed uses), typography (font family, scale/weight, headings, labels), grid/spacing, border radii/surfaces, iconography, information density, responsive adaptations, states, motion and relative consistency. Provide a grounded design identity statement and identify both strengths and weaknesses. Compare similar components across routes rather than evaluating only isolated screenshots.

**Component intelligence:** Inventory actual HTML/CSS/JS components and their relationships, including sidebar, topbar, metric cards, data table, badges, settings controls, modal, toast, charts and customer cards if observed. Do not invent a React component hierarchy for a vanilla JS application. Link source files, routes, usage and rendered evidence.

**Behavior:** Verify user journeys and control feedback, keyboard/focus, modal behavior, empty/search states, settings save and theme behavior, slider mapping and mobile navigation. Record `observed` versus `source-inferred`, and avoid submitting destructive actions against arbitrary real apps. For this fixture, local-only simulated state changes are safe.

**Technical:** Determine actual module structure, CSS strategy and test coverage, semantic/accessibility issues, data flow into `innerHTML` sinks, actual error and network results and real measured browser timings if available. Distinguish constant HTML strings from untrusted input flows; do not label every `innerHTML` occurrence as exploitable. Do not invent Web Vitals or promise complete WCAG compliance.

**Evidence:** Each finding requires category, severity, confidence, source/route, concrete observation, evidence reference, user impact, actionable remedy and verification type. Keep a complete component/route/design inventory alongside summary findings. Perform targeted follow-up when large gaps remain.

## Stage 6 — Introduce meaningful audit completion gates

A successful process exit or valid JSON response does not imply a successful exhaustive audit. Implement a coverage contract that verifies route/viewport screenshots, required specialist outputs, minimum evidence types and report content. Distinguish `completed`, `completed_with_limitations`, `incomplete`, and `failed` consistently with the existing state machine.

For this benchmark, declare exhaustive visual analysis **incomplete** if no rendered screens or screenshot interpretations exist, or if required specialists failed. Preserve partial reports and diagnostic artifacts. Provide a next-step recovery choice rather than resetting state or continuing straight to design approval. The guided workflow should discover an existing server or offer to start one under explicit authorization, carry its verified URL into all browser steps, and avoid requiring users to know hidden `--url` dependencies.

For larger real applications, represent partial coverage honestly; do not hard-code “all five routes” in production. Use route groups, configurable budgets and reproducible sampling.

## Stage 7 — Freeze reports, then evaluate against the private key

Before opening `evaluator-private/`, save a timestamped, immutable or reproducibly copied run of the audit reports and evidence. Only then read `evaluator-private/EXPECTED_FINDINGS.md`, `REVIEW_SCORECARD.md`, and `ORCHESTRATOR_FAILURES_TO_RETEST.md` as the HUMAN/EVALUATOR aid. Do not feed these files to the auditing model or turn their findings into hardcoded detection paths.

Apply the six-dimension weighted quality rubric: rendered accuracy 25%, design intelligence 20%, component understanding 15%, behavioral depth 15%, evidence and coverage 15%, recommendations 10%. Score each 0–5 using actual report and screenshot evidence. The previous baseline was 20/100, but do not claim improvement without a new comparable measurement. Also record supported/partially supported/missed seeded findings and false positives; finding every seeded issue is not mandatory and new legitimate findings can be credited. Judge quality rather than just word count.

Aim for a credible >=80/100 human-reviewed score on this benchmark, ideally >=4/5 in rendered accuracy, design intelligence, component understanding and evidence quality. This is an improvement target, not a guarantee or license to invent results.

## Stage 8 — Implement targeted fixes and regressions

Use evidence from the baseline to prioritize the smallest sound architectural corrections: schema compatibility, redacted diagnostics, server URL propagation, route/viewport evidence, image attachment, specialist execution, cross-route synthesis and completion gating. Preserve approval isolation, temporary Git patch workflow, target-file hashes and user edits. Do not modify fixture source. Add automated tests for:

1. Schema acceptance and invalid-schema diagnostics (mock + optional real CLI).
2. Browser startup/attachment, route/viewport screenshots and manifest integrity.
3. Screenshot bytes actually provided to visual backend (stub/contract test).
4. Incomplete status when no URL, browser or screenshots are available.
5. Specialist failure propagation without fake visual findings.
6. Source `innerHTML` sink triage using data-flow evidence, not regex-only medium severity claims.
7. Deep component/color/typography inventory against a generic static fixture.
8. Safe interaction evidence and truthful unverified state labels.
9. Reproducible audits, versioned artifacts and cross-report references.
10. Guided next-step choices, optional added instructions, pause/resume/end and independent implementation approval.
11. Compatibility with existing CLI, stored workflows and installed resources.

Do not write tests that merely assert expected fixture-specific phrases in generated reports. Test observable behaviors, schemas and evidence-handling contracts.

## Stage 9 — Re-run and deliver evidence

After corrections, repeat the SAME benchmark with the SAME routes, widths, model settings, permissions and meaningful test conditions. Run unit/integration tests, syntax checks and relevant packaging checks. Re-score against the frozen baseline, retaining before/after artifacts and documenting any external tool limitation. Do not claim screenshots were reviewed if no visual backend actually inspected them.

Deliver:

- Root-cause summary for the earlier failures, including the full safely redacted `Invalid sc...` explanation if reproduced.
- List of production files changed and why.
- Actual live invocation commands used.
- Codex agent execution status and schema validation status.
- Route/viewport screenshot matrix with actual artifact paths.
- Sample accurate screen-by-screen visual and behavioral findings.
- Technical, visual and behavioral audit report links/paths.
- Explicit coverage gaps, model/tool failures and caveats.
- Baseline and after scores, with evidence; do not invent scores if no human evaluation occurred.
- Test commands/results and any unrun checks.
- Next recommended improvement, with one optional-input question.

**Completion criterion:** A real audited frontend is rendered and interpreted; specialist agents produce valid structured findings; route/component/design patterns are described concretely with evidence; errors remain visible rather than silently converted to success; and the guided session offers a meaningful next action without bypassing human authorization. If any part is blocked, deliver the maximum verified result, mark it incomplete, and identify the exact blocker. Do not solve the benchmark by exposing its private key to the model or altering the mock app.
