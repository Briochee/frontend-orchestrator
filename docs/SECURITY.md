# Security and limitations

## Trust model

The target repository, discovered skill metadata, project documentation, screenshots, agent output, and Codex output are untrusted data. Discovery reads metadata and source only. It does not execute project instructions, install tools, start the application, or make network requests.

Skill discovery reads only a small frontmatter prefix and never executes a skill. Agent discovery parses TOML fields but does not execute agent instructions. MCP and plugin states are reported conservatively: configured or cached is not the same as callable. Discovery remains metadata-only and makes no network requests.

## Codex and ChatGPT plan usage

Codex runs are opt-in (`audit --codex`, `mockup --codex`, `plan --codex`, or an approved `implement`). They use the installed `codex exec` command and saved ChatGPT sign-in. The adapter passes Codex a small environment allowlist, removes API-key and Git redirection variables, and requires login status to report ChatGPT authentication. It does not require an API key and does not support API-key billing.

An opt-in model call sends the included filtered text files, prompt, and any attached screenshots to the Codex service under the signed-in account. Do not use Codex mode for repositories or screenshots that must remain local. Static analysis and deterministic browser evidence remain local; no subjective screenshot interpretation is claimed without the explicit Codex visual pass.

The adapter uses the read-only sandbox for auditing and planning. Mockup generation and implementation use workspace-write only inside a temporary mockup workspace or filtered temporary Git snapshot. It does not request danger-full-access or configure broader permissions. Codex custom agents inherit their parent's permissions; agent instructions alone cannot sandbox them.

## Filesystem and patch scope

- Snapshot creation omits symlinks, Git metadata, `.agents`, `.codex`, project instruction files, common dependency/build/cache directories, non-text files, environment/credential files, and selected recognizable secret patterns.
- Snapshots are temporary and removed after a Codex call. They have file-count, per-file, and total-size limits.
- The implementation plan uses exact relative paths and file hashes. Credential paths, traversal, protected directories, duplicate paths, and symlinks are rejected.
- Codex implementation changes only a scratch copy. An out-of-scope change prevents patch creation. A patch is only an artifact until the human reviews and applies it.
- Before applying, the coordinator verifies the patch digest, file list, approved scope, target file hashes, and `git apply --check` result.
- Git subprocesses discard inherited `GIT_*` redirection variables and user/system Git configuration before operating in the selected temporary or target directory.
- A process with direct filesystem access can still alter the local SQLite database or artifacts. This tool assumes the host user account and the local project are trusted; it does not cryptographically attest human identity.

## Approval gates

Interactive commands require a TTY and an exact typed phrase. The CLI has no `--yes` or agent-provided approval flag. Human confirmations are persisted with session, type, artifact digest, exact scope, timestamp, and linked decision IDs. Updating an artifact or plan invalidates approvals bound to the old digest.

The approval model protects actions performed through this orchestrator. It cannot prevent a separate process or a human from directly editing project files outside the tool.

## Browser access

Screenshot capture is disabled unless the user provides a URL. By default only loopback hosts are accepted. Remote access requires `--allow-remote`; browser requests are restricted to the explicitly approved origin and GET/HEAD/OPTIONS. Static route candidates are visited by default; when exact `--route` values are supplied, they limit capture to the base URL and those paths. Dynamic route patterns are not invented. One passive Tab focus state is captured when possible; the browser does not activate controls or submit forms. Authentication workflows and storage-state reuse are not automated. Screenshots and bounded DOM/style metadata are kept in the local session artifact directory and sent to Codex only if the human also selects `--codex`.

An optional `--start-command` requires an interactive typed approval and a loopback HTTP readiness URL. The command is parsed to an argument vector, launched with `shell=False` and a filtered environment, logged with common secret patterns redacted, and stopped by the process group owned by the orchestrator. Duplicate servers at the selected URL are not started. **This lifecycle manager is not an OS sandbox.** The target process may still read files available to the user account or access the network; approve only a command you trust. Starting a project server never implies permission to install packages or modify manifests.

## Verification and logs

No manifest command or discovered shell script is run automatically. Verification commands are supplied by the user, passed without a shell, and require a separate confirmation. Raw subprocess output is discarded rather than written to workflow logs.

Local activity and request logs are JSON Lines under `.agents/frontend-design-director/logs/`. Active files rotate at approximately 10,000 lines. Logs omit common credential-key names and redact common token patterns; avoid placing sensitive values in user-provided command arguments because process listings may expose them on the host.

## Known limits

- Source-level audits can produce false positives and cannot verify runtime behavior or rendered appearance.
- Secret filtering covers common patterns, not every proprietary identifier or credential format. Review the snapshot boundary before opting into Codex.
- Browser evidence covers the supplied base URL, statically discovered non-dynamic route candidates by default, or the operator's exact route selection, and the selected viewport profile. A passive first-Tab focus state may be captured. Other interactive states, authenticated routes, themes, and cross-browser rendering are not automatically exercised.
- Browser navigation timing is a single-run lab observation. No LCP, INP, CLS, bundle-size, main-thread profile, or comparable before/after score is fabricated.
- Deterministic source and DOM inventories use framework-neutral heuristics. They can miss generated routes/components and cannot establish that every source-defined design token is used.
- Automated label and limited opaque-color contrast samples do not constitute complete keyboard, screen-reader, zoom/reflow, or WCAG 2.2 AA verification.
- Patch application requires Git tooling even though discovery and static reports can run in a non-Git directory.
