---

id: DI-0012
title: Damage Intelligence Domain Model
version: 1.0.0
document_type: Product Specification
document_class: Domain Model Specification
status: Draft
classification: Internal
owner: Riyadah Technology
reviewers:

* Chief Enterprise Architect
* Product Owner
* Domain Architect
* API Architecture Lead
* AI Engineering Lead
* Security Lead
* CROMS Lead
* Maintenance Lead
  approvers: []
  created: 2026-06-27
  updated: 2026-06-27
  authoritative: true
  ai_consumable: true
  related:
* DI-0001
* DI-0002
* DI-0004
* DI-0005
* DI-0006
* DI-0007
* DI-0008
* DI-0009
* DI-0010
* DI-0011
* RA-0001
* RA-0002
* GEES-0011
* GEES-0013
* PLATFORM-0005

---

# Damage Intelligence Domain Model

## Executive Summary

This document defines the logical domain model for Damage Intelligence.

The Damage Intelligence domain model describes the core business entities, aggregates, value objects, lifecycle states, relationships, ownership boundaries, and integration references required to implement the Damage Intelligence capability.

The model supports:

* Vehicle inspection sessions.
* Inspection image evidence.
* AI damage findings.
* Human-reviewed damage findings.
* Damage comparison results.
* Damage cases.
* Severity assessment.
* Advisory repair estimation.
* CROMS integration.
* Maintenance integration.
* Auditability.
* Traceability.
* Tenant isolation.

This document is a logical domain model. It is not a physical database schema.

Physical database tables, indexes, foreign keys, and persistence design SHALL be defined later in implementation-specific data specifications.

---

# Purpose

The purpose of this document is to define the business domain structure required for Damage Intelligence.

This specification SHALL guide:

* Backend domain modeling.
* API schema design.
* Database design.
* Event design.
* UI data requirements.
* AI output mapping.
* Test case design.
* Traceability.
* Integration with CROMS and Maintenance.

---

# Scope

## In Scope

This domain model covers:

* Domain boundaries.
* Aggregates.
* Entities.
* Value objects.
* Enumerations.
* Relationships.
* Lifecycle states.
* Invariants.
* Ownership rules.
* Integration references.
* Domain events.
* Audit model implications.

## Out of Scope

This document does not define:

* Physical database schema.
* ORM implementation.
* Full OpenAPI schema.
* Full UI data binding.
* AI model internals.
* CROMS internal domain model.
* Maintenance internal domain model.
* Finance accounting model.
* Insurance claim model.

---

# Domain Boundary

Damage Intelligence is a bounded context within the GCU365 enterprise application ecosystem.

Damage Intelligence owns:

* Inspection Session
* Inspection Image
* Image Quality Result
* AI Damage Finding
* Damage Finding
* Damage Comparison
* Damage Case
* Review Decision
* Severity Assessment
* Repair Estimate
* Damage Report
* Capture Template
* Damage Taxonomy references
* Damage audit records related to this context

Damage Intelligence references, but does not own:

* Vehicle master record
* Rental Agreement
* Customer master record
* Branch master record
* Maintenance Work Order
* Finance invoice
* Insurance claim
* User identity master record

---

# Domain Context Map

```text
CROMS
  ├── Vehicle
  ├── Rental Agreement
  ├── Customer Reference
  └── Branch Context
        ↓
Damage Intelligence
  ├── Inspection Session
  ├── Inspection Image
  ├── AI Damage Finding
  ├── Damage Comparison
  ├── Damage Case
  ├── Review Decision
  ├── Severity Assessment
  ├── Repair Estimate
  └── Damage Report
        ↓
Maintenance
  ├── Maintenance Request
  ├── Work Order
  ├── Repair Status
  └── Actual Repair Cost
```

---

# Core Aggregates

Damage Intelligence SHALL define the following primary aggregates.

| Aggregate         | Purpose                                                       |
| ----------------- | ------------------------------------------------------------- |
| InspectionSession | Governs inspection workflow and evidence capture              |
| DamageFinding     | Represents detected or reported vehicle damage                |
| DamageComparison  | Represents comparison between current and historical evidence |
| DamageCase        | Manages operational damage case lifecycle                     |
| ReviewDecision    | Captures human review and approval decisions                  |
| RepairEstimate    | Manages advisory repair cost estimate lifecycle               |
| DamageReport      | Represents generated evidence/reporting output                |
| CaptureTemplate   | Defines required capture positions and rules                  |

