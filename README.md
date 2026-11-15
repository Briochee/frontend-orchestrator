# Frontend Design Director

`frontend-design-director` is a Python 3.11+ workflow orchestrator for discovering frontend capabilities, producing evidence-linked audits, collecting independent design decisions, generating responsive mockups, and applying implementation patches only after explicit human approval.

## Installation

Install the Python CLI from this checkout, then install its skill and specialist agents into Codex's documented discovery directories. No npm publication, OpenAI API key, or Codex configuration edit is required. Open a new Codex session after installation so it can discover the files.

### Global installation for all projects

With `pipx` installed, run from this repository. The editable install keeps the global CLI linked to this checkout while you develop:

```bash
pipx install --force --editable .
frontend-director install-codex --scope user
```

This makes `frontend-director` available as a user-level CLI and installs the workflow skill in `~/.agents/skills/frontend-design-director/` and the specialist agents in `~/.codex/agents/`. If `CODEX_HOME` is set, agents are installed in `<CODEX_HOME>/agents/` instead.

If pipx is not installed, follow the [official pipx installation guide](https://pipx.pypa.io/stable/how-to/install-pipx.html). If pipx reports its application directory is missing from `PATH`, run `pipx ensurepath` and open a new terminal before using `frontend-director`.

### Project-specific installation

From the target project, create and activate a virtual environment, install this checkout, then install the Codex files into the project:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -e /path/to/frontend-orchestrator
frontend-director install-codex --scope project --project .
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`. Project installation places the skill in `.agents/skills/frontend-design-director/` and the specialist agents in `.codex/agents/`.

`install-codex` installs both integrations. The separate `install-skill` and `install-agents` commands remain available. The command only copies bundled files to the selected Codex discovery paths; it does not install plugins, enable MCP servers, or make model calls.

### Updating and checking installation health

Refresh the Python CLI from this local checkout, synchronize the Codex skill and agents, then check package and resource status:

```bash
cd /path/to/frontend-orchestrator
pipx install --force --editable .
frontend-director update-codex --scope user --force
frontend-director doctor --expected-source .
```

The `pipx` command refreshes the Python distribution and executable from this checkout. `update-codex` compares each installed file with the bundled SHA-256 hash. It updates unchanged files owned by an earlier install, and `--force` explicitly authorizes replacing differences at the exact Frontend Design Director skill and agent paths. Before replacement, it creates a unique `.bak.<timestamp>.<id>` copy and reports its path. Use `frontend-director update-codex --scope user` without `--force` to update managed files while preserving local modifications and untracked legacy files. The project equivalent is `frontend-director update-codex --scope project --project /path/to/frontend`; scopes do not overlap.

`frontend-director doctor` is read-only. It reports Python/distribution versions, editable source path when available, active executable and module paths, Codex availability, the effective Codex directories, manifest status, per-resource hashes, and recommended commands. When run from this checkout, it detects the current repository as the expected source; use `--expected-source /path/to/frontend-orchestrator` when running elsewhere. Codex skill and agent files are copied resources, so updating the Python CLI alone does not synchronize them. Open a new Codex session after a successful integration update.

### Uninstall

Remove the Codex skill and specialist agents installed by this tool:

```bash
# Current project
frontend-director uninstall-codex --scope project --project /path/to/frontend

# Current user's Codex environment
frontend-director uninstall-codex --scope user
```

The command asks you to type `UNINSTALL CODEX` unless you pass `--yes` for a scripted run. It removes only unchanged files marked as managed in the install manifest. Pre-existing, manually copied, and subsequently modified files are preserved. Backups made by forced updates are retained. If user-scope agents were installed with a custom `CODEX_HOME`, run the uninstall with that same `CODEX_HOME` value. Older installs without a manifest are left untouched because the installer cannot establish ownership safely.

The Python package is removed separately after the Codex files. For a global `pipx` install, run `pipx uninstall frontend-design-director`; for a project virtual environment, activate it and run `python -m pip uninstall frontend-design-director`. Uninstalling the Codex files does not delete workflow state or project artifacts under `.agents/frontend-design-director/`.

After opening a new Codex session, ask: “Use the `frontend-design-director` skill to discover this frontend and stop so I can review the capability report.”

It uses the installed Codex CLI when you opt in. Codex CLI reuses saved ChatGPT sign-in, so the default setup does not require an OpenAI API key. Model calls use the user's ChatGPT plan usage. The defaults are **GPT-6 Luna**, **xhigh** reasoning, **high** verbosity, and a **detailed** reasoning summary; all four are configurable. Codex requests use JSON Schema output.

## Version checks

The current version is **0.3.0** (`frontend-director --version`), defined once in the package and reused for build metadata. Each normal CLI command makes a best-effort check for a newer stable version using the [GitHub Releases API](https://github.com/Briochee/frontend-orchestrator/releases). If no release is available, it checks the version declaration in the repository's `main` branch. The check sends only a version metadata request; it does not send project files, Codex credentials, or API keys. It never installs an update automatically. When a newer version is found, the CLI prints a notice to stderr and leaves the command's normal or JSON output unchanged. Offline or unavailable update sources do not block work. Skip the network check for one command with `frontend-director --no-update-check audit --project /path/to/frontend`.

## Safety boundary

Inspection, design, and implementation have separate controls:

1. `discover` reads project metadata and installed capability metadata.
2. `audit` is local and source-based by default. `--codex` explicitly sends a filtered source snapshot to the signed-in Codex service. `--url` explicitly captures a running application; remote URLs require `--allow-remote`.
3. `direction` requires a human decision for visual appearance, behavior, and scope independently.
4. `mockup` writes static HTML/CSS into `.agents/frontend-design-director/`, isolated from production files. The built-in template works without Codex; `--codex` is optional.
5. `mockup-review approve` approves the prototype only.
6. `plan` records exact file paths. `approve-implementation` is a separate human gate.
7. `implement` writes changes in a filtered temporary Git snapshot and returns a patch. `apply` requires a second human review and checks current target file hashes before applying.
8. `verify` runs only commands the human explicitly supplies; it never runs package scripts merely because they appear in a manifest.

Custom Codex agents cannot approve a direction, mockup, implementation plan, or patch. Their permissions are inherited from the parent Codex run; their instructions are not a permission boundary.

## Quick start

Run these commands from a terminal. Human approval commands require a TTY and a typed confirmation phrase.

```bash
frontend-director init /path/to/frontend
frontend-director discover --project /path/to/frontend
frontend-director audit --project /path/to/frontend
frontend-director report audit-summary --project /path/to/frontend
```

To include Codex findings using the signed-in account:

```bash
frontend-director --model gpt-6-luna --reasoning-effort xhigh audit --project /path/to/frontend --codex
```

Audit collaboration defaults to `comprehensive`; use `--collaboration focused` to skip the additional challenge round or `--collaboration exhaustive` to allow one evidence-triggered follow-up. The mode also guides later mockup, planning, and post-approval implementation reviews. Every phase report records selected roles, excluded resources, citations, limitations, challenges, and Director dispositions:

```bash
frontend-director audit --project /path/to/frontend --codex --collaboration exhaustive
frontend-director report collaboration --project /path/to/frontend
frontend-director report collaboration-planning --project /path/to/frontend
```

Claude Code capabilities can be discovered without executing them. Sharing an audit snapshot with Claude requires explicit per-audit authorization and a verified login:

```bash
frontend-director audit --project /path/to/frontend --codex --allow-secondary-provider claude
```

Verification review is also opt-in because it sends command summaries and applied file scope to Codex:

```bash
frontend-director verify --project /path/to/frontend --command "npm test" --codex-review
```

See [docs/COLLABORATION_AND_PROVIDERS.md](docs/COLLABORATION_AND_PROVIDERS.md) for the provider status model, review boundaries, and artifact names.

The audit can capture a running local application at the required desktop, tablet, and mobile sizes when Playwright is installed:

```bash
frontend-director audit --project /path/to/frontend --url http://127.0.0.1:5173 --codex
```

Application controls remain passive by default. For a locally served page, `--exercise-safe-interactions` opts into reversible probes of the first eligible text edit, search, range, switch, and read-only details control per route. The isolated browser context is discarded after probes; all HTTP and WebSocket requests after page readiness are blocked. Probes never submit forms or activate save/delete/archive/confirmation actions. Remote pages are not probed. The behavioral report separates tested observations from source-based inference:

```bash
frontend-director audit --project /path/to/frontend --url http://127.0.0.1:5173 --codex --exercise-safe-interactions
```

After reviewing the separate technical, behavior, and visual reports, proceed through the decision and prototype gates:

```bash
frontend-director direction --project /path/to/frontend --visual refine --behavior improve --scope screens
frontend-director mockup --project /path/to/frontend --brief-file design-brief.md --codex
frontend-director mockup-review approve --project /path/to/frontend
frontend-director plan --project /path/to/frontend --codex
frontend-director report implementation-plan-md --project /path/to/frontend
frontend-director approve-implementation --project /path/to/frontend
frontend-director implement --project /path/to/frontend
frontend-director apply --project /path/to/frontend
frontend-director verify --project /path/to/frontend --command "npm test"
frontend-director report final-report --project /path/to/frontend
```

The commands are separate so the human can inspect each artifact before advancing. Do not use `--codex` if the project or screenshot content must remain local.

## Guided deep review

Use `guide` when you want the director to keep the session moving, retain instructions, and resume after a terminal closes. It discovers first, then pauses at the capability review. At each phase it proposes safe next steps, supports report review and re-auditing, and waits without consuming model calls when it needs human input.

```bash
frontend-director guide --project /path/to/frontend --depth deep --codex
```

To include rendered evidence, either start the project yourself and attach to its loopback URL, or provide the exact local command and readiness URL for a per-run interactive approval:

```bash
# Attach to a server you started yourself.
frontend-director guide --project /path/to/frontend --url http://127.0.0.1:5173 --depth exhaustive --codex

# Or approve one exact server command in the terminal.
frontend-director guide --project /path/to/frontend \
  --start-command "npm run dev -- --host 127.0.0.1" \
  --server-url http://127.0.0.1:5173/ --depth deep --codex
```

The server command is parsed into an argument vector and is not run through a shell. The guide asks for `RUN PROJECT SERVER`, checks HTTP readiness, captures only same-origin read-only browser requests, and stops only the process group it started. The server process is not an OS sandbox; only authorize project scripts you trust. By default the browser visits the base URL plus all statically discovered, non-dynamic routes. Supplying one or more `--route` options limits capture to the base URL and those exact paths. Dynamic parameters are not synthesized. Unreachable/authenticated routes remain uncovered.

After screenshots are collected, `--codex` explicitly sends the filtered source snapshot and screenshots to the signed-in Codex service for screenshot-backed specialist analysis using the user's plan. Without it, deterministic inventories and objective browser observations are still produced, but screenshots are not semantically interpreted by a vision evaluator. The default is deep: 1440×1000, 768×1024, and 390×844. Exhaustive adds 1920, 1280, and 320 pixel widths. The browser captures one passive Tab focus state per route when possible; it does not activate application controls, and other interaction states remain unverified.

The guided session remains open at decision points. Use `instructions` to save multiline guidance (finish with `END INSTRUCTIONS`), `re-audit` to create a new additive audit revision, `review` to list artifacts, `pause` to persist a pending action, and `end` only when you intend to close the guided session. Resume with the same `guide --project ...` command or `--session <id>`. Continuing never equals design, implementation, or patch approval. Instructions entered while a plan or patch is awaiting approval do not alter that artifact; a revision must be reviewed separately.

The audit writes `reports/audit-index.md`, executive/application summaries, architecture and route maps, component and design-system inventories, separate color/typography/layout/responsive/technical/behavioral/visual/performance/accessibility reports, structured findings, and a coverage/limitations report. Screenshot manifests and a local HTML contact sheet live under `evidence/`. Audit revisions are also retained under `reports/audits/audit-NNN/`.

## Workflow state

Sessions persist in SQLite at `<project>/.agents/frontend-design-director/workflow.sqlite3`. Reports, approvals, findings, mockup revisions, patches, and execution history are also stored beneath `.agents/frontend-design-director/`. Use `status`, `pause`, and `resume` to inspect or continue a session. Existing databases under `.frontend-design-director/` are copied to the new location on first access; the original database is retained.

```bash
frontend-director status --project /path/to/frontend
frontend-director pause --project /path/to/frontend
frontend-director resume --project /path/to/frontend
```

See [docs/SETUP.md](docs/SETUP.md) for optional Playwright and development dependencies, and [docs/CODEX_INTEGRATION.md](docs/CODEX_INTEGRATION.md) for details about the bundled skill and agents.

## Capabilities and limitations

- Static discovery and source analysis work without Codex, Playwright, or specialist skills.
- The visual report says appearance was not audited when rendered evidence is missing. CSS source alone is not used to claim what the user sees.
- Browser capture is optional and uses same-origin GET/HEAD/OPTIONS requests only. Loopback is the default; remote targets require `--allow-remote` and explicit URL selection.
- Source-derived route candidates and their browser rendering are recorded separately. Dynamic routes, protected data states, interaction outcomes, alternate themes, and cross-browser behavior are not automatically fabricated or exercised.
- Deterministic browser rules can report objective signals such as document overflow, uncaught page exceptions, missing input names, and simple contrast pairs. Subjective screenshot analysis requires the explicit `--codex` visual specialist pass.
- Performance output contains single-run local navigation timing only. It does not claim field LCP/INP/CLS, bundle profiling, or comparable before/after results.
- Plugin manifests and MCP config are reported as observed, configured, or cached. The tool does not infer that an integration is callable without an explicit probe.
- Codex source snapshots omit repository instructions, skills, plugins, symlinks, non-text assets, common generated directories, credential files, and likely embedded credentials. The model call still transmits the remaining approved source and screenshots to the signed-in Codex service.
- Implementation uses a temporary Git workspace and only exposes a generated patch after exact-path scope validation. Target files are not modified until `apply` passes hash and patch checks and receives a human confirmation.
- Accessibility and performance claims are marked as measured, static, observed, hypothetical, or unverified. The tool does not fabricate Lighthouse/Web Vitals data.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), [docs/SECURITY.md](docs/SECURITY.md), [docs/CODEX_INTEGRATION.md](docs/CODEX_INTEGRATION.md), and [docs/EXAMPLE_WORKFLOW.md](docs/EXAMPLE_WORKFLOW.md).
