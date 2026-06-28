"""
Repository Traceability:
- Source Documents: DI-SPRINT-01 (Inspection Status Lifecycle), DI-0012 (Domain Model).
- Purpose: Stable inspection status codes and allowed transitions.
"""


class InspectionStatus:
    DRAFT = "DRAFT"
    CAPTURE_IN_PROGRESS = "CAPTURE_IN_PROGRESS"
    EVIDENCE_REGISTERED = "EVIDENCE_REGISTERED"
    SUBMITTED = "SUBMITTED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"


ALL_STATUSES = [
    InspectionStatus.DRAFT,
    InspectionStatus.CAPTURE_IN_PROGRESS,
    InspectionStatus.EVIDENCE_REGISTERED,
    InspectionStatus.SUBMITTED,
    InspectionStatus.CANCELLED,
    InspectionStatus.FAILED,
]

TERMINAL_STATUSES = {InspectionStatus.SUBMITTED, InspectionStatus.CANCELLED, InspectionStatus.FAILED}

# Allowed forward transitions. SUBMITTED is reachable ONLY via the /submit endpoint
# (kept here so the status-update endpoint can reject any attempt to set SUBMITTED directly).
ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    InspectionStatus.DRAFT: {
        InspectionStatus.CAPTURE_IN_PROGRESS,
        InspectionStatus.CANCELLED,
        InspectionStatus.FAILED,
    },
    InspectionStatus.CAPTURE_IN_PROGRESS: {
        InspectionStatus.EVIDENCE_REGISTERED,
        InspectionStatus.SUBMITTED,
        InspectionStatus.CANCELLED,
        InspectionStatus.FAILED,
    },
    InspectionStatus.EVIDENCE_REGISTERED: {
        InspectionStatus.SUBMITTED,
        InspectionStatus.CANCELLED,
        InspectionStatus.FAILED,
    },
    InspectionStatus.SUBMITTED: set(),
    InspectionStatus.CANCELLED: set(),
    InspectionStatus.FAILED: set(),
}


def can_transition(current: str, target: str) -> bool:
    return target in ALLOWED_TRANSITIONS.get(current, set())
