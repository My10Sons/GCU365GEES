---
id: DI-0011
title: Damage Intelligence API Specification
version: 1.0.0
document_type: Product Specification
document_class: API Specification
status: Draft
classification: Internal
owner: Riyadah Technology
reviewers:
  - Chief Enterprise Architect
  - Product Owner
  - API Architecture Lead
  - AI Engineering Lead
  - Security Lead
  - Maintenance Lead
  - CROMS Lead
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
  - RA-0001
  - RA-0002
  - GEES-0005
  - GEES-0007
  - GEES-0009
  - PLATFORM-0005
---

# Damage Intelligence API Specification

## Executive Summary

This document defines the API specification for Damage Intelligence.

The Damage Intelligence APIs provide governed access to inspection sessions, image capture, AI analysis, damage findings, damage comparison, damage cases, human review, maintenance routing, taxonomy, reports, and integration with GCU365 CROMS and GCU365 Maintenance.

The APIs defined in this document are logical product-level contracts. Final machine-readable OpenAPI specifications SHALL be generated later under the `specs/openapi/` directory.

All APIs SHALL preserve security, tenant isolation, traceability, auditability, and human accountability.

---

# Purpose

The purpose of this document is to define the API capabilities required to implement Damage Intelligence and integrate it with GCU365 CROMS and GCU365 Maintenance.

This specification SHALL guide:

- REST API design.
- OpenAPI generation.
- Backend service implementation.
- Integration with CROMS.
- Integration with Maintenance.
- Mobile capture workflows.
- AI service orchestration.
- Audit logging.
- Test case generation.
- Security review.
- Traceability.

---

# Scope

## In Scope

This API specification covers APIs for:

- Inspection session management.
- Inspection image upload.
- Image metadata management.
- Image quality validation.
- AI damage detection.
- Damage comparison.
- Damage finding management.
- Damage case management.
- Human review.
- Maintenance routing.
- Damage taxonomy retrieval.
- Capture template retrieval.
- Reports.
- Audit retrieval.
- Integration callbacks.

## Out of Scope

The following are outside this document:

- Full CROMS API specification.
- Full Maintenance API specification.
- Final OpenAPI YAML.
- Full database schema.
- Full UI specification.
- AI model internal APIs.
- Vendor repair APIs.
- Payment APIs.
- Insurance claim APIs.

---

# API Principles

Damage Intelligence APIs SHALL follow these principles:

1. API First
2. Security by Design
3. Tenant Isolation
4. Versioning
5. Idempotency Where Required
6. Auditability
7. Traceability
8. Consistent Error Handling
9. Backward Compatibility Where Practical
10. Human Review Before Final Customer-Impacting Decisions

---

# Base URL

The logical base path SHALL be:

```text
/api/v1/damage-intelligence
```

Future versions SHALL use explicit versioning:

```text
/api/v2/damage-intelligence
```

---

# API Style

The primary API style SHALL be REST.

Where asynchronous operations are required, APIs MAY return operation references or processing status resources.

Events SHALL be used for asynchronous cross-domain communication where appropriate.

---

# Authentication and Authorization

All APIs SHALL require authentication unless explicitly documented otherwise.

Authentication SHALL use approved platform identity mechanisms.

Authorization SHALL enforce role-based access and tenant isolation.

APIs SHALL validate:

- Tenant access.
- User permissions.
- Object ownership.
- Role privileges.
- Operation scope.

---

# Required Headers

Clients SHOULD send the following headers where applicable:

| Header | Required | Description |
|--------|----------|-------------|
| Authorization | Yes | Bearer access token |
| X-Tenant-Id | Yes | Tenant identifier |
| X-Correlation-Id | Recommended | Request correlation ID |
| X-Idempotency-Key | Conditional | Idempotency key for create/submit operations |
| Accept-Language | Optional | Preferred response language |
| Content-Type | Conditional | Request content type |

---

# Standard Response Envelope

APIs SHOULD use a consistent response envelope.

