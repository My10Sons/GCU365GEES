---
id: DI-0013
title: Damage Intelligence Events
version: 1.0.0
document_type: Product Specification
document_class: Event Specification
status: Draft
classification: Internal
owner: Riyadah Technology
reviewers:
  - Chief Enterprise Architect
  - Product Owner
  - Domain Architect
  - API Architecture Lead
  - AI Engineering Lead
  - Security Lead
  - CROMS Lead
  - Maintenance Lead
approvers: []
created: 2026-06-27
updated: 2026-06-27
authoritative: true
ai_consumable: true
related:
  - DI-0001
  - DI-0002
  - DI-0004
  - DI-0005
  - DI-0006
  - DI-0007
  - DI-0008
  - DI-0009
  - DI-0010
  - DI-0011
  - DI-0012
  - RA-0001
  - RA-0002
  - GEES-0007
  - GEES-0009
  - PLATFORM-0005
---

# Damage Intelligence Events

## Executive Summary

This document defines the domain events and integration events used by Damage Intelligence.

Events are used to communicate significant lifecycle changes across Damage Intelligence, CROMS, Maintenance, AI services, reporting, audit, and notification workflows.

Damage Intelligence events SHALL support:

- Inspection workflow tracking.
- Image capture and evidence processing.
- AI analysis orchestration.
- Damage finding creation.
- Damage comparison completion.
- Damage case management.
- Human review workflow.
- Maintenance routing.
- Report generation.
- Auditability.
- Traceability.
- Asynchronous integration.

This specification defines logical event contracts. Physical event schemas, topics, queues, and message broker implementation SHALL be defined later in implementation-specific architecture and integration specifications.

---

# Purpose

The purpose of this document is to define the event model required for Damage Intelligence.

This specification SHALL guide:

- Backend event design.
- Domain event implementation.
- Integration event implementation.
- Message broker design.
- API and event alignment.
- CROMS integration.
- Maintenance integration.
- AI service orchestration.
- Audit logging.
- Notifications.
- Test case generation.
- Traceability.

---

# Scope

## In Scope

This event specification covers:

- Event principles.
- Event categories.
- Event envelope.
- Event naming conventions.
- Inspection events.
- Image events.
- AI analysis events.
- Damage finding events.
- Damage comparison events.
- Damage case events.
- Review decision events.
- Repair estimate events.
- Maintenance routing events.
- Report events.
- Audit and notification implications.
- Event reliability requirements.

## Out of Scope

This specification does not define:

- Physical broker infrastructure.
- Final Kafka or RabbitMQ topic names.
- Final event serialization schema.
- Final retry policy implementation.
- Full notification template content.
- Full OpenAPI callbacks.
- Full data warehouse pipeline design.
- Full external insurance integration.

---

# Event Principles

Damage Intelligence events SHALL follow these principles:

1. Business Meaning
2. Clear Ownership
3. Traceability
4. Auditability
5. Tenant Isolation
6. Idempotent Consumption
7. Versioning
8. Backward Compatibility Where Practical
9. Secure Payloads
10. No Sensitive Data Leakage

Events SHALL describe something that has happened, not a command to do something.

---

# Event Types

Damage Intelligence SHALL support two logical event types.

## Domain Events

Domain events represent internal business facts within Damage Intelligence.

Examples:

- InspectionSessionCreated
- DamageFindingCreated
- DamageCaseClosed

## Integration Events

Integration events are published for other bounded contexts or external systems.

Examples:

- DamageCaseRoutedToMaintenance
- RentalDamageSummaryUpdated
- DamageReportGenerated

The same business fact MAY produce both an internal domain event and an external integration event.

---

# Event Naming Convention

Event names SHALL use past-tense business language.

Examples:

```text
InspectionSessionCreated
InspectionSubmitted
AIAnalysisCompleted
DamageCaseCreated
DamageCaseRoutedToMaintenance
```

Event names SHALL NOT use vague names such as:

```text
ProcessData
UpdateRecord
HandleDamage
DoAnalysis
```

---

# Standard Event Envelope

All events SHOULD use a standard envelope.

