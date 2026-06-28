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

### 2026-06-28 — Sprint 03 (TASK-04) — **DONE**

- **Damage comparison with REAL Gemini multimodal vision** (`gemini-3.1-pro-preview`, multi-image baseline-vs-current per capture position via new `call_vision_model_multi`). Baseline anchor accepts explicit `baselineInspectionSessionId` OR auto-anchors to the most recent prior SUBMITTED inspection for the same `externalVehicleRef` (DECISION-Sprint03-a). Missing baseline / no-overlap → `NOT_COMPARABLE` (never auto-confirms new damage). Outcome codes: `NEW, PRE_EXISTING, CHANGED, REPAIRED, UNCERTAIN, NOT_COMPARABLE` (DECISION-Sprint03-c, full spec set; locked 4-class maps onto these).
- **Review queue** (`di_review_queue_items`, idempotent on object): LOW_CONFIDENCE/UNCERTAIN AI findings + review-required comparison results auto-route on Run AI / Run comparison (DECISION-Sprint03-b; per-tenant `autoRouteLowConfidence` switch, default true, on `di_ai_configuration` via PUT `/configuration/ai-thresholds`). Decision codes `CONFIRMED/REJECTED/EDITED/ESCALATED/ADDITIONAL_EVIDENCE_REQUIRED/DEFERRED/DUPLICATE` (reason enforced where required); EDITED applies + audits before/after diff. Additional-evidence requests stored + linked.
- **Damage cases** (`di_damage_cases` + status history + links collection): create from findings/comparison results, duplicate prevention (sha256 dedupeKey over inspection+linked ids while an active case exists → 409), controlled status lifecycle with transition map + reason enforcement, link-evidence/finding/comparison endpoints. Ownership boundary preserved (no charge/closure/repair-cost/work-order).
- **DI-0037 Per-Vehicle Evidence Strip** (DECISION-Sprint03-d): GET `/inspection-sessions/{id}/per-vehicle-strip` — prior same-vehicle evidence in tenant, no raw objectPath/URLs.
- 13 endpoints under 3 new routers (`comparison.py`, `review.py`, `damage_cases.py`); 10 new MongoDB collections w/ tenant-scoped indexes; new audit actions for all comparison/review/case events.
- Web: Review Queue list + Review Item detail (decision + additional-evidence + create-case), Damage Cases list + detail (status update + history), comparison panel + per-vehicle strip on InspectionDetail. 40+ new data-testids.
- Tests: `backend/tests/smoke_sprint03.py` (17 assertion blocks, all green incl. real Gemini). Regression: Sprint 00/01/02 smokes updated (stale 404 guards) and green. Testing agent iteration_6 — backend 100% (17/17), frontend 100% on all ACs, 0 issues.
- Delivery record: `docs/07-Damage-Intelligence/implementation/SPRINT-03-DELIVERY-NOTES.md`.

### 2026-06-28 — Sprint 02 (TASK-03) — **DONE**

- **AI advisory damage detection wired to real Gemini multimodal vision** via Emergent LLM key (`gemini-3.5-flash` for image-quality, `gemini-3.1-pro-preview` for damage detection — both swappable via env without code change).
- 9 endpoints: per-image and per-session quality check, per-session AI analysis, get analysis, list findings (analysis-scoped + session-scoped), retry, GET + PUT `/configuration/ai-thresholds`. All under `/api/v1/damage-intelligence`. All carry `isAdvisory: true`. Every persisted analysis/finding carries `modelVersion`, `confidenceThreshold`, `correlationId`, tenant scope.
- 4 new MongoDB collections (`di_image_quality_results`, `di_ai_analyses`, `di_ai_findings`, `di_ai_configuration`) — tenant-scoped indexes.
- Default confidence threshold `0.70`; per-tenant override via `di_ai_configuration` (DI_Admin only). Status mapping: <0.30 → `UNCERTAIN`, <threshold → `LOW_CONFIDENCE`, ≥threshold → `AUTO_ACCEPTABLE`.
- Failure handling: Gemini timeout / `ChatError` → 1 retry + backoff → safe envelope with `qualityStatus=ERROR` or empty findings + `uncertaintyReason="model_unparseable"`. Cross-tenant returns 404 with audit row. No raw image bytes / secrets / tokens / unrestricted URLs in any log or audit.
- Web: `InspectionDetail` extended with Quality-check + Run-AI buttons, AI advisory panel + per-finding cards.
- Smoke tests: 15-step Sprint 02 + 16-step Sprint 01 + 12-step Sprint 00 — **all 43 assertions green** against the live Gemini API.
- Feeder doc: `docs/07-Damage-Intelligence/DI-0037-Per-Vehicle-Evidence-Strip.md` drafted (will land in Sprint 03 alongside comparison).
- Delivery record: `docs/07-Damage-Intelligence/implementation/SPRINT-02-DELIVERY-NOTES.md`.

### 2026-06-28 — Sprint 01 (TASK-02) — DONE