```json
{
  "success": true,
  "data": {},
  "errors": [],
  "metadata": {
    "correlationId": "CORR-000001",
    "timestamp": "2026-06-27T00:00:00Z",
    "version": "v1"
  }
}
```

Error response example:

```json
{
  "success": false,
  "data": null,
  "errors": [
    {
      "code": "DI_VALIDATION_ERROR",
      "message": "Required capture position is missing.",
      "target": "capturePositions"
    }
  ],
  "metadata": {
    "correlationId": "CORR-000001",
    "timestamp": "2026-06-27T00:00:00Z",
    "version": "v1"
  }
}
```

---

# Error Code Categories

| Category | Prefix | Description |
|----------|--------|-------------|
| Validation | DI_VALIDATION | Invalid request or missing data |
| Security | DI_SECURITY | Authentication or authorization failure |
| Not Found | DI_NOT_FOUND | Resource not found |
| Conflict | DI_CONFLICT | Duplicate or state conflict |
| AI | DI_AI | AI processing failure |
| Storage | DI_STORAGE | Image or evidence storage failure |
| Integration | DI_INTEGRATION | CROMS or Maintenance integration failure |
| Workflow | DI_WORKFLOW | Invalid lifecycle transition |
| System | DI_SYSTEM | Unexpected system error |

---

# Pagination

List APIs SHALL support pagination where result sets may grow.

Recommended query parameters:

| Parameter | Description |
|-----------|-------------|
| page | Page number |
| pageSize | Number of records |
| sortBy | Sort field |
| sortDirection | asc or desc |
| filter | Filter expression where supported |

---

# Idempotency

The following operations SHOULD support idempotency:

- Create inspection session.
- Submit inspection.
- Upload image metadata.
- Create damage case.
- Route to Maintenance.
- Trigger AI analysis.
- Trigger comparison.

Idempotent requests SHOULD use:

```text
X-Idempotency-Key
```

---

# API Resource Summary

| API Group | Purpose |
|-----------|---------|
| Inspection Sessions | Manage inspection lifecycle |
| Inspection Images | Upload and manage evidence |
| AI Analysis | Trigger and retrieve AI damage detection |
| Damage Findings | Manage detected damage findings |
| Damage Comparison | Compare current and historical evidence |
| Damage Cases | Manage structured damage cases |
| Review | Human review workflow |
| Maintenance Routing | Send confirmed damage to Maintenance |
| Taxonomy | Retrieve damage taxonomy |
| Capture Templates | Retrieve capture requirements |
| Reports | Generate damage and inspection reports |
| Audit | Retrieve audit history |
| Integration | Receive or send integration status |

---

# Inspection Session APIs

## Create Inspection Session

```http
POST /api/v1/damage-intelligence/inspection-sessions
```

### Purpose

Create a new inspection session.

### Used By

- CROMS
- Maintenance
- Damage Intelligence Portal
- Mobile Capture App

### Request

```json
{
  "inspectionType": "CheckOut",
  "vehicleId": "VEH-000001",
  "rentalAgreementId": "RA-000001",
  "workOrderId": null,
  "branchId": "BR-000001",
  "requestedBy": "USR-000001",
  "captureTemplateId": "TPL-DI-000001"
}
```

### Response

```json
{
  "inspectionSessionId": "INS-DI-000001",
  "status": "Draft",
  "inspectionType": "CheckOut",
  "vehicleId": "VEH-000001",
  "rentalAgreementId": "RA-000001",
  "captureTemplateId": "TPL-DI-000001",
  "requiredCapturePositions": [
    "CAPTURE-FRONT",
    "CAPTURE-REAR",
    "CAPTURE-LEFT",
    "CAPTURE-RIGHT"
  ],
  "createdAt": "2026-06-27T00:00:00Z"
}
```

---

## Get Inspection Session

```http
GET /api/v1/damage-intelligence/inspection-sessions/{inspectionSessionId}
```

### Purpose

Retrieve inspection session details.

### Response Includes