---

# Aggregate: InspectionSession

## Description

InspectionSession is the central aggregate for vehicle condition inspection.

It represents one inspection workflow instance for a vehicle.

Examples:

* Check-out inspection.
* Check-in inspection.
* Maintenance intake inspection.
* Maintenance quality inspection.
* Ad hoc inspection.

## Ownership

Damage Intelligence owns InspectionSession.

## Key Attributes

| Attribute           | Description                                        |
| ------------------- | -------------------------------------------------- |
| inspectionSessionId | Unique inspection session identifier               |
| tenantId            | Tenant identifier                                  |
| inspectionType      | Type of inspection                                 |
| status              | Current inspection lifecycle status                |
| vehicleId           | Referenced vehicle identifier                      |
| rentalAgreementId   | Referenced rental agreement where applicable       |
| workOrderId         | Referenced maintenance work order where applicable |
| branchId            | Branch or operational location                     |
| captureTemplateId   | Capture template used                              |
| createdBy           | User who created the session                       |
| assignedTo          | User assigned to complete inspection               |
| startedAt           | Start timestamp                                    |
| submittedAt         | Submission timestamp                               |
| completedAt         | Completion timestamp                               |
| closedAt            | Closure timestamp                                  |

## Child Entities

InspectionSession MAY contain:

* InspectionImage
* ImageQualityResult
* InspectionAuditEntry
* AIAnalysisReference
* DamageFinding references
* DamageComparison references

## Lifecycle States

```text
Draft
  ↓
Started
  ↓
Capturing
  ↓
Submitted
  ↓
Analyzing
  ↓
PendingReview
  ↓
Completed
  ↓
Closed
```

## Invariants

InspectionSession SHALL enforce:

* Tenant ID is required.
* Vehicle ID is required.
* Inspection type is required.
* Capture template is required where inspection requires images.
* Required capture positions must be satisfied before submission unless authorized override exists.
* Submitted inspections SHALL preserve evidence.
* Closed inspections SHALL NOT be modified except through approved correction workflow.

---

# Aggregate: InspectionImage

## Description

InspectionImage represents one captured or uploaded inspection image.

## Ownership

InspectionImage is owned by Damage Intelligence and belongs to an InspectionSession.

## Key Attributes

| Attribute           | Description                          |
| ------------------- | ------------------------------------ |
| imageId             | Unique image identifier              |
| inspectionSessionId | Parent inspection session            |
| tenantId            | Tenant identifier                    |
| vehicleId           | Vehicle reference                    |
| capturePositionId   | Capture position                     |
| storageReference    | Secure storage reference             |
| contentType         | Image content type                   |
| fileSizeBytes       | File size                            |
| imageHash           | Hash for integrity where available   |
| capturedAt          | Capture timestamp                    |
| capturedBy          | Capture user                         |
| deviceId            | Device identifier where available    |
| gpsLocation         | Optional permitted location metadata |
| uploadStatus        | Upload state                         |
| qualityStatus       | Image quality status                 |

## Lifecycle States

```text
Created
  ↓
UploadPending
  ↓
Uploaded
  ↓
QualityCheckPending
  ↓
QualityPassed / QualityFailed
  ↓
Accepted / Rejected / Superseded
```

## Invariants

InspectionImage SHALL enforce:

* Image belongs to one InspectionSession.
* Image must have a capture position.
* Image must have secure storage reference after upload.
* Image access must be authorized.
* Approved image evidence SHALL NOT be overwritten.
* Retake SHALL create a new image record or version.

---

# Entity: ImageQualityResult

## Description

ImageQualityResult records the outcome of automated or manual image quality checks.

## Key Attributes

| Attribute                  | Description                      |
| -------------------------- | -------------------------------- |
| imageQualityResultId       | Unique result identifier         |
| imageId                    | Related image                    |
| inspectionSessionId        | Related inspection               |
| qualityStatus              | Passed, Failed, Warning, Unknown |
| blurResult                 | Blur check result                |
| brightnessResult           | Brightness check result          |
| vehiclePresenceResult      | Vehicle presence result          |
| capturePositionMatchResult | Capture position match result    |
| duplicateResult            | Duplicate image check            |
| obstructionResult          | Obstruction check                |
| qualityScore               | Numeric score where available    |
| failureReasons             | Reasons for failure              |
| checkedAt                  | Quality check timestamp          |

