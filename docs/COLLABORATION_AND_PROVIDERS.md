# Collaboration and provider boundaries

The director records a task-specific team plan, independent contributions, challenges, evidence references, and Director dispositions in session artifacts and the SQLite decision ledger. Reports are advisory: specialists cannot approve a design direction, mockup, implementation plan, or patch.

## Modes

`audit --collaboration focused|comprehensive|exhaustive` controls additional collaboration. The resumable guide accepts the same option; it defaults to comprehensive and persists the selected mode for later phases and session resume. The established technical, behavioral, and rendered-visual audit passes remain required for audit coverage. Comprehensive adds an independent cross-disciplinary challenge pass. Exhaustive may run one targeted investigation when the challenge round finds a material, evidence-backed dispute.

When Codex is explicitly enabled, mockup generation and implementation planning receive independent phase-specific review. The approved implementation is still generated in its isolated snapshot and reviewed as a patch excerpt before it becomes available for human review. Applying that patch remains a separate explicit approval. Verification commands remain user-supplied and individually confirmed; model review is separately opt-in:

```bash
frontend-director verify --project /path/to/frontend --command "npm test" --codex-review
```

Review artifacts are available through `report collaboration`, `report collaboration-plan`, and phase reports such as `report collaboration-mockup`, `report collaboration-planning`, `report collaboration-implementation`, and `report collaboration-verification`.

## Discovery and execution

- Codex skills, custom agents, plugins, and MCP configuration are represented as distinct resources. Skill and agent metadata is read without executing their instructions. Installed custom agent definitions are not reported as callable native subagents because this CLI uses documented role-based `codex exec` calls and does not claim named-agent delegation.
- Codex role availability requires an installed CLI, verified ChatGPT plan sign-in, and structured-output support. Configured MCP servers are not considered callable until a supported probe confirms their tools; this release does not probe or invoke them.
- Claude Code skills, subagent definitions, plugins, and MCP configuration are discovered as metadata. They are not interchangeable with Codex formats. Claude is considered callable only after its installed CLI documents every required invocation flag and authentication, print-mode, and JSON-schema checks pass. Its adapter is read-only, disables MCP servers, and is used only as an audit reviewer when explicitly enabled with `audit --allow-secondary-provider claude --codex` or the equivalent guided-session option.
- A standalone audit's secondary-provider authorization applies only to that audit. The guided workflow persists its explicit secondary-provider setting with its resumable session. Discovery, a saved login, an installed plugin, or a project MCP configuration does not authorize source transfer or execution.
- Project-local skills, agent definitions, plugins, hooks, and MCP configuration remain untrusted metadata during discovery. They are excluded from filtered model snapshots. Human review and explicit provider flags are required before relevant data leaves the local workflow.
- Capability selection records callable status, prerequisites, trust, framework fit, excluded resources, and coverage gaps. Role-based calls are independent task prompts; they are not claims of native subagent orchestration.
- Contributions and challenges must cite supplied evidence references. Invalid references or schema responses are rejected and retained as limitations. Disagreements are adjudicated from evidence, not by vote. Exhaustive follow-up is bounded to one targeted call.

See [SECURITY.md](SECURITY.md) for the project data-sharing and approval boundaries, and [CODEX_INTEGRATION.md](CODEX_INTEGRATION.md) for the existing Codex invocation details.