```json
{
  "eventId": "EVT-DI-000001",
  "eventType": "InspectionSessionCreated",
  "eventVersion": "1.0.0",
  "occurredAt": "2026-06-27T00:00:00Z",
  "publishedAt": "2026-06-27T00:00:01Z",
  "tenantId": "TENANT-000001",
  "correlationId": "CORR-000001",
  "causationId": "CMD-000001",
  "source": "DamageIntelligence",
  "actor": {
    "actorType": "User",
    "actorId": "USR-000001"
  },
  "subject": {
    "subjectType": "InspectionSession",
    "subjectId": "INS-DI-000001"
  },
  "data": {},
  "metadata": {
    "traceId": "TRACE-000001"
  }
}
```

---

# Required Event Envelope Fields

| Field | Required | Description |
|------|----------|-------------|
| eventId | Yes | Unique event identifier |
| eventType | Yes | Event name |
| eventVersion | Yes | Event contract version |
| occurredAt | Yes | Time the business event occurred |
| publishedAt | Yes | Time the event was published |
| tenantId | Yes | Tenant identifier |
| correlationId | Yes | End-to-end correlation identifier |
| causationId | Recommended | Command or event that caused this event |
| source | Yes | Publishing bounded context or service |
| actor | Recommended | User or system actor |
| subject | Yes | Primary business object |
| data | Yes | Event payload |
| metadata | Optional | Additional tracing or processing metadata |

---

# Event Versioning

Events SHALL be versioned.

Versioning rules:

- Additive changes MAY remain in the same major version.
- Breaking changes SHALL require a new major version.
- Consumers SHALL ignore unknown fields.
- Deprecated fields SHOULD remain available during migration.
- Event versions SHALL be documented.

---

# Event Security

Events SHALL comply with GEES security standards.

Events SHALL NOT include:

- Unrestricted image URLs.
- Access tokens.
- Passwords.
- Secrets.
- Full customer personal data unless explicitly approved.
- Sensitive financial details unless required and authorized.

Events SHOULD include references to protected resources rather than embedding sensitive content.

---

# Event Reliability Requirements

The event system SHOULD support:

- At-least-once delivery.
- Idempotent consumers.
- Retry handling.
- Dead-letter handling.
- Correlation IDs.
- Event audit logging.
- Failure monitoring.
- Replay where practical.

Consumers SHALL be designed to tolerate duplicate events.

---

# Event Categories

Damage Intelligence events are grouped into the following categories.

| Category | Purpose |
|---------|---------|
| Inspection Events | Inspection session lifecycle |
| Image Events | Image upload, quality, evidence lifecycle |
| AI Events | AI analysis lifecycle |
| Damage Finding Events | Damage finding lifecycle |
| Comparison Events | Historical comparison lifecycle |
| Damage Case Events | Damage case lifecycle |
| Review Events | Human review decisions |
| Repair Estimate Events | Advisory estimate lifecycle |
| Maintenance Routing Events | Handoff to Maintenance |
| Report Events | Damage report generation |
| Integration Events | CROMS and Maintenance coordination |

---

# Inspection Events

## InspectionSessionCreated

### Trigger

Published when a new inspection session is created.

### Primary Consumers

- CROMS
- Mobile Capture App
- Notification Service
- Audit Service
- Reporting Service

### Payload

```json
{
  "inspectionSessionId": "INS-DI-000001",
  "inspectionType": "CheckOut",
  "vehicleId": "VEH-000001",
  "rentalAgreementId": "RA-000001",
  "workOrderId": null,
  "branchId": "BR-000001",
  "status": "Draft",
  "captureTemplateId": "TPL-DI-000001"
}
```

---

## InspectionSessionStarted

### Trigger

Published when an inspection session is started by a user.

### Payload

```json
{
  "inspectionSessionId": "INS-DI-000001",
  "inspectionType": "CheckOut",
  "vehicleId": "VEH-000001",
  "startedBy": "USR-000001",
  "startedAt": "2026-06-27T00:00:00Z",
  "status": "Started"
}
```

---

## InspectionSubmitted

### Trigger

Published when an inspection session is submitted for processing.

### Payload

```json
{
  "inspectionSessionId": "INS-DI-000001",
  "inspectionType": "CheckIn",
  "vehicleId": "VEH-000001",
  "rentalAgreementId": "RA-000001",
  "submittedBy": "USR-000001",
  "submittedAt": "2026-06-27T00:00:00Z",
  "imageCount": 10,
  "status": "Submitted"
}
```

