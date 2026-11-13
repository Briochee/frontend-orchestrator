# Setup and local execution

## Supported environment

- Python **3.11 or newer**.
- macOS, Linux, or Windows with Python and Git on `PATH`.
- Git is required for Codex snapshot initialization and guarded patch generation. Static discovery and source-based audits do not require Git.
- No runtime package dependency and no API key are required.
- The Codex backend requires the Codex CLI, a ChatGPT sign-in, and account access to the configured model. It does not use `OPENAI_API_KEY` or `CODEX_API_KEY`.
- Browser screenshots are optional and require Playwright plus its Chromium browser. The orchestrator will not install either automatically.

## Install from a checkout

```bash
git clone <repository-url>
cd frontend-orchestrator
python3.11 -m venv .venv
```

Activate the virtual environment:

```bash
# macOS or Linux
source .venv/bin/activate
```

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Install the package and command:

```bash
python -m pip install -e .
frontend-director --help
```

## Install the Codex integration

Once the CLI is installed, install both the workflow skill and specialist agent definitions with one command. For one project:

```bash
frontend-director install-codex --scope project --project /path/to/frontend
```

For the current Codex user across projects:

```bash
frontend-director install-codex --scope user
```

The project scope writes under `.agents/skills/frontend-design-director/` and `.codex/agents/`. The user scope writes under `~/.agents/skills/frontend-design-director/` and `~/.codex/agents/`; when `CODEX_HOME` is set, user-scope agent files go to `<CODEX_HOME>/agents/`. The installer compares content hashes, reports current, outdated, modified, untracked, missing, and invalid resources, and records managed files in a versioned manifest. It preserves local modifications unless `--force` is supplied. Open a new Codex session after installation. The command uses documented file discovery locations and does not modify Codex configuration or make a model call.

## Update or repair an installation

The Python CLI and its copied Codex files are updated separately. From the source checkout, refresh the pipx environment from that exact local path:

```bash
cd /path/to/frontend-orchestrator
pipx install --force --editable .
```

`pipx install --editable .` may report that the package is already installed and leave pipx's environment metadata and entry point untouched. If that existing install is already editable from this checkout, Python source edits are normally visible immediately; the message by itself does not reveal the install mode or source path. `frontend-director doctor --expected-source .` reports the mode and path when available. The `--force --editable .` command is supported by pipx and explicitly reinstalls from the current checkout, refreshing package metadata and entry points as well. It does not publish the package or require an API key. Do not use `pipx upgrade frontend-design-director` to switch an installation to a different local checkout; refresh from the path with the command above.

Synchronize user-level Codex files with the active package:

```bash
frontend-director update-codex --scope user
frontend-director doctor --expected-source .
```

Normal synchronization replaces only unchanged managed resources. Locally modified and untracked files are preserved and reported with an actionable next step. To intentionally replace those recognized skill/agent paths, use the explicit `--force` flag:

```bash
frontend-director update-codex --scope user --force
frontend-director doctor --expected-source .
```

`--force` is the documented non-interactive confirmation. Every differing target file is copied to a unique timestamped `.bak` file before replacement; backups are not removed by uninstall. The force option only applies to the exact bundled skill and `frontend-*.toml` agent destinations. It does not follow symbolic links or overwrite other directory contents. For project scope, add `--scope project --project /path/to/frontend` to both commands. `doctor` is read-only and reports package metadata, editable source, executable path, effective `CODEX_HOME`, manifest health, and per-file hashes. It detects this checkout as the expected source when run from the repository root; `--expected-source` can be set explicitly from another directory.

The v2 manifest migrates the prior v1 hash manifest when an install/update runs. It retains ownership only for resources the installer previously recorded or files explicitly created/replaced by the installer. Existing legacy files that were never managed remain unowned unless explicitly replaced with `--force`; uninstallation preserves them.

## Uninstall

Remove the Codex files created by the installer with the corresponding scope:

```bash
frontend-director uninstall-codex --scope project --project /path/to/frontend
frontend-director uninstall-codex --scope user
```

The command requires typing `UNINSTALL CODEX` in an interactive terminal; `--yes` skips that prompt for a deliberate scripted invocation. It removes only files listed in the ownership manifest that still match their install-time hashes. It preserves pre-existing, modified, symbolic-link, and non-file entries. Installs made before ownership manifests were introduced are treated as unmanaged and are left untouched. When a custom `CODEX_HOME` was used for user-scope agents, set the same value for uninstall.

The command removes the Codex skill/agent integration, not the Python distribution or workflow data. Remove the package separately:

```bash
# If installed globally with pipx
pipx uninstall frontend-design-director

# If installed in a project virtual environment, activate it first
python -m pip uninstall frontend-design-director
```

Workflow state and artifacts in the target project's `.agents/frontend-design-director/` are retained.

