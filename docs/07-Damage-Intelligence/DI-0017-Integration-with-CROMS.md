---
id: "DI-0017"
title: "Damage Intelligence Integration with CROMS"
version: "1.0.0"
document_type: "Product Specification"
document_class: "Integration Specification"
status: "Draft"
classification: "Internal"
owner: "Riyadah Technology"
reviewers: "Chief Enterprise Architect, Product Owner, CROMS Lead, Damage Intelligence Lead, API Architecture Lead, Security Lead, Operations Lead, QA Lead"
approvers: ""
created: "2026-06-27"
updated: "2026-06-27"
authoritative: true
ai_consumable: true
related: "DI-0001, DI-0002, DI-0004, DI-0005, DI-0006, DI-0007, DI-0008, DI-0009, DI-0010, DI-0011, DI-0012, DI-0013, DI-0014, DI-0015, DI-0016, RA-0001, RA-0002, GEES-0007, GEES-0009, PLATFORM-0005"
---
---

id: "DI-0017"
title: "Damage Intelligence Integration with CROMS"
version: "1.0.0"
document_type: "Product Specification"
document_class: "Integration Specification"
status: "Draft"
classification: "Internal"
owner: "Riyadah Technology"
reviewers: "Chief Enterprise Architect, Product Owner, CROMS Lead, Damage Intelligence Lead, API Architecture Lead, Security Lead, Operations Lead, QA Lead"
approvers: ""
created: "2026-06-27"
updated: "2026-06-27"
authoritative: true
ai_consumable: true
related: "DI-0001, DI-0002, DI-0004, DI-0005, DI-0006, DI-0007, DI-0008, DI-0009, DI-0010, DI-0011, DI-0012, DI-0013, DI-0014, DI-0015, DI-0016, RA-0001, RA-0002, GEES-0007, GEES-0009, PLATFORM-0005"
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Damage Intelligence Integration with CROMS

## Executive Summary

This document defines the integration between Damage Intelligence and GCU365 CROMS.

CROMS is the primary rental operations system. Damage Intelligence provides vehicle condition inspection, image evidence capture, AI-assisted damage detection, historical comparison, damage case handling, review status, reporting, and maintenance-routing context.

The integration SHALL support:

* Rental check-out inspection.
* Rental check-in inspection.
* Vehicle condition baseline creation.
* Return damage comparison.
* Damage case creation.
* Damage review status sharing.
* Rental damage summary.
* Vehicle availability decision support.
* Customer dispute evidence.
* Maintenance routing visibility.

Damage Intelligence SHALL not own the rental agreement lifecycle. CROMS SHALL remain the system of record for rental agreements, vehicle rental lifecycle, customer rental context, and rental closure workflow.

---

# Purpose

The purpose of this document is to define how CROMS and Damage Intelligence interact.

This specification SHALL guide:

* CROMS workflow integration.
* Damage Intelligence workflow integration.
* API contracts.
* Event contracts.
* Data ownership.
* State synchronization.
* Error handling.
* Security controls.
* Audit and traceability.
* Test case generation.
* Implementation planning.

---

# Scope

## In Scope

This specification covers:

* CROMS-to-Damage Intelligence integration principles.
* Data ownership boundaries.
* Check-out inspection initiation.
* Check-in inspection initiation.
* Rental damage summary exchange.
* Vehicle condition evidence sharing.
* Damage case status sharing.
* Damage comparison result sharing.
* Maintenance routing status sharing.
* API and event integration.
* Failure handling.
* Security and tenant isolation.
* Audit and traceability.
* Acceptance criteria.

## Out of Scope

This specification does not define:

* Full CROMS rental agreement design.
* Full CROMS billing workflow.
* Full customer payment workflow.
* Full insurance claim workflow.
* Full Maintenance integration.
* Full OpenAPI YAML.
* Final database schema.
* Final UI screen design.
* Final notification templates.

---

# Integration Principles

The integration between CROMS and Damage Intelligence SHALL follow these principles:

