---
id: "DI-SPRINT-04"
title: "Damage Intelligence Sprint 04 Production CROMS and Maintenance Integration"
version: "1.0.0"
document_type: "Implementation Plan"
document_class: "Sprint Execution Plan"
status: "Draft"
classification: "Internal"
owner: "Riyadah Technology"
reviewers: "Chief Enterprise Architect, Product Owner, Damage Intelligence Lead, Backend Lead, Integration Lead, QA Lead, Security Lead, DevOps Lead, CROMS Lead, Maintenance Lead"
approvers: ""
created: "2026-06-27"
updated: "2026-06-27"
authoritative: true
ai_consumable: true
related: "DI-0011, DI-0012, DI-0013, DI-0014, DI-0015, DI-0017, DI-0018, DI-0019, DI-0020, DI-0031, DI-0032, DI-0033, DI-0034, DI-0035, DI-SPRINT-00, DI-SPRINT-01, DI-SPRINT-02, DI-SPRINT-03"
---

# Damage Intelligence Sprint 04 Production CROMS and Maintenance Integration

## Executive Summary

Sprint 04 delivers the production-ready integration layer between Damage Intelligence, existing GCU365 CROMS, and existing GCU365Maintenance.

This sprint connects the completed Damage Intelligence inspection, evidence, AI, comparison, review, and damage case capabilities to the existing operational systems that need to consume them.

Damage Intelligence remains an image analysis and damage detection application for existing GCU365 CROMS and GCU365Maintenance systems.

Damage Intelligence SHALL NOT replace CROMS, GCU365Maintenance, Fleet, Finance, rental lifecycle ownership, maintenance work order execution, actual repair cost ownership, or vehicle asset management.

Sprint 04 is not an MVP sprint. It is a production-ready integration sprint.

---

# Purpose

The purpose of Sprint 04 is to implement secure, reliable, auditable, and idempotent integrations with existing GCU365 CROMS and GCU365Maintenance.

Sprint 04 SHALL ensure that:

- CROMS can request check-out inspections.
- CROMS can request check-in inspections.
- CROMS can receive or query rental damage summaries.
- Damage Intelligence stores CROMS references without owning rental lifecycle.
- Damage Intelligence can route approved damage context to GCU365Maintenance.
- GCU365Maintenance can return maintenance request, work order, repair status, and actual cost references.
- Damage Intelligence stores Maintenance references without owning repair execution.
- Integration requests are authenticated and authorized.
- Integration retries are idempotent.
- Integration failures are observable.
- Integration actions are auditable.
- Evidence sharing remains secure and controlled.
- Ownership boundaries remain clear.

---

# Scope

## In Scope

Sprint 04 includes:

- CROMS check-out inspection request API.
- CROMS check-in inspection request API.
- CROMS rental damage summary API.
- CROMS callback or notification foundation where required.
- Maintenance handoff API.
- Maintenance work order reference callback API.
- Maintenance repair status callback API.
- Maintenance rejection reason callback API.
- Maintenance additional evidence request callback where required.
- Integration authentication.
- Integration authorization.
- Tenant validation.
- Idempotency handling.
- Retry handling.
- Dead-letter or failure tracking.
- Correlation ID propagation.
- Integration audit records.
- Integration monitoring.
- Integration test coverage.
- Integration smoke test.

## Out of Scope

Sprint 04 does not include:

- Rebuilding CROMS.
- Rebuilding GCU365Maintenance.
- Changing CROMS rental lifecycle ownership.
- Changing Maintenance work order ownership.
- Creating final customer charges.
- Closing rental agreements.
- Executing repair work orders.
- Assigning technicians.
- Owning actual repair cost.
- Finance posting.
- Accounting.
- Fleet Management.
- Vehicle asset lifecycle management.

---

# Sprint Goal

The Sprint 04 goal is:

```text
Implement production-ready CROMS and GCU365Maintenance integrations that exchange inspection, evidence, damage, report, and status context while preserving existing system ownership boundaries.
```

---

# Production-Ready Expectations

Sprint 04 output SHALL be production-grade integration work, not prototype work.

The following must be true:

- Integration APIs are authenticated.
- Integration APIs are authorized.
- Integration APIs enforce tenant isolation.
- Integration APIs support idempotency.
- Integration APIs support correlation IDs.
- Integration APIs return safe errors.
- Integration retries do not create duplicate inspections, cases, reports, or handoffs.
- Evidence links are controlled and time-limited where applicable.
- Integration failures are logged and monitored.
- Integration actions are audited.
- CROMS remains owner of rental lifecycle.
- GCU365Maintenance remains owner of work orders and repair execution.
- Damage Intelligence remains owner of evidence and damage analysis.

---

# Scope Boundary Reminder

Damage Intelligence owns:

- Inspection evidence.
- AI damage findings.
- Damage comparison results.
- Review decisions.
- Damage case context.
- Evidence packages.
- Damage reports.
- Integration references.
- Integration audit records.

CROMS owns:

- Rental agreement.
- Rental lifecycle.
- Check-out rental operation.
- Check-in rental operation.
- Rental closure.
- Final rental customer charge.
- Rental invoice reference where applicable.

GCU365Maintenance owns:

- Maintenance request.
- Work order.
- Repair execution.
- Technician workflow.
- Workshop workflow.
- Repair status.
- Actual repair cost.
- Maintenance completion.

Damage Intelligence SHALL NOT override these ownership boundaries.

---

# Sprint 04 Workstreams

| Workstream | Objective |
|-----------|-----------|
| CROMS Integration | Implement check-out, check-in, and damage summary integration |
| Maintenance Integration | Implement handoff, work order reference, and repair status integration |
| Backend API | Implement production integration APIs |
| Security | Secure service-to-service communication |
| Idempotency | Prevent duplicate integration side effects |
| Audit | Record integration actions and failures |
| Observability | Monitor integration health and failures |
| QA | Validate integration, security, idempotency, and ownership boundaries |
| DevOps | Configure integration endpoints, secrets, and environments |
| Documentation | Update integration notes and operational runbooks |

---

# Integration Principles

Sprint 04 SHALL follow these principles:

1. Existing systems remain systems of record.
2. Damage Intelligence exchanges references, evidence, reports, and status context.
3. Damage Intelligence does not duplicate CROMS or Maintenance ownership.
4. All integration requests must be tenant-scoped.
5. All write integration requests should be idempotent.
6. All integration failures must be traceable.
7. Evidence access must remain controlled.
8. Final business decisions remain outside AI and Damage Intelligence unless explicitly approved.
9. Integration APIs must support safe retry.
10. Integration logs must not expose secrets or raw evidence.

---

# CROMS Integration Scope

Damage Intelligence SHALL support CROMS workflows for rental inspection and damage context.

CROMS MAY request:

- Check-out inspection session.
- Check-in inspection session.
- Rental damage summary.
- Damage report reference.
- Evidence package reference.
- Inspection status.
- Damage case status.

Damage Intelligence MAY return:

- Inspection session ID.
- Inspection status.
- Check-out inspection reference.
- Check-in inspection reference.
- Damage findings summary.
- Comparison result summary.
- Review status.
- Damage case IDs.
- Evidence package reference.
- Report reference.

Damage Intelligence SHALL NOT return or decide:

- Final customer charge.
- Rental closure decision.
- Customer liability final decision.
- Invoice posting.
- Payment collection.
- Accounting entry.

---

# Maintenance Integration Scope

Damage Intelligence SHALL support Maintenance workflows for repair-relevant damage context.

Damage Intelligence MAY send to GCU365Maintenance:

- Damage case ID.
- Vehicle reference.
- Damage finding summary.
- Severity suggestion.
- Evidence package reference.
- Report reference.
- Advisory repair estimate reference where enabled.
- Review status.
- Additional notes.

GCU365Maintenance MAY return:

- Maintenance request ID.
- Work order ID.
- Repair status.
- Rejection reason.
- Additional evidence request.
- Actual repair cost reference.
- Repair completion confirmation.
- Post-repair inspection recommendation.

Damage Intelligence SHALL NOT own:

- Work order execution.
- Technician assignment.
- Parts usage.
- Labor tracking.
- Actual repair cost.
- Maintenance financial approval.
- Repair completion decision.

---

# Backend API Implementation

## Required CROMS APIs

Sprint 04 SHALL implement or finalize the following APIs:

```text
POST /api/v1/damage-intelligence/integrations/croms/check-out-inspections
POST /api/v1/damage-intelligence/integrations/croms/check-in-inspections
GET /api/v1/damage-intelligence/integrations/croms/rental-agreements/{rentalAgreementId}/damage-summary
GET /api/v1/damage-intelligence/integrations/croms/inspection-sessions/{inspectionSessionId}/status
POST /api/v1/damage-intelligence/integrations/croms/notifications/damage-summary-ready
```

The notification endpoint MAY be implemented as outbound callback, event, or webhook depending on approved architecture.

## Required Maintenance APIs

Sprint 04 SHALL implement or finalize the following APIs:

```text
POST /api/v1/damage-intelligence/integrations/maintenance/handoffs
POST /api/v1/damage-intelligence/integrations/maintenance/work-order-references
POST /api/v1/damage-intelligence/integrations/maintenance/repair-status-updates
POST /api/v1/damage-intelligence/integrations/maintenance/rejection-reasons
POST /api/v1/damage-intelligence/integrations/maintenance/additional-evidence-requests
GET /api/v1/damage-intelligence/integrations/maintenance/damage-cases/{damageCaseId}/handoff-status
```

## API Rules

All integration APIs SHALL:

- Require service authentication.
- Enforce tenant validation.
- Validate source system.
- Validate object references.
- Support correlation ID.
- Support safe error responses.
- Support audit records.
- Prevent cross-tenant references.
- Avoid exposing unrestricted evidence URLs.
- Preserve existing system ownership boundaries.

Write APIs SHOULD support idempotency keys.

---

# CROMS Check-Out Inspection Request

## Endpoint

```http
POST /api/v1/damage-intelligence/integrations/croms/check-out-inspections
```

## Required Headers

```http
Authorization: Bearer SERVICE_TOKEN
X-Tenant-Id: TENANT-000001
X-Correlation-Id: CORR-000001
X-Idempotency-Key: CROMS-RA-000001-CHECKOUT
```

## Required Behavior

The API SHALL:

- Authenticate CROMS service identity.
- Validate tenant context.
- Validate rental agreement reference.
- Validate vehicle reference.
- Validate branch reference where provided.
- Create or return check-out inspection session.
- Store CROMS references only.
- Return inspection session ID and status.
- Create audit record.
- Preserve CROMS ownership of rental lifecycle.

## Example Request

```json
{
  "rentalAgreementId": "RA-000001",
  "vehicleId": "VEH-000001",
  "branchId": "BR-000001",
  "customerReference": {
    "customerId": "CUS-000001"
  },
  "requestedBySystem": "GCU365-CROMS"
}
```

## Example Response

```json
{
  "success": true,
  "correlationId": "CORR-000001",
  "data": {
    "inspectionSessionId": "DI-INS-000001",
    "inspectionType": "CHECK_OUT",
    "status": "DRAFT"
  },
  "errors": []
}
```

---

# CROMS Check-In Inspection Request

## Endpoint

```http
POST /api/v1/damage-intelligence/integrations/croms/check-in-inspections
```

## Required Behavior

The API SHALL:

- Authenticate CROMS service identity.
- Validate tenant context.
- Validate rental agreement reference.
- Validate vehicle reference.
- Validate baseline inspection reference where provided.
- Create or return check-in inspection session.
- Link baseline check-out inspection where valid.
- Store CROMS references only.
- Return inspection session ID and status.
- Create audit record.
- Preserve CROMS ownership of rental closure.

## Example Request

```json
{
  "rentalAgreementId": "RA-000001",
  "vehicleId": "VEH-000001",
  "branchId": "BR-000001",
  "baselineInspectionSessionId": "DI-INS-000001",
  "requestedBySystem": "GCU365-CROMS"
}
```

## Example Response

```json
{
  "success": true,
  "correlationId": "CORR-000002",
  "data": {
    "inspectionSessionId": "DI-INS-000002",
    "inspectionType": "CHECK_IN",
    "status": "DRAFT",
    "baselineInspectionSessionId": "DI-INS-000001"
  },
  "errors": []
}
```

---

# CROMS Rental Damage Summary

## Endpoint

```http
GET /api/v1/damage-intelligence/integrations/croms/rental-agreements/{rentalAgreementId}/damage-summary
```

## Required Behavior

The API SHALL:

- Authenticate CROMS service identity.
- Validate tenant context.
- Validate rental agreement reference.
- Retrieve linked check-out and check-in inspections.
- Retrieve damage finding summaries.
- Retrieve comparison status.
- Retrieve damage case status.
- Return report reference where available.
- Return evidence package reference where available.
- Avoid final charge or liability decision.
- Create audit or access record where required.

## Example Response

```json
{
  "success": true,
  "correlationId": "CORR-000003",
  "data": {
    "rentalAgreementId": "RA-000001",
    "vehicleId": "VEH-000001",
    "checkOutInspectionSessionId": "DI-INS-000001",
    "checkInInspectionSessionId": "DI-INS-000002",
    "damageSummaryStatus": "REVIEW_REQUIRED",
    "damageCaseIds": [
      "DI-CASE-000001"
    ],
    "comparisonStatus": "COMPLETED",
    "reportReference": {
      "reportId": "DI-RPT-000001"
    },
    "finalCustomerChargeDecision": "NOT_OWNED_BY_DAMAGE_INTELLIGENCE"
  },
  "errors": []
}
```

---

# Maintenance Handoff

## Endpoint

```http
POST /api/v1/damage-intelligence/integrations/maintenance/handoffs
```

## Required Headers

```http
Authorization: Bearer SERVICE_TOKEN
X-Tenant-Id: TENANT-000001
X-Correlation-Id: CORR-000004
X-Idempotency-Key: DI-CASE-000001-MAINTENANCE-HANDOFF
```

## Required Behavior

The API SHALL:

- Authenticate integration service identity.
- Validate tenant context.
- Validate damage case exists.
- Validate damage case is eligible for Maintenance handoff.
- Validate evidence package reference.
- Send or record handoff to GCU365Maintenance.
- Store handoff status.
- Return handoff ID and status.
- Create audit record.
- Preserve Maintenance ownership of work order execution.

## Example Request

```json
{
  "damageCaseId": "DI-CASE-000001",
  "vehicleId": "VEH-000001",
  "severityCode": "MODERATE",
  "evidencePackageReference": {
    "evidencePackageId": "DI-EPK-000001"
  },
  "advisoryEstimateReference": {
    "estimateId": "DI-EST-000001"
  },
  "requestedBySystem": "DamageIntelligence"
}
```

## Example Response

```json
{
  "success": true,
  "correlationId": "CORR-000004",
  "data": {
    "maintenanceHandoffId": "DI-MHO-000001",
    "status": "SENT",
    "damageCaseId": "DI-CASE-000001"
  },
  "errors": []
}
```

---

# Maintenance Work Order Reference Callback

## Endpoint

```http
POST /api/v1/damage-intelligence/integrations/maintenance/work-order-references
```

## Required Behavior

The API SHALL:

- Authenticate GCU365Maintenance service identity.
- Validate tenant context.
- Validate damage case reference.
- Validate maintenance request reference.
- Validate work order reference.
- Store Maintenance reference.
- Link work order reference to damage case.
- Create audit record.
- Preserve Maintenance ownership of work order execution.

## Example Request

```json
{
  "damageCaseId": "DI-CASE-000001",
  "maintenanceRequestId": "MNT-REQ-000001",
  "workOrderId": "WO-000001",
  "status": "WORK_ORDER_CREATED",
  "updatedAt": "2026-06-27T12:00:00Z"
}
```

## Example Response

```json
{
  "success": true,
  "correlationId": "CORR-000005",
  "data": {
    "damageCaseId": "DI-CASE-000001",
    "maintenanceRequestId": "MNT-REQ-000001",
    "workOrderId": "WO-000001",
    "linked": true
  },
  "errors": []
}
```

---

# Maintenance Repair Status Update

## Endpoint

```http
POST /api/v1/damage-intelligence/integrations/maintenance/repair-status-updates
```

## Required Behavior

The API SHALL:

- Authenticate GCU365Maintenance service identity.
- Validate tenant context.
- Validate damage case reference.
- Validate work order reference.
- Store repair status as external Maintenance context.
- Store actual repair cost reference where provided.
- Avoid owning actual repair cost.
- Recommend post-repair inspection where configured.
- Create audit record.

## Example Request

