---

id: "DI-0018"
title: "Damage Intelligence Integration with Maintenance"
version: "1.0.0"
document_type: "Product Specification"
document_class: "Integration Specification"
status: "Draft"
classification: "Internal"
owner: "Riyadah Technology"
reviewers: "Chief Enterprise Architect, Product Owner, Maintenance Lead, Damage Intelligence Lead, API Architecture Lead, Security Lead, Operations Lead, QA Lead"
approvers: ""
created: "2026-06-27"
updated: "2026-06-27"
authoritative: true
ai_consumable: true
related: "DI-0001, DI-0002, DI-0004, DI-0005, DI-0006, DI-0007, DI-0008, DI-0009, DI-0010, DI-0011, DI-0012, DI-0013, DI-0014, DI-0015, DI-0016, DI-0017, RA-0001, RA-0002, GEES-0007, GEES-0009, PLATFORM-0005"
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Damage Intelligence Integration with Maintenance

## Executive Summary

This document defines the integration between Damage Intelligence and GCU365 Maintenance.

Damage Intelligence identifies, classifies, compares, reviews, and documents vehicle damage. Maintenance manages repair review, work order creation, technician assignment, repair execution, parts usage, actual repair cost, and repair completion.

The integration SHALL support:

* Routing confirmed repair-required damage to Maintenance.
* Sharing inspection evidence with Maintenance.
* Sharing damage type, severity, vehicle area, and comparison outcome.
* Providing advisory repair estimate context.
* Creating or requesting maintenance review.
* Receiving work order and repair status updates.
* Supporting post-repair inspection.
* Supporting evidence-based closure.
* Preserving audit and traceability.

Damage Intelligence SHALL not own the Maintenance work order lifecycle or actual repair cost. Maintenance SHALL remain the system of record for repair execution and actual repair outcomes.

---

# Purpose

The purpose of this document is to define how Damage Intelligence and Maintenance interact.

This specification SHALL guide:

* Maintenance routing workflow.
* Damage case handoff.
* Evidence sharing.
* Advisory repair estimate sharing.
* Work order reference mapping.
* Repair status synchronization.
* Post-repair inspection workflow.
* API and event integration.
* Audit and traceability.
* Security and privacy.
* Test case generation.

---

# Scope

## In Scope

This specification covers:

* Damage-to-Maintenance handoff.
* Maintenance review request.
* Evidence package transfer.
* Damage case routing.
* Advisory repair estimate sharing.
* Work order reference synchronization.
* Repair status updates.
* Post-repair inspection coordination.
* Actual repair cost reference handling.
* Maintenance closure feedback.
* API integration.
* Event integration.
* Failure handling.
* Security and tenant isolation.
* Audit and traceability.

## Out of Scope

This specification does not define:

* Full Maintenance work order design.
* Technician scheduling.
* Parts inventory workflow.
* Procurement workflow.
* Final repair invoice.
* Final accounting posting.
* Final customer charge.
* Full workshop operation workflow.
* Full Maintenance mobile app UI.
* Final OpenAPI YAML.
* Final database schema.

---

# Integration Principles

The integration between Damage Intelligence and Maintenance SHALL follow these principles:

1. Clear System Ownership
2. Evidence-Based Repair Handoff
3. Advisory Estimate Separation
4. Secure Evidence Access
5. Tenant Isolation
6. Idempotent Routing
7. Auditable State Changes
8. Traceable Repair Context
9. Human Review Before Repair Impact
10. No Duplicate Work Order Ownership

---

# System Ownership

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
* Severity Assessment.
* Advisory Repair Estimates.
* Damage Reports.
* Damage evidence audit trail.

## Maintenance Owns

Maintenance SHALL own:

* Maintenance Request.
* Work Order.
* Repair planning.
* Technician assignment.
* Repair execution.
* Parts usage.
* Actual repair cost.
* Repair completion status.
* Post-repair work order closure.
* Maintenance operational audit.

## Shared Context

The following are shared by reference:

* Tenant ID.
* Vehicle ID.
* Damage Case ID.
* Damage Finding ID.
* Inspection Session ID.
* Evidence Image ID.
* Repair Estimate ID.
* Maintenance Request ID.
* Work Order ID.
* User ID.
* Branch ID.

Shared context SHALL use stable identifiers.

---

# Integration Context Map

```text
Damage Intelligence
  |
  | Confirmed repair-required damage
  | Evidence package
  | Severity
  | Advisory estimate
  v
Maintenance
  |
  | Maintenance review
  | Work order creation
  | Repair execution
  | Actual cost
  | Repair completion
  v
Damage Intelligence
  |
  | Post-repair evidence
  | Damage case update
  | Repair status visibility
  | Reporting and audit
```

---

# Primary Integration Workflows

Damage Intelligence and Maintenance SHALL support the following primary workflows.

| Workflow                    | Description                                                      |
| --------------------------- | ---------------------------------------------------------------- |
| Damage Case Routing         | Route confirmed repair-required damage to Maintenance            |
| Maintenance Review          | Maintenance reviews evidence and decides repair action           |
| Work Order Reference Sync   | Maintenance shares work order reference with Damage Intelligence |
| Repair Status Update        | Maintenance updates repair lifecycle status                      |
| Post-Repair Inspection      | Damage Intelligence supports post-repair evidence capture        |
| Actual Cost Reference       | Maintenance or Finance shares actual repair cost reference       |
| Damage Case Closure Support | Repair completion informs Damage Intelligence case status        |

---

# Damage Case Routing Workflow

## Purpose

Damage Case Routing sends confirmed or review-required repair damage from Damage Intelligence to Maintenance.

## Trigger

Damage Intelligence MAY route a damage case to Maintenance when:

* Damage is confirmed by authorized reviewer.
* Severity is Major or Critical.
* Damage is safety-relevant.
* Repair category indicates repair required.
* Advisory estimate recommends Maintenance review.
* CROMS or Operations policy requires Maintenance review.
* Damage case status requires repair assessment.

## Preconditions

Before routing:

* Damage Case SHALL exist.
* Damage Finding SHALL exist.
* Vehicle ID SHALL be known.
* Evidence package SHOULD be available.
* Human review SHOULD be completed where required.
* Routing user or system SHALL be authorized.
* Maintenance integration SHALL be available or queued.

---

# Routing Payload

Damage Intelligence SHOULD provide Maintenance with the following routing payload.

| Field               | Required    | Description                          |
| ------------------- | ----------- | ------------------------------------ |
| tenantId            | Yes         | Tenant identifier                    |
| damageCaseId        | Yes         | Damage case reference                |
| vehicleId           | Yes         | Vehicle reference                    |
| rentalAgreementId   | Optional    | Rental context where available       |
| inspectionSessionId | Yes         | Source inspection session            |
| damageFindingIds    | Yes         | Related damage findings              |
| damageType          | Yes         | Damage taxonomy value                |
| vehicleArea         | Yes         | Affected vehicle area                |
| severity            | Yes         | Severity value                       |
| comparisonOutcome   | Optional    | New, PreExisting, Changed, etc.      |
| repairRelevance     | Recommended | Repair relevance classification      |
| advisoryEstimateId  | Optional    | Advisory estimate reference          |
| evidenceImageIds    | Recommended | Evidence image references            |
| reportId            | Optional    | Maintenance handoff report reference |
| routedBy            | Yes         | User or system actor                 |
| routedAt            | Yes         | Routing timestamp                    |
| routingReason       | Yes         | Reason for routing                   |

---

# Routing Payload Example

```json
{
  "tenantId": "TENANT-000001",
  "damageCaseId": "DMC-DI-000001",
  "vehicleId": "VEH-000001",
  "rentalAgreementId": "RA-000001",
  "inspectionSessionId": "INS-DI-000025",
  "damageFindingIds": [
    "DMF-DI-000001"
  ],
  "damageType": "DENT",
  "vehicleArea": "LEFT_REAR_DOOR",
  "severity": "MODERATE",
  "comparisonOutcome": "New",
  "repairRelevance": "REPAIR_RECOMMENDED",
  "advisoryEstimateId": "EST-DI-000001",
  "evidenceImageIds": [
    "IMG-DI-000101",
    "IMG-DI-000055"
  ],
  "reportId": "RPT-DI-000001",
  "routedBy": "USR-000001",
  "routedAt": "2026-06-27T00:00:00Z",
  "routingReason": "RepairRequired"
}
```