---

## InspectionCompleted

### Trigger

Published when inspection processing and required review are completed.

### Payload

```json
{
  "inspectionSessionId": "INS-DI-000001",
  "vehicleId": "VEH-000001",
  "rentalAgreementId": "RA-000001",
  "completedAt": "2026-06-27T00:00:00Z",
  "damageFindingsCount": 2,
  "damageCasesCount": 1,
  "status": "Completed"
}
```

---

## InspectionClosed

### Trigger

Published when an inspection session is closed and archived.

### Payload

```json
{
  "inspectionSessionId": "INS-DI-000001",
  "vehicleId": "VEH-000001",
  "closedAt": "2026-06-27T00:00:00Z",
  "closedBy": "USR-000001",
  "status": "Closed"
}
```

---

# Image Events

## InspectionImageRegistered

### Trigger

Published when an inspection image is registered after upload.

### Payload

```json
{
  "imageId": "IMG-DI-000001",
  "inspectionSessionId": "INS-DI-000001",
  "vehicleId": "VEH-000001",
  "capturePositionId": "CAPTURE-FRONT",
  "contentType": "image/jpeg",
  "storageReference": "blob://damage/INS-DI-000001/front.jpg",
  "capturedAt": "2026-06-27T00:00:00Z",
  "registeredAt": "2026-06-27T00:00:05Z"
}
```

---

## ImageQualityChecked

### Trigger

Published when automated or manual image quality validation is completed.

### Payload

```json
{
  "imageId": "IMG-DI-000001",
  "inspectionSessionId": "INS-DI-000001",
  "qualityStatus": "Passed",
  "qualityScore": 0.91,
  "failureReasons": [],
  "checkedAt": "2026-06-27T00:00:00Z"
}
```

---

## ImageQualityFailed

### Trigger

Published when an image fails required quality checks.

### Payload

```json
{
  "imageId": "IMG-DI-000001",
  "inspectionSessionId": "INS-DI-000001",
  "capturePositionId": "CAPTURE-FRONT",
  "qualityStatus": "Failed",
  "failureReasons": [
    "BLUR",
    "LOW_LIGHT"
  ],
  "recaptureRequired": true
}
```

---

## InspectionImageSuperseded

### Trigger

Published when a captured image is replaced by a retake.

### Payload

```json
{
  "originalImageId": "IMG-DI-000001",
  "newImageId": "IMG-DI-000002",
  "inspectionSessionId": "INS-DI-000001",
  "capturePositionId": "CAPTURE-FRONT",
  "reason": "RetakeDueToBlur"
}
```

---

# AI Analysis Events

## AIAnalysisRequested

### Trigger

Published when AI damage analysis is requested.

### Payload

```json
{
  "analysisId": "AIA-DI-000001",
  "inspectionSessionId": "INS-DI-000001",
  "vehicleId": "VEH-000001",
  "imageIds": [
    "IMG-DI-000001",
    "IMG-DI-000002"
  ],
  "analysisType": "DamageDetection",
  "requestedAt": "2026-06-27T00:00:00Z"
}
```

---

## AIAnalysisStarted

### Trigger

Published when AI analysis starts.

### Payload

```json
{
  "analysisId": "AIA-DI-000001",
  "inspectionSessionId": "INS-DI-000001",
  "startedAt": "2026-06-27T00:00:00Z",
  "engineType": "HybridVision"
}
```

---

## AIAnalysisCompleted

### Trigger

Published when AI analysis completes successfully.

### Payload

```json
{
  "analysisId": "AIA-DI-000001",
  "inspectionSessionId": "INS-DI-000001",
  "completedAt": "2026-06-27T00:00:15Z",
  "findingsCount": 3,
  "engineType": "HybridVision",
  "modelVersion": "TBD"
}
```

---

## AIAnalysisFailed

### Trigger

Published when AI analysis fails.

### Payload

```json
{
  "analysisId": "AIA-DI-000001",
  "inspectionSessionId": "INS-DI-000001",
  "failedAt": "2026-06-27T00:00:15Z",
  "failureCode": "AI_TIMEOUT",
  "retryable": true
}
```