```json
{
  "damageCaseId": "DI-CASE-000001",
  "workOrderId": "WO-000001",
  "repairStatus": "REPAIR_COMPLETED",
  "actualRepairCostReference": {
    "sourceSystem": "GCU365Maintenance",
    "referenceId": "MNT-COST-000001"
  },
  "updatedAt": "2026-06-27T15:00:00Z"
}
```

## Example Response

```json
{
  "success": true,
  "correlationId": "CORR-000006",
  "data": {
    "damageCaseId": "DI-CASE-000001",
    "repairStatus": "REPAIR_COMPLETED",
    "actualRepairCostOwnedBy": "GCU365Maintenance",
    "postRepairInspectionRecommended": true
  },
  "errors": []
}
```

---

# Maintenance Rejection Reason

## Endpoint

```http
POST /api/v1/damage-intelligence/integrations/maintenance/rejection-reasons
```

## Required Behavior

The API SHALL:

- Authenticate GCU365Maintenance service identity.
- Validate tenant context.
- Validate damage case reference.
- Store rejection reason.
- Update handoff or case integration status.
- Preserve damage case history.
- Create audit record.

## Example Request

```json
{
  "damageCaseId": "DI-CASE-000001",
  "maintenanceRequestId": "MNT-REQ-000001",
  "rejectionCode": "INSUFFICIENT_EVIDENCE",
  "rejectionReason": "Additional close-up image required before work order creation.",
  "requestedAdditionalEvidence": true
}
```

---

# Additional Evidence Request from Maintenance

## Endpoint

```http
POST /api/v1/damage-intelligence/integrations/maintenance/additional-evidence-requests
```

## Required Behavior

The API SHALL:

- Authenticate GCU365Maintenance service identity.
- Validate tenant context.
- Validate damage case reference.
- Create additional evidence request.
- Link request to damage case.
- Notify or expose request to authorized Damage Intelligence users.
- Create audit record.

---

# Integration Statuses

Sprint 04 SHOULD support the following integration statuses:

| Status | Meaning |
|-------|---------|
| NOT_STARTED | Integration has not started |
| PENDING | Integration request is pending |
| SENT | Integration request was sent |
| RECEIVED | Integration callback was received |
| COMPLETED | Integration completed successfully |
| FAILED | Integration failed |
| RETRY_PENDING | Retry is pending |
| DEAD_LETTERED | Integration moved to failure queue |
| REJECTED | Target system rejected request |
| CANCELLED | Integration was cancelled |

---

# Idempotency Implementation

Sprint 04 SHALL implement idempotency for integration write operations.

## Required Behavior

When `X-Idempotency-Key` is provided:

- Same tenant, same key, and same payload SHALL return the same result.
- Same tenant, same key, and different payload SHALL return `IDEMPOTENCY_CONFLICT`.
- Idempotency records SHALL be tenant-scoped.
- Idempotency records SHALL include correlation ID.
- Idempotency records SHALL expire according to configured retention rules.
- Idempotency events SHOULD be auditable.

## Required Idempotent Operations

Idempotency SHOULD apply to:

- CROMS check-out inspection request.
- CROMS check-in inspection request.
- Maintenance handoff.
- Work order reference callback.
- Repair status callback.
- Maintenance rejection callback.
- Additional evidence request callback.

---

# Retry and Failure Handling

Sprint 04 SHALL support safe integration failure handling.

## Required Behavior

The system SHALL:

- Record failed integration attempts.
- Preserve correlation ID.
- Preserve request reference.
- Preserve safe failure reason.
- Support retry where configured.
- Prevent duplicate side effects during retry.
- Alert operations where failure threshold is reached.
- Move unrecoverable failures to dead-letter state where configured.
- Avoid exposing secrets or sensitive payloads in logs.

---

# Database Implementation

Sprint 04 SHALL implement migrations for integration records.

## Required Tables

Recommended tables:

```text
di_integration_requests
di_integration_attempts
di_integration_callbacks
di_integration_idempotency_records
di_croms_inspection_links
di_croms_damage_summary_access
di_maintenance_handoffs
di_maintenance_references
di_maintenance_status_updates
di_integration_dead_letters
```

## Required Columns

Integration tables SHOULD include:

```text
id
tenant_id
source_system
target_system
operation_code
external_reference_id
damage_case_id
inspection_session_id
status
idempotency_key
correlation_id
request_hash
attempt_count
last_attempt_at
created_at
created_by
updated_at
updated_by
safe_failure_code
safe_failure_message
```