1. Clear Ownership
2. API-First Integration
3. Event-Driven Where Appropriate
4. Tenant Isolation
5. Secure Evidence Access
6. Idempotent Requests
7. Auditable State Changes
8. Human Review Before Customer-Impacting Decisions
9. Evidence Preservation
10. No Duplicate System of Record

---

# System Ownership

## CROMS Owns

CROMS SHALL own:

* Rental Agreement.
* Rental lifecycle.
* Customer rental context.
* Vehicle assignment to rental.
* Check-out workflow orchestration.
* Check-in workflow orchestration.
* Rental closure decision.
* Rental billing decision.
* Vehicle availability decision according to rental policy.
* Customer-facing rental documents.

## Damage Intelligence Owns

Damage Intelligence SHALL own:

* Inspection Session.
* Inspection Images.
* Image Quality Results.
* AI Damage Findings.
* Damage Findings.
* Damage Comparison Results.
* Damage Cases.
* Human Review Decisions related to damage.
* Advisory Repair Estimates.
* Damage Reports.
* Damage evidence audit trail.

## Shared Context

The following are shared by reference:

* Vehicle ID.
* Rental Agreement ID.
* Customer Reference ID.
* Branch ID.
* User ID.
* Inspection Session ID.
* Damage Case ID.
* Report ID.

Shared context SHALL use stable identifiers.

---

# Integration Context Map

```text
CROMS
  |
  | Creates rental agreement
  | Assigns vehicle
  | Requests inspection
  v
Damage Intelligence
  |
  | Captures evidence
  | Runs AI detection
  | Compares check-in vs check-out
  | Creates damage case
  | Sends damage summary
  v
CROMS
  |
  | Uses summary in rental workflow
  | Shows evidence/report references
  | Applies rental policy
  | Coordinates billing/closure outside Damage Intelligence
```

---

# Primary Integration Workflows

Damage Intelligence and CROMS SHALL support the following primary workflows.

| Workflow                     | Description                                                |
| ---------------------------- | ---------------------------------------------------------- |
| Check-Out Inspection         | CROMS requests baseline inspection before rental handover  |
| Check-In Inspection          | CROMS requests return inspection when vehicle is returned  |
| Rental Damage Summary        | Damage Intelligence provides damage status to CROMS        |
| Damage Case Review Status    | Damage Intelligence updates CROMS about review status      |
| Vehicle Availability Support | Damage Intelligence provides damage/maintenance indicators |
| Customer Dispute Evidence    | CROMS can request controlled damage evidence reports       |

---

# Check-Out Inspection Integration

## Purpose

The Check-Out Inspection creates the baseline vehicle condition record before rental start.

## Trigger

CROMS SHOULD trigger Check-Out Inspection when:

* Rental Agreement is created or prepared.
* Vehicle is assigned to rental.
* Customer is ready for handover.
* Branch agent starts check-out workflow.

## CROMS Request Data

CROMS SHALL provide:

| Field              | Required    | Description                        |
| ------------------ | ----------- | ---------------------------------- |
| tenantId           | Yes         | Tenant identifier                  |
| rentalAgreementId  | Yes         | Rental agreement reference         |
| vehicleId          | Yes         | Vehicle reference                  |
| customerId         | Recommended | Customer reference                 |
| branchId           | Yes         | Branch/location                    |
| requestedBy        | Yes         | User or service initiating request |
| inspectionType     | Yes         | CheckOut                           |
| expectedHandoverAt | Optional    | Expected handover time             |
| captureTemplateId  | Optional    | Preferred capture template         |

## Damage Intelligence Response

Damage Intelligence SHALL return:

| Field                    | Description                        |
| ------------------------ | ---------------------------------- |
| inspectionSessionId      | Created inspection session         |
| status                   | Initial inspection status          |
| requiredCapturePositions | Required image checklist           |
| captureTemplateId        | Applied capture template           |
| expiresAt                | Optional session expiry            |
| links                    | API/UI references where applicable |

## Expected Outcome

CROMS receives an inspection session reference and can show the inspection status inside the rental workflow.

---

# Check-Out Flow