---

# Aggregate: DamageFinding

## Description

DamageFinding represents a detected, reported, reviewed, or confirmed damage item.

A finding MAY originate from:

* AI analysis.
* Human capture.
* Manual review.
* Imported historical record.
* System comparison.

## Ownership

Damage Intelligence owns DamageFinding.

## Key Attributes

| Attribute           | Description                                                   |
| ------------------- | ------------------------------------------------------------- |
| damageFindingId     | Unique finding identifier                                     |
| tenantId            | Tenant identifier                                             |
| inspectionSessionId | Related inspection session                                    |
| vehicleId           | Vehicle reference                                             |
| rentalAgreementId   | Rental agreement reference where applicable                   |
| damageType          | Taxonomy damage type                                          |
| damageCategory      | Taxonomy damage category                                      |
| vehicleArea         | Affected vehicle area                                         |
| severity            | Severity label                                                |
| source              | AI, Human, Imported, System, Hybrid                           |
| description         | Damage description                                            |
| confidenceScore     | Confidence where applicable                                   |
| status              | Finding lifecycle state                                       |
| reviewStatus        | Review status                                                 |
| comparisonOutcome   | New, PreExisting, Changed, Repaired, Uncertain, NotComparable |
| repairRelevance     | Repair relevance                                              |
| evidenceImageIds    | Related evidence images                                       |
| createdAt           | Creation timestamp                                            |
| updatedAt           | Last update timestamp                                         |

## Lifecycle States

```text
Generated
  ↓
PendingReview
  ↓
Confirmed / Edited / Rejected / Escalated
  ↓
Closed
```

## Invariants

DamageFinding SHALL enforce:

* Every finding must reference a vehicle.
* Every finding must reference evidence where practical.
* AI-generated findings must remain advisory until reviewed where review is required.
* Damage type SHALL use approved taxonomy.
* Vehicle area SHALL use approved taxonomy or unknown value.
* Severity SHALL use approved severity labels.
* Review changes SHALL be audited.

---

# Entity: AIDamageFinding

## Description

AIDamageFinding represents AI-generated detection output before or during human review.

AIDamageFinding MAY be mapped to a general DamageFinding.

## Key Attributes

| Attribute                 | Description                         |
| ------------------------- | ----------------------------------- |
| aiFindingId               | Unique AI finding identifier        |
| damageFindingId           | Related damage finding where mapped |
| analysisId                | AI analysis reference               |
| imageId                   | Evidence image                      |
| damageType                | AI suggested damage type            |
| vehicleArea               | AI suggested vehicle area           |
| severitySuggestion        | AI suggested severity               |
| confidenceScore           | AI confidence                       |
| boundingBox               | Detected region where available     |
| segmentationMaskReference | Mask reference where available      |
| explanation               | AI explanation                      |
| modelVersion              | AI model/version                    |
| uncertaintyReasons        | AI uncertainty reasons              |
| createdAt                 | AI output timestamp                 |

## Invariants

AIDamageFinding SHALL enforce:

* AI finding must identify evidence image.
* AI confidence must be stored where available.
* AI model or engine reference should be stored.
* AI output SHALL NOT become a final liability decision.

---

# Aggregate: DamageComparison

## Description

DamageComparison represents comparison between current inspection evidence and historical evidence.

## Ownership

Damage Intelligence owns DamageComparison.

## Key Attributes

| Attribute                   | Description                                |
| --------------------------- | ------------------------------------------ |
| comparisonId                | Unique comparison identifier               |
| tenantId                    | Tenant identifier                          |
| currentInspectionSessionId  | Current inspection                         |
| baselineInspectionSessionId | Historical baseline where available        |
| currentFindingId            | Current finding                            |
| historicalFindingId         | Matched historical finding where available |
| vehicleId                   | Vehicle reference                          |
| comparisonOutcome           | Outcome classification                     |
| confidenceScore             | Comparison confidence                      |
| baselineSelectionReason     | Why baseline was selected                  |
| explanation                 | Comparison explanation                     |
| reviewRecommendation        | Review recommendation                      |
| evidenceReferences          | Current and historical evidence references |
| status                      | Comparison status                          |
| createdAt                   | Creation timestamp                         |

## Lifecycle States

```text
Requested
  ↓
EvidenceLoaded
  ↓
Compared
  ↓
PendingReview
  ↓
Confirmed / Edited / Rejected
  ↓
Closed
```