---

# Damage Finding Events

## DamageFindingCreated

### Trigger

Published when a damage finding is created from AI, human input, or system comparison.

### Payload

```json
{
  "damageFindingId": "DMF-DI-000001",
  "inspectionSessionId": "INS-DI-000001",
  "vehicleId": "VEH-000001",
  "damageType": "SCRATCH",
  "vehicleArea": "REAR_BUMPER",
  "severity": "MINOR",
  "source": "AI",
  "confidenceScore": 0.87,
  "status": "Generated"
}
```

---

## DamageFindingUpdated

### Trigger

Published when a damage finding is updated by an authorized user or system workflow.

### Payload

```json
{
  "damageFindingId": "DMF-DI-000001",
  "updatedFields": [
    "severity",
    "vehicleArea"
  ],
  "previousStatus": "PendingReview",
  "newStatus": "Edited",
  "updatedBy": "USR-000001",
  "updatedAt": "2026-06-27T00:00:00Z"
}
```

---

## DamageFindingRejected

### Trigger

Published when a damage finding is rejected during review.

### Payload

```json
{
  "damageFindingId": "DMF-DI-000001",
  "inspectionSessionId": "INS-DI-000001",
  "rejectedBy": "USR-000001",
  "rejectionReason": "Image artifact, no visible damage",
  "rejectedAt": "2026-06-27T00:00:00Z"
}
```

---

## DamageFindingConfirmed

### Trigger

Published when a damage finding is confirmed by an authorized reviewer.

### Payload

```json
{
  "damageFindingId": "DMF-DI-000001",
  "inspectionSessionId": "INS-DI-000001",
  "vehicleId": "VEH-000001",
  "damageType": "DENT",
  "vehicleArea": "LEFT_REAR_DOOR",
  "severity": "MODERATE",
  "confirmedBy": "USR-000001",
  "confirmedAt": "2026-06-27T00:00:00Z"
}
```

---

# Damage Comparison Events

## DamageComparisonRequested

### Trigger

Published when historical damage comparison is requested.

### Payload

```json
{
  "comparisonId": "CMP-DI-000001",
  "inspectionSessionId": "INS-DI-000001",
  "vehicleId": "VEH-000001",
  "baselineSelectionMode": "Auto",
  "requestedAt": "2026-06-27T00:00:00Z"
}
```

---

## DamageComparisonCompleted

### Trigger

Published when damage comparison completes.

### Payload

```json
{
  "comparisonId": "CMP-DI-000001",
  "inspectionSessionId": "INS-DI-000001",
  "vehicleId": "VEH-000001",
  "baselineInspectionSessionId": "INS-DI-000000",
  "comparisonOutcomeSummary": {
    "new": 1,
    "preExisting": 1,
    "changed": 0,
    "repaired": 0,
    "uncertain": 1,
    "notComparable": 0
  },
  "completedAt": "2026-06-27T00:00:00Z"
}
```

---

## DamageComparisonFailed

### Trigger

Published when damage comparison fails.

### Payload

```json
{
  "comparisonId": "CMP-DI-000001",
  "inspectionSessionId": "INS-DI-000001",
  "vehicleId": "VEH-000001",
  "failureCode": "BASELINE_RETRIEVAL_FAILED",
  "retryable": true,
  "failedAt": "2026-06-27T00:00:00Z"
}
```

---

## NewDamageCandidateIdentified

### Trigger

Published when comparison identifies candidate new damage.

### Payload

```json
{
  "comparisonId": "CMP-DI-000001",
  "damageFindingId": "DMF-DI-000001",
  "vehicleId": "VEH-000001",
  "damageType": "DENT",
  "vehicleArea": "LEFT_REAR_DOOR",
  "comparisonOutcome": "New",
  "confidenceScore": 0.84,
  "reviewRequired": true"
}
```

---

# Damage Case Events

## DamageCaseCreated

### Trigger

Published when a damage case is created.

### Payload

