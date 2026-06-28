"""
Repository Traceability:
- Source Documents: DI-SPRINT-03 (Comparison Statuses + Comparison Outcome Codes),
  DI-0006 (Damage Comparison), DI-0034.
- Purpose: Stable enums for the Sprint 03 damage-comparison domain.

NOTE on outcome codes: The authoritative DI-SPRINT-03 spec lists six outcome codes
(NEW, PRE_EXISTING, CHANGED, REPAIRED, UNCERTAIN, NOT_COMPARABLE). The product-owner
locked decision (DECISION-Sprint03-c) names four classes; they map onto the spec codes:
  NEW_DAMAGE -> NEW, PRE_EXISTING_DAMAGE -> PRE_EXISTING, RESOLVED -> REPAIRED,
  NOT_COMPARABLE -> NOT_COMPARABLE. The full spec set is supported for traceability.
"""


class ComparisonStatus:
    NOT_STARTED = "NOT_STARTED"
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    COMPLETED_WITH_WARNINGS = "COMPLETED_WITH_WARNINGS"
    FAILED = "FAILED"
    NOT_COMPARABLE = "NOT_COMPARABLE"
    CANCELLED = "CANCELLED"


ALL_COMPARISON_STATUSES = [
    ComparisonStatus.NOT_STARTED, ComparisonStatus.QUEUED, ComparisonStatus.PROCESSING,
    ComparisonStatus.COMPLETED, ComparisonStatus.COMPLETED_WITH_WARNINGS,
    ComparisonStatus.FAILED, ComparisonStatus.NOT_COMPARABLE, ComparisonStatus.CANCELLED,
]


class ComparisonOutcomeCode:
    NEW = "NEW"
    PRE_EXISTING = "PRE_EXISTING"
    CHANGED = "CHANGED"
    REPAIRED = "REPAIRED"
    UNCERTAIN = "UNCERTAIN"
    NOT_COMPARABLE = "NOT_COMPARABLE"


ALL_OUTCOME_CODES = {
    ComparisonOutcomeCode.NEW, ComparisonOutcomeCode.PRE_EXISTING, ComparisonOutcomeCode.CHANGED,
    ComparisonOutcomeCode.REPAIRED, ComparisonOutcomeCode.UNCERTAIN, ComparisonOutcomeCode.NOT_COMPARABLE,
}
