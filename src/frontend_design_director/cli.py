"""Command-line interface for human-supervised frontend design workflows."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import shlex
import sqlite3
import stat
import sys
import tempfile
import tomllib
import uuid
from datetime import datetime, timezone
from importlib import metadata
from importlib.resources import files
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from . import __version__
from .codex_backend import CodexCLIBackend, CodexSettings
from .director import FrontendDesignDirector, WorkflowBlocked
from .guided import run_guided_workflow
from .models import Phase
from .storage import LEGACY_WORKFLOW_STATE_DIRECTORY, WORKFLOW_STATE_DIRECTORY, WorkflowStore
from .update_check import check_for_update


CODEX_INSTALL_MANIFEST = Path(".frontend-design-director") / "codex-install"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="frontend-director",
        description="Discover and audit a frontend, review independent design decisions, create responsive mockups, then implement only a human-approved file scope.",
        epilog="The default audit is read-only and local. Codex model calls use saved ChatGPT sign-in and the account plan, not an API key. Production edits require separate implementation and patch approvals.",
    )
    parser.add_argument("--model", default="gpt-6-luna", help="Codex model used for optional specialist calls (default: gpt-6-luna).")
    parser.add_argument("--reasoning-effort", default="xhigh", choices=["low", "medium", "high", "xhigh", "max"], help="Codex reasoning effort (default: xhigh).")
    parser.add_argument("--verbosity", default="high", choices=["low", "medium", "high"], help="Codex response verbosity (default: high).")
    parser.add_argument("--summary", default="detailed", choices=["auto", "concise", "detailed", "none"], help="Codex reasoning summary setting (default: detailed).")
    parser.add_argument("--no-update-check", action="store_true", help="Skip the best-effort public version check for this invocation.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init", help="Create a durable workflow session for a target project.")
    init.add_argument("project_path", nargs="?", type=Path, help="Target project directory; defaults to the current directory.")
    init.add_argument("--project", type=Path, default=argparse.SUPPRESS, help="Target project directory.")
    init.add_argument("--title", default="", help="Optional human-readable session title.")
    _add_output(init)

    discover = subparsers.add_parser("discover", help="Inspect frontend files, skills, agents, Codex, MCP configuration, and cached plugins.")
    _add_context(discover)
    _add_output(discover)

    audit = subparsers.add_parser("audit", help="Generate separate technical, behavioral, and visual audit reports.")
    _add_context(audit)
    audit.add_argument("--codex", action="store_true", help="Ask the signed-in Codex CLI for structured specialist findings (uses plan usage and sends filtered source/screenshots to the service).")
    audit.add_argument("--depth", choices=["standard", "deep", "exhaustive"], default="deep", help="Audit profile: standard (desktop/mobile), deep (1440/768/390), or exhaustive (1920/1440/1280/768/390/320). Default: deep.")
    audit.add_argument("--url", help="Capture the running application at each source-discovered static route and selected responsive viewport. This attaches only; it does not start project scripts.")
    audit.add_argument("--start-command", help="Optionally start this argument vector (parsed with shlex; never through a shell) after an interactive RUN PROJECT SERVER approval.")
    audit.add_argument("--server-url", help="Local HTTP readiness URL required with --start-command, such as http://127.0.0.1:5173/.")
    audit.add_argument("--route", action="append", default=[], help="Limit browser capture to exact same-origin paths plus the base URL; repeat as needed. Without this option, all static source-discovered routes are attempted. Dynamic parameters are never invented.")
    audit.add_argument("--allow-remote", action="store_true", help="Permit screenshots of a non-local URL supplied with --url.")
    _add_output(audit)

    report = subparsers.add_parser("report", help="Display a previously generated report or JSON artifact.")
    _add_context(report)
    report.add_argument("name", choices=["audit-index", "audit-execution", "backend-diagnostics", "executive-summary", "application-overview", "technical-audit", "behavioral-audit", "interaction-behavior-audit", "accessibility-audit", "performance-audit", "visual-audit", "visual-analysis", "audit-summary", "findings", "coverage-and-limitations", "capability-inventory", "frontend-intelligence", "frontend-architecture-map", "route-and-screen-inventory", "component-inventory", "design-system-analysis", "color-system-analysis", "typography-analysis", "layout-and-density-analysis", "responsive-design-analysis", "runtime-evidence", "browser-evidence", "screenshot-gallery", "implementation-spec", "implementation-spec-md", "implementation-plan", "implementation-plan-md", "final-report", "verification"], help="Report artifact to display.")
    _add_output(report)

    direction = subparsers.add_parser("direction", help="Record separately selected visual, behavioral, and scope direction after audit review.")
    _add_context(direction)
    direction.add_argument("--visual", choices=["preserve", "refine", "explore", "custom"], help="Visual appearance direction.")
    direction.add_argument("--behavior", choices=["preserve", "improve", "explore", "custom"], help="Behavior and interaction direction.")
    direction.add_argument("--scope", choices=["components", "screens", "opportunities", "frontend"], help="Approved change scope.")
    direction.add_argument("--constraints", default="", help="Specific user-provided requirements or constraints.")
    _add_output(direction)

    mockup = subparsers.add_parser("mockup", help="Generate an isolated responsive HTML/CSS prototype after direction approval.")
    _add_context(mockup)
    mockup.add_argument("--brief-file", type=Path, help="Optional human-authored content and screen brief (20 KB maximum).")
    mockup.add_argument("--codex", action="store_true", help="Use the signed-in Codex CLI to refine the isolated prototype (uses plan usage).")
    mockup.add_argument("--revision-note", default="", help="Human direction for the next mockup revision.")
    _add_output(mockup)

    review = subparsers.add_parser("mockup-review", help="Approve, revise, or reject the current mockup; approval does not authorize implementation.")
    _add_context(review)
    review.add_argument("action", choices=["approve", "revise", "reject"])
    review.add_argument("--note", default="", help="Required note for revise and reject decisions.")
    _add_output(review)

    plan = subparsers.add_parser("plan", help="Create a reviewable exact-file implementation plan.")
    _add_context(plan)
    plan.add_argument("--file", action="append", default=[], help="Existing project-relative file to include. Repeat as needed.")
    plan.add_argument("--new-file", action="append", default=[], help="New project-relative file to include. Repeat as needed.")
    plan.add_argument("--codex", action="store_true", help="Ask Codex for a read-only plan. The result still requires explicit human approval.")
    _add_output(plan)

    approve = subparsers.add_parser("approve-implementation", help="Approve the exact plan and file scope before any code generation.")
    _add_context(approve)
    _add_output(approve)

    implement = subparsers.add_parser("implement", help="Run an authorized Codex implementation in an isolated snapshot and produce a patch.")
    _add_context(implement)
    _add_output(implement)

    apply = subparsers.add_parser("apply", help="Review and apply a human-approved, scope-checked patch to the target project.")
    _add_context(apply)
    _add_output(apply)

    verify = subparsers.add_parser("verify", help="Run only explicitly supplied verification commands and write a final report.")
    _add_context(verify)
    verify.add_argument("--command", dest="verification_command", action="append", default=[], help="Exact command to run, such as `npm test`; repeat for more than one. No shell operators are accepted.")
    _add_output(verify)

    status = subparsers.add_parser("status", help="Show the current phase, artifacts, and blocked requirements.")
    _add_context(status)
    _add_output(status)

    resume = subparsers.add_parser("resume", help="Resume a paused session or show the latest persisted session state.")
    _add_context(resume)
    _add_output(resume)

    pause = subparsers.add_parser("pause", help="Persistently pause the selected session.")
    _add_context(pause)
    _add_output(pause)

    guide = subparsers.add_parser("guide", help="Run a resumable, human-guided workflow that proposes the next safe step and preserves pending decisions.")
    _add_context(guide)
    guide.add_argument("--depth", choices=["standard", "deep", "exhaustive"], default="deep", help="Audit viewport profile (default: deep).")
    guide.add_argument("--codex", action="store_true", help="Explicitly allow Codex specialist calls using the signed-in account plan for audit/mockup/planning stages.")
    guide.add_argument("--url", help="Attach Playwright to this explicitly supplied running application URL; source-discovered static routes are captured and project scripts are not started.")
    guide.add_argument("--start-command", help="Optionally start the application with a shell-free argument vector after an interactive approval gate.")
    guide.add_argument("--server-url", help="Local readiness URL required with --start-command.")
    guide.add_argument("--route", action="append", default=[], help="Limit browser capture to exact same-origin paths plus the base URL; repeat as needed. Without this option, all static source-discovered routes are attempted.")
    guide.add_argument("--allow-remote", action="store_true", help="Allow the explicitly supplied remote URL and same-origin read-only requests.")

    install_agents = subparsers.add_parser("install-agents", help="Install bundled read-only specialist Codex agents into a target project's .codex/agents directory.")
    install_agents.add_argument("project_path", nargs="?", type=Path, help="Target project directory; defaults to the current directory.")
    install_agents.add_argument("--project", type=Path, default=argparse.SUPPRESS, help="Target project directory.")
    install_agents.add_argument("--upgrade", action="store_true", help="Update unchanged installer-managed files to the bundled versions; preserve local edits.")
    install_agents.add_argument("--force", action="store_true", help="Replace recognized agent files after backing up differences.")
    _add_output(install_agents)

    install_skill = subparsers.add_parser("install-skill", help="Install the bundled Codex workflow skill into a target project's .agents/skills directory.")
    install_skill.add_argument("project_path", nargs="?", type=Path, help="Target project directory; defaults to the current directory.")
    install_skill.add_argument("--project", type=Path, default=argparse.SUPPRESS, help="Target project directory.")
    install_skill.add_argument("--upgrade", action="store_true", help="Update an unchanged installer-managed skill; preserve local edits.")
    install_skill.add_argument("--force", action="store_true", help="Replace the recognized skill file after backing up differences.")
    _add_output(install_skill)

    install_codex = subparsers.add_parser(
        "install-codex",
        help="Install the bundled workflow skill and specialist agents into Codex project or user discovery paths.",
    )
    install_codex.add_argument("project_path", nargs="?", type=Path, help="Target project directory for project scope; defaults to the current directory.")
    install_codex.add_argument("--project", type=Path, default=argparse.SUPPRESS, help="Target project directory for project scope.")
    install_codex.add_argument("--scope", choices=["project", "user"], default="project", help="Install for one project or the current user's Codex environment (default: project).")
    install_codex.add_argument("--upgrade", action="store_true", help="Update unchanged installer-managed files to the bundled versions; preserve local edits.")
    install_codex.add_argument("--force", action="store_true", help="Replace recognized existing files after backing up differences.")
    _add_output(install_codex)

    update_codex = subparsers.add_parser(
        "update-codex",
        help="Synchronize the installed Codex skill and agents with bundled resources using content hashes.",
    )
    update_codex.add_argument("project_path", nargs="?", type=Path, help="Target project directory for project scope; defaults to the current directory.")
    update_codex.add_argument("--project", type=Path, default=argparse.SUPPRESS, help="Target project directory for project scope.")
    update_codex.add_argument("--scope", choices=["project", "user"], default="user", help="Synchronize one project or the current user's Codex environment (default: user).")
    update_codex.add_argument("--force", action="store_true", help="Back up and replace modified or untracked files at exact Frontend Design Director resource paths.")
    _add_output(update_codex)

    doctor = subparsers.add_parser(
        "doctor",
        help="Inspect Python package and Codex integration synchronization without modifying files.",
    )
    doctor.add_argument("project_path", nargs="?", type=Path, help="Target project directory for project scope; defaults to the current directory.")
    doctor.add_argument("--project", type=Path, default=argparse.SUPPRESS, help="Target project directory for project scope.")
    doctor.add_argument("--scope", choices=["project", "user"], default="user", help="Inspect one project's or the user's Codex installation (default: user).")
    doctor.add_argument("--expected-source", type=Path, help="Optional source checkout the active Python package is expected to use.")
    _add_output(doctor)

    uninstall_codex = subparsers.add_parser(
        "uninstall-codex",
        help="Remove unchanged Codex files recorded by this install; preserve modified or unmanaged files.",
    )
    uninstall_codex.add_argument("project_path", nargs="?", type=Path, help="Target project directory for project scope; defaults to the current directory.")
    uninstall_codex.add_argument("--project", type=Path, default=argparse.SUPPRESS, help="Target project directory for project scope.")
    uninstall_codex.add_argument("--scope", choices=["project", "user"], default="project", help="Uninstall from one project or the current user's Codex environment (default: project).")
    uninstall_codex.add_argument("--yes", action="store_true", help="Skip the interactive confirmation after reviewing the scope.")
    _add_output(uninstall_codex)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    project = getattr(args, "project", None) or getattr(args, "project_path", None) or Path.cwd()
    try:
        project = project.expanduser().resolve(strict=True)
        if not args.no_update_check and args.command != "doctor":
            _warn_if_update_available()
        if args.command == "init":
            store = _store_for(project)
            director = _director(store, args)
            session = director.create_session(project, args.title)
            _output({"session_id": session.id, "phase": session.phase.value, "project_root": session.project_root, "state_dir": session.state_dir}, args.json_output)
            return 0
        if args.command == "install-agents":
            _output(
                _install_codex(
                    project,
                    "project",
                    include_skill=False,
                    upgrade=args.upgrade,
                    force=args.force,
                )["agents"],
                args.json_output,
            )
            return 0
        if args.command == "install-skill":
            _output(
                _install_codex(
                    project,
                    "project",
                    include_agents=False,
                    upgrade=args.upgrade,
                    force=args.force,
                )["skill"],
                args.json_output,
            )
            return 0
        if args.command == "install-codex":
            if args.scope == "user" and (args.project_path is not None or hasattr(args, "project")):
                raise ValueError("Do not supply a project path with `install-codex --scope user`.")
            _output(_install_codex(project, args.scope, upgrade=args.upgrade, force=args.force), args.json_output)
            return 0
        if args.command == "update-codex":
            if args.scope == "user" and (args.project_path is not None or hasattr(args, "project")):
                raise ValueError("Do not supply a project path with `update-codex --scope user`.")
            _output(_install_codex(project, args.scope, upgrade=True, force=args.force), args.json_output)
            return 0
        if args.command == "doctor":
            if args.scope == "user" and (args.project_path is not None or hasattr(args, "project")):
                raise ValueError("Do not supply a project path with `doctor --scope user`.")
            _output(_installation_doctor(project, args.scope, expected_source=args.expected_source), args.json_output)
            return 0
        if args.command == "uninstall-codex":
            if args.scope == "user" and (args.project_path is not None or hasattr(args, "project")):
                raise ValueError("Do not supply a project path with `uninstall-codex --scope user`.")
            if not args.yes:
                _human_gate(
                    "This removes only unchanged files recorded in the frontend-director Codex install manifest. "
                    "Pre-existing and modified files are preserved. Type UNINSTALL CODEX to continue.",
                    "UNINSTALL CODEX",
                )
            _output(_uninstall_codex(project, args.scope), args.json_output)
            return 0
        store = _store_for(project)
        if args.command == "guide":
            if args.allow_remote and not args.url:
                raise ValueError("--allow-remote requires an explicit --url.")
            if args.start_command and (args.url or not args.server_url):
                raise ValueError("Use --start-command with --server-url, without --url.")
            if args.server_url and not args.start_command:
                raise ValueError("--server-url requires --start-command.")
            if args.route and not (args.url or args.start_command):
                raise ValueError("--route requires an explicit --url or --start-command with --server-url.")
            director = _director(store, args)
            session = store.get_session(args.session) if args.session else _latest_open_guided_session(store, director, project)
            if session.project_root != str(project):
                raise ValueError("The selected session belongs to a different project. Specify its project root.")
            run_guided_workflow(
                director, store, session.id,
                use_codex=args.codex,
                browser_url=args.url,
                allow_remote=args.allow_remote,
                route_paths=args.route,
                depth=args.depth,
                start_command=_parse_start_command(args.start_command) if args.start_command else None,
                server_url=args.server_url,
            )
            return 0
        session = _select_session(store, args.session)
        if session.project_root != str(project):
            raise ValueError("The selected session belongs to a different project. Specify its project root.")
        director = _director(store, args)

        if args.command == "discover":
            result = director.discover(session.id)
            _output(result, args.json_output)
        elif args.command == "audit":
            if args.allow_remote and not args.url:
                raise ValueError("--allow-remote requires an explicit --url.")
            if args.start_command and (args.url or not args.server_url):
                raise ValueError("Use --start-command with --server-url, without --url.")
            if args.server_url and not args.start_command:
                raise ValueError("--server-url requires --start-command.")
            if args.route and not (args.url or args.start_command):
                raise ValueError("--route requires an explicit --url or --start-command with --server-url.")
            command = _parse_start_command(args.start_command) if args.start_command else None
            if command:
                phrase = "RUN PROJECT SERVER"
                _human_gate(f"The orchestrator will run this command with no shell in `{project}` and stop only the process group it starts. Readiness URL: {args.server_url}\nCommand: {shlex.join(command)}\nType {phrase}", phrase)
            result = director.audit(session.id, use_codex=args.codex, browser_url=args.url, allow_remote=args.allow_remote, route_paths=args.route, depth=args.depth, start_command=command, server_url=args.server_url, server_human_confirmation=bool(command))
            _output(result, args.json_output)
            if result.get("completion_status") in {"incomplete", "failed"}:
                return 3
        elif args.command == "report":
            _show_report(store, session.id, args.name, args.json_output)
        elif args.command == "direction":
            summary_artifact = store.artifact(session.id, "audit_summary")
            print(Path(summary_artifact["path"]).read_text(encoding="utf-8"))
            visual = args.visual or _choose("Visual appearance", ["preserve", "refine", "explore", "custom"])
            behavior = args.behavior or _choose("Behavior and interaction", ["preserve", "improve", "explore", "custom"])
            scope = args.scope or _choose("Implementation scope", ["components", "screens", "opportunities", "frontend"])
            constraints = args.constraints
            if (visual == "custom" or behavior == "custom") and not constraints.strip():
                constraints = _prompt("Describe the required visual and behavioral constraints")
            _human_gate(f"Visual: {visual}; behavior: {behavior}; scope: {scope}\nType CONFIRM DIRECTION to persist these choices", "CONFIRM DIRECTION")
            result = director.record_direction(session.id, visual=visual, behavior=behavior, scope=scope, constraints=constraints, human_confirmation=True)
            _output(result, args.json_output)
        elif args.command == "mockup":
            brief = ""
            if args.brief_file:
                if args.brief_file.stat().st_size > 20_000:
                    raise ValueError("Mockup brief files are limited to 20 KB.")
                brief = args.brief_file.read_text(encoding="utf-8")
            revision_note = args.revision_note or _session_revision_note(store, session.id)
            result = director.generate_mockup(session.id, brief=brief, revision_note=revision_note, use_codex=args.codex)
            _output(result, args.json_output)
        elif args.command == "mockup-review":
            if args.action in {"revise", "reject"} and not args.note.strip():
                args.note = _prompt("Describe the revision or reason for rejection")
            phrase = "APPROVE MOCKUP" if args.action == "approve" else "CONFIRM REVISION" if args.action == "revise" else "CONFIRM REJECTION"
            _human_gate(f"Mockup action: {args.action}; note: {args.note or '(none)'}\nType {phrase} to confirm", phrase)
            result = director.review_mockup(session.id, action=args.action, note=args.note, human_confirmation=True)
            _output(result, args.json_output)
        elif args.command == "plan":
            result = director.plan_implementation(session.id, files=args.file or None, new_files=args.new_file or None, use_codex=args.codex)
            _output(result, args.json_output)
        elif args.command == "approve-implementation":
            plan_artifact = store.artifact(session.id, "implementation-plan")
            plan_value = json.loads(Path(plan_artifact["path"]).read_text(encoding="utf-8"))
            scope = plan_value["approved_scope"]
            plan_sha = plan_artifact["sha256"]
            plan_report = store.artifact(session.id, "implementation-plan-md")
            print(Path(plan_report["path"]).read_text(encoding="utf-8"))
            phrase = f"AUTHORIZE IMPLEMENTATION {session.id[:8]}"
            _human_gate(f"Approved file scope:\n" + "\n".join(f"- {item}" for item in scope) + f"\nPlan SHA-256: {plan_sha}\nType {phrase} to authorize Codex changes in an isolated snapshot", phrase)
            result = director.approve_implementation(session.id, human_confirmation=True)
            _output(result, args.json_output)
        elif args.command == "implement":
            result = director.implement(session.id)
            _output(result, args.json_output)
        elif args.command == "apply":
            patch = store.artifact(session.id, "implementation-patch")
            manifest = json.loads(Path(store.artifact(session.id, "implementation-result")["path"]).read_text(encoding="utf-8"))
            print(f"Implementation summary: {manifest.get('summary', 'Not provided.')}")
            print("Changed files:")
            for changed_path in manifest.get("changed_files", []):
                print(f"- {changed_path}")
            if Path(patch["path"]).stat().st_size <= 40_000:
                print("\nGenerated patch:")
                print(Path(patch["path"]).read_text(encoding="utf-8", errors="replace"))
            else:
                print(f"\nPatch is larger than 40 KB; inspect the full artifact at {patch['path']} before continuing.")
            phrase = f"APPLY PATCH {session.id[:8]}"
            _human_gate(f"Patch: {patch['path']}\nSHA-256: {patch['sha256']}\nThe patch will be checked against approved paths and current file hashes. Type {phrase} to apply", phrase)
            result = director.approve_patch_application(session.id, human_confirmation=True)
            applied = director.apply_patch(session.id)
            _output({"approval": result, "application": applied}, args.json_output)
        elif args.command == "verify":
            commands = getattr(args, "verification_command", [])
            if commands:
                _human_gate("The following explicit commands may execute project code:\n" + "\n".join(f"- {item}" for item in commands) + "\nType RUN VERIFICATION to continue", "RUN VERIFICATION")
            result = director.verify(session.id, commands)
            _output(result, args.json_output)
        elif args.command == "status":
            _output(director.status(session.id), args.json_output)
        elif args.command == "resume":
            resumed = director.resume(session.id)
            _output(director.status(resumed.id), args.json_output)
        elif args.command == "pause":
            paused = director.pause(session.id)
            _output({"session_id": paused.id, "phase": paused.phase.value}, args.json_output)
        else:
            parser.error(f"Unsupported command: {args.command}")
        return 0
    except (ValueError, KeyError, WorkflowBlocked, OSError, RuntimeError) as error:
        print(f"error: {type(error).__name__}: {error}", file=sys.stderr)
        return 2


def _add_context(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--project", type=Path, default=argparse.SUPPRESS, help="Target project directory; defaults to the current directory.")
    parser.add_argument("--session", help="Workflow session ID; defaults to the latest session for this project.")


def _warn_if_update_available() -> None:
    result = check_for_update()
    if result["status"] != "update_available":
        return
    print(
        f"A newer frontend-director is available ({result['current_version']} → {result['latest_version']}). "
        "Update using your existing installation source.",
        file=sys.stderr,
    )


def _add_output(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--json", dest="json_output", action="store_true", help="Print result as structured JSON.")


def _store_for(project: Path) -> WorkflowStore:
    root = project.resolve(strict=True)
    state_dir = _safe_project_directory(root, WORKFLOW_STATE_DIRECTORY)
    database_path = state_dir / "workflow.sqlite3"
    if database_path.is_symlink():
        raise ValueError("The workflow state directory must be a normal directory inside the selected project.")
    if not database_path.exists():
        legacy_directory = _safe_project_directory(root, LEGACY_WORKFLOW_STATE_DIRECTORY)
        legacy_database = legacy_directory / "workflow.sqlite3"
        if legacy_database.is_symlink():
            raise ValueError("The legacy workflow database cannot be a symbolic link.")
        if legacy_database.exists():
            if not legacy_database.is_file():
                raise ValueError("The legacy workflow database must be a regular file.")
            state_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
            state_dir = _safe_project_directory(root, WORKFLOW_STATE_DIRECTORY)
            database_path = state_dir / "workflow.sqlite3"
            _copy_legacy_workflow_database(legacy_database, database_path)
    if database_path.exists() and not database_path.is_file():
        raise ValueError("The workflow database must be a regular file.")
    return WorkflowStore(database_path)


def _copy_legacy_workflow_database(source: Path, destination: Path) -> None:
    """Copy a legacy SQLite state database without deleting its original."""
    if destination.is_symlink():
        raise ValueError("The new workflow database cannot be a symbolic link.")
    if destination.exists():
        return
    descriptor, temporary_name = tempfile.mkstemp(prefix=".workflow-", suffix=".sqlite3", dir=destination.parent)
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        source_connection = sqlite3.connect(source)
        try:
            destination_connection = sqlite3.connect(temporary)
            try:
                source_connection.backup(destination_connection)
            finally:
                destination_connection.close()
        finally:
            source_connection.close()
        temporary.chmod(0o600)
        try:
            os.link(temporary, destination)
        except FileExistsError:
            # Another initializer completed the same migration concurrently.
            pass
    finally:
        temporary.unlink(missing_ok=True)


def _select_session(store: WorkflowStore, session_id: str | None):
    return store.get_session(session_id) if session_id else store.latest_session()


def _parse_start_command(value: str) -> list[str]:
    if len(value) > 4_096:
        raise ValueError("--start-command is limited to 4,096 characters.")
    try:
        command = shlex.split(value)
    except ValueError as error:
        raise ValueError(f"Could not parse --start-command: {error}") from error
    if not command or len(command) > 128 or any(len(item) > 1_024 for item in command):
        raise ValueError("--start-command must contain a bounded executable and argument vector.")
    return command


def _latest_open_guided_session(store: WorkflowStore, director: FrontendDesignDirector, project: Path):
    try:
        session = store.latest_session()
    except KeyError:
        return director.create_session(project)
    if session.project_root != str(project) or session.phase.value == "CANCELLED" or session.metadata.get("guided_session", {}).get("status") == "ended":
        return director.create_session(project)
    return session


def _director(store: WorkflowStore, args: argparse.Namespace) -> FrontendDesignDirector:
    settings = CodexSettings(model=args.model, reasoning_effort=args.reasoning_effort, verbosity=args.verbosity, summary=args.summary)
    return FrontendDesignDirector(store, CodexCLIBackend(settings=settings))


def _output(value: Any, as_json: bool) -> None:
    if as_json:
        print(json.dumps(value, indent=2, ensure_ascii=False, default=_json_default))
        return
    if isinstance(value, dict):
        _print_readable(value)
    else:
        print(value)


def _print_readable(value: dict[str, Any]) -> None:
    for key, item in value.items():
        label = key.replace("_", " ").capitalize()
        if isinstance(item, dict):
            print(f"{label}:")
            for child_key, child_value in item.items():
                print(f"  {child_key.replace('_', ' ')}: {child_value}")
        elif isinstance(item, list):
            print(f"{label}:")
            for child in item:
                print(f"  - {json.dumps(child, ensure_ascii=False, default=_json_default) if isinstance(child, (dict, list)) else child}")
        else:
            print(f"{label}: {item}")


def _json_default(value: Any) -> Any:
    return value.value if hasattr(value, "value") else str(value)


def _choose(title: str, options: list[str]) -> str:
    if not sys.stdin.isatty():
        raise ValueError("This decision requires an interactive terminal. Pass all choices and confirm in a TTY.")
    print(title + ":")
    for index, option in enumerate(options, start=1):
        print(f"  {index}. {option}")
    while True:
        selected = input("Choose a number: ").strip()
        if selected.isdigit() and 1 <= int(selected) <= len(options):
            return options[int(selected) - 1]
        print(f"Enter a number from 1 to {len(options)}.")


def _prompt(label: str) -> str:
    if not sys.stdin.isatty():
        raise ValueError("This information requires an interactive terminal.")
    return input(f"{label}: ").strip()


def _human_gate(message: str, expected: str) -> None:
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        raise ValueError("Human approval requires a terminal interaction; non-interactive or agent-generated text is not accepted.")
    print(message)
    answer = input("> ").strip()
    if answer != expected:
        raise ValueError("Human confirmation phrase did not match; no approval was recorded.")


def _show_report(store: WorkflowStore, session_id: str, name: str, as_json: bool) -> None:
    artifact_name = name.replace("-", "_")
    if name == "technical-audit":
        artifact_name = "technical_audit"
    elif name == "behavioral-audit":
        artifact_name = "behavioral_audit"
    elif name == "visual-audit":
        artifact_name = "visual_audit"
    elif name == "audit-summary":
        artifact_name = "audit_summary"
    elif name == "capability-inventory":
        artifact_name = "capability_inventory"
    elif name == "implementation-spec-md":
        artifact_name = "implementation_spec_md"
    elif name == "implementation-plan-md":
        artifact_name = "implementation_plan_md"
    elif name == "final-report":
        artifact_name = "final_report"
    elif name == "verification":
        artifact_name = "verification"
    artifact = store.artifact(session_id, artifact_name)
    path = Path(artifact["path"])
    if as_json:
        print(json.dumps({"artifact": artifact, "content": path.read_text(encoding="utf-8")}, indent=2))
    else:
        print(path.read_text(encoding="utf-8"))


def _session_revision_note(store: WorkflowStore, session_id: str) -> str:
    session = store.get_session(session_id)
    return str(session.metadata.get("mockup_revision_note", ""))


def _install_agents(project: Path, relative_directory: Path | None = None) -> dict[str, Any]:
    root = project.resolve(strict=True)
    target = _safe_project_directory(root, relative_directory or (Path(".codex") / "agents"))
    target.mkdir(parents=True, exist_ok=True)
    resource_dir = files("frontend_design_director").joinpath("data", "agents")
    installed: list[str] = []
    skipped: list[str] = []
    for resource in resource_dir.iterdir():
        if not resource.name.endswith(".toml"):
            continue
        path = target / resource.name
        if path.is_symlink():
            raise ValueError(f"Agent install file is a symbolic link: {path}")
        if path.exists():
            skipped.append(str(path))
            continue
        path.write_text(resource.read_text(encoding="utf-8"), encoding="utf-8")
        installed.append(str(path))
    return {"installed": installed, "already_present_not_overwritten": skipped, "path": str(target)}


def _install_skill(project: Path) -> dict[str, Any]:
    root = project.resolve(strict=True)
    target_directory = _safe_project_directory(root, Path(".agents") / "skills" / "frontend-design-director")
    target = target_directory / "SKILL.md"
    if target.is_symlink():
        raise ValueError(f"Skill install file is a symbolic link: {target}")
    if target.exists():
        return {"installed": False, "already_present_not_overwritten": str(target)}
    target.parent.mkdir(parents=True, exist_ok=True)
    resource = files("frontend_design_director").joinpath("data", "skill", "SKILL.md")
    target.write_text(resource.read_text(encoding="utf-8"), encoding="utf-8")
    return {"installed": True, "path": str(target)}


def _codex_install_locations(project: Path, scope: str, *, create: bool) -> tuple[Path, Path, Path, Path]:
    if scope == "project":
        root = project.resolve(strict=True)
        agents_root = root
        agents_relative = Path(".codex") / "agents"
    elif scope == "user":
        root = Path.home().resolve(strict=True)
        codex_home_setting = os.environ.get("CODEX_HOME")
        if codex_home_setting:
            codex_home = Path(codex_home_setting).expanduser()
            if create:
                codex_home.mkdir(parents=True, exist_ok=True, mode=0o700)
            agents_root = codex_home.resolve(strict=create)
            if create and not agents_root.is_dir():
                raise ValueError("CODEX_HOME must point to a directory for user-scope installation.")
            agents_relative = Path("agents")
        else:
            agents_root = root
            agents_relative = Path(".codex") / "agents"
    else:
        raise ValueError("Codex install scope must be `project` or `user`.")
    agents_directory = (agents_root / agents_relative).resolve(strict=False)
    return root, agents_root, agents_relative, agents_directory


def _codex_manifest_path(root: Path, agents_directory: Path, *, create_parent: bool = False) -> Path:
    state_directory = _safe_project_directory(root, CODEX_INSTALL_MANIFEST.parent)
    if create_parent:
        state_directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    digest = hashlib.sha256(str(agents_directory).encode("utf-8")).hexdigest()[:16]
    path = state_directory / f"{CODEX_INSTALL_MANIFEST.name}-{digest}.json"
    if path.is_symlink():
        raise ValueError(f"Codex installation manifest is a symbolic link: {path}")
    return path


def _valid_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(character in "0123456789abcdef" for character in value)


def _codex_resource_destination(resource_id: str, root: Path, agents_directory: Path) -> Path:
    if resource_id == "skill":
        directory = _safe_project_directory(root, Path(".agents") / "skills" / "frontend-design-director")
        return directory / "SKILL.md"
    if resource_id.startswith("agent:"):
        name = resource_id.removeprefix("agent:")
        if Path(name).name != name or not name.startswith("frontend-") or not name.endswith(".toml"):
            raise ValueError("Codex install manifest contains an invalid agent identifier.")
        return agents_directory / name
    raise ValueError("Codex install manifest contains an unknown resource identifier.")


def _read_codex_manifest(path: Path, *, scope: str, root: Path, agents_directory: Path) -> dict[str, Any] | None:
    if path.is_symlink():
        raise ValueError(f"Codex installation manifest is a symbolic link: {path}")
    if not path.exists():
        return None
    if not path.is_file():
        raise ValueError(f"Codex installation manifest is not a regular file: {path}")
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Codex installation manifest cannot be read: {path}") from error
    if not isinstance(manifest, dict) or isinstance(manifest.get("schema_version"), bool) or manifest.get("schema_version") not in {1, 2}:
        raise ValueError("Unsupported or malformed Codex installation manifest.")
    if manifest.get("scope") != scope or manifest.get("root") != str(root) or manifest.get("agents_directory") != str(agents_directory):
        raise ValueError("Codex installation scope or CODEX_HOME differs from the saved manifest.")
    if manifest["schema_version"] == 1:
        skill_hash = manifest.get("skill_sha256")
        agent_hashes = manifest.get("agent_sha256")
        if skill_hash is not None and not _valid_sha256(skill_hash):
            raise ValueError("Codex installation manifest contains an invalid skill hash.")
        if not isinstance(agent_hashes, dict):
            raise ValueError("Codex installation manifest has an invalid agent hash map.")
        resources: dict[str, dict[str, Any]] = {}
        if skill_hash is not None:
            resources["skill"] = {
                "type": "skill",
                "name": "frontend-design-director",
                "source": "data/skill/SKILL.md",
                "destination": str(_codex_resource_destination("skill", root, agents_directory)),
                "sha256": skill_hash,
                "managed": True,
            }
        for name, digest in agent_hashes.items():
            if not isinstance(name, str) or name in {".", ".."} or Path(name).name != name or not name.startswith("frontend-") or not name.endswith(".toml") or not _valid_sha256(digest):
                raise ValueError("Codex installation manifest contains an invalid agent entry.")
            resource_id = f"agent:{name}"
            resources[resource_id] = {
                "type": "agent",
                "name": name,
                "source": f"data/agents/{name}",
                "destination": str(_codex_resource_destination(resource_id, root, agents_directory)),
                "sha256": digest,
                "managed": True,
            }
        manifest = {**manifest, "schema_version": 2, "resources": resources, "_migrated_from_schema": 1}
    else:
        resources = manifest.get("resources")
        if not isinstance(resources, dict):
            raise ValueError("Codex installation manifest has an invalid resource map.")
        for resource_id, record in resources.items():
            if not isinstance(resource_id, str) or not isinstance(record, dict):
                raise ValueError("Codex installation manifest contains an invalid resource entry.")
            expected_destination = _codex_resource_destination(resource_id, root, agents_directory)
            if record.get("destination") != str(expected_destination):
                raise ValueError("Codex installation manifest contains a resource outside its expected install path.")
            if record.get("type") != ("skill" if resource_id == "skill" else "agent"):
                raise ValueError("Codex installation manifest contains an invalid resource type.")
            if not isinstance(record.get("name"), str) or not isinstance(record.get("source"), str):
                raise ValueError("Codex installation manifest contains incomplete resource metadata.")
            digest = record.get("sha256")
            managed = record.get("managed")
            if (digest is not None and not _valid_sha256(digest)) or not isinstance(managed, bool) or (managed and digest is None):
                raise ValueError("Codex installation manifest contains invalid ownership or hash metadata.")
    return manifest


def _write_codex_manifest(path: Path, manifest: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if path.is_symlink():
        raise ValueError(f"Codex installation manifest is a symbolic link: {path}")
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        temporary.chmod(0o600)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _bundled_codex_resources(
    *, include_skill: bool = True, include_agents: bool = True
) -> list[dict[str, Any]]:
    resources: list[dict[str, Any]] = []
    package = files("frontend_design_director")
    if include_skill:
        skill = package.joinpath("data", "skill", "SKILL.md")
        resources.append({
            "id": "skill",
            "type": "skill",
            "name": "frontend-design-director",
            "source": "data/skill/SKILL.md",
            "content": skill.read_bytes(),
        })
    if include_agents:
        agent_directory = package.joinpath("data", "agents")
        agent_resources = sorted(
            (resource for resource in agent_directory.iterdir() if resource.name.startswith("frontend-") and resource.name.endswith(".toml")),
            key=lambda resource: resource.name,
        )
        for resource in agent_resources:
            resources.append({
                "id": f"agent:{resource.name}",
                "type": "agent",
                "name": resource.name,
                "source": f"data/agents/{resource.name}",
                "content": resource.read_bytes(),
            })
    return resources


def _inspect_codex_resource(path: Path, previous: dict[str, Any] | None, bundled_sha256: str) -> dict[str, Any]:
    try:
        file_stat = path.lstat()
    except FileNotFoundError:
        return {"status": "missing", "installed_sha256": None, "content": None, "mode": None}
    except OSError as error:
        return {"status": "invalid", "installed_sha256": None, "content": None, "mode": None, "error": str(error)}
    if stat.S_ISLNK(file_stat.st_mode) or not stat.S_ISREG(file_stat.st_mode):
        reason = "symbolic_link" if stat.S_ISLNK(file_stat.st_mode) else "not_a_regular_file"
        return {"status": "invalid", "installed_sha256": None, "content": None, "mode": None, "error": reason}
    try:
        content = path.read_bytes()
    except OSError as error:
        return {"status": "invalid", "installed_sha256": None, "content": None, "mode": None, "error": str(error)}
    digest = hashlib.sha256(content).hexdigest()
    if digest == bundled_sha256:
        status = "current" if previous and previous.get("managed") else "current_unmanaged"
    elif not previous or not previous.get("managed"):
        status = "untracked_legacy"
    elif digest == previous.get("sha256"):
        status = "outdated_unmodified"
    else:
        status = "modified_locally"
    return {
        "status": status,
        "installed_sha256": digest,
        "content": content,
        "mode": stat.S_IMODE(file_stat.st_mode),
    }


def _inspect_obsolete_codex_resources(
    resources: dict[str, dict[str, Any]], bundled_ids: set[str]
) -> list[dict[str, Any]]:
    obsolete: list[dict[str, Any]] = []
    for resource_id, record in resources.items():
        if resource_id in bundled_ids:
            continue
        path = Path(record["destination"])
        if not record["managed"]:
            inspection = _inspect_codex_resource(path, None, "")
            status = "unmanaged_obsolete" if inspection["status"] != "missing" else "obsolete_missing"
        else:
            inspection = _inspect_codex_resource(path, record, "")
            status = {
                "outdated_unmodified": "obsolete_managed",
                "modified_locally": "modified_obsolete",
                "missing": "obsolete_missing",
                "invalid": "invalid",
            }.get(inspection["status"], "invalid")
        obsolete.append({
            "id": resource_id,
            "type": record["type"],
            "name": record["name"],
            "destination": str(path),
            "installed_sha256": inspection.get("installed_sha256"),
            "managed": bool(record["managed"]),
            "status": status,
            "error": inspection.get("error"),
        })
    return obsolete


def _create_codex_backup(path: Path, expected_sha256: str) -> Path:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"Cannot back up a non-regular Codex integration file: {path}")
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    backup = path.with_name(f"{path.name}.bak.{timestamp}.{uuid.uuid4().hex[:8]}")
    try:
        with path.open("rb") as source, backup.open("xb") as destination:
            shutil.copyfileobj(source, destination)
        shutil.copystat(path, backup, follow_symlinks=False)
        if _file_sha256(backup) != expected_sha256:
            raise OSError(f"Codex integration file changed while its backup was being created: {path}")
    except Exception:
        backup.unlink(missing_ok=True)
        raise
    return backup


def _stage_codex_resource(path: Path, content: bytes, mode: int | None) -> Path:
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        if mode is not None:
            temporary.chmod(mode)
        return temporary
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def _atomic_restore(path: Path, content: bytes, mode: int | None) -> None:
    if path.is_symlink():
        raise ValueError(f"Refusing to restore through a symbolic link: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = _stage_codex_resource(path, content, mode)
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _install_codex(
    project: Path,
    scope: str,
    *,
    include_skill: bool = True,
    include_agents: bool = True,
    upgrade: bool = False,
    force: bool = False,
) -> dict[str, Any]:
    """Install or content-synchronize only this package's expected Codex paths."""
    if not include_skill and not include_agents:
        raise ValueError("At least one Codex integration component must be selected.")
    if force:
        upgrade = True
    root, agents_root, agents_relative, agents_directory = _codex_install_locations(project, scope, create=False)
    manifest_path = _codex_manifest_path(root, agents_directory)
    previous_manifest = _read_codex_manifest(manifest_path, scope=scope, root=root, agents_directory=agents_directory)
    previous_resources = previous_manifest.get("resources", {}) if previous_manifest else {}
    bundled = _bundled_codex_resources(include_skill=include_skill, include_agents=include_agents)
    skill_directory = _safe_project_directory(root, Path(".agents") / "skills" / "frontend-design-director")
    safe_agents_root = agents_root.resolve(strict=False)
    safe_agents_directory = _safe_project_directory(safe_agents_root, agents_relative)
    selected: list[dict[str, Any]] = []
    planned_writes: list[dict[str, Any]] = []
    resources_for_manifest = dict(previous_resources)

    for resource in bundled:
        resource_id = str(resource["id"])
        destination = skill_directory / "SKILL.md" if resource_id == "skill" else safe_agents_directory / str(resource["name"])
        inspection = _inspect_codex_resource(destination, previous_resources.get(resource_id), hashlib.sha256(resource["content"]).hexdigest())
        original_status = inspection["status"]
        should_write = original_status == "missing" or (upgrade and original_status == "outdated_unmodified") or (force and original_status in {"modified_locally", "untracked_legacy"})
        action_status = original_status
        if should_write:
            action_status = "installed" if original_status == "missing" else ("backed_up_and_updated" if force and original_status in {"modified_locally", "untracked_legacy"} else "updated")
            planned_writes.append({
                "resource": resource,
                "destination": destination,
                "previous": inspection,
                "bundled_sha256": hashlib.sha256(resource["content"]).hexdigest(),
                "status": action_status,
            })
        elif original_status == "current_unmanaged":
            action_status = "current_unmanaged"
        elif original_status == "outdated_unmodified":
            action_status = "outdated"
        selected.append({
            "id": resource_id,
            "type": resource["type"],
            "name": resource["name"],
            "source": resource["source"],
            "destination": str(destination),
            "status": action_status,
            "installed_sha256": inspection.get("installed_sha256"),
            "bundled_sha256": hashlib.sha256(resource["content"]).hexdigest(),
            "managed": bool(previous_resources.get(resource_id, {}).get("managed")),
            "backup": None,
        })

        old_record = previous_resources.get(resource_id)
        if should_write:
            resources_for_manifest[resource_id] = {
                "type": resource["type"],
                "name": resource["name"],
                "source": resource["source"],
                "destination": str(destination),
                "sha256": hashlib.sha256(resource["content"]).hexdigest(),
                "managed": True,
            }
            selected[-1]["managed"] = True
        elif inspection.get("status") in {"current", "current_unmanaged"}:
            resources_for_manifest[resource_id] = {
                "type": resource["type"],
                "name": resource["name"],
                "source": resource["source"],
                "destination": str(destination),
                "sha256": inspection["installed_sha256"] if old_record and old_record.get("managed") else None,
                "managed": bool(old_record and old_record.get("managed")),
            }
        elif old_record:
            resources_for_manifest[resource_id] = old_record
        else:
            resources_for_manifest[resource_id] = {
                "type": resource["type"],
                "name": resource["name"],
                "source": resource["source"],
                "destination": str(destination),
                "sha256": None,
                "managed": False,
            }

    obsolete_resources = _inspect_obsolete_codex_resources(resources_for_manifest, {str(item["id"]) for item in bundled})

    manifest = {
        "schema_version": 2,
        "package_name": "frontend-design-director",
        "package_version": __version__,
        "scope": scope,
        "root": str(root),
        "agents_directory": str(agents_directory),
        "installed_at": (previous_manifest or {}).get("installed_at") or datetime.now(timezone.utc).isoformat(),
        "resources": resources_for_manifest,
    }
    if previous_manifest and previous_manifest.get("_migrated_from_schema"):
        manifest["migrated_from_schema"] = previous_manifest["_migrated_from_schema"]

    original_manifest_bytes: bytes | None = None
    original_manifest_mode: int | None = None
    if manifest_path.is_file() and not manifest_path.is_symlink():
        original_manifest_bytes = manifest_path.read_bytes()
        original_manifest_mode = stat.S_IMODE(manifest_path.stat().st_mode)
    backups: list[str] = []
    applied: list[dict[str, Any]] = []
    try:
        for write in planned_writes:
            if write["resource"]["type"] == "skill":
                base = root
                relative_directory = Path(".agents") / "skills" / "frontend-design-director"
                filename = "SKILL.md"
            else:
                base = safe_agents_root
                relative_directory = agents_relative
                filename = str(write["resource"]["name"])
            directory = _safe_project_directory(base, relative_directory)
            directory.mkdir(parents=True, exist_ok=True, mode=0o755)
            directory = _safe_project_directory(base, relative_directory)
            destination = directory / filename
            write["destination"] = destination
            component = next(item for item in selected if item["id"] == write["resource"]["id"])
            component["destination"] = str(destination)
            resources_for_manifest[write["resource"]["id"]]["destination"] = str(destination)
            write["staged"] = _stage_codex_resource(destination, write["resource"]["content"], write["previous"].get("mode"))

        for write in planned_writes:
            destination = write["destination"]
            previous = write["previous"]
            current = _inspect_codex_resource(destination, None, write["bundled_sha256"])
            if current["status"] == "invalid" or current.get("installed_sha256") != previous.get("installed_sha256"):
                if previous["status"] == "missing" and current["status"] == "missing":
                    pass
                else:
                    raise RuntimeError(f"Codex integration file changed during update planning: {destination}")
            if previous["status"] != "missing":
                backup = _create_codex_backup(destination, str(previous["installed_sha256"]))
                backups.append(str(backup))
                component = next(item for item in selected if item["id"] == write["resource"]["id"])
                component["backup"] = str(backup)

        for write in planned_writes:
            destination = write["destination"]
            previous = write["previous"]
            if destination.is_symlink():
                raise ValueError(f"Codex integration file became a symbolic link during update: {destination}")
            if previous["status"] == "missing":
                if destination.exists():
                    raise RuntimeError(f"Codex integration file appeared during update: {destination}")
            elif _file_sha256(destination) != previous["installed_sha256"]:
                raise RuntimeError(f"Codex integration file changed during update: {destination}")
            os.replace(write["staged"], destination)
            applied.append(write)
            if _file_sha256(destination) != write["bundled_sha256"]:
                raise OSError(f"Verification failed after writing Codex integration file: {destination}")

        manifest_changed = previous_manifest is None or previous_manifest.get("_migrated_from_schema") or json.loads(original_manifest_bytes or b"{}") != manifest
        if manifest_changed:
            _write_codex_manifest(manifest_path, manifest)
        saved_manifest = _read_codex_manifest(manifest_path, scope=scope, root=root, agents_directory=agents_directory)
        if saved_manifest is None:
            raise OSError("Codex installation manifest was not created.")
        for item in selected:
            if item["status"] in {"installed", "updated", "backed_up_and_updated"} and _file_sha256(Path(item["destination"])) != item["bundled_sha256"]:
                raise OSError(f"Final hash verification failed for {item['destination']}.")
    except Exception as error:
        rollback_errors: list[str] = []
        for write in reversed(applied):
            destination = write["destination"]
            try:
                if write["previous"]["status"] == "missing":
                    if destination.is_symlink():
                        raise ValueError(f"Refusing to remove a replacement that became a symlink: {destination}")
                    destination.unlink(missing_ok=True)
                else:
                    _atomic_restore(destination, write["previous"]["content"], write["previous"].get("mode"))
            except Exception as rollback_error:
                rollback_errors.append(f"{destination}: {rollback_error}")
        try:
            if original_manifest_bytes is None:
                if manifest_path.exists() and not manifest_path.is_symlink():
                    manifest_path.unlink()
            elif not manifest_path.is_symlink() and manifest_path.read_bytes() != original_manifest_bytes:
                _atomic_restore(manifest_path, original_manifest_bytes, original_manifest_mode)
        except Exception as rollback_error:
            rollback_errors.append(f"{manifest_path}: {rollback_error}")
        if rollback_errors:
            raise RuntimeError(f"Codex update failed: {error}; rollback errors: {'; '.join(rollback_errors)}") from error
        raise
    finally:
        for write in planned_writes:
            staged = write.get("staged")
            if staged:
                Path(staged).unlink(missing_ok=True)

    matched = sum(1 for item in selected if _file_sha256(Path(item["destination"])) == item["bundled_sha256"])
    verification = {"passed": matched == len(selected), "matched": matched, "total": len(selected)}
    unresolved_obsolete = [item for item in obsolete_resources if item["status"] != "obsolete_missing"]
    result_status = "synchronized" if verification["passed"] and not unresolved_obsolete else "conflicts"
    skill_component = next((item for item in selected if item["id"] == "skill"), None)
    agent_components = [item for item in selected if item["type"] == "agent"]
    skill = _component_install_result(skill_component) if skill_component else None
    agents = _agent_install_result(agent_components, str(safe_agents_directory)) if include_agents else None
    return {
        "scope": scope,
        "root": str(root),
        "status": result_status,
        "components": selected,
        "obsolete_resources": obsolete_resources,
        "backups": backups,
        "verification": verification,
        "skill": skill,
        "agents": agents,
        "install_manifest": str(manifest_path),
        "next_step": "Open a new Codex session to discover the installed skill and agents.",
    }