```json
{
  "damageCaseId": "DMC-DI-000001",
  "inspectionSessionId": "INS-DI-000001",
  "vehicleId": "VEH-000001",
  "rentalAgreementId": "RA-000001",
  "damageFindingIds": [
    "DMF-DI-000001"
  ],
  "caseReason": "PotentialNewDamage",
  "caseStatus": "Created",
  "createdAt": "2026-06-27T00:00:00Z"
}
```

---

## DamageCaseUpdated

### Trigger

Published when a damage case is updated.

### Payload

```json
{
  "damageCaseId": "DMC-DI-000001",
  "previousStatus": "InReview",
  "newStatus": "Confirmed",
  "updatedBy": "USR-000001",
  "updatedAt": "2026-06-27T00:00:00Z"
}
```

---

## DamageCaseConfirmed

### Trigger

Published when a damage case is confirmed.

### Payload

```json
{
  "damageCaseId": "DMC-DI-000001",
  "vehicleId": "VEH-000001",
  "rentalAgreementId": "RA-000001",
  "severity": "MODERATE",
  "confirmedBy": "USR-000001",
  "confirmedAt": "2026-06-27T00:00:00Z"
}
```

---

## DamageCaseRejected

### Trigger

Published when a damage case is rejected.

### Payload

```json
{
  "damageCaseId": "DMC-DI-000001",
  "rejectedBy": "USR-000001",
  "rejectionReason": "Finding confirmed as pre-existing damage",
  "rejectedAt": "2026-06-27T00:00:00Z"
}
```

---

## DamageCaseClosed

### Trigger

Published when a damage case is closed.

### Payload

```json
{
  "damageCaseId": "DMC-DI-000001",
  "vehicleId": "VEH-000001",
  "closedBy": "USR-000001",
  "closureReason": "Resolved",
  "closedAt": "2026-06-27T00:00:00Z"
}
```

---

# Review Events

## ReviewDecisionRecorded

### Trigger

Published when an authorized user records a review decision.

### Payload

```json
{
  "reviewDecisionId": "REV-DI-000001",
  "targetType": "DamageFinding",
  "targetId": "DMF-DI-000001",
  "decision": "Confirmed",
  "reviewerId": "USR-000001",
  "reviewedAt": "2026-06-27T00:00:00Z"
}
```

---

## ReviewEscalated

### Trigger

Published when a review is escalated.

### Payload

```json
{
  "reviewDecisionId": "REV-DI-000002",
  "targetType": "DamageCase",
  "targetId": "DMC-DI-000001",
  "escalatedBy": "USR-000001",
  "escalationReason": "Customer dispute risk",
  "escalatedAt": "2026-06-27T00:00:00Z"
}
```

---

## AdditionalEvidenceRequested

### Trigger

Published when reviewer requests additional evidence.

### Payload

```json
{
  "reviewDecisionId": "REV-DI-000003",
  "targetType": "DamageCase",
  "targetId": "DMC-DI-000001",
  "requestedBy": "USR-000001",
  "reason": "Close-up image required",
  "requestedAt": "2026-06-27T00:00:00Z"
}
```

---

# Repair Estimate Events

## RepairEstimateGenerated

### Trigger

Published when an advisory repair estimate is generated.

### Payload

```json
{
  "estimateId": "EST-DI-000001",
  "damageCaseId": "DMC-DI-000001",
  "damageFindingId": "DMF-DI-000001",
  "estimateType": "AdvisoryEstimate",
  "estimatedCostMin": 350,
  "estimatedCostMax": 750,
  "currency": "SAR",
  "confidenceScore": 0.72,
  "status": "Generated"
}
```

---

## RepairEstimateReviewed

### Trigger

Published when an advisory estimate is reviewed by an authorized user.

### Payload

```json
{
  "estimateId": "EST-DI-000001",
  "damageCaseId": "DMC-DI-000001",
  "decision": "Accepted",
  "reviewedBy": "USR-000001",
  "reviewedAt": "2026-06-27T00:00:00Z"
}
```

---

## RepairEstimateSuperseded

### Trigger

Published when a Maintenance or Finance actual cost supersedes advisory estimate.

### Payload

```json
{
  "estimateId": "EST-DI-000001",
  "damageCaseId": "DMC-DI-000001",
  "supersededBy": "ActualRepairCost",
  "workOrderId": "WO-000001",
  "supersededAt": "2026-06-27T00:00:00Z"
}
```

