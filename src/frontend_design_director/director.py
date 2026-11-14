"""Orchestrate persisted frontend discovery, audit, design, mockup, and implementation stages."""

from __future__ import annotations

import hashlib
import json
import tempfile
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from .auditing import AuditResult, run_codex_audit, run_static_audit
from .backend import AgentBackend
from .browser import BrowserUnavailable, DEPTH_VIEWPORTS, capture_mockup_screenshots, capture_screenshots
from .codex_backend import BackendFailure, BackendUnavailable, CodexCLIBackend
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


def _codex_audit_limitations(
    static_limitations: tuple[str, ...],
    codex_limitations: tuple[str, ...],
    *,
    visual_analysis_validated: bool,
    runtime_observations: bool,
) -> tuple[str, ...]:
    """Merge only run-level limits; keep source and specialist limits in their scoped reports."""
    merged: list[str] = []
    for limitation in static_limitations:
        if visual_analysis_validated and limitation.startswith((
            "Screenshots were captured, but no visual evaluator was run",
            "No rendered screenshots or equivalent browser evidence were available",
        )):
            continue
        if limitation.startswith("No project scripts, builds, dependency lifecycle hooks, or development servers were executed."):
            limitation = "No project build, test, or dependency-lifecycle scripts were executed; browser navigation did run the frontend page scripts."
        elif runtime_observations and limitation.startswith("No runtime, bundle-size, Web Vitals, network, or interaction measurements were collected."):
            limitation = "LCP, INP, CLS, and bundle-size measurements were not collected. Browser navigation timing and request data are single-run lab observations; the automated capture did not activate controls."
        merged.append(limitation)
    merged.extend(codex_limitations)
    return tuple(dict.fromkeys(merged))