---

# Maintenance Response

Maintenance SHOULD return:

| Field                | Description                          |
| -------------------- | ------------------------------------ |
| maintenanceRequestId | Maintenance request reference        |
| workOrderId          | Work order reference where created   |
| status               | Maintenance routing status           |
| accepted             | Whether Maintenance accepted request |
| rejectionReason      | Reason if rejected                   |
| assignedTeam         | Maintenance team where available     |
| receivedAt           | Timestamp                            |

---

# Maintenance Review Workflow

```text
Damage Case Routed
        ↓
Maintenance Receives Evidence Package
        ↓
Maintenance Advisor Reviews Damage Context
        ↓
Maintenance Accepts, Rejects, or Requests More Evidence
        ↓
Work Order Created Where Required
        ↓
Damage Intelligence Receives Maintenance Status
        ↓
Damage Case Updated with Maintenance Reference
```

---

# Work Order Creation Rules

Maintenance MAY create a work order when:

* Repair is required.
* Inspection evidence is sufficient.
* Vehicle is available for repair.
* Maintenance policy requires work order.
* Safety review requires workshop inspection.
* Manual Maintenance advisor approves work order creation.

Damage Intelligence SHALL NOT create the final work order directly unless Maintenance exposes an approved API contract that treats the request as a Maintenance-owned operation.

---

# Evidence Package

Damage Intelligence SHALL provide Maintenance with controlled access to an evidence package.

The evidence package MAY include:

* Current inspection images.
* Historical baseline images.
* Damage finding details.
* Damage comparison result.
* Severity assessment.
* Human review decision.
* Advisory repair estimate.
* Damage case report.
* Capture metadata.
* Audit references where authorized.

Evidence access SHALL be secure and authorized.

---

# Advisory Repair Estimate Sharing

Damage Intelligence MAY provide advisory repair estimate context to Maintenance.

Maintenance SHALL treat Damage Intelligence repair estimates as advisory.

Maintenance SHALL own:

* Final repair scope.
* Final labor estimate.
* Parts requirement.
* Actual repair cost.
* Work order cost.
* Repair completion status.

Damage Intelligence SHALL NOT treat advisory estimate as final repair cost.

---

# Maintenance Status Values

Maintenance SHOULD return standardized status values.

| Status                     | Description                       |
| -------------------------- | --------------------------------- |
| Received                   | Maintenance received routed case  |
| UnderReview                | Maintenance is reviewing evidence |
| AdditionalEvidenceRequired | Maintenance needs more evidence   |
| Accepted                   | Maintenance accepted the case     |
| Rejected                   | Maintenance rejected the case     |
| WorkOrderCreated           | Work order created                |
| RepairInProgress           | Repair work is in progress        |
| WaitingForParts            | Repair is waiting for parts       |
| RepairCompleted            | Repair completed                  |
| QualityInspectionRequired  | Post-repair inspection required   |
| Closed                     | Maintenance process closed        |
| Cancelled                  | Maintenance request cancelled     |

---

# Damage Intelligence Status Mapping

| Maintenance Status         | Damage Intelligence Impact                  |
| -------------------------- | ------------------------------------------- |
| Received                   | MaintenanceRoutingStatus = Received         |
| UnderReview                | MaintenanceRoutingStatus = UnderReview      |
| AdditionalEvidenceRequired | Damage Case requires additional evidence    |
| Accepted                   | Damage Case marked accepted by Maintenance  |
| Rejected                   | Damage Case marked MaintenanceRejected      |
| WorkOrderCreated           | Work Order reference stored                 |
| RepairInProgress           | Repair status visible in Damage Case        |
| WaitingForParts            | Repair delay visible in reports             |
| RepairCompleted            | Post-repair inspection may be triggered     |
| QualityInspectionRequired  | Post-repair inspection required             |
| Closed                     | Damage Case may move toward resolved/closed |
| Cancelled                  | Damage Case requires review                 |