def _component_install_result(component: dict[str, Any] | None) -> dict[str, Any]:
    if component is None:
        return {"installed": False, "status": "not_selected"}
    status = component["status"]
    return {
        "installed": status == "installed",
        "updated": status in {"updated", "backed_up_and_updated"},
        "current": status in {"current", "current_unmanaged"},
        "status": status,
        "path": component["destination"],
        "backup": component["backup"],
        "already_present_not_overwritten": component["destination"] if status in {"outdated", "modified_locally", "untracked_legacy", "invalid"} else None,
    }


def _agent_install_result(components: list[dict[str, Any]], directory: str) -> dict[str, Any]:
    return {
        "installed": [item["destination"] for item in components if item["status"] == "installed"],
        "updated": [item["destination"] for item in components if item["status"] in {"updated", "backed_up_and_updated"}],
        "current": [item["destination"] for item in components if item["status"] in {"current", "current_unmanaged"}],
        "already_present_not_overwritten": [item["destination"] for item in components if item["status"] in {"outdated", "modified_locally", "untracked_legacy", "invalid"}],
        "resources": components,
        "path": directory,
    }


def _installation_doctor(
    project: Path,
    scope: str,
    *,
    expected_source: Path | None = None,
) -> dict[str, Any]:
    """Inspect runtime package metadata and Codex resource hashes without writing."""
    if expected_source is None:
        expected_source = _current_frontend_director_checkout()
    try:
        root, agents_root, agents_relative, agents_directory = _codex_install_locations(project, scope, create=False)
        manifest_path = _codex_manifest_path(root, agents_directory)
    except (OSError, ValueError) as error:
        return _installation_doctor_path_error(project, scope, expected_source, str(error))
    manifest_error: str | None = None
    try:
        manifest = _read_codex_manifest(manifest_path, scope=scope, root=root, agents_directory=agents_directory)
    except ValueError as error:
        manifest = None
        manifest_error = str(error)
    previous_resources = manifest.get("resources", {}) if manifest else {}
    try:
        skill_directory = _safe_project_directory(root, Path(".agents") / "skills" / "frontend-design-director")
        safe_agents_directory = _safe_project_directory(agents_root.resolve(strict=False), agents_relative)
    except (OSError, ValueError) as error:
        return _installation_doctor_path_error(project, scope, expected_source, str(error), manifest_path=manifest_path, manifest_error=manifest_error)
    bundled_resources = _bundled_codex_resources()
    components: list[dict[str, Any]] = []
    counts = {"current": 0, "outdated": 0, "modified": 0, "untracked": 0, "missing": 0, "invalid": 0, "obsolete": 0}

    for resource in bundled_resources:
        resource_id = str(resource["id"])
        destination = skill_directory / "SKILL.md" if resource_id == "skill" else safe_agents_directory / str(resource["name"])
        bundled_hash = hashlib.sha256(resource["content"]).hexdigest()
        inspection = _inspect_codex_resource(destination, previous_resources.get(resource_id), bundled_hash)
        status = inspection["status"]
        if status in {"current", "current_unmanaged"}:
            counts["current"] += 1
        elif status == "outdated_unmodified":
            counts["outdated"] += 1
        elif status == "modified_locally":
            counts["modified"] += 1
        elif status == "untracked_legacy":
            counts["untracked"] += 1
        else:
            counts["missing" if status == "missing" else "invalid"] += 1
        components.append({
            "id": resource_id,
            "type": resource["type"],
            "name": resource["name"],
            "destination": str(destination),
            "bundled_sha256": bundled_hash,
            "installed_sha256": inspection.get("installed_sha256"),
            "managed": bool(previous_resources.get(resource_id, {}).get("managed")),
            "status": status,
            "error": inspection.get("error"),
        })

    obsolete_resources = _inspect_obsolete_codex_resources(previous_resources, {str(item["id"]) for item in bundled_resources})
    for resource in obsolete_resources:
        if resource["status"] != "obsolete_missing":
            counts["obsolete"] += 1
        components.append({**resource, "bundled_sha256": None})

    legacy_manifest = bool(manifest and manifest.get("_migrated_from_schema"))
    if counts["modified"] or counts["untracked"] or counts["invalid"] or counts["obsolete"] or manifest_error:
        codex_status = "conflicts"
    elif counts["outdated"] or counts["missing"]:
        codex_status = "update_available"
    elif legacy_manifest:
        codex_status = "manifest_update_available"
    elif not manifest and counts["current"] == len(components):
        codex_status = "current_unmanaged"
    else:
        codex_status = "current"
    manifest_status = "invalid" if manifest_error else ("schema_v1" if legacy_manifest else ("present" if manifest else "missing"))
    python_report = _python_installation_report(expected_source)
    recommendations: list[str] = []
    source_path = python_report.get("source_path")
    if not python_report["supported_python"]:
        recommendations.append("Use Python 3.11 or newer to run frontend-design-director.")
    if not python_report["distribution_installed"] or python_report.get("distribution_version") != __version__ or python_report.get("source_matches_active") is False:
        location = expected_source.expanduser().resolve() if expected_source else source_path
        location_text = str(location) if location else "<path-to-frontend-orchestrator>"
        operation = "Install" if not python_report["distribution_installed"] else "Refresh"
        recommendations.append(f"{operation} the Python CLI from the intended checkout: pipx install --force --editable {location_text}")
    if manifest_error:
        recommendations.append(f"Inspect and back up the invalid install manifest before synchronizing: {manifest_path}")
    elif codex_status in {"update_available", "manifest_update_available"}:
        recommendations.append(f"Synchronize the installed Codex files: frontend-director update-codex --scope {scope}" + (f" --project {project}" if scope == "project" else ""))
    elif codex_status == "current_unmanaged":
        recommendations.append(f"Create an ownership manifest without replacing current files: frontend-director install-codex --scope {scope}" + (f" --project {project}" if scope == "project" else ""))
    elif counts["modified"] or counts["untracked"]:
        recommendations.append(f"To replace modified or legacy resource files, run frontend-director update-codex --scope {scope} --force" + (f" --project {project}" if scope == "project" else "") + ". Existing files will be backed up first.")
    if counts["obsolete"]:
        recommendations.append("Review obsolete or locally modified managed agent files listed in the resource inventory. They are preserved until you explicitly remove or uninstall them.")
    if expected_source is not None and python_report.get("expected_source_matches") is False:
        expected = str(expected_source.expanduser().resolve())
        recommendations.append(f"The active package is not using the expected checkout. Reinstall with: pipx install --force --editable {expected}")
    if not recommendations and codex_status == "current":
        recommendations.append("The Python package and bundled Codex resources appear current.")

    return {
        "python": python_report,
        "codex": {
            "cli": {"available": shutil.which("codex") is not None, "path": shutil.which("codex")},
            "scope": scope,
            "user_home": str(Path.home()),
            "codex_home": str(Path(os.environ.get("CODEX_HOME", "~/.codex")).expanduser().resolve(strict=False)),
            "agents_directory": str(agents_directory),
            "skill_directory": str(skill_directory),
            "manifest": {
                "present": manifest is not None or manifest_error is not None,
                "schema_version": 1 if legacy_manifest else (manifest.get("schema_version") if manifest else None),
                "path": str(manifest_path),
                "status": manifest_status,
                "error": manifest_error,
            },
            "status": codex_status,
            "summary": {**counts, "total": len(components)},
            "resources": components,
        },
        "recommendations": recommendations,
        "status": "current" if codex_status == "current" and python_report["distribution_installed"] and python_report.get("source_matches_active") is not False and python_report.get("distribution_version") == __version__ and python_report.get("expected_source_matches") is not False else "action_recommended",
    }


