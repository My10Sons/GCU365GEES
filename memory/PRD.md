# Damage Intelligence — Product Requirements Document (PRD)

## Source of Truth

The authoritative repository is `/app/docs/07-Damage-Intelligence/`. This PRD is
the **delivery side** of that documentation set, recording what has been built,
when, and how each line of code traces back to a repository document.

Do **not** treat this PRD as a substitute for the DI-00xx specifications.

## Original Problem Statement

> Start from `EMERGENT-AI-START-HERE.md`. Do not write code until TASK-00
> Repository Understanding and Scope Lock is complete. Use the repository as the
> source of truth for every line of code.

## Product

Damage Intelligence is a production-ready, multi-tenant, image-analysis and
damage-detection capability for **existing** GCU365 CROMS (rental) and
GCU365Maintenance (workshop) systems. It owns inspection evidence, AI
**advisory** findings, damage comparison, human review, damage cases, evidence
packages, damage reports, and the related audit trail.

It does **not** own rental lifecycle, customer charge, work order execution,
actual repair cost, fleet master, or finance posting.

## Architecture (as approved & built in Sprint 00)

| Layer | Tech | Notes |
|-------|------|-------|
| API base path | `/api/v1/damage-intelligence` | DI-0034 |
| Backend | **FastAPI (Python 3.11)** | Substitutes ASP.NET Core (DECISION-001a). Clean-Architecture package layout: `domain/`, `application/`, `infrastructure/`, `api/`, `tests/`. |
| AI service | **In-process FastAPI module** | Substitutes separate Python service (DECISION-001b). Will split when AI complexity warrants. |
| Database | **MongoDB** via `MONGO_URL` | Substitutes PostgreSQL (DECISION-004). Tenant-scoped collections (`di_*`). Idempotent index creation at startup acts as the migration baseline. |
| Object storage | **Local-disk abstraction** behind `StorageProvider` | DECISION-001e. HMAC-signed time-limited links only. No public unrestricted URLs. Production object store integration is a Sprint-05 hardening item. |
| Auth | **JWT bearer + RBAC + multi-tenant** | DECISION-003. Access 60min / refresh 7d. `Authorization: Bearer` (no cookies, matches DI-0034). `X-Tenant-Id` cross-checked against JWT claim. |
| Web | **React 18 (CRA + Tailwind)** | DECISION-001c substitutes Blazor. Lean dep set for Sprint 00; shadcn primitives added when Sprint 01–03 screens need them. |
| Mobile | **Deferred** | DECISION-001d. Bearer-token + X-Tenant-Id contract is already mobile-compatible. |

## User Personas

| Role | Sprint 00 access |
|------|-----------------|
| `DI_Admin` (21 perms) | All current routes + future configuration |
| `DI_Inspector` (9 perms) | Inspection capture + image upload + AI request/read |
| `DI_Reviewer` (12 perms) | Review queue + damage cases + reports |
| `DI_Operations` (9 perms) | Read-only operational monitoring |
| `DI_Auditor` (4 perms) | Audit + report read |
| `DI_IntegrationService` (4 perms) | Service-to-service callers (CROMS / Maintenance) |

## Core Static Requirements (unchanging)

1. AI outputs are advisory; final charge, rental closure, work order execution,
   and actual repair cost remain with CROMS / Maintenance / Finance.
2. Every protected request enforces tenant isolation (`X-Tenant-Id` ↔ JWT
   `tenantId` cross-check; `TENANT_SCOPE_VIOLATION` otherwise).
3. Every critical action writes an append-only audit record (DI-0015).
4. Evidence and report access is controlled — time-limited links only.
5. No raw images, secrets, tokens, stack traces, or unrestricted URLs in logs.
6. Standard envelope (`{success, correlationId, data, errors}`) on every API
   response. 14 stable error codes from DI-0034.
7. Idempotency on integration write APIs (`X-Idempotency-Key`).

## Implementation Status

### 2026-06-28 — Sprint 00 (TASK-01) — **DONE**

- TASK-00 (Repository Understanding and Scope Lock) — complete
- BLOCKER-001 (`DI-0034` missing) — resolved upstream, file synced
- Stack-substitution decisions (DECISION-001..004) — approved by product owner
- Backend FastAPI app online (`supervisor status backend = RUNNING`)
  - 9 endpoints implemented: health (×2), version, auth (×4), integration ping (×2)
  - 6 MongoDB collections + tenant-scoped indexes
  - JWT (60min access, 7d refresh) + bcrypt + brute-force guard
  - 6 roles × 23 permissions baseline
  - Correlation-id middleware, safe-errors middleware, JSON logging that scrubs secrets
  - CROMS + Maintenance integration **stubs** (Sprint-04 placeholder)
  - HMAC-signed local-storage provider behind `StorageProvider` interface
- Frontend React shell online (`supervisor status frontend = RUNNING`)
  - `/login` with prefilled dev creds + safe error rendering
  - `/` Dashboard with live health probes + DI-0031 scope card + sprint plan card
  - `/inspections /review /cases /reports /admin` placeholders (each cites repo doc + sprint)
  - Sidebar role-based menu visibility (permission-gated)
  - `data-testid` registry (`src/constants/testIds.js`)
- 11 of 11 Sprint 00 acceptance criteria PASS or formally DOCUMENTED
- Smoke test `backend/tests/smoke_sprint00.py` — 12 assertions, all green
- Delivery record: `docs/07-Damage-Intelligence/implementation/SPRINT-00-DELIVERY-NOTES.md`
- Credentials: `/app/memory/test_credentials.md` and `/app/auth_testing.md`

## Prioritized Backlog

### P0 — Next sprint

- **TASK-02 / Sprint 01 — Production Inspection and Evidence Foundation**
  - Inspection session domain model, status lifecycle + status history
  - External references (vehicle, rental, branch, maintenance placeholder)
  - Capture positions, secure upload request, image registration, evidence references
  - Evidence access link generation (controlled, time-limited)
  - Tenant isolation tests, audit records, safe errors
  - 9 APIs (POST `/inspection-sessions`, GET, list, submit, PATCH status, upload-request, register image, list images, evidence access-link)
  - 8 collections (`di_inspection_sessions`, `di_inspection_status_history`, `di_inspection_images`, `di_evidence_references`, `di_upload_requests`, `di_external_system_references`, `di_capture_positions`, `di_audit_records`)
  - Web: inspection foundation screens
  - QA: TC-DI-0101..0205, 1101..1104, 1201, 1202, 1401, 1701

### P1 — Subsequent sprints

- TASK-03 / Sprint 02 — Image quality + AI detection (advisory) + low-confidence routing
- TASK-04 / Sprint 03 — Damage comparison, review queue, damage cases
- TASK-05 / Sprint 04 — CROMS + GCU365Maintenance integration (idempotent, audited)
- TASK-06 / Sprint 05 — Reports, evidence packages, monitoring, security hardening, release gates
- TASK-07 — Full regression + production readiness validation
- TASK-08 — Final handover report

### P2 — Backlog / hardening

- Split AI module into a separate Python service when pipeline complexity warrants
- Replace local-disk storage with production object store (Sprint-05 hardening)
- Mobile (Flutter) inspection capture
- CI/CD pipeline wiring (build, test, lint, secret scan)
- Arabic / RTL polish (DI-0025)

## Open Decisions / Risks

| Item | Status |
|------|--------|
| Auth pre-fill on `/login` for dev convenience | Must be removed before any non-dev deployment |
| CI/CD pipeline (AC-DI-S00-008) | Documented but not wired in the Emergent preview |
| Production object storage provider | Deferred to Sprint 05 — abstraction in place |
