"""
Repository Traceability:
- Source Documents: DI-SPRINT-03 (Review Decision Codes + review routing), DI-0019, DI-0034.
- Purpose: Stable enums for the Sprint 03 review-queue domain.
"""


class ReviewItemStatus:
    PENDING = "PENDING"
    IN_REVIEW = "IN_REVIEW"
    DECIDED = "DECIDED"
    ESCALATED = "ESCALATED"
    ADDITIONAL_EVIDENCE_REQUIRED = "ADDITIONAL_EVIDENCE_REQUIRED"


ALL_REVIEW_ITEM_STATUSES = [
    ReviewItemStatus.PENDING, ReviewItemStatus.IN_REVIEW, ReviewItemStatus.DECIDED,
    ReviewItemStatus.ESCALATED, ReviewItemStatus.ADDITIONAL_EVIDENCE_REQUIRED,
]

TERMINAL_REVIEW_STATUSES = {ReviewItemStatus.DECIDED}


class ReviewDecisionCode:
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"
    EDITED = "EDITED"
    ESCALATED = "ESCALATED"
    ADDITIONAL_EVIDENCE_REQUIRED = "ADDITIONAL_EVIDENCE_REQUIRED"
    DEFERRED = "DEFERRED"
    DUPLICATE = "DUPLICATE"


ALL_DECISION_CODES = {
    ReviewDecisionCode.CONFIRMED, ReviewDecisionCode.REJECTED, ReviewDecisionCode.EDITED,
    ReviewDecisionCode.ESCALATED, ReviewDecisionCode.ADDITIONAL_EVIDENCE_REQUIRED,
    ReviewDecisionCode.DEFERRED, ReviewDecisionCode.DUPLICATE,
}

# Decision codes that require a free-text reason.
DECISIONS_REQUIRING_REASON = {
    ReviewDecisionCode.REJECTED, ReviewDecisionCode.ESCALATED,
    ReviewDecisionCode.ADDITIONAL_EVIDENCE_REQUIRED, ReviewDecisionCode.DUPLICATE,
}


class ReviewObjectType:
    DAMAGE_FINDING = "DAMAGE_FINDING"
    COMPARISON_RESULT = "COMPARISON_RESULT"


class ReviewPriority:
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