```text
CROMS Rental Agreement Ready
        ↓
CROMS Requests Check-Out Inspection
        ↓
Damage Intelligence Creates Inspection Session
        ↓
Rental Agent Captures Baseline Evidence
        ↓
Inspection Submitted
        ↓
Damage Intelligence Stores Evidence
        ↓
AI Analysis Optional
        ↓
Baseline Completed
        ↓
CROMS Receives Completion Status
        ↓
CROMS Continues Rental Handover
```

---

# Check-Out Completion Rules

Before CROMS allows final handover, policy MAY require:

* Inspection session completed.
* Required images captured.
* Image quality passed or override recorded.
* Baseline evidence stored.
* Critical visible damage reviewed if detected.
* Inspection completion status received.

CROMS SHALL determine whether rental handover can proceed according to approved rental policy.

Damage Intelligence SHALL provide evidence and status only.

---

# Check-In Inspection Integration

## Purpose

The Check-In Inspection captures vehicle return condition and compares it against baseline or historical evidence.

## Trigger

CROMS SHOULD trigger Check-In Inspection when:

* Customer returns vehicle.
* Branch agent starts return workflow.
* Rental Agreement is ready for closure.
* Vehicle return event is recorded.

## CROMS Request Data

CROMS SHALL provide:

| Field                       | Required    | Description                        |
| --------------------------- | ----------- | ---------------------------------- |
| tenantId                    | Yes         | Tenant identifier                  |
| rentalAgreementId           | Yes         | Rental agreement reference         |
| vehicleId                   | Yes         | Vehicle reference                  |
| customerId                  | Recommended | Customer reference                 |
| branchId                    | Yes         | Return branch                      |
| requestedBy                 | Yes         | User or service initiating request |
| inspectionType              | Yes         | CheckIn                            |
| actualReturnAt              | Recommended | Actual return timestamp            |
| baselineInspectionSessionId | Optional    | Known check-out inspection session |

## Damage Intelligence Response

Damage Intelligence SHALL return:

| Field                       | Description                   |
| --------------------------- | ----------------------------- |
| inspectionSessionId         | Return inspection session     |
| status                      | Initial status                |
| baselineInspectionSessionId | Selected or expected baseline |
| requiredCapturePositions    | Required image checklist      |
| comparisonStatus            | Damage comparison status      |

---

# Check-In Flow

```text
CROMS Return Workflow Started
        ↓
CROMS Requests Check-In Inspection
        ↓
Damage Intelligence Creates Return Inspection
        ↓
Rental Agent Captures Return Evidence
        ↓
Inspection Submitted
        ↓
AI Damage Detection Runs
        ↓
Damage Comparison Runs
        ↓
New / Existing / Changed / Uncertain Damage Classified
        ↓
Human Review Where Required
        ↓
Damage Case Created Where Required
        ↓
CROMS Receives Rental Damage Summary
        ↓
CROMS Continues Rental Closure Policy
```

---

# Damage Comparison Integration

For check-in workflows, Damage Intelligence SHALL compare return evidence against:

1. Check-out inspection for the same rental agreement.
2. Most recent approved inspection before rental start.
3. Approved vehicle damage history.
4. No baseline, where no valid evidence exists.

Damage Intelligence SHALL inform CROMS when:

* Comparison completed.
* Comparison failed.
* Baseline was unavailable.
* New damage candidate exists.
* Review is required.
* Damage case is created.
* Damage is confirmed or rejected.

Damage Intelligence SHALL NOT classify damage as confirmed new solely because baseline evidence is missing.

---

# Rental Damage Summary

Damage Intelligence SHALL provide CROMS with a rental damage summary.

## Summary Fields

The Rental Damage Summary SHOULD include:

| Field                       | Description                               |
| --------------------------- | ----------------------------------------- |
| rentalAgreementId           | Rental agreement reference                |
| vehicleId                   | Vehicle reference                         |
| checkOutInspectionSessionId | Baseline inspection                       |
| checkInInspectionSessionId  | Return inspection                         |
| inspectionStatus            | Inspection workflow status                |
| comparisonStatus            | Comparison workflow status                |
| damageCasesCount            | Total related damage cases                |
| newDamageCount              | Candidate or confirmed new damage         |
| preExistingDamageCount      | Pre-existing damage                       |
| changedDamageCount          | Changed/worsened damage                   |
| uncertainDamageCount        | Uncertain damage                          |
| pendingReviewCount          | Items pending human review                |
| confirmedDamageCount        | Confirmed findings                        |
| rejectedDamageCount         | Rejected findings                         |
| highestSeverity             | Highest severity identified               |
| maintenanceRequired         | Whether Maintenance routing is required   |
| reportId                    | Evidence report reference where available |
| updatedAt                   | Last update timestamp                     |

---

# Rental Damage Summary Example

```json
{
  "rentalAgreementId": "RA-000001",
  "vehicleId": "VEH-000001",
  "checkOutInspectionSessionId": "INS-DI-000010",
  "checkInInspectionSessionId": "INS-DI-000025",
  "inspectionStatus": "Completed",
  "comparisonStatus": "Completed",
  "damageCasesCount": 1,
  "newDamageCount": 1,
  "preExistingDamageCount": 0,
  "changedDamageCount": 0,
  "uncertainDamageCount": 0,
  "pendingReviewCount": 0,
  "confirmedDamageCount": 1,
  "rejectedDamageCount": 0,
  "highestSeverity": "MODERATE",
  "maintenanceRequired": true,
  "reportId": "RPT-DI-000001",
  "updatedAt": "2026-06-27T00:00:00Z"
}
```

---

# CROMS UI Integration Requirements

CROMS SHOULD display Damage Intelligence status in rental workflows.

## Check-Out Screen

CROMS SHOULD show:

* Inspection required status.
* Inspection session link.
* Capture completion status.
* Required image completion.
* Image quality warnings.
* Baseline completed indicator.
* Damage findings where policy allows.

## Check-In Screen

CROMS SHOULD show:

* Return inspection status.
* AI analysis status.
* Damage comparison status.
* Pending review count.
* Damage case count.
* Highest severity.
* Maintenance required flag.
* Damage report link.
* Rental closure guidance based on policy.

## Vehicle Profile

CROMS MAY show:

* Vehicle damage history summary.
* Open damage cases.
* Last inspection date.
* Last inspection status.
* Maintenance routing status.

---

# API Integration

The following Damage Intelligence APIs support CROMS integration.

## Start Check-Out Inspection

```http
POST /api/v1/damage-intelligence/integrations/croms/check-out-inspections
```

## Start Check-In Inspection

```http
POST /api/v1/damage-intelligence/integrations/croms/check-in-inspections
```

## Get Rental Damage Summary

```http
GET /api/v1/damage-intelligence/integrations/croms/rental-agreements/{rentalAgreementId}/damage-summary
```

## Get Inspection Session

```http
GET /api/v1/damage-intelligence/inspection-sessions/{inspectionSessionId}
```

## Get Damage Case

```http
GET /api/v1/damage-intelligence/damage-cases/{damageCaseId}
```

## Generate Damage Report

```http
POST /api/v1/damage-intelligence/damage-cases/{damageCaseId}/reports
```

Detailed logical API behavior is defined in:

```text
DI-0011-API-Specification.md
```

---

# Event Integration

Damage Intelligence SHOULD publish or consume events for CROMS workflows.

## Events from CROMS to Damage Intelligence

| Event                       | Purpose                     |
| --------------------------- | --------------------------- |
| RentalAgreementCreated      | Rental context available    |
| VehicleAssignedToRental     | Vehicle selected for rental |
| CheckOutInspectionRequested | Request baseline inspection |
| VehicleReturned             | Return workflow started     |
| CheckInInspectionRequested  | Request return inspection   |
| RentalAgreementClosed       | Rental closed in CROMS      |

## Events from Damage Intelligence to CROMS