---

# Maintenance Routing Events

## DamageCaseRoutedToMaintenance

### Trigger

Published when a confirmed or repair-required damage case is routed to Maintenance.

### Payload

```json
{
  "damageCaseId": "DMC-DI-000001",
  "vehicleId": "VEH-000001",
  "maintenanceRequestId": "MREQ-DI-000001",
  "routingReason": "RepairRequired",
  "severity": "MODERATE",
  "routedBy": "USR-000001",
  "routedAt": "2026-06-27T00:00:00Z"
}
```

---

## MaintenanceStatusReceived

### Trigger

Published when Damage Intelligence receives Maintenance status update.

### Payload

```json
{
  "damageCaseId": "DMC-DI-000001",
  "maintenanceRequestId": "MREQ-DI-000001",
  "workOrderId": "WO-000001",
  "maintenanceStatus": "WorkOrderCreated",
  "receivedAt": "2026-06-27T00:00:00Z"
}
```

---

## RepairCompletedReceived

### Trigger

Published when Maintenance reports repair completion.

### Payload

```json
{
  "damageCaseId": "DMC-DI-000001",
  "workOrderId": "WO-000001",
  "repairCompletedAt": "2026-06-27T00:00:00Z",
  "actualRepairCostReference": "FIN-COST-000001"
}
```

---

# Report Events

## DamageReportRequested

### Trigger

Published when a damage report generation is requested.

### Payload

```json
{
  "reportId": "RPT-DI-000001",
  "reportType": "DamageCaseReport",
  "damageCaseId": "DMC-DI-000001",
  "requestedBy": "USR-000001",
  "requestedAt": "2026-06-27T00:00:00Z"
}
```

---

## DamageReportGenerated

### Trigger

Published when a damage report is generated successfully.

### Payload

```json
{
  "reportId": "RPT-DI-000001",
  "reportType": "DamageCaseReport",
  "damageCaseId": "DMC-DI-000001",
  "storageReference": "blob://damage-reports/RPT-DI-000001.pdf",
  "generatedAt": "2026-06-27T00:00:00Z"
}
```

---

## DamageReportGenerationFailed

### Trigger

Published when report generation fails.

### Payload

```json
{
  "reportId": "RPT-DI-000001",
  "reportType": "DamageCaseReport",
  "damageCaseId": "DMC-DI-000001",
  "failureCode": "REPORT_RENDER_FAILED",
  "retryable": true,
  "failedAt": "2026-06-27T00:00:00Z"
}
```

---

# CROMS Integration Events

## CROMSCheckOutInspectionRequested

### Trigger

Published or received when CROMS requests a check-out inspection.

### Payload

```json
{
  "rentalAgreementId": "RA-000001",
  "vehicleId": "VEH-000001",
  "customerId": "CUS-000001",
  "branchId": "BR-000001",
  "requestedAt": "2026-06-27T00:00:00Z"
}
```

---

## CROMSCheckInInspectionRequested

### Trigger

Published or received when CROMS requests a return inspection.

### Payload

```json
{
  "rentalAgreementId": "RA-000001",
  "vehicleId": "VEH-000001",
  "customerId": "CUS-000001",
  "branchId": "BR-000001",
  "requestedAt": "2026-06-27T00:00:00Z"
}
```

---

## RentalDamageSummaryUpdated

### Trigger

Published when Damage Intelligence updates CROMS-facing rental damage summary.

### Payload

```json
{
  "rentalAgreementId": "RA-000001",
  "vehicleId": "VEH-000001",
  "inspectionSessionId": "INS-DI-000001",
  "damageCasesCount": 1,
  "newDamageCount": 1,
  "pendingReviewCount": 0,
  "maintenanceRequired": true,
  "updatedAt": "2026-06-27T00:00:00Z"
}
```

---

# Notification Event Candidates

The following events MAY trigger notifications:

| Event | Possible Notification |
|------|------------------------|
| InspectionSessionCreated | Inspection assigned |
| ImageQualityFailed | Recapture required |
| AIAnalysisCompleted | AI findings ready |
| DamageCaseCreated | Damage case created |
| ReviewDecisionRecorded | Review completed |
| ReviewEscalated | Escalation required |
| AdditionalEvidenceRequested | Additional evidence required |
| DamageCaseRoutedToMaintenance | Maintenance handoff created |
| DamageReportGenerated | Report available |
| IntegrationFailureDetected | Integration failure requires attention |