def _installation_doctor_path_error(
    project: Path,
    scope: str,
    expected_source: Path | None,
    error: str,
    *,
    manifest_path: Path | None = None,
    manifest_error: str | None = None,
) -> dict[str, Any]:
    return {
        "python": _python_installation_report(expected_source),
        "codex": {
            "cli": {"available": shutil.which("codex") is not None, "path": shutil.which("codex")},
            "scope": scope,
            "root": str(project.resolve(strict=False) if scope == "project" else Path.home().resolve(strict=False)),
            "codex_home": str(Path(os.environ.get("CODEX_HOME", "~/.codex")).expanduser().resolve(strict=False)),
            "manifest": {
                "present": bool(manifest_path and manifest_path.is_file()),
                "path": str(manifest_path) if manifest_path else None,
                "status": "invalid" if manifest_error or error else "unknown",
                "error": manifest_error,
            },
            "status": "conflicts",
            "summary": {"current": 0, "outdated": 0, "modified": 0, "untracked": 0, "missing": 0, "invalid": 1, "obsolete": 0, "total": 0},
            "resources": [],
            "path_error": error,
        },
        "recommendations": [f"Resolve the unsafe or inaccessible Codex installation path before updating: {error}"],
        "status": "action_recommended",
    }


def _source_checkout_root(active_module: Path) -> Path | None:
    source_directory = active_module.parent.parent
    if source_directory.name != "src":
        return None
    checkout = source_directory.parent
    return checkout if (checkout / "pyproject.toml").is_file() else None


