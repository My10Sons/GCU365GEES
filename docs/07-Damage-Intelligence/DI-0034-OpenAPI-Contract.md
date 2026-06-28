---
id: "DI-0034"
title: "Damage Intelligence OpenAPI Contract"
version: "1.0.0"
document_type: "Product Specification"
document_class: "API Contract"
status: "Draft"
classification: "Internal"
owner: "Riyadah Technology"
reviewers: "Chief Enterprise Architect, Product Owner, Damage Intelligence Lead, Backend Lead, AI Engineering Lead, QA Lead, Security Lead, CROMS Lead, Maintenance Lead"
approvers: ""
created: "2026-06-27"
updated: "2026-06-27"
authoritative: true
ai_consumable: true
related: "DI-0011, DI-0012, DI-0013, DI-0014, DI-0015, DI-0017, DI-0018, DI-0019, DI-0020, DI-0031, DI-0032, DI-0033, DI-0035"
---

# Damage Intelligence OpenAPI Contract

## Executive Summary

This document defines the OpenAPI contract for the Damage Intelligence application.

Damage Intelligence is a production-ready image analysis and damage detection application for existing GCU365 CROMS and existing GCU365Maintenance systems.

Damage Intelligence provides inspection session APIs, secure evidence APIs, image quality APIs, AI-assisted damage detection APIs, comparison APIs, review APIs, damage case APIs, reporting APIs, audit APIs, configuration APIs, and integration APIs for CROMS and GCU365Maintenance.

Damage Intelligence SHALL NOT replace CROMS, GCU365Maintenance, Fleet, Finance, rental lifecycle ownership, maintenance work order execution, actual repair cost ownership, or vehicle asset management.

---

# Base API Path

All Damage Intelligence APIs SHALL use the following base path:

```text
/api/v1/damage-intelligence
```

---

# API Principles

All APIs SHALL follow these principles:

- Require authentication except approved health endpoints.
- Enforce tenant isolation.
- Enforce object-level authorization.
- Validate all request payloads.
- Return safe error responses.
- Return correlation ID.
- Create audit records for critical actions.
- Avoid exposing secrets.
- Avoid exposing stack traces.
- Avoid exposing raw storage paths.
- Avoid exposing unrestricted evidence URLs.
- Avoid exposing unrestricted report URLs.
- Preserve CROMS and Maintenance ownership boundaries.
- Treat AI outputs as advisory.
- Support idempotency for integration write operations where required.

---

# Standard Headers

## Required Request Headers

```http
Authorization: Bearer ACCESS_TOKEN
X-Tenant-Id: TENANT-000001
X-Correlation-Id: CORR-000001
```

## Optional Request Headers

```http
X-Idempotency-Key: IDEMPOTENCY-KEY-000001
Accept-Language: en
```

## Response Headers

```http
X-Correlation-Id: CORR-000001
Content-Type: application/json
```

---

# Standard Response Envelope

All APIs SHOULD return a standard response envelope.

```json
{
  "success": true,
  "correlationId": "CORR-000001",
  "data": {},
  "errors": []
}
```

Error response:

```json
{
  "success": false,
  "correlationId": "CORR-000001",
  "data": null,
  "errors": [
    {
      "code": "VALIDATION_ERROR",
      "message": "The request is invalid.",
      "field": "inspectionType"
    }
  ]
}
```

---

# Standard Error Codes

| Error Code | Meaning |
|-----------|---------|
| VALIDATION_ERROR | Request validation failed |
| UNAUTHORIZED | Authentication is missing or invalid |
| FORBIDDEN | Authenticated actor does not have permission |
| NOT_FOUND | Requested object was not found or not accessible |
| TENANT_SCOPE_VIOLATION | Cross-tenant access attempt |
| CONFLICT | Request conflicts with current state |
| INVALID_STATUS_TRANSITION | Requested status transition is invalid |
| IDEMPOTENCY_CONFLICT | Same idempotency key used with different payload |
| UNSUPPORTED_MEDIA_TYPE | File or payload media type is not supported |
| PAYLOAD_TOO_LARGE | Request payload or file exceeds allowed size |
| AI_PROCESSING_FAILED | AI processing failed safely |
| INTEGRATION_FAILED | External integration failed safely |
| REPORT_GENERATION_FAILED | Report generation failed safely |
| INTERNAL_ERROR | Internal error without sensitive details |

---

# Pagination Contract

List APIs SHOULD support pagination.

## Query Parameters