- Inspection session metadata.
- Capture progress.
- Image list.
- AI analysis status.
- Comparison status.
- Review status.
- Damage case references.

---

## List Inspection Sessions

```http
GET /api/v1/damage-intelligence/inspection-sessions
```

### Supported Filters

- vehicleId
- rentalAgreementId
- workOrderId
- inspectionType
- status
- branchId
- dateFrom
- dateTo

---

## Start Inspection Session

```http
POST /api/v1/damage-intelligence/inspection-sessions/{inspectionSessionId}/start
```

### Purpose

Move inspection session from `Draft` to `Started`.

---

## Submit Inspection Session

```http
POST /api/v1/damage-intelligence/inspection-sessions/{inspectionSessionId}/submit
```

### Purpose

Submit captured inspection evidence for processing.

### Validation

System SHALL validate:

- Required images are captured.
- Required metadata exists.
- User has submit permission.
- Inspection is in a submittable state.

### Response

```json
{
  "inspectionSessionId": "INS-DI-000001",
  "status": "Submitted",
  "aiAnalysisStatus": "Queued",
  "comparisonStatus": "Pending"
}
```

---

## Close Inspection Session

```http
POST /api/v1/damage-intelligence/inspection-sessions/{inspectionSessionId}/close
```

### Purpose

Close inspection session after all required processing and review is complete.

---

# Inspection Image APIs

## Request Image Upload URL

```http
POST /api/v1/damage-intelligence/inspection-sessions/{inspectionSessionId}/images/upload-url
```

### Purpose

Generate a secure upload URL for an inspection image.

### Request

```json
{
  "capturePositionId": "CAPTURE-FRONT",
  "fileName": "front-view.jpg",
  "contentType": "image/jpeg",
  "fileSizeBytes": 2350000
}
```

### Response

```json
{
  "imageId": "IMG-DI-000001",
  "uploadUrl": "https://storage.example.com/signed-url",
  "expiresAt": "2026-06-27T00:10:00Z"
}
```

---

## Register Uploaded Image

```http
POST /api/v1/damage-intelligence/inspection-sessions/{inspectionSessionId}/images
```

### Purpose

Register metadata for an uploaded image.

### Request

```json
{
  "imageId": "IMG-DI-000001",
  "capturePositionId": "CAPTURE-FRONT",
  "storageReference": "blob://damage/INS-DI-000001/front.jpg",
  "capturedAt": "2026-06-27T00:00:00Z",
  "deviceId": "DEVICE-000001",
  "gps": {
    "latitude": 24.7136,
    "longitude": 46.6753
  }
}
```

---

## Get Inspection Image

```http
GET /api/v1/damage-intelligence/images/{imageId}
```

### Purpose

Retrieve image metadata and authorized viewing reference.

The API SHALL NOT expose unrestricted public image access.

---

## Validate Image Quality

```http
POST /api/v1/damage-intelligence/images/{imageId}/quality-check
```

### Purpose

Run image quality validation.

### Response

```json
{
  "imageId": "IMG-DI-000001",
  "qualityStatus": "Passed",
  "checks": {
    "blur": "Passed",
    "brightness": "Passed",
    "vehiclePresence": "Passed",
    "capturePositionMatch": "Passed"
  }
}
```

---

# AI Analysis APIs

## Trigger AI Analysis

```http
POST /api/v1/damage-intelligence/inspection-sessions/{inspectionSessionId}/ai-analysis
```

### Purpose

Trigger AI damage detection for an inspection session.

### Response

```json
{
  "analysisId": "AIA-DI-000001",
  "inspectionSessionId": "INS-DI-000001",
  "status": "Queued"
}
```

---

## Get AI Analysis Status

```http
GET /api/v1/damage-intelligence/ai-analysis/{analysisId}
```

### Response

```json
{
  "analysisId": "AIA-DI-000001",
  "status": "Completed",
  "startedAt": "2026-06-27T00:00:00Z",
  "completedAt": "2026-06-27T00:00:15Z",
  "findingsCount": 3
}
```

---

## Get AI Findings for Inspection

