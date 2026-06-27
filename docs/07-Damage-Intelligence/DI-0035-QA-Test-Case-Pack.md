---
id: "DI-0035"
title: "Damage Intelligence QA Test Case Pack"
version: "1.0.0"
document_type: "Product Specification"
document_class: "QA Test Case Pack"
status: "Draft"
classification: "Internal"
owner: "Riyadah Technology"
reviewers: "Chief Enterprise Architect, Product Owner, Damage Intelligence Lead, QA Lead, Backend Lead, AI Engineering Lead, Security Lead, DevOps Lead, CROMS Lead, Maintenance Lead"
approvers: ""
created: "2026-06-27"
updated: "2026-06-27"
authoritative: true
ai_consumable: true
related: "DI-0001, DI-0002, DI-0004, DI-0005, DI-0006, DI-0011, DI-0012, DI-0014, DI-0015, DI-0017, DI-0018, DI-0019, DI-0020, DI-0021, DI-0030, DI-0031, DI-0032, DI-0033, DI-0034, PLATFORM-0005, GEES-0007, GEES-0009"
---

# Damage Intelligence QA Test Case Pack

## Executive Summary

This document defines the QA test case pack for Damage Intelligence.

Damage Intelligence is an image analysis and damage detection capability that integrates with existing GCU365 CROMS and GCU365Maintenance systems. It is not a replacement for CROMS, Maintenance, Fleet, Finance, or any existing enterprise system.

This QA pack provides structured test scenarios for:

- Inspection sessions.
- Image upload and evidence handling.
- Image quality validation.
- AI-assisted damage detection.
- Damage findings.
- Damage comparison.
- Human review.
- Damage cases.
- CROMS integration.
- GCU365Maintenance integration.
- Reports and evidence packages.
- Security and tenant isolation.
- Audit and traceability.
- Configuration.
- Monitoring.
- Arabic localization.
- Failure scenarios.
- Release smoke testing.

---

# Purpose

The purpose of this document is to provide QA-ready test cases for validating Damage Intelligence before production release.

This specification SHALL guide:

- Manual testing.
- Automated API testing.
- Integration testing.
- Regression testing.
- Security testing.
- AI validation testing.
- Release smoke testing.
- UAT preparation.
- Defect triage.
- Acceptance validation.

---

# Scope

## In Scope

This QA pack covers:

- Functional tests.
- API tests.
- Integration tests.
- Security tests.
- Tenant isolation tests.
- Evidence access tests.
- AI tests.
- Image quality tests.
- Comparison tests.
- Review workflow tests.
- Damage case tests.
- Report tests.
- Configuration tests.
- Audit tests.
- Monitoring tests.
- Localization tests.
- Negative tests.
- Failure and recovery tests.

## Out of Scope

This QA pack does not test:

- Full CROMS product behavior.
- Full GCU365Maintenance product behavior.
- Fleet Management.
- Finance or accounting posting.
- Final legal liability workflow.
- Final customer billing workflow.
- Final production SLA.
- Final AI vendor procurement.
- Full penetration testing report.

---

# QA Principles

Damage Intelligence QA SHALL follow these principles:

1. Validate the real scope only.
2. Treat CROMS and GCU365Maintenance as existing systems.
3. Validate integration boundaries.
4. Validate tenant isolation.
5. Validate evidence security.
6. Validate auditability.
7. Validate AI advisory behavior.
8. Validate idempotency.
9. Validate failure handling.
10. Validate release readiness.

---

# Test Case Format

Each test case SHOULD include:

- Test Case ID.
- Title.
- Priority.
- Type.
- Requirement references.
- Preconditions.
- Test steps.
- Expected result.
- Notes.

---

# Test Priority

| Priority | Meaning |
|---------|---------|
| Critical | Must pass before MVP or production release |
| High | Required for core release |
| Medium | Important but may be deferred with approval |
| Low | Enhancement or non-critical validation |

---

# Test Types

| Type | Description |
|------|-------------|
| Functional | Validates business behavior |
| API | Validates API contract |
| Integration | Validates CROMS or Maintenance integration |
| Security | Validates access control and protection |
| Audit | Validates traceability |
| AI | Validates AI detection and output behavior |
| Performance | Validates latency and capacity expectations |
| Localization | Validates Arabic and RTL behavior |
| Negative | Validates invalid or unsafe inputs |
| Smoke | Validates release readiness |

---

# Test Data Requirements

QA test data SHOULD include:

- Test tenants.
- Test users.
- Test roles.
- Test vehicles.
- Test rental agreement references from CROMS.
- Test maintenance request references.
- Test work order references.
- Test inspection sessions.
- Test clean vehicle images.
- Test damaged vehicle images.
- Blurry images.
- Low-light images.
- Obstructed images.
- Unsupported file types.
- Large image files.
- Baseline inspection images.
- Current inspection images.
- Arabic labels.
- Report templates.
- Integration idempotency keys.

Production customer data SHALL NOT be used in QA unless formally approved and anonymized.

---