- All 12 acceptance criteria (AC-DI-S01-001 to AC-DI-S01-012) PASS
- Two human-in-the-loop decisions captured: DECISION-Sprint01-a (seed `RIYADAH-DOH-001` alongside `TENANT-000001`), DECISION-Sprint01-b (opaque external string references, align in Sprint 04). Documented in `docs/07-Damage-Intelligence/implementation/SPRINT-01-DELIVERY-NOTES.md`.
- Backend: 8 inspection/image endpoints + evidence access-link + capture-positions reference + signed-URL PUT/GET storage targets. 6 status lifecycle states with explicit transition map. Action-scoped HMAC (PUT signatures cannot be reused as GET). 7 new MongoDB collections with tenant-scoped indexes. 14 audit-action codes with `correlationId` everywhere.
- Web: `/inspections` list (filters + pagination + create), `/inspections/:id` detail (references, lifecycle, images, upload/submit/cancel, evidence access link opens in a new tab). 40+ new `data-testid`s.
- Testing agent regression — 63/63 pytest green (22 Sprint-00 + 41 Sprint-01) + both smoke tests green. One bug found & fixed mid-iteration: `validation_exception_handler` was returning HTTP 422 instead of DI-0034's required HTTP 400 for `VALIDATION_ERROR` envelopes; single-line fix in `/app/backend/api/middleware/safe_errors.py`.
- Smoke tests preserved: `backend/tests/smoke_sprint00.py` (12 assertions) + `backend/tests/smoke_sprint01.py` (16 assertions).

### 2026-06-28 — Sprint 00 (TASK-01) — DONE

- (As previously recorded; see `docs/07-Damage-Intelligence/implementation/SPRINT-00-DELIVERY-NOTES.md`.)
- TASK-00 Repository Scope Lock complete. BLOCKER-001 (`DI-0034`) resolved upstream.
- FastAPI backend with health/version/auth/integration-stub endpoints, JWT + RBAC, tenant-scope cross-check, brute-force guard, safe-error envelope, correlation-id round-trip, HMAC-signed local storage abstraction. React shell with login + dashboard + sidebar.

## Prioritized Backlog

### P0 — Next sprint

- **TASK-05 / Sprint 04 — Production CROMS + GCU365Maintenance Integration.** Required reading: DI-0031, DI-0034, DI-0035, and `implementation/SPRINT-04-Production-CROMS-and-Maintenance-Integration.md`. Deliverables: idempotent (`X-Idempotency-Key`) audited inbound/outbound integration APIs, opaque-ref shape alignment (DECISION-Sprint01-b), replace CROMS/Maintenance ping stubs with real contract surfaces, maintenance handoff foundation.

### P1 — Subsequent sprints

- TASK-06 / Sprint 05 — Reports, evidence packages, monitoring, security hardening, release gates (production object store, login pre-fill removal, X-Forwarded-For trust).
- TASK-07 — Full regression + production readiness validation.
- TASK-08 — Final handover report.

### P2 — Backlog / hardening

- Replace local-disk storage with production object store (Sprint 05 hardening).
- Split AI module into a separate Python service when pipeline complexity warrants.
- Mobile (Flutter) inspection capture (DECISION-001d deferral).
- CI/CD pipeline (AC-DI-S00-008 documented but not wired in Emergent preview).
- Required-evidence-completeness rule before submit (e.g., all 6 required capture positions registered) — current Sprint-01 implementation allows submit on any non-zero image count.
- Pytest deprecation cleanup (`test_sprint01_backend.py::TestEvidenceAccessLink` class-scoped fixture).
- Arabic / RTL polish (DI-0025).

## Open Decisions / Risks

| Item | Status |
|------|--------|
| Auth pre-fill on `/login` for dev convenience | Must be removed before any non-dev deployment (Sprint 05) |
| CI/CD pipeline (AC-DI-S00-008) | Documented but not wired in the Emergent preview |
| Production object storage provider | Deferred to Sprint 05 — abstraction in place |
| Submit-readiness rule (required capture positions present) | Deferred — current sprint accepts ≥1 image |

## Locked-in Sprint 03 (TASK-04) decisions — for next session

These decisions were confirmed by the product owner on 2026-06-28 and MUST NOT be
re-asked when TASK-04 starts in a fresh session.

| ID | Decision |
|----|----------|
| DECISION-Sprint03-a | **Damage comparison anchor**: API accepts BOTH explicit `baselineInspectionSessionId` AND auto-anchors to the most recent prior submitted inspection for the same `externalVehicleRef` within the tenant when no baseline is provided. |
| DECISION-Sprint03-b | **Review-queue auto-routing**: Findings flagged `LOW_CONFIDENCE` or `UNCERTAIN` are auto-inserted into `di_review_queue` immediately on `Run AI`. Tenant-level switch `autoRouteLowConfidence: true` (default) in `di_ai_configuration` lets a DI_Admin opt-out per tenant. |
| DECISION-Sprint03-c | **Comparison classification**: each AI advisory finding in a comparison is classified as one of `NEW_DAMAGE`, `PRE_EXISTING_DAMAGE`, `RESOLVED`, or `NOT_COMPARABLE`. |
| DECISION-Sprint03-d | **DI-0037 (Per-Vehicle Evidence Strip)** is bundled INTO Sprint 03 (single sprint delivery alongside damage comparison). |

Required reading at TASK-04 start (do not skip): DI-0006, DI-0009, DI-0011, DI-0012,
DI-0014, DI-0015, DI-0019, DI-0034, DI-0035, DI-0037, and
`implementation/SPRINT-03-Production-Review-Comparison-and-Damage-Cases.md`.
