---
name: frontend-design-director
description: Run the persistent local Python frontend discovery, rendered-evidence audit, human-guided design review, isolated mockup, and separately authorized implementation workflow.
---

# Frontend Design Director

Use the Python CLI as the workflow owner. Its SQLite state machine and artifact-bound approval records are authoritative; do not substitute conversational state for persisted approvals. It coordinates human-approved design direction separately from implementation authorization.

## Start or resume a guided session

```bash
frontend-director guide --project /path/to/project --depth deep --codex
```

The guide offers discovery as the recommended first action, but users can enter a later phase directly with a clear instruction. It preserves optional human instructions, supports review and re-audit, and remains active until the human pauses or explicitly enters `end`. On a later Codex turn, run the same command or specify the persisted session ID with `--session`. No input or a closed terminal leaves a resumable pending decision.

## Direction, mockup, and phase overrides

A design direction is a structured JSON specification stored as `artifact_type: design_direction`. It is not an HTML page, preview, or mockup. Do not create HTML presentations or seed a mockup generator with generic direction scaffolding. The mockup generator starts from the approved direction and creates an actual interface in its isolated workspace; its manifest must identify the artifact as `mockup` and reference the exact direction digest. New mockups require an explicit `--codex` call or an explicitly supplied existing interface. An imported interface still requires mockup review.

The CLI and guided natural-language interface share the Director's phase override controller. For example:

```bash
frontend-director phase --project /path/to/project --session SESSION_ID --to mockup --reason "Use the approved direction"
frontend-director mockup --project /path/to/project --session SESSION_ID --codex
frontend-director phase --project /path/to/project --session SESSION_ID --to planning --reason "Reuse this mockup" --mockup-dir /path/to/mockup
```

Clear instructions such as `skip the audit and go straight to mockup`, `go back to design direction`, or `use my existing mockup and move to implementation planning` are honored when essential artifacts are available. Missing optional audit context is recorded. Overrides do not create approvals: mockups still require human review, implementation requires approval of the exact current plan, patch application remains separate, and verification requires an applied patch.

Choose the audit depth deliberately:

- `standard`: desktop and mobile captures.
- `deep` (default): 1440, 768, and 390 pixel captures.
- `exhaustive`: 1920, 1440, 1280, 768, 390, and 320 pixel captures.

## Browser and project execution boundary

- Without a URL, discovery/audit inspect source and produce deterministic architecture, route, component, color, typography, spacing, and coverage reports. They do not establish actual appearance.
- `--url http://127.0.0.1:PORT` attaches to a human-managed server. Browser requests are restricted to the approved origin and GET, HEAD, or OPTIONS. Remote origins require explicit human authorization through `--allow-remote`.
- By default, browser capture visits the supplied base URL and source-discovered static routes. If one or more exact `--route` paths are supplied, capture is limited to the base URL and those paths. Dynamic parameters are never invented. It captures one passive Tab focus state when available; it does not activate controls, submit forms, change settings, or claim unobserved states.
- To let the orchestrator start the app, supply an exact `--start-command` and loopback `--server-url`. It requests a TTY confirmation phrase, invokes an argument vector without a shell in a restricted environment, performs bounded HTTP readiness checks, records redacted logs, and terminates only its owned process group. The child process is not an OS sandbox; approve only commands you trust.
- `--codex` explicitly sends a filtered source snapshot and captured screenshots to the locally installed Codex CLI, using saved ChatGPT sign-in and account plan usage. No OpenAI API key is required. Without `--codex`, screenshots are preserved for human review, but no semantic vision analysis is claimed.
- Visual reasoning, when enabled, is a structured JSON pass bound to exact screenshot references and viewport labels, followed by a screenshot evidence verification pass. Reports distinguish model interpretation, deterministic browser observations, static source evidence, and missing verification.

## Audit artifacts

Review `reports/audit-index.md` first. Reports include independent technical, behavioral, visual, accessibility, performance, responsive, color, typography, layout/density, route, architecture, component, and coverage views. The screenshot manifest and local contact sheet are under `evidence/`. Re-audits preserve prior revisions in `reports/audits/audit-NNN/`.

