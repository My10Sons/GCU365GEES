---
id: "DI-SPRINT-03"
title: "Damage Intelligence Sprint 03 Production Review Comparison and Damage Cases"
version: "1.0.0"
document_type: "Implementation Plan"
document_class: "Sprint Execution Plan"
status: "Draft"
classification: "Internal"
owner: "Riyadah Technology"
reviewers: "Chief Enterprise Architect, Product Owner, Damage Intelligence Lead, AI Engineering Lead, Backend Lead, Frontend Lead, QA Lead, Security Lead, DevOps Lead, CROMS Lead, Maintenance Lead"
approvers: ""
created: "2026-06-27"
updated: "2026-06-27"
authoritative: true
ai_consumable: true
related: "DI-0005, DI-0006, DI-0008, DI-0009, DI-0011, DI-0012, DI-0014, DI-0015, DI-0019, DI-0020, DI-0031, DI-0032, DI-0033, DI-0034, DI-0035, DI-SPRINT-00, DI-SPRINT-01, DI-SPRINT-02"
---

# Damage Intelligence Sprint 03 Production Review Comparison and Damage Cases

## Executive Summary

Sprint 03 delivers the production-ready review, comparison, and damage case capabilities for Damage Intelligence.

This sprint builds on Sprint 01 inspection and evidence foundation and Sprint 02 image quality and AI detection by adding damage comparison, baseline selection, comparison outcomes, review queue, review decisions, damage case creation, damage case status management, additional evidence requests, and auditability for review and case actions.

Damage Intelligence remains an image analysis and damage detection application for existing GCU365 CROMS and GCU365Maintenance systems.

Damage Intelligence SHALL NOT replace CROMS, GCU365Maintenance, Fleet, Finance, rental lifecycle ownership, maintenance work order execution, actual repair cost ownership, or vehicle asset management.

Sprint 03 is not an MVP sprint. It is a production-ready review, comparison, and case management sprint.

---

# Purpose

The purpose of Sprint 03 is to implement production-ready workflows for comparing vehicle condition, reviewing AI outputs, and managing damage case context.

Sprint 03 SHALL ensure that:

- Current inspection evidence can be compared with baseline evidence.
- Comparison outcomes are stored and traceable.
- Missing or poor baseline evidence is handled safely.
- New, pre-existing, changed, repaired, uncertain, and not comparable outcomes are supported.
- Review queue is available for AI findings and comparison results.
- Reviewers can confirm, reject, edit, escalate, or request additional evidence.
- Damage cases can be created from findings or comparison results.
- Damage cases can be updated with controlled status transitions.
- Review and case actions are auditable.
- AI remains advisory.
- No final liability, charge, repair cost, rental closure, or work order execution decision is made by Damage Intelligence.

---

# Scope

## In Scope

Sprint 03 includes:

- Baseline inspection selection.
- Damage comparison request API.
- Damage comparison result API.
- Comparison outcome model.
- Comparison status lifecycle.
- Review queue API.
- Review decision API.
- Review decision model.
- Review routing rules.
- Additional evidence request foundation.
- Damage case creation API.
- Damage case retrieval API.
- Damage case status update API.
- Damage case linkage to evidence, findings, comparison, and external references.
- Duplicate damage case prevention.
- Audit logging for comparison, review, and case actions.
- Web review queue screens.
- Web damage case screens.
- QA tests for comparison, review, cases, audit, security, and negative scenarios.

## Out of Scope

Sprint 03 does not include:

- Final CROMS production integration.
- Final GCU365Maintenance production integration.
- Final Maintenance handoff production flow.
- Final repair estimate workflow.
- Final report generation engine.
- Final Arabic report rendering.
- Final customer liability decision.
- Final rental charge decision.
- Actual repair cost decision.
- Rental closure.
- Work order execution.
- Technician assignment.

---

# Sprint Goal

The Sprint 03 goal is:

```text
Implement production-ready damage comparison, human review, and damage case context with auditability, tenant isolation, advisory AI boundaries, and controlled status transitions.
```

---

# Production-Ready Expectations

Sprint 03 output SHALL be production-grade workflow foundation work, not prototype work.

The following must be true:

- Comparison results are traceable.
- Baseline selection is controlled.
- Missing baseline does not automatically confirm new damage.
- NotComparable outcomes are supported.
- Review decisions are permission-controlled.
- Review decisions are audited.
- Damage cases are traceable to evidence.
- Damage cases do not duplicate existing CROMS or Maintenance ownership.
- AI outputs remain advisory until reviewed or processed through approved workflow.
- No final customer charge is created by Damage Intelligence.
- No actual repair cost is owned by Damage Intelligence.
- No work order execution is performed by Damage Intelligence.
- Security and tenant isolation are enforced.

---

# Scope Boundary Reminder

Damage Intelligence owns:

- Damage comparison results.
- Damage finding review context.
- Review queue items.
- Review decisions.
- Damage case context.
- Damage case status within Damage Intelligence.
- Evidence-to-case linkage.
- Comparison-to-case linkage.
- Review audit records.
- Case audit records.

Damage Intelligence does not own:

- Rental lifecycle.
- Rental closure.
- Final rental customer charge.
- Customer billing.
- Maintenance work order execution.
- Technician assignment.
- Actual repair cost.
- Finance posting.
- Insurance approval.
- Vehicle asset lifecycle.

---

# Sprint 03 Workstreams

| Workstream | Objective |
|-----------|-----------|
| Backend API | Implement comparison, review, and damage case APIs |
| Domain Model | Implement comparison, review, and damage case entities |
| Database | Implement production migrations |
| Security | Enforce permissions and tenant boundaries |
| Audit | Record comparison, review, and case actions |
| Web | Implement review queue and damage case screens |
| QA | Validate functional, security, audit, and negative tests |
| DevOps | Validate deployment, configuration, logs, and smoke tests |
| Observability | Add metrics, logs, and alerts for review and cases |

---

# Domain Objects

Sprint 03 SHOULD implement the following domain objects.

| Object | Purpose |
|-------|---------|
| DamageComparison | Represents comparison between baseline and current inspection |
| DamageComparisonResult | Stores comparison outcome for findings or image regions |
| ReviewQueueItem | Represents item requiring human review |
| ReviewDecision | Stores reviewer decision and reasoning |
| AdditionalEvidenceRequest | Stores request for more evidence |
| DamageCase | Represents damage case context |
| DamageCaseStatusHistory | Tracks damage case status changes |
| DamageCaseEvidenceLink | Links evidence to damage case |
| DamageCaseFindingLink | Links findings to damage case |
| DamageCaseComparisonLink | Links comparison results to damage case |

---

# Comparison Statuses

Sprint 03 SHOULD support the following comparison statuses:

| Status | Meaning |
|-------|---------|
| NOT_STARTED | Comparison has not started |
| QUEUED | Comparison is queued |
| PROCESSING | Comparison is running |
| COMPLETED | Comparison completed successfully |
| COMPLETED_WITH_WARNINGS | Comparison completed with warnings |
| FAILED | Comparison failed |
| NOT_COMPARABLE | Comparison cannot be completed reliably |
| CANCELLED | Comparison was cancelled |

---

# Comparison Outcome Codes

Sprint 03 SHOULD support the following comparison outcome codes:

| Code | Meaning |
|-----|---------|
| NEW | Damage appears to be new compared with baseline |
| PRE_EXISTING | Damage appears to exist in baseline |
| CHANGED | Damage appears changed compared with baseline |
| REPAIRED | Damage appears repaired compared with baseline |
| UNCERTAIN | Comparison confidence is insufficient |
| NOT_COMPARABLE | Evidence cannot be compared reliably |

Stable codes SHALL remain language-neutral.

Localized labels MAY be added later.

---

# Review Decision Codes

Sprint 03 SHOULD support the following review decision codes:

| Code | Meaning |
|-----|---------|
| CONFIRMED | Reviewer confirmed the finding or comparison result |
| REJECTED | Reviewer rejected the finding or comparison result |
| EDITED | Reviewer edited finding details |
| ESCALATED | Reviewer escalated the item |
| ADDITIONAL_EVIDENCE_REQUIRED | Reviewer requested more evidence |
| DEFERRED | Reviewer deferred decision |
| DUPLICATE | Reviewer marked item as duplicate |

Review decisions SHALL be auditable.

---

# Damage Case Statuses

Sprint 03 SHOULD support the following damage case statuses:

| Status | Meaning |
|-------|---------|
| OPEN | Damage case is open |
| PENDING_REVIEW | Damage case requires review |
| REVIEWED | Damage case has been reviewed |
| ADDITIONAL_EVIDENCE_REQUIRED | More evidence is required |
| READY_FOR_MAINTENANCE_REVIEW | Case is ready for future Maintenance handoff |
| ROUTED_TO_MAINTENANCE | Case has been routed to Maintenance |
| CLOSED | Case has been closed |
| CANCELLED | Case was cancelled |
| REJECTED | Case was rejected |

Maintenance execution remains outside Damage Intelligence.

---

# Backend API Implementation

## Required APIs

Sprint 03 SHALL implement or extend the following APIs:

```text
POST /api/v1/damage-intelligence/inspection-sessions/{inspectionSessionId}/comparison
GET /api/v1/damage-intelligence/comparisons/{comparisonId}
GET /api/v1/damage-intelligence/inspection-sessions/{inspectionSessionId}/comparisons
GET /api/v1/damage-intelligence/review-queue
GET /api/v1/damage-intelligence/review-items/{reviewItemId}
POST /api/v1/damage-intelligence/review-items/{reviewItemId}/decision
POST /api/v1/damage-intelligence/review-items/{reviewItemId}/additional-evidence-request
POST /api/v1/damage-intelligence/damage-cases
GET /api/v1/damage-intelligence/damage-cases/{damageCaseId}
GET /api/v1/damage-intelligence/damage-cases
PATCH /api/v1/damage-intelligence/damage-cases/{damageCaseId}/status
POST /api/v1/damage-intelligence/damage-cases/{damageCaseId}/link-evidence
POST /api/v1/damage-intelligence/damage-cases/{damageCaseId}/link-finding
POST /api/v1/damage-intelligence/damage-cases/{damageCaseId}/link-comparison
```

## API Rules

All APIs SHALL:

- Require authentication.
- Enforce tenant context.
- Enforce authorization.
- Validate object ownership.
- Validate state transitions.
- Return safe error responses.
- Return correlation ID.
- Create audit records where required.
- Avoid exposing unrestricted evidence URLs.
- Preserve AI advisory boundaries.

---

# Damage Comparison Request API

## Endpoint

```http
POST /api/v1/damage-intelligence/inspection-sessions/{inspectionSessionId}/comparison
```

## Required Behavior

The API SHALL:

- Validate current inspection exists.
- Validate tenant access.
- Validate user or service permission.
- Validate current inspection has eligible evidence.
- Select baseline inspection where provided or configured.
- Validate baseline inspection belongs to same tenant.
- Create comparison request.
- Queue or process comparison.
- Store comparison status.
- Create audit record.

## Example Request

```json
{
  "baselineInspectionSessionId": "DI-INS-BASE-000001",
  "comparisonProfileCode": "CHECK_IN_VS_CHECK_OUT",
  "routeUncertainToReview": true
}
```

## Example Response

```json
{
  "success": true,
  "correlationId": "CORR-000001",
  "data": {
    "comparisonId": "DI-CMP-000001",
    "inspectionSessionId": "DI-INS-000002",
    "baselineInspectionSessionId": "DI-INS-BASE-000001",
    "status": "QUEUED"
  },
  "errors": []
}
```

---

# Damage Comparison Result API

## Endpoint

```http
GET /api/v1/damage-intelligence/comparisons/{comparisonId}
```

## Required Behavior

The API SHALL:

- Validate comparison exists.
- Validate tenant access.
- Validate permission.
- Return comparison status.
- Return baseline inspection reference.
- Return current inspection reference.
- Return comparison outcomes.
- Return confidence score where available.
- Return uncertainty reason where applicable.
- Return review required flag where applicable.

## Example Response

```json
{
  "success": true,
  "correlationId": "CORR-000002",
  "data": {
    "comparisonId": "DI-CMP-000001",
    "status": "COMPLETED",
    "currentInspectionSessionId": "DI-INS-000002",
    "baselineInspectionSessionId": "DI-INS-000001",
    "outcomes": [
      {
        "comparisonResultId": "DI-CMP-RES-000001",
        "damageFindingId": "DI-FND-000002",
        "comparisonOutcomeCode": "NEW",
        "confidenceScore": 0.82,
        "uncertaintyReason": null,
        "reviewRequired": true
      }
    ]
  },
  "errors": []
}
```

---

# Missing Baseline Handling

If no valid baseline exists, the system SHALL:

- Return `NOT_COMPARABLE` or controlled missing baseline status.
- Record the reason.
- Avoid confirming new damage automatically.
- Route to review where configured.
- Allow additional evidence request where configured.
- Create audit record.