def _codex_audit_recommendations(
    static_recommendations: tuple[str, ...],
    codex_recommendations: tuple[str, ...],
    *,
    visual_evidence_complete: bool,
) -> tuple[str, ...]:
    """Drop the static-only screenshot request after the visual coverage gate passes."""
    base = tuple(
        item for item in static_recommendations
        if not (visual_evidence_complete and item.startswith("Capture desktop (1440 px)"))
    )
    return tuple(dict.fromkeys((*base, *codex_recommendations)))


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
        if session.phase not in {Phase.CAPABILITIES_REVIEW, Phase.AWAITING_DIRECTION, Phase.AUDIT_COMPLETED, Phase.AUDIT_COMPLETED_WITH_LIMITATIONS, Phase.AUDIT_INCOMPLETE, Phase.AUDITING}:
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
        capture_routes: list[str] = []
        expected_routes: list[str] = []
        if browser_url:
            intelligence = build_project_intelligence(Path(session.project_root), discovery["project"])
            discovered_routes = renderable_route_candidates(intelligence)
            capture_routes = list(dict.fromkeys(route_paths if route_paths else discovered_routes))
            base_path = urlsplit(browser_url).path or "/"
            expected_routes = sorted(set([base_path, *capture_routes]))
            try:
                with tempfile.TemporaryDirectory(prefix="frontend-director-browser-") as temporary:
                    screenshot_directory = Path(temporary) / "screenshots"
                    captured = capture_screenshots(browser_url, screenshot_directory, allow_remote=allow_remote, route_paths=capture_routes, viewports=DEPTH_VIEWPORTS[depth])
                    for item in captured:
                        if item.get("evidence_type") != "rendered_browser_screenshot":
                            browser_capture_records.append(item)
                            limitations.append(f"Browser route `{item.get('route', '/')}` at `{item.get('viewport', 'unknown')}` could not be captured: {item.get('error', 'unknown navigation error')}")
                            continue
                        screenshot_path = Path(str(item.get("path", "")))
                        if not screenshot_path.is_file():
                            failure = {
                                **item,
                                "evidence_type": "browser_navigation_failure",
                                "error_classification": "missing_screenshot",
                                "error": "Screenshot capture returned a path that does not exist.",
                            }
                            browser_capture_records.append(failure)
                            limitations.append(f"Screenshot file was missing for `{item.get('route', '/')}` / `{item.get('viewport', 'unknown')}`.")
                            continue
                        image_integrity_error = _screenshot_integrity_error(item, screenshot_path)
                        if image_integrity_error:
                            item = {
                                **item,
                                "visual_evidence_status": "invalid_screenshot",
                                "capture_status": "captured_invalid",
                                "image_integrity_verified": False,
                                "image_integrity_error": image_integrity_error,
                            }
                        else:
                            item = {**item, "image_integrity_verified": True}
                        route_slug = item.get("route_slug", "home")
                        viewport_label = item.get("viewport_label", item["viewport"])
                        state_suffix = "-keyboard-focus" if item.get("interaction_state") == "keyboard_focus_after_one_tab" else ""
                        route_digest = hashlib.sha256(str(item.get("route", "/")).encode("utf-8")).hexdigest()[:6]
                        screenshot_name = f"{route_slug}-{route_digest}-{viewport_label}{state_suffix}.png"
                        artifact_name = f"screenshot-{route_slug}-{route_digest}-{viewport_label}{state_suffix}"
                        artifact = self.store.write_artifact(session_id, artifact_name, f"evidence/screenshots/{screenshot_name}", screenshot_path.read_bytes())
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
                category = "missing_screenshot" if isinstance(error, BrowserUnavailable) else "backend_invocation_failed"
                browser_capture_records.append({
                    "evidence_type": "browser_capture_failure",
                    "error_classification": category,
                    "error": f"{type(error).__name__}: {str(error)[:1000]}",
                    "routes_requested": expected_routes,
                    "viewports_requested": list(DEPTH_VIEWPORTS[depth]),
                })
                limitations.append(f"Browser evidence was unavailable: {type(error).__name__}: {str(error)[:500]}")
                requests.warning("Browser screenshot capture unavailable", context={"session_id": session_id, "error_category": type(error).__name__})
        else:
            limitations.append("Rendered browser evidence was not collected because no explicit --url was supplied. Source analysis cannot establish actual appearance or runtime behavior.")
        if browser_url:
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
        expected_pairs = sorted((route, viewport) for route in expected_routes for viewport in DEPTH_VIEWPORTS[depth])
        valid_pairs = {
            (str(item.get("route", "/")), str(item.get("viewport_label", item.get("viewport", "unknown"))))
            for item in screenshots
            if item.get("evidence_type") == "rendered_browser_screenshot"
            and item.get("visual_evidence_status", "valid") == "valid"
            and item.get("interaction_state", "default") == "default"
        }
        missing_pairs = sorted(set(expected_pairs) - valid_pairs)
        intelligence["coverage"].update({
            "expected_routes": len(expected_routes),
            "expected_viewports": list(DEPTH_VIEWPORTS[depth]) if browser_url else [],
            "expected_route_viewport_pairs": len(expected_pairs),
            "valid_route_viewport_pairs": len(valid_pairs),
            "missing_route_viewports": [{"route": route, "viewport": viewport} for route, viewport in missing_pairs],
            "invalid_screenshots": sum(item.get("visual_evidence_status") != "valid" for item in screenshots),
        })
        self.store.set_metadata(session_id, "frontend_intelligence", intelligence)
        self.store.set_metadata(session_id, "audit_depth", depth)
        self.store.write_artifact(session_id, "frontend-intelligence", "reports/frontend-intelligence.json", _json_bytes(intelligence))
        static_result = run_static_audit(Path(session.project_root), discovery["project"], screenshots)
        observed_findings = runtime_findings(intelligence)
        if observed_findings:
            static_result = replace(static_result, findings=tuple(_merge_findings(static_result.findings, tuple(observed_findings))))
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
                visual_evidence_complete = (
                    bool(codex_result.visual_delivery.get("validated"))
                    and codex_result.visual_delivery.get("route_viewports_assessed", 0) >= len(expected_pairs)
                )
                result = AuditResult(
                    findings=tuple(_merge_findings(static_result.findings, codex_result.findings)),
                    limitations=tuple(dict.fromkeys((
                        *_codex_audit_limitations(
                            static_result.limitations,
                            codex_result.limitations,
                            visual_analysis_validated=visual_evidence_complete,
                            runtime_observations=bool(intelligence.get("runtime")),
                        ),
                        *limitations,
                    ))),
                    recommendations=_codex_audit_recommendations(
                        static_result.recommendations,
                        codex_result.recommendations,
                        visual_evidence_complete=visual_evidence_complete,
                    ),
                    screenshots=tuple(screenshots),
                    backend_used="codex_cli_plus_static",
                    visual_analysis=codex_result.visual_analysis,
                    specialist_runs=codex_result.specialist_runs,
                    diagnostics=codex_result.diagnostics,
                    security_data_flows=static_result.security_data_flows,
                    specialist_assessments=codex_result.specialist_assessments,
                )
            except Exception as error:
                category = "model_timeout" if isinstance(error, TimeoutError) else "backend_invocation_failed"
                result = AuditResult(
                    findings=static_result.findings,
                    limitations=tuple(dict.fromkeys((*static_result.limitations, *limitations, f"Codex specialist audit could not run: {type(error).__name__}: {str(error)[:500]}"))),
                    recommendations=static_result.recommendations,
                    screenshots=tuple(screenshots),
                    backend_used="static_codex_unavailable",
                    visual_analysis={},
                    security_data_flows=static_result.security_data_flows,
                    diagnostics=({
                        "specialist": "audit_coordinator",
                        "error_classification": category,
                        "failure_location": "audit.coordinator",
                        "retry_attempts": 0,
                        "message": str(error)[:1000],
                        **(dict(getattr(error, "diagnostic", {}) or {})),
                    },),
                )
        else:
            if audit_instructions:
                limitations.append("Human audit instructions were preserved in the session but not interpreted by the deterministic source rules; use the explicit Codex audit option if you want model-assisted interpretation.")
            if limitations:
                result = replace(static_result, limitations=tuple(dict.fromkeys((*static_result.limitations, *limitations))), screenshots=tuple(screenshots), backend_used="static", visual_analysis={})

        completion_reasons: list[str] = []
        blockers: list[str] = []
        if browser_url:
            if missing_pairs:
                sample = ", ".join(f"{route} / {viewport}" for route, viewport in missing_pairs[:8])
                blockers.append(f"{len(missing_pairs)} requested route/viewport pair(s) lack a valid screenshot: {sample}.")
            if not expected_pairs:
                blockers.append("No route/viewport pairs were selected for browser capture.")
        else:
            completion_reasons.append("No explicit browser URL was supplied; rendered appearance and runtime behavior remain unverified.")
            if use_codex:
                blockers.append("Codex-assisted comprehensive review requires rendered browser evidence; supply --url and retry.")

        if use_codex:
            required_specialists = ("frontend_code_auditor", "frontend_ux_auditor", "frontend_visual_auditor")
            specialist_by_name = {item.get("specialist"): item for item in result.specialist_runs}
            for role in required_specialists:
                run = specialist_by_name.get(role)
                if not run or run.get("status") != "completed":
                    blockers.append(f"Required specialist `{role}` did not complete both structured passes.")
            if not result.visual_analysis:
                blockers.append("No screenshot-backed visual analysis passed evidence validation.")
        else:
            completion_reasons.append("Codex specialist interpretation was not requested; appearance and specialist findings are not semantically verified.")

        valid_visual_screenshots = [
            item for item in screenshots
            if item.get("evidence_type") == "rendered_browser_screenshot"
            and item.get("visual_evidence_status", "valid") == "valid"
            and item.get("interaction_state", "default") == "default"
        ]
        visual_run = next((item for item in result.specialist_runs if item.get("specialist") == "frontend_visual_auditor"), {})
        visual_diagnostic = next((item for item in result.diagnostics if item.get("specialist") == "frontend_visual_auditor"), {})
        attached_details = visual_diagnostic.get("invocation", {}).get("images_attached", [])
        submitted_count = visual_run.get("images_submitted", len(attached_details))
        attached_count = visual_run.get("images_attached", 0) if visual_run.get("first_pass") in {"valid", "partial"} else 0
        visual_delivery = {
            "screenshots_captured": len(valid_visual_screenshots),
            "screenshot_references": [
                {
                    "path": item["path"],
                    "route": item.get("route", "/"),
                    "viewport": item.get("viewport_label", item.get("viewport")),
                    "image_dimensions": item.get("image_dimensions"),
                    "image_format": item.get("image_format"),
                    "sha256": item.get("image_sha256"),
                    "integrity_verified": item.get("image_integrity_verified", False),
                }
                for item in valid_visual_screenshots
            ],
            "screenshots_submitted": submitted_count,
            "attached_to_visual_backend": attached_count > 0,
            "screenshots_attached": attached_count,
            "interpreted": bool(result.visual_analysis),
            "validated": bool(result.visual_analysis) and visual_run.get("status") == "completed",
            "route_viewports_assessed": len({(item.get("route"), item.get("viewport")) for item in result.visual_analysis.get("route_assessments", [])}),
        }
        intelligence["coverage"].update({
            "screenshots_attached_to_visual": attached_count,
            "visual_analysis_interpreted": visual_delivery["interpreted"],
            "visual_analysis_validated": visual_delivery["validated"],
            "visual_route_viewports_assessed": visual_delivery["route_viewports_assessed"],
        })
        if browser_url and not use_codex:
            completion_reasons.append("Browser screenshots were captured, but no visual reasoning pass interpreted them.")
        if any(item.get("visual_evidence_status") not in (None, "valid") for item in screenshots):
            completion_reasons.append("One or more saved screenshots failed visual-evidence validation and were not attached to the visual auditor.")
        completion_status = "incomplete" if blockers else "completed_with_limitations" if completion_reasons else "completed"
        retry_recommendation = None
        if completion_status == "incomplete":
            target = str(Path(session.project_root))
            if browser_url:
                parsed = urlsplit(browser_url)
                safe_url = urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", ""))
                retry_recommendation = f"Review partial findings, correct the listed evidence or backend gaps, then retry with: frontend-director audit --project {target} --url {safe_url} --depth {depth} --codex"
            else:
                retry_recommendation = f"Start or attach to the project server, then retry: frontend-director audit --project {target} --url <verified-local-url> --depth {depth} --codex"
            limitations.append("Audit status is incomplete. " + " ".join(blockers))
            limitations.append(retry_recommendation)
        elif completion_reasons:
            limitations.extend(completion_reasons)
        result = replace(
            result,
            limitations=tuple(dict.fromkeys(limitations + list(result.limitations))),
            completion_status=completion_status,
            completion_reasons=tuple(dict.fromkeys((*completion_reasons, *blockers))),
            visual_delivery=visual_delivery,
        )
        findings = list(result.findings)
        self.store.replace_findings(session_id, findings)
        reports = audit_reports(findings, result, discovery["project"], intelligence)
        reports.update(intelligence_reports(intelligence))
        if result.visual_analysis:
            reports["visual-analysis.json"] = _json_bytes(result.visual_analysis)
        reports["audit-execution.json"] = _json_bytes({
            "completion_status": completion_status,
            "completion_reasons": list(result.completion_reasons),
            "depth": depth,
            "browser_url": (lambda parsed: urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", "")))(urlsplit(browser_url)) if browser_url else None,
            "expected_routes": expected_routes,
            "expected_viewports": list(DEPTH_VIEWPORTS[depth]) if browser_url else [],
            "expected_route_viewport_pairs": expected_pairs,
            "missing_route_viewports": [{"route": route, "viewport": viewport} for route, viewport in missing_pairs],
            "visual_delivery": visual_delivery,
            "specialists": list(result.specialist_runs),
            "specialist_assessments": list(result.specialist_assessments),
            "retry_recommendation": retry_recommendation,
        })
        reports["backend-diagnostics.json"] = _json_bytes({
            "schema_version": 1,
            "diagnostics": list(result.diagnostics),
        })
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
            "completion_status": completion_status,
            "completion_reasons": list(result.completion_reasons),
            "specialists": list(result.specialist_runs),
            "visual_delivery": visual_delivery,
            "retry_recommendation": retry_recommendation,
            "human_instructions_present": bool(audit_instructions),
            "revision": report_revision,
            "coverage": intelligence["coverage"],
            "reports": sorted(reports),
        }
        self.store.set_metadata(session_id, "audit", summary)
        phase = {
            "completed": Phase.AUDIT_COMPLETED,
            "completed_with_limitations": Phase.AUDIT_COMPLETED_WITH_LIMITATIONS,
            "incomplete": Phase.AUDIT_INCOMPLETE,
        }[completion_status]
        summary["workflow_phase"] = phase.value
        self.store.set_metadata(session_id, "audit", summary)
        self.store.transition(session_id, phase)
        activity.info("Frontend audit finished", context={"session_id": session_id, "findings": len(findings), "backend": result.backend_used, "completion_status": completion_status})
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
        if session.phase not in {Phase.AUDIT_COMPLETED, Phase.AUDIT_COMPLETED_WITH_LIMITATIONS, Phase.AWAITING_DIRECTION}:
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
        if session.phase in {Phase.AUDIT_COMPLETED, Phase.AUDIT_COMPLETED_WITH_LIMITATIONS}:
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


