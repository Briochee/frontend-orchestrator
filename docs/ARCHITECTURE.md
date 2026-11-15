# Architecture

## Runtime boundaries

The package is standard-library-first. `argparse` exposes the CLI, `sqlite3` is the canonical workflow-state owner, and JSON/JSON Schema contracts move data between the coordinator and the optional Codex CLI adapter. Playwright is an optional dependency used only when the user supplies a URL.

```text
CLI
 └─ FrontendDesignDirector
    ├─ Discovery: project manifests, documented skill paths, custom-agent TOML, Codex config/cache
    ├─ Audit: architecture/route/component/style inventory + optional rendered browser evidence + optional Codex specialists
    ├─ Evidence: route/viewport screenshots, DOM structure, computed styles, browser errors, navigation timing, contact sheet
    ├─ Reports: separate technical/behavioral/visual outputs + coverage, color, typography, layout, responsive, and component inventories
    ├─ Consultation: separate human visual, behavioral, and scope decisions
    ├─ Mockups: isolated static artifacts + human revision loop
    ├─ Implementation planning: exact existing/new file paths + baseline hashes
    ├─ Isolated Codex execution: filtered temporary Git snapshot -> patch artifact
    └─ Patch application and verification: exact scope + hash checks -> report
```

The Python coordinator, not Codex, owns phase transitions and structured approval records. Specialist agents return findings; the coordinator validates them before persistence. An agent response cannot change a SQLite approval or count as human confirmation.

## Codex resource installation

The Python distribution and its copied Codex resources have separate update lifecycles. `pipx install --force --editable PATH` refreshes the CLI from a selected checkout; `update-codex` synchronizes the skill and agent files bundled inside the currently running distribution. Resource identity is content-based, not package-version-only.

The installer classifies each expected file using its bundled SHA-256, current installed SHA-256, and prior manifest hash. It updates missing files and unchanged managed files; it reports and preserves modified or untracked legacy files unless `--force` is supplied. Force only affects the exact bundled skill path and `frontend-*.toml` agent paths, creates a unique backup first, stages replacements beside their destination, and atomically replaces files. The v2 manifest records scope, destination, resource hash, and ownership; v1 hash manifests are normalized and migrated on the next write. Uninstall removes only managed files that still match their recorded hash.

`doctor` reads package distribution metadata and PEP 610 editable-source metadata when present, compares those with the active module and optional expected checkout, and hashes each expected Codex file against the active package resources. It does not modify the package, resource files, or manifest.

## State machine

The active path is:

```text
INITIALIZED -> DISCOVERING -> CAPABILITIES_REVIEW -> AUDITING -> AUDIT_COMPLETED
  -> AWAITING_DIRECTION -> DIRECTION_APPROVED -> GENERATING_MOCKUPS
  -> AWAITING_MOCKUP_REVIEW -> MOCKUP_APPROVED -> AWAITING_IMPLEMENTATION_APPROVAL
  -> IMPLEMENTING -> PATCH_READY -> APPLYING -> VERIFYING -> COMPLETED
```

`PAUSED`, `FAILED`, and `CANCELLED` preserve interruption and failure state. `state_machine.py` contains the explicit transition map. Invalid transitions raise before the state row changes.

The SQLite database stores sessions, phase events, findings, user decisions, approvals, artifact hashes, and agent execution outcomes. Reports and prototypes are files under the session state directory; SQLite records their paths, versions, and SHA-256 digests. Approval validity is checked against the current artifact digest each time a gated action runs.

## Discovery and audit

Discovery reads JSON/TOML manifests, skill frontmatter, agent TOML fields, Codex MCP config names, and local plugin manifests. For the two preferred design skills, it also records bounded content fingerprints, provider-manifest versions when verifiable, command/script names, hook presence, and Taste app-inspector prerequisites. It never runs an installed tool. A locally cached manifest does not prove a plugin is installed, enabled, or callable.

The deterministic audit scans source for a small set of evidence-backed signals. It does not launch a build, development server, dependency manager, project script, or test. Reports keep technical, behavioral/accessibility, and visual findings separate. The visual report explicitly says the visual audit is incomplete when screenshot evidence or a visual evaluator is absent.

The deterministic intelligence pass maps framework-neutral static route candidates, file/module components, local imports, project structure, CSS custom properties, color literals, font families/sizes/line heights, repeated dimensions, and media-query breakpoints. These values are labeled as source-defined until corroborated by sampled browser-computed styles. Static route candidates without dynamic parameters are navigated automatically when a browser URL is explicitly supplied. Supplying one or more exact `--route` paths limits the capture to the base route and those paths. Dynamic patterns are listed but never instantiated. A passive first-Tab focus state is captured when available; UI controls are not activated.

Depth profiles select viewport sets: standard uses 1440 and 390; deep uses 1440, 768, and 390; exhaustive uses 1920, 1440, 1280, 768, 390, and 320. Each route/viewport creates a full-page capture and bounded metadata for document dimensions, landmarks, controls and accessible-name signals, sampled computed styles, console/page errors, failed requests, readiness, and navigation timing. Only same-origin GET/HEAD/OPTIONS browser requests are allowed. A local HTML gallery is created. Deterministic findings are limited to objective observations such as width overflow, uncaught errors, and missing input names; they do not interpret subjective composition.

When an authorized `--start-command` and loopback readiness URL are supplied, `server.py` asks the CLI for interactive confirmation, runs the argument vector without a shell under a filtered environment, uses bounded HTTP readiness checks, captures redacted output, and stops only the process group it started. This does not provide OS-level containment for the target script. Attaching to a user-managed server remains available through `--url`.

