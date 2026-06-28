"""
Repository Traceability:
- Source Documents: DI-SPRINT-03 (Damage Case Statuses + production rules), DI-0012, DI-0034.
- Purpose: Stable enums + transition map for the Sprint 03 damage-case domain.
  Maintenance work-order execution and final charge remain OUTSIDE Damage Intelligence.
"""


class DamageCaseStatus:
    OPEN = "OPEN"
    PENDING_REVIEW = "PENDING_REVIEW"
    REVIEWED = "REVIEWED"
    ADDITIONAL_EVIDENCE_REQUIRED = "ADDITIONAL_EVIDENCE_REQUIRED"
    READY_FOR_MAINTENANCE_REVIEW = "READY_FOR_MAINTENANCE_REVIEW"
    ROUTED_TO_MAINTENANCE = "ROUTED_TO_MAINTENANCE"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


ALL_CASE_STATUSES = [
    DamageCaseStatus.OPEN, DamageCaseStatus.PENDING_REVIEW, DamageCaseStatus.REVIEWED,
    DamageCaseStatus.ADDITIONAL_EVIDENCE_REQUIRED, DamageCaseStatus.READY_FOR_MAINTENANCE_REVIEW,
    DamageCaseStatus.ROUTED_TO_MAINTENANCE, DamageCaseStatus.CLOSED,
    DamageCaseStatus.CANCELLED, DamageCaseStatus.REJECTED,
]

TERMINAL_CASE_STATUSES = {
    DamageCaseStatus.CLOSED, DamageCaseStatus.CANCELLED, DamageCaseStatus.REJECTED,
}

# Decision codes that require a reason on status change.
CASE_STATUSES_REQUIRING_REASON = {
    DamageCaseStatus.ADDITIONAL_EVIDENCE_REQUIRED, DamageCaseStatus.ROUTED_TO_MAINTENANCE,
    DamageCaseStatus.CLOSED, DamageCaseStatus.CANCELLED, DamageCaseStatus.REJECTED,
}

ALLOWED_CASE_TRANSITIONS: dict[str, set[str]] = {
    DamageCaseStatus.OPEN: {
        DamageCaseStatus.PENDING_REVIEW, DamageCaseStatus.REVIEWED,
        DamageCaseStatus.ADDITIONAL_EVIDENCE_REQUIRED, DamageCaseStatus.CANCELLED,
        DamageCaseStatus.REJECTED,
    },
    DamageCaseStatus.PENDING_REVIEW: {
        DamageCaseStatus.REVIEWED, DamageCaseStatus.ADDITIONAL_EVIDENCE_REQUIRED,
        DamageCaseStatus.CANCELLED, DamageCaseStatus.REJECTED,
    },
    DamageCaseStatus.REVIEWED: {
        DamageCaseStatus.READY_FOR_MAINTENANCE_REVIEW, DamageCaseStatus.ADDITIONAL_EVIDENCE_REQUIRED,
        DamageCaseStatus.CLOSED, DamageCaseStatus.CANCELLED, DamageCaseStatus.REJECTED,
    },
    DamageCaseStatus.ADDITIONAL_EVIDENCE_REQUIRED: {
        DamageCaseStatus.PENDING_REVIEW, DamageCaseStatus.REVIEWED,
        DamageCaseStatus.CANCELLED, DamageCaseStatus.REJECTED,
    },
    DamageCaseStatus.READY_FOR_MAINTENANCE_REVIEW: {
        DamageCaseStatus.ROUTED_TO_MAINTENANCE, DamageCaseStatus.REVIEWED,
        DamageCaseStatus.CLOSED, DamageCaseStatus.CANCELLED,
    },
    DamageCaseStatus.ROUTED_TO_MAINTENANCE: {
        DamageCaseStatus.CLOSED, DamageCaseStatus.CANCELLED,
    },
    DamageCaseStatus.CLOSED: set(),
    DamageCaseStatus.CANCELLED: set(),
    DamageCaseStatus.REJECTED: set(),
}


def can_case_transition(current: str, target: str) -> bool:
    return target in ALLOWED_CASE_TRANSITIONS.get(current, set())


class CaseType:
    REPAIR_RELEVANT = "REPAIR_RELEVANT"
    COSMETIC = "COSMETIC"
    PRE_EXISTING = "PRE_EXISTING"
    INFORMATIONAL = "INFORMATIONAL"
    OTHER = "OTHER"


ALL_CASE_TYPES = {
    CaseType.REPAIR_RELEVANT, CaseType.COSMETIC, CaseType.PRE_EXISTING,
    CaseType.INFORMATIONAL, CaseType.OTHER,
}


class CaseLinkType:
    EVIDENCE = "EVIDENCE"
    FINDING = "FINDING"
    COMPARISON_RESULT = "COMPARISON_RESULT"
