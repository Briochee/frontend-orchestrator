# Complete example workflow

This walkthrough uses `examples/sample-frontend/`, a static HTML/CSS fixture. It demonstrates the full state flow. Audit, direction, and manual planning work without Codex. Creating a new interface mockup requires an explicit `--codex` opt-in; an existing interface can instead be supplied for review.

## 1. Install and inspect

From the orchestrator checkout:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
frontend-director init examples/sample-frontend --title "Sample dashboard review"
```

Capture the session ID printed by `init`, or let subsequent commands select the latest session for the project.

```bash
frontend-director discover --project examples/sample-frontend
frontend-director status --project examples/sample-frontend
```

Discovery reads the HTML, CSS, and manifest metadata. It does not run an application command.

## 2. Produce and review audits

The source-only version runs without a browser or specialist skills. It produces an architecture map, route/screen and component inventories, design-system values, coverage limitations, and independent technical, behavior, and visual reports:

```bash
frontend-director audit --project examples/sample-frontend
frontend-director report technical-audit --project examples/sample-frontend
frontend-director report behavioral-audit --project examples/sample-frontend
frontend-director report visual-audit --project examples/sample-frontend
frontend-director report audit-summary --project examples/sample-frontend
frontend-director report audit-index --project examples/sample-frontend
frontend-director report component-inventory --project examples/sample-frontend
frontend-director report design-system-analysis --project examples/sample-frontend
frontend-director report coverage-and-limitations --project examples/sample-frontend
```

The fixture includes a literal image without alternative text, so source inspection can report that evidence. The visual report must say that appearance was not audited when screenshots are absent.

For rendered evidence, either start the fixture yourself in a second terminal:

```bash
python -m http.server 8080 --bind 127.0.0.1 --directory examples/sample-frontend
```

Or authorize the exact local fixture-server command for this audit:

```bash
frontend-director audit --project examples/sample-frontend \
  --start-command "python3 -m http.server 8080 --bind 127.0.0.1" \
  --server-url http://127.0.0.1:8080/ --depth exhaustive --codex
```

The CLI asks for `RUN PROJECT SERVER` before it runs the command, launches without a shell, waits for HTTP readiness, captures source-discovered static routes at six viewport widths, and terminates only its own process group. This is not an OS sandbox. Screenshots and their JSON index are stored beneath `.agents/frontend-design-director/evidence/`. `--codex` asks the signed-in visual specialist to inspect those images and emit structured analysis whose route/viewport citations are validated; without it, visual interpretation remains for human review. The fixture has one static page, so route breadth is intentionally small.

## Guided alternative

To have the CLI retain the next step and resume the conversation later, use:

```bash
frontend-director guide --project examples/sample-frontend \
  --start-command "python3 -m http.server 8080 --bind 127.0.0.1" \
  --server-url http://127.0.0.1:8080/ --depth deep --codex
```

At the initial prompt, choose `continue` to follow the recommended discovery-first workflow, or give a clear phase instruction. The guide asks for `RUN PROJECT SERVER` when the audit stage begins. After the audit, `continue` opens separate visual, behavior, and scope choices and then asks `CONFIRM DIRECTION`. After mockup generation, choose `approve mockup` or `revise mockup`; that decision does not authorize implementation. Continuing from an approved mockup prepares an exact-path plan. The guide requires a separate typed implementation authorization, produces a patch in an isolated snapshot, and asks again before applying it to the fixture. Verification is an explicit choice and any commands are confirmed before running. After the cycle, choose `new audit`, `review`, `pause`, or `end`; ending is the only action that marks the guided session ended.

To test recovery, press Ctrl-D at any non-approval prompt, then rerun the same `guide --project ...` command. The current phase and pending action remain in SQLite; no interrupted prompt is treated as approval.

## 3. Choose design direction

After reviewing the summary, select independent visual, behavior, and scope directions. The command prints them and requires the human to type `CONFIRM DIRECTION` in the terminal.

```bash
frontend-director direction --project examples/sample-frontend --visual refine --behavior preserve --scope screens --constraints "Preserve the current task list and navigation order. Improve hierarchy and mobile spacing."
```

This does not approve implementation.

To start with known project context, explicitly enter the direction phase first. The user still chooses and confirms the direction:

```bash
frontend-director phase --project examples/sample-frontend --to direction --reason "I already know the intended direction"
frontend-director direction --project examples/sample-frontend --visual refine --behavior preserve --scope screens --constraints "Preserve the current task list and navigation order."
```

## 4. Generate and review a mockup

Create an actual responsive interface from the approved direction in a fresh isolated workspace:

```bash
frontend-director phase --project examples/sample-frontend --to mockup --reason "Generate the approved direction"
frontend-director mockup --project examples/sample-frontend --brief-file examples/sample-frontend/README.md --codex
```

The output is stored beneath `.agents/frontend-design-director/mockups/revision-001/`. Open `index.html` in a browser or serve the artifact directory to inspect it. The direction JSON is passed directly to the mockup generator; no HTML direction page or generic seed scaffold is produced. The generator must return an interface-shaped document, responsive styles, tokens, and a summary before the mockup can be reviewed.

To use an existing interface instead, import its directory. It must contain `index.html` and `styles.css`; import does not approve the mockup:

```bash
frontend-director phase --project examples/sample-frontend --to planning --reason "Reuse the existing screen" --mockup-dir /path/to/mockup
```

The workflow pauses at mockup review. Approve the mockup before preparing an implementation plan.

Approve, request a revision, or reject. The confirmation phrase is displayed by the CLI.

```bash
frontend-director mockup-review approve --project examples/sample-frontend
frontend-director report implementation-spec-md --project examples/sample-frontend
```

Mockup approval creates a formal specification but still does not authorize code changes.

## 5. Plan and authorize implementation

For a model-generated plan, use `--codex`; for a hand-selected exact scope, pass each path explicitly:

```bash
frontend-director plan --project examples/sample-frontend --file index.html --file styles.css
frontend-director report implementation-plan-md --project examples/sample-frontend
frontend-director approve-implementation --project examples/sample-frontend
```

The approval prompt displays the exact path list and plan digest. No implementation starts until the human types the requested authorization phrase.

## 6. Generate, inspect, and apply the patch

```bash
frontend-director implement --project examples/sample-frontend
frontend-director status --project examples/sample-frontend
frontend-director apply --project examples/sample-frontend
```

`implement` writes only inside a temporary filtered Git repository. The patch is an artifact until `apply` verifies the approved file set and confirms that target files still match their planned hashes. `apply` asks for a separate human confirmation.

## 7. Verify and report

The fixture provides a deterministic standard-library test command. Verification is not run until the human confirms the exact command:

```bash
frontend-director verify --project examples/sample-frontend --command "python3 -m unittest discover -s tests"
frontend-director report final-report --project examples/sample-frontend
```

The report separates applied paths, approved scope, command outcomes, and remaining unverified visual, accessibility, and performance work. Read `coverage-and-limitations.md`: browser capture is not interaction automation, screenshots do not imply design analysis without the visual Codex pass, and navigation timing is a lab sample rather than field Web Vitals.