To install the CLI for the user without a per-project virtual environment, install [`pipx`](https://pipx.pypa.io/stable/how-to/install-pipx.html) using your platform's package manager, then run `pipx install --force --editable /path/to/frontend-orchestrator`. Run `frontend-director install-codex --scope user` for a first install or `frontend-director update-codex --scope user` to synchronize copied resources afterward.

Install development dependencies when running the pytest suite:

```bash
python -m pip install -e '.[dev]'
python -m pytest
```

The standard-library unittest suite can run without pytest:

```bash
python -m unittest discover -s tests -v
```

## Optional browser setup

Review this optional install before running it. It installs the Python package and downloads a Chromium browser binary. The [official Playwright Python installation guide](https://playwright.dev/python/docs/intro) documents the package setup, and the [browser guide](https://playwright.dev/python/docs/browsers) describes the separate browser download:

```bash
python -m pip install -e '.[browser]'
python -m playwright install chromium
```

Run a source and browser-based audit against an application you started yourself:

```bash
frontend-director audit --project /path/to/frontend --url http://127.0.0.1:5173
```

This visits the base URL and statically discovered non-dynamic route candidates at the selected depth profile. Supplying one or more `--route /path` values restricts capture to the base URL and those exact paths. Dynamic route patterns are never guessed. Or start one exact command through an interactive approval:

```bash
frontend-director audit --project /path/to/frontend \
  --start-command "npm run dev -- --host 127.0.0.1" \
  --server-url http://127.0.0.1:5173/ --depth deep
```

The CLI asks for `RUN PROJECT SERVER`. It invokes the parsed argument vector without a shell, waits for bounded HTTP readiness, captures redacted output, and stops only its own process group. This is not an OS sandbox; authorize only project commands you trust. Neither option installs dependencies. Add `--codex` to have the signed-in Codex service interpret the filtered source and screenshots using plan usage.

The default depth is `deep`: 1440×1000 desktop, 768×1024 tablet, and 390×844 mobile. `standard` uses desktop/mobile; `exhaustive` adds 1920, 1280, and 320 pixel widths. Browser requests to the approved origin are restricted to GET/HEAD/OPTIONS. Remote page capture requires the explicit `--allow-remote` flag. Authentication flows, browser storage reuse, and interaction-state activation are not automated.

## Codex sign-in and model settings

Install and sign in to Codex separately using its official installer and `codex login`. Choose ChatGPT sign-in. Confirm availability with:

```bash
codex --version
codex login status
```

The backend reuses this saved login and removes `CODEX_API_KEY` and `OPENAI_API_KEY` from its child-process environment. It refuses API-key auth and does not ask for a key. Default model settings are GPT-6 Luna, xhigh reasoning, high verbosity, and detailed reasoning summaries. Override the settings before a command:

```bash
frontend-director --model gpt-6-luna --reasoning-effort xhigh --verbosity high --summary detailed audit --project /path/to/frontend --codex
```

If the signed-in account cannot use the selected model or reasoning effort, Codex returns an error; the orchestrator does not silently switch models.

## Version checks

The CLI version is available with `frontend-director --version`. Normal commands check the [GitHub Releases API](https://github.com/Briochee/frontend-orchestrator/releases) for a newer stable version, then fall back to the version declaration in the repository's `main` branch. This sends only a version metadata request and never installs updates. An available update is reported on stderr; offline or unavailable sources are ignored so the requested workflow can continue. Skip the check for an invocation with `frontend-director --no-update-check audit --project /path/to/frontend`.

## Session artifacts

`frontend-director init /path/to/frontend` creates `.agents/frontend-design-director/` in that project. This contains `workflow.sqlite3`, reports, mockup revisions, screenshots, approvals, logs, and patches. The directory is private to the user where supported by filesystem permissions and should not be committed. Add this specific ignore rule to the target project only after reviewing its existing `.gitignore`; do not ignore all of `.agents/`, since it can contain Codex skills:

```gitignore
.agents/frontend-design-director/
```

The orchestrator never edits a target project's ignore file automatically.

## Verification

Run orchestrator checks from this repository:

```bash
python -m compileall -q src tests
python -m unittest discover -s tests -v
python -m frontend_design_director --help
```

To run an optional target-project command, supply it explicitly after implementation and patch application:

```bash
frontend-director verify --project /path/to/frontend --command "npm test"
```

The CLI requires an interactive confirmation before executing any supplied command. Use one command invocation per `--command`; shell operators and shell expansion are not used.

For optional automated accessibility rules, a project that already runs browser checks can evaluate [axe-core](https://github.com/dequelabs/axe-core). It overlaps automated semantic and WCAG checks but does not replace keyboard, screen-reader, or manual review. The orchestrator does not install or execute axe-core.
