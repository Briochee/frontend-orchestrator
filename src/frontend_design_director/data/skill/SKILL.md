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

The guide discovers the project, proposes the next action, preserves optional human instructions, supports review and re-audit, and remains active until the human pauses or explicitly enters `end`. On a later Codex turn, run the same command or specify the persisted session ID with `--session`. No input or a closed terminal leaves a resumable pending decision.

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

Use `review` to list current artifacts, `instructions` to persist multiline stage-specific guidance (finish with `END INSTRUCTIONS`), `re-audit` to add a revision without discarding prior reports, `pause` to persist the current decision, and `end` only for explicit session termination. Guidance entered while a plan or patch is awaiting approval does not change that plan or patch. Never bypass CLI approval gates or modify target files outside the approved patch workflow.