```text
pageNumber
pageSize
sortBy
sortDirection
```

## Example Response

```json
{
  "success": true,
  "correlationId": "CORR-000001",
  "data": {
    "items": [],
    "pageNumber": 1,
    "pageSize": 50,
    "totalItems": 0,
    "totalPages": 0
  },
  "errors": []
}
```

---

# Authentication and Authorization

All protected APIs SHALL require authentication.

Authorization SHALL be enforced using roles and permissions.

Recommended permissions:

| Permission | Purpose |
|-----------|---------|
| di.inspections.create | Create inspection sessions |
| di.inspections.read | Read inspection sessions |
| di.inspections.submit | Submit inspections |
| di.inspections.cancel | Cancel inspections |
| di.images.upload | Request and register image uploads |
| di.images.read | Read image metadata |
| di.evidence.access | Request controlled evidence access links |
| di.ai.request | Request AI analysis |
| di.ai.read | Read AI analysis and findings |
| di.comparison.request | Request damage comparison |
| di.comparison.read | Read comparison results |
| di.review.read | Read review queue |
| di.review.decide | Record review decisions |
| di.damagecases.create | Create damage cases |
| di.damagecases.read | Read damage cases |
| di.damagecases.update | Update damage cases |
| di.integrations.croms | CROMS service integration |
| di.integrations.maintenance | Maintenance service integration |
| di.reports.generate | Generate reports |
| di.reports.read | Read report metadata |
| di.reports.access | Generate controlled report access links |
| di.audit.read | Read audit records |
| di.configuration.manage | Manage configuration |

---

# API Groups

Damage Intelligence API groups are:

| Group | Purpose |
|------|---------|
| Health | Service and dependency health |
| Inspection Sessions | Inspection lifecycle |
| Images and Evidence | Image upload and evidence access |
| Image Quality | Image quality validation |
| AI Analysis | AI-assisted damage detection |
| Damage Findings | AI and reviewed findings |
| Damage Comparison | Baseline versus current condition comparison |
| Review | Human review queue and decisions |
| Damage Cases | Damage case context |
| CROMS Integration | Existing CROMS integration |
| Maintenance Integration | Existing GCU365Maintenance integration |
| Reports | Reports and evidence packages |
| Configuration | Controlled administration settings |
| Audit | Audit query and traceability |

---

# Health APIs

## GET /health

Returns basic service health.

```http
GET /api/v1/damage-intelligence/health
```

Authentication MAY be optional depending on deployment policy.

## GET /health/dependencies

Returns dependency health.

```http
GET /api/v1/damage-intelligence/health/dependencies
```

The response SHALL NOT expose secrets.

---

# Inspection Session APIs

## POST /inspection-sessions

Creates a new inspection session.

```http
POST /api/v1/damage-intelligence/inspection-sessions
```

### Request

```json
{
  "inspectionType": "CHECK_OUT",
  "sourceSystem": "GCU365-CROMS",
  "vehicleReference": {
    "vehicleId": "VEH-000001"
  },
  "rentalReference": {
    "rentalAgreementId": "RA-000001"
  },
  "maintenanceReference": {
    "workOrderId": null
  },
  "branchReference": {
    "branchId": "BR-000001"
  }
}
```

### Response

```json
{
  "success": true,
  "correlationId": "CORR-000001",
  "data": {
    "inspectionSessionId": "DI-INS-000001",
    "inspectionType": "CHECK_OUT",
    "status": "DRAFT",
    "createdAt": "2026-06-27T10:00:00Z"
  },
  "errors": []
}
```

## GET /inspection-sessions/{inspectionSessionId}

Retrieves an inspection session.

```http
GET /api/v1/damage-intelligence/inspection-sessions/{inspectionSessionId}
```

## GET /inspection-sessions

Lists inspection sessions.

```http
GET /api/v1/damage-intelligence/inspection-sessions
```

Supported filters SHOULD include:

```text
status
inspectionType
vehicleId
rentalAgreementId
branchId
createdFrom
createdTo
```

## POST /inspection-sessions/{inspectionSessionId}/submit

Submits an inspection session.

```http
POST /api/v1/damage-intelligence/inspection-sessions/{inspectionSessionId}/submit
```

## PATCH /inspection-sessions/{inspectionSessionId}/status

Updates inspection status using controlled status transitions.

```http
PATCH /api/v1/damage-intelligence/inspection-sessions/{inspectionSessionId}/status
```

### Request