## Invariants

DamageComparison SHALL enforce:

* Current inspection must be identified.
* Selected baseline must be recorded where available.
* Absence of baseline must be recorded.
* Missing history SHALL NOT prove new damage.
* Comparison outcome SHALL use approved values.
* Comparison evidence references SHALL be preserved.

---

# Aggregate: DamageCase

## Description

DamageCase represents an operational case created from one or more damage findings.

A DamageCase is used for review, decisioning, maintenance routing, reporting, and dispute support.

## Ownership

Damage Intelligence owns DamageCase.

## Key Attributes

| Attribute                | Description                                 |
| ------------------------ | ------------------------------------------- |
| damageCaseId             | Unique damage case identifier               |
| tenantId                 | Tenant identifier                           |
| vehicleId                | Vehicle reference                           |
| rentalAgreementId        | Rental agreement reference where applicable |
| inspectionSessionId      | Related inspection                          |
| damageFindingIds         | Related findings                            |
| caseStatus               | Damage case lifecycle status                |
| caseReason               | Reason for case creation                    |
| severity                 | Case-level severity                         |
| reviewStatus             | Review status                               |
| maintenanceRoutingStatus | Maintenance routing status                  |
| repairEstimateId         | Related advisory repair estimate            |
| assignedTo               | Reviewer or owner                           |
| createdAt                | Creation timestamp                          |
| closedAt                 | Closure timestamp                           |

## Lifecycle States

```text
Draft
  ↓
Created
  ↓
InReview
  ↓
Confirmed / Rejected / Escalated
  ↓
RoutedToMaintenance
  ↓
Resolved
  ↓
Closed
  ↓
Archived
```

## Invariants

DamageCase SHALL enforce:

* Damage case must reference at least one damage finding.
* Damage case must reference a vehicle.
* Customer-impacting cases SHALL require human review.
* Repair-required cases SHOULD be routable to Maintenance.
* Case closure SHALL preserve evidence and decisions.
* Case status changes SHALL be audited.

---

# Aggregate: ReviewDecision

## Description

ReviewDecision captures authorized human decisions on findings, comparisons, cases, severity, or estimates.

## Ownership

Damage Intelligence owns ReviewDecision.

## Key Attributes

| Attribute        | Description                                   |
| ---------------- | --------------------------------------------- |
| reviewDecisionId | Unique review decision identifier             |
| tenantId         | Tenant identifier                             |
| targetType       | Finding, Comparison, Case, Severity, Estimate |
| targetId         | Reviewed object identifier                    |
| decision         | Review decision                               |
| reviewerId       | Authorized reviewer                           |
| notes            | Review notes                                  |
| previousValue    | Previous value where applicable               |
| newValue         | New value where applicable                    |
| createdAt        | Review timestamp                              |

## Review Decision Values

Examples:

* Confirmed
* Edited
* Rejected
* Escalated
* AdditionalEvidenceRequired
* Deferred
* Closed

## Invariants

ReviewDecision SHALL enforce:

* Reviewer must be authorized.
* Decision must target a valid object.
* Decision must be immutable after recording except through approved correction workflow.
* Review notes MAY be required by policy.
* Review decision SHALL be audited.

---

# Aggregate: RepairEstimate

## Description

RepairEstimate represents an advisory estimate of repair cost, labor, parts, and repair category.

## Ownership

Damage Intelligence owns advisory repair estimates.

Maintenance or Finance owns final actual repair cost.

## Key Attributes

| Attribute         | Description                         |
| ----------------- | ----------------------------------- |
| estimateId        | Unique estimate identifier          |
| tenantId          | Tenant identifier                   |
| damageCaseId      | Related damage case                 |
| damageFindingId   | Related damage finding              |
| estimateType      | Advisory, AI, Reviewer, Maintenance |
| repairCategory    | Repair category                     |
| estimatedLaborMin | Minimum estimated labor             |
| estimatedLaborMax | Maximum estimated labor             |
| estimatedCostMin  | Minimum estimated cost              |
| estimatedCostMax  | Maximum estimated cost              |
| currency          | Currency                            |
| confidenceScore   | Estimate confidence                 |
| assumptions       | Estimate assumptions                |
| exclusions        | Estimate exclusions                 |
| status            | Estimate status                     |
| reviewedBy        | Reviewer where applicable           |
| createdAt         | Creation timestamp                  |

## Lifecycle States

