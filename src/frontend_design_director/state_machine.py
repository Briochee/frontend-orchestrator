"""Explicit state transitions that keep discovery, design, and implementation separate."""

from .models import Phase


class InvalidTransition(ValueError):
    """Raised when a workflow phase change has not been authorized."""


TRANSITIONS: dict[Phase, frozenset[Phase]] = {
    Phase.INITIALIZED: frozenset({Phase.DISCOVERING, Phase.PAUSED, Phase.CANCELLED}),
    Phase.DISCOVERING: frozenset({Phase.CAPABILITIES_REVIEW, Phase.FAILED, Phase.PAUSED}),
    Phase.CAPABILITIES_REVIEW: frozenset({Phase.AUDITING, Phase.PAUSED, Phase.CANCELLED}),
    Phase.AUDITING: frozenset({Phase.AUDIT_COMPLETED, Phase.FAILED, Phase.PAUSED}),
    Phase.AUDIT_COMPLETED: frozenset({Phase.AWAITING_DIRECTION, Phase.AUDITING, Phase.PAUSED}),
    Phase.AWAITING_DIRECTION: frozenset({Phase.DIRECTION_APPROVED, Phase.AUDITING, Phase.PAUSED, Phase.CANCELLED}),
    Phase.DIRECTION_APPROVED: frozenset({Phase.GENERATING_MOCKUPS, Phase.PAUSED}),
    Phase.GENERATING_MOCKUPS: frozenset({Phase.AWAITING_MOCKUP_REVIEW, Phase.FAILED, Phase.PAUSED}),
    Phase.AWAITING_MOCKUP_REVIEW: frozenset({Phase.MOCKUP_REVISION, Phase.MOCKUP_APPROVED, Phase.AWAITING_DIRECTION, Phase.PAUSED}),
    Phase.MOCKUP_REVISION: frozenset({Phase.GENERATING_MOCKUPS, Phase.AWAITING_DIRECTION, Phase.PAUSED}),
    Phase.MOCKUP_APPROVED: frozenset({Phase.AWAITING_IMPLEMENTATION_APPROVAL, Phase.PAUSED}),
    Phase.AWAITING_IMPLEMENTATION_APPROVAL: frozenset({Phase.IMPLEMENTING, Phase.MOCKUP_REVISION, Phase.PAUSED, Phase.CANCELLED}),
    Phase.IMPLEMENTING: frozenset({Phase.PATCH_READY, Phase.FAILED, Phase.PAUSED}),
    Phase.PATCH_READY: frozenset({Phase.APPLYING, Phase.IMPLEMENTING, Phase.MOCKUP_REVISION, Phase.PAUSED}),
    Phase.APPLYING: frozenset({Phase.VERIFYING, Phase.FAILED, Phase.PAUSED}),
    Phase.VERIFYING: frozenset({Phase.COMPLETED, Phase.FAILED, Phase.PAUSED}),
    # A completed implementation cycle can begin another explicitly selected audit cycle.
    Phase.COMPLETED: frozenset({Phase.DISCOVERING, Phase.AUDITING, Phase.CANCELLED}),
    Phase.FAILED: frozenset({Phase.DISCOVERING, Phase.AUDITING, Phase.MOCKUP_REVISION, Phase.IMPLEMENTING, Phase.PATCH_READY, Phase.VERIFYING, Phase.PAUSED, Phase.CANCELLED}),
    Phase.PAUSED: frozenset({Phase.INITIALIZED, Phase.DISCOVERING, Phase.CAPABILITIES_REVIEW, Phase.AUDITING, Phase.AUDIT_COMPLETED, Phase.AWAITING_DIRECTION, Phase.DIRECTION_APPROVED, Phase.GENERATING_MOCKUPS, Phase.AWAITING_MOCKUP_REVIEW, Phase.MOCKUP_REVISION, Phase.MOCKUP_APPROVED, Phase.AWAITING_IMPLEMENTATION_APPROVAL, Phase.IMPLEMENTING, Phase.PATCH_READY, Phase.APPLYING, Phase.VERIFYING, Phase.CANCELLED}),
    Phase.CANCELLED: frozenset(),
}


def validate_transition(current: Phase, target: Phase) -> None:
    """Reject any state change that is not listed in the workflow graph."""
    if target not in TRANSITIONS[current]:
        raise InvalidTransition(f"Cannot transition workflow from {current.value} to {target.value}.")
