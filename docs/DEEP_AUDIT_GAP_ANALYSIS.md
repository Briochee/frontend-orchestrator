# Deep Audit and Guided Workflow Gap Analysis

## Assessment scope

This assessment follows the current package and fixture at the time of implementation. It describes verified behavior in the repository, not an assumption that an optional tool is callable. The baseline standard-library suite contained 38 passing tests. Playwright is importable in the development environment; Chromium was not found on `PATH`, so the Playwright-managed browser executable still needs a runtime launch check.

## 1. Current implementation architecture

- `cli.py` is an `argparse` command router. It creates a `WorkflowStore`, selects a session, delegates one operation to `FrontendDesignDirector`, prints the result, and exits.
- `director.py` owns the workflow operations and phase changes. Discovery, audit, direction, mockup, planning, approval, patching, and verification are separate methods.
- `storage.py` persists sessions, events, artifacts, findings, decisions, approvals, and execution records in SQLite. Human approvals are bound to artifact digests and checked before implementation or patch application.
- `discovery.py` inspects project manifests and conventional paths without executing project code. It also discovers Codex, skills, agent files, and configured integration metadata.
- `snapshot.py` creates a filtered, symlink-free temporary Git checkout for Codex. Its limits are configurable in code (5,000 files, 2 MB per file, 100 MB total by default); sensitive-looking content and project instructions are excluded.
- `auditing.py` provides a small deterministic static pass and three optional Codex roles: technical, behavioral, and screenshot-backed visual. `reporting.py` renders five Markdown/JSON artifacts.
- `browser.py` is an optional Playwright adapter. It captures a supplied URL or a static mockup. It does not start an application, discover routes, interact with controls, inspect computed styles, or gather runtime diagnostics.
- `mockups.py`, `implementation.py`, and `verification.py` preserve isolated mockup generation, exact-path planning, temporary implementation snapshots, patch review, and explicit verification-command gates.
- The packaged Codex skill explains the granular CLI sequence and approval boundaries. No persistent guide/session interaction is implemented.

## 2. Existing audit execution flow

1. `frontend-director init` creates a session and its SQLite store.
2. `discover` inventories manifests, files, and Codex capabilities, then transitions to `CAPABILITIES_REVIEW`.
3. `audit` transitions the session to `AUDITING`, optionally captures one caller-supplied URL at three viewport sizes, runs static checks, and optionally invokes the three Codex roles in sequence.
4. Findings are replaced for the session, reports are written under the session artifact directory, and the session transitions to `AUDIT_COMPLETED`.
5. The process exits. The user or calling Codex agent must choose and invoke the next CLI command.

The current state machine correctly prevents audit or mockup completion from granting implementation permission. Its states model the production workflow, but not an independent guided-session status, pending conversational action, audit revision, or repeated improvement cycle.

## 3. Current source and browser evidence collection

### Source

- `discover_project` reads package manifests, selected configuration files, source-path suffixes, and a few styling signals. It detects framework dependencies and route-like files heuristically.
- `run_static_audit` currently emits a few rules: missing test infrastructure, a no-media-query hypothesis, direct HTML injection sinks, and literal HTML images without `alt`.
- Codex receives a filtered project snapshot. The prompt provides project metadata, the included/excluded file lists, and the screenshot inventory. Codex can inspect snapshot files under its read-only sandbox, but its task is a single high-level instruction per perspective rather than a sequenced reconnaissance, detail, cross-check, and gap-review process.
- Generic file discovery is not a relationship map. There is no component-to-route graph, screen inventory, theme inventory, token usage map, or project-specific analysis budget report.

### Browser

- Browser inspection is opt-in through `audit --url`; the orchestrator does not start project code or attach to a preexisting process automatically.
- The adapter visits exactly one supplied URL and records a full-page screenshot for 1440×1000, 768×1024, and 390×844. It restricts requests to the approved origin and blocks redirects outside it.
- It waits for `domcontentloaded`, then captures immediately. It does not wait for fonts or application readiness, inspect loading state, collect page errors, console messages, failed requests, navigation links, route coverage, DOM landmarks, computed CSS, accessibility snapshots, resource timing, or interactions.
- Captures are registered as screenshot artifacts. There is no screenshot manifest containing route, state, theme, readiness, or interaction provenance beyond viewport, URL, status, timestamp, and dimensions. No contact sheet or targeted element crop is created.