## Database Rules

- Tenant ID SHALL be indexed.
- Idempotency key SHALL be unique within tenant and operation scope.
- External references SHALL be indexed.
- Integration attempts SHALL preserve history.
- Failure records SHALL avoid secrets and raw evidence.
- Audit records SHALL be append-only where practical.

---

# Security Implementation

Sprint 04 SHALL enforce integration security controls.

## Required Controls

Security implementation SHALL include:

- Service-to-service authentication.
- Service-to-service authorization.
- Tenant validation.
- Source system validation.
- Payload validation.
- Replay protection where required.
- Idempotency validation.
- Rate limiting where required.
- Secrets protection.
- Signature or token validation where approved.
- Safe error responses.
- Security event logging.
- No secrets in logs.
- No raw evidence in logs.
- No unrestricted evidence URLs in integration payloads.

---

# Audit Implementation

Sprint 04 SHALL create audit records for integration actions.

## Required Audit Events

| Event | Trigger |
|------|---------|
| CROMS_CHECKOUT_INSPECTION_REQUESTED | CROMS requests check-out inspection |
| CROMS_CHECKIN_INSPECTION_REQUESTED | CROMS requests check-in inspection |
| CROMS_DAMAGE_SUMMARY_ACCESSED | CROMS accesses rental damage summary |
| MAINTENANCE_HANDOFF_REQUESTED | Damage case routed to Maintenance |
| MAINTENANCE_WORK_ORDER_REFERENCE_RECEIVED | Work order reference received |
| MAINTENANCE_REPAIR_STATUS_RECEIVED | Repair status received |
| MAINTENANCE_REJECTION_RECEIVED | Maintenance rejection received |
| MAINTENANCE_ADDITIONAL_EVIDENCE_REQUESTED | Maintenance requests more evidence |
| INTEGRATION_RETRY_SCHEDULED | Integration retry scheduled |
| INTEGRATION_FAILED | Integration failed |
| INTEGRATION_DEAD_LETTERED | Integration moved to dead-letter state |
| IDEMPOTENCY_CONFLICT_DETECTED | Idempotency conflict detected |

Audit records SHALL avoid raw images, secrets, tokens, unrestricted URLs, and unnecessary personal data.

---

# Observability Implementation

Sprint 04 SHALL provide integration operational visibility.

## Required Metrics

Recommended metrics:

| Metric | Purpose |
|-------|---------|
| croms_checkout_request_count | CROMS check-out inspection requests |
| croms_checkin_request_count | CROMS check-in inspection requests |
| croms_damage_summary_request_count | CROMS damage summary requests |
| maintenance_handoff_count | Maintenance handoffs |
| maintenance_callback_count | Maintenance callbacks received |
| integration_failure_count | Failed integration requests |
| integration_retry_count | Retry attempts |
| integration_dead_letter_count | Dead-lettered integrations |
| idempotency_conflict_count | Idempotency conflicts |
| integration_latency_ms | Integration latency |

## Required Logs

Logs SHALL include:

- Correlation ID.
- Tenant ID where safe.
- Operation code.
- Source system.
- Target system.
- Safe status.
- Safe failure code.
- No secrets.
- No raw images.
- No unrestricted evidence URLs.

---

# QA Implementation

QA SHALL validate Sprint 04 against DI-0035.

## Required QA Coverage

Sprint 04 QA SHALL include:

- CROMS check-out integration test.
- CROMS check-in integration test.
- CROMS damage summary test.
- CROMS idempotency test.
- CROMS idempotency conflict test.
- Maintenance handoff test.
- Maintenance work order reference callback test.
- Maintenance repair status callback test.
- Maintenance rejection test.
- Maintenance additional evidence request test.
- Integration authentication test.
- Integration authorization test.
- Tenant mismatch test.
- Duplicate request test.
- Retry behavior test.
- Safe error test.
- Audit test.
- Monitoring test.
- Smoke test.

---

# Sprint 04 Test Cases

Sprint 04 SHALL execute or prepare the following DI-0035 tests:

```text
TC-DI-0801
TC-DI-0802
TC-DI-0803
TC-DI-0804
TC-DI-0805
TC-DI-0901
TC-DI-0902
TC-DI-0903
TC-DI-0904
TC-DI-1101
TC-DI-1102
TC-DI-1103
TC-DI-1104
TC-DI-1201
TC-DI-1202
TC-DI-1203
TC-DI-1403
TC-DI-1701
```

---

# Production Data Protection Rules

Sprint 04 SHALL follow these data protection rules:

- Integration payloads SHALL include only required data.
- Customer data SHALL be minimized.
- Evidence access SHALL use controlled references.
- Public unrestricted evidence URLs SHALL NOT be sent.
- Secrets SHALL NOT be logged.
- Raw images SHALL NOT be logged.
- Tenant context SHALL be validated for every integration.
- Cross-tenant references SHALL be rejected.
- Maintenance and CROMS references SHALL be stored as references only.

---

# Acceptance Criteria

## AC-DI-S04-001 — CROMS Check-Out Integration Works

Given CROMS sends an authorized check-out inspection request, then Damage Intelligence SHALL create or return a check-out inspection session.

## AC-DI-S04-002 — CROMS Check-In Integration Works

Given CROMS sends an authorized check-in inspection request, then Damage Intelligence SHALL create or return a check-in inspection session and link valid baseline inspection where provided.

## AC-DI-S04-003 — CROMS Damage Summary Works

Given CROMS requests a rental damage summary, then Damage Intelligence SHALL return inspection, damage, comparison, case, report, and evidence context without deciding final customer charge.

## AC-DI-S04-004 — Maintenance Handoff Works

Given an eligible damage case is routed to Maintenance, then Damage Intelligence SHALL send or record a Maintenance handoff with evidence context and preserve Maintenance ownership of work order execution.

## AC-DI-S04-005 — Work Order Reference Is Stored

Given GCU365Maintenance returns a work order reference, then Damage Intelligence SHALL store it as external Maintenance reference without owning the work order.

## AC-DI-S04-006 — Repair Status Is Stored

Given GCU365Maintenance returns repair status, then Damage Intelligence SHALL store it as Maintenance context without owning repair execution or actual repair cost.

## AC-DI-S04-007 — Idempotency Prevents Duplicates

Given duplicate integration requests are received with the same idempotency key and same payload, then Damage Intelligence SHOULD return the original result without duplicate business objects.

## AC-DI-S04-008 — Idempotency Conflict Is Detected

Given the same idempotency key is reused with a different payload, then Damage Intelligence SHALL return `IDEMPOTENCY_CONFLICT`.

## AC-DI-S04-009 — Integration Security Is Enforced

Given an unauthorized or invalid integration request is received, then Damage Intelligence SHALL reject it safely and log or audit the attempt.

## AC-DI-S04-010 — Integration Audit Records Are Created

Given integration actions occur, then audit records SHALL be created for critical actions.

## AC-DI-S04-011 — Ownership Boundaries Are Preserved

Given integration workflows execute, then Damage Intelligence SHALL NOT own rental closure, final customer charge, work order execution, technician assignment, actual repair cost, Finance posting, Fleet, or vehicle asset lifecycle.

## AC-DI-S04-012 — Sprint 04 Smoke Test Passes

Given Sprint 04 is complete, then the Sprint 04 smoke test SHALL pass.

---

# Sprint 04 Smoke Test

The Sprint 04 smoke test SHALL include:

1. Start backend API.
2. Verify health endpoint.
3. Authenticate CROMS integration service.
4. Send CROMS check-out inspection request.
5. Confirm inspection session is created.
6. Send duplicate CROMS check-out request with same idempotency key.
7. Confirm no duplicate inspection is created.
8. Send CROMS check-in inspection request.
9. Confirm baseline reference is linked where provided.
10. Complete inspection, AI, comparison, and case test data where needed.
11. Request CROMS rental damage summary.
12. Confirm no final customer charge is returned.
13. Route eligible damage case to Maintenance.
14. Receive work order reference from Maintenance.
15. Receive repair status update from Maintenance.
16. Confirm actual repair cost is stored only as reference.
17. Verify integration audit records.
18. Simulate unauthorized integration request.
19. Confirm safe rejection.
20. Confirm no unrestricted evidence URL is exposed.
21. Confirm no secrets or raw images appear in logs.

Expected result:

```text
Sprint 04 production CROMS and Maintenance integration smoke test passed.
```

---

# Definition of Done

Sprint 04 is done when:

- CROMS check-out integration API is implemented.
- CROMS check-in integration API is implemented.
- CROMS damage summary API is implemented.
- Maintenance handoff API is implemented.
- Maintenance work order reference callback is implemented.
- Maintenance repair status callback is implemented.
- Maintenance rejection or additional evidence callback is implemented where required.
- Integration authentication is implemented.
- Integration authorization is implemented.
- Tenant validation is enforced.
- Idempotency is implemented.
- Retry and failure handling is implemented.
- Integration audit records are created.
- Integration monitoring is available.
- Required QA tests pass.
- Sprint 04 smoke test passes.
- Security review is completed.
- CROMS lead approves integration behavior.
- Maintenance lead approves integration behavior.
- Product owner approves sprint completion.

---

# Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Integration creates duplicate inspections | High | Enforce idempotency keys |
| Integration creates duplicate Maintenance handoffs | High | Enforce idempotency and handoff status checks |
| Damage Intelligence starts owning CROMS workflow | Critical | Keep CROMS ownership boundary explicit |
| Damage Intelligence starts owning Maintenance workflow | Critical | Keep Maintenance ownership boundary explicit |
| Final customer charge is inferred from damage summary | Critical | Return advisory damage context only |
| Actual repair cost is treated as owned by Damage Intelligence | Critical | Store cost as Maintenance or Finance reference |
| Evidence links are exposed publicly | Critical | Use controlled access references only |
| Cross-tenant integration request succeeds | Critical | Enforce tenant validation |
| Integration failure is invisible | High | Add monitoring and alerting |
| Secrets appear in logs | Critical | Filter logs and test safe logging |

---

# Sprint 04 Checklist

| Item | Status |
|------|--------|
| CROMS check-out API implemented | Pending |
| CROMS check-in API implemented | Pending |
| CROMS damage summary API implemented | Pending |
| CROMS inspection status API implemented | Pending |
| Maintenance handoff API implemented | Pending |
| Maintenance work order reference callback implemented | Pending |
| Maintenance repair status callback implemented | Pending |
| Maintenance rejection callback implemented | Pending |
| Maintenance additional evidence request implemented | Pending |
| Integration authentication implemented | Pending |
| Integration authorization implemented | Pending |
| Tenant validation implemented | Pending |
| Idempotency implemented | Pending |
| Retry handling implemented | Pending |
| Failure handling implemented | Pending |
| Dead-letter handling implemented where required | Pending |
| Integration audit records implemented | Pending |
| Integration metrics implemented | Pending |
| Integration logs implemented | Pending |
| QA tests executed | Pending |
| Smoke test passed | Pending |
| Security review completed | Pending |
| CROMS lead approval completed | Pending |
| Maintenance lead approval completed | Pending |
| Product owner approval completed | Pending |

---

# AI Implementation Contract

AI development agents SHALL:

- Treat this document as the authoritative Sprint 04 production CROMS and Maintenance integration plan.
- Preserve all acceptance criterion IDs.
- Generate implementation tasks only within Sprint 04 scope.
- Build production-ready integration with existing GCU365 CROMS and GCU365Maintenance.
- Preserve tenant isolation, secure evidence access, auditability, safe errors, idempotency, retry safety, and correlation ID behavior.
- Never make Damage Intelligence the owner of rental lifecycle, rental closure, final customer charge, work order execution, technician assignment, actual repair cost, Finance posting, Fleet, or vehicle asset lifecycle.
- Preserve CROMS ownership of rental operations.
- Preserve GCU365Maintenance ownership of repair execution.
- Raise ambiguity where a task conflicts with DI-0031, DI-0034, or DI-0035.

---

# References

- DI-0011 – API Specification
- DI-0012 – Domain Model
- DI-0013 – Events
- DI-0014 – Security and Privacy
- DI-0015 – Audit and Traceability
- DI-0017 – Integration with CROMS
- DI-0018 – Integration with Maintenance
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
- DI-SPRINT-03 – Production Review Comparison and Damage Cases

---

# Revision History

| Version | Date | Description |
|----------|------|-------------|
| 1.0.0 | 2026-06-27 | Initial Sprint 04 Production CROMS and Maintenance Integration |