```http
GET /api/v1/damage-intelligence/inspection-sessions/{inspectionSessionId}/ai-findings
```

### Purpose

Retrieve AI-generated damage findings for the inspection.

---

# Damage Finding APIs

## List Damage Findings

```http
GET /api/v1/damage-intelligence/damage-findings
```

### Supported Filters

- inspectionSessionId
- vehicleId
- damageType
- vehicleArea
- severity
- status
- comparisonOutcome
- reviewStatus

---

## Get Damage Finding

```http
GET /api/v1/damage-intelligence/damage-findings/{damageFindingId}
```

---

## Create Manual Damage Finding

```http
POST /api/v1/damage-intelligence/damage-findings
```

### Purpose

Allow authorized users to create a manual damage finding.

### Request

```json
{
  "inspectionSessionId": "INS-DI-000001",
  "damageType": "SCRATCH",
  "vehicleArea": "REAR_BUMPER",
  "severity": "MINOR",
  "description": "Scratch on rear bumper",
  "evidenceImageIds": ["IMG-DI-000001"]
}
```

---

## Update Damage Finding

```http
PATCH /api/v1/damage-intelligence/damage-findings/{damageFindingId}
```

### Purpose

Allow authorized users to edit damage finding classification.

All updates SHALL be audited.

---

# Damage Comparison APIs

## Trigger Damage Comparison

```http
POST /api/v1/damage-intelligence/inspection-sessions/{inspectionSessionId}/damage-comparison
```

### Purpose

Compare the current inspection against historical evidence.

### Request

```json
{
  "baselineSelectionMode": "Auto",
  "preferredBaselineInspectionSessionId": null
}
```

---

## Get Damage Comparison Result

```http
GET /api/v1/damage-intelligence/damage-comparisons/{comparisonId}
```

---

## List Comparison Results for Inspection

```http
GET /api/v1/damage-intelligence/inspection-sessions/{inspectionSessionId}/damage-comparisons
```

---

# Damage Case APIs

## Create Damage Case

```http
POST /api/v1/damage-intelligence/damage-cases
```

### Purpose

Create a structured damage case from one or more findings.

### Request

```json
{
  "vehicleId": "VEH-000001",
  "rentalAgreementId": "RA-000001",
  "inspectionSessionId": "INS-DI-000001",
  "damageFindingIds": ["DMF-DI-000001"],
  "caseReason": "PotentialNewDamage"
}
```

---

## Get Damage Case

```http
GET /api/v1/damage-intelligence/damage-cases/{damageCaseId}
```

---

## List Damage Cases

```http
GET /api/v1/damage-intelligence/damage-cases
```

### Supported Filters

- vehicleId
- rentalAgreementId
- status
- severity
- branchId
- reviewStatus
- maintenanceRoutingStatus

---

## Update Damage Case

```http
PATCH /api/v1/damage-intelligence/damage-cases/{damageCaseId}
```

---

## Close Damage Case

```http
POST /api/v1/damage-intelligence/damage-cases/{damageCaseId}/close
```

---

# Human Review APIs

## Submit Finding Review Decision

```http
POST /api/v1/damage-intelligence/damage-findings/{damageFindingId}/review
```

### Request

```json
{
  "decision": "Confirmed",
  "damageType": "SCRATCH",
  "vehicleArea": "REAR_BUMPER",
  "severity": "MINOR",
  "reviewNotes": "Damage visible and consistent with AI finding."
}
```

### Rules

Review decisions SHALL be audited.

---

## Submit Damage Case Review Decision

```http
POST /api/v1/damage-intelligence/damage-cases/{damageCaseId}/review
```

### Request

```json
{
  "decision": "ConfirmedNewDamage",
  "reviewNotes": "Current return inspection shows damage not present in check-out inspection.",
  "requiresMaintenance": true
}
```

---

## Get Review Queue

```http
GET /api/v1/damage-intelligence/review-queue
```

### Supported Filters

- priority
- severity
- reviewReason
- branchId
- assignedTo
- status