## 4. Where information is lost or overly summarized

- The static pass examines source lines for a few patterns; it does not explain application architecture or user journeys.
- The Codex audit sends a large inventory of filenames but no relevance-ranked file map or explicit staged context. The specialist tasks do not require route coverage, component profiles, design-token inventories, cross-screen comparisons, or a contradiction/gap report.
- Browser evidence is summarized as three images for one URL. Runtime errors, computed values, interaction paths, and route-specific context are discarded because they are never collected.
- The visual report has a design-identity heading, but only fills it with a generic evidence-boundary sentence when findings exist. It contains no extracted color, typography, spacing, component, theme, or responsive inventory.
- Audit artifacts use stable names and are rewritten on re-audit. `replace_findings` deletes the previous finding set; audit history and findings revisions are not preserved as first-class artifacts.
- `AuditResult` contains findings, limitations, recommendations, screenshots, and one backend label. It cannot represent coverage dimensions, route states, source maps, runtime observations, analysis passes, or unresolved questions.
- The CLI prints a stage result and exits. There is no stored next action, instruction registry, user-instruction append operation, guided resume prompt, revision request, or explicit end-of-guided-session marker.

## 5. Existing limitations

- Running or attaching to the target application is not implemented. The existing explicit URL boundary is safer, but requires a human to start the server and find a URL.
- Routes are inferred from a limited set of filenames/manifest hints; browser navigation links and route definitions are not reconciled.
- Only three fixed viewport widths are collected. Themes, breakpoints around actual CSS rules, component crops, and interaction states are not captured.
- Playwright availability is inferred from the Python package import. Browser installation and launch readiness are not probed during discovery.
- Static analysis has no parser/AST layer and is intentionally much narrower than the report vocabulary suggests.
- Codex audit quality depends on model behavior and one pass per role. The output contract validates finding shape/evidence ownership, not analytical coverage or completeness.
- The workflow is command-oriented. `status`, `pause`, and `resume` persist operational state, but not the user’s continuing conversational intent.
- The sample fixture is a small static page. It validates the base workflow but does not yet exercise route discovery, multiple components/screens, browser runtime evidence, or guided continuation.

## 6. Root causes

### Shallow analysis

1. The main deficiency is not merely prompt length: the evidence layer does not collect routes, DOM structure, computed styles, runtime errors, interaction outcomes, or component relationships.
2. The Codex roles receive no explicit inventory or pass protocol requiring architecture mapping, detailed token analysis, route comparison, and coverage review.
3. The default static path is a few pattern checks, while browser evidence is optional and has no local visual analyzer. A screenshot by itself is not interpreted unless a signed-in Codex visual role is invoked.
4. The schema validates individual findings but has no audit coverage model, observation taxonomy, source-location collection, screen/component profile, or validation status for expected analysis areas.
5. Reports mostly render findings that happen to exist. They do not independently construct the requested application map, route inventory, component inventory, design-system report, or limitations matrix.

### Discontinuous workflow

1. The CLI deliberately dispatches one command and exits; no command composes stages or presents a next-step choice.
2. Session metadata stores discovery and audit summaries, but there is no durable instruction registry or pending-user-action record.
3. The production phase enum ends at `COMPLETED`, with no orthogonal guided-session lifecycle or repeated-cycle relationship.
4. The skill lists commands in sequence but cannot make a completed CLI call stay active, recover pending conversational state, or distinguish “continue” from explicit workflow termination.

## 7. Proposed improvements

The implementation should improve the current evidence model and workflow incrementally rather than replacing the approval state machine.