---

# Post-Repair Inspection Workflow

## Purpose

Post-repair inspection captures evidence after repair completion.

## Trigger

Post-repair inspection MAY be triggered when:

* Maintenance marks repair completed.
* Maintenance requests quality inspection.
* Work order requires closure evidence.
* Damage Intelligence policy requires repair verification.
* CROMS requires vehicle readiness evidence.

## Workflow

```text
Maintenance Reports Repair Completed
        ↓
Damage Intelligence Creates Maintenance Quality Inspection
        ↓
User Captures Post-Repair Evidence
        ↓
Evidence Compared to Pre-Repair Damage
        ↓
Reviewer Confirms Repair Outcome Where Required
        ↓
Damage Case Updated
        ↓
Maintenance and CROMS Receive Status
```

---

# Post-Repair Evidence

Post-repair evidence SHOULD include:

* Post-repair images.
* Repair completion timestamp.
* Work Order ID.
* Technician or advisor reference where available.
* Quality inspection result.
* Reviewer decision where required.
* Remaining damage notes where applicable.

---

# Actual Repair Cost Reference

Maintenance or Finance MAY provide actual repair cost reference.

Damage Intelligence MAY store:

* Actual cost reference ID.
* Work Order ID.
* Cost availability status.
* Currency.
* Summary range or amount only where authorized.
* Supersession of advisory estimate.

Damage Intelligence SHALL NOT own final actual repair cost.

Actual repair cost SHALL be owned by Maintenance or Finance.

---

# API Integration

The following logical APIs support Maintenance integration.

## Route Damage Case to Maintenance

```http
POST /api/v1/damage-intelligence/damage-cases/{damageCaseId}/route-to-maintenance
```

## Receive Maintenance Status Update

```http
POST /api/v1/damage-intelligence/integrations/maintenance/status-updates
```

## Get Damage Case for Maintenance

```http
GET /api/v1/damage-intelligence/damage-cases/{damageCaseId}
```

## Get Maintenance Handoff Report

```http
GET /api/v1/damage-intelligence/reports/{reportId}
```

## Start Post-Repair Inspection

```http
POST /api/v1/damage-intelligence/integrations/maintenance/post-repair-inspections
```

Detailed logical API behavior is defined in:

```text
DI-0011-API-Specification.md
```

---

# Event Integration

## Events from Damage Intelligence to Maintenance

| Event                             | Purpose                          |
| --------------------------------- | -------------------------------- |
| DamageCaseRoutedToMaintenance     | Repair-required damage routed    |
| MaintenanceHandoffReportGenerated | Evidence report available        |
| AdditionalEvidenceProvided        | Requested evidence provided      |
| PostRepairInspectionCompleted     | Post-repair inspection completed |
| DamageCaseClosed                  | Damage case closed or resolved   |

## Events from Maintenance to Damage Intelligence

| Event                      | Purpose                          |
| -------------------------- | -------------------------------- |
| MaintenanceRequestReceived | Maintenance accepted receipt     |
| MaintenanceRequestRejected | Maintenance rejected request     |
| WorkOrderCreated           | Work order created               |
| RepairStatusUpdated        | Repair lifecycle changed         |
| RepairCompleted            | Repair completed                 |
| QualityInspectionRequested | Post-repair inspection requested |
| ActualRepairCostAvailable  | Actual cost reference available  |

Detailed event behavior is defined in:

```text
DI-0013-Events.md
```

---

# Data Mapping

## Damage Intelligence to Maintenance

