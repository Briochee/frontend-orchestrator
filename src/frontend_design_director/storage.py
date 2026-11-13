"""SQLite persistence for sessions, findings, decisions, approvals, and artifacts."""

from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import Approval, Finding, Phase, Session, utc_now
from .state_machine import validate_transition

WORKFLOW_STATE_DIRECTORY = Path(".agents") / "frontend-design-director"
LEGACY_WORKFLOW_STATE_DIRECTORY = Path(".frontend-design-director")


class _ClosingConnection(sqlite3.Connection):
    """Keep transaction context management and close each short-lived connection."""

    def __exit__(self, exception_type, exception, traceback):
        try:
            return super().__exit__(exception_type, exception, traceback)
        finally:
            self.close()


class WorkflowStore:
    """Persist durable workflow state in a per-session SQLite database."""

    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        try:
            self.database_path.parent.chmod(0o700)
        except OSError:
            pass
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path, timeout=10, factory=_ClosingConnection)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    project_root TEXT NOT NULL,
                    state_dir TEXT NOT NULL,
                    phase TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    title TEXT NOT NULL,
                    metadata_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL REFERENCES sessions(id),
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS artifacts (
                    session_id TEXT NOT NULL REFERENCES sessions(id),
                    name TEXT NOT NULL,
                    path TEXT NOT NULL,
                    sha256 TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    PRIMARY KEY (session_id, name)
                );
                CREATE TABLE IF NOT EXISTS findings (
                    session_id TEXT NOT NULL REFERENCES sessions(id),
                    finding_id TEXT NOT NULL,
                    audit_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    PRIMARY KEY (session_id, finding_id)
                );
                CREATE TABLE IF NOT EXISTS decisions (
                    session_id TEXT NOT NULL REFERENCES sessions(id),
                    decision_id TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    PRIMARY KEY (session_id, decision_id)
                );
                CREATE TABLE IF NOT EXISTS approvals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL REFERENCES sessions(id),
                    approval_type TEXT NOT NULL,
                    artifact_name TEXT NOT NULL,
                    artifact_sha256 TEXT NOT NULL,
                    approved_scope_json TEXT NOT NULL,
                    decision_ids_json TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    human_confirmation INTEGER NOT NULL,
                    approved_by TEXT NOT NULL,
                    revoked_at TEXT,
                    revoke_reason TEXT
                );
                CREATE TABLE IF NOT EXISTS executions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL REFERENCES sessions(id),
                    role TEXT NOT NULL,
                    status TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    finished_at TEXT,
                    details_json TEXT NOT NULL
                );
                """
            )

    def create_session(self, project_root: Path, state_dir: Path, title: str = "") -> Session:
        project = project_root.resolve(strict=True)
        if not project.is_dir():
            raise ValueError("Target project must be a directory.")
        requested_state = state_dir.absolute()
        try:
            relative_state = requested_state.relative_to(project)
        except ValueError as error:
            raise ValueError("Workflow state must be stored inside the selected project.") from error
        current = project
        for component in relative_state.parts:
            current = current / component
            if current.is_symlink():
                raise ValueError("Workflow state cannot be created through a symbolic link.")
        state = requested_state.resolve()
        if state == project or not state.is_relative_to(project):
            raise ValueError("Workflow state must be a child directory of the selected project.")
        state.mkdir(parents=True, exist_ok=True, mode=0o700)
        session_id = str(uuid.uuid4())
        now = utc_now()
        metadata = {"schema_version": 1}
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO sessions VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (session_id, str(project), str(state), Phase.INITIALIZED.value, now, now, title or project.name, json.dumps(metadata)),
            )
            self._event(connection, session_id, "session_created", {"project_root": str(project)})
        return self.get_session(session_id)

    def get_session(self, session_id: str) -> Session:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if row is None:
            raise KeyError(f"Workflow session not found: {session_id}")
        return Session.from_row(dict(row))

    def latest_session(self) -> Session:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM sessions ORDER BY created_at DESC LIMIT 1").fetchone()
        if row is None:
            raise KeyError("No workflow sessions exist yet.")
        return Session.from_row(dict(row))

    def transition(self, session_id: str, target: Phase, payload: dict[str, Any] | None = None) -> Session:
        with self._connect() as connection:
            row = connection.execute("SELECT phase FROM sessions WHERE id = ?", (session_id,)).fetchone()
            if row is None:
                raise KeyError(f"Workflow session not found: {session_id}")
            current = Phase(row["phase"])
            validate_transition(current, target)
            now = utc_now()
            connection.execute("UPDATE sessions SET phase = ?, updated_at = ? WHERE id = ?", (target.value, now, session_id))
            self._event(connection, session_id, "phase_changed", {"from": current.value, "to": target.value, **(payload or {})})
        return self.get_session(session_id)

    def set_metadata(self, session_id: str, key: str, value: Any) -> None:
        with self._connect() as connection:
            row = connection.execute("SELECT metadata_json FROM sessions WHERE id = ?", (session_id,)).fetchone()
            if row is None:
                raise KeyError(f"Workflow session not found: {session_id}")
            metadata = json.loads(row["metadata_json"])
            metadata[key] = value
            connection.execute(
                "UPDATE sessions SET metadata_json = ?, updated_at = ? WHERE id = ?",
                (json.dumps(metadata, sort_keys=True), utc_now(), session_id),
            )

    def write_artifact(self, session_id: str, name: str, relative_path: str, content: bytes) -> dict[str, Any]:
        session = self.get_session(session_id)
        project_root = Path(session.project_root).resolve(strict=True)
        state_path = Path(session.state_dir)
        if state_path.is_symlink() or not state_path.resolve().is_relative_to(project_root):
            raise ValueError("Workflow state directory was replaced or moved outside the project.")
        root = state_path.resolve()
        path = (root / relative_path).resolve()
        if not path.is_relative_to(root):
            raise ValueError("Artifact path escapes the workflow state directory.")
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        path.write_bytes(content)
        try:
            path.chmod(0o600)
        except OSError:
            pass
        digest = hashlib.sha256(content).hexdigest()
        with self._connect() as connection:
            row = connection.execute("SELECT version FROM artifacts WHERE session_id = ? AND name = ?", (session_id, name)).fetchone()
            version = 1 if row is None else int(row["version"]) + 1
            connection.execute(
                "INSERT INTO artifacts VALUES (?, ?, ?, ?, ?, ?) ON CONFLICT(session_id, name) DO UPDATE SET path=excluded.path, sha256=excluded.sha256, version=excluded.version, created_at=excluded.created_at",
                (session_id, name, str(path), digest, version, utc_now()),
            )
            self._event(connection, session_id, "artifact_written", {"name": name, "sha256": digest, "version": version})
        return {"name": name, "path": str(path), "sha256": digest, "version": version}

    def artifact(self, session_id: str, name: str) -> dict[str, Any]:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM artifacts WHERE session_id = ? AND name = ?", (session_id, name)).fetchone()
        if row is None:
            raise KeyError(f"Artifact not found: {name}")
        result = dict(row)
        path = Path(result["path"])
        if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != result["sha256"]:
            raise ValueError(f"Artifact integrity check failed: {name}")
        return result

    def list_artifacts(self, session_id: str) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM artifacts WHERE session_id = ? ORDER BY name", (session_id,)).fetchall()
        return [dict(row) for row in rows]

    def replace_findings(self, session_id: str, findings: list[Finding]) -> None:
        ids = [item.id for item in findings]
        if len(ids) != len(set(ids)):
            raise ValueError("Finding identifiers must be unique within a session.")
        with self._connect() as connection:
            connection.execute("DELETE FROM findings WHERE session_id = ?", (session_id,))
            connection.executemany(
                "INSERT INTO findings VALUES (?, ?, ?, ?)",
                [(session_id, item.id, item.audit_type.value, json.dumps(item.to_dict(), sort_keys=True)) for item in findings],
            )
            self._event(connection, session_id, "findings_saved", {"count": len(findings)})

    def findings(self, session_id: str, audit_type: str | None = None) -> list[Finding]:
        with self._connect() as connection:
            if audit_type:
                rows = connection.execute("SELECT payload_json FROM findings WHERE session_id = ? AND audit_type = ? ORDER BY finding_id", (session_id, audit_type)).fetchall()
            else:
                rows = connection.execute("SELECT payload_json FROM findings WHERE session_id = ? ORDER BY finding_id", (session_id,)).fetchall()
        return [Finding.from_dict(json.loads(row["payload_json"])) for row in rows]

    def add_decision(self, session_id: str, decision_id: str, payload: dict[str, Any]) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO decisions VALUES (?, ?, ?, ?)",
                (session_id, decision_id, json.dumps(payload, sort_keys=True), utc_now()),
            )
            self._event(connection, session_id, "decision_recorded", {"decision_id": decision_id, "kind": payload.get("kind")})

    def decisions(self, session_id: str) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute("SELECT decision_id, payload_json, created_at FROM decisions WHERE session_id = ? ORDER BY created_at", (session_id,)).fetchall()
        return [{"id": row["decision_id"], **json.loads(row["payload_json"]), "created_at": row["created_at"]} for row in rows]

    def add_approval(self, approval: Approval) -> None:
        if not approval.human_confirmation or approval.approved_by != "human":
            raise ValueError("Agent-generated approval records are not accepted.")
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO approvals(session_id, approval_type, artifact_name, artifact_sha256, approved_scope_json, decision_ids_json, timestamp, human_confirmation, approved_by) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (approval.session_id, approval.approval_type, approval.artifact_name, approval.artifact_sha256, json.dumps(approval.approved_scope), json.dumps(approval.decision_ids), approval.timestamp, int(approval.human_confirmation), approval.approved_by),
            )
            self._event(connection, approval.session_id, "human_approval", {"approval_type": approval.approval_type, "artifact_name": approval.artifact_name, "artifact_sha256": approval.artifact_sha256, "scope": list(approval.approved_scope)})

    def latest_valid_approval(self, session_id: str, approval_type: str, artifact_name: str) -> Approval | None:
        current = self.artifact(session_id, artifact_name)
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM approvals WHERE session_id = ? AND approval_type = ? AND artifact_name = ? AND revoked_at IS NULL ORDER BY id DESC LIMIT 1",
                (session_id, approval_type, artifact_name),
            ).fetchone()
        if row is None:
            return None
        if row["artifact_sha256"] != current["sha256"] or not row["human_confirmation"] or row["approved_by"] != "human":
            return None
        return Approval(
            session_id=row["session_id"], approval_type=row["approval_type"], artifact_name=row["artifact_name"], artifact_sha256=row["artifact_sha256"],
            approved_scope=tuple(json.loads(row["approved_scope_json"])), timestamp=row["timestamp"], human_confirmation=bool(row["human_confirmation"]),
            decision_ids=tuple(json.loads(row["decision_ids_json"])), approved_by=row["approved_by"],
        )

    def revoke_approvals(self, session_id: str, approval_types: tuple[str, ...], reason: str) -> None:
        if not approval_types:
            return
        placeholders = ",".join("?" for _ in approval_types)
        with self._connect() as connection:
            connection.execute(
                f"UPDATE approvals SET revoked_at = ?, revoke_reason = ? WHERE session_id = ? AND approval_type IN ({placeholders}) AND revoked_at IS NULL",
                (utc_now(), reason, session_id, *approval_types),
            )
            self._event(connection, session_id, "approvals_revoked", {"types": list(approval_types), "reason": reason})

    def add_execution(self, session_id: str, role: str, status: str, details: dict[str, Any], started_at: str | None = None) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO executions(session_id, role, status, started_at, finished_at, details_json) VALUES (?, ?, ?, ?, ?, ?)",
                (session_id, role, status, started_at or utc_now(), utc_now(), json.dumps(details, sort_keys=True)),
            )

    def history(self, session_id: str) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute("SELECT timestamp, event_type, payload_json FROM events WHERE session_id = ? ORDER BY id", (session_id,)).fetchall()
        return [{"timestamp": row["timestamp"], "event_type": row["event_type"], "payload": json.loads(row["payload_json"])} for row in rows]

    @staticmethod
    def _event(connection: sqlite3.Connection, session_id: str, event_type: str, payload: dict[str, Any]) -> None:
        connection.execute(
            "INSERT INTO events(session_id, timestamp, event_type, payload_json) VALUES (?, ?, ?, ?)",
            (session_id, datetime.now(timezone.utc).isoformat(timespec="seconds"), event_type, json.dumps(payload, sort_keys=True)),
        )
