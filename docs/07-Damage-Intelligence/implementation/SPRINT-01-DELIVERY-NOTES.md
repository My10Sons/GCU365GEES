---
id: "DI-SPRINT-01-DELIVERY-NOTES"
title: "Damage Intelligence Sprint 01 — Delivery Notes"
version: "1.0.0"
document_type: "Implementation Record"
document_class: "Delivery Notes"
status: "Draft"
classification: "Internal"
owner: "Riyadah Technology"
created: "2026-06-28"
updated: "2026-06-28"
authoritative: false
ai_consumable: true
related: "DI-SPRINT-01, DI-0004, DI-0007, DI-0011, DI-0012, DI-0014, DI-0015, DI-0031, DI-0034, DI-0035"
---

# Sprint 01 Delivery Notes — Production Inspection and Evidence Foundation

## Purpose

Record the as-built state of Sprint 01 (TASK-02) plus the two governance decisions taken
at sprint start so every subsequent sprint stays traceable to the repository and to the
human approvals captured in the chat session of 2026-06-28.

## Approved Decisions (Human-in-the-Loop)

| ID | Decision | Status |
|----|----------|--------|
| **DECISION-Sprint01-a** | Seed a **second realistic tenant** `RIYADAH-DOH-001` (Riyadah Technology, Doha primary branch) alongside the existing `TENANT-000001`. Both are seeded with admin + inspector principals so the AC-DI-S01 tenant-isolation tests are genuinely meaningful. | Approved 2026-06-28 |
| **DECISION-Sprint01-b** | Model external references (vehicle, rental agreement, branch, maintenance, work-order) as **opaque strings** for Sprint 01. Shape alignment with the actual CROMS / GCU365Maintenance reference data lives in Sprint 04 (TASK-05). | Approved 2026-06-28 |

These decisions are recorded here (delivery side) per the standing instruction not to modify `EMERGENT-AI-BLOCKERS-AND-DECISIONS.md`.

## As-Built — Backend

### New & updated files (Sprint 01)

```text
backend/
├── domain/
│   ├── enums/
│   │   ├── inspection_status.py        ← 6 statuses + ALLOWED_TRANSITIONS map (DRAFT → terminal)
│   │   ├── inspection_type.py          ← 5 inspection types + 4 source systems + image status
│   │   ├── capture_positions.py        ← 12 stable capture-position codes
│   │   └── audit_actions.py            ← 14 stable audit actions (auth + inspection + image + evidence + security)
│   └── models/
│       └── inspection.py               ← Pydantic response shapes (kept thin; storage is dict-based)
├── application/services/
│   ├── inspection_service.py           ← create / get / list / submit / patch-status + status-history writer
│   ├── image_service.py                ← upload-request / register / list-images / evidence-access-link
│   └── external_references_service.py  ← write-through to di_external_system_references
├── infrastructure/
│   ├── db/indexes.py                   ← +7 Sprint-01 tenant-scoped indexes
│   ├── seed/admin_seed.py              ← +RIYADAH-DOH-001 tenant with admin + inspector
│   ├── seed/capture_positions_seed.py  ← idempotent seed of 12 capture positions
│   └── storage/local_storage.py        ← action-scoped HMAC (PUT vs GET signatures cannot be cross-used)
├── api/routes/
│   ├── inspections.py                  ← 8 endpoints (POST/GET/list/submit/PATCH/upload-request/register/list-images)
│   ├── evidence.py                     ← POST /evidence/{evidenceId}/access-link
│   ├── storage_internal.py             ← PUT /internal/storage/upload + GET /internal/storage/access (signed-URL targets)
│   └── reference.py                    ← GET /reference/capture-positions
├── server.py                           ← register all Sprint-01 routes + capture-positions startup seed
├── tests/
│   ├── smoke_sprint01.py               ← 16-step end-to-end smoke (passes)
│   └── smoke_sprint00.py               ← Sprint 00 smoke (still green — regression preserved)
└── .env                                ← +DI_SEED_TENANT_ID_SECONDARY + 2 Doha credentials
```

### Implemented APIs (under `/api/v1/damage-intelligence`)

```
POST /inspection-sessions
GET  /inspection-sessions/{id}
GET  /inspection-sessions                            (page, pageSize, status, inspectionType,
                                                      externalVehicleRef, externalRentalAgreementRef,
                                                      externalBranchRef, createdFrom, createdTo)
POST /inspection-sessions/{id}/submit
PATCH /inspection-sessions/{id}/status               (CAPTURE_IN_PROGRESS | CANCELLED | FAILED only)
POST /inspection-sessions/{id}/images/upload-request
POST /inspection-sessions/{id}/images                (idempotent on uploadRequestId)
GET  /inspection-sessions/{id}/images
POST /evidence/{evidenceId}/access-link
GET  /reference/capture-positions
PUT  /internal/storage/upload?path=&exp=&sig=        (signed URL target; HMAC verified)
GET  /internal/storage/access?path=&exp=&sig=        (signed URL target; HMAC verified)
```

The signed URL HMAC keys the `action` ("PUT" vs "GET") so an upload signature cannot be
used to download and vice versa.

### MongoDB collections (Sprint 01 additions)

```
di_inspection_sessions              tenant-scoped (idx: createdAt, status, inspectionType, references.*)
di_inspection_status_history        append-only (idx: tenant + session + timestamp)
di_inspection_images                tenant-scoped (unique partial idx: (tenant, session, uploadRequestId))
di_evidence_references              tenant-scoped (idx: session, image)
di_upload_requests                  tenant-scoped (idx: session, createdAt, expiresAt)
di_external_system_references       write-through (idx: tenant + refType + refValue)
di_capture_positions                reference data — 12 codes seeded idempotently
```