def _current_frontend_director_checkout() -> Path | None:
    manifest_path = Path.cwd() / "pyproject.toml"
    try:
        project = tomllib.loads(manifest_path.read_text(encoding="utf-8")).get("project", {})
    except (OSError, tomllib.TOMLDecodeError):
        return None
    if isinstance(project, dict) and project.get("name") == "frontend-design-director":
        return manifest_path.parent.resolve(strict=False)
    return None


def _python_installation_report(expected_source: Path | None) -> dict[str, Any]:
    active_module = Path(__file__).resolve()
    executable = Path(sys.argv[0]).expanduser().resolve(strict=False)
    distribution_version: str | None = None
    distribution_location: str | None = None
    installation_mode = "source checkout" if _source_checkout_root(active_module) else "unknown"
    distribution_source_path: Path | None = None
    editable: bool | None = None
    try:
        distribution = metadata.distribution("frontend-design-director")
    except metadata.PackageNotFoundError:
        distribution = None
    if distribution is not None:
        distribution_version = distribution.version
        distribution_location = str(Path(distribution.locate_file("")).resolve(strict=False))
        direct_url_text = distribution.read_text("direct_url.json")
        if direct_url_text:
            try:
                direct_url = json.loads(direct_url_text)
                if not isinstance(direct_url, dict):
                    raise ValueError("direct_url.json must contain an object")
                dir_info = direct_url.get("dir_info", {})
                if isinstance(dir_info, dict) and isinstance(dir_info.get("editable"), bool):
                    editable = dir_info["editable"]
                parsed = urlparse(str(direct_url.get("url", "")))
                if parsed.scheme == "file":
                    distribution_source_path = Path(unquote(parsed.path)).resolve(strict=False)
                elif parsed.scheme == "" and parsed.path:
                    distribution_source_path = Path(parsed.path).resolve(strict=False)
            except (json.JSONDecodeError, OSError, TypeError, ValueError):
                editable = None
        installation_mode = (
            "editable" if editable else "wheel or non-editable"
        ) if editable is not None else "unknown"
    inferred_checkout = _source_checkout_root(active_module)
    editable_source_path = distribution_source_path if editable else None
    source_path = distribution_source_path or inferred_checkout
    source_matches_active = active_module.is_relative_to(editable_source_path) if editable_source_path else (True if inferred_checkout and distribution is None else None)
    expected_root = expected_source.expanduser().resolve(strict=False) if expected_source else None
    expected_source_matches = (
        active_module.is_relative_to(expected_root) and (editable_source_path is None or editable_source_path == expected_root)
        if expected_root
        else None
    )
    return {
        "runtime_version": sys.version.split()[0],
        "package_version": __version__,
        "distribution_version": distribution_version,
        "distribution_installed": distribution is not None,
        "installation_mode": installation_mode,
        "editable": editable,
        "source_path": str(source_path) if source_path else None,
        "editable_source_path": str(editable_source_path) if editable_source_path else None,
        "active_module_path": str(active_module),
        "source_matches_active": source_matches_active,
        "expected_source": str(expected_root) if expected_root else None,
        "expected_source_matches": expected_source_matches,
        "distribution_location": distribution_location,
        "executable_path": str(executable),
        "pipx_executable_path": shutil.which("pipx"),
        "supported_python": sys.version_info >= (3, 11),
        "virtual_environment": sys.prefix != sys.base_prefix,
    }