With `--codex`, the coordinator creates a temporary Git snapshot containing bounded text source and configuration files. It skips `.git`, `.agents`, `.codex`, project instruction files, common generated directories, symlinks, non-text assets, credential-like filenames, and files matching selected common secret patterns. Codex receives only that snapshot and explicitly captured screenshots. Technical, behavioral, and visual specialists run independent structured passes and evidence cross-validation. The visual schema requires a screenshot-grounded design identity, route/viewport assessments, strengths, concerns, consistency patterns, and preserve/refine/human-decision recommendations; references must match screenshots supplied to that task. JSON Schema constrains each role's final result. Without `--codex`, screenshots remain human-reviewable evidence and no subjective image interpretation is claimed.

The capability registry keeps skills, agents, plugins, MCP servers, provider roles, and deterministic local tools distinct. A discovered definition is not treated as executable. The selector records phase fit, provider and trust status, selected roles, supporting metadata hints, exclusions, and gaps. Impeccable and Taste Skill are preferred design roles for design-related tasks; when a human-authorized Codex role is selected, it may receive a bounded sanitized excerpt of the installed skill as advisory context. This `skill_guided_role` fallback is not native plugin execution. Missing or incomplete tools produce provider-specific recommendations, and user/project settings can disable either contributor. Role-based Codex/Claude calls do not claim native subagent delegation. Specialist contributions and challenges must cite artifact references supplied to that call; the Director records non-voting dispositions in the existing SQLite decision ledger.

Reports are generated from inventories and findings with explicit evidence boundaries. They include an index, executive/application summaries, architecture and screen maps, component/design system inventories, separate color/typography/layout/responsive/accessibility/performance/interaction views, runtime evidence, and coverage/limitations. Re-audits store versioned copies under `reports/audits/audit-NNN/` while stable latest-report artifact names remain available.

## Human direction and mockups

Visual direction, interaction direction, and scope are independent decisions. A direction approval is bound to the digest of `design-direction.json`. Mockups are versioned under `mockups/revision-NNN/`; prior revisions remain available. The built-in renderer produces static HTML/CSS/tokens and labels its sample content and colors as illustrative. `mockup --codex` optionally refines the prototype in a temporary workspace with only the mockup files as writable outputs, then requests phase-appropriate read-only review of its artifacts and rendered mockup screenshots.

Mockup approval writes a formal implementation specification. It does not authorize production changes. The implementation plan records exact paths, reasons, change classes, and SHA-256 baselines for existing files. The human then approves that exact plan digest and scope.

## Controlled implementation

`implement` copies the filtered target into a temporary Git repository, checks that approved files still match their planned baseline, and asks Codex to edit only the approved exact paths. The adapter rejects unexpected changed paths, symlinks, or non-file outputs. It creates a Git patch but does not modify the target project. A read-only specialist pass receives a bounded patch excerpt and approved scope; its results are advisory and cannot create either implementation or patch-application approval.

`apply` requires a separate human confirmation. It validates the patch digest and file list, compares current target hashes with the plan baselines, runs `git apply --check`, then applies the patch. Unrelated user changes outside the approved file set are preserved. If a planned target file changes while implementation runs, application is blocked and the user must produce a new plan.

## Verification

The coordinator never runs commands found in project manifests. `verify --command ...` runs only exact commands supplied by the human and requires interactive confirmation. It invokes commands without a shell, rejects shell operators, applies a timeout, and records command name/status/exit code/duration without persisting raw output. A separate `--codex-review` opt-in sends only the verification summary and approved file scope for independent review. A report marks visual, accessibility, and performance work `not verified` unless a corresponding check actually ran.

## Guided continuity

`guide` composes the existing director methods and does not create a parallel approval engine. Discovery and read-only audit run as safe stages; at human boundaries the guide stores a pending action, offers review/instruction/re-audit/pause/end options, and returns without polling or consuming model calls when input ends. Global and stage-specific human instructions append to SQLite metadata with source/timestamp; they do not become approvals. A completed improvement cycle remains resumable and offers a new cycle. `continue` only advances ordinary workflow; implementation authorization and patch application still require TTY confirmation phrases bound to exact artifact/scope digests.

## Module map

- `models.py`, `storage.py`, `state_machine.py`: schemas, SQLite ownership, phase validation.
- `discovery.py`, `snapshot.py`: metadata-only environment inspection and filtered Codex snapshots.
- `intelligence.py`: static route/component/design-value inventories, runtime finding conversion, and architecture/system reports.
- `auditing.py`, `reporting.py`, `browser.py`: specialist contracts, findings, screenshot capture/diagnostics, and audit artifacts.
- `server.py`, `guided.py`: explicitly confirmed local-server lifecycle and persistent interactive stage routing.
- `codex_backend.py`: non-interactive local Codex adapter with saved ChatGPT auth, sandbox mode, JSON Schema, and API-key environment stripping.
- `mockups.py`: responsive static template, optional isolated Codex refinement, and path validation.
- `implementation.py`: plans, baseline hashes, isolated patches, scope enforcement, and guarded application.
- `verification.py`, `logging_setup.py`: explicit user-selected checks and bounded local JSONL logs.
- `director.py`, `cli.py`: orchestration service, CLI gates, content-aware Codex resource install/update, manifest migration, and installation diagnostics.