| Event                         | Purpose                             |
| ----------------------------- | ----------------------------------- |
| InspectionSessionCreated      | Inspection session created          |
| InspectionSubmitted           | Inspection evidence submitted       |
| InspectionCompleted           | Inspection completed                |
| AIAnalysisCompleted           | AI findings available               |
| DamageComparisonCompleted     | Comparison completed                |
| DamageCaseCreated             | Damage case created                 |
| ReviewDecisionRecorded        | Review decision recorded            |
| RentalDamageSummaryUpdated    | CROMS-facing damage summary updated |
| DamageReportGenerated         | Evidence report available           |
| DamageCaseRoutedToMaintenance | Repair-required damage routed       |

Detailed event behavior is defined in:

```text
DI-0013-Events.md
```

---

# Data Mapping

## CROMS to Damage Intelligence

| CROMS Field       | Damage Intelligence Field         |
| ----------------- | --------------------------------- |
| TenantId          | tenantId                          |
| RentalAgreementId | rentalAgreementId                 |
| VehicleId         | vehicleId                         |
| CustomerId        | customerId reference              |
| BranchId          | branchId                          |
| UserId            | requestedBy / actorId             |
| CheckOutTime      | expectedHandoverAt                |
| ReturnTime        | actualReturnAt                    |
| VehicleClass      | vehicleType / reporting dimension |

## Damage Intelligence to CROMS

| Damage Intelligence Field | CROMS Field or Usage              |
| ------------------------- | --------------------------------- |
| inspectionSessionId       | Rental inspection reference       |
| inspectionStatus          | Rental workflow indicator         |
| damageCaseId              | Damage case reference             |
| damageSummary             | Rental damage summary             |
| reportId                  | Evidence report reference         |
| maintenanceRequired       | Vehicle/rental workflow indicator |
| highestSeverity           | Rental closure decision support   |
| pendingReviewCount        | Closure warning                   |
| comparisonOutcome         | Damage review context             |

---

# State Synchronization

CROMS and Damage Intelligence SHALL synchronize key states.

## Inspection States Shared with CROMS

* Draft
* Started
* Capturing
* Submitted
* Analyzing
* PendingReview
* Completed
* Closed
* Cancelled

## Damage States Shared with CROMS

* NoDamageDetected
* DamageDetected
* PendingReview
* Confirmed
* Rejected
* Escalated
* RoutedToMaintenance
* Closed

## Synchronization Rules

* Damage Intelligence is authoritative for inspection and damage states.
* CROMS is authoritative for rental states.
* CROMS SHALL not directly modify Damage Intelligence-owned states.
* Damage Intelligence SHALL not directly close rental agreements.
* Integration updates SHALL be idempotent.
* State changes SHALL be audited.

---

# Vehicle Availability Support

Damage Intelligence MAY provide vehicle availability indicators to CROMS.

Examples:

| Indicator                 | Meaning                                         |
| ------------------------- | ----------------------------------------------- |
| NoDamageImpact            | No damage impact identified                     |
| ReviewRequired            | Damage review required before decision          |
| MaintenanceReviewRequired | Maintenance review recommended or required      |
| HoldRecommended           | Damage severity suggests vehicle should be held |
| CriticalSafetyReview      | Potential safety issue requiring escalation     |

Final vehicle availability decision SHALL remain governed by CROMS and Maintenance policies.

---

# Customer Dispute Support

CROMS MAY request Damage Intelligence evidence for customer dispute handling.

Damage Intelligence SHALL provide controlled access to:

* Inspection Summary Report.
* Damage Case Report.
* Current inspection evidence.
* Baseline inspection evidence.
* Damage comparison result.
* Human review decision.
* Audit references where authorized.

Customer-facing reports SHALL be minimized and access-controlled.

AI-only findings SHALL be clearly distinguished from human-reviewed decisions.

---

# Maintenance Routing Visibility in CROMS

When Damage Intelligence routes a case to Maintenance, CROMS SHOULD be able to see:

* Damage Case ID.
* Maintenance Request ID.
* Work Order ID where available.
* Routing status.
* Maintenance status.
* Repair completion status.
* Post-repair inspection status.
* Vehicle availability impact.

Maintenance execution details remain owned by Maintenance.

---

# Security Requirements

