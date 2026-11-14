# Collaborative Intelligence Gap Analysis

## Existing orchestration architecture

`FrontendDesignDirector` owns the workflow state machine and delegates work to focused modules. Discovery is implemented in `discovery.py`, browser evidence in `browser.py` and `intelligence.py`, audit coordination in `auditing.py`, report generation in `reporting.py`, and durable workflow state in `storage.py`. The SQLite store already persists findings, artifacts, decisions, executions, and artifact-bound human approvals.

## Capability discovery behavior

Discovery reads project metadata and manifests, classifies supported frontend frameworks, collects filtered source facts, and discovers skill metadata and Codex TOML agent definitions. Skill discovery reads only bounded frontmatter and does not execute skill instructions. Codex MCP configuration and cached plugin manifests are reported, but an MCP definition is not treated as callable without a connection probe. Claude Code resources were not previously represented.

The existing `Capability` model is an audit-facing readiness summary, not a normalized registry of skills, agents, plugins, MCP servers, model roles, and local tools. Keyword matching classifies a skill's likely domain, but does not make that skill an executable specialist.

## Current agent execution model

`run_codex_audit` uses three fixed role prompts: technical, behavioral, and visual. The code and UX roles each run a first pass and a same-role verification pass. Visual analysis uses route-specific screenshot review and synthesis. All model execution is through the `AgentBackend` protocol; the production implementation invokes `codex exec` with a constrained JSON Schema, read-only sandbox, and attached image paths.

Discovered Codex custom agent definitions are not selected or invoked by name. The existing pipeline performs role-based specialist execution, not verified native subagent delegation. Other phases such as mockup generation and implementation planning use a single role-specific Codex call.

## Current synthesis and decision process

The audit validates findings, source paths, line numbers, screenshot references, and visual route/viewport coverage. Findings are merged with deterministic source and browser observations. Audit completion gates check required browser and specialist evidence. Human design, mockup, implementation, and patch approvals are persisted separately and remain authoritative.

Specialist assessments are retained, but there is no normalized contribution contract, structured cross-disciplinary challenge record, task-specific recruitment plan, or durable Director adjudication ledger. SQLite decisions are already suitable for storing concise collaboration decisions without a database migration.

## Missing coordination capabilities

- A unified registry distinguishing resource kind, provider, installation/configuration, trust, compatibility, and verified callability.
- Claude Code discovery and a provider adapter.
- Selection rationale and collaboration intensity controls.
- Separation of provider discovery from authorization to send project evidence.
- Structured challenges, targeted follow-up, and Director decisions.
- Persistent provenance linking selected experts, evidence, contributions, and decisions.
- Collaboration plans applied consistently to substantive workflow phases.

## Provider-specific limits and current environment

The installed Codex CLI is 0.167.1. Its `exec` interface supports a JSON Schema output file, image inputs, sandbox selection, and the current backend's role-based calls. Custom Codex agent files can be discovered, but this orchestrator has no verified named-agent execution interface; the implementation must not claim native delegation.

Claude Code 2.1.308 is installed and reports `loggedIn: false`. Its current CLI help exposes print mode, JSON output, `--json-schema`, `--agent`, explicit tool selection, permission modes, and strict MCP configuration. Capability discovery now reads a bounded 20 KB help excerpt because the complete current help places several supported flags beyond the former 4 KB probe limit. A read-only provider adapter is implemented, but this machine cannot verify an authenticated model call. Claude use therefore remains unavailable until authentication and explicit secondary-provider authorization are present.

Codex custom agents, Claude subagents, skills, plugins, and MCP integrations have provider-specific semantics. The adapters must not treat their metadata formats or execution behavior as interchangeable. Useful references: [Codex CLI](https://developers.openai.com/codex/cli), [Claude Code custom subagents](https://docs.anthropic.com/en/docs/claude-code/sub-agents), [Claude Code skills](https://docs.anthropic.com/en/docs/claude-code/skills), [Claude Code MCP](https://docs.anthropic.com/en/docs/claude-code/mcp), and [Claude Code plugins](https://docs.anthropic.com/en/docs/claude-code/plugins).

## Risks of dynamic delegation

- Discovered skill and agent instructions are untrusted input and may contain prompt injection or unsafe tool requests.
- A secondary provider is a separate data-sharing boundary; installation or authentication does not grant permission to transmit source or screenshots.
- MCP configuration is not proof that a server is healthy or that its tools are relevant.
- Running many specialists can amplify cost, quota pressure, duplicate claims, and anchoring.
- Parallel browser navigation can invalidate evidence if specialists share one browser context.
- Model consensus does not replace evidence validation or human approval.

## Recommended architecture and implementation plan

1. Keep `FrontendDesignDirector` as the workflow owner and preserve the existing store and approval model.
2. Add a compact normalized capability and task-selection layer. Skills provide metadata hints; agents and providers are executable only through verified adapters.
3. Add provider-specific discovery. Codex remains the default model backend; Claude is opt-in, read-only, schema-constrained, and denied MCP access by default.
4. Assemble a task-specific team from evidence needs, project framework, resource status, trust, and the selected collaboration mode. Explain excluded resources as well as selected roles.
5. Preserve independent audit roles and add structured cross-review only where the configured mode and budget justify it.
6. Validate contribution and challenge references against the filtered source snapshot and attached screenshots before adjudication.
7. Record the plan, provider provenance, specialist outcomes, challenges, and concise Director decisions through the existing SQLite decision/event/artifact APIs.
8. Continue to enforce the existing approval gates for design directions, mockups, implementation scope, and patch application.

## Relevant files

- `src/frontend_design_director/discovery.py`: project, skill, Codex agent, CLI, plugin, and MCP discovery.
- `src/frontend_design_director/codex_backend.py`: current schema-constrained Codex CLI adapter.
- `src/frontend_design_director/auditing.py`: specialist prompts, independent passes, screenshot validation, and audit result.
- `src/frontend_design_director/director.py`: workflow coordination and persistence.
- `src/frontend_design_director/cli.py`: user-facing audit options.
- `src/frontend_design_director/storage.py`: SQLite session, decision, artifact, execution, and approval persistence.
- `src/frontend_design_director/state_machine.py`: phase transitions.

## Backward-compatibility requirements

Keep existing CLI syntax and behavior unless a new optional flag is supplied. Keep the current Codex backend protocol, audit report fields, database schema, and serialized session metadata readable. Default secondary-provider sharing to disabled. Preserve exact-path scope validation, temporary Git implementation workspaces, and human approval requirements.

## Verification strategy

Use deterministic tests for provider metadata parsing, status distinctions, expert selection, collaboration modes, contribution/challenge validation, refusal of unauthorized cross-provider execution, decision persistence, and human approval invariants. Run the existing test suite with the repository source on `PYTHONPATH`. Keep real provider tests separate from normal tests and do not make a paid model call without an explicit user-facing authorization path. The benchmark audit must continue to use only `demo-app/`; private evaluator files are for post-run comparison only.
