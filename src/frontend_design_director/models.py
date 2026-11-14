"""Validated JSON-compatible contracts shared by discovery and workflow stages."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from typing import Any


def utc_now() -> str:
    """Return a timezone-aware ISO-8601 timestamp."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Phase(StrEnum):
    INITIALIZED = "INITIALIZED"
    DISCOVERING = "DISCOVERING"
    CAPABILITIES_REVIEW = "CAPABILITIES_REVIEW"
    AUDITING = "AUDITING"
    AUDIT_COMPLETED = "AUDIT_COMPLETED"
    AUDIT_COMPLETED_WITH_LIMITATIONS = "AUDIT_COMPLETED_WITH_LIMITATIONS"
    AUDIT_INCOMPLETE = "AUDIT_INCOMPLETE"
    AWAITING_DIRECTION = "AWAITING_DIRECTION"
    DIRECTION_APPROVED = "DIRECTION_APPROVED"
    GENERATING_MOCKUPS = "GENERATING_MOCKUPS"
    AWAITING_MOCKUP_REVIEW = "AWAITING_MOCKUP_REVIEW"
    MOCKUP_REVISION = "MOCKUP_REVISION"
    MOCKUP_APPROVED = "MOCKUP_APPROVED"
    AWAITING_IMPLEMENTATION_APPROVAL = "AWAITING_IMPLEMENTATION_APPROVAL"
    IMPLEMENTING = "IMPLEMENTING"
    PATCH_READY = "PATCH_READY"
    APPLYING = "APPLYING"
    VERIFYING = "VERIFYING"
    COMPLETED = "COMPLETED"
    PAUSED = "PAUSED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class AuditType(StrEnum):
    TECHNICAL = "technical"
    VISUAL = "visual"
    BEHAVIORAL = "behavioral"


class Severity(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Confidence(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class VerificationStatus(StrEnum):
    OBSERVED = "observed"
    MEASURED = "measured"
    STATIC_ANALYSIS = "static_analysis"
    HYPOTHESIS = "hypothesis"
    NOT_VERIFIED = "not_verified"


@dataclass(frozen=True)
class EvidenceReference:
    """Point to a repository file, screenshot, command result, or unavailable evidence."""

    kind: str
    reference: str
    description: str
    line: int | None = None
    viewport: str | None = None

    def __post_init__(self) -> None:
        if not self.kind.strip() or not self.reference.strip():
            raise ValueError("Evidence kind and reference must be non-empty.")
        if self.line is not None and self.line < 1:
            raise ValueError("Evidence line numbers start at 1.")


@dataclass(frozen=True)
class Finding:
    """A stable, evidence-linked technical, behavioral, or visual audit finding."""

    id: str
    audit_type: AuditType
    category: str
    severity: Severity
    title: str
    description: str
    affected_routes: tuple[str, ...] = ()
    affected_components: tuple[str, ...] = ()
    evidence: tuple[EvidenceReference, ...] = ()
    impact: str = ""
    recommendation: str = ""
    confidence: Confidence = Confidence.MEDIUM
    verification_status: VerificationStatus = VerificationStatus.STATIC_ANALYSIS
    requires_human_decision: bool = False

    def __post_init__(self) -> None:
        if not self.id.strip() or not self.title.strip() or not self.description.strip():
            raise ValueError("Finding id, title, and description must be non-empty.")
        if not self.category.strip():
            raise ValueError("Finding category must be non-empty.")
        if not isinstance(self.audit_type, AuditType):
            object.__setattr__(self, "audit_type", AuditType(self.audit_type))
        if not isinstance(self.severity, Severity):
            object.__setattr__(self, "severity", Severity(self.severity))
        if not isinstance(self.confidence, Confidence):
            object.__setattr__(self, "confidence", Confidence(self.confidence))
        if not isinstance(self.verification_status, VerificationStatus):
            object.__setattr__(self, "verification_status", VerificationStatus(self.verification_status))
        if not isinstance(self.evidence, tuple):
            object.__setattr__(self, "evidence", tuple(self.evidence))
        if any(not isinstance(item, EvidenceReference) for item in self.evidence):
            raise ValueError("Finding evidence entries must be EvidenceReference values.")

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        for key, enum_type in (
            ("audit_type", AuditType),
            ("severity", Severity),
            ("confidence", Confidence),
            ("verification_status", VerificationStatus),
        ):
            result[key] = enum_type(result[key]).value
        result["evidence"] = [asdict(item) for item in self.evidence]
        return result

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> Finding:
        data = dict(value)
        data["audit_type"] = AuditType(data["audit_type"])
        data["severity"] = Severity(data["severity"])
        data["confidence"] = Confidence(data.get("confidence", "medium"))
        data["verification_status"] = VerificationStatus(data.get("verification_status", "static_analysis"))
        data["evidence"] = tuple(EvidenceReference(**item) for item in data.get("evidence", []))
        for key in ("affected_routes", "affected_components"):
            data[key] = tuple(data.get(key, ()))
        return cls(**data)


@dataclass(frozen=True)
class Capability:
    """Describe a discovered capability without overstating availability."""

    name: str
    available: bool
    selected_tool: str | None
    status: str
    recommendation: str
    evidence: tuple[str, ...] = ()
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Approval:
    """Persisted human authorization bound to an artifact version and scope."""

    session_id: str
    approval_type: str
    artifact_name: str
    artifact_sha256: str
    approved_scope: tuple[str, ...]
    timestamp: str
    human_confirmation: bool
    decision_ids: tuple[str, ...] = ()
    approved_by: str = "human"

    def __post_init__(self) -> None:
        if self.approved_by != "human" or not self.human_confirmation:
            raise ValueError("Only explicit human confirmation can create an approval.")
        if not self.session_id or not self.approval_type or not self.artifact_name:
            raise ValueError("Approval requires a session, type, and artifact.")
        if not self.artifact_sha256:
            raise ValueError("Approval must bind to a specific artifact digest.")


@dataclass(frozen=True)
class Session:
    id: str
    project_root: str
    state_dir: str
    phase: Phase
    created_at: str
    updated_at: str
    title: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> Session:
        import json

        return cls(
            id=row["id"],
            project_root=str(Path(row["project_root"]).resolve()),
            state_dir=str(Path(row["state_dir"]).resolve()),
            phase=Phase(row["phase"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            title=row["title"],
            metadata=json.loads(row["metadata_json"]),
        )
