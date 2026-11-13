# Codex integration

## Supported interfaces used

The implementation was checked against the installed Codex CLI and current OpenAI documentation on [non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode), [custom subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents), [skills](https://learn.chatgpt.com/docs/build-skills), and the [configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference).

- **Execution:** `codex exec` is the documented non-interactive CLI. The adapter uses `--ephemeral`, `--ignore-user-config`, `--cd`, a restricted sandbox, `--output-schema`, and `--output-last-message`.
- **Authentication:** `codex exec` reuses saved CLI authentication. The adapter requires ChatGPT sign-in and removes API-key environment variables, so model work uses the signed-in ChatGPT plan rather than API-key billing.
- **Model:** defaults to `gpt-6-luna` with `model_reasoning_effort="xhigh"`. Response verbosity defaults to `high`; reasoning summary defaults to `detailed`. The user can override these settings. Model availability is account-specific.
- **JSON contracts:** every role receives a JSON Schema for its final response. Python validates the returned JSON again before storing findings or plans.
- **Sandbox:** audit and plan calls use `read-only`; mockup and implementation calls use `workspace-write` only in a temporary isolated repository. The adapter never selects `danger-full-access`.
- **Custom agents:** standalone TOML definitions live in package resources under `src/frontend_design_director/data/agents/`. `install-agents` installs missing files and reports existing resource status. `--upgrade` refreshes unchanged managed files; `--force` backs up and replaces differences at the exact bundled agent paths. Custom agents inherit the parent's sandbox and tools; instructions cannot grant human approval or independent permission boundaries.
- **Skills:** local discovery follows documented `.agents/skills/`, `~/.agents/skills/`, `/etc/codex/skills/`, and installed Codex locations. It reads only the metadata prefix. The skill is bundled as a package resource. `install-skill` supports the same content-aware update and backup rules at `PATH/.agents/skills/frontend-design-director/SKILL.md`.
- **MCP and plugins:** configured MCP server names and local plugin manifests can be observed. The initial implementation does not call MCP tools or query remote plugin catalogs. It does not claim that a cached plugin is enabled or callable without a documented probe.

## Deliberately isolated adapter

The Python interface is `CodexCLIBackend.execute(...)`. It accepts a working directory, a role-specific instruction, a JSON Schema, a sandbox mode, and optional screenshot paths. It fails clearly when Codex is missing, ChatGPT sign-in is unavailable, the process times out, or output does not match the requested schema.

The adapter does not depend on undocumented Codex APIs, app-server protocols, or plugin invocation behavior. Browser, model, and other agent runtimes can be added behind the same bounded interface after their supported interfaces are verified.

## Optional Codex configuration

Install the complete integration with one command after installing the Python package:

```bash
frontend-director install-codex --scope project --project /path/to/frontend
```

Use `--scope user` to install the skill and agents for the current user across projects. Project scope writes to `.agents/skills/frontend-design-director/SKILL.md` and `.codex/agents/*.toml`; user scope writes the skill to `~/.agents/skills/frontend-design-director/SKILL.md` and agents to `~/.codex/agents/*.toml`, or `<CODEX_HOME>/agents/*.toml` when `CODEX_HOME` is set. Installation compares file hashes and records managed resource hashes in a schema-versioned manifest. It never assumes that file existence means the installed version is current.

Synchronize an existing install without overwriting locally edited or legacy files:

```bash
frontend-director update-codex --scope user
```

For explicitly authorized replacement of those exact package resource paths, use `--force`. It creates a unique backup before writing; a backup failure aborts the replacement. `install-codex --upgrade` is equivalent to a safe synchronization. Both scopes use the same path resolver and manifest. `frontend-director doctor` checks package/distribution versions, editable source metadata where available, Codex paths, manifest state, and installed-versus-bundled resource hashes without writing files. Start a new Codex session after updating the files. The commands copy documented resources directly; they do not invoke an undocumented Codex installer API or alter Codex configuration.

Remove an installation using the same scope:

```bash
frontend-director uninstall-codex --scope project --project /path/to/frontend
frontend-director uninstall-codex --scope user
```

The uninstall command requires an interactive `UNINSTALL CODEX` confirmation unless `--yes` is supplied. It uses the install manifest to remove only unchanged files marked as installer-managed; it preserves pre-existing, modified, unmanaged, and backup files. It accepts the previous v1 manifest format and migrates it on the next install/update. If `CODEX_HOME` was set for a user-scope installation, use the same value when uninstalling. This removes the Codex integration, not the Python package or target project's saved workflow artifacts. Remove the Python package separately with `pipx uninstall frontend-design-director` or, inside its virtual environment, `python -m pip uninstall frontend-design-director`.

To expose the bundled role files to an existing target project, run:

```bash
frontend-director install-agents --project /path/to/frontend
```

Existing files are classified by content. The installer creates no MCP configuration, enables no plugin, and does not alter the user's global Codex configuration outside the selected install paths and manifest.

To invoke the workflow from Codex, install the bundled skill into the target project or call `frontend-director guide --project PATH --depth deep --codex`. The guide's SQLite state and pending action remain authoritative across Codex turns. Read `audit-index.md` and the relevant evidence-backed reports, summarize the important next decision, and continue from the stored phase when the user replies.

The visual specialist receives the captured PNG files through the documented `codex exec --image` argument and a strict schema for screenshot-grounded design identity, strengths, concerns, cross-screen consistency, responsive route/viewport readings, and preserve/refine/human-decision options. Python checks every narrative observation against the screenshots passed to that invocation. If browser evidence or the Codex visual pass is unavailable, report that gap and do not infer appearance from CSS.

Never turn user continuation into approval. Design direction, mockup approval, exact implementation-plan authorization, patch application, and project-command verification remain independent interactive CLI gates. Agent text is not approval, and the guide ends only after an explicit human end action.