```json
{
  "status": "CANCELLED",
  "reason": "Inspection cancelled by authorized user."
}
```

---

# Images and Evidence APIs

## POST /inspection-sessions/{inspectionSessionId}/images/upload-request

Generates a secure upload instruction.

```http
POST /api/v1/damage-intelligence/inspection-sessions/{inspectionSessionId}/images/upload-request
```

### Request

```json
{
  "capturePositionCode": "CAPTURE_FRONT",
  "fileName": "front.jpg",
  "contentType": "image/jpeg",
  "fileSizeBytes": 2450000
}
```

### Response

```json
{
  "success": true,
  "correlationId": "CORR-000002",
  "data": {
    "uploadRequestId": "DI-UPL-000001",
    "uploadUrl": "CONTROLLED_TIME_LIMITED_UPLOAD_URL",
    "expiresAt": "2026-06-27T10:15:00Z",
    "method": "PUT"
  },
  "errors": []
}
```

## POST /inspection-sessions/{inspectionSessionId}/images

Registers an uploaded image.

```http
POST /api/v1/damage-intelligence/inspection-sessions/{inspectionSessionId}/images
```

### Request

```json
{
  "uploadRequestId": "DI-UPL-000001",
  "capturePositionCode": "CAPTURE_FRONT",
  "storageObjectReference": "tenants/TENANT-000001/damage-intelligence/inspections/DI-INS-000001/images/DI-IMG-000001",
  "metadata": {
    "fileName": "front.jpg",
    "contentType": "image/jpeg",
    "fileSizeBytes": 2450000
  }
}
```

## GET /inspection-sessions/{inspectionSessionId}/images

Lists inspection image metadata.

```http
GET /api/v1/damage-intelligence/inspection-sessions/{inspectionSessionId}/images
```

## POST /evidence/{evidenceId}/access-link

Generates a controlled evidence access link.

```http
POST /api/v1/damage-intelligence/evidence/{evidenceId}/access-link
```

### Request

```json
{
  "purpose": "REVIEW",
  "expiresInMinutes": 15
}
```

---

# Image Quality APIs

## POST /images/{inspectionImageId}/quality-check

Runs or queues image quality validation.

```http
POST /api/v1/damage-intelligence/images/{inspectionImageId}/quality-check
```

## GET /images/{inspectionImageId}/quality-result

Retrieves image quality result.

```http
GET /api/v1/damage-intelligence/images/{inspectionImageId}/quality-result
```

## POST /inspection-sessions/{inspectionSessionId}/quality-check

Runs or queues quality validation for inspection images.

```http
POST /api/v1/damage-intelligence/inspection-sessions/{inspectionSessionId}/quality-check
```

---

# AI Analysis APIs

## POST /inspection-sessions/{inspectionSessionId}/ai-analysis

Requests AI-assisted damage detection.

```http
POST /api/v1/damage-intelligence/inspection-sessions/{inspectionSessionId}/ai-analysis
```

### Request

```json
{
  "analysisProfileCode": "STANDARD_DAMAGE_DETECTION",
  "includeImageQualityResults": true,
  "routeLowConfidenceToReview": true
}
```

## GET /ai-analysis/{aiAnalysisId}

Retrieves AI analysis status.

```http
GET /api/v1/damage-intelligence/ai-analysis/{aiAnalysisId}
```

## GET /ai-analysis/{aiAnalysisId}/findings

Retrieves AI findings.

```http
GET /api/v1/damage-intelligence/ai-analysis/{aiAnalysisId}/findings
```

## GET /inspection-sessions/{inspectionSessionId}/ai-findings

Retrieves AI findings for an inspection session.

```http
GET /api/v1/damage-intelligence/inspection-sessions/{inspectionSessionId}/ai-findings
```

## POST /ai-analysis/{aiAnalysisId}/retry

Retries eligible failed AI analysis.

```http
POST /api/v1/damage-intelligence/ai-analysis/{aiAnalysisId}/retry
```

AI outputs SHALL remain advisory.

---

# Damage Finding APIs

## POST /inspection-sessions/{inspectionSessionId}/damage-findings

Creates a manually added or reviewed damage finding where authorized.

```http
POST /api/v1/damage-intelligence/inspection-sessions/{inspectionSessionId}/damage-findings
```

## GET /inspection-sessions/{inspectionSessionId}/damage-findings

Lists damage findings for an inspection session.