---

# Maintenance Routing APIs

## Route Damage Case to Maintenance

```http
POST /api/v1/damage-intelligence/damage-cases/{damageCaseId}/route-to-maintenance
```

### Purpose

Send confirmed repair-required damage to Maintenance.

### Request

```json
{
  "routingReason": "RepairRequired",
  "recommendedRepairCategory": "BODY_REPAIR",
  "notes": "Rear bumper scratch requires maintenance review."
}
```

### Response

```json
{
  "damageCaseId": "DMC-DI-000001",
  "maintenanceRequestId": "MREQ-DI-000001",
  "status": "RoutedToMaintenance"
}
```

---

## Receive Maintenance Status Update

```http
POST /api/v1/damage-intelligence/integrations/maintenance/status-updates
```

### Purpose

Receive Maintenance status updates related to routed damage.

---

# CROMS Integration APIs

## Start Check-Out Inspection

```http
POST /api/v1/damage-intelligence/integrations/croms/check-out-inspections
```

### Purpose

CROMS requests a check-out inspection session.

---

## Start Check-In Inspection

```http
POST /api/v1/damage-intelligence/integrations/croms/check-in-inspections
```

### Purpose

CROMS requests a return inspection session.

---

## Get Rental Damage Summary

```http
GET /api/v1/damage-intelligence/integrations/croms/rental-agreements/{rentalAgreementId}/damage-summary
```

### Purpose

Provide CROMS with inspection and damage summary for a rental agreement.

---

# Taxonomy APIs

## Get Damage Taxonomy

```http
GET /api/v1/damage-intelligence/taxonomy/damage
```

### Purpose

Retrieve approved damage taxonomy values.

---

## Get Vehicle Area Taxonomy

```http
GET /api/v1/damage-intelligence/taxonomy/vehicle-areas
```

---

## Get Severity Taxonomy

```http
GET /api/v1/damage-intelligence/taxonomy/severity
```

---

# Capture Template APIs

## Get Capture Templates

```http
GET /api/v1/damage-intelligence/capture-templates
```

---

## Get Capture Template

```http
GET /api/v1/damage-intelligence/capture-templates/{captureTemplateId}
```

---

# Repair Estimate APIs

## Generate Advisory Repair Estimate

```http
POST /api/v1/damage-intelligence/damage-cases/{damageCaseId}/repair-estimates
```

---

## Get Repair Estimate

```http
GET /api/v1/damage-intelligence/repair-estimates/{estimateId}
```

---

## Review Repair Estimate

```http
POST /api/v1/damage-intelligence/repair-estimates/{estimateId}/review
```

---

# Report APIs

## Generate Damage Report

```http
POST /api/v1/damage-intelligence/damage-cases/{damageCaseId}/reports
```

---

## Get Damage Report

```http
GET /api/v1/damage-intelligence/reports/{reportId}
```

---

## Get Vehicle Damage History

```http
GET /api/v1/damage-intelligence/vehicles/{vehicleId}/damage-history
```

---

# Audit APIs

## Get Audit History for Inspection

```http
GET /api/v1/damage-intelligence/inspection-sessions/{inspectionSessionId}/audit
```

---

## Get Audit History for Damage Case

```http
GET /api/v1/damage-intelligence/damage-cases/{damageCaseId}/audit
```

Audit APIs SHALL be restricted to authorized users.

---

# API Data Object Summary

The following logical data objects SHALL be represented in future OpenAPI schemas.

| Object | Purpose |
|--------|---------|
| InspectionSession | Inspection workflow container |
| InspectionImage | Captured image and metadata |
| ImageQualityResult | Image validation result |
| AIDamageFinding | AI-generated finding |
| DamageFinding | General damage finding |
| DamageComparison | Historical comparison result |
| DamageCase | Managed damage case |
| ReviewDecision | Human review decision |
| RepairEstimate | Advisory repair estimate |
| DamageReport | Generated report |
| AuditRecord | Audit trail entry |
| CaptureTemplate | Required capture configuration |
| TaxonomyValue | Controlled vocabulary value |