Missing baseline SHALL NOT create final liability or charge decision.

---

# NotComparable Handling

If images cannot be compared reliably, the system SHALL:

- Store outcome as `NOT_COMPARABLE`.
- Store reason.
- Avoid confirming damage automatically.
- Route to review where configured.
- Allow additional evidence request.
- Preserve all evidence.
- Create audit record.

---

# Review Queue API

## Endpoint

```http
GET /api/v1/damage-intelligence/review-queue
```

## Required Behavior

The API SHALL:

- Validate tenant access.
- Validate reviewer permission.
- Return pending review items.
- Support filtering by status, severity, branch, inspection type, source, and age where practical.
- Return item priority.
- Return item age.
- Return linked inspection and evidence references.
- Avoid returning unrestricted evidence URLs.

## Example Response

```json
{
  "success": true,
  "correlationId": "CORR-000003",
  "data": {
    "items": [
      {
        "reviewItemId": "DI-REV-000001",
        "objectType": "DAMAGE_FINDING",
        "objectId": "DI-FND-000001",
        "priority": "HIGH",
        "severityCode": "MODERATE",
        "reviewStatus": "PENDING",
        "ageMinutes": 45,
        "inspectionSessionId": "DI-INS-000002"
      }
    ]
  },
  "errors": []
}
```

---

# Review Decision API

## Endpoint

```http
POST /api/v1/damage-intelligence/review-items/{reviewItemId}/decision
```

## Required Behavior

The API SHALL:

- Validate review item exists.
- Validate tenant access.
- Validate reviewer permission.
- Validate decision code.
- Require reason where configured.
- Allow authorized field edits where configured.
- Store review decision.
- Update review item status.
- Update linked finding or comparison status where applicable.
- Create audit record.

## Example Request

```json
{
  "decisionCode": "CONFIRMED",
  "reason": "Damage is visible and supported by evidence.",
  "updatedFinding": {
    "damageTypeCode": "SCRATCH",
    "vehicleAreaCode": "FRONT_BUMPER",
    "severityCode": "MINOR"
  }
}
```

## Example Response

```json
{
  "success": true,
  "correlationId": "CORR-000004",
  "data": {
    "reviewDecisionId": "DI-RD-000001",
    "reviewItemId": "DI-REV-000001",
    "decisionCode": "CONFIRMED",
    "recordedAt": "2026-06-27T11:00:00Z"
  },
  "errors": []
}
```

---

# Additional Evidence Request API

## Endpoint

```http
POST /api/v1/damage-intelligence/review-items/{reviewItemId}/additional-evidence-request
```

## Required Behavior

The API SHALL:

- Validate review item exists.
- Validate tenant access.
- Validate reviewer permission.
- Require request reason.
- Store additional evidence request.
- Link request to inspection, review item, and damage case where applicable.
- Update review item or case status where applicable.
- Create audit record.

---

# Damage Case Creation API

## Endpoint

```http
POST /api/v1/damage-intelligence/damage-cases
```

## Required Behavior

The API SHALL:

- Validate tenant access.
- Validate user permission.
- Validate source finding or comparison result.
- Create damage case.
- Link evidence.
- Link findings.
- Link comparison results.
- Set initial status.
- Prevent duplicate case creation where practical.
- Create audit record.

## Example Request

```json
{
  "inspectionSessionId": "DI-INS-000002",
  "damageFindingIds": [
    "DI-FND-000001"
  ],
  "comparisonResultIds": [
    "DI-CMP-RES-000001"
  ],
  "caseType": "REPAIR_RELEVANT",
  "severityCode": "MODERATE",
  "description": "Possible new scratch on front bumper."
}
```

## Example Response

```json
{
  "success": true,
  "correlationId": "CORR-000005",
  "data": {
    "damageCaseId": "DI-CASE-000001",
    "status": "OPEN",
    "createdAt": "2026-06-27T11:10:00Z"
  },
  "errors": []
}
```

---

# Damage Case Status API

## Endpoint

```http
PATCH /api/v1/damage-intelligence/damage-cases/{damageCaseId}/status
```

## Required Behavior

The API SHALL:

- Validate damage case exists.
- Validate tenant access.
- Validate permission.
- Validate status transition.
- Require reason where configured.
- Update status.
- Store status history.
- Create audit record.

## Production Rules