```http
GET /api/v1/damage-intelligence/inspection-sessions/{inspectionSessionId}/damage-findings
```

---

# Damage Comparison APIs

## POST /inspection-sessions/{inspectionSessionId}/comparison

Requests comparison between current and baseline inspection.

```http
POST /api/v1/damage-intelligence/inspection-sessions/{inspectionSessionId}/comparison
```

### Request

```json
{
  "baselineInspectionSessionId": "DI-INS-BASE-000001",
  "comparisonProfileCode": "CHECK_IN_VS_CHECK_OUT",
  "routeUncertainToReview": true
}
```

## GET /comparisons/{comparisonId}

Retrieves comparison result.

```http
GET /api/v1/damage-intelligence/comparisons/{comparisonId}
```

## GET /inspection-sessions/{inspectionSessionId}/comparisons

Lists comparisons for an inspection session.

```http
GET /api/v1/damage-intelligence/inspection-sessions/{inspectionSessionId}/comparisons
```

Comparison outcomes SHALL include:

```text
NEW
PRE_EXISTING
CHANGED
REPAIRED
UNCERTAIN
NOT_COMPARABLE
```

---

# Review APIs

## GET /review-queue

Retrieves pending review items.

```http
GET /api/v1/damage-intelligence/review-queue
```

## GET /review-items/{reviewItemId}

Retrieves review item details.

```http
GET /api/v1/damage-intelligence/review-items/{reviewItemId}
```

## POST /review-items/{reviewItemId}/decision

Records a review decision.

```http
POST /api/v1/damage-intelligence/review-items/{reviewItemId}/decision
```

### Request

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

## POST /review-items/{reviewItemId}/additional-evidence-request

Requests additional evidence.

```http
POST /api/v1/damage-intelligence/review-items/{reviewItemId}/additional-evidence-request
```

---

# Damage Case APIs

## POST /damage-cases

Creates a damage case.

```http
POST /api/v1/damage-intelligence/damage-cases
```

## GET /damage-cases/{damageCaseId}

Retrieves a damage case.

```http
GET /api/v1/damage-intelligence/damage-cases/{damageCaseId}
```

## GET /damage-cases

Lists damage cases.

```http
GET /api/v1/damage-intelligence/damage-cases
```

## PATCH /damage-cases/{damageCaseId}/status

Updates damage case status.

```http
PATCH /api/v1/damage-intelligence/damage-cases/{damageCaseId}/status
```

## POST /damage-cases/{damageCaseId}/link-evidence

Links evidence to a damage case.

```http
POST /api/v1/damage-intelligence/damage-cases/{damageCaseId}/link-evidence
```

## POST /damage-cases/{damageCaseId}/link-finding

Links finding to a damage case.

```http
POST /api/v1/damage-intelligence/damage-cases/{damageCaseId}/link-finding
```

## POST /damage-cases/{damageCaseId}/link-comparison

Links comparison result to a damage case.

```http
POST /api/v1/damage-intelligence/damage-cases/{damageCaseId}/link-comparison
```

Damage case status SHALL NOT close rentals, create final charges, execute work orders, or own actual repair costs.

---

# CROMS Integration APIs

## POST /integrations/croms/check-out-inspections

Allows existing GCU365 CROMS to request a check-out inspection.

```http
POST /api/v1/damage-intelligence/integrations/croms/check-out-inspections
```

### Required Headers

```http
Authorization: Bearer SERVICE_TOKEN
X-Tenant-Id: TENANT-000001
X-Correlation-Id: CORR-000001
X-Idempotency-Key: CROMS-RA-000001-CHECKOUT
```

## POST /integrations/croms/check-in-inspections

Allows existing GCU365 CROMS to request a check-in inspection.

```http
POST /api/v1/damage-intelligence/integrations/croms/check-in-inspections
```

## GET /integrations/croms/rental-agreements/{rentalAgreementId}/damage-summary

Allows CROMS to retrieve rental damage context.

```http
GET /api/v1/damage-intelligence/integrations/croms/rental-agreements/{rentalAgreementId}/damage-summary
```

## GET /integrations/croms/inspection-sessions/{inspectionSessionId}/status

Allows CROMS to retrieve inspection status.

```http
GET /api/v1/damage-intelligence/integrations/croms/inspection-sessions/{inspectionSessionId}/status
```

## POST /integrations/croms/notifications/damage-summary-ready

Optional callback or notification endpoint.

```http
POST /api/v1/damage-intelligence/integrations/croms/notifications/damage-summary-ready
```