---

# API Security Rules

APIs SHALL enforce:

- Authentication
- Authorization
- Tenant isolation
- Object-level access control
- Secure image access
- Audit logging
- Rate limiting where required
- Input validation
- Output filtering

Sensitive image URLs SHALL be short-lived and access-controlled.

---

# API Audit Rules

The following API operations SHALL generate audit records:

- Create inspection session.
- Start inspection.
- Submit inspection.
- Upload/register image.
- Run AI analysis.
- Run damage comparison.
- Create damage finding.
- Review finding.
- Create damage case.
- Review damage case.
- Route to Maintenance.
- Generate report.
- Access protected evidence.
- Modify estimate.
- Override AI result.

---

# API Event Integration

APIs MAY publish domain events.

Examples:

- InspectionSessionCreated
- InspectionSubmitted
- ImageRegistered
- ImageQualityFailed
- AIAnalysisCompleted
- DamageDetected
- DamageComparisonCompleted
- DamageCaseCreated
- DamageReviewed
- DamageRoutedToMaintenance
- DamageReportGenerated

Detailed event specifications SHALL be defined in:

```text
DI-0013-Events.md
```

---

# API Versioning

APIs SHALL be versioned.

Breaking changes SHALL require a new API version.

Backward-compatible changes MAY remain in the same version.

Clients SHALL NOT depend on undocumented fields.

---

# API Performance Expectations

APIs SHOULD meet operationally acceptable response times.

AI-heavy operations SHOULD support asynchronous processing.

Recommended behavior:

- Create/read/update APIs return synchronously.
- AI analysis returns queued status.
- Damage comparison may run asynchronously.
- Report generation may run asynchronously.

Detailed performance thresholds SHALL be defined separately.

---

# API Reliability

APIs SHALL support:

- Retry-safe operations where appropriate.
- Idempotency for create/submit operations.
- Clear error codes.
- Correlation IDs.
- Integration failure handling.
- Operational logging.

---

# Normative Requirements

## Requirement

ID: REQ-DI-1000

Title:
Damage Intelligence API

Statement:
Damage Intelligence SHALL expose governed APIs for inspection, damage detection, comparison, review, reporting, and integration.

Priority:
Critical

Verification:
API Review

---

## Requirement

ID: REQ-DI-1001

Title:
API Versioning

Statement:
Damage Intelligence APIs SHALL use explicit versioning.

Priority:
Critical

Verification:
API Review

---

## Requirement

ID: REQ-DI-1002

Title:
API Authentication

Statement:
All Damage Intelligence APIs SHALL require authentication unless explicitly approved otherwise.

Priority:
Critical

Verification:
Security Review

---

## Requirement

ID: REQ-DI-1003

Title:
API Authorization

Statement:
Damage Intelligence APIs SHALL enforce authorization and tenant isolation.

Priority:
Critical

Verification:
Security Test

---

## Requirement

ID: REQ-DI-1004

Title:
Inspection Session APIs

Statement:
Damage Intelligence SHALL provide APIs to create, retrieve, start, submit, and close inspection sessions.

Priority:
Critical

Verification:
API Test

---

## Requirement

ID: REQ-DI-1005

Title:
Image APIs

Statement:
Damage Intelligence SHALL provide APIs for secure inspection image upload, registration, retrieval, and quality validation.

Priority:
Critical

Verification:
API Test

---

## Requirement

ID: REQ-DI-1006

Title:
AI Analysis APIs

Statement:
Damage Intelligence SHALL provide APIs to trigger and retrieve AI damage analysis.

Priority:
Critical

Verification:
API/AI Test

---

## Requirement

ID: REQ-DI-1007

Title:
Damage Comparison APIs

Statement:
Damage Intelligence SHALL provide APIs to trigger and retrieve damage comparison results.

Priority:
Critical

Verification:
API Test

---

## Requirement

ID: REQ-DI-1008

Title:
Damage Case APIs