| Damage Intelligence Field | Maintenance Field or Usage           |
| ------------------------- | ------------------------------------ |
| damageCaseId              | Maintenance request source reference |
| vehicleId                 | Vehicle reference                    |
| inspectionSessionId       | Inspection evidence source           |
| damageFindingIds          | Damage scope references              |
| damageType                | Repair category input                |
| vehicleArea               | Repair location                      |
| severity                  | Repair priority input                |
| repairRelevance           | Repair requirement guidance          |
| advisoryEstimateId        | Estimate context                     |
| evidenceImageIds          | Evidence references                  |
| reportId                  | Maintenance handoff report           |
| routingReason             | Maintenance request reason           |

## Maintenance to Damage Intelligence

| Maintenance Field            | Damage Intelligence Field or Usage |
| ---------------------------- | ---------------------------------- |
| maintenanceRequestId         | Maintenance routing reference      |
| workOrderId                  | Work order reference               |
| maintenanceStatus            | Maintenance routing status         |
| repairStatus                 | Repair progress                    |
| actualRepairCostReference    | Actual cost reference              |
| repairCompletedAt            | Repair completion timestamp        |
| postRepairInspectionRequired | Inspection trigger                 |
| rejectionReason              | Routing review reason              |

---

# Security Requirements

Maintenance integration SHALL enforce:

* Service authentication.
* User authentication where applicable.
* Authorization.
* Tenant isolation.
* Object-level access control.
* Secure transport.
* Payload validation.
* Controlled evidence access.
* No permanent public image URLs.
* Audit logging.

Maintenance users SHALL access only authorized evidence and reports.

---

# Privacy Requirements

Maintenance integration SHALL minimize customer-linked data.

Maintenance SHOULD receive:

* Vehicle reference.
* Damage evidence.
* Damage classification.
* Repair context.
* Work order context.

Maintenance SHOULD NOT receive unnecessary customer personal data unless explicitly required by approved business process.

---

# Audit and Traceability

The integration SHALL support traceability across:

```text
Damage Case
  ↓
Damage Findings
  ↓
Evidence Package
  ↓
Human Review Decision
  ↓
Advisory Repair Estimate
  ↓
Maintenance Routing
  ↓
Maintenance Request
  ↓
Work Order
  ↓
Repair Status
  ↓
Post-Repair Inspection
  ↓
Damage Case Closure
```

All significant routing, status, review, repair, and closure actions SHALL be audited.

---

# Error Handling

## Duplicate Routing

If the same damage case is routed more than once:

* System SHOULD detect duplicate routing.
* Existing Maintenance request SHOULD be returned where appropriate.
* Duplicate Maintenance requests SHOULD be avoided.

## Missing Evidence

If evidence is missing:

* Maintenance MAY request additional evidence.
* Damage Intelligence SHALL record the request.
* Damage Case status MAY move to AdditionalEvidenceRequired.

## Maintenance Rejection

If Maintenance rejects a routed case:

* Rejection reason SHALL be recorded.
* Damage Case SHALL require review.
* CROMS MAY be notified where rental workflow is affected.

## Maintenance Unavailable

If Maintenance is unavailable:

* Routing request SHOULD be queued or retried.
* Failure SHALL be visible to authorized users.
* Audit record SHALL be created.

## Status Update Failure

If Damage Intelligence cannot process a Maintenance status update:

* Failure SHALL be logged.
* Event MAY be retried or dead-lettered.
* Manual recovery SHOULD be supported.

---

# Idempotency

The following operations SHOULD support idempotency:

* Route damage case to Maintenance.
* Receive Maintenance request acceptance.
* Receive work order creation.
* Receive repair status update.
* Receive repair completion.
* Start post-repair inspection.

Idempotency SHOULD use:

* Damage Case ID.
* Maintenance Request ID.
* Work Order ID.
* Event ID.
* Correlation ID.
* Idempotency key where applicable.

---

# Performance Expectations

Recommended behavior:

* Routing request may be synchronous if Maintenance is available.
* Work order creation may be asynchronous.
* Repair status updates should be event-driven or API callback-based.
* Post-repair inspection creation should be synchronous or queued.
* Large reports should be generated asynchronously.

---

# Reliability Requirements

The integration SHOULD support:

* Retry-safe operations.
* Idempotent event consumption.
* Dead-letter handling.
* Manual replay where approved.
* Visible integration status.
* Alerting for failed routing.
* Audit trail for retries and failures.

---

# Integration Testing

Testing SHALL cover:

* Route confirmed damage case to Maintenance.
* Route safety-critical damage.
* Duplicate routing request.
* Missing evidence handling.
* Maintenance acceptance.
* Maintenance rejection.
* Work order reference update.
* Repair status update.
* Repair completion.
* Post-repair inspection creation.
* Actual cost reference handling.
* Security authorization.
* Tenant isolation.
* Evidence access control.
* Audit creation.
* Correlation ID propagation.
* Integration failure and retry.

---

# Acceptance Criteria

The integration SHALL be accepted when:

* Damage Intelligence can route confirmed repair-required damage to Maintenance.
* Maintenance can receive damage case context and evidence references.
* Maintenance can return request and work order references.
* Damage Intelligence can receive Maintenance status updates.
* Damage Intelligence can trigger post-repair inspection when required.
* Actual repair cost remains owned by Maintenance or Finance.
* Advisory estimates are not treated as actual costs.
* Evidence access is secure and auditable.
* Duplicate routing does not create duplicate Maintenance requests.
* Integration failures are visible and recoverable.
* Tenant isolation is enforced.

---

# Normative Requirements

## Requirement

ID: REQ-DI-1700

Title:
Maintenance Integration

Statement:
Damage Intelligence SHALL integrate with Maintenance for routing confirmed repair-required damage, sharing evidence context, receiving work order references, and tracking repair status.

Priority:
Critical

Verification:
Integration Test

---

## Requirement

ID: REQ-DI-1701

Title:
Maintenance Ownership Boundary

Statement:
Maintenance SHALL remain the system of record for maintenance requests, work orders, repair execution, technician assignment, parts usage, actual repair cost, and repair completion.

Priority:
Critical

Verification:
Architecture Review

---

## Requirement

ID: REQ-DI-1702

Title:
Damage Intelligence Ownership Boundary

Statement:
Damage Intelligence SHALL remain the system of record for damage evidence, findings, comparisons, cases, review decisions, severity assessments, advisory estimates, and damage reports.

Priority:
Critical

Verification:
Architecture Review

---

## Requirement

ID: REQ-DI-1703

Title:
Damage Case Routing

Statement:
Damage Intelligence SHALL support routing confirmed repair-required damage cases to Maintenance.

Priority:
Critical

Verification:
Integration Test

---

## Requirement

ID: REQ-DI-1704

Title:
Maintenance Evidence Package

Statement:
Damage Intelligence SHALL provide Maintenance with controlled access to evidence packages for routed damage cases.

Priority:
Critical

Verification:
Security/Integration Test

---

## Requirement

ID: REQ-DI-1705

Title:
Advisory Estimate Separation

Statement:
Damage Intelligence advisory repair estimates SHALL NOT be treated as actual repair costs.

Priority:
Critical

Verification:
Governance Review

---

## Requirement

ID: REQ-DI-1706

Title:
Work Order Reference Synchronization

Statement:
Maintenance SHALL be able to provide work order references back to Damage Intelligence.

Priority:
High

Verification:
Integration Test

---

## Requirement

ID: REQ-DI-1707

Title:
Repair Status Synchronization

Statement:
Maintenance SHALL be able to provide repair status updates to Damage Intelligence.

Priority:
High

Verification:
Integration Test

---

## Requirement

ID: REQ-DI-1708

Title:
Post-Repair Inspection

Statement:
Damage Intelligence SHOULD support post-repair inspection triggered by Maintenance repair completion or quality inspection requirement.

Priority:
High

Verification:
Workflow Test

---

## Requirement

ID: REQ-DI-1709

Title:
Actual Cost Ownership

Statement:
Actual repair cost SHALL be owned by Maintenance or Finance, not Damage Intelligence.

Priority:
Critical

Verification:
Architecture Review

---

## Requirement

ID: REQ-DI-1710