Notification templates SHALL be defined separately.

---

# Event Audit Requirements

Every published event SHOULD be auditable.

Audit SHOULD record:

- Event ID
- Event type
- Event version
- Tenant ID
- Correlation ID
- Publishing service
- Subject type
- Subject ID
- Published timestamp
- Delivery status where available

---

# Idempotency Requirements

Event consumers SHALL be idempotent.

Consumers SHOULD use:

- eventId
- subjectId
- eventType
- eventVersion
- correlationId

Duplicate events SHALL NOT create duplicate business actions.

---

# Event Ordering

The system SHOULD NOT rely exclusively on strict global event ordering.

Where order matters, consumers SHOULD use:

- occurredAt
- aggregate version
- subject ID
- lifecycle state validation

---

# Event Failure Handling

Event processing SHOULD support:

- Retry policy.
- Dead-letter queue.
- Failure alerting.
- Manual replay where approved.
- Correlation-based troubleshooting.

Failures SHALL NOT silently disappear.

---

# Event Payload Rules

Event payloads SHALL:

- Include enough data for consumers to understand the event.
- Avoid unnecessary sensitive data.
- Use references for protected resources.
- Include tenant ID in the envelope.
- Include correlation ID in the envelope.
- Preserve event version.
- Use stable identifiers.

---

# Event Traceability

Events SHALL support traceability to:

- Requirements.
- API operations.
- Domain objects.
- Audit records.
- User actions.
- Integration requests.
- AI analysis runs.
- Reports.

---

# Event to Requirement Mapping

| Event Category | Related Requirement Area |
|---------------|--------------------------|
| Inspection Events | Inspection Workflow |
| Image Events | Vehicle Capture Standards |
| AI Events | AI Damage Detection |
| Comparison Events | Damage Comparison |
| Damage Case Events | Domain Model |
| Review Events | Human Review |
| Repair Estimate Events | Repair Cost Estimation |
| Maintenance Routing Events | Maintenance Integration |
| CROMS Events | CROMS Integration |
| Report Events | Evidence and Reporting |

---

# Normative Requirements

## Requirement

ID: REQ-DI-1200

Title:
Damage Intelligence Events

Statement:
Damage Intelligence SHALL define governed domain and integration events for significant lifecycle changes.

Priority:
Critical

Verification:
Architecture Review

---

## Requirement

ID: REQ-DI-1201

Title:
Standard Event Envelope

Statement:
Damage Intelligence events SHOULD use a standard event envelope containing event ID, event type, version, tenant ID, correlation ID, source, subject, and payload.

Priority:
High

Verification:
Event Contract Review

---

## Requirement

ID: REQ-DI-1202

Title:
Event Versioning

Statement:
Damage Intelligence events SHALL be versioned.

Priority:
Critical

Verification:
Event Contract Review

---

## Requirement

ID: REQ-DI-1203

Title:
Tenant Isolation in Events

Statement:
Damage Intelligence events SHALL preserve tenant isolation and include tenant context.

Priority:
Critical

Verification:
Security Review

---

## Requirement

ID: REQ-DI-1204

Title:
Secure Event Payloads

Statement:
Damage Intelligence events SHALL NOT expose secrets, unrestricted image URLs, access tokens, or unauthorized sensitive data.

Priority:
Critical

Verification:
Security Review

---

## Requirement

ID: REQ-DI-1205

Title:
Inspection Events

Statement:
Damage Intelligence SHALL publish events for significant inspection lifecycle changes.

Priority:
High

Verification:
Event Test

---

## Requirement

ID: REQ-DI-1206

Title:
Image Events

Statement:
Damage Intelligence SHALL publish events for significant image registration, quality, and evidence lifecycle changes.

Priority:
High

Verification:
Event Test

---

## Requirement

ID: REQ-DI-1207

Title:
AI Analysis Events

Statement:
Damage Intelligence SHALL publish events for AI analysis request, completion, and failure.

Priority:
High

Verification:
Event Test

---

## Requirement