Statement:
Damage Intelligence SHALL provide APIs for damage case creation, retrieval, update, review, and closure.

Priority:
Critical

Verification:
API Test

---

## Requirement

ID: REQ-DI-1009

Title:
Human Review APIs

Statement:
Damage Intelligence SHALL provide APIs for authorized human review decisions.

Priority:
Critical

Verification:
Workflow/API Test

---

## Requirement

ID: REQ-DI-1010

Title:
Maintenance Routing APIs

Statement:
Damage Intelligence SHALL provide APIs or integration contracts to route confirmed repair-required damage to Maintenance.

Priority:
High

Verification:
Integration Test

---

## Requirement

ID: REQ-DI-1011

Title:
CROMS Integration APIs

Statement:
Damage Intelligence SHALL provide APIs or integration contracts for CROMS check-out and check-in inspection workflows.

Priority:
Critical

Verification:
Integration Test

---

## Requirement

ID: REQ-DI-1012

Title:
Taxonomy APIs

Statement:
Damage Intelligence SHALL provide APIs to retrieve approved taxonomy values.

Priority:
High

Verification:
API Test

---

## Requirement

ID: REQ-DI-1013

Title:
API Auditability

Statement:
Significant Damage Intelligence API operations SHALL generate audit records.

Priority:
Critical

Verification:
Audit Review

---

## Requirement

ID: REQ-DI-1014

Title:
API Error Standardization

Statement:
Damage Intelligence APIs SHALL use standardized error response structures.

Priority:
High

Verification:
API Review

---

## Requirement

ID: REQ-DI-1015

Title:
Idempotent Operations

Statement:
Damage Intelligence SHOULD support idempotency for create, submit, upload, route, and processing-trigger operations.

Priority:
High

Verification:
API Test

---

## Requirement

ID: REQ-DI-1016

Title:
OpenAPI Specification

Statement:
Damage Intelligence APIs SHALL be documented using OpenAPI before implementation is considered complete.

Priority:
Critical

Verification:
Documentation Review

---

# Business Rules

## BR-DI-0600 — APIs Must Preserve Tenant Boundaries

Damage Intelligence APIs SHALL NOT expose tenant data across tenant boundaries.

---

## BR-DI-0601 — Image Access Must Be Controlled

Inspection image access SHALL require authorization and SHALL NOT rely on permanent public URLs.

---

## BR-DI-0602 — AI Processing May Be Asynchronous

AI-heavy operations MAY be asynchronous and return processing status.

---

## BR-DI-0603 — Review APIs Require Authorization

Only authorized users SHALL submit review decisions.

---

## BR-DI-0604 — Significant API Actions Must Be Audited

Operationally significant API actions SHALL create audit records.

---

# AI Implementation Contract

AI development agents SHALL:

- Treat this document as the authoritative logical API specification for Damage Intelligence.
- Preserve all endpoint groups and requirement IDs.
- Generate future OpenAPI files consistent with this document.
- Not expose unrestricted image URLs.
- Preserve authentication, authorization, and tenant isolation requirements.
- Preserve audit requirements.
- Preserve human review requirements.
- Preserve CROMS and Maintenance integration boundaries.
- Raise ambiguity where request/response fields are insufficiently defined.

---

# References

- DI-0001 – Damage Intelligence Product Vision
- DI-0002 – Damage Intelligence Business Requirements
- DI-0004 – Damage Intelligence Inspection Workflow
- DI-0005 – AI Damage Detection
- DI-0006 – Damage Comparison
- DI-0007 – Vehicle Capture Standards
- DI-0008 – Damage Taxonomy
- DI-0009 – Severity Assessment
- DI-0010 – Repair Cost Estimation
- DI-0013 – Events
- GEES-0007 – Enterprise Security Standard
- GEES-0009 – Traceability Standard
- PLATFORM-0005 – GEES Core and Application Architecture

---

# Revision History

| Version | Date | Description |
|----------|------|-------------|
| 1.0.0 | 2026-06-27 | Initial Damage Intelligence API Specification |
