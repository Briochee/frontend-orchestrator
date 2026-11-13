"""Orchestrate persisted frontend discovery, audit, design, mockup, and implementation stages."""

from __future__ import annotations

import hashlib
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .auditing import AuditResult, run_codex_audit, run_static_audit
from .backend import AgentBackend
from .browser import DEPTH_VIEWPORTS, capture_mockup_screenshots, capture_screenshots
from .codex_backend import CodexCLIBackend
from .discovery import build_capability_matrix, discover_agents, discover_codex, discover_project, discover_skills
from .implementation import _current_baselines, apply_implementation_patch, create_implementation_plan, execute_implementation
from .intelligence import attach_runtime_evidence, build_project_intelligence, intelligence_reports, renderable_route_candidates, runtime_findings
from .logging_setup import configure_logging
from .mockups import create_codex_mockup, create_template_mockup
from .models import Approval, AuditType, Phase, Session, utc_now
from .reporting import audit_reports
from .server import managed_development_server
from .storage import WORKFLOW_STATE_DIRECTORY, WorkflowStore
from .state_machine import TRANSITIONS
from .verification import run_verification, verification_reports


class WorkflowBlocked(RuntimeError):
    """Raised when the current workflow has not reached a required gate."""


class FrontendDesignDirector:
    """High-level workflow service; approval transitions remain controlled in this process."""

    def __init__(self, store: WorkflowStore, backend: AgentBackend | None = None) -> None:
        self.store = store
        self.backend = backend or CodexCLIBackend()

    def create_session(self, project_root: Path, title: str = "") -> Session:
        root = project_root.resolve(strict=True)
        state_dir = root / WORKFLOW_STATE_DIRECTORY
        session = self.store.create_session(root, state_dir, title)
        configure_logging(state_dir / "logs")[0].info("Workflow session created", context={"session_id": session.id, "project_root": str(root)})
        return session

    def discover(self, session_id: str) -> dict[str, Any]:
        session = self.store.get_session(session_id)
        if session.phase != Phase.DISCOVERING:
            self.store.transition(session_id, Phase.DISCOVERING)
        activity, _ = configure_logging(Path(session.state_dir) / "logs")
        try:
            project = discover_project(Path(session.project_root))
            skills, skill_errors = discover_skills(Path(session.project_root))
            agents, agent_errors = discover_agents(Path(session.project_root))
            codex = discover_codex(Path(session.project_root))
            capabilities = build_capability_matrix(project, skills, agents, codex)
            inventory = {
                "schema_version": 1,
                "project": project,
                "skills": skills,
                "skill_discovery_errors": skill_errors,
                "agents": agents,
                "agent_discovery_errors": agent_errors,
                "codex": codex,
                "capabilities": [item.__dict__ for item in capabilities],
                "installation_policy": "No skill, plugin, dependency, or browser was installed.",
            }
            self.store.set_metadata(session_id, "discovery", inventory)
            self.store.write_artifact(session_id, "capability-inventory", "reports/capability-inventory.json", _json_bytes(inventory))
            self.store.write_artifact(session_id, "discovery-report", "reports/discovery.json", _json_bytes(inventory))
            self.store.transition(session_id, Phase.CAPABILITIES_REVIEW)
            activity.info("Capability discovery completed", context={"session_id": session_id, "skill_count": len(skills), "agent_count": len(agents)})
            return inventory
        except Exception as error:
            self._fail(session_id, error, "discovery")
            raise

    def audit(
        self,
        session_id: str,
        *,
        use_codex: bool = False,
        browser_url: str | None = None,
        allow_remote: bool = False,
        route_paths: tuple[str, ...] | list[str] = (),
        depth: str = "deep",
        start_command: list[str] | tuple[str, ...] | None = None,
        server_url: str | None = None,
        server_human_confirmation: bool = False,
    ) -> dict[str, Any]:
        if depth not in DEPTH_VIEWPORTS:
            raise ValueError(f"Unsupported audit depth: {depth}.")
        if start_command and (not server_url or browser_url or not server_human_confirmation):
            raise ValueError("Starting a project server requires an explicit local readiness URL, no --url, and interactive human confirmation.")
        if server_url and not start_command:
            raise ValueError("A server readiness URL requires an explicit --start-command.")
        try:
            if start_command:
                with managed_development_server(Path(self.store.get_session(session_id).project_root), start_command, server_url) as server_run:
                    result = self._audit(session_id, use_codex=use_codex, browser_url=server_run.url, allow_remote=False, route_paths=route_paths, depth=depth)
                details = server_run.details
                server_artifacts = {
                    "development-server-run": self.store.write_artifact(session_id, "development-server-run", "evidence/development-server.json", _json_bytes(details)),
                    "development-server-stdout": self.store.write_artifact(session_id, "development-server-stdout", "logs/development-server-stdout.log", server_run.stdout_excerpt.encode("utf-8")),
                    "development-server-stderr": self.store.write_artifact(session_id, "development-server-stderr", "logs/development-server-stderr.log", server_run.stderr_excerpt.encode("utf-8")),
                }
                self.store.add_execution(session_id, "development_server", "started_and_stopped", {**details, "log_artifacts": {name: item["path"] for name, item in server_artifacts.items()}})
                result["development_server"] = details
                result["server_logs"] = {name: item["path"] for name, item in server_artifacts.items() if name != "development-server-run"}
                self.store.set_metadata(session_id, "audit", result)
                return result
            return self._audit(session_id, use_codex=use_codex, browser_url=browser_url, allow_remote=allow_remote, route_paths=route_paths, depth=depth)
        except Exception as error:
            self._fail(session_id, error, "audit")
            raise

    def _audit(
        self,
        session_id: str,
        *,
        use_codex: bool = False,
        browser_url: str | None = None,
        allow_remote: bool = False,
        route_paths: tuple[str, ...] | list[str] = (),
        depth: str = "deep",
    ) -> dict[str, Any]:
        session = self.store.get_session(session_id)
        if session.phase not in {Phase.CAPABILITIES_REVIEW, Phase.AWAITING_DIRECTION, Phase.AUDIT_COMPLETED, Phase.AUDITING}:
            raise WorkflowBlocked(f"Audit requires a discovery review or a prior audit cycle; current phase is {session.phase.value}.")
        discovery = session.metadata.get("discovery")
        if not discovery:
            raise WorkflowBlocked("Run `discover` before starting the audit.")
        if session.phase != Phase.AUDITING:
            self.store.transition(session_id, Phase.AUDITING)
        activity, requests = configure_logging(Path(session.state_dir) / "logs")
        screenshots: list[dict[str, Any]] = []
        browser_capture_records: list[dict[str, Any]] = []
        limitations: list[str] = []
        audit_instructions = self._stage_instructions(session_id, "audit")
        captured_gallery = b""
        intelligence = None
        if browser_url:
            intelligence = build_project_intelligence(Path(session.project_root), discovery["project"])
            discovered_routes = renderable_route_candidates(intelligence)
            capture_routes = list(dict.fromkeys(route_paths if route_paths else discovered_routes))
            try:
                with tempfile.TemporaryDirectory(prefix="frontend-director-browser-") as temporary:
                    screenshot_directory = Path(temporary) / "screenshots"
                    captured = capture_screenshots(browser_url, screenshot_directory, allow_remote=allow_remote, route_paths=capture_routes, viewports=DEPTH_VIEWPORTS[depth])
                    for item in captured:
                        if item.get("evidence_type") != "rendered_browser_screenshot":
                            browser_capture_records.append(item)
                            limitations.append(f"Browser route `{item.get('route', '/')}` at `{item.get('viewport', 'unknown')}` could not be captured: {item.get('error', 'unknown navigation error')}")
                            continue
                        route_slug = item.get("route_slug", "home")
                        viewport_label = item.get("viewport_label", item["viewport"])
                        state_suffix = "-keyboard-focus" if item.get("interaction_state") == "keyboard_focus_after_one_tab" else ""
                        route_digest = hashlib.sha256(str(item.get("route", "/")).encode("utf-8")).hexdigest()[:6]
                        screenshot_name = f"{route_slug}-{route_digest}-{viewport_label}{state_suffix}.png"
                        artifact_name = f"screenshot-{route_slug}-{route_digest}-{viewport_label}{state_suffix}"
                        artifact = self.store.write_artifact(session_id, artifact_name, f"evidence/screenshots/{screenshot_name}", Path(item["path"]).read_bytes())
                        stored = {**item, "path": artifact["path"], "sha256": artifact["sha256"]}
                        screenshots.append(stored)
                        browser_capture_records.append(stored)
                    gallery_path = screenshot_directory / "gallery.html"
                    if gallery_path.is_file():
                        gallery_text = gallery_path.read_text(encoding="utf-8")
                        for item in captured:
                            if item.get("evidence_type") != "rendered_browser_screenshot":
                                continue
                            local_name = Path(item["path"]).name
                            route_slug = item.get("route_slug", "home")
                            viewport_label = item.get("viewport_label", item["viewport"])
                            state_suffix = "-keyboard-focus" if item.get("interaction_state") == "keyboard_focus_after_one_tab" else ""
                            route_digest = hashlib.sha256(str(item.get("route", "/")).encode("utf-8")).hexdigest()[:6]
                            gallery_text = gallery_text.replace(local_name, f"{route_slug}-{route_digest}-{viewport_label}{state_suffix}.png")
                        captured_gallery = gallery_text.encode("utf-8")
            except Exception as error:
                limitations.append(f"Browser evidence was unavailable: {type(error).__name__}: {str(error)[:240]}")
                requests.warning("Browser screenshot capture unavailable", context={"session_id": session_id, "error_category": type(error).__name__})
        else:
            limitations.append("Rendered browser evidence was not collected because no explicit --url was supplied. Source analysis cannot establish actual appearance or runtime behavior.")
        if browser_capture_records:
            self.store.write_artifact(session_id, "browser-evidence", "evidence/browser-evidence.json", _json_bytes(browser_capture_records))
            if screenshots:
                self.store.write_artifact(session_id, "screenshot-gallery", "evidence/screenshots/gallery.html", captured_gallery)
        intelligence = attach_runtime_evidence(intelligence, screenshots) if intelligence else build_project_intelligence(Path(session.project_root), discovery["project"], screenshots)
        intelligence["audit_depth"] = depth
        intelligence["capture_route_policy"] = (
            "operator_selected" if route_paths else "all_static_candidates"
        ) if browser_url else "not_rendered"
        intelligence["capture_route_paths"] = list(route_paths) if browser_url else []
        navigation_failures = [item for item in browser_capture_records if item.get("evidence_type") == "browser_navigation_failure"]
        intelligence["browser_navigation_failures"] = navigation_failures
        intelligence["coverage"]["browser_navigation_failures"] = len(navigation_failures)
        self.store.set_metadata(session_id, "frontend_intelligence", intelligence)
        self.store.set_metadata(session_id, "audit_depth", depth)
        self.store.write_artifact(session_id, "frontend-intelligence", "reports/frontend-intelligence.json", _json_bytes(intelligence))
        static_result = run_static_audit(Path(session.project_root), discovery["project"], screenshots)
        observed_findings = runtime_findings(intelligence)
        if observed_findings:
            static_result = AuditResult(
                findings=tuple(_merge_findings(static_result.findings, tuple(observed_findings))),
                limitations=static_result.limitations,
                recommendations=static_result.recommendations,
                screenshots=static_result.screenshots,
                backend_used=static_result.backend_used,
                visual_analysis=static_result.visual_analysis,
            )
        refreshed_discovery = dict(discovery)
        refreshed_discovery["capabilities"] = [
            item.__dict__ for item in build_capability_matrix(
                discovery["project"],
                discovery["skills"],
                discovery["agents"],
                discovery["codex"],
                rendered_screenshots=[item["path"] for item in screenshots],
            )
        ]
        self.store.set_metadata(session_id, "discovery", refreshed_discovery)
        self.store.write_artifact(session_id, "capability-inventory", "reports/capability-inventory.json", _json_bytes(refreshed_discovery))
        result = static_result
        if use_codex:
            try:
                codex_result = run_codex_audit(Path(session.project_root), discovery["project"], screenshots=screenshots, backend=self.backend, intelligence=intelligence, user_instructions=audit_instructions)
                result = AuditResult(
                    findings=tuple(_merge_findings(static_result.findings, codex_result.findings)),
                    limitations=tuple(dict.fromkeys((*static_result.limitations, *codex_result.limitations, *limitations))),
                    recommendations=tuple(dict.fromkeys((*static_result.recommendations, *codex_result.recommendations))),
                    screenshots=tuple(screenshots),
                    backend_used="codex_cli_plus_static",
                    visual_analysis=codex_result.visual_analysis,
                )
            except Exception as error:
                result = AuditResult(
                    findings=static_result.findings,
                    limitations=tuple(dict.fromkeys((*static_result.limitations, *limitations, f"Codex specialist audit could not run: {type(error).__name__}: {str(error)[:240]}"))),
                    recommendations=static_result.recommendations,
                    screenshots=tuple(screenshots),
                    backend_used="static_codex_unavailable",
                    visual_analysis={},
                )
        else:
            if audit_instructions:
                limitations.append("Human audit instructions were preserved in the session but not interpreted by the deterministic source rules; use the explicit Codex audit option if you want model-assisted interpretation.")
            if limitations:
                result = AuditResult(static_result.findings, tuple(dict.fromkeys((*static_result.limitations, *limitations))), static_result.recommendations, tuple(screenshots), "static", {})
        findings = list(result.findings)
        self.store.replace_findings(session_id, findings)
        reports = audit_reports(findings, result, discovery["project"], intelligence)
        reports.update(intelligence_reports(intelligence))
        if result.visual_analysis:
            reports["visual-analysis.json"] = _json_bytes(result.visual_analysis)
        report_revision = int(session.metadata.get("audit_revision", 0)) + 1
        for filename, content in reports.items():
            artifact_name = filename.removesuffix(".md").removesuffix(".json").replace("-", "_")
            self.store.write_artifact(session_id, artifact_name, f"reports/{filename}", content)
            revision_name = f"audit-{report_revision:03d}-{artifact_name}"
            self.store.write_artifact(session_id, revision_name, f"reports/audits/audit-{report_revision:03d}/{filename}", content)
        self.store.set_metadata(session_id, "audit_revision", report_revision)
        self.store.set_metadata(session_id, "audit_history", [*session.metadata.get("audit_history", []), {
            "revision": report_revision,
            "created_at": utc_now(),
            "findings_count": len(findings),
            "routes_discovered": intelligence["coverage"]["routes_discovered"],
            "routes_rendered": intelligence["coverage"]["routes_rendered"],
            "screenshots_captured": intelligence["coverage"]["screenshots_captured"],
        }])
        summary = {
            "schema_version": 1,
            "findings_count": len(findings),
            "by_audit_type": {kind.value: sum(item.audit_type == kind for item in findings) for kind in AuditType},
            "limitations": list(result.limitations),
            "screenshots": list(result.screenshots),
            "backend": result.backend_used,
            "depth": depth,
            "human_instructions_present": bool(audit_instructions),
            "revision": report_revision,
            "coverage": intelligence["coverage"],
            "reports": sorted(reports),
        }
        self.store.set_metadata(session_id, "audit", summary)
        self.store.transition(session_id, Phase.AUDIT_COMPLETED)
        activity.info("Frontend audit completed", context={"session_id": session_id, "findings": len(findings), "backend": result.backend_used})
        return summary

    def record_guided_instruction(self, session_id: str, instruction: str, *, stage: str = "global") -> dict[str, Any]:
        """Persist a human instruction without granting any design or implementation approval."""
        value = instruction.strip()
        if not value or len(value) > 10_000:
            raise ValueError("Instruction must contain 1 to 10,000 characters.")
        session = self.store.get_session(session_id)
        registry = list(session.metadata.get("guided_instructions", []))
        record = {"stage": stage, "instruction": value, "recorded_at": utc_now(), "source": "human"}
        registry.append(record)
        self.store.set_metadata(session_id, "guided_instructions", registry)
        self.store.add_execution(session_id, "guided_instruction", "recorded", {"stage": stage, "character_count": len(value)})
        return {"stage": stage, "instruction_count": len(registry), "approval_granted": False}

    def _stage_instructions(self, session_id: str, stage: str) -> str:
        session = self.store.get_session(session_id)
        records = session.metadata.get("guided_instructions", [])
        selected = [item["instruction"] for item in records if item.get("stage") in {"global", stage} and isinstance(item.get("instruction"), str)]
        return "\n\n".join(selected)[-20_000:]

    def record_direction(
        self,
        session_id: str,
        *,
        visual: str,
        behavior: str,
        scope: str,
        constraints: str = "",
        human_confirmation: bool,
    ) -> dict[str, Any]:
        session = self.store.get_session(session_id)
        if session.phase not in {Phase.AUDIT_COMPLETED, Phase.AWAITING_DIRECTION}:
            raise WorkflowBlocked("Design direction can be recorded only after the audit report is ready.")
        if visual not in {"preserve", "refine", "explore", "custom"}:
            raise ValueError("Visual direction must be preserve, refine, explore, or custom.")
        if behavior not in {"preserve", "improve", "explore", "custom"}:
            raise ValueError("Behavior direction must be preserve, improve, explore, or custom.")
        if scope not in {"components", "screens", "opportunities", "frontend"}:
            raise ValueError("Scope must be components, screens, opportunities, or frontend.")
        if (visual == "custom" or behavior == "custom") and not constraints.strip():
            raise ValueError("Custom directions require explicit user constraints.")
        if not human_confirmation:
            raise ValueError("Design direction requires an interactive human confirmation.")
        if session.phase == Phase.AUDIT_COMPLETED:
            self.store.transition(session_id, Phase.AWAITING_DIRECTION)
        decision_id = f"direction-{utc_now().replace(':', '').replace('-', '')}"
        direction = {
            "schema_version": 1,
            "visual_appearance": visual,
            "behavior_and_interaction": behavior,
            "scope": scope,
            "constraints": constraints.strip(),
            "recorded_at": utc_now(),
            "decided_by": "human",
        }
        self.store.add_decision(session_id, decision_id, {"kind": "design_direction", **direction})
        self.store.revoke_approvals(session_id, ("design_direction", "mockup", "implementation", "patch_application"), "Design direction was updated.")
        artifact = self.store.write_artifact(session_id, "design-direction", "decisions/design-direction.json", _json_bytes(direction))
        self.store.add_approval(Approval(
            session_id=session_id,
            approval_type="design_direction",
            artifact_name="design-direction",
            artifact_sha256=artifact["sha256"],
            approved_scope=(scope,),
            timestamp=utc_now(),
            human_confirmation=True,
            decision_ids=(decision_id,),
        ))
        self.store.transition(session_id, Phase.DIRECTION_APPROVED, {"decision_id": decision_id})
        configure_logging(Path(session.state_dir) / "logs")[0].info("Human design direction recorded", context={"session_id": session_id, "decision_id": decision_id, "visual": visual, "behavior": behavior, "scope": scope})
        return direction

    def generate_mockup(self, session_id: str, *, brief: str = "", revision_note: str = "", use_codex: bool = False) -> dict[str, Any]:
        try:
            return self._generate_mockup(session_id, brief=brief, revision_note=revision_note, use_codex=use_codex)
        except Exception as error:
            self._fail(session_id, error, "mockup_generation")
            raise

    def _generate_mockup(self, session_id: str, *, brief: str = "", revision_note: str = "", use_codex: bool = False) -> dict[str, Any]:
        session = self.store.get_session(session_id)
        if session.phase not in {Phase.DIRECTION_APPROVED, Phase.MOCKUP_REVISION, Phase.GENERATING_MOCKUPS}:
            raise WorkflowBlocked("Mockup generation requires an approved design direction.")
        if not self.store.latest_valid_approval(session_id, "design_direction", "design-direction"):
            raise WorkflowBlocked("The current design direction does not have a valid human approval.")
        if session.phase != Phase.GENERATING_MOCKUPS:
            self.store.transition(session_id, Phase.GENERATING_MOCKUPS)
        self.store.revoke_approvals(session_id, ("mockup", "implementation", "patch_application"), "A new mockup revision invalidates prior approvals.")
        revision = int(session.metadata.get("mockup_revision", 0)) + 1
        direction = _read_json_artifact(self.store, session_id, "design-direction")
        files = create_template_mockup(
            project_name=session.title,
            visual_direction=direction["visual_appearance"],
            behavior_direction=direction["behavior_and_interaction"],
            scope=direction["scope"],
            revision=revision,
            brief=brief or direction.get("constraints", ""),
            revision_note=revision_note,
        )
        generation_summary = "Generated by the built-in static template."
        mode = "template"
        if use_codex:
            report_path = Path(session.state_dir) / "reports" / "audit-summary.md"
            findings_path = Path(session.state_dir) / "reports" / "findings.json"
            context = {
                "design_direction": direction,
                "human_revision_note": revision_note,
                "user_brief": brief,
                "audit_summary": report_path.read_text(encoding="utf-8") if report_path.exists() else "",
                "findings": json.loads(findings_path.read_text(encoding="utf-8")) if findings_path.exists() else {"findings": []},
                "screenshots": session.metadata.get("audit", {}).get("screenshots", []),
            }
            output_path = Path(session.state_dir) / "mockups" / f"revision-{revision:03d}"
            files, generation_summary = create_codex_mockup(output_directory=output_path, initial_files=files, context=context, backend=self.backend)
            mode = "codex_cli_isolated"
        revision_dir = f"mockups/revision-{revision:03d}"
        file_artifacts: dict[str, dict[str, Any]] = {}
        for name, content in files.items():
            artifact_name = f"mockup-r{revision:03d}-{name.replace('.', '_')}"
            file_artifacts[name] = self.store.write_artifact(session_id, artifact_name, f"{revision_dir}/{name}", content)
        screenshots: list[dict[str, Any]] = []
        rendering_limitations: list[str] = []
        try:
            with tempfile.TemporaryDirectory(prefix="frontend-director-mockup-browser-") as temporary:
                captured = capture_mockup_screenshots(Path(file_artifacts["index.html"]["path"]), Path(temporary) / "screenshots")
                for item in captured:
                    artifact = self.store.write_artifact(
                        session_id,
                        f"mockup-screenshot-r{revision:03d}-{item['viewport']}",
                        f"{revision_dir}/screenshots/{item['viewport']}.png",
                        Path(item["path"]).read_bytes(),
                    )
                    screenshots.append({**item, "path": artifact["path"], "sha256": artifact["sha256"]})
        except Exception as error:
            rendering_limitations.append(f"Mockup screenshots were unavailable: {type(error).__name__}: {str(error)[:240]}")
        manifest = {
            "schema_version": 1,
            "revision": revision,
            "revision_note": revision_note,
            "generation_mode": mode,
            "summary": generation_summary,
            "design_direction_sha256": self.store.artifact(session_id, "design-direction")["sha256"],
            "files": {name: {"path": artifact["path"], "sha256": artifact["sha256"]} for name, artifact in file_artifacts.items()},
            "responsive_targets_px": [1440, 768, 390],
            "screenshots": screenshots,
            "limitations": rendering_limitations,
            "human_approval": "pending",
        }
        manifest_artifact = self.store.write_artifact(session_id, "mockup-manifest", f"{revision_dir}/mockup-manifest.json", _json_bytes(manifest))
        self.store.set_metadata(session_id, "mockup_revision", revision)
        self.store.set_metadata(session_id, "mockup_summary", generation_summary)
        self.store.transition(session_id, Phase.AWAITING_MOCKUP_REVIEW, {"revision": revision, "manifest_sha256": manifest_artifact["sha256"]})
        return manifest

    def review_mockup(self, session_id: str, *, action: str, note: str = "", human_confirmation: bool) -> dict[str, Any]:
        session = self.store.get_session(session_id)
        if action not in {"approve", "revise", "reject"}:
            raise ValueError("Mockup review action must be approve, revise, or reject.")
        reviewable_phases = {Phase.AWAITING_MOCKUP_REVIEW}
        if action == "revise":
            reviewable_phases.update({Phase.AWAITING_IMPLEMENTATION_APPROVAL, Phase.PATCH_READY})
        if session.phase not in reviewable_phases:
            raise WorkflowBlocked("There is no mockup available for this review action.")
        if action in {"revise", "reject"} and not note.strip():
            raise ValueError("Provide a short note for a revision or rejection.")
        if not human_confirmation:
            raise ValueError("Mockup review requires an interactive human confirmation.")
        revision = int(session.metadata["mockup_revision"])
        decision_id = f"mockup-review-{revision:03d}-{action}"
        self.store.add_decision(session_id, decision_id, {"kind": "mockup_review", "action": action, "note": note.strip(), "revision": revision, "decided_by": "human"})
        if action == "revise":
            self.store.revoke_approvals(session_id, ("mockup", "implementation", "patch_application"), "A revised mockup invalidates prior mockup and implementation approvals.")
            self.store.set_metadata(session_id, "mockup_revision_note", note.strip())
            self.store.transition(session_id, Phase.MOCKUP_REVISION, {"revision": revision, "note": note.strip()})
            return {"action": action, "phase": Phase.MOCKUP_REVISION.value, "revision": revision + 1}
        if action == "reject":
            self.store.revoke_approvals(session_id, ("design_direction", "mockup", "implementation", "patch_application"), "Human rejected the mockup and returned to direction selection.")
            self.store.transition(session_id, Phase.AWAITING_DIRECTION, {"revision": revision, "rejection_note": note.strip()})
            return {"action": action, "phase": Phase.AWAITING_DIRECTION.value}

        manifest_artifact = self.store.artifact(session_id, "mockup-manifest")
        self.store.add_approval(Approval(
            session_id=session_id,
            approval_type="mockup",
            artifact_name="mockup-manifest",
            artifact_sha256=manifest_artifact["sha256"],
            approved_scope=(f"mockups/revision-{revision:03d}",),
            timestamp=utc_now(),
            human_confirmation=True,
            decision_ids=(decision_id,),
        ))
        manifest = json.loads(Path(manifest_artifact["path"]).read_text(encoding="utf-8"))
        direction = _read_json_artifact(self.store, session_id, "design-direction")
        specification = {
            "schema_version": 1,
            "approved_mockup_revision": revision,
            "approved_mockup_sha256": manifest_artifact["sha256"],
            "visual_changes": [direction["visual_appearance"], note.strip() or "Follow the approved prototype artifacts."],
            "behavioral_changes": [direction["behavior_and_interaction"]],
            "affected_scope": direction["scope"],
            "design_tokens_path": manifest["files"]["design-tokens.json"]["path"],
            "responsive_requirements": ["1440px desktop", "768px tablet", "390px mobile"],
            "accessibility_requirements": ["Semantic HTML", "Keyboard focus visibility", "Reduced-motion support", "Manual WCAG 2.2 AA review where applicable"],
            "explicitly_prohibited": ["Unapproved route or navigation changes", "Backend/API contract changes", "Framework or state-management changes", "Dependency changes", "Unrelated refactoring", "Unapproved workflow changes"],
            "acceptance_criteria": ["Match the approved mockup within the approved scope", "Preserve unapproved behavior and backend contracts", "Verify target viewport layouts", "Report tests and remaining unverified areas"],
            "implementation_risks": ["Template colors and copy are illustrative until confirmed against rendered target evidence."],
        }
        spec_artifact = self.store.write_artifact(session_id, "implementation-spec", "decisions/implementation-spec.json", _json_bytes(specification))
        spec_md = _implementation_spec_markdown(specification)
        self.store.write_artifact(session_id, "implementation-spec-md", "decisions/implementation-spec.md", spec_md.encode())
        self.store.transition(session_id, Phase.MOCKUP_APPROVED, {"revision": revision, "approval_decision": decision_id})
        self.store.transition(session_id, Phase.AWAITING_IMPLEMENTATION_APPROVAL, {"specification_sha256": spec_artifact["sha256"]})
        return {"action": action, "phase": Phase.AWAITING_IMPLEMENTATION_APPROVAL.value, "specification_sha256": spec_artifact["sha256"]}

    def plan_implementation(self, session_id: str, *, files: list[str] | None = None, new_files: list[str] | None = None, use_codex: bool = False) -> dict[str, Any]:
        session = self.store.get_session(session_id)
        if session.phase != Phase.AWAITING_IMPLEMENTATION_APPROVAL:
            raise WorkflowBlocked("Implementation planning requires an approved mockup and implementation specification.")
        spec_record = self.store.artifact(session_id, "implementation-spec")
        specification = _read_json_artifact(self.store, session_id, "implementation-spec")
        specification["sha256"] = spec_record["sha256"]
        plan = create_implementation_plan(Path(session.project_root), specification, files=files, new_files=new_files, use_codex=use_codex, backend=self.backend)
        self.store.revoke_approvals(session_id, ("implementation", "patch_application"), "The implementation plan was changed.")
        plan_artifact = self.store.write_artifact(session_id, "implementation-plan", "decisions/implementation-plan.json", _json_bytes(plan))
        plan_markdown = _implementation_plan_markdown(plan)
        self.store.write_artifact(session_id, "implementation-plan-md", "decisions/implementation-plan.md", plan_markdown.encode())
        plan["plan_sha256"] = plan_artifact["sha256"]
        return plan

    def approve_implementation(self, session_id: str, *, human_confirmation: bool) -> dict[str, Any]:
        session = self.store.get_session(session_id)
        if session.phase != Phase.AWAITING_IMPLEMENTATION_APPROVAL:
            raise WorkflowBlocked("Implementation approval requires AWAITING_IMPLEMENTATION_APPROVAL.")
        if not human_confirmation:
            raise ValueError("Implementation requires an explicit human approval.")
        plan_record = self.store.artifact(session_id, "implementation-plan")
        plan = _read_json_artifact(self.store, session_id, "implementation-plan")
        scope = tuple(plan["approved_scope"])
        if not scope or set(scope) != set(plan["baseline_sha256"]):
            raise WorkflowBlocked("The implementation plan has no valid exact file scope.")
        current_spec = self.store.artifact(session_id, "implementation-spec")
        if plan.get("specification_sha256") != current_spec["sha256"]:
            raise WorkflowBlocked("The implementation plan is stale. Recreate it against the current approved specification.")
        if _current_baselines(Path(session.project_root), plan) != plan["baseline_sha256"]:
            raise WorkflowBlocked("A planned file changed after the plan was created. Recreate and review the implementation plan.")
        direction_approval = self.store.latest_valid_approval(session_id, "design_direction", "design-direction")
        mockup_approval = self.store.latest_valid_approval(session_id, "mockup", "mockup-manifest")
        if not direction_approval or not mockup_approval:
            raise WorkflowBlocked("A valid human design-direction and mockup approval are required.")
        specification = _read_json_artifact(self.store, session_id, "implementation-spec")
        if specification.get("approved_mockup_sha256") != mockup_approval.artifact_sha256:
            raise WorkflowBlocked("The current implementation specification does not match the approved mockup revision.")
        decision_id = f"implementation-approval-{utc_now().replace(':', '').replace('-', '')}"
        self.store.add_decision(session_id, decision_id, {"kind": "implementation_approval", "scope": list(scope), "plan_sha256": plan_record["sha256"], "decided_by": "human"})
        self.store.add_approval(Approval(
            session_id=session_id,
            approval_type="implementation",
            artifact_name="implementation-plan",
            artifact_sha256=plan_record["sha256"],
            approved_scope=scope,
            timestamp=utc_now(),
            human_confirmation=True,
            decision_ids=tuple([decision_id, *mockup_approval.decision_ids]),
        ))
        self.store.transition(session_id, Phase.IMPLEMENTING, {"approval_decision": decision_id, "approved_scope": list(scope)})
        return {"status": "authorized", "scope": list(scope), "plan_sha256": plan_record["sha256"], "implementation_started": False}

    def implement(self, session_id: str) -> dict[str, Any]:
        session = self.store.get_session(session_id)
        if session.phase != Phase.IMPLEMENTING:
            raise WorkflowBlocked("Implementation has not been explicitly authorized.")
        approval = self.store.latest_valid_approval(session_id, "implementation", "implementation-plan")
        if not approval:
            raise WorkflowBlocked("No valid human implementation approval matches the current plan.")
        if not self.store.latest_valid_approval(session_id, "design_direction", "design-direction") or not self.store.latest_valid_approval(session_id, "mockup", "mockup-manifest"):
            raise WorkflowBlocked("The approved design direction or mockup has changed; implementation authorization is no longer valid.")
        plan = _read_json_artifact(self.store, session_id, "implementation-plan")
        if set(approval.approved_scope) != set(plan["approved_scope"]):
            raise WorkflowBlocked("The implementation approval scope does not match the current plan.")
        specification_artifact = self.store.artifact(session_id, "implementation-spec")
        if plan.get("specification_sha256") != specification_artifact["sha256"]:
            raise WorkflowBlocked("The implementation plan is stale. Recreate and reapprove it.")
        started_at = utc_now()
        try:
            patch, manifest = execute_implementation(Path(session.project_root), plan, backend=self.backend)
            patch_artifact = self.store.write_artifact(session_id, "implementation-patch", "patches/implementation.patch", patch)
            manifest["patch_path"] = patch_artifact["path"]
            self.store.write_artifact(session_id, "implementation-result", "patches/implementation-result.json", _json_bytes(manifest))
            self.store.add_execution(session_id, "frontend_implementer", "patch_ready", {"changed_files": manifest["changed_files"], "patch_sha256": manifest["patch_sha256"]}, started_at)
            self.store.transition(session_id, Phase.PATCH_READY, {"changed_files": manifest["changed_files"], "patch_sha256": manifest["patch_sha256"]})
            return manifest
        except Exception as error:
            self.store.add_execution(session_id, "frontend_implementer", "failed", {"error_category": type(error).__name__, "message": _safe_failure(str(error))}, started_at)
            self._fail(session_id, error, "implementation")
            raise

    def approve_patch_application(self, session_id: str, *, human_confirmation: bool) -> dict[str, Any]:
        session = self.store.get_session(session_id)
        if session.phase != Phase.PATCH_READY:
            raise WorkflowBlocked("There is no implementation patch ready for application.")
        if not human_confirmation:
            raise ValueError("Applying an implementation patch requires interactive human confirmation.")
        patch = self.store.artifact(session_id, "implementation-patch")
        result = _read_json_artifact(self.store, session_id, "implementation-result")
        if patch["sha256"] != result["patch_sha256"]:
            raise WorkflowBlocked("The generated patch does not match its implementation manifest.")
        plan = _read_json_artifact(self.store, session_id, "implementation-plan")
        implementation_approval = self.store.latest_valid_approval(session_id, "implementation", "implementation-plan")
        if not implementation_approval or set(result["changed_files"]) - set(implementation_approval.approved_scope):
            raise WorkflowBlocked("Patch changes exceed the approved implementation scope.")
        decision_id = f"patch-application-{utc_now().replace(':', '').replace('-', '')}"
        self.store.add_decision(session_id, decision_id, {"kind": "patch_application", "changed_files": result["changed_files"], "patch_sha256": patch["sha256"], "decided_by": "human"})
        self.store.add_approval(Approval(
            session_id=session_id,
            approval_type="patch_application",
            artifact_name="implementation-patch",
            artifact_sha256=patch["sha256"],
            approved_scope=tuple(result["changed_files"]),
            timestamp=utc_now(),
            human_confirmation=True,
            decision_ids=(decision_id,),
        ))
        return {"status": "patch_application_approved", "changed_files": result["changed_files"], "patch_sha256": patch["sha256"], "plan_scope": plan["approved_scope"]}

    def apply_patch(self, session_id: str) -> dict[str, Any]:
        session = self.store.get_session(session_id)
        if session.phase not in {Phase.PATCH_READY, Phase.APPLYING}:
            raise WorkflowBlocked("A generated patch must be ready before it can be applied.")
        patch_approval = self.store.latest_valid_approval(session_id, "patch_application", "implementation-patch")
        if not patch_approval:
            raise WorkflowBlocked("Human review and approval of the generated patch are required.")
        patch_artifact = self.store.artifact(session_id, "implementation-patch")
        manifest = _read_json_artifact(self.store, session_id, "implementation-result")
        plan = _read_json_artifact(self.store, session_id, "implementation-plan")
        if set(patch_approval.approved_scope) != set(manifest["changed_files"]):
            raise WorkflowBlocked("Patch application approval does not match the exact changed files.")
        if session.phase != Phase.APPLYING:
            self.store.transition(session_id, Phase.APPLYING)
        try:
            applied = apply_implementation_patch(Path(session.project_root), Path(patch_artifact["path"]).read_bytes(), manifest, plan)
            self.store.add_execution(session_id, "patch_applier", "applied", applied)
            self.store.set_metadata(session_id, "applied_files", applied["changed_files"])
            self.store.transition(session_id, Phase.VERIFYING, {"changed_files": applied["changed_files"]})
            return applied
        except Exception as error:
            self.store.add_execution(session_id, "patch_applier", "failed", {"error_category": type(error).__name__, "message": _safe_failure(str(error))})
            self._fail(session_id, error, "patch_application")
            raise

    def verify(self, session_id: str, commands: list[str] | None = None) -> dict[str, Any]:
        session = self.store.get_session(session_id)
        if session.phase != Phase.VERIFYING:
            raise WorkflowBlocked("Verification starts after a reviewed patch has been applied.")
        result = run_verification(Path(session.project_root), commands or [])
        plan = _read_json_artifact(self.store, session_id, "implementation-plan")
        changed = list(session.metadata.get("applied_files", []))
        reports = verification_reports(result, changed_files=changed, approved_scope=plan["approved_scope"])
        for filename, content in reports.items():
            self.store.write_artifact(session_id, filename.removesuffix(".md").removesuffix(".json").replace("-", "_"), f"reports/{filename}", content)
        self.store.set_metadata(session_id, "verification", result)
        self.store.add_execution(session_id, "quality_verification", result["status"], result)
        self.store.transition(session_id, Phase.COMPLETED, {"verification_status": result["status"], "commands_executed": len(commands or [])})
        return result

    def pause(self, session_id: str) -> Session:
        session = self.store.get_session(session_id)
        if session.phase in {Phase.PAUSED, Phase.COMPLETED, Phase.CANCELLED}:
            return session
        self.store.set_metadata(session_id, "paused_from", session.phase.value)
        return self.store.transition(session_id, Phase.PAUSED)

    def resume(self, session_id: str) -> Session:
        session = self.store.get_session(session_id)
        if session.phase == Phase.PAUSED:
            previous = Phase(session.metadata.get("paused_from", Phase.INITIALIZED.value))
            return self.store.transition(session_id, previous, {"resumed": True})
        if session.phase == Phase.FAILED:
            operation = session.metadata.get("failed_operation")
            previous = {
                "discovery": Phase.DISCOVERING,
                "audit": Phase.AUDITING,
                "mockup_generation": Phase.MOCKUP_REVISION,
                "implementation": Phase.IMPLEMENTING,
                "patch_application": Phase.PATCH_READY,
                "verification": Phase.VERIFYING,
            }.get(operation)
            if previous:
                return self.store.transition(session_id, previous, {"resumed_after_failure": operation})
        return session

    def status(self, session_id: str) -> dict[str, Any]:
        session = self.store.get_session(session_id)
        blocked = _blocked_requirements(session.phase)
        return {
            "session_id": session.id,
            "project_root": session.project_root,
            "state_dir": session.state_dir,
            "phase": session.phase.value,
            "title": session.title,
            "updated_at": session.updated_at,
            "blocked_requirements": blocked,
            "artifacts": self.store.list_artifacts(session_id),
            "recent_events": self.store.history(session_id)[-12:],
        }

    def _fail(self, session_id: str, error: Exception, operation: str) -> None:
        current = self.store.get_session(session_id).phase
        if Phase.FAILED in TRANSITIONS[current]:
            self.store.set_metadata(session_id, "failed_operation", operation)
            self.store.transition(session_id, Phase.FAILED, {"operation": operation, "error_category": type(error).__name__, "message": _safe_failure(str(error))})