# Environment Requirements

QA environments SHOULD include:

- Backend API environment.
- AI service environment.
- Object storage test container.
- Test database.
- Test identity provider.
- CROMS test or stub integration.
- GCU365Maintenance test or stub integration.
- Monitoring test environment.
- Test user roles.
- Test tenant data.

---

# TC-DI-0100 — Inspection Session Tests

## TC-DI-0101 — Create Inspection Session Successfully

Priority:
Critical

Type:
Functional, API

Requirement References:
REQ-DI-3303, REQ-DI-3103, REQ-DI-3008

Preconditions:

- Authorized user or CROMS service token exists.
- Tenant exists.
- Vehicle reference exists in source system.

Steps:

1. Send create inspection session request.
2. Include tenant ID.
3. Include vehicle reference.
4. Include inspection type.
5. Include CROMS rental reference where applicable.

Expected Result:

- Inspection session is created.
- Unique inspection session ID is returned.
- Status is `DRAFT`.
- Tenant ID is correctly associated.
- External references are stored as references.
- Audit record is created.

---

## TC-DI-0102 — Reject Inspection Creation Without Tenant

Priority:
Critical

Type:
Negative, Security, API

Requirement References:
REQ-DI-3301, REQ-DI-1301

Steps:

1. Send create inspection request without tenant context.

Expected Result:

- Request is rejected.
- Error is safe.
- No inspection is created.
- No cross-tenant default is assumed.

---

## TC-DI-0103 — Submit Inspection Successfully

Priority:
Critical

Type:
Functional, API

Requirement References:
REQ-DI-0303, REQ-DI-3303

Preconditions:

- Inspection exists.
- Required images are uploaded or approved override exists.

Steps:

1. Submit inspection session.
2. Set `triggerAnalysis` to true.

Expected Result:

- Status changes to `SUBMITTED`.
- Analysis workflow is triggered where configured.
- Audit record is created.
- Invalid state transition does not occur.

---

## TC-DI-0104 — Reject Invalid State Transition

Priority:
High

Type:
Negative, API

Requirement References:
REQ-DI-0304

Steps:

1. Attempt to submit an already closed inspection.
2. Attempt to return inspection to invalid previous status.

Expected Result:

- API rejects invalid transition.
- Safe error code is returned.
- Existing inspection state remains unchanged.
- Attempt is logged or audited where required.

---

# TC-DI-0200 — Image Upload and Evidence Tests

## TC-DI-0201 — Generate Secure Upload Request

Priority:
Critical

Type:
Functional, API, Security

Requirement References:
REQ-DI-3304, REQ-DI-3302

Steps:

1. Request upload URL for an inspection image.
2. Provide valid capture position.
3. Provide valid content type and file size.

Expected Result:

- Upload request is created.
- Time-limited upload URL is returned.
- Storage path is tenant-isolated.
- No permanent public URL is returned.
- Request is logged or audited where required.

---

## TC-DI-0202 — Register Uploaded Image Successfully

Priority:
Critical

Type:
Functional, API

Requirement References:
REQ-DI-3304, REQ-DI-1402

Preconditions:

- Upload request exists.
- Image object exists in test storage.

Steps:

1. Register uploaded image.
2. Provide upload request ID.
3. Provide capture position.
4. Provide storage object reference.

Expected Result:

- Image is registered.
- Image is linked to inspection.
- Capture position is saved.
- Metadata is saved.
- Audit record is created.

---

## TC-DI-0203 — Reject Image Registration for Wrong Tenant Path

Priority:
Critical

Type:
Security, Negative

Requirement References:
REQ-DI-3301, REQ-DI-3302

Steps:

1. Attempt to register image using another tenant storage path.

Expected Result:

- Registration is rejected.
- Tenant scope violation is returned.
- No evidence record is created.
- Security event is logged.

---

## TC-DI-0204 — View Evidence as Authorized User

Priority:
Critical

Type:
Security, Functional

Requirement References:
REQ-DI-3302, REQ-DI-1305

Steps:

1. Login as authorized reviewer.
2. Request evidence access link.
3. Open evidence link before expiry.

Expected Result:

- Access is granted.
- Link is time-limited.
- Evidence is visible only to authorized user.
- Access is audited where required.

---

## TC-DI-0205 — Deny Unauthorized Evidence Access

Priority:
Critical

Type:
Security, Negative

Requirement References:
REQ-DI-3302, REQ-DI-2211

Steps:

1. Login as unauthorized user.
2. Attempt to access evidence from another tenant or unauthorized inspection.

Expected Result:

- Access is denied.
- No evidence is exposed.
- Attempt is logged or audited.
- Security monitoring can detect the attempt.

---

# TC-DI-0300 — Image Quality Tests

## TC-DI-0301 — Pass Valid Image Quality Check

Priority:
High

Type:
Functional, AI

Requirement References:
REQ-DI-3104, REQ-DI-0401

Steps:

1. Upload valid image.
2. Run image quality validation.

Expected Result:

- Quality status is `PASSED`.
- Quality score is returned.
- No recapture is required.

---

## TC-DI-0302 — Fail Blurry Image

Priority:
High

Type:
Functional, AI, Negative

Requirement References:
REQ-DI-0401, REQ-DI-0605

Steps:

1. Upload blurry image.
2. Run quality validation.

Expected Result:

- Quality status is `FAILED`.
- Failure reason includes `BLURRY_IMAGE`.
- Recapture is recommended.
- Result is stored.

---

## TC-DI-0303 — Fail Low-Light Image

Priority:
High

Type:
Functional, AI, Negative

Requirement References:
REQ-DI-0401, REQ-DI-0605

Steps:

1. Upload low-light image.
2. Run quality validation.

Expected Result:

- Quality status is `FAILED`.
- Failure reason includes `LOW_LIGHT`.
- Recapture is recommended.

---

## TC-DI-0304 — Reject Unsupported File Type

Priority:
High

Type:
API, Negative, Security

Requirement References:
REQ-DI-3304, REQ-DI-3316

Steps:

1. Request upload for unsupported file type.
2. Attempt to register unsupported file.

Expected Result:

- Request or registration is rejected.
- Safe error is returned.
- No unsafe file is processed.

---

# TC-DI-0400 — AI Damage Detection Tests

## TC-DI-0401 — Request AI Analysis Successfully

Priority:
High

Type:
AI, API, Functional

Requirement References:
REQ-DI-3305, REQ-DI-3104

Preconditions:

- Inspection exists.
- Images are registered.
- Images pass quality validation or policy allows analysis.

Steps:

1. Request AI analysis.
2. Check analysis status.

Expected Result:

- AI analysis is queued.
- Analysis ID is returned.
- Status is trackable.
- Audit record is created.

---

## TC-DI-0402 — Store AI Finding

Priority:
High

Type:
AI, Functional

Requirement References:
REQ-DI-3305, REQ-DI-0403

Steps:

1. Run AI analysis on image with visible damage.
2. Retrieve AI findings.

Expected Result:

- AI finding is created.
- Damage type code is populated.
- Vehicle area code is populated.
- Confidence score is populated.
- Finding is linked to image and inspection.
- Finding is advisory.

---

## TC-DI-0403 — AI Finding Is Advisory

Priority:
Critical

Type:
AI, Governance

Requirement References:
REQ-DI-3007, REQ-DI-3305

Steps:

1. Retrieve AI finding.
2. Inspect finding payload and UI display.

Expected Result:

- AI output is marked or treated as advisory.
- AI does not assign final liability.
- AI does not assign final customer charge.
- AI does not determine actual repair cost.
- AI does not close rental or execute work order.

---

## TC-DI-0404 — Route Low-Confidence AI Finding to Review

Priority:
Critical

Type:
AI, Functional

Requirement References:
REQ-DI-0406, REQ-DI-3203

Steps:

1. Configure low-confidence threshold.
2. Run AI analysis producing low-confidence finding.
3. Check review queue.

Expected Result:

- Finding is routed to review.
- Review item is visible to authorized reviewer.
- Routing is auditable.

---

## TC-DI-0405 — Handle AI Service Failure

Priority:
High

Type:
AI, Failure

Requirement References:
REQ-DI-2707, REQ-DI-3104

Steps:

1. Simulate AI service failure.
2. Request analysis.

Expected Result:

- Failure is handled safely.
- Inspection evidence remains preserved.
- Analysis status indicates failure or retry.
- Manual review fallback is available where configured.
- Failure is logged and monitored.

---

# TC-DI-0500 — Damage Comparison Tests

## TC-DI-0501 — Select Baseline Evidence

Priority:
High

Type:
Functional

Requirement References:
REQ-DI-3306, REQ-DI-0500

Steps:

1. Create check-out inspection.
2. Create check-in inspection.
3. Request comparison using check-out as baseline.

Expected Result:

- Baseline inspection is selected.
- Baseline reference is recorded.
- Comparison request is queued or completed.

---

## TC-DI-0502 — Detect New Damage Candidate

Priority:
High

Type:
AI, Functional

Requirement References:
REQ-DI-0501, REQ-DI-3306

Steps:

1. Use baseline image without damage.
2. Use current image with visible damage.
3. Run comparison.

Expected Result:

- Comparison outcome includes `NEW`.
- Confidence score is recorded.
- Review required flag is applied where configured.

---

## TC-DI-0503 — Detect Pre-Existing Damage

Priority:
High

Type:
AI, Functional

Requirement References:
REQ-DI-0502

Steps:

1. Use baseline image with visible damage.
2. Use current image with same visible damage.
3. Run comparison.

Expected Result:

- Comparison outcome includes `PRE_EXISTING`.
- Result is linked to baseline and current evidence.

---

## TC-DI-0504 — Missing Baseline Does Not Confirm New Damage

Priority:
Critical

Type:
Negative, Governance

Requirement References:
REQ-DI-0508, BR-DI-0104

Steps:

1. Create inspection without baseline.
2. Run comparison.