```text
Draft
  ↓
Generated
  ↓
PendingReview
  ↓
Reviewed
  ↓
Accepted / Edited / Rejected / Escalated
  ↓
RoutedToMaintenance
  ↓
Superseded
  ↓
Closed
```

## Invariants

RepairEstimate SHALL enforce:

* Estimate must be linked to a damage case or damage finding.
* Estimate must include currency where cost is present.
* Estimate SHALL be advisory unless approved by authorized workflow.
* Estimate SHALL NOT determine final customer charge.
* Estimate changes SHALL be audited.

---

# Aggregate: DamageReport

## Description

DamageReport represents a generated report containing inspection evidence, damage findings, comparison results, review decisions, and supporting audit references.

## Ownership

Damage Intelligence owns DamageReport.

## Key Attributes

| Attribute           | Description                       |
| ------------------- | --------------------------------- |
| reportId            | Unique report identifier          |
| tenantId            | Tenant identifier                 |
| reportType          | Report type                       |
| damageCaseId        | Related damage case               |
| inspectionSessionId | Related inspection                |
| vehicleId           | Vehicle reference                 |
| rentalAgreementId   | Rental reference where applicable |
| reportStatus        | Generated, Failed, Archived       |
| storageReference    | Secure report location            |
| generatedBy         | User or system                    |
| generatedAt         | Generation timestamp              |

## Report Types

Examples:

* Inspection Summary
* Damage Case Report
* Customer Dispute Evidence Report
* Maintenance Handoff Report
* Vehicle Damage History Report

---

# Aggregate: CaptureTemplate

## Description

CaptureTemplate defines required and optional capture positions for an inspection workflow.

## Ownership

Damage Intelligence owns CaptureTemplate.

## Key Attributes

| Attribute                | Description                   |
| ------------------------ | ----------------------------- |
| captureTemplateId        | Unique template identifier    |
| tenantId                 | Tenant identifier             |
| templateName             | Template name                 |
| inspectionType           | Inspection type               |
| vehicleType              | Vehicle type where applicable |
| requiredCapturePositions | Required positions            |
| optionalCapturePositions | Optional positions            |
| qualityRules             | Image quality rules           |
| overridePolicy           | Override policy               |
| active                   | Active status                 |
| version                  | Template version              |

## Invariants

CaptureTemplate SHALL enforce:

* Active template must have at least one required capture position.
* Required capture position IDs must be valid.
* Template version must be tracked.
* Template changes SHOULD be audited.

---

# Value Objects

## VehicleReference

Represents a reference to a vehicle owned by CROMS or Fleet domain.

| Attribute   | Description            |
| ----------- | ---------------------- |
| vehicleId   | Vehicle identifier     |
| plateNumber | Optional display value |
| make        | Optional display value |
| model       | Optional display value |
| year        | Optional display value |

---

## RentalAgreementReference

Represents a reference to a rental agreement owned by CROMS.

| Attribute         | Description                 |
| ----------------- | --------------------------- |
| rentalAgreementId | Rental agreement identifier |
| customerId        | Customer reference          |
| checkOutAt        | Check-out timestamp         |
| expectedReturnAt  | Expected return timestamp   |
| actualReturnAt    | Actual return timestamp     |

---

## WorkOrderReference

Represents a reference to a Maintenance work order.

| Attribute            | Description                                  |
| -------------------- | -------------------------------------------- |
| workOrderId          | Work order identifier                        |
| maintenanceRequestId | Maintenance request identifier               |
| status               | Maintenance status                           |
| actualCostReference  | Actual repair cost reference where available |

---

## EvidenceReference

Represents evidence linked to findings, comparisons, reports, or review decisions.

| Attribute        | Description                                        |
| ---------------- | -------------------------------------------------- |
| evidenceType     | Image, Report, AI Finding, Review Note, Comparison |
| evidenceId       | Evidence identifier                                |
| storageReference | Storage reference where applicable                 |
| description      | Evidence description                               |

---

## MoneyRange

Represents estimated cost range.

| Attribute | Description    |
| --------- | -------------- |
| minimum   | Minimum amount |
| maximum   | Maximum amount |
| currency  | Currency code  |

---

## ConfidenceScore

Represents confidence from AI, comparison, or estimate.

| Attribute | Description                 |
| --------- | --------------------------- |
| score     | Numeric score from 0 to 1   |
| label     | High, Medium, Low, Unknown  |
| reason    | Explanation where available |