Integration between CROMS and Damage Intelligence SHALL enforce:

* Service authentication.
* User authentication where user context is involved.
* Authorization.
* Tenant isolation.
* Object-level access control.
* Secure transport.
* Payload validation.
* Correlation ID.
* Audit logging.
* No permanent public image URLs.

CROMS SHALL only access Damage Intelligence data it is authorized to display.

---

# Privacy Requirements

CROMS integration SHALL minimize customer-linked data.

Damage Intelligence SHOULD receive only the customer reference needed for rental context, not unnecessary customer personal data.

Customer-facing outputs SHALL not expose:

* Internal reviewer notes unless approved.
* Internal AI prompts.
* Internal confidence scores unless approved.
* Unrestricted image links.
* Security audit details.
* Sensitive operational comments.

---

# Audit and Traceability

The integration SHALL support traceability across:

```text
Rental Agreement
  ↓
Check-Out Inspection
  ↓
Baseline Evidence
  ↓
Check-In Inspection
  ↓
Return Evidence
  ↓
AI Findings
  ↓
Damage Comparison
  ↓
Review Decision
  ↓
Damage Case
  ↓
Rental Damage Summary
  ↓
CROMS Rental Closure Workflow
```

All significant integration actions SHALL be audited.

---

# Error Handling

## Duplicate Request

If CROMS sends the same inspection request more than once:

* Damage Intelligence SHOULD detect duplicate request using idempotency key or rental context.
* Existing inspection session SHOULD be returned where appropriate.
* Duplicate sessions SHOULD be avoided unless explicitly allowed.

## Missing Vehicle

If vehicle reference is invalid:

* Request SHALL be rejected.
* Error SHALL identify invalid vehicle reference.
* Audit SHALL record failure.

## Missing Rental Agreement

If rental agreement reference is invalid:

* Request SHALL be rejected or accepted only where inspection type permits.
* Error SHALL identify invalid rental context.

## Damage Intelligence Unavailable

If Damage Intelligence is unavailable:

* CROMS SHOULD show inspection service unavailable.
* CROMS MAY allow manual fallback according to policy.
* Requests SHOULD retry where appropriate.
* Failure SHALL be auditable.

## CROMS Callback Failure

If Damage Intelligence cannot update CROMS:

* Update SHALL be retried.
* Failure SHALL be logged.
* Event MAY be dead-lettered.
* Authorized users SHOULD see integration failure status.

---

# Idempotency

The following integration operations SHALL support idempotency:

* Create check-out inspection.
* Create check-in inspection.
* Submit inspection status update.
* Rental damage summary update.
* Damage case notification.
* Report generation request.

Idempotency SHOULD use:

* X-Idempotency-Key.
* Rental Agreement ID.
* Vehicle ID.
* Inspection Type.
* Correlation ID.

---

# Correlation and Causation

All CROMS integration requests SHOULD include:

* Correlation ID.
* Causation ID where available.
* Actor ID.
* Tenant ID.
* Source system.

Damage Intelligence SHALL propagate correlation IDs to:

* Audit records.
* Events.
* AI processing.
* Reports.
* Maintenance routing.

---

# Performance Expectations

Integration APIs SHOULD support operational responsiveness.

Recommended behavior:

* Inspection session creation: synchronous.
* Image upload: asynchronous upload with registration.
* AI analysis: asynchronous.
* Damage comparison: asynchronous where needed.
* Damage summary retrieval: synchronous.
* Report generation: asynchronous where large.

CROMS UI SHOULD show clear processing states.

---

# Reliability Requirements

The integration SHOULD support:

* Retry-safe operations.
* Idempotent consumers.
* Dead-letter handling for events.
* Monitoring of failed integrations.
* Manual replay where approved.
* Clear user-facing status.
* Audit trail for failures and retries.

---

# Integration Testing

Testing SHALL cover:

* Check-out inspection request.
* Check-in inspection request.
* Duplicate request handling.
* Missing vehicle reference.
* Missing rental agreement reference.
* Inspection status update.
* AI analysis completion update.
* Damage comparison completion update.
* Damage case creation update.
* Rental damage summary retrieval.
* Damage report retrieval.
* Security authorization.
* Tenant isolation.
* CROMS callback failure.
* Event retry.
* Audit creation.
* Correlation ID propagation.

---

# Acceptance Criteria

The integration SHALL be accepted when:

* CROMS can create check-out inspection sessions.
* CROMS can create check-in inspection sessions.
* Damage Intelligence can return inspection status to CROMS.
* Damage Intelligence can provide rental damage summary.
* Damage Intelligence can provide evidence report references.
* Damage Intelligence can notify CROMS of review-required damage.
* Damage Intelligence can notify CROMS of confirmed or rejected damage.
* Integration enforces tenant isolation.
* Integration actions are auditable.
* Duplicate requests do not create duplicate inspection sessions or duplicate damage cases.
* Failure states are visible and recoverable.

---

# Normative Requirements

## Requirement

ID: REQ-DI-1600

Title:
CROMS Integration

Statement:
Damage Intelligence SHALL integrate with CROMS for rental check-out, rental check-in, rental damage summary, damage case status, and evidence report access.

Priority:
Critical

Verification:
Integration Test

---

## Requirement

ID: REQ-DI-1601

Title:
CROMS Ownership Boundary

Statement:
CROMS SHALL remain the system of record for rental agreements, rental lifecycle, customer rental context, rental closure, and vehicle availability decisions.

Priority:
Critical

Verification:
Architecture Review

---

## Requirement

ID: REQ-DI-1602

Title:
Damage Intelligence Ownership Boundary

Statement:
Damage Intelligence SHALL remain the system of record for inspection evidence, damage findings, comparisons, damage cases, review decisions, advisory estimates, and damage reports.

Priority:
Critical

Verification:
Architecture Review

---

## Requirement

ID: REQ-DI-1603

Title:
Check-Out Inspection Request

Statement:
CROMS SHALL be able to request creation of a Damage Intelligence Check-Out Inspection session.

Priority:
Critical

Verification:
Integration Test

---

## Requirement

ID: REQ-DI-1604

Title:
Check-In Inspection Request

Statement:
CROMS SHALL be able to request creation of a Damage Intelligence Check-In Inspection session.

Priority:
Critical

Verification:
Integration Test

---

## Requirement

ID: REQ-DI-1605

Title:
Rental Damage Summary

Statement:
Damage Intelligence SHALL provide CROMS with a rental damage summary for rental workflow decision support.

Priority:
Critical

Verification:
Integration Test

---

## Requirement

ID: REQ-DI-1606

Title:
Damage Comparison Status to CROMS

Statement:
Damage Intelligence SHALL provide CROMS with damage comparison status and outcome summary for check-in workflows.

Priority:
High

Verification:
Integration Test

---

## Requirement

ID: REQ-DI-1607

Title:
Damage Case Status to CROMS

Statement:
Damage Intelligence SHALL provide CROMS with damage case status updates for rental-related damage cases.

Priority:
High

Verification:
Integration Test

---

## Requirement

ID: REQ-DI-1608

Title:
Evidence Report Reference

Statement:
Damage Intelligence SHALL provide CROMS with controlled evidence report references where authorized.

Priority:
High

Verification:
Security/Integration Test

---

## Requirement

ID: REQ-DI-1609

Title:
No Final Rental Closure by Damage Intelligence

Statement:
Damage Intelligence SHALL NOT directly close rental agreements or make final rental billing decisions.

Priority:
Critical

Verification:
Governance Review

---

## Requirement

ID: REQ-DI-1610

Title:
No Final Customer Charge by Damage Intelligence

Statement:
Damage Intelligence SHALL NOT independently determine final customer charges through CROMS integration.

Priority:
Critical

Verification:
Governance Review

---

## Requirement

ID: REQ-DI-1611

Title:
Integration Security

Statement:
CROMS and Damage Intelligence integration SHALL enforce authentication, authorization, tenant isolation, secure transport, and audit logging.

Priority:
Critical

Verification:
Security Test

---