CROMS remains the system of record for rental lifecycle, rental closure, and final customer charge.

---

# Maintenance Integration APIs

## POST /integrations/maintenance/handoffs

Routes damage case context to GCU365Maintenance.

```http
POST /api/v1/damage-intelligence/integrations/maintenance/handoffs
```

## POST /integrations/maintenance/work-order-references

Receives Maintenance work order reference.

```http
POST /api/v1/damage-intelligence/integrations/maintenance/work-order-references
```

## POST /integrations/maintenance/repair-status-updates

Receives repair status updates.

```http
POST /api/v1/damage-intelligence/integrations/maintenance/repair-status-updates
```

## POST /integrations/maintenance/rejection-reasons

Receives Maintenance rejection reason.

```http
POST /api/v1/damage-intelligence/integrations/maintenance/rejection-reasons
```

## POST /integrations/maintenance/additional-evidence-requests

Receives additional evidence request from Maintenance.

```http
POST /api/v1/damage-intelligence/integrations/maintenance/additional-evidence-requests
```

## GET /integrations/maintenance/damage-cases/{damageCaseId}/handoff-status

Retrieves Maintenance handoff status.

```http
GET /api/v1/damage-intelligence/integrations/maintenance/damage-cases/{damageCaseId}/handoff-status
```

GCU365Maintenance remains the system of record for work orders, repair execution, technician workflow, and actual repair cost.

---

# Report APIs

## POST /reports

Generates or queues a report.

```http
POST /api/v1/damage-intelligence/reports
```

### Request

```json
{
  "reportType": "DAMAGE_COMPARISON_REPORT",
  "inspectionSessionId": "DI-INS-000002",
  "damageCaseId": "DI-CASE-000001",
  "locale": "en",
  "format": "PDF"
}
```

## GET /reports/{reportId}

Retrieves report metadata.

```http
GET /api/v1/damage-intelligence/reports/{reportId}
```

## POST /reports/{reportId}/access-link

Generates controlled report access link.

```http
POST /api/v1/damage-intelligence/reports/{reportId}/access-link
```

Reports SHALL NOT expose public unrestricted URLs.

---

# Configuration APIs

## GET /configuration/taxonomy

Retrieves configured taxonomy.

```http
GET /api/v1/damage-intelligence/configuration/taxonomy
```

## PUT /configuration/ai-thresholds

Updates AI threshold configuration.

```http
PUT /api/v1/damage-intelligence/configuration/ai-thresholds
```

Configuration changes SHALL be permission-controlled and audited.

---

# Audit APIs

## GET /audit-records

Retrieves audit records for authorized users.

```http
GET /api/v1/damage-intelligence/audit-records
```

Supported filters SHOULD include:

```text
objectType
objectId
actorId
action
createdFrom
createdTo
```

Audit APIs SHALL be permission-controlled.

---

# Idempotency Contract

Integration write APIs SHOULD support idempotency using:

```http
X-Idempotency-Key
```

Required behavior:

- Same tenant, same key, same payload SHALL return the original result.
- Same tenant, same key, different payload SHALL return `IDEMPOTENCY_CONFLICT`.
- Idempotency records SHALL be tenant-scoped.
- Idempotency records SHALL expire according to retention policy.

---

# OpenAPI Implementation Requirement

Emergent AI SHALL generate OpenAPI documentation from implemented APIs.

The OpenAPI output SHOULD include:

- Endpoint paths.
- HTTP methods.
- Request schemas.
- Response schemas.
- Error schemas.
- Security scheme.
- Required headers.
- Status codes.
- Examples where practical.

---

# Acceptance Criteria

## AC-DI-3400 — OpenAPI Contract Exists

Given the Damage Intelligence API is implemented, then a documented OpenAPI contract SHALL exist for the API surface.

## AC-DI-3401 — API Tenant Isolation

Given any tenant-scoped API is called, then tenant isolation SHALL be enforced.

## AC-DI-3402 — Secure Evidence APIs

Given evidence APIs are called, then evidence access SHALL be controlled and audited.

## AC-DI-3403 — Inspection APIs

Given inspection APIs are called, then inspection session lifecycle SHALL be supported.

## AC-DI-3404 — Image Upload APIs

Given image upload APIs are called, then secure upload and registration SHALL be supported.

## AC-DI-3405 — AI Analysis APIs

Given AI APIs are called, then AI analysis request, status, and findings SHALL be supported.