def _read_json_artifact(store: WorkflowStore, session_id: str, name: str) -> dict[str, Any]:
    artifact = store.artifact(session_id, name)
    value = json.loads(Path(artifact["path"]).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Artifact {name} must contain a JSON object.")
    return value


def _merge_findings(*collections: tuple[Any, ...]) -> list[Any]:
    combined: dict[str, Any] = {}
    for collection in collections:
        for finding in collection:
            combined[finding.id] = finding
    return sorted(combined.values(), key=lambda item: item.id)


def _json_bytes(value: Any) -> bytes:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False).encode("utf-8")


def _implementation_spec_markdown(specification: dict[str, Any]) -> str:
    sections = [
        ("Approved visual changes", specification["visual_changes"]),
        ("Approved behavior changes", specification["behavioral_changes"]),
        ("Affected scope", [specification["affected_scope"]]),
        ("Design tokens", [specification["design_tokens_path"]]),
        ("Responsive requirements", specification["responsive_requirements"]),
        ("Accessibility requirements", specification["accessibility_requirements"]),
        ("Explicitly prohibited changes", specification["explicitly_prohibited"]),
        ("Acceptance criteria", specification["acceptance_criteria"]),
        ("Implementation risks", specification["implementation_risks"]),
    ]
    lines = [f"# Implementation specification · mockup revision {specification['approved_mockup_revision']:03d}", ""]
    for title, values in sections:
        lines.extend([f"## {title}", ""])
        lines.extend(f"- {value}" for value in values)
        lines.append("")
    lines.append("This specification records design approval only. It does not authorize production implementation.")
    return "\n".join(lines) + "\n"