- Damage Intelligence case status SHALL NOT close rental agreement.
- Damage Intelligence case status SHALL NOT create final customer charge.
- Damage Intelligence case status SHALL NOT execute Maintenance work order.
- Damage Intelligence case status SHALL NOT own actual repair cost.

---

# Database Implementation

Sprint 03 SHALL implement migrations for comparison, review, and damage cases.

## Required Tables

Recommended tables:

```text
di_damage_comparisons
di_damage_comparison_results
di_review_queue_items
di_review_decisions
di_additional_evidence_requests
di_damage_cases
di_damage_case_status_history
di_damage_case_evidence_links
di_damage_case_finding_links
di_damage_case_comparison_links
```

## Required Columns

All Sprint 03 tables SHOULD include:

```text
id
tenant_id
status
created_at
created_by
updated_at
updated_by
correlation_id
```

Review and case tables SHOULD include reason fields where applicable.

## Database Rules

- Tenant ID SHALL be indexed.
- Comparison results SHALL be linked to inspection sessions.
- Review decisions SHALL be linked to review items.
- Damage cases SHALL be linked to evidence, findings, and comparison results.
- Status history SHALL be preserved.
- Audit records SHALL be append-only where practical.
- Duplicate cases SHOULD be prevented where practical.

---

# Security Implementation

Sprint 03 SHALL enforce review and case security controls.

## Required Controls

Security implementation SHALL include:

- Tenant validation before comparison.
- Tenant validation before review access.
- Tenant validation before case access.
- Reviewer role permission checks.
- Damage case permission checks.
- Object-level authorization.
- Evidence link authorization.
- Safe error responses.
- Security event logging for denied access.
- No public evidence URLs.
- No secrets in logs.
- No raw images in logs.

---

# Audit Implementation

Sprint 03 SHALL create audit records for comparison, review, and damage case actions.

## Required Audit Events

| Event | Trigger |
|------|---------|
| DAMAGE_COMPARISON_REQUESTED | Comparison requested |
| DAMAGE_COMPARISON_COMPLETED | Comparison completed |
| DAMAGE_COMPARISON_FAILED | Comparison failed |
| COMPARISON_NOT_COMPARABLE | Comparison not comparable |
| REVIEW_ITEM_CREATED | Review item created |
| REVIEW_DECISION_RECORDED | Review decision recorded |
| REVIEW_ITEM_ESCALATED | Review item escalated |
| ADDITIONAL_EVIDENCE_REQUESTED | Additional evidence requested |
| DAMAGE_CASE_CREATED | Damage case created |
| DAMAGE_CASE_STATUS_CHANGED | Damage case status changed |
| DAMAGE_CASE_LINK_UPDATED | Evidence, finding, or comparison linked to case |
| DUPLICATE_DAMAGE_CASE_PREVENTED | Duplicate case attempt prevented |

Audit records SHALL avoid raw images, secrets, tokens, unrestricted URLs, and unnecessary personal data.

---

# Web Implementation

Sprint 03 SHOULD add web UI support for comparison, review, and damage cases.

## Required Screens and Components

Web SHOULD include:

- Comparison result view.
- Baseline and current inspection context.
- Comparison outcome labels.
- Review queue list.
- Review item detail.
- Review decision form.
- Additional evidence request form.
- Damage case list.
- Damage case detail.
- Damage case status update action.
- Evidence links using controlled access.
- Audit or activity timeline where practical.

## Web Rules

The web portal SHALL:

- Clearly label AI and comparison outputs as advisory unless reviewed.
- Show NotComparable and Uncertain outcomes clearly.
- Require reason for configured review decisions.
- Avoid exposing unrestricted evidence URLs.
- Respect tenant and role permissions.

---

# QA Implementation

QA SHALL validate Sprint 03 against DI-0035.

## Required QA Coverage

Sprint 03 QA SHALL include:

- Baseline selection test.
- New damage comparison test.
- Pre-existing damage comparison test.
- Missing baseline test.
- NotComparable test.
- Review queue access test.
- Review decision test.
- Review edit test.
- Additional evidence request test.
- Damage case creation test.
- Damage case status update test.
- Duplicate damage case test.
- Tenant isolation test.
- Authorization test.
- Audit test.
- Safe error test.
- Smoke test.

---

# Sprint 03 Test Cases

Sprint 03 SHALL execute or prepare the following DI-0035 tests:

```text
TC-DI-0501
TC-DI-0502
TC-DI-0503
TC-DI-0504
TC-DI-0505
TC-DI-0601
TC-DI-0602
TC-DI-0603
TC-DI-0604
TC-DI-0701
TC-DI-0702
TC-DI-0703
TC-DI-1101
TC-DI-1102
TC-DI-1103
TC-DI-1104
TC-DI-1201
TC-DI-1202
TC-DI-1203
TC-DI-1701
```

---

# Observability Implementation

Sprint 03 SHALL provide workflow operational visibility.

## Required Metrics

Recommended metrics:

| Metric | Purpose |
|-------|---------|
| comparison_requested_count | Number of comparison requests |
| comparison_completed_count | Number of completed comparisons |
| comparison_failed_count | Number of failed comparisons |
| comparison_not_comparable_count | Number of NotComparable outcomes |
| review_queue_pending_count | Pending review items |
| review_decision_count | Review decisions recorded |
| additional_evidence_request_count | Additional evidence requests |
| damage_case_created_count | Damage cases created |
| damage_case_status_changed_count | Damage case status changes |
| duplicate_case_prevented_count | Duplicate case prevention events |

## Required Logs

Logs SHALL include:

- Correlation ID.
- Tenant ID where safe.
- Comparison ID where safe.
- Review item ID where safe.
- Damage case ID where safe.
- Safe status and error codes.
- No raw images.
- No secrets.
- No unrestricted evidence URLs.

---

# Production Data Protection Rules

Sprint 03 SHALL follow these data protection rules:

- Reviewers SHALL only access authorized evidence.
- Damage cases SHALL store only required context.
- Customer data SHALL be minimized.
- Evidence access SHALL remain controlled.
- Review reasons SHALL avoid unnecessary sensitive data.
- Audit records SHALL avoid raw evidence.
- Cross-tenant review and case access SHALL be denied.
- Damage case exports are out of scope unless controlled reporting is implemented later.

---

# Acceptance Criteria

## AC-DI-S03-001 — Comparison Request Works

Given an authorized comparison request is submitted, then the system SHALL create a comparison record and process or queue comparison.

## AC-DI-S03-002 — Baseline Selection Is Controlled

Given comparison is requested, then the system SHALL validate baseline inspection and SHALL NOT compare across unauthorized tenants.

## AC-DI-S03-003 — Missing Baseline Is Safe

Given no valid baseline exists, then the system SHALL return missing baseline or NotComparable status and SHALL NOT automatically confirm new damage.

## AC-DI-S03-004 — Comparison Outcomes Are Stored

Given comparison completes, then outcomes SHALL be stored using stable outcome codes.

## AC-DI-S03-005 — Review Queue Works

Given findings or comparison results require review, then authorized reviewers SHALL see them in the review queue.

## AC-DI-S03-006 — Review Decision Works

Given an authorized reviewer records a decision, then the system SHALL store the decision, update related status, and create audit record.

## AC-DI-S03-007 — Additional Evidence Request Works

Given a reviewer requests additional evidence, then the system SHALL store the request and link it to the review context.

## AC-DI-S03-008 — Damage Case Creation Works

Given eligible findings or comparison results exist, then the system SHALL create a damage case linked to evidence and context.

## AC-DI-S03-009 — Damage Case Status Is Controlled

Given a damage case status update is requested, then the system SHALL validate transition, require reason where configured, and preserve status history.

## AC-DI-S03-010 — Damage Intelligence Does Not Own Final Decisions

Given comparison, review, or damage case actions occur, then Damage Intelligence SHALL NOT decide final customer charge, rental closure, actual repair cost, or work order execution.

## AC-DI-S03-011 — Sprint 03 Smoke Test Passes

Given Sprint 03 is complete, then the Sprint 03 smoke test SHALL pass.

---

# Sprint 03 Smoke Test

The Sprint 03 smoke test SHALL include:

1. Start backend API.
2. Verify health endpoint.
3. Create baseline inspection with evidence.
4. Create current inspection with evidence.
5. Run AI analysis or use existing test findings.
6. Request comparison.
7. Confirm comparison result is stored.
8. Confirm review item is created where required.
9. Open review queue.
10. Record review decision.
11. Create damage case.
12. Update damage case status.
13. Verify audit records.
14. Attempt unauthorized review access.
15. Attempt cross-tenant damage case access.
16. Confirm safe errors.
17. Confirm no public evidence URL is exposed.
18. Confirm no final charge, final liability, actual repair cost, rental closure, or work order execution is created.