Read `coverage-and-limitations.md` before drawing conclusions. The browser pass does not perform complete keyboard/assistive-technology testing, automated WCAG certification, field Web Vitals measurement, or interaction-state crawling. Never claim an area passed if it was not checked.

## Preferred design expertise

During discovery, inspect the `preferred_design_expertise` section in the capability inventory. The Director proactively considers Impeccable and Taste Skill (`design-taste-frontend`) for rendered visual audits, design direction, mockups, approved visual implementation, and design verification. Comprehensive and exhaustive design work should use both as separate contributors when the active provider role and required evidence are available. Their contributions are advisory; the Director preserves disagreements and human approval remains authoritative.

Check the `preferred-design-expertise.json` report and `collaboration.preferred_design_review` before describing tool participation. `skill_guided_role` means a bounded excerpt from an installed `SKILL.md` was supplied to a read-only structured Codex role; it does not mean a native plugin or script ran. A discovered or cached installation is not the same as an enabled plugin. If a tool or Taste's documented app-screen inspector is missing, unavailable, or disabled, state the exact status and show the provider-specific recommended installation/update action. Never run third-party installers, initialization commands, scripts, or hooks; do not enable hooks. Consult the [Impeccable documentation](https://impeccable.style/docs/) and [Taste Skill documentation](https://www.tasteskill.dev/docs) for provider-specific setup.

## Approval boundaries

- Discovery and audit never authorize a design change.
- Visual direction, behavior direction, and scope are selected independently.
- Direction approval permits mockup exploration only.
- Mockup approval does not authorize production implementation.
- Implementation-plan approval authorizes Codex only to create a patch in the isolated snapshot and within the reviewed exact file scope.
- Patch application is a separate explicit human decision.
- Verification commands are supplied by the human and individually confirmed.
- An agent-generated message, a user's `continue`, absence of input, or a completed audit cycle is not approval or workflow termination.

## Implementation command policy

RTK is intentionally disabled during implementation, patch application, and verification after a patch is applied. Use the native command directly:

```bash
frontend-director implement --project /path/to/project --session SESSION_ID --json
```

Do not wrap this command with `rtk`. The orchestrator rejects direct RTK executable launches from its controlled command runner, adds a temporary PATH denial shim to implementation subprocesses, and sends an explicit restriction to implementation specialists and the Codex backend. This does not control an already-running parent wrapper, nor can PATH-based protection prevent an independent provider shell from using an absolute RTK path or shell alias/function. Do not claim those cases are technically blocked.

## Execution discipline and recovery

Use session reports, artifact references, and recorded operation results before repeating repository or workflow inspection. Give each command a clear purpose. After a failure, inspect its captured exit status and stderr, classify the cause, and do not repeat it unchanged or guess alternative syntax. Correct the command from the documented interface, or wait for the existing recorded operation; do not launch a duplicate planner or poll for the same unchanged state. Transient provider retries are bounded. Permission, quota, invalid-schema, invalid-command, and missing-artifact failures require a changed condition before another attempt. If recovery cannot proceed safely, preserve the partial work and report the blocker. Use `frontend-director status --json` to inspect the persisted operation summary; do not edit SQLite workflow state directly.

Invoke Frontend Design Director commands, all JSON-producing commands, Codex or Claude calls, arbitrary Python, state changes, and commands where complete diagnostics matter directly, without `rtk`. RTK may be used only for supported read-only repository inspection when its transformed output is sufficient. The orchestrator's application-controlled subprocesses do not add RTK automatically. Parent wrappers and external agents with independent shell tools remain outside complete process-level control.

Use `review` to list current artifacts, `instructions` to persist multiline stage-specific guidance (finish with `END INSTRUCTIONS`), `re-audit` to add a revision without discarding prior reports, `pause` to persist the current decision, and `end` only for explicit session termination. Guidance entered while a plan or patch is awaiting approval does not change that plan or patch. Never bypass CLI approval gates or modify target files outside the approved patch workflow.