## AC-DI-3406 — Comparison APIs

Given comparison APIs are called, then damage comparison SHALL be supported.

## AC-DI-3407 — Review APIs

Given review APIs are called, then review queue and decision workflows SHALL be supported.

## AC-DI-3408 — Damage Case APIs

Given damage case APIs are called, then damage case workflows SHALL be supported.

## AC-DI-3409 — CROMS Integration APIs

Given CROMS integration APIs are called, then check-out, check-in, status, and damage summary APIs SHALL be supported.

## AC-DI-3410 — Maintenance Integration APIs

Given Maintenance integration APIs are called, then handoff and repair status APIs SHALL be supported.

## AC-DI-3411 — Reporting APIs

Given report APIs are called, then report generation and controlled report access SHALL be supported.

## AC-DI-3412 — Configuration APIs

Given configuration APIs are called, then permission-controlled configuration SHALL be supported.

## AC-DI-3413 — Audit APIs

Given audit APIs are called, then permission-controlled audit query SHALL be supported.

## AC-DI-3414 — Health APIs

Given health APIs are called, then service and dependency health SHALL be supported.

## AC-DI-3415 — API Idempotency

Given integration write APIs are retried, then idempotency SHALL prevent duplicate side effects.

## AC-DI-3416 — Safe API Errors

Given any API error occurs, then safe error responses SHALL be returned without secrets, stack traces, raw images, or unrestricted URLs.

---

# Requirement Registry Entries

Add these rows to:

```text
docs/99-Appendices/Requirement-Registry/DAMAGE.md
```

```markdown
| REQ-DI-3300 | OpenAPI Contract | Draft | DI-0034 | API contract for Damage Intelligence |
| REQ-DI-3301 | API Tenant Isolation | Draft | DI-0034 | APIs enforce tenant isolation and object authorization |
| REQ-DI-3302 | Secure Evidence APIs | Draft | DI-0034 | Controlled secure evidence access |
| REQ-DI-3303 | Inspection APIs | Draft | DI-0034 | Inspection session APIs |
| REQ-DI-3304 | Image Upload APIs | Draft | DI-0034 | Secure image upload and registration APIs |
| REQ-DI-3305 | AI Analysis APIs | Draft | DI-0034 | AI analysis request, status, and findings APIs |
| REQ-DI-3306 | Comparison APIs | Draft | DI-0034 | Damage comparison APIs |
| REQ-DI-3307 | Review APIs | Draft | DI-0034 | Review queue and decision APIs |
| REQ-DI-3308 | Damage Case APIs | Draft | DI-0034 | Damage case APIs |
| REQ-DI-3309 | CROMS Integration APIs | Draft | DI-0034 | CROMS check-out, check-in, and damage summary APIs |
| REQ-DI-3310 | Maintenance Integration APIs | Draft | DI-0034 | Maintenance handoff and repair status APIs |
| REQ-DI-3311 | Reporting APIs | Draft | DI-0034 | Report generation and access APIs |
| REQ-DI-3312 | Configuration APIs | Draft | DI-0034 | Permission-controlled configuration APIs |
| REQ-DI-3313 | Audit APIs | Draft | DI-0034 | Permission-controlled audit query APIs |
| REQ-DI-3314 | Health APIs | Draft | DI-0034 | Service and dependency health APIs |
| REQ-DI-3315 | API Idempotency | Draft | DI-0034 | Idempotency for integration and write APIs |
| REQ-DI-3316 | Safe API Errors | Draft | DI-0034 | Safe error responses without sensitive details |
```

---

# AI Implementation Contract

Emergent AI SHALL:

- Treat this document as the authoritative OpenAPI contract for Damage Intelligence.
- Use `/api/v1/damage-intelligence` as the API base path.
- Implement only documented APIs.
- Avoid undocumented endpoints.
- Enforce tenant isolation on every tenant-scoped endpoint.
- Enforce authorization on protected endpoints.
- Use safe response envelopes.
- Use safe error responses.
- Preserve auditability.
- Preserve AI advisory behavior.
- Preserve CROMS and Maintenance ownership boundaries.
- Avoid final customer charge, rental closure, actual repair cost, work order execution, Finance posting, Fleet, or vehicle asset lifecycle behavior.

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
- DI-0035 – QA Test Case Pack

---

# Revision History

| Version | Date | Description |
|----------|------|-------------|
| 1.0.0 | 2026-06-27 | Initial Damage Intelligence OpenAPI contract |