1. **Architecture and route evidence:** build deterministic maps from discovered manifests, source paths, router declarations, navigation links, and component imports. Record confidence and discovery method for each route/component link.
2. **Runtime evidence:** retain explicit URL authorization; enrich Playwright capture with readiness, console/page errors, failed requests, document dimensions, landmarks, links, controls, loaded fonts, sampled computed styles, and navigation/resource timing. Add route-list input before any crawler. Keep same-origin and read-only interaction restrictions.
3. **Design-system extraction:** extract defined CSS variables and repeated color/type/spacing values from source, then correlate them with sampled rendered styles. Label source definitions separately from observed usage. Calculate contrast only for reliable foreground/background pairs.
4. **Coverage-aware analysis:** persist a coverage matrix and structured evidence records. Split source, runtime, visual, and interaction passes; cross-validate high-priority observations and report unavailable evidence explicitly. Preserve previous audit revisions.
5. **Detailed reports:** add architecture map, screen inventory, component inventory, design-system inventory, browser diagnostics, and coverage/limitations artifacts. Keep technical, visual, and behavioral findings independently addressable.
6. **Guided continuity:** add a `guide` command that composes safe completed stages, persists user instructions and pending actions, offers review/revisit/pause/end choices at human decision points, and resumes from stored phase without converting continuation into approval.
7. **Application execution:** only add a controlled server manager after the user approves a specific command and the implementation can prove process ownership, bounded readiness, log capture, and cleanup. Until then, attach only to an explicitly supplied or human-managed URL.
8. **Codex:** retain the existing supported `codex exec` adapter and JSON schemas. Feed each specialist only the relevant architecture, source references, screenshots, prior findings, and user constraints. Do not create speculative MCP or agent APIs.

## 8. Files and modules requiring modification

- `discovery.py`: architecture, route, package-root, and component relationships.
- `browser.py`: runtime diagnostics, readiness criteria, route navigation, computed styles, and richer evidence manifests.
- `models.py` / `storage.py`: typed evidence/coverage/instruction records and versioned audit history, while preserving existing SQLite sessions and approvals.
- `auditing.py`: multi-pass specialist tasks, objective static extraction, evidence validation, and coverage-quality checks.
- `reporting.py` / `director.py`: detailed report artifacts, architecture map, inventories, and audit revisions.
- `cli.py` / `state_machine.py`: guided session entry point, durable pending actions, optional instructions, revisit/continue/end behavior.
- `src/frontend_design_director/data/skill/SKILL.md`: explain guide/resume usage and preserve separate authorization gates.
- `tests/` and `examples/sample-frontend/`: deterministic route/component fixture, mocked backend contracts, and browser/runtime coverage.
- `README.md`, `docs/ARCHITECTURE.md`, `docs/SETUP.md`, `docs/SECURITY.md`, and `docs/EXAMPLE_WORKFLOW.md`: update after shipped behavior exists.

## 9. Backward-compatibility considerations

- Keep existing CLI commands and their approval semantics. `guide` should call the same director methods rather than implementing a second workflow engine.
- Do not change the meaning of existing phases. Store guided-session state separately from the production phase, or introduce a tested database migration if new durable tables are needed.
- Continue to load legacy SQLite state through the existing non-destructive copy migration. Preserve previous artifact paths and approval digests.
- Keep old audit artifact names readable. New report revisions should be additive and the latest artifacts should remain accessible through `report`.
- Preserve `Finding` JSON compatibility by adding optional fields/defaults rather than making old finding payloads invalid.
- Keep Playwright optional and continue a clearly labeled source-only audit when it is absent.
- Keep the current same-origin URL restriction and filtered Codex snapshot behavior.

## 10. Implementation risks

- Page readiness is application-specific; fixed delays can create false evidence. Readiness must be bounded, configurable, and recorded.
- Route enumeration or clicking can trigger state changes. Initial route discovery should be static and browser navigation restricted to known same-origin paths; destructive controls must not be activated.
- DOM/style inventories can be large or include sensitive UI text. Store only bounded structural/style data, redact likely secrets, and never send it externally without the existing explicit Codex flag.
- Contrast and token correlation can be wrong for opacity, gradients, images, overlays, and inherited styles. Mark computed pairs with provenance and refuse unsupported pass/fail claims.
- SQLite metadata-only expansion avoids schema migration but risks unvalidated blobs. If tables are added, migrate and test existing databases.
- A guided CLI can accidentally conflate continue with approval. Every approval must still pass through the existing human confirmation and artifact-bound authorization methods.
- External Codex calls remain account- and model-dependent. Unit tests must use deterministic mock backends and reports must expose unavailable passes.

## 11. Verification strategy