Expected Result:

- System returns missing baseline or NotComparable.
- System does not automatically confirm new damage.
- Review or additional evidence may be required.

---

## TC-DI-0505 — NotComparable Result

Priority:
High

Type:
Functional, Negative

Requirement References:
REQ-DI-0508

Steps:

1. Use poor baseline image.
2. Run comparison.

Expected Result:

- Outcome is `NOT_COMPARABLE`.
- Reason is recorded.
- No final damage liability is assigned.

---

# TC-DI-0600 — Human Review Tests

## TC-DI-0601 — View Review Queue

Priority:
High

Type:
Functional, Security

Requirement References:
REQ-DI-3307, REQ-DI-3203

Steps:

1. Login as authorized reviewer.
2. Open review queue.

Expected Result:

- Pending review items are visible.
- Queue respects tenant and branch scope.
- Unauthorized items are hidden.

---

## TC-DI-0602 — Confirm Damage Finding

Priority:
Critical

Type:
Functional, Audit

Requirement References:
REQ-DI-3307, REQ-DI-1408

Steps:

1. Open pending review item.
2. Confirm finding with reason.
3. Save decision.

Expected Result:

- Review decision is saved.
- Finding status is updated.
- Audit record is created.
- Decision is traceable.

---

## TC-DI-0603 — Reject Damage Finding

Priority:
High

Type:
Functional, Audit

Requirement References:
REQ-DI-3307

Steps:

1. Open pending review item.
2. Reject finding with reason.
3. Save decision.

Expected Result:

- Finding is rejected.
- Reason is stored.
- Audit record is created.

---

## TC-DI-0604 — Edit Damage Finding During Review

Priority:
High

Type:
Functional, Audit

Requirement References:
REQ-DI-3307

Steps:

1. Open pending review item.
2. Change damage type, area, or severity.
3. Save decision.

Expected Result:

- Updated values are saved.
- Previous values are traceable.
- Audit record is created.

---

# TC-DI-0700 — Damage Case Tests

## TC-DI-0701 — Create Damage Case

Priority:
High

Type:
Functional, API

Requirement References:
REQ-DI-3308, REQ-DI-3105

Steps:

1. Create damage case from confirmed finding.
2. Link evidence and inspection.

Expected Result:

- Damage case is created.
- Case ID is returned.
- Evidence is linked.
- Case status is `OPEN`.
- Audit record is created.

---

## TC-DI-0702 — Update Damage Case Status

Priority:
High

Type:
Functional, Audit

Requirement References:
REQ-DI-3308

Steps:

1. Open damage case.
2. Update status.
3. Provide reason.

Expected Result:

- Status changes.
- Status history is preserved.
- Audit record is created.

---

## TC-DI-0703 — Prevent Duplicate Damage Case

Priority:
Medium

Type:
Negative, Functional

Requirement References:
REQ-DI-3308

Steps:

1. Attempt to create duplicate case for same finding and context.

Expected Result:

- Duplicate is prevented or flagged.
- Existing case reference is returned where applicable.

---

# TC-DI-0800 — CROMS Integration Tests

## TC-DI-0801 — CROMS Check-Out Inspection Request

Priority:
Critical

Type:
Integration, API

Requirement References:
REQ-DI-3309, REQ-DI-3004

Steps:

1. Send CROMS check-out inspection request.
2. Include rental agreement reference.
3. Include vehicle reference.
4. Include idempotency key.

Expected Result:

- Inspection session is created or returned.
- Inspection type is `CHECK_OUT`.
- Rental agreement is stored as reference.
- CROMS remains owner of rental lifecycle.
- Audit record is created.

---

## TC-DI-0802 — CROMS Check-In Inspection Request

Priority:
Critical

Type:
Integration, API

Requirement References:
REQ-DI-3309, REQ-DI-3004

Steps:

1. Send CROMS check-in inspection request.
2. Include rental agreement reference.
3. Include baseline inspection reference where available.

Expected Result:

- Check-in inspection is created.
- Baseline reference is stored where provided.
- Damage comparison can be triggered where configured.
- CROMS remains owner of rental closure.

---

## TC-DI-0803 — Get Rental Damage Summary

Priority:
Critical

Type:
Integration, API

Requirement References:
REQ-DI-3309

Steps:

1. Complete check-out and check-in inspections.
2. Generate damage findings.
3. Request rental damage summary.

Expected Result:

- Summary is returned to CROMS.
- Summary includes inspection and damage context.
- Summary does not decide final customer charge.
- Rental closure remains with CROMS.

---

## TC-DI-0804 — Duplicate CROMS Request Uses Idempotency

Priority:
High

Type:
Integration, API, Negative

Requirement References:
REQ-DI-3315

Steps:

1. Send same CROMS request twice with same idempotency key and same payload.

Expected Result:

- Same result is returned.
- No duplicate inspection is created.

---

## TC-DI-0805 — Idempotency Conflict

Priority:
High

Type:
Integration, Negative

Requirement References:
REQ-DI-3315