Expected result:

```text
Sprint 03 production review comparison and damage cases smoke test passed.
```

---

# Definition of Done

Sprint 03 is done when:

- Comparison APIs are implemented.
- Comparison result storage is implemented.
- Missing baseline handling is implemented.
- NotComparable handling is implemented.
- Review queue API is implemented.
- Review decision API is implemented.
- Additional evidence request foundation is implemented.
- Damage case APIs are implemented.
- Damage case status history is implemented.
- Duplicate damage case prevention is implemented where practical.
- Audit records are created.
- Tenant isolation is enforced.
- Authorization is enforced.
- Web review and case screens are implemented where planned.
- Required QA tests pass.
- Sprint 03 smoke test passes.
- Security review is completed.
- Product owner approves sprint completion.

---

# Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Missing baseline creates false new damage | Critical | Use NotComparable or review-required status |
| Review decisions are not audited | Critical | Audit every review decision |
| Damage case duplicates are created | High | Implement duplicate prevention rules |
| AI output is treated as final liability | Critical | Preserve advisory labels and review workflow |
| Cross-tenant review access | Critical | Enforce tenant checks on review and case APIs |
| Case status implies rental closure | High | Keep CROMS ownership boundary explicit |
| Case status implies work order execution | High | Keep Maintenance ownership boundary explicit |
| Reviewer changes finding without trace | High | Preserve previous and new values in audit or history |

---

# Sprint 03 Checklist

| Item | Status |
|------|--------|
| Damage comparison model implemented | Pending |
| Comparison request API implemented | Pending |
| Comparison result API implemented | Pending |
| Baseline selection implemented | Pending |
| Missing baseline handling implemented | Pending |
| NotComparable handling implemented | Pending |
| Review queue model implemented | Pending |
| Review queue API implemented | Pending |
| Review decision API implemented | Pending |
| Additional evidence request implemented | Pending |
| Damage case model implemented | Pending |
| Damage case create API implemented | Pending |
| Damage case get API implemented | Pending |
| Damage case list API implemented | Pending |
| Damage case status API implemented | Pending |
| Damage case link APIs implemented | Pending |
| Duplicate damage case prevention implemented | Pending |
| Audit records implemented | Pending |
| Web review queue implemented | Pending |
| Web damage case screens implemented | Pending |
| QA tests executed | Pending |
| Smoke test passed | Pending |
| Security review completed | Pending |
| Product owner approval completed | Pending |

---

# AI Implementation Contract

AI development agents SHALL:

- Treat this document as the authoritative Sprint 03 production review, comparison, and damage case plan.
- Preserve all acceptance criterion IDs.
- Generate implementation tasks only within Sprint 03 scope.
- Build production-ready comparison, review, and damage case context capabilities.
- Preserve tenant isolation, secure evidence access, auditability, safe errors, advisory AI behavior, and correlation ID behavior.
- Never make Damage Intelligence the owner of final liability, final customer charge, rental closure, actual repair cost, work order execution, Finance posting, Fleet, or vehicle asset lifecycle.
- Do not implement final CROMS integration, Maintenance integration, report generation, or repair estimate workflows in Sprint 03 unless explicitly approved in later sprint scope.
- Raise ambiguity where a task conflicts with DI-0031, DI-0034, or DI-0035.

---

# References

- DI-0005 – AI Damage Detection
- DI-0006 – Damage Comparison
- DI-0008 – Damage Taxonomy
- DI-0009 – Severity Assessment
- DI-0011 – API Specification
- DI-0012 – Domain Model
- DI-0014 – Security and Privacy
- DI-0015 – Audit and Traceability
- DI-0019 – Acceptance Criteria
- DI-0020 – Test Strategy
- DI-0031 – Existing System Integration Scope
- DI-0032 – Implementation Plan
- DI-0033 – User Stories and Backlog
- DI-0034 – OpenAPI Contract
- DI-0035 – QA Test Case Pack
- DI-SPRINT-00 – Engineering Setup
- DI-SPRINT-01 – Production Inspection and Evidence Foundation
- DI-SPRINT-02 – Production Image Quality and AI Detection

---

# Revision History

| Version | Date | Description |
|----------|------|-------------|
| 1.0.0 | 2026-06-27 | Initial Sprint 03 Production Review Comparison and Damage Cases |