## Requirement

ID: REQ-DI-1612

Title:
Integration Idempotency

Statement:
CROMS integration operations SHOULD support idempotency to avoid duplicate inspections, cases, reports, or updates.

Priority:
High

Verification:
Integration Test

---

## Requirement

ID: REQ-DI-1613

Title:
Integration Traceability

Statement:
CROMS integration SHALL propagate correlation IDs and support traceability from rental agreement to inspection, evidence, damage case, report, and audit records.

Priority:
High

Verification:
Traceability Test

---

## Requirement

ID: REQ-DI-1614

Title:
Integration Failure Handling

Statement:
Damage Intelligence and CROMS SHALL handle integration failures through retries, visible status, audit logging, and manual recovery where approved.

Priority:
High

Verification:
Reliability Test

---

## Requirement

ID: REQ-DI-1615

Title:
Customer Dispute Evidence Support

Statement:
Damage Intelligence SHALL support controlled evidence and report access for CROMS customer dispute workflows where authorized.

Priority:
High

Verification:
Report/Security Test

---

# Business Rules

## BR-DI-1200 — CROMS Owns Rental Lifecycle

CROMS SHALL own rental agreement state, rental closure, and rental billing decisions.

---

## BR-DI-1201 — Damage Intelligence Owns Inspection Evidence

Damage Intelligence SHALL own inspection evidence, damage findings, comparison results, and damage cases.

---

## BR-DI-1202 — Rental Handover May Require Baseline Inspection

CROMS policy MAY require completed baseline inspection before rental handover.

---

## BR-DI-1203 — Rental Closure May Require Return Inspection

CROMS policy MAY require completed return inspection before rental closure.

---

## BR-DI-1204 — Customer-Impacting Damage Requires Review

Damage that may affect customer dispute or charge workflow SHALL require human review according to approved policy.

---

## BR-DI-1205 — Damage Summary Is Decision Support

Rental Damage Summary SHALL support CROMS decisions but SHALL NOT itself be final billing or liability decision.

---

## BR-DI-1206 — Evidence Links Must Be Controlled

CROMS SHALL access evidence only through authorized, controlled references.

---

## BR-DI-1207 — Duplicate Integration Requests Must Not Duplicate Business Objects

Duplicate CROMS requests SHALL NOT create duplicate inspection sessions, damage cases, or reports where idempotency applies.

---

# AI Implementation Contract

AI development agents SHALL:

* Treat this document as the authoritative CROMS integration specification for Damage Intelligence.
* Preserve all requirement IDs.
* Preserve CROMS and Damage Intelligence ownership boundaries.
* Preserve the rule that Damage Intelligence does not close rentals or determine final customer charges.
* Generate APIs, events, schemas, tests, and UI integration behavior consistent with this document.
* Preserve tenant isolation, authentication, authorization, audit, and traceability requirements.
* Preserve idempotency and failure handling requirements.
* Preserve controlled evidence access.
* Raise ambiguity where rental lifecycle ownership, damage summary meaning, customer-facing report access, or vehicle availability policy is unclear.

---

# References

* DI-0004 – Damage Intelligence Inspection Workflow
* DI-0005 – AI Damage Detection
* DI-0006 – Damage Comparison
* DI-0007 – Vehicle Capture Standards
* DI-0008 – Damage Taxonomy
* DI-0009 – Severity Assessment
* DI-0010 – Repair Cost Estimation
* DI-0011 – API Specification
* DI-0012 – Domain Model
* DI-0013 – Events
* DI-0014 – Security and Privacy
* DI-0015 – Audit and Traceability
* DI-0016 – Reporting and Dashboards
* RA-0002 – Domain-Driven Design Architecture
* GEES-0007 – Enterprise Security Standard
* GEES-0009 – Traceability Standard
* PLATFORM-0005 – GEES Core and Application Architecture

---

# Revision History

| Version | Date       | Description                                                      |
| ------- | ---------- | ---------------------------------------------------------------- |
| 1.0.0   | 2026-06-27 | Initial Damage Intelligence Integration with CROMS Specification |