Steps:

1. Send CROMS request with idempotency key.
2. Send different payload with same idempotency key.

Expected Result:

- API returns `IDEMPOTENCY_CONFLICT`.
- No duplicate object is created.

---

# TC-DI-0900 — Maintenance Integration Tests

## TC-DI-0901 — Send Damage Case to Maintenance

Priority:
High

Type:
Integration, API

Requirement References:
REQ-DI-3310, REQ-DI-3005

Steps:

1. Create damage case.
2. Send Maintenance handoff request.

Expected Result:

- Maintenance handoff is created.
- Evidence package reference is included.
- Damage Intelligence does not create work order execution.
- Request is audited.

---

## TC-DI-0902 — Receive Work Order Reference

Priority:
High

Type:
Integration, API

Requirement References:
REQ-DI-3310

Steps:

1. Send work order reference callback from GCU365Maintenance.
2. Include damage case ID and work order ID.

Expected Result:

- Work order reference is stored.
- Work order remains owned by GCU365Maintenance.
- Update is audited.

---

## TC-DI-0903 — Receive Repair Status Update

Priority:
Medium

Type:
Integration, API

Requirement References:
REQ-DI-3310

Steps:

1. Send repair status update from GCU365Maintenance.

Expected Result:

- Repair status is stored as reference context.
- Actual repair cost is stored only as reference where provided.
- Damage Intelligence does not own actual repair cost.

---

## TC-DI-0904 — Duplicate Maintenance Handoff Prevention

Priority:
High

Type:
Integration, Negative

Requirement References:
REQ-DI-3315

Steps:

1. Send same Maintenance handoff request twice with same idempotency key.

Expected Result:

- Same handoff result is returned.
- No duplicate Maintenance handoff is created.

---

# TC-DI-1000 — Reporting Tests

## TC-DI-1001 — Generate Inspection Summary Report

Priority:
High

Type:
Functional, API

Requirement References:
REQ-DI-3311, REQ-DI-1500

Steps:

1. Complete inspection.
2. Request inspection summary report.

Expected Result:

- Report is generated.
- Report includes inspection summary.
- Report includes controlled evidence references.
- Report generation is audited.

---

## TC-DI-1002 — Generate Damage Comparison Report

Priority:
High

Type:
Functional

Requirement References:
REQ-DI-3311

Steps:

1. Complete comparison.
2. Request comparison report.

Expected Result:

- Report includes comparison outcome.
- Report labels uncertain and NotComparable outcomes.
- Report does not assign final liability.

---

## TC-DI-1003 — Report Access Is Controlled

Priority:
Critical

Type:
Security

Requirement References:
REQ-DI-3311, REQ-DI-3302

Steps:

1. Generate report.
2. Request report access link as authorized user.
3. Attempt access as unauthorized user.

Expected Result:

- Authorized access succeeds.
- Unauthorized access fails.
- Access link is time-limited.
- Report access is audited.

---

# TC-DI-1100 — Security and Tenant Isolation Tests

## TC-DI-1101 — Cross-Tenant Inspection Access Denied

Priority:
Critical

Type:
Security, Negative

Requirement References:
REQ-DI-3301

Steps:

1. Create inspection under Tenant A.
2. Login as Tenant B user.
3. Attempt to access Tenant A inspection.

Expected Result:

- Access is denied.
- No data is exposed.
- Security event is logged.

---

## TC-DI-1102 — Cross-Tenant Evidence Access Denied

Priority:
Critical

Type:
Security, Negative

Requirement References:
REQ-DI-3302

Steps:

1. Create evidence under Tenant A.
2. Attempt access from Tenant B.

Expected Result:

- Access is denied.
- Evidence is not exposed.
- Attempt is logged or audited.

---

## TC-DI-1103 — No Secrets in API Error

Priority:
Critical

Type:
Security, Negative

Requirement References:
REQ-DI-3316

Steps:

1. Trigger server-side error condition.
2. Inspect API response.

Expected Result:

- Error does not include stack trace.
- Error does not include storage paths.
- Error does not include secrets.
- Error does not include tokens.
- Error does not include raw evidence.

---

## TC-DI-1104 — Role Permission Enforcement

Priority:
Critical

Type:
Security

Requirement References:
REQ-DI-3107

Steps:

1. Login as user without review permission.
2. Attempt to record review decision.

Expected Result:

- Request is denied.
- No review decision is created.
- Attempt is logged.

---

# TC-DI-1200 — Audit and Traceability Tests

## TC-DI-1201 — Audit Inspection Creation

Priority:
Critical

Type:
Audit

Requirement References:
REQ-DI-3108, REQ-DI-1400

Steps:

1. Create inspection session.
2. Search audit records.

Expected Result:

- Audit record exists.
- Actor, action, object, tenant, timestamp, and correlation ID are recorded.

---

## TC-DI-1202 — Audit Evidence Access

Priority:
Critical

Type:
Audit, Security

Requirement References:
REQ-DI-3108

Steps:

1. Access evidence as authorized user.
2. Search audit records.

Expected Result:

- Evidence access audit record exists where required.
- Access purpose is recorded.
- No raw image data appears in audit record.

---

## TC-DI-1203 — Audit Review Decision

Priority:
Critical

Type:
Audit

Requirement References:
REQ-DI-3108

Steps:

1. Record review decision.
2. Search audit records.

Expected Result:

- Review decision is audited.
- Previous and new status are traceable where applicable.

---

# TC-DI-1300 — Configuration Tests

## TC-DI-1301 — Update AI Threshold with Permission

Priority:
High

Type:
Functional, Security

Requirement References:
REQ-DI-3312, REQ-DI-2318

Steps:

1. Login as authorized admin.
2. Update AI threshold configuration.

Expected Result:

- Configuration is saved or moved to approval state.
- Version is created.
- Change is audited.

---

## TC-DI-1302 — Reject Configuration Update Without Permission

Priority:
Critical

Type:
Security, Negative

Requirement References:
REQ-DI-3312

Steps:

1. Login as non-admin user.
2. Attempt to update AI threshold.

Expected Result:

- Request is denied.
- No configuration change occurs.
- Attempt is logged.

---

## TC-DI-1303 — No Secrets in Configuration Output

Priority:
Critical

Type:
Security

Requirement References:
REQ-DI-2318

Steps:

1. Retrieve integration configuration.
2. Inspect API response.

Expected Result:

- Secrets are masked or omitted.
- Tokens and API keys are not exposed.

---

# TC-DI-1400 — Monitoring and Operations Tests

## TC-DI-1401 — Health Endpoint Returns Service Status

Priority:
High

Type:
Smoke, Operational

Requirement References:
REQ-DI-3314, REQ-DI-3109

Steps:

1. Call service health endpoint.

Expected Result:

- Health status is returned.
- Response does not expose secrets.
- Service version is visible where configured.

---

## TC-DI-1402 — Dependency Health Endpoint

Priority:
High

Type:
Operational

Requirement References:
REQ-DI-3314

Steps:

1. Call dependency health endpoint.

Expected Result:

- Database status is visible.
- Storage status is visible.
- AI service status is visible.
- Integration status is visible.
- No sensitive configuration is exposed.

---

## TC-DI-1403 — Integration Failure Alert

Priority:
High

Type:
Operational, Integration

Requirement References:
REQ-DI-3109

Steps:

1. Simulate CROMS or Maintenance integration failure.
2. Check monitoring dashboard or alert output.

Expected Result:

- Failure is visible.
- Correlation ID is available.
- Alert does not expose secrets or sensitive payload.

---

# TC-DI-1500 — Localization and Arabic Tests

## TC-DI-1501 — Arabic Capture Instructions

Priority:
Medium

Type:
Localization

Requirement References:
REQ-DI-2405

Steps:

1. Set language to Arabic.
2. Open mobile capture screen.

Expected Result:

- Capture instructions appear in Arabic.
- RTL layout is applied where supported.
- Stable capture codes remain unchanged internally.

---

## TC-DI-1502 — Arabic Report Generation

Priority:
Medium

Type:
Localization, Reporting

Requirement References:
REQ-DI-2407

Steps:

1. Request Arabic report.
2. Open generated report.

Expected Result:

- Report labels appear in Arabic where supported.
- RTL layout is applied.
- Stable codes remain language-neutral.
- Evidence access remains controlled.

---

## TC-DI-1503 — Missing Translation Fallback

Priority:
Medium

Type:
Localization, Negative

Requirement References:
REQ-DI-2411

Steps:

1. Remove or simulate missing translation.
2. Open affected UI or report.

Expected Result:

- Safe fallback label is shown.
- Workflow does not fail.
- Stable code remains available.

---

# TC-DI-1600 — Performance Tests

## TC-DI-1601 — Image Upload Performance

Priority:
Medium

Type:
Performance

Requirement References:
REQ-DI-1910

Steps:

1. Upload supported image sizes.
2. Measure upload request and registration response times.

Expected Result:

- Upload request responds within agreed threshold.
- Registration responds within agreed threshold.
- No timeout occurs under expected load.

---

## TC-DI-1602 — AI Queue Throughput

Priority:
Medium

Type:
Performance, AI

Requirement References:
REQ-DI-1910, REQ-DI-2204

Steps:

1. Submit multiple inspections for AI analysis.
2. Monitor queue and processing time.

Expected Result:

- Queue processes within agreed threshold.
- Failures are visible.
- Backlog alert triggers where threshold is exceeded.

---

## TC-DI-1603 — Report Generation Performance

Priority:
Medium

Type:
Performance

Requirement References:
REQ-DI-1910, REQ-DI-3311

Steps:

1. Generate reports with different evidence counts.
2. Measure generation time.

Expected Result:

- Report generation completes within agreed threshold.
- Long-running reports are handled asynchronously where needed.

---

# TC-DI-1700 — Release Smoke Tests

## TC-DI-1701 — Production Smoke Test

