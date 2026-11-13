"""Command-line interface for human-supervised frontend design workflows."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import sqlite3
import sys
import tempfile
from importlib.resources import files
from pathlib import Path
from typing import Any

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
    report.add_argument("name", choices=["audit-index", "executive-summary", "application-overview", "technical-audit", "behavioral-audit", "interaction-behavior-audit", "accessibility-audit", "performance-audit", "visual-audit", "visual-analysis", "audit-summary", "findings", "coverage-and-limitations", "capability-inventory", "frontend-intelligence", "frontend-architecture-map", "route-and-screen-inventory", "component-inventory", "design-system-analysis", "color-system-analysis", "typography-analysis", "layout-and-density-analysis", "responsive-design-analysis", "runtime-evidence", "browser-evidence", "screenshot-gallery", "implementation-spec", "implementation-spec-md", "implementation-plan", "implementation-plan-md", "final-report", "verification"], help="Report artifact to display.")
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

    install_agents = subparsers.add_parser("install-agents", help="Install bundled read-only specialist Codex agents into a target project's .codex/agents directory without overwriting files.")
    install_agents.add_argument("project_path", nargs="?", type=Path, help="Target project directory; defaults to the current directory.")
    install_agents.add_argument("--project", type=Path, default=argparse.SUPPRESS, help="Target project directory.")
    _add_output(install_agents)

    install_skill = subparsers.add_parser("install-skill", help="Install the bundled Codex workflow skill into a target project's .agents/skills directory without overwriting files.")
    install_skill.add_argument("project_path", nargs="?", type=Path, help="Target project directory; defaults to the current directory.")
    install_skill.add_argument("--project", type=Path, default=argparse.SUPPRESS, help="Target project directory.")
    _add_output(install_skill)

    install_codex = subparsers.add_parser(
        "install-codex",
        help="Install the bundled workflow skill and specialist agents into Codex project or user discovery paths.",
    )
    install_codex.add_argument("project_path", nargs="?", type=Path, help="Target project directory for project scope; defaults to the current directory.")
    install_codex.add_argument("--project", type=Path, default=argparse.SUPPRESS, help="Target project directory for project scope.")
    install_codex.add_argument("--scope", choices=["project", "user"], default="project", help="Install for one project or the current user's Codex environment (default: project).")
    _add_output(install_codex)

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
        if not args.no_update_check:
            _warn_if_update_available()
        if args.command == "init":
            store = _store_for(project)
            director = _director(store, args)
            session = director.create_session(project, args.title)
            _output({"session_id": session.id, "phase": session.phase.value, "project_root": session.project_root, "state_dir": session.state_dir}, args.json_output)
            return 0
        if args.command == "install-agents":
            _output(_install_codex(project, "project", include_skill=False)["agents"], args.json_output)
            return 0
        if args.command == "install-skill":
            _output(_install_codex(project, "project", include_agents=False)["skill"], args.json_output)
            return 0
        if args.command == "install-codex":
            if args.scope == "user" and (args.project_path is not None or hasattr(args, "project")):
                raise ValueError("Do not supply a project path with `install-codex --scope user`.")
            _output(_install_codex(project, args.scope), args.json_output)
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


def _read_codex_manifest(path: Path, *, scope: str, root: Path, agents_directory: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"Codex installation manifest is not a regular file: {path}")
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Codex installation manifest cannot be read: {path}") from error
    if not isinstance(manifest, dict) or manifest.get("schema_version") != 1:
        raise ValueError("Unsupported or malformed Codex installation manifest.")
    if manifest.get("scope") != scope or manifest.get("root") != str(root) or manifest.get("agents_directory") != str(agents_directory):
        raise ValueError("Codex installation scope or CODEX_HOME differs from the saved manifest.")
    skill_hash = manifest.get("skill_sha256")
    agent_hashes = manifest.get("agent_sha256")
    if skill_hash is not None and not _valid_sha256(skill_hash):
        raise ValueError("Codex installation manifest contains an invalid skill hash.")
    if not isinstance(agent_hashes, dict):
        raise ValueError("Codex installation manifest has an invalid agent hash map.")
    for name, digest in agent_hashes.items():
        if not isinstance(name, str) or name in {".", ".."} or Path(name).name != name or not name.endswith(".toml") or not _valid_sha256(digest):
            raise ValueError("Codex installation manifest contains an invalid agent entry.")
    return manifest


def _write_codex_manifest(path: Path, manifest: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if path.is_symlink():
        raise ValueError(f"Codex installation manifest is a symbolic link: {path}")
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    if temporary.exists() or temporary.is_symlink():
        raise ValueError(f"Codex installation temporary file already exists: {temporary}")
    try:
        temporary.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        temporary.chmod(0o600)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _install_codex(
    project: Path,
    scope: str,
    *,
    include_skill: bool = True,
    include_agents: bool = True,
) -> dict[str, Any]:
    """Install the bundled Codex files and record ownership for safe removal."""
    if not include_skill and not include_agents:
        raise ValueError("At least one Codex integration component must be selected.")
    root, agents_root, agents_relative, agents_directory = _codex_install_locations(project, scope, create=True)
    manifest_path = _codex_manifest_path(root, agents_directory)
    manifest = _read_codex_manifest(manifest_path, scope=scope, root=root, agents_directory=agents_directory)
    if manifest is None:
        manifest = {
            "schema_version": 1,
            "scope": scope,
            "root": str(root),
            "agents_directory": str(agents_directory),
            "skill_sha256": None,
            "agent_sha256": {},
        }

    skill = _install_skill(root) if include_skill else None
    agents = _install_agents(agents_root, agents_relative) if include_agents else None
    if skill and skill.get("installed"):
        manifest["skill_sha256"] = _file_sha256(Path(skill["path"]))
    if agents:
        for name in agents["installed"]:
            agent_path = Path(name)
            manifest["agent_sha256"][agent_path.name] = _file_sha256(agent_path)

    has_managed_files = manifest["skill_sha256"] is not None or bool(manifest["agent_sha256"])
    if has_managed_files:
        _write_codex_manifest(manifest_path, manifest)
        manifest_reference = str(manifest_path)
    else:
        manifest_reference = None
    return {
        "scope": scope,
        "root": str(root),
        "skill": skill,
        "agents": agents,
        "install_manifest": manifest_reference,
        "next_step": "Open a new Codex session to discover the installed skill and agents.",
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
        "manifest": str(manifest_path),
    }
    if manifest["skill_sha256"] is not None:
        _remove_owned_file(skill_directory / "SKILL.md", manifest["skill_sha256"], result)
    for name, digest in manifest["agent_sha256"].items():
        _remove_owned_file(agents_directory / name, digest, result)

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
    if result["preserved_modified"] or result["preserved_symlinks"] or result["preserved_non_files"]:
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
