from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from frontend_design_director.collaboration import (
    CapabilityResource,
    CapabilityStatus,
    CollaborationMode,
    ResourceKind,
    SpecialistChallenge,
    TrustLevel,
    adjudicate_challenges,
    assemble_expert_team,
    build_capability_registry,
    run_phase_collaboration,
)
from frontend_design_director.discovery import discover_agents, discover_claude_code, discover_codex
from frontend_design_director.providers import ClaudeCodeBackend
from frontend_design_director.codex_backend import BackendFailure, BackendUnavailable
from frontend_design_director.snapshot import create_project_snapshot
from frontend_design_director.auditing import _run_visual_audit_by_route, run_codex_audit
from frontend_design_director.director import FrontendDesignDirector, _add_rendered_screenshot_evidence
from frontend_design_director.models import AuditType
from frontend_design_director.storage import WorkflowStore


class CapabilityRegistryTests(unittest.TestCase):
    def test_registry_distinguishes_provider_roles_agents_skills_and_unprobed_mcp(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            inventory = build_capability_registry(
                {"root": str(root)},
                [{"name": "web design", "source_path": str(root / ".agents/skills/web/SKILL.md"), "capabilities": ["visual"]}],
                [{"name": "React expert", "source_path": str(root / ".codex/agents/react.toml"), "capabilities": ["frontend"]}],
                {
                    "cli": {"installed": True, "authenticated": True, "auth_mode": "chatgpt_plan", "codex_exec_supported": True, "structured_output_supported": True, "image_input_supported": True, "version": "codex-cli 0.167.1"},
                    "mcp_servers": [{"name": "docs", "configured": True, "enabled": True, "callable": "not_probed"}],
                    "plugins": [{"name": "design-plugin", "installed": True, "configured": False}],
                },
                {"cli": {"installed": True, "authenticated": False, "structured_output_supported": True, "version": "2.1.50"}},
            )
        skill = next(item for item in inventory if item.kind == ResourceKind.SKILL)
        agent = next(item for item in inventory if item.kind == ResourceKind.AGENT and item.provider == "codex")
        mcp = next(item for item in inventory if item.kind == ResourceKind.MCP_SERVER)
        plugin = next(item for item in inventory if item.kind == ResourceKind.PLUGIN)
        codex_role = next(item for item in inventory if item.id == "codex:role:technical_architecture_specialist")
        claude_role = next(item for item in inventory if item.provider == "claude_code" and item.kind == ResourceKind.PROVIDER_ROLE)
        self.assertEqual(skill.status, CapabilityStatus.INSTALLED)
        self.assertFalse(skill.callable)
        self.assertEqual(skill.trust_level, TrustLevel.PROJECT_LOCAL_UNREVIEWED)
        self.assertEqual(agent.status, CapabilityStatus.INSTALLED)
        self.assertFalse(agent.callable)
        self.assertEqual(mcp.status, CapabilityStatus.ENABLED)
        self.assertFalse(mcp.callable)
        self.assertEqual(plugin.status, CapabilityStatus.INSTALLED)
        self.assertFalse(plugin.callable)
        self.assertEqual(codex_role.status, CapabilityStatus.CALLABLE)
        self.assertEqual(claude_role.status, CapabilityStatus.UNAVAILABLE)
        self.assertEqual(agent.trust_level, TrustLevel.PROJECT_LOCAL_UNREVIEWED)

    def test_user_skill_is_not_mislabeled_as_project_local(self) -> None:
        inventory = build_capability_registry(
            {"project_root": "/tmp/frontend-project"},
            [{"name": "user frontend skill", "source_path": "/Users/example/.agents/skills/frontend/SKILL.md", "capabilities": ["frontend"]}],
            [],
            {"cli": {}},
        )
        skill = next(item for item in inventory if item.kind == ResourceKind.SKILL)
        self.assertEqual(skill.trust_level, TrustLevel.LOCAL_UNREVIEWED)

    def test_codex_api_key_authentication_is_not_callable_for_chatgpt_plan_backend(self) -> None:
        inventory = build_capability_registry(
            {"project_root": "/tmp/frontend"}, [], [],
            {"cli": {"installed": True, "authenticated": True, "auth_mode": "api_key", "codex_exec_supported": True, "structured_output_supported": True, "image_input_supported": True}},
        )
        role = next(item for item in inventory if item.id == "codex:role:technical_architecture_specialist")
        self.assertEqual(role.status, CapabilityStatus.UNAVAILABLE)

    def test_selection_respects_framework_and_secondary_provider_authorization(self) -> None:
        def role(resource_id: str, provider: str, status: str, domains: tuple[str, ...], frameworks: tuple[str, ...] = ()):
            return CapabilityResource(
                id=resource_id, name=resource_id, provider=provider, kind=ResourceKind.PROVIDER_ROLE,
                status=CapabilityStatus(status), trust_level=TrustLevel.FIRST_PARTY_INSTALLED,
                capabilities=domains, supported_phases=("audit", "planning", "mockup", "implementation", "verification"), invocation_method="read-only role call",
                supports_images=resource_id.endswith("visual_design_specialist"), framework_compatibility=frameworks,
            )

        inventory = [
            role("codex:role:technical_architecture_specialist", "codex", "callable", ("architecture",), ("React",)),
            role("codex:role:ux_accessibility_specialist", "codex", "callable", ("ux",)),
            role("codex:role:visual_design_specialist", "codex", "callable", ("visual",)),
            role("codex:role:cross_disciplinary_reviewer", "codex", "callable", ("evidence_review",)),
            role("claude_code:role:cross_disciplinary_reviewer", "claude_code", "callable", ("evidence_review",)),
        ]
        plan = assemble_expert_team(
            phase="audit", mode=CollaborationMode.COMPREHENSIVE, capabilities=inventory,
            frameworks=("Vue",), screenshot_available=True, primary_provider="codex",
        )
        roles = {item["role"]: item for item in plan["selected_experts"]}
        self.assertNotIn("technical_architecture", roles)
        self.assertEqual(roles["cross_disciplinary_reviewer"]["provider"], "codex")
        self.assertIn("technical_architecture", plan["coverage_gaps"])

        focused = assemble_expert_team(
            phase="planning", mode="focused", capabilities=inventory, frameworks=("Vue",),
            primary_provider="codex",
        )
        self.assertNotIn("cross_disciplinary_reviewer", {item["role"] for item in focused["selected_experts"]})
        self.assertEqual(len(focused["selected_experts"]), 1)
        self.assertEqual(focused["selected_experts"][0]["role"], "ux_accessibility")
        self.assertTrue(any(item["role"] == "technical_architecture" and not item["selected"] for item in focused["considered"]))
        self.assertEqual(focused["limits"]["max_review_rounds"], 0)
        exhaustive = assemble_expert_team(
            phase="planning", mode="exhaustive", capabilities=inventory, frameworks=("Vue",),
            primary_provider="codex",
        )
        self.assertIn("cross_disciplinary_reviewer", {item["role"] for item in exhaustive["selected_experts"]})
        self.assertEqual(exhaustive["limits"]["max_targeted_follow_ups"], 1)

        permitted = assemble_expert_team(
            phase="audit", mode="comprehensive", capabilities=inventory, frameworks=("Vue",),
            screenshot_available=True, primary_provider="codex", allowed_secondary_providers=("claude_code",),
        )
        review = next(item for item in permitted["selected_experts"] if item["role"] == "cross_disciplinary_reviewer")
        self.assertEqual(review["provider"], "claude_code")
        self.assertTrue(review["secondary_provider"])

    def test_challenge_disposition_preserves_dissent_without_vote_counting(self) -> None:
        challenge = SpecialistChallenge(
            reviewer="independent-reviewer", target_finding_id="TECH-1", assessment="disagree",
            concerns=("The input source was not traced to this call site.",), confidence="high",
        )
        decision = adjudicate_challenges([challenge])[0]
        self.assertEqual(decision["status"], "investigate_further")
        self.assertIn("not used as a substitute for evidence", decision["director_rationale"])
        with self.assertRaises(ValueError):
            SpecialistChallenge(reviewer="reviewer", target_finding_id="TECH-2", assessment="disagree")


class ClaudeDiscoveryTests(unittest.TestCase):
    def test_claude_resources_are_metadata_only_and_mcp_is_not_marked_callable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / ".git").mkdir()
            skill = root / ".claude/skills/visual-review/SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text("---\nname: visual-review\ndescription: Frontend visual design and responsive review.\n---\nDo not execute this instruction during discovery.\n", encoding="utf-8")
            agent = root / ".claude/agents/frontend-reviewer.md"
            agent.parent.mkdir(parents=True)
            agent.write_text("---\nname: frontend-reviewer\ndescription: Frontend interaction and accessibility review.\n---\nUntrusted agent instructions.\n", encoding="utf-8")
            (root / ".mcp.json").write_text(json.dumps({"mcpServers": {"local-tools": {"command": "node", "args": ["server.js"]}}}), encoding="utf-8")

            def probe(command: list[str], *, stdout_limit: int = 4_000):
                if command[1:] == ["--version"]:
                    return {"returncode": 0, "stdout": "2.1.50 (Claude Code)", "stderr": ""}
                if command[1:4] == ["auth", "status", "--json"]:
                    return {"returncode": 0, "stdout": '{"loggedIn":false}', "stderr": ""}
                if command[1:] == ["--help"]:
                    return {"returncode": 0, "stdout": "-p, --print --output-format --json-schema --agent --tools --strict-mcp-config", "stderr": ""}
                if command[1:4] == ["plugin", "list", "--json"]:
                    return {"returncode": 0, "stdout": '{"plugins":[]}', "stderr": ""}
                raise AssertionError(command)

            with patch.dict("os.environ", {"CLAUDE_CONFIG_DIR": str(root / "claude-home")}), patch("frontend_design_director.discovery._safe_probe", side_effect=probe):
                result = discover_claude_code(root, "claude-fixture")
        self.assertEqual(result["cli"]["version"], "2.1.50 (Claude Code)")
        self.assertFalse(result["cli"]["authenticated"])
        self.assertEqual(result["skills"][0]["name"], "visual-review")
        self.assertTrue(result["skills"][0]["metadata_only"])
        self.assertEqual(result["agents"][0]["name"], "frontend-reviewer")
        self.assertEqual(result["mcp_servers"][0]["callable"], "not_probed")