ID: REQ-DI-1208

Title:
Damage Finding Events

Statement:
Damage Intelligence SHALL publish events for significant damage finding lifecycle changes.

Priority:
High

Verification:
Event Test

---

## Requirement

ID: REQ-DI-1209

Title:
Damage Comparison Events

Statement:
Damage Intelligence SHALL publish events for damage comparison request, completion, and failure.

Priority:
High

Verification:
Event Test

---

## Requirement

ID: REQ-DI-1210

Title:
Damage Case Events

Statement:
Damage Intelligence SHALL publish events for significant damage case lifecycle changes.

Priority:
Critical

Verification:
Event Test

---

## Requirement

ID: REQ-DI-1211

Title:
Review Events

Statement:
Damage Intelligence SHALL publish events for authorized review decisions and escalations.

Priority:
High

Verification:
Event Test

---

## Requirement

ID: REQ-DI-1212

Title:
Maintenance Routing Events

Statement:
Damage Intelligence SHALL publish integration events when damage cases are routed to Maintenance or Maintenance status is received.

Priority:
High

Verification:
Integration Test

---

## Requirement

ID: REQ-DI-1213

Title:
CROMS Integration Events

Statement:
Damage Intelligence SHALL support events or integration contracts for CROMS check-out, check-in, and rental damage summary workflows.

Priority:
Critical

Verification:
Integration Test

---

## Requirement

ID: REQ-DI-1214

Title:
Event Auditability

Statement:
Damage Intelligence event publishing and processing SHOULD be auditable.

Priority:
High

Verification:
Audit Review

---

## Requirement

ID: REQ-DI-1215

Title:
Idempotent Event Consumption

Statement:
Damage Intelligence event consumers SHALL tolerate duplicate event delivery.

Priority:
High

Verification:
Reliability Test

---

## Requirement

ID: REQ-DI-1216

Title:
Event Failure Handling

Statement:
Damage Intelligence event processing SHOULD support retry, dead-letter handling, alerting, and replay where approved.

Priority:
High

Verification:
Reliability Review

---

# Business Rules

## BR-DI-0800 — Events Represent Facts

Damage Intelligence events SHALL represent business facts that already occurred.

---

## BR-DI-0801 — Event Consumers Must Be Idempotent

Duplicate events SHALL NOT create duplicate damage cases, duplicate maintenance requests, or duplicate reports.

---

## BR-DI-0802 — Events Must Preserve Tenant Context

Events SHALL include tenant context and SHALL NOT cause cross-tenant data exposure.

---

## BR-DI-0803 — Sensitive Data Must Be Protected

Events SHALL use protected references instead of embedding sensitive image, customer, or financial data.

---

## BR-DI-0804 — Significant Lifecycle Changes Should Publish Events

Significant inspection, finding, comparison, case, review, estimate, routing, and report changes SHOULD publish events.

---

# AI Implementation Contract

AI development agents SHALL:

- Treat this document as the authoritative event specification for Damage Intelligence.
- Preserve all event names and requirement IDs.
- Preserve the standard event envelope.
- Preserve event security and tenant isolation requirements.
- Not include unrestricted image URLs, tokens, secrets, or unauthorized sensitive data in event payloads.
- Generate future event schemas, topics, consumers, tests, and integration contracts consistent with this document.
- Preserve idempotency and failure handling requirements.
- Raise ambiguity where event ownership, payload fields, or consumer responsibilities are unclear.

---

# References

- DI-0004 – Damage Intelligence Inspection Workflow
- DI-0005 – AI Damage Detection
- DI-0006 – Damage Comparison
- DI-0007 – Vehicle Capture Standards
- DI-0008 – Damage Taxonomy
- DI-0009 – Severity Assessment
- DI-0010 – Repair Cost Estimation
- DI-0011 – API Specification
- DI-0012 – Domain Model
- RA-0002 – Domain-Driven Design Architecture
- GEES-0007 – Enterprise Security Standard
- GEES-0009 – Traceability Standard
- PLATFORM-0005 – GEES Core and Application Architecture

---

# Revision History

| Version | Date | Description |
|----------|------|-------------|
| 1.0.0 | 2026-06-27 | Initial Damage Intelligence Events Specification |