---

## AuditReference

Represents audit trail reference.

| Attribute | Description      |
| --------- | ---------------- |
| auditId   | Audit identifier |
| eventType | Audit event type |
| timestamp | Event timestamp  |
| actorId   | Actor identifier |

---

# Enumerations

## InspectionType

| Code               | Description                    |
| ------------------ | ------------------------------ |
| CheckOut           | Rental check-out inspection    |
| CheckIn            | Rental return inspection       |
| MaintenanceIntake  | Maintenance intake inspection  |
| MaintenanceQuality | Post-repair quality inspection |
| AdHoc              | Manual inspection              |

---

## InspectionStatus

| Code          |
| ------------- |
| Draft         |
| Started       |
| Capturing     |
| Submitted     |
| Analyzing     |
| PendingReview |
| Completed     |
| Closed        |
| Cancelled     |

---

## ImageQualityStatus

| Code       |
| ---------- |
| NotChecked |
| Passed     |
| Failed     |
| Warning    |
| Unknown    |

---

## FindingSource

| Code     |
| -------- |
| AI       |
| Human    |
| Imported |
| System   |
| Hybrid   |

---

## DamageFindingStatus

| Code          |
| ------------- |
| Generated     |
| PendingReview |
| Confirmed     |
| Edited        |
| Rejected      |
| Escalated     |
| Closed        |

---

## ComparisonOutcome

| Code          |
| ------------- |
| New           |
| PreExisting   |
| Changed       |
| Repaired      |
| Uncertain     |
| NotComparable |

---

## ReviewStatus

| Code        |
| ----------- |
| NotRequired |
| Required    |
| Pending     |
| Completed   |
| Escalated   |
| Rejected    |

---

## DamageCaseStatus

| Code                |
| ------------------- |
| Draft               |
| Created             |
| InReview            |
| Confirmed           |
| Rejected            |
| Escalated           |
| RoutedToMaintenance |
| Resolved            |
| Closed              |
| Archived            |

---

## RepairEstimateStatus

| Code                |
| ------------------- |
| Draft               |
| Generated           |
| PendingReview       |
| Reviewed            |
| Accepted            |
| Edited              |
| Rejected            |
| Escalated           |
| RoutedToMaintenance |
| Superseded          |
| Closed              |

---

# Relationship Model

## Primary Relationships

| Relationship                         | Cardinality                               |
| ------------------------------------ | ----------------------------------------- |
| Vehicle to InspectionSession         | One vehicle has many inspection sessions  |
| InspectionSession to InspectionImage | One inspection session has many images    |
| InspectionSession to DamageFinding   | One inspection session has many findings  |
| DamageFinding to InspectionImage     | One finding may reference many images     |
| DamageFinding to DamageComparison    | One finding may have many comparisons     |
| DamageCase to DamageFinding          | One case may contain one or many findings |
| DamageCase to ReviewDecision         | One case may have many review decisions   |
| DamageCase to RepairEstimate         | One case may have many estimates          |
| DamageCase to DamageReport           | One case may have many reports            |
| CaptureTemplate to InspectionSession | One template may be used by many sessions |

---

# Domain Invariants

Damage Intelligence SHALL enforce the following domain invariants:

1. Tenant isolation SHALL apply to all domain objects.
2. Inspection evidence SHALL be preserved after submission.
3. AI findings SHALL be advisory until reviewed where review is required.
4. Missing historical evidence SHALL NOT prove new damage.
5. Customer-impacting decisions SHALL require human review where policy requires.
6. Damage taxonomy values SHALL use approved codes.
7. Severity values SHALL use approved codes.
8. Repair estimates SHALL NOT become final customer charges.
9. Damage case closure SHALL preserve evidence, review decisions, and audit history.
10. Significant state transitions SHALL be audited.

---

# Domain Events

Damage Intelligence SHOULD emit domain events for significant lifecycle changes.