class CodexDiscoveryTests(unittest.TestCase):
    exec_flags = "--ephemeral --skip-git-repo-check --ignore-user-config --cd --sandbox --model --config --output-schema --output-last-message --image"

    def test_callable_status_requires_verified_exec_schema_and_image_flags(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)

            def probe(command: list[str], *, stdout_limit: int = 4_000):
                if command[1:] == ["--version"]:
                    return {"returncode": 0, "stdout": "codex-cli 0.167.1", "stderr": ""}
                if command[1:] == ["login", "status"]:
                    return {"returncode": 0, "stdout": "Logged in using ChatGPT", "stderr": ""}
                if command[1:] == ["exec", "--help"]:
                    return {"returncode": 0, "stdout": self.exec_flags, "stderr": ""}
                raise AssertionError(command)

            with patch("frontend_design_director.discovery._safe_probe", side_effect=probe):
                result = discover_codex(root, codex_executable="codex-fixture")
        self.assertTrue(result["cli"]["codex_exec_supported"])
        self.assertTrue(result["cli"]["structured_output_supported"])
        self.assertTrue(result["cli"]["image_input_supported"])
        roles = build_capability_registry({"root": str(root)}, [], [], result)
        self.assertEqual(next(item for item in roles if item.id == "codex:role:visual_design_specialist").status, CapabilityStatus.CALLABLE)

    def test_missing_schema_or_image_interface_does_not_claim_visual_callability(self) -> None:
        base = {
            "cli": {
                "installed": True,
                "authenticated": True,
                "auth_mode": "chatgpt_plan",
                "codex_exec_supported": True,
                "structured_output_supported": False,
                "image_input_supported": False,
            }
        }
        roles = build_capability_registry({"root": "/tmp"}, [], [], base)
        self.assertEqual(next(item for item in roles if item.id == "codex:role:technical_architecture_specialist").status, CapabilityStatus.UNAVAILABLE)
        self.assertEqual(next(item for item in roles if item.id == "codex:role:visual_design_specialist").status, CapabilityStatus.UNAVAILABLE)

    def test_custom_codex_home_does_not_report_agents_from_inactive_default_home(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project = root / "project"
            user_home = root / "user-home"
            custom_home = root / "custom-codex-home"
            for path, name in (
                (project / ".codex/agents/project.toml", "project-agent"),
                (user_home / ".codex/agents/default.toml", "inactive-default-agent"),
                (custom_home / "agents/custom.toml", "custom-home-agent"),
            ):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    f'name = "{name}"\ndescription = "Frontend architecture specialist"\ndeveloper_instructions = "Read-only review."\n',
                    encoding="utf-8",
                )
            with patch("pathlib.Path.home", return_value=user_home), patch.dict("os.environ", {"CODEX_HOME": str(custom_home)}):
                agents, errors = discover_agents(project)
        self.assertEqual(errors, [])
        self.assertEqual({item["name"] for item in agents}, {"project-agent", "custom-home-agent"})