Title:
Maintenance Integration Security

Statement:
Maintenance integration SHALL enforce authentication, authorization, tenant isolation, secure transport, controlled evidence access, and audit logging.

Priority:
Critical

Verification:
Security Test

---

## Requirement

ID: REQ-DI-1711

Title:
Maintenance Integration Idempotency

Statement:
Maintenance integration operations SHOULD support idempotency to avoid duplicate maintenance requests, work orders, inspections, or status updates.

Priority:
High

Verification:
Reliability Test

---

## Requirement

ID: REQ-DI-1712

Title:
Maintenance Integration Traceability

Statement:
Maintenance integration SHALL support traceability from damage case to evidence, review decision, maintenance request, work order, repair status, and post-repair inspection.

Priority:
High

Verification:
Traceability Test

---

## Requirement

ID: REQ-DI-1713

Title:
Maintenance Failure Handling

Statement:
Damage Intelligence and Maintenance SHALL handle integration failures through retries, visible status, audit logging, and manual recovery where approved.

Priority:
High

Verification:
Reliability Test

---

## Requirement

ID: REQ-DI-1714

Title:
Additional Evidence Request

Statement:
Maintenance SHALL be able to request additional evidence for routed damage cases where evidence is insufficient.

Priority:
Medium

Verification:
Workflow Test

---

## Requirement

ID: REQ-DI-1715

Title:
Maintenance Rejection Handling

Statement:
Damage Intelligence SHALL record Maintenance rejection reasons and route rejected cases for review.

Priority:
Medium

Verification:
Workflow Test

---

# Business Rules

## BR-DI-1300 — Maintenance Owns Repair Execution

Maintenance SHALL own repair planning, work order creation, technician assignment, repair execution, and repair completion.

---

## BR-DI-1301 — Damage Intelligence Owns Damage Evidence

Damage Intelligence SHALL own damage evidence, damage findings, comparison results, review decisions, and damage cases.

---

## BR-DI-1302 — Advisory Estimate Is Not Actual Cost

Damage Intelligence advisory estimate SHALL NOT be treated as actual repair cost.

---

## BR-DI-1303 — Repair-Required Damage May Be Routed

Confirmed repair-required damage MAY be routed to Maintenance according to policy.

---

## BR-DI-1304 — Safety-Relevant Damage Requires Maintenance Review

Safety-relevant damage SHALL require Maintenance or safety review before release decisions where policy requires.

---

## BR-DI-1305 — Evidence Access Must Be Controlled

Maintenance SHALL access damage evidence only through authorized, controlled references.

---

## BR-DI-1306 — Duplicate Routing Must Not Duplicate Maintenance Work

Duplicate routing requests SHALL NOT create duplicate Maintenance requests or work orders where idempotency applies.

---

# AI Implementation Contract

AI development agents SHALL:

* Treat this document as the authoritative Maintenance integration specification for Damage Intelligence.
* Preserve all requirement IDs.
* Preserve Damage Intelligence and Maintenance ownership boundaries.
* Preserve the rule that actual repair cost is not owned by Damage Intelligence.
* Preserve the rule that advisory estimates are not actual repair costs or final customer charges.
* Generate APIs, events, schemas, tests, and UI integration behavior consistent with this document.
* Preserve tenant isolation, authentication, authorization, audit, and traceability requirements.
* Preserve idempotency and failure handling requirements.
* Preserve controlled evidence access.
* Raise ambiguity where repair ownership, work order state, actual cost reference, post-repair inspection rules, or evidence access rules are unclear.

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
* DI-0017 – Integration with CROMS
* RA-0002 – Domain-Driven Design Architecture
* GEES-0007 – Enterprise Security Standard
* GEES-0009 – Traceability Standard
* PLATFORM-0005 – GEES Core and Application Architecture

---

# Revision History

| Version | Date       | Description                                                            |
| ------- | ---------- | ---------------------------------------------------------------------- |
| 1.0.0   | 2026-06-27 | Initial Damage Intelligence Integration with Maintenance Specification |