def _screenshot_integrity_error(metadata: dict[str, Any], path: Path) -> str | None:
    """Check that a captured PNG still matches its recorded dimensions and digest."""
    try:
        content = path.read_bytes()
    except OSError as error:
        return f"Screenshot could not be read: {type(error).__name__}."
    if not content.startswith(b"\x89PNG\r\n\x1a\n") or len(content) < 24:
        return "Screenshot is not a readable PNG file."
    dimensions = metadata.get("image_dimensions")
    actual = {
        "width": int.from_bytes(content[16:20], "big"),
        "height": int.from_bytes(content[20:24], "big"),
    }
    if not isinstance(dimensions, dict) or dimensions != actual:
        return "Screenshot dimensions do not match the capture manifest."
    document_height = metadata.get("document", {}).get("height") if isinstance(metadata.get("document"), dict) else None
    minimum_height = min(metadata.get("height", 1), document_height) if isinstance(document_height, int) and document_height > 0 else 1
    if actual["width"] != metadata.get("width") or actual["height"] < minimum_height:
        return "Screenshot dimensions do not cover the requested viewport."
    if metadata.get("image_sha256") and hashlib.sha256(content).hexdigest() != metadata["image_sha256"]:
        return "Screenshot SHA-256 does not match the capture manifest."
    if metadata.get("image_byte_size") and len(content) != metadata["image_byte_size"]:
        return "Screenshot size does not match the capture manifest."
    return None


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
        Phase.AUDIT_COMPLETED_WITH_LIMITATIONS: ["Review the audit limitations before choosing design direction."],
        Phase.AUDIT_INCOMPLETE: ["Review partial results and retry the audit after correcting evidence or specialist failures."],
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