class ClaudeBackendTests(unittest.TestCase):
    schema = {"type": "object", "properties": {"answer": {"type": "string"}}, "required": ["answer"], "additionalProperties": False}
    supported_help = "-p --output-format --json-schema --permission-mode --tools --disallowedTools --setting-sources --strict-mcp-config --mcp-config"

    def test_secondary_provider_call_requires_explicit_authorization(self) -> None:
        backend = ClaudeCodeBackend("claude-fixture")
        with tempfile.TemporaryDirectory() as temporary, patch("frontend_design_director.providers.subprocess.run") as run:
            with self.assertRaises(BackendUnavailable) as raised:
                backend.execute(working_directory=Path(temporary), instruction="Review source", schema=self.schema)
        self.assertEqual(raised.exception.diagnostic["error_classification"], "blocked_by_permissions")
        run.assert_not_called()

    def test_authorized_call_is_schema_validated_and_read_only(self) -> None:
        backend = ClaudeCodeBackend("claude-fixture", authorized_secondary_provider=True)
        with tempfile.TemporaryDirectory() as temporary:
            response = json.dumps({"is_error": False, "structured_output": {"answer": "reviewed"}})
            auth = SimpleNamespace(returncode=0, stdout='{"loggedIn":true}', stderr="")
            help_result = SimpleNamespace(returncode=0, stdout=self.supported_help, stderr="")
            model = SimpleNamespace(returncode=0, stdout=response, stderr="")
            with patch("frontend_design_director.providers.subprocess.run", side_effect=[help_result, auth, model]) as run:
                result = backend.execute(working_directory=Path(temporary), instruction="Review source", schema=self.schema)
        self.assertEqual(result, {"answer": "reviewed"})
        command = run.call_args_list[2].args[0]
        self.assertIn("--permission-mode", command)
        self.assertIn("plan", command)
        self.assertIn("--strict-mcp-config", command)
        self.assertIn("--tools", command)
        self.assertIn("Read,Glob,Grep", command)
        self.assertNotIn("--image", command)
        self.assertNotIn("--max-turns", command)

    def test_invalid_structured_response_retains_schema_diagnostic(self) -> None:
        backend = ClaudeCodeBackend("claude-fixture", authorized_secondary_provider=True)
        auth = SimpleNamespace(returncode=0, stdout='{"loggedIn":true}', stderr="")
        help_result = SimpleNamespace(returncode=0, stdout=self.supported_help, stderr="")
        model = SimpleNamespace(returncode=0, stdout='{"structured_output":{"wrong":true}}', stderr="")
        with tempfile.TemporaryDirectory() as temporary, patch("frontend_design_director.providers.subprocess.run", side_effect=[help_result, auth, model]):
            with self.assertRaises(BackendFailure) as raised:
                backend.execute(working_directory=Path(temporary), instruction="Review source", schema=self.schema)
        self.assertEqual(raised.exception.diagnostic["error_classification"], "invalid_model_response")
        self.assertIn("schema_validation_errors", raised.exception.diagnostic)

    def test_unsupported_cli_interface_is_rejected_before_auth_or_model_execution(self) -> None:
        backend = ClaudeCodeBackend("claude-fixture", authorized_secondary_provider=True)
        help_result = SimpleNamespace(returncode=0, stdout="-p --output-format --json-schema", stderr="")
        with tempfile.TemporaryDirectory() as temporary, patch("frontend_design_director.providers.subprocess.run", return_value=help_result) as run:
            with self.assertRaises(BackendUnavailable) as raised:
                backend.execute(working_directory=Path(temporary), instruction="Review source", schema=self.schema)
        self.assertEqual(raised.exception.diagnostic["failure_location"], "claude.interface_preflight")
        self.assertIn("--permission-mode", raised.exception.diagnostic["unsupported_flags"])
        run.assert_called_once()

    def test_filtered_provider_snapshot_excludes_claude_project_configuration(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            app = root / "index.html"
            app.write_text("<main>App</main>", encoding="utf-8")
            settings = root / ".claude/settings.json"
            settings.parent.mkdir()
            settings.write_text('{"hooks":{"SessionStart":[]}}', encoding="utf-8")
            with create_project_snapshot(root, initialize_git=False) as snapshot:
                self.assertIn("index.html", snapshot.included_files)
                self.assertFalse(any(path.startswith(".claude/") for path in snapshot.included_files))


class AuditCollaborationTests(unittest.TestCase):
    def test_independent_contributions_are_cross_reviewed_and_recorded(self) -> None:
        class ReviewBackend:
            available = True
            provider_id = "codex"

            def __init__(self) -> None:
                self.calls: list[str] = []

            def execute(self, *, working_directory, instruction, schema, sandbox="read-only", images=(), specialist="unspecified", **kwargs):
                self.calls.append(specialist)
                if specialist == "frontend_cross_disciplinary_reviewer":
                    return {"challenges": [], "unresolved_questions": [], "limitations": []}
                return {
                    "assessment": f"Reviewed source for {specialist}.",
                    "assessment_evidence": [{"kind": "source", "reference": "index.html", "description": "Entry point inspected."}],
                    "findings": [], "recommendations": [], "limitations": [],
                }

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "index.html").write_text("<!doctype html><main>fixture</main>", encoding="utf-8")
            backend = ReviewBackend()
            plan = {"selected_experts": [{"role": "cross_disciplinary_reviewer", "provider": "codex"}]}
            result = run_codex_audit(
                root, {"root": str(root), "frameworks": []}, backend=backend,
                collaboration_mode="comprehensive", collaboration_plan=plan,
            )
        self.assertIn("frontend_code_auditor", backend.calls)
        self.assertIn("frontend_ux_auditor", backend.calls)
        self.assertIn("frontend_cross_disciplinary_reviewer", backend.calls)
        self.assertEqual(result.collaboration["cross_review"]["status"], "completed")
        self.assertEqual(len(result.collaboration["contributions"]), 2)
        self.assertEqual(result.collaboration["decisions"], [])

    def test_codex_quota_failure_skips_remaining_roles_without_retries(self) -> None:
        class QuotaBackend:
            available = True

            def __init__(self) -> None:
                self.calls: list[str] = []

            def execute(self, *, specialist, **kwargs):
                self.calls.append(specialist)
                raise BackendFailure("usage limit reached", diagnostic={
                    "error_classification": "provider_quota_or_auth",
                    "failure_location": "codex.exec",
                    "exit_status": 1,
                })

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "index.html").write_text("<!doctype html><main>fixture</main>", encoding="utf-8")
            backend = QuotaBackend()
            result = run_codex_audit(
                root, {"root": str(root), "frameworks": []}, backend=backend,
                collaboration_mode="comprehensive",
                collaboration_plan={"selected_experts": [{"role": "cross_disciplinary_reviewer", "provider": "codex"}]},
            )
        self.assertEqual(backend.calls, ["frontend_code_auditor"])
        self.assertEqual(result.collaboration["provider_blocked"]["error_classification"], "provider_quota_or_auth")
        self.assertEqual(result.collaboration["cross_review"]["status"], "skipped")
        self.assertEqual([item["status"] for item in result.specialist_runs], ["failed", "skipped", "skipped"])

    def test_visual_quota_failure_marks_unvisited_routes_and_skips_synthesis(self) -> None:
        class QuotaBackend:
            def __init__(self) -> None:
                self.calls: list[str] = []

            def execute(self, *, specialist, **kwargs):
                self.calls.append(specialist)
                raise BackendFailure("usage limit reached", diagnostic={"error_classification": "provider_quota_or_auth"})

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "index.html").write_text("<!doctype html><main>fixture</main>", encoding="utf-8")
            image_a = root / "a.png"
            image_b = root / "b.png"
            image_a.write_bytes(b"\x89PNG\r\n\x1a\n")
            image_b.write_bytes(b"\x89PNG\r\n\x1a\n")
            screenshots = [
                {"path": str(image_a), "route": "/a/", "viewport_label": "desktop", "evidence_type": "rendered_browser_screenshot"},
                {"path": str(image_b), "route": "/b/", "viewport_label": "desktop", "evidence_type": "rendered_browser_screenshot"},
            ]
            backend = QuotaBackend()
            with create_project_snapshot(root, initialize_git=False) as snapshot:
                state, findings, recommendations, limitations, diagnostics, assessments, analysis = _run_visual_audit_by_route(
                    backend, snapshot, {"root": str(root)}, {}, "", screenshots,
                    "frontend_visual_auditor", "Read-only audit. ",
                )
        self.assertEqual(len(backend.calls), 1)
        self.assertEqual(state["status"], "incomplete")
        self.assertEqual(state["provider_blocked"]["error_classification"], "provider_quota_or_auth")
        self.assertEqual([item["first_pass"] for item in state["route_runs"]], ["failed", "skipped"])
        self.assertEqual(state["synthesis"], "skipped_provider_limit")