def _implementation_plan_markdown(plan: dict[str, Any]) -> str:
    lines = ["# Implementation plan", "", plan["summary"], "", f"Plan source: `{plan['plan_source']}`", "", "## Exact file scope", ""]
    lines.extend(f"- `{item['path']}` — {item['change_class']}: {item['reason']}" for item in plan["files"])
    lines.extend(["", "## New files", ""])
    lines.extend(f"- `{item['path']}` — {item['change_class']}: {item['reason']}" for item in plan["new_files"])
    lines.extend(["", "## Suggested verification commands", ""])
    lines.extend(f"- `{item}` (not run during planning)" for item in plan["verification_commands"])
    if plan["risks"]:
        lines.extend(["", "## Risks", ""])
        lines.extend(f"- {item}" for item in plan["risks"])
    lines.extend(["", "Implementation remains blocked until a human approves this exact plan and file scope."])
    return "\n".join(lines) + "\n"


def _blocked_requirements(phase: Phase) -> list[str]:
    return {
        Phase.INITIALIZED: ["Run capability discovery."],
        Phase.CAPABILITIES_REVIEW: ["Run the independent technical and visual audit."],
        Phase.AUDIT_COMPLETED: ["Review the audit and record independent visual, behavioral, and scope decisions."],
        Phase.AWAITING_DIRECTION: ["Human design-direction approval is required before mockups."],
        Phase.DIRECTION_APPROVED: ["Generate a mockup from the approved direction."],
        Phase.AWAITING_MOCKUP_REVIEW: ["Human mockup review is required before implementation planning."],
        Phase.MOCKUP_APPROVED: ["Create a scoped implementation plan."],
        Phase.AWAITING_IMPLEMENTATION_APPROVAL: ["Review and explicitly approve the implementation plan and exact file paths."],
        Phase.IMPLEMENTING: ["Run the authorized Codex implementation in the isolated workspace."],
        Phase.PATCH_READY: ["Review the generated diff and approve patch application."],
        Phase.VERIFYING: ["Run explicit verification commands or document that verification was not performed."],
        Phase.COMPLETED: [],
        Phase.PAUSED: ["Resume the session to continue."],
        Phase.FAILED: ["Inspect the failure details and retry the failed phase after correcting the blocker."],
        Phase.CANCELLED: [],
        Phase.DISCOVERING: ["Discovery is in progress."],
        Phase.AUDITING: ["Audit is in progress."],
        Phase.GENERATING_MOCKUPS: ["Mockup generation is in progress."],
        Phase.MOCKUP_REVISION: ["Generate the next mockup revision."],
        Phase.APPLYING: ["Patch application is in progress."],
    }.get(phase, [])


def _safe_failure(value: str) -> str:
    import re

    return re.sub(r"(?i)(authorization|api[_-]?key|token|password)(\s*[=:]\s*)[^\s,;]+", r"\1\2[REDACTED]", value)[:400]