(Sprint 00 collections — `di_users`, `di_login_attempts`, `di_audit_records`,
`di_integration_idempotency_records`, `di_schema_version`, `di_system_health_check` — are
unchanged.)

### Inspection status lifecycle

```
DRAFT ─┬─→ CAPTURE_IN_PROGRESS ─┬─→ EVIDENCE_REGISTERED ─→ SUBMITTED  (terminal)
       │   (auto on first        │   (auto on first registered
       │    upload-request)      │    image)
       │                         ├─→ CANCELLED (reason required) (terminal)
       │                         └─→ FAILED    (reason required) (terminal)
       ├─→ CANCELLED (reason required) (terminal)
       └─→ FAILED    (reason required) (terminal)
```

`PATCH /status` rejects `SUBMITTED` with `INVALID_STATUS_TRANSITION` and directs the
caller to `POST /submit`. All status changes write a `di_inspection_status_history` row.

### Audit events created (Sprint 01)

`INSPECTION_CREATED`, `INSPECTION_VIEWED`, `INSPECTION_LISTED`, `INSPECTION_SUBMITTED`,
`INSPECTION_STATUS_CHANGED`, `INSPECTION_CANCELLED`, `INSPECTION_FAILED`,
`IMAGE_UPLOAD_REQUESTED`, `IMAGE_REGISTERED`, `IMAGE_REGISTRATION_REJECTED`,
`EVIDENCE_ACCESS_LINK_CREATED`, `EVIDENCE_ACCESS_DENIED`, `TENANT_SCOPE_VIOLATION`,
`UNAUTHORIZED_ACCESS_ATTEMPT`. Every record carries `correlationId`, `actorId`,
`tenantId`, and a redacted `safeMetadata` blob (no raw images, no tokens, no secrets,
no permanent URLs).

## As-Built — Web

```text
frontend/src/
├── lib/inspections-api.js                     ← service layer wrapping all Sprint-01 endpoints
├── components/
│   ├── ui/Modal.jsx
│   └── inspection/
│       ├── StatusBadge.jsx                    ← pill rendering for the 6 statuses
│       ├── CreateInspectionModal.jsx
│       └── UploadImageModal.jsx               ← capture-position picker + signed-URL PUT + register
├── pages/
│   ├── Inspections.jsx                        ← list + filters + pagination + create
│   └── InspectionDetail.jsx                   ← references + lifecycle + images + actions
├── App.js                                     ← /inspections + /inspections/:id routes
└── constants/testIds.js                       ← extended with 40+ Sprint-01 testids
```

Web rules respected: role-aware action visibility (`Upload`, `Submit`, `Cancel` only shown when the principal has the required permission), evidence access opens through a freshly-issued time-limited signed link in a new tab (no long-lived URL stored in DOM), tenants are isolated end-to-end.

## Mobile (Flutter)

**Deferred** per DECISION-001d (Sprint 00). The Bearer + `X-Tenant-Id` contract is mobile-compatible whenever mobile work resumes.

## Sprint 01 Acceptance Criteria Status

| AC | Description | Status | Evidence |
|----|-------------|--------|----------|
| AC-DI-S01-001 | Inspection creation works | **PASS** | `POST /inspection-sessions` → status DRAFT + audit |
| AC-DI-S01-002 | Inspection retrieval is secure | **PASS** | cross-tenant GET returns `NOT_FOUND` (no information leak) |
| AC-DI-S01-003 | Inspection submission works | **PASS** | `POST /submit` → SUBMITTED + audit |
| AC-DI-S01-004 | Invalid status transitions rejected | **PASS** | `PATCH SUBMITTED` → 409 INVALID_STATUS_TRANSITION |
| AC-DI-S01-005 | Secure upload request works | **PASS** | HMAC-signed time-limited PUT URL |
| AC-DI-S01-006 | Uploaded image registration works | **PASS** | idempotent on `uploadRequestId` |
| AC-DI-S01-007 | Evidence access is controlled | **PASS** | time-limited HMAC URL; audit on every link issued |
| AC-DI-S01-008 | Public evidence access prevented | **PASS** | forged/unsigned URL → 403 FORBIDDEN |
| AC-DI-S01-009 | Tenant isolation enforced | **PASS** | T2 cannot read T1 sessions/evidence; cross-tenant header → TENANT_SCOPE_VIOLATION |
| AC-DI-S01-010 | Audit records created | **PASS** | 14 stable audit actions; correlationId on every row |
| AC-DI-S01-011 | Safe errors returned | **PASS** | DI-0034 envelope; no stack traces, no secrets |
| AC-DI-S01-012 | Sprint 01 smoke test passes | **PASS** | `backend/tests/smoke_sprint01.py` — 16/16 |

## Known Limitations (Sprint 01)

- Required-evidence-completeness rules (e.g., "all 4 required capture positions must have registered images before submit") are NOT enforced — submission allows any non-zero image count. Configurable enforcement is a Sprint 02/03 follow-up.
- Object storage remains local-disk per DECISION-001e. Production object store integration is Sprint 05 hardening.
- AI quality scoring is NOT applied during registration — Sprint 02 scope.
- CROMS / Maintenance write integrations remain stubs — Sprint 04 scope.
- Mobile (Flutter) connection is deferred.

## Sprint 01 Smoke Test

`backend/tests/smoke_sprint01.py` — 16 steps end-to-end against the live server. To run:

```bash
cd /app/backend && set -a && source .env && set +a && /root/.venv/bin/python tests/smoke_sprint01.py
```

Expected last line: `Sprint 01 production inspection and evidence foundation smoke test passed.`