Priority:
Critical

Type:
Smoke

Requirement References:
REQ-DI-2512

Steps:

1. Check health endpoint.
2. Create test inspection.
3. Upload test image.
4. Register image.
5. Run quality check.
6. Request AI analysis where enabled.
7. Generate basic report.
8. Verify audit record.
9. Verify tenant isolation with negative access test.

Expected Result:

- All critical smoke steps pass.
- No security issue is observed.
- No public evidence URL is exposed.
- Audit records exist.

---

# Defect Severity

| Severity | Meaning |
|---------|---------|
| Blocker | Prevents release or critical workflow |
| Critical | Security, tenant isolation, evidence, audit, or integration boundary failure |
| High | Core workflow failure |
| Medium | Important defect with workaround |
| Low | Minor UI, wording, or non-critical issue |

---

# Release Exit Criteria

Damage Intelligence SHALL NOT be released to production unless:

- Critical and blocker defects are resolved or formally accepted.
- Tenant isolation tests pass.
- Evidence security tests pass.
- Audit tests pass.
- CROMS integration tests pass where in release scope.
- Maintenance integration tests pass where in release scope.
- AI advisory boundary tests pass where AI is enabled.
- Smoke tests pass.
- Security review is complete.
- Product owner approval is recorded.

---

# QA Acceptance Criteria

## AC-DI-3500 — QA Test Pack Exists

Given Damage Intelligence implementation is planned, then a QA test case pack SHALL exist.

## AC-DI-3501 — Scope Validation

Given QA tests are reviewed, then tests SHALL validate that Damage Intelligence does not replace CROMS, GCU365Maintenance, Fleet, Finance, or vehicle asset management.

## AC-DI-3502 — Security Validation

Given QA testing is executed, then tenant isolation, evidence access, authorization, and safe error handling SHALL be tested.

## AC-DI-3503 — Integration Validation

Given integration testing is executed, then CROMS and Maintenance ownership boundaries SHALL be validated.

## AC-DI-3504 — AI Advisory Validation

Given AI testing is executed, then AI outputs SHALL be validated as advisory and not final authority.

## AC-DI-3505 — Audit Validation

Given critical workflow testing is executed, then required audit records SHALL be verified.

## AC-DI-3506 — Release Smoke Validation

Given production release is planned, then smoke tests SHALL be executed and passed or formally accepted by release governance.

---

# Normative Requirements

## Requirement

ID: REQ-DI-3400

Title:
QA Test Case Pack

Statement:
Damage Intelligence SHALL define a QA test case pack covering functional, API, integration, security, audit, AI, reporting, localization, performance, negative, and smoke tests.

Priority:
Critical

Verification:
QA Review

---

## Requirement

ID: REQ-DI-3401

Title:
Inspection Test Coverage

Statement:
Damage Intelligence QA SHALL cover inspection session creation, viewing, submission, status transitions, and invalid state handling.

Priority:
Critical

Verification:
QA Execution

---

## Requirement

ID: REQ-DI-3402

Title:
Evidence Test Coverage

Statement:
Damage Intelligence QA SHALL cover image upload, image registration, evidence access, tenant-isolated storage, and unauthorized access denial.

Priority:
Critical

Verification:
QA Execution

---

## Requirement

ID: REQ-DI-3403

Title:
Image Quality Test Coverage

Statement:
Damage Intelligence QA SHOULD cover image quality validation including valid images, blurry images, low-light images, unsupported file types, and recapture recommendations.

Priority:
High

Verification:
QA Execution

---

## Requirement

ID: REQ-DI-3404

Title:
AI Test Coverage

Statement:
Damage Intelligence QA SHOULD cover AI analysis request, AI finding creation, confidence score, uncertainty, low-confidence routing, advisory behavior, and AI failure handling.

Priority:
High

Verification:
QA Execution

---

## Requirement

ID: REQ-DI-3405

Title:
Comparison Test Coverage

Statement:
Damage Intelligence QA SHOULD cover baseline selection, new damage, pre-existing damage, changed damage, repaired damage, missing baseline, and NotComparable outcomes.

Priority:
High

Verification:
QA Execution

---

## Requirement

ID: REQ-DI-3406

Title:
Review and Case Test Coverage

Statement:
Damage Intelligence QA SHOULD cover review queue, review decisions, review edits, escalation, damage case creation, damage case status changes, and duplicate case prevention.

Priority:
High

Verification:
QA Execution

---

## Requirement

ID: REQ-DI-3407

Title:
CROMS Integration Test Coverage

Statement:
Damage Intelligence QA SHALL cover CROMS check-out, check-in, rental damage summary, idempotency, and ownership boundary behavior.

Priority:
Critical

Verification:
Integration QA

---

## Requirement

ID: REQ-DI-3408

Title:
Maintenance Integration Test Coverage

Statement:
Damage Intelligence QA SHALL cover Maintenance handoff, work order reference, repair status update, idempotency, and ownership boundary behavior.

Priority:
Critical

Verification:
Integration QA

---

## Requirement