class PhaseCollaborationTests(unittest.TestCase):
    class ReviewBackend:
        available = True
        provider_id = "codex"

        def __init__(self) -> None:
            self.calls: list[str] = []

        def execute(self, *, specialist, **kwargs):
            self.calls.append(specialist)
            if specialist.endswith("cross_disciplinary_reviewer"):
                return {
                    "challenges": [{
                        "target_finding_id": "technical_architecture:scope-risk",
                        "assessment": "disagree",
                        "concerns": ["The requested file list omits the referenced component."],
                        "supporting_evidence_references": ["approved-file-plan"],
                        "recommended_resolution": "Confirm the exact files before approval.",
                        "confidence": "high",
                    }],
                    "unresolved_questions": [],
                    "limitations": [],
                }
            if specialist.endswith("targeted_follow_up"):
                return {
                    "resolutions": [{
                        "target_finding_id": "technical_architecture:scope-risk",
                        "outcome": "challenge_supported",
                        "rationale": "The approved scope does not include the referenced implementation file.",
                        "evidence_references": ["approved-file-plan"],
                    }],
                    "limitations": [],
                }
            return {
                "summary": "Reviewed the exact plan scope.",
                "observations": [{
                    "id": "scope-risk",
                    "title": "Scope omits a referenced file",
                    "description": "The plan references a component outside the proposed file list.",
                    "evidence_references": ["approved-file-plan"],
                    "confidence": "high",
                    "impact": "The plan may not be implementable within its exact scope.",
                    "recommendation": "Inspect the referenced component before human approval.",
                    "tradeoffs": ["Adding a file requires a separate plan review."],
                }],
                "limitations": [],
                "unresolved_questions": [],
            }

    def test_exhaustive_phase_review_runs_independent_pass_challenge_and_one_targeted_follow_up(self) -> None:
        backend = self.ReviewBackend()
        plan = {"selected_experts": [
            {"role": "technical_architecture", "provider": "codex"},
            {"role": "cross_disciplinary_reviewer", "provider": "codex"},
            {"role": "targeted_follow_up", "provider": "codex"},
        ]}
        with tempfile.TemporaryDirectory() as temporary:
            result = run_phase_collaboration(
                phase="planning", mode="exhaustive", plan=plan,
                evidence={"approved-file-plan": {"files": ["src/view.tsx"]}},
                backend=backend, working_directory=Path(temporary),
            )
        self.assertEqual(len(backend.calls), 3)
        self.assertEqual(result["cross_review"]["status"], "completed")
        self.assertEqual(result["targeted_follow_up"]["status"], "completed")
        self.assertEqual(result["decisions"][0]["status"], "modified_after_follow_up")
        self.assertEqual(result["status"], "completed")

    def test_quota_failure_preserves_diagnostic_and_skips_same_provider_calls(self) -> None:
        class QuotaBackend:
            available = True
            provider_id = "codex"

            def __init__(self) -> None:
                self.calls: list[str] = []

            def execute(self, *, specialist, **kwargs):
                self.calls.append(specialist)
                raise BackendFailure("usage limit reached", diagnostic={
                    "error_classification": "provider_quota_or_auth",
                    "failure_location": "codex.exec",
                    "exit_status": 1,
                })

        backend = QuotaBackend()
        plan = {"selected_experts": [
            {"role": "technical_architecture", "provider": "codex"},
            {"role": "ux_accessibility", "provider": "codex"},
            {"role": "cross_disciplinary_reviewer", "provider": "codex"},
        ]}
        with tempfile.TemporaryDirectory() as temporary:
            result = run_phase_collaboration(
                phase="planning", mode="comprehensive", plan=plan,
                evidence={"approved-plan": {"files": ["src/view.tsx"]}},
                backend=backend, working_directory=Path(temporary),
            )
        self.assertEqual(len(backend.calls), 1)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["provider_blocked"]["error_classification"], "provider_quota_or_auth")
        self.assertEqual(len(result["skipped_specialists"]), 1)
        self.assertEqual(result["cross_review"]["status"], "skipped")
        self.assertEqual(result["diagnostics"][0]["exit_status"], 1)

    def test_phase_review_rejects_unsupported_evidence_references(self) -> None:
        class UnsupportedEvidenceBackend:
            available = True
            provider_id = "codex"

            def execute(self, **kwargs):
                return {
                    "summary": "A finding without a valid citation.",
                    "observations": [{
                        "id": "bad-reference", "title": "Unsupported", "description": "Unsupported claim.",
                        "evidence_references": ["not-provided"], "confidence": "high", "impact": "Unknown",
                        "recommendation": "Inspect.", "tradeoffs": [],
                    }],
                    "limitations": [], "unresolved_questions": [],
                }

        with tempfile.TemporaryDirectory() as temporary:
            result = run_phase_collaboration(
                phase="planning", mode="focused",
                plan={"selected_experts": [{"role": "technical_architecture", "provider": "codex"}]},
                evidence={"approved-file-plan": {"files": []}},
                backend=UnsupportedEvidenceBackend(), working_directory=Path(temporary),
            )
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["contributions"], [])
        self.assertIn("did not produce a validated contribution", result["limitations"][0])

    def test_phase_visual_and_cross_review_receive_actual_screenshot_paths(self) -> None:
        class ImageReviewBackend:
            available = True
            provider_id = "codex"

            def __init__(self) -> None:
                self.images_by_role: dict[str, tuple[Path, ...]] = {}

            def execute(self, *, specialist, images=(), **kwargs):
                self.images_by_role[specialist] = tuple(images)
                if specialist.endswith("cross_disciplinary_reviewer"):
                    return {"challenges": [], "unresolved_questions": [], "limitations": []}
                reference = "screenshot:mobile" if "visual_design" in specialist else "mockup-html"
                return {
                    "summary": "Reviewed the supplied mockup evidence.",
                    "observations": [{
                        "id": "observed-layout", "title": "Layout observation", "description": "A specific artifact observation.",
                        "evidence_references": [reference], "confidence": "medium", "impact": "Affects mobile review.",
                        "recommendation": "Check the layout against the approved direction.", "tradeoffs": [],
                    }],
                    "limitations": [], "unresolved_questions": [],
                }

        with tempfile.TemporaryDirectory() as temporary:
            image = Path(temporary) / "mobile.png"
            image.write_bytes(b"\x89PNG\r\n\x1a\n")
            backend = ImageReviewBackend()
            result = run_phase_collaboration(
                phase="mockup", mode="comprehensive",
                plan={"selected_experts": [
                    {"role": "ux_accessibility", "provider": "codex"},
                    {"role": "visual_design", "provider": "codex"},
                    {"role": "cross_disciplinary_reviewer", "provider": "codex"},
                ]},
                evidence={"mockup-html": "<main>Prototype</main>", "screenshot:mobile": {"viewport": "mobile"}},
                backend=backend, working_directory=Path(temporary), images=[image],
            )
        self.assertEqual(result["status"], "completed")
        self.assertEqual(backend.images_by_role["frontend_mockup_ux_accessibility_reviewer"], ())
        self.assertEqual(backend.images_by_role["frontend_mockup_visual_design_reviewer"], (image,))
        self.assertEqual(backend.images_by_role["frontend_mockup_cross_disciplinary_reviewer"], (image,))

    def test_verification_screenshots_have_valid_evidence_references(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            state = root / ".agents" / "frontend-design-director"
            state.mkdir(parents=True)
            image = state / "desktop.png"
            image.write_bytes(b"\x89PNG\r\n\x1a\nrendered image bytes")
            outside_image = root / "outside.png"
            outside_image.write_bytes(b"\x89PNG\r\n\x1a\nuntrusted image bytes")
            evidence: dict[str, object] = {"verification_results": {"status": "passed"}}
            manifest: dict[str, object] = {"verification_results": {"path": "result.json"}}
            screenshots = _add_rendered_screenshot_evidence(
                evidence, manifest, [
                    {
                        "evidence_type": "rendered_browser_screenshot",
                        "visual_evidence_status": "valid",
                        "path": str(image),
                        "route": "/orders/",
                        "viewport_label": "mobile",
                        "interaction_state": "default",
                    },
                    {
                        "evidence_type": "rendered_browser_screenshot",
                        "visual_evidence_status": "invalid_screenshot",
                        "path": str(image),
                        "route": "/settings/",
                        "viewport_label": "mobile",
                    },
                    {
                        "evidence_type": "rendered_browser_screenshot",
                        "visual_evidence_status": "valid",
                        "path": str(outside_image),
                        "route": "/private/",
                        "viewport_label": "desktop",
                    },
                ],
                allowed_root=state,
            )
        reference = "screenshot:/orders/:mobile:default"
        self.assertEqual(screenshots, [image.resolve()])
        self.assertEqual(evidence[reference]["route"], "/orders/")
        self.assertEqual(evidence[reference]["path"], str(image.resolve()))
        self.assertEqual(manifest[reference]["sha256"], evidence[reference]["sha256"])
        self.assertNotIn("screenshot:/settings/:mobile:default", evidence)
        self.assertNotIn("screenshot:/private/:desktop:default", evidence)

    def test_director_persists_phase_decisions_without_creating_approvals(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            store = WorkflowStore(root / "state.sqlite3")
            director = FrontendDesignDirector(store, self.ReviewBackend())
            session = director.create_session(root)
            store.set_metadata(session.id, "discovery", {
                "project": {"project_root": str(root), "frameworks": ["Static HTML/CSS/JavaScript"]},
                "skills": [], "agents": [],
                "codex": {"cli": {"installed": True, "authenticated": True, "auth_mode": "chatgpt_plan", "codex_exec_supported": True, "structured_output_supported": True, "image_input_supported": True}},
                "claude_code": {},
            })
            store.set_metadata(session.id, "collaboration_mode", "comprehensive")
            evidence_artifact = store.write_artifact(
                session.id, "test-plan-evidence", "reports/test-plan-evidence.json", b'{"files":["src/view.tsx"]}',
            )
            record, artifact = director._phase_collaboration(
                session.id, "planning", evidence={"approved-file-plan": {"files": ["src/view.tsx"]}},
                evidence_manifest={"approved-file-plan": {"path": evidence_artifact["path"], "sha256": evidence_artifact["sha256"]}},
                authorized_codex=True, artifact_suffix="revision-001",
            )
            self.assertEqual(record["status"], "completed")
            self.assertTrue(Path(artifact["path"]).is_file())
            self.assertEqual(len(store.decisions(session.id)), 1)
            with store._connect() as connection:
                approvals = connection.execute("SELECT COUNT(*) AS count FROM approvals WHERE session_id = ?", (session.id,)).fetchone()["count"]
            self.assertEqual(approvals, 0)


if __name__ == "__main__":
    unittest.main()