| Event                         | Trigger                            |
| ----------------------------- | ---------------------------------- |
| InspectionSessionCreated      | New inspection session created     |
| InspectionSessionStarted      | Inspection started                 |
| InspectionImageRegistered     | Image registered                   |
| ImageQualityChecked           | Image quality check completed      |
| InspectionSubmitted           | Inspection submitted               |
| AIAnalysisRequested           | AI analysis requested              |
| AIAnalysisCompleted           | AI analysis completed              |
| DamageFindingCreated          | Damage finding created             |
| DamageComparisonCompleted     | Comparison completed               |
| DamageCaseCreated             | Damage case created                |
| ReviewDecisionRecorded        | Human review decision recorded     |
| RepairEstimateGenerated       | Advisory repair estimate generated |
| DamageCaseRoutedToMaintenance | Damage case routed to Maintenance  |
| DamageReportGenerated         | Report generated                   |
| DamageCaseClosed              | Damage case closed                 |

Detailed event specification SHALL be defined in:

```text
DI-0013-Events.md
```

---

# Audit Model Implications

Every aggregate SHALL support auditability.

Audit SHALL capture:

* Object type.
* Object identifier.
* Tenant identifier.
* Actor.
* Action.
* Previous state where applicable.
* New state where applicable.
* Timestamp.
* Reason where applicable.
* Correlation ID.

Audit records SHOULD be immutable.

---

# Security Model Implications

The domain model SHALL support:

* Tenant isolation.
* Object-level authorization.
* Role-based access control.
* Secure evidence access.
* Secure report access.
* Controlled customer data exposure.
* Audit of evidence access.
* Protection of advisory cost estimate details.

---

# Integration Ownership Rules

## CROMS Ownership

CROMS owns:

* Rental Agreement
* Customer master reference
* Vehicle rental lifecycle
* Vehicle availability decision according to rental policy

Damage Intelligence references CROMS data but does not own it.

## Maintenance Ownership

Maintenance owns:

* Work Order
* Repair execution
* Technician assignment
* Parts usage
* Actual repair cost
* Repair completion status

Damage Intelligence provides evidence and advisory context.

## Damage Intelligence Ownership

Damage Intelligence owns:

* Inspection evidence.
* Damage findings.
* Damage comparisons.
* Damage cases.
* Human damage review records.
* Advisory repair estimates.
* Damage reports.

---

# Data Retention Implications

The domain model SHALL support evidence retention policies.

Retention SHOULD apply to:

* Inspection images.
* Damage findings.
* Damage cases.
* Review decisions.
* Comparison results.
* Reports.
* Audit records.
* Advisory estimates.

Evidence supporting customer-impacting decisions SHOULD be retained according to approved business and legal policy.

---

# Reporting Implications

The domain model SHALL support reporting by:

* Vehicle.
* Rental agreement.
* Branch.
* Tenant.
* Damage type.
* Vehicle area.
* Severity.
* Comparison outcome.
* Review decision.
* Maintenance routing status.
* Estimate range.
* Date period.

---

# Normative Requirements

## Requirement

ID: REQ-DI-1100

Title:
Damage Intelligence Domain Model

Statement:
Damage Intelligence SHALL define and maintain a logical domain model for inspection, evidence, damage findings, comparisons, cases, review decisions, repair estimates, and reports.

Priority:
Critical

Verification:
Architecture Review

---

## Requirement

ID: REQ-DI-1101

Title:
Domain Boundary

Statement:
Damage Intelligence SHALL clearly separate owned domain objects from external references owned by CROMS, Maintenance, Finance, or Identity domains.

Priority:
Critical

Verification:
Architecture Review

---

## Requirement

ID: REQ-DI-1102

Title:
Inspection Session Aggregate

Statement:
Damage Intelligence SHALL model InspectionSession as the aggregate governing inspection workflow and captured evidence.

Priority:
Critical

Verification:
Domain Model Review

---

## Requirement

ID: REQ-DI-1103

Title:
Inspection Image Entity

Statement:
Damage Intelligence SHALL model InspectionImage as evidence belonging to an InspectionSession.

Priority:
Critical

Verification:
Domain Model Review

---

## Requirement

ID: REQ-DI-1104

Title:
Damage Finding Aggregate

Statement:
Damage Intelligence SHALL model detected, reported, and reviewed damage as DamageFinding.

Priority:
Critical

Verification:
Domain Model Review

---

## Requirement

ID: REQ-DI-1105

Title:
Damage Comparison Aggregate

Statement:
Damage Intelligence SHALL model historical evidence comparison as DamageComparison.

Priority:
Critical

Verification:
Domain Model Review

---

## Requirement

ID: REQ-DI-1106

Title:
Damage Case Aggregate

Statement:
Damage Intelligence SHALL model operational damage case handling as DamageCase.

Priority:
Critical

Verification:
Domain Model Review

