# Collaboration and provider boundaries

The director records a task-specific team plan, independent contributions, challenges, evidence references, and Director dispositions in session artifacts and the SQLite decision ledger. Reports are advisory: specialists cannot approve a design direction, mockup, implementation plan, or patch.

## Modes

`audit --collaboration focused|comprehensive|exhaustive` controls additional collaboration. The resumable guide accepts the same option; it defaults to comprehensive and persists the selected mode for later phases and session resume. The established technical, behavioral, and rendered-visual audit passes remain required for audit coverage. Comprehensive adds an independent cross-disciplinary challenge pass. Exhaustive may run one targeted investigation when the challenge round finds a material, evidence-backed dispute.

When Codex is explicitly enabled, mockup generation and implementation planning receive independent phase-specific review. The approved implementation is still generated in its isolated snapshot and reviewed as a patch excerpt before it becomes available for human review. Applying that patch remains a separate explicit approval. Verification commands remain user-supplied and individually confirmed; model review is separately opt-in:

```bash
frontend-director verify --project /path/to/frontend --command "npm test" --codex-review
```

Review artifacts are available through `report collaboration`, `report collaboration-plan`, and phase reports such as `report collaboration-mockup`, `report collaboration-planning`, `report collaboration-implementation`, and `report collaboration-verification`.

## Preferred design contributors

For rendered design audits, planning, mockups, implementation of an approved visual direction, and visual verification, discovery proactively considers Impeccable and the canonical Taste Skill `design-taste-frontend`. Comprehensive and exhaustive design work select both when the active provider can make the bounded role calls; focused work limits preferred design participation to one contributor. Framework and security constraints, screenshots, user configuration, provider authorization, and human approval gates remain controlling. Technical implementation tasks are not automatically treated as visual work.

The current Codex adapter uses an explicitly labeled `skill_guided_role` fallback: it reads a size-limited, sanitized excerpt from the installed `SKILL.md` and sends it with the evidence to a read-only structured role call. Native plugin execution, slash-command execution, Taste scripts, hooks, initialization, and installation are not implied or run by this fallback. The contribution record includes its invocation method, skill path and content fingerprint, whether the guidance was attached, screenshot references, validated output status, and the fact that no native plugin was invoked. Successful file discovery alone does not count as specialist participation.

The audit plan and `preferred-design-expertise.json` artifact distinguish installed skill files from provider callability and native plugin state. It lists the benefits and provider-specific remediation command when either skill or a documented workflow is missing. Taste's app-screen inspector is reported separately from its art-direction fallback; marketing-page guidance is not applied to dashboard screens. Native installations and command lists are reported only when observed in local metadata; version is omitted unless it is verifiable from frontmatter or a provider plugin manifest.

Preferred contributors can be disabled without changing other collaborators in `~/.config/frontend-design-director/config.toml` or the target project's `.frontend-design-director/config.toml`:

```toml
[design_expertise]
enabled = true
prefer_impeccable = true
prefer_taste_skill = true
independent_contributions = true
cross_review = true
recommend_missing = true
recommend_updates = true
auto_install = false
require_user_approval = true
```

Per-tool overrides are available as `[design_expertise.impeccable] enabled = false` or `[design_expertise.taste_skill] enabled = false`. Project settings override user settings. Discovery and readiness checks never install third-party resources or enable hooks.

## Discovery and execution

- Codex skills, custom agents, plugins, and MCP configuration are represented as distinct resources. Skill and agent metadata is read without executing their instructions. Installed custom agent definitions are not reported as callable native subagents because this CLI uses documented role-based `codex exec` calls and does not claim named-agent delegation.
- Codex role availability requires an installed CLI, verified ChatGPT plan sign-in, and structured-output support. Configured MCP servers are not considered callable until a supported probe confirms their tools; this release does not probe or invoke them.
- Claude Code skills, subagent definitions, plugins, and MCP configuration are discovered as metadata. They are not interchangeable with Codex formats. Claude is considered callable only after its installed CLI documents every required invocation flag and authentication, print-mode, and JSON-schema checks pass. Its adapter is read-only, disables MCP servers, and is used only as an audit reviewer when explicitly enabled with `audit --allow-secondary-provider claude --codex` or the equivalent guided-session option.
- Implementation-phase restrictions are attached to each provider role request and passed through the adapter. The current Claude adapter remains read-only and explicitly disallows Bash, Edit, and Write; it is not an implementation backend. If a future authorized phase uses Claude for implementation-related review, the adapter receives the same no-RTK policy, while provider-controlled shell execution is not claimed as fully blocked.
- A standalone audit's secondary-provider authorization applies only to that audit. The guided workflow persists its explicit secondary-provider setting with its resumable session. Discovery, a saved login, an installed plugin, or a project MCP configuration does not authorize source transfer or execution.
- Project-local skills, agent definitions, plugins, hooks, and MCP configuration remain untrusted metadata during discovery. They are excluded from filtered model snapshots. Human review and explicit provider flags are required before relevant data leaves the local workflow.
- Capability selection records callable status, prerequisites, trust, framework fit, excluded resources, and coverage gaps. Role-based calls are independent task prompts; they are not claims of native subagent orchestration.
- Contributions and challenges must cite supplied evidence references. Invalid references or schema responses are rejected and retained as limitations. Disagreements are adjudicated from evidence, not by vote. Exhaustive follow-up is bounded to one targeted call.

Cross-review may identify duplicate finding IDs, but automatic consolidation requires a high-confidence agreement or partial agreement with validated supporting evidence. The retained finding preserves combined evidence and scope; disagreement, uncited proposals, and lower-confidence proposals never merge findings.

See [SECURITY.md](SECURITY.md) for the project data-sharing and approval boundaries, and [CODEX_INTEGRATION.md](CODEX_INTEGRATION.md) for the existing Codex invocation details.