ID: REQ-DI-3409

Title:
Security Test Coverage

Statement:
Damage Intelligence QA SHALL cover authentication, authorization, tenant isolation, evidence security, role permissions, safe errors, and secret exposure prevention.

Priority:
Critical

Verification:
Security QA

---

## Requirement

ID: REQ-DI-3410

Title:
Audit Test Coverage

Statement:
Damage Intelligence QA SHALL verify audit records for critical inspection, evidence, AI, review, case, report, integration, configuration, and security actions.

Priority:
Critical

Verification:
Audit QA

---

## Requirement

ID: REQ-DI-3411

Title:
Reporting Test Coverage

Statement:
Damage Intelligence QA SHOULD cover report generation, report access, report authorization, report privacy, report expiration, and report audit.

Priority:
High

Verification:
Reporting QA

---

## Requirement

ID: REQ-DI-3412

Title:
Configuration Test Coverage

Statement:
Damage Intelligence QA SHOULD cover authorized configuration changes, unauthorized changes, audit, versioning, approval, and secret masking.

Priority:
High

Verification:
Configuration QA

---

## Requirement

ID: REQ-DI-3413

Title:
Monitoring Test Coverage

Statement:
Damage Intelligence QA SHOULD cover health endpoints, dependency health, integration failure visibility, AI queue visibility, and alert privacy.

Priority:
Medium

Verification:
Operational QA

---

## Requirement

ID: REQ-DI-3414

Title:
Localization Test Coverage

Statement:
Damage Intelligence QA SHOULD cover Arabic capture instructions, Arabic reports, RTL behavior, missing translation fallback, and Arabic export readability where enabled.

Priority:
Medium

Verification:
Localization QA

---

## Requirement

ID: REQ-DI-3415

Title:
Release Smoke Tests

Statement:
Damage Intelligence SHALL define release smoke tests for critical health, inspection, evidence, AI where enabled, reporting, audit, and tenant isolation.

Priority:
Critical

Verification:
Release Smoke Test

---

# Business Rules

## BR-DI-3000 — QA Must Validate Scope

QA SHALL validate that Damage Intelligence remains an image analysis and damage detection capability for existing CROMS and GCU365Maintenance.

---

## BR-DI-3001 — Security Failures Block Release

Tenant isolation failure, unauthorized evidence access, secret exposure, or public evidence URL exposure SHALL block release unless formally accepted by security governance.

---

## BR-DI-3002 — Audit Failure Blocks Critical Release

Missing audit records for critical actions SHALL block release unless formally accepted by governance.

---

## BR-DI-3003 — AI Final Authority Must Fail QA

Any behavior where AI independently decides final liability, final customer charge, actual repair cost, rental closure, or work order execution SHALL fail QA.

---

## BR-DI-3004 — Integration Duplicate Creation Must Fail QA

Duplicate inspections, damage cases, reports, or Maintenance handoffs caused by retry or replay SHALL fail integration QA unless documented and accepted.

---

## BR-DI-3005 — Release Requires Smoke Test

Every production release SHALL pass smoke tests or have documented formal risk acceptance.

---

# AI Implementation Contract

AI development agents SHALL:

- Treat this document as the authoritative QA test case pack for Damage Intelligence.
- Preserve all test case IDs, requirement IDs, acceptance criterion IDs, and business rule IDs.
- Generate manual test cases, automated test scripts, API tests, integration tests, regression suites, and release smoke tests consistent with this document.
- Preserve the scope boundary that Damage Intelligence is image analysis and damage detection for existing GCU365 CROMS and GCU365Maintenance.
- Never generate QA expectations that require Damage Intelligence to replace CROMS, replace Maintenance, build Fleet, own Finance, own rental closure, own actual repair cost, or own work order execution.
- Preserve tenant isolation, evidence security, auditability, AI advisory boundaries, idempotency, and safe error requirements.
- Raise ambiguity where a test case conflicts with DI-0031 or existing system ownership.

---

# References

- DI-0004 – Inspection Workflow
- DI-0005 – AI Damage Detection
- DI-0006 – Damage Comparison
- DI-0011 – API Specification
- DI-0012 – Domain Model
- DI-0014 – Security and Privacy
- DI-0015 – Audit and Traceability
- DI-0017 – Integration with CROMS
- DI-0018 – Integration with Maintenance
- DI-0019 – Acceptance Criteria
- DI-0020 – Test Strategy
- DI-0021 – Implementation Readiness Checklist
- DI-0030 – Glossary and Terminology
- DI-0031 – Existing System Integration Scope
- DI-0032 – Implementation Plan
- DI-0033 – User Stories and Backlog
- DI-0034 – OpenAPI Contract
- PLATFORM-0005 – GEES Core and Application Architecture
- GEES-0007 – Enterprise Security Standard
- GEES-0009 – Traceability Standard

---

# Revision History

| Version | Date | Description |
|----------|------|-------------|
| 1.0.0 | 2026-06-27 | Initial Damage Intelligence QA Test Case Pack |