---

## Requirement

ID: REQ-DI-1107

Title:
Review Decision Entity

Statement:
Damage Intelligence SHALL capture authorized human decisions using ReviewDecision.

Priority:
Critical

Verification:
Workflow Review

---

## Requirement

ID: REQ-DI-1108

Title:
Repair Estimate Aggregate

Statement:
Damage Intelligence SHALL model advisory repair cost estimates separately from actual repair costs.

Priority:
High

Verification:
Domain Model Review

---

## Requirement

ID: REQ-DI-1109

Title:
External References

Statement:
Damage Intelligence SHALL use references for Vehicle, Rental Agreement, Customer, Work Order, and User objects owned by other domains.

Priority:
Critical

Verification:
Architecture Review

---

## Requirement

ID: REQ-DI-1110

Title:
Domain State Control

Statement:
Damage Intelligence SHALL define lifecycle states for core aggregates.

Priority:
High

Verification:
Domain Model Review

---

## Requirement

ID: REQ-DI-1111

Title:
Domain Invariants

Statement:
Damage Intelligence SHALL enforce domain invariants related to evidence preservation, advisory AI, human review, taxonomy usage, and auditability.

Priority:
Critical

Verification:
Architecture/Test Review

---

## Requirement

ID: REQ-DI-1112

Title:
Domain Events

Statement:
Damage Intelligence SHOULD emit domain events for significant aggregate lifecycle changes.

Priority:
High

Verification:
Event Design Review

---

## Requirement

ID: REQ-DI-1113

Title:
Tenant Isolation in Domain Model

Statement:
Damage Intelligence domain objects SHALL include tenant isolation support.

Priority:
Critical

Verification:
Security Review

---

## Requirement

ID: REQ-DI-1114

Title:
Auditability in Domain Model

Statement:
Damage Intelligence core aggregates SHALL support auditability for significant state and decision changes.

Priority:
Critical

Verification:
Audit Review

---

# Business Rules

## BR-DI-0700 — Damage Intelligence Owns Evidence

Inspection evidence captured through Damage Intelligence SHALL be owned by Damage Intelligence.

---

## BR-DI-0701 — External Objects Are Referenced

Vehicle, Rental Agreement, Customer, User, Work Order, and Finance objects SHALL be referenced and not duplicated as owned records.

---

## BR-DI-0702 — AI Findings Are Advisory

AI findings SHALL remain advisory until reviewed where human review is required.

---

## BR-DI-0703 — Actual Repair Cost Is External

Actual repair cost SHALL be owned by Maintenance or Finance, not Damage Intelligence.

---

## BR-DI-0704 — State Changes Must Be Audited

Significant domain object state changes SHALL be audited.

---

## BR-DI-0705 — Taxonomy Codes Must Be Used

Damage type, vehicle area, severity, comparison outcome, and review status SHALL use approved taxonomy or enum values.

---

# AI Implementation Contract

AI development agents SHALL:

* Treat this document as the authoritative logical domain model for Damage Intelligence.
* Preserve all aggregate names, entity names, value object names, lifecycle states, and requirement IDs.
* Not convert this logical model directly into database tables without later data design review.
* Preserve the separation between owned objects and external references.
* Preserve CROMS and Maintenance ownership boundaries.
* Preserve advisory AI and advisory repair estimate rules.
* Preserve tenant isolation, auditability, and evidence integrity requirements.
* Generate future APIs, schemas, events, tests, and database designs consistent with this model.
* Raise ambiguity where aggregate ownership, lifecycle state, or external reference ownership is unclear.

---

# References

* DI-0001 – Damage Intelligence Product Vision
* DI-0002 – Damage Intelligence Business Requirements
* DI-0004 – Damage Intelligence Inspection Workflow
* DI-0005 – AI Damage Detection
* DI-0006 – Damage Comparison
* DI-0007 – Vehicle Capture Standards
* DI-0008 – Damage Taxonomy
* DI-0009 – Severity Assessment
* DI-0010 – Repair Cost Estimation
* DI-0011 – API Specification
* DI-0013 – Events
* RA-0002 – Domain-Driven Design Architecture
* PLATFORM-0005 – GEES Core and Application Architecture

---

# Revision History

| Version | Date       | Description                                            |
| ------- | ---------- | ------------------------------------------------------ |
| 1.0.0   | 2026-06-27 | Initial Damage Intelligence Domain Model Specification |

