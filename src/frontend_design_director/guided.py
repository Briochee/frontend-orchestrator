"""Interactive, persistent guidance over the director's existing approval-gated stages."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Callable

from .collaboration import CollaborationMode
from .director import FrontendDesignDirector
from .models import Phase
from .storage import WorkflowStore


Input = Callable[[str], str]
Output = Callable[[str], Any]


def run_guided_workflow(
    director: FrontendDesignDirector,
    store: WorkflowStore,
    session_id: str,
    *,
    use_codex: bool = False,
    browser_url: str | None = None,
    allow_remote: bool = False,
    exercise_safe_interactions: bool | None = None,
    route_paths: tuple[str, ...] | list[str] = (),
    depth: str = "deep",
    collaboration_mode: CollaborationMode | str | None = None,
    allowed_secondary_providers: tuple[str, ...] | list[str] | None = None,
    start_command: tuple[str, ...] | list[str] | None = None,
    server_url: str | None = None,
    input_fn: Input = input,
    output_fn: Output = print,
) -> dict[str, Any]:
    """Guide a user between phases while preserving pending choices on interruption."""
    session = store.get_session(session_id)
    if session.project_root != str(Path(session.project_root).resolve()):
        raise ValueError("Guided session project root is no longer canonical.")
    state = dict(session.metadata.get("guided_session", {}))
    if state.get("status") == "ended":
        raise ValueError("This guided session was explicitly ended. Start a new session or select another session.")
    mode = CollaborationMode(
        collaboration_mode
        or session.metadata.get("collaboration_mode", CollaborationMode.COMPREHENSIVE.value)
    )
    existing_secondary = session.metadata.get("allowed_secondary_providers", [])
    secondary_providers = list(allowed_secondary_providers if allowed_secondary_providers is not None else existing_secondary)
    exercise_interactions = bool(
        session.metadata.get("exercise_safe_interactions", False)
        if exercise_safe_interactions is None else exercise_safe_interactions
    )
    if set(secondary_providers) - {"claude"}:
        raise ValueError("Guided workflow has an unsupported secondary provider.")
    if allowed_secondary_providers and secondary_providers and not use_codex:
        raise ValueError("Secondary-provider review requires the primary Codex audit (`--codex`).")
    store.set_metadata(session_id, "collaboration_mode", mode.value)
    store.set_metadata(session_id, "allowed_secondary_providers", secondary_providers)
    store.set_metadata(session_id, "exercise_safe_interactions", exercise_interactions)
    _save_state(store, session_id, status="active", pending_action=state.get("pending_action"))
    output_fn(f"Frontend Design Director · {session.title}\nSession: {session.id}\nPhase: {session.phase.value}\n")

    while True:
        session = store.get_session(session_id)
        phase = session.phase
        if phase == Phase.INITIALIZED:
            output_fn("Reading project files and available tooling. No project scripts will be executed.")
            director.discover(session_id)
            _save_state(store, session_id, last_completed="discovery", pending_action="review_discovery")
            _print_stage_result(output_fn, store, session_id, "Discovery", "capability-inventory")
            continue
        if phase == Phase.DISCOVERING:
            output_fn("Resuming interrupted read-only discovery.")
            director.discover(session_id)
            continue
        if phase == Phase.AUDITING:
            output_fn("An audit was interrupted before its report was committed. Re-running the read-only audit.")
            _run_audit(director, session_id, use_codex, browser_url, allow_remote, exercise_interactions, route_paths, depth, start_command, server_url, input_fn, output_fn)
            _print_stage_result(output_fn, store, session_id, "Audit", "audit-summary")
            continue
        if phase == Phase.GENERATING_MOCKUPS:
            output_fn("A mockup generation was interrupted. You can retry it after reviewing the current state.")
        action = _prompt_action(phase, input_fn, output_fn)
        if action is None:
            _save_state(store, session_id, status="waiting_for_input", pending_action=_pending_action(phase))
            output_fn("No input was received. The workflow is still open; run `frontend-director guide --project <path> --session " + session_id + "` to resume.")
            return {"session_id": session_id, "status": "waiting_for_input", "phase": phase.value}
        action = action.casefold().strip()
        if action in {"end", "end workflow", "finish session", "terminate workflow"}:
            _save_state(store, session_id, status="ended", pending_action=None, ended_by="human")
            output_fn("Guided workflow ended. Session artifacts and decisions remain available.")
            return {"session_id": session_id, "status": "ended", "phase": phase.value}
        if action in {"pause", "p"}:
            paused = director.pause(session_id)
            _save_state(store, session_id, status="paused", pending_action=_pending_action(phase))
            output_fn(f"Session paused at {paused.phase.value}. Resume with `frontend-director guide --project <path> --session {session_id}`.")
            return {"session_id": session_id, "status": "paused", "phase": paused.phase.value}
        if action in {"instructions", "add instructions", "brief"}:
            stage = _instruction_stage(phase)
            try:
                instruction = _read_instruction_block(input_fn, output_fn, stage)
            except EOFError:
                _save_state(store, session_id, status="waiting_for_input", pending_action=_pending_action(phase))
                output_fn("Input ended while saving instructions. The prior state is preserved; resume the guide to continue.")
                return {"session_id": session_id, "status": "waiting_for_input", "phase": phase.value}
            if instruction:
                director.record_guided_instruction(session_id, instruction, stage=stage)
                output_fn(_instruction_saved_message(stage, phase))
            continue
        if action in {"review", "review reports", "artifacts"}:
            _review_current(store, session_id, phase, output_fn)
            continue
        if action in {"revisit", "revisit audit", "re-audit", "new audit"}:
            if phase not in {Phase.AUDIT_COMPLETED, Phase.AUDIT_COMPLETED_WITH_LIMITATIONS, Phase.AUDIT_INCOMPLETE, Phase.AWAITING_DIRECTION, Phase.COMPLETED, Phase.CAPABILITIES_REVIEW}:
                output_fn("A new audit cannot start from this phase; finish or review the pending approval stage first.")
                continue
            if phase == Phase.COMPLETED:
                director.discover(session_id)
            _run_audit(director, session_id, use_codex, browser_url, allow_remote, exercise_interactions, route_paths, depth, start_command, server_url, input_fn, output_fn)
            _print_stage_result(output_fn, store, session_id, "Updated audit", "audit-summary")
            continue

        try:
            if phase == Phase.CAPABILITIES_REVIEW and action in {"continue", "audit", "run audit"}:
                _run_audit(director, session_id, use_codex, browser_url, allow_remote, exercise_interactions, route_paths, depth, start_command, server_url, input_fn, output_fn)
                _print_stage_result(output_fn, store, session_id, "Audit", "audit-summary")
            elif phase in {Phase.AUDIT_COMPLETED, Phase.AUDIT_COMPLETED_WITH_LIMITATIONS, Phase.AWAITING_DIRECTION} and action in {"continue", "choose direction", "design direction"}:
                _collect_direction(director, session_id, input_fn, output_fn)
            elif phase in {Phase.DIRECTION_APPROVED, Phase.MOCKUP_REVISION, Phase.GENERATING_MOCKUPS} and action in {"continue", "mockup", "generate mockup", "retry generation"}:
                instructions = director._stage_instructions(session_id, "mockup")
                brief = "\n\n".join(item for item in (instructions, _direction_constraints(store, session_id)) if item)
                result = director.generate_mockup(session_id, brief=brief, revision_note=store.get_session(session_id).metadata.get("mockup_revision_note", ""), use_codex=use_codex)
                _save_state(store, session_id, last_completed="mockup", pending_action="review_mockup")
                output_fn(f"Mockup revision {result['revision']} is ready. Review the artifacts before approving it.")
                for item in result.get("artifacts", {}).values():
                    output_fn(f"- {item.get('path')}")
            elif phase == Phase.AWAITING_MOCKUP_REVIEW and action in {"approve mockup", "approve", "revise mockup", "revise", "reject mockup", "reject"}:
                _review_mockup(director, session_id, action, input_fn, output_fn)
            elif phase == Phase.MOCKUP_APPROVED and action in {"continue", "plan", "implementation plan"}:
                files = _csv_paths(_read_optional(input_fn, output_fn, "Existing project-relative files to include in the proposed plan (comma-separated; blank lets the planner select)"))
                new_files = _csv_paths(_read_optional(input_fn, output_fn, "New project-relative files, if any (comma-separated; blank for none)"))
                result = director.plan_implementation(session_id, files=files or None, new_files=new_files or None, use_codex=use_codex)
                output_fn(f"Implementation plan created for {len(result.get('approved_scope', []))} file(s). Review it; implementation remains blocked pending explicit authorization.")
                _print_stage_result(output_fn, store, session_id, "Implementation plan", "implementation-plan-md")
            elif phase == Phase.AWAITING_IMPLEMENTATION_APPROVAL and action in {"approve implementation", "authorize implementation"}:
                artifact = store.artifact(session_id, "implementation-plan")
                plan = json.loads(Path(artifact["path"]).read_text(encoding="utf-8"))
                phrase = f"AUTHORIZE IMPLEMENTATION {session_id[:8]}"
                _confirm(input_fn, output_fn, f"This authorizes Codex to modify an isolated snapshot within this exact scope:\n" + "\n".join(f"- {item}" for item in plan["approved_scope"]) + f"\nPlan SHA-256: {artifact['sha256']}\nType {phrase}", phrase)
                director.approve_implementation(session_id, human_confirmation=True)
                output_fn("Implementation authorized for the recorded scope. This does not authorize applying a patch to the project.")
            elif phase == Phase.IMPLEMENTING and action in {"continue", "implement", "generate patch"}:
                result = director.implement(session_id)
                output_fn(f"Patch generated for: {', '.join(result.get('changed_files', []))}. Target project files are still unchanged.")
            elif phase == Phase.PATCH_READY and action in {"apply patch", "apply"}:
                patch = store.artifact(session_id, "implementation-patch")
                manifest = json.loads(Path(store.artifact(session_id, "implementation-result")["path"]).read_text(encoding="utf-8"))
                phrase = f"APPLY PATCH {session_id[:8]}"
                _confirm(input_fn, output_fn, f"Review patch {patch['path']} (SHA-256 {patch['sha256']}). Changed files: {', '.join(manifest.get('changed_files', []))}. Type {phrase}", phrase)
                director.approve_patch_application(session_id, human_confirmation=True)
                result = director.apply_patch(session_id)
                output_fn(f"Approved patch applied to: {', '.join(result.get('changed_files', []))}.")
            elif phase == Phase.VERIFYING and action in {"continue", "verify", "verify without commands"}:
                command_text = _read_optional(input_fn, output_fn, "Optional exact verification commands, separated by ` ; ` (blank runs report-only verification)")
                commands = [part.strip() for part in command_text.split(";") if part.strip()]
                if commands:
                    _confirm(input_fn, output_fn, "These commands may execute project code:\n" + "\n".join(f"- {item}" for item in commands) + "\nType RUN VERIFICATION", "RUN VERIFICATION")
                result = director.verify(session_id, commands)
                output_fn(f"Verification status: {result['status']}. See the persisted final report for checks and limitations.")
            elif phase == Phase.COMPLETED and action in {"new audit", "another cycle", "continue"}:
                director.discover(session_id)
                _run_audit(director, session_id, use_codex, browser_url, allow_remote, exercise_interactions, route_paths, depth, start_command, server_url, input_fn, output_fn)
                _print_stage_result(output_fn, store, session_id, "Next audit cycle", "audit-summary")
            elif phase == Phase.PAUSED and action in {"continue", "resume"}:
                director.resume(session_id)
            elif phase == Phase.FAILED and action in {"continue", "retry", "resume"}:
                director.resume(session_id)
            else:
                output_fn(f"Action `{action}` is not available in phase {phase.value}. Choose one of the listed actions.")
                continue
        except EOFError:
            _save_state(store, session_id, status="waiting_for_input", pending_action=_pending_action(phase))
            output_fn("Input ended. The workflow remains open and can resume from this decision.")
            return {"session_id": session_id, "status": "waiting_for_input", "phase": phase.value}
        _save_state(store, session_id, status="active", pending_action=_pending_action(store.get_session(session_id).phase), last_action=action)


def _prompt_action(phase: Phase, input_fn: Input, output_fn: Output) -> str | None:
    choices: dict[Phase, list[str]] = {
        Phase.CAPABILITIES_REVIEW: ["continue", "instructions", "review", "pause", "end"],
        Phase.AUDIT_COMPLETED: ["continue", "re-audit", "instructions", "review", "pause", "end"],
        Phase.AUDIT_COMPLETED_WITH_LIMITATIONS: ["continue", "re-audit", "instructions", "review", "pause", "end"],
        Phase.AUDIT_INCOMPLETE: ["re-audit", "instructions", "review", "pause", "end"],
        Phase.AWAITING_DIRECTION: ["continue", "re-audit", "instructions", "review", "pause", "end"],
        Phase.DIRECTION_APPROVED: ["continue", "instructions", "review", "pause", "end"],
        Phase.MOCKUP_REVISION: ["continue", "instructions", "review", "pause", "end"],
        Phase.GENERATING_MOCKUPS: ["continue", "instructions", "review", "pause", "end"],
        Phase.AWAITING_MOCKUP_REVIEW: ["approve mockup", "revise mockup", "reject mockup", "instructions", "review", "pause", "end"],
        Phase.MOCKUP_APPROVED: ["continue", "instructions", "review", "pause", "end"],
        Phase.AWAITING_IMPLEMENTATION_APPROVAL: ["approve implementation", "instructions", "review", "pause", "end"],
        Phase.IMPLEMENTING: ["continue", "instructions", "pause", "end"],
        Phase.PATCH_READY: ["apply patch", "instructions", "review", "pause", "end"],
        Phase.VERIFYING: ["continue", "instructions", "review", "pause", "end"],
        Phase.COMPLETED: ["new audit", "instructions", "review", "pause", "end"],
        Phase.PAUSED: ["continue", "instructions", "review", "end"],
        Phase.FAILED: ["continue", "instructions", "review", "pause", "end"],
        Phase.AUDITING: ["continue", "instructions", "review", "pause", "end"],
        Phase.APPLYING: ["instructions", "review", "pause", "end"],
        Phase.CANCELLED: ["instructions", "review", "end"],
    }
    options = choices.get(phase, ["review", "pause", "end"])
    output_fn(f"Current phase: {phase.value}\nNext actions: " + " · ".join(options))
    try:
        return input_fn("Action (or `instructions`, `revisit`, `pause`, `end`): ").strip()
    except EOFError:
        return None


def _run_audit(
    director: FrontendDesignDirector,
    session_id: str,
    use_codex: bool,
    url: str | None,
    allow_remote: bool,
    exercise_safe_interactions: bool,
    routes: tuple[str, ...] | list[str],
    depth: str,
    start_command: tuple[str, ...] | list[str] | None,
    server_url: str | None,
    input_fn: Input,
    output_fn: Output,
) -> dict[str, Any]:
    confirmation = False
    if start_command:
        phrase = "RUN PROJECT SERVER"
        import shlex
        _confirm(input_fn, output_fn, f"The orchestrator will execute `{shlex.join(start_command)}` without a shell in the selected project, wait for {server_url}, capture read-only same-origin evidence, and stop only the process group it starts. Type {phrase}", phrase)
        confirmation = True
    session = director.store.get_session(session_id)
    return director.audit(
        session_id,
        use_codex=use_codex,
        browser_url=url,
        allow_remote=allow_remote,
        exercise_safe_interactions=exercise_safe_interactions,
        route_paths=routes,
        depth=depth,
        collaboration=session.metadata.get("collaboration_mode", CollaborationMode.COMPREHENSIVE.value),
        allowed_secondary_providers=session.metadata.get("allowed_secondary_providers", []),
        start_command=start_command,
        server_url=server_url,
        server_human_confirmation=confirmation,
    )


def _collect_direction(director: FrontendDesignDirector, session_id: str, input_fn: Input, output_fn: Output) -> None:
    _review_current(director.store, session_id, Phase.AUDIT_COMPLETED, output_fn)
    visual = _ask_choice(input_fn, output_fn, "Visual appearance", ["preserve", "refine", "explore", "custom"])
    behavior = _ask_choice(input_fn, output_fn, "Behavior and interaction", ["preserve", "improve", "explore", "custom"])
    scope = _ask_choice(input_fn, output_fn, "Scope", ["components", "screens", "opportunities", "frontend"])
    constraints = director._stage_instructions(session_id, "design")
    if visual == "custom" or behavior == "custom":
        constraints = "\n\n".join(item for item in (constraints, _read_optional(input_fn, output_fn, "Describe the custom direction and any elements that must remain unchanged")) if item)
    phrase = "CONFIRM DIRECTION"
    _confirm(input_fn, output_fn, f"Visual: {visual}; behavior: {behavior}; scope: {scope}. These remain independent decisions. Type {phrase}", phrase)
    director.record_direction(session_id, visual=visual, behavior=behavior, scope=scope, constraints=constraints, human_confirmation=True)
    output_fn("Design direction recorded. It authorizes mockup exploration only; production implementation remains blocked.")


def _review_mockup(director: FrontendDesignDirector, session_id: str, action: str, input_fn: Input, output_fn: Output) -> None:
    normalized = "approve" if action in {"approve", "approve mockup"} else "revise" if action in {"revise", "revise mockup"} else "reject"
    note = ""
    if normalized in {"revise", "reject"}:
        note = _read_optional(input_fn, output_fn, "Describe the requested revision or rejection reason")
        if not note:
            output_fn("A non-empty note is required; no mockup decision was recorded.")
            return
    phrase = {"approve": "APPROVE MOCKUP", "revise": "CONFIRM REVISION", "reject": "CONFIRM REJECTION"}[normalized]
    _confirm(input_fn, output_fn, f"Mockup action: {normalized}; note: {note or '(none)'}. Type {phrase}", phrase)
    result = director.review_mockup(session_id, action=normalized, note=note, human_confirmation=True)
    output_fn(f"Mockup decision recorded: {result.get('status', normalized)}. This does not approve implementation.")


def _ask_choice(input_fn: Input, output_fn: Output, label: str, choices: list[str]) -> str:
    while True:
        value = input_fn(f"{label} [{'/'.join(choices)}]: ").strip().casefold()
        if value in choices:
            return value
        output_fn("Choose one of the listed values.")


def _confirm(input_fn: Input, output_fn: Output, message: str, expected: str) -> None:
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        raise ValueError("Approval in guided mode requires an interactive terminal; no approval was recorded.")
    output_fn(message)
    if input_fn("> ").strip() != expected:
        raise ValueError("Human confirmation did not match; no approval was recorded.")


def _read_optional(input_fn: Input, output_fn: Output, label: str) -> str:
    try:
        return input_fn(f"{label}: ").strip()
    except EOFError:
        return ""


def _read_instruction_block(input_fn: Input, output_fn: Output, stage: str) -> str:
    output_fn(f"Additional {stage} instructions. Enter one or more lines; finish with `END INSTRUCTIONS`. A blank first line cancels.")
    lines: list[str] = []
    while True:
        line = input_fn("> ").rstrip()
        if line.strip().casefold() == "end instructions":
            break
        if not lines and not line.strip():
            return ""
        lines.append(line)
        if sum(len(item) + 1 for item in lines) > 10_000:
            raise ValueError("Guided instruction blocks are limited to 10,000 characters.")
    return "\n".join(lines).strip()


def _instruction_saved_message(stage: str, phase: Phase) -> str:
    if phase in {Phase.AWAITING_IMPLEMENTATION_APPROVAL, Phase.IMPLEMENTING, Phase.PATCH_READY}:
        return f"Saved {stage} guidance. The current plan or patch is unchanged; revising it requires a new reviewed plan and applicable approval."
    return f"Saved {stage} guidance. It does not approve design, implementation, or patch application."


def _csv_paths(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _direction_constraints(store: WorkflowStore, session_id: str) -> str:
    try:
        artifact = store.artifact(session_id, "design-direction")
        value = json.loads(Path(artifact["path"]).read_text(encoding="utf-8"))
        return str(value.get("constraints", ""))
    except (KeyError, OSError, ValueError, json.JSONDecodeError):
        return ""


def _review_current(store: WorkflowStore, session_id: str, phase: Phase, output_fn: Output) -> None:
    names = {
        Phase.CAPABILITIES_REVIEW: ["capability-inventory"],
        Phase.AUDIT_COMPLETED: ["audit-index", "executive-summary", "audit-summary", "frontend-architecture-map", "route-and-screen-inventory", "component-inventory", "design-system-analysis", "color-system-analysis", "typography-analysis", "layout-and-density-analysis", "responsive-design-analysis", "visual-audit", "visual-analysis", "technical-audit", "interaction-behavior-audit", "accessibility-audit", "performance-audit", "runtime-evidence", "coverage-and-limitations"],
        Phase.AUDIT_COMPLETED_WITH_LIMITATIONS: ["audit-index", "executive-summary", "audit-summary", "frontend-architecture-map", "route-and-screen-inventory", "component-inventory", "design-system-analysis", "color-system-analysis", "typography-analysis", "layout-and-density-analysis", "responsive-design-analysis", "visual-audit", "visual-analysis", "technical-audit", "interaction-behavior-audit", "accessibility-audit", "performance-audit", "runtime-evidence", "coverage-and-limitations"],
        Phase.AUDIT_INCOMPLETE: ["audit-index", "executive-summary", "audit-summary", "visual-audit", "technical-audit", "interaction-behavior-audit", "coverage-and-limitations", "backend-diagnostics"],
        Phase.AWAITING_DIRECTION: ["audit-index", "executive-summary", "audit-summary", "visual-audit", "technical-audit", "interaction-behavior-audit", "coverage-and-limitations"],
        Phase.AWAITING_MOCKUP_REVIEW: ["mockup-r001-index_html", "implementation-spec"],
        Phase.AWAITING_IMPLEMENTATION_APPROVAL: ["implementation-plan-md", "implementation-plan"],
        Phase.PATCH_READY: ["implementation-result", "implementation-patch"],
        Phase.COMPLETED: ["final-report", "verification"],
    }.get(phase, ["audit-summary", "final-report"])
    output_fn("Available review artifacts:")
    for name in names:
        try:
            artifact = store.artifact(session_id, name)
            output_fn(f"- {name}: {artifact['path']}")
        except (KeyError, ValueError):
            continue


def _print_stage_result(output_fn: Output, store: WorkflowStore, session_id: str, title: str, artifact_name: str) -> None:
    output_fn(f"{title} completed.")
    try:
        artifact = store.artifact(session_id, artifact_name.replace("-", "_"))
        output_fn(f"Review: {artifact['path']}")
        if artifact_name == "audit-summary":
            summary = store.get_session(session_id).metadata.get("audit", {})
            coverage = summary.get("coverage", {})
            output_fn(f"Findings: {summary.get('findings_count', 0)} · routes: {coverage.get('routes_rendered', 0)}/{coverage.get('routes_discovered', 0)} rendered/discovered · screenshots: {coverage.get('screenshots_captured', 0)} · revision: {summary.get('revision', 1)}")
    except (KeyError, ValueError, OSError, json.JSONDecodeError):
        output_fn("Detailed artifact is not available yet.")


def _instruction_stage(phase: Phase) -> str:
    return {
        Phase.CAPABILITIES_REVIEW: "audit",
        Phase.AUDIT_COMPLETED: "design",
        Phase.AUDIT_COMPLETED_WITH_LIMITATIONS: "design",
        Phase.AUDIT_INCOMPLETE: "audit",
        Phase.AWAITING_DIRECTION: "design",
        Phase.DIRECTION_APPROVED: "mockup",
        Phase.MOCKUP_REVISION: "mockup",
        Phase.AWAITING_MOCKUP_REVIEW: "mockup",
        Phase.MOCKUP_APPROVED: "implementation",
    }.get(phase, "global")


def _pending_action(phase: Phase) -> str:
    return {
        Phase.CAPABILITIES_REVIEW: "review_discovery",
        Phase.AUDIT_COMPLETED: "review_audit_and_choose_direction",
        Phase.AUDIT_COMPLETED_WITH_LIMITATIONS: "review_limited_audit_and_choose_direction",
        Phase.AUDIT_INCOMPLETE: "retry_audit_or_review_partial_results",
        Phase.AWAITING_DIRECTION: "choose_design_direction",
        Phase.DIRECTION_APPROVED: "generate_mockup",
        Phase.MOCKUP_REVISION: "generate_mockup_revision",
        Phase.AWAITING_MOCKUP_REVIEW: "review_mockup",
        Phase.MOCKUP_APPROVED: "create_implementation_plan",
        Phase.AWAITING_IMPLEMENTATION_APPROVAL: "authorize_implementation_or_pause",
        Phase.IMPLEMENTING: "generate_patch",
        Phase.PATCH_READY: "review_and_apply_patch",
        Phase.VERIFYING: "run_or_skip_verification_commands",
        Phase.COMPLETED: "select_next_cycle_or_end",
    }.get(phase, phase.value.casefold())


def _save_state(store: WorkflowStore, session_id: str, **updates: Any) -> None:
    session = store.get_session(session_id)
    state = {**session.metadata.get("guided_session", {}), **updates}
    store.set_metadata(session_id, "guided_session", state)