1. Preserve the existing unit suite as the baseline; add focused tests for route/component mapping, token extraction, screenshot evidence metadata, browser diagnostics, coverage status, instruction persistence, and guide continuation.
2. Use a static multi-screen fixture with no package scripts for deterministic discovery and source tests.
3. Serve the static fixture through a controlled local test server, then use the installed Playwright runtime if Chromium launches. Verify 1440, 768, and 390 captures plus DOM/style/error metadata. Never run fixture package scripts.
4. Use mocked `AgentBackend` responses to verify multi-pass prompts, malformed response handling, evidence binding, and missing-browser degradation without paid model calls.
5. Exercise a complete guided discovery/audit/review/pause/resume/end path. Assert that continuing cannot create or apply approvals.
6. Run `python -m unittest`, compilation, CLI help, package build/install smoke checks, and `git diff --check`. Report any environmental browser limitation distinctly from application defects.

## 12. Initial implementation plan

The first vertical slice will make project structure and rendered evidence substantially richer, produce additive architecture/screen/design-system artifacts, and add a persistent guided audit loop. It will continue attaching to an explicit URL rather than executing discovered project scripts. A server-manager adapter and broad route interaction crawler remain follow-up work until their command-authorization and process-ownership boundaries are fully testable.

## 13. Implementation progress and verified boundary

This section records the implementation that followed the baseline assessment; sections 1–12 describe the original system and its root causes.

### Shipped in this enhancement

- Added a deterministic architecture, route, component/import, styling-value, breakpoint, and runtime inventory in `src/frontend_design_director/intelligence.py`.
- Added route-aware browser evidence capture with the standard/deep/exhaustive viewport profiles, source-discovered static route navigation, full-page PNGs, a JSON screenshot manifest, an HTML contact sheet, readiness signals, DOM landmark/control counts, sampled computed styles, console/page errors, failed requests, and single-run navigation timing.
- Kept dynamic route patterns visible in the route report but excluded them from automatic navigation. Browser collection adds one passive Tab focus screenshot per route when a focusable element is available; application controls remain unactivated.
- Added a human-confirmed local server lifecycle adapter. It uses an argument vector without a shell, loopback readiness checks, filtered environment, redacted logs, and owned-process-group cleanup. This is process lifecycle management, not OS sandbox containment.
- Added deterministic runtime findings for measured document overflow, missing input accessible names, and uncaught page exceptions, each linked to the captured route/viewport screenshot.
- Added separate architecture, screen, component, design-system, color, typography, layout/density, responsive, interaction/behavior, accessibility, performance, executive, application overview, runtime, and coverage reports. The reports mark source definitions, browser observations, Codex image interpretation, and unavailable checks separately.
- Added a screenshot-specific structured visual analysis contract and a second validation pass. Python rejects narrative observations whose route, viewport, or screenshot reference was not supplied to the visual task. The local-only audit does not claim to interpret images.
- Added additive audit revisions, stage-specific and global human-instruction persistence, and `guide` continuation/review/re-audit/pause/resume/end choices. Existing mockup, plan, patch, and implementation approval methods remain the guide's only authorization path.

### Remaining unsupported or partial capabilities

- Route discovery uses framework-neutral static heuristics plus local HTML links. It does not interrogate every framework router at runtime, crawl arbitrary links, synthesize dynamic parameters, or bypass authentication.
- Browser capture observes inert DOM and one passive first-Tab focus state per route when a focusable element exists. It does not activate application controls, test end-to-end user journeys, inspect screen readers, compare light/dark themes, or execute hover/loading/error state exploration.
- Subjective visual analysis requires the opt-in Codex pass. The deterministic color/typography/layout inventories do not infer aesthetic quality or prove that a source token is rendered.
- Accessibility evaluation is partial: accessible-name structure and only unambiguous opaque contrast samples are observed; no axe/ARIA-AT certification, manual screen-reader evaluation, or full WCAG 2.2 AA conformance is claimed.
- Performance output is browser navigation timing from one local run. LCP, INP, CLS, field data, bundle profiling, long-task attribution, and controlled before/after comparisons remain unavailable.
- The development server manager is not a process sandbox and cannot prevent an approved app script from reading other user-accessible files or making its own network calls.
- Browser integration tests require loopback binding and a Chromium executable. In restricted environments the fixture tests skip with an explicit reason; static and state-machine tests remain available. Exact `--route` selections limit capture to the base URL plus those paths; otherwise all source-discovered static candidates are attempted.

Verification on the development host completed all 53 `unittest` tests, including the three loopback/Chromium browser and server-lifecycle tests, with no skips. The wheel built and installed into an isolated temporary target, and the installed module CLI help ran successfully. No external Codex model call or target project script was run as part of that verification.