def _remove_owned_file(path: Path, digest: str, result: dict[str, Any]) -> None:
    if path.is_symlink():
        result["preserved_symlinks"].append(str(path))
    elif not path.exists():
        result["already_missing"].append(str(path))
    elif not path.is_file():
        result["preserved_non_files"].append(str(path))
    elif _file_sha256(path) != digest:
        result["preserved_modified"].append(str(path))
    else:
        path.unlink()
        result["removed"].append(str(path))


def _remove_if_empty(path: Path) -> None:
    if path.is_symlink():
        return
    try:
        path.rmdir()
    except OSError:
        pass


def _uninstall_codex(project: Path, scope: str) -> dict[str, Any]:
    """Remove only unchanged files recorded as created by this installer."""
    root, agents_root, agents_relative, agents_directory = _codex_install_locations(project, scope, create=False)
    manifest_path = _codex_manifest_path(root, agents_directory)
    manifest = _read_codex_manifest(manifest_path, scope=scope, root=root, agents_directory=agents_directory)
    if manifest is None:
        return {
            "scope": scope,
            "status": "not_managed",
            "removed": [],
            "message": "No ownership manifest exists; no files were removed. Pre-manifest or manually copied files are unmanaged.",
        }

    skill_relative = Path(".agents") / "skills" / "frontend-design-director"
    skill_directory = _safe_project_directory(root, skill_relative)
    if agents_root.is_dir():
        safe_agents_root = agents_root.resolve(strict=True)
        agents_directory = _safe_project_directory(safe_agents_root, agents_relative)
    else:
        agents_directory = agents_root / agents_relative

    result: dict[str, Any] = {
        "scope": scope,
        "status": "uninstalled",
        "removed": [],
        "already_missing": [],
        "preserved_modified": [],
        "preserved_symlinks": [],
        "preserved_non_files": [],
        "preserved_unmanaged": [],
        "manifest": str(manifest_path),
    }
    for resource in manifest["resources"].values():
        path = Path(resource["destination"])
        if resource["managed"]:
            _remove_owned_file(path, resource["sha256"], result)
        elif path.exists() or path.is_symlink():
            result["preserved_unmanaged"].append(str(path))

    if manifest_path.is_symlink():
        raise ValueError(f"Codex installation manifest became a symbolic link: {manifest_path}")
    manifest_path.unlink()
    result["manifest_removed"] = True
    for directory in (
        skill_directory,
        skill_directory.parent,
        skill_directory.parent.parent,
        agents_directory,
        manifest_path.parent,
    ):
        _remove_if_empty(directory)
    if result["preserved_modified"] or result["preserved_symlinks"] or result["preserved_non_files"] or result["preserved_unmanaged"]:
        result["status"] = "uninstalled_with_preserved_files"
    elif not result["removed"]:
        result["status"] = "already_absent"
    result["python_package_removed"] = False
    result["message"] = "Remove the Python package separately with pipx or pip if desired."
    return result


def _safe_project_directory(root: Path, relative: Path) -> Path:
    """Reject install locations that traverse symlinks or escape the chosen project."""
    current = root
    for component in relative.parts:
        current = current / component
        if current.is_symlink():
            raise ValueError(f"Install location crosses a symbolic link: {current}")
    resolved = current.resolve()
    if not resolved.is_relative_to(root):
        raise ValueError("Install location must remain inside the selected project.")
    return current


if __name__ == "__main__":
    raise SystemExit(main())
