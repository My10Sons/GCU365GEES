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

### 2026-06-29 — Trip Inspection (anonymous quick before/after analysis) — **DONE**

- New **Trip Inspection** page + nav item: upload a Before and After rental photo → real Gemini vision comparison → advisory verdict on **dents, scratches, and tyre issues**, each NEW vs PRE-EXISTING, with severity/confidence/location + plain-language summary.
- **Anonymous & ephemeral** (per user choice): no reference fields, NOTHING persisted — images written to a temp dir and deleted immediately after analysis; only a lightweight audit row (`QUICK_TRIP_ANALYSIS_RUN`) is written.
- Backend: `POST /trip-inspection/session|upload|analyze` (gated by `di.ai.request`); ephemeral temp storage; focused Gemini prompt; safe NOT_COMPARABLE handling (e.g. mismatched vehicles). Frontend downscales images client-side (≤1600px JPEG) to stay within proxy limits; analyze uses a 180s per-request timeout (Gemini Pro can take ~60-90s).
- Verified: curl run correctly detected dent+scratch+flat tyre on a damaged "after" photo; UI verified for both NEW_DAMAGE_FOUND and NOT_COMPARABLE states; compile clean; works in light/dark.

### 2026-06-28 — Light mode — **DONE**

- Converted the color palette (ink/steel/signal/amber/emerald + `white`) to CSS-variable tokens with Tailwind alpha support; `:root` = dark (default), `html.light` = light overrides. No component rewrites needed.
- Theme manager (`lib/theme.js`): persists to localStorage, applied pre-render (no flash). Sun/Moon toggle in the Shell header and on the Login page.
- Verified in both modes across Dashboard, Reports, and nav — readable surfaces/text/badges/accents; clean compile.

### 2026-06-28 — Demo seeder + GitHub reminder — **DONE**

- **One-click demo seeder**: admin-only `POST /demo/seed` runs a full advisory flow (inspection → evidence → AI → comparison → review item → damage case → evidence-package report) in ~2s; surfaced as a "Load demo data" button on the Dashboard with a success message. Verified via curl + live UI (metrics increment correctly).
- **Save-to-GitHub reminder**: inline Dashboard tip pointing operators to the chat "Save to GitHub" option.

### 2026-06-28 — Deployment readiness + Ops alert banner — **DONE**

- **deployment_agent: PASS** (no blockers) — env hygiene, CORS, ports, no hardcoded secrets/URLs, supervisor config valid, compilation clean.
- **Integration/security alert banner**: app-wide dismissible banner (`IntegrationAlertBanner`) polling `/monitoring/metrics` every 60s; lights amber on idempotency conflicts, tenant-scope violations, unauthorized attempts, or rejected handoffs, linking to the Dashboard. Verified rendering live.

### 2026-06-28 — TASK-07 Full Regression + TASK-08 Handover — **DONE**

- **Closing-the-loop feature**: CROMS damage-summary now auto-populates `reportReference` (latest RENTAL_DAMAGE_SUMMARY_REPORT) + `evidencePackageReference` (latest EVIDENCE_PACKAGE_REPORT); Maintenance handoff auto-links evidence-package + damage-case report references (caller-supplied preserved; idempotent). Verified in `smoke_sprint05.py`.
- **TASK-07 full regression**: all 6 sprint smokes green; testing agent iteration_9 — backend 100% (6/6 smokes + closing-the-loop), frontend 100% across the app, 0 issues. Cross-tenant isolation, signed-link-only access, advisory labelling, and ownership boundaries all verified.
- **TASK-08 handover**: `docs/07-Damage-Intelligence/DI-0040-Final-Handover-Report.md` consolidates Sprints 00–05 (architecture, data model, capabilities, security, test evidence, deferrals, run instructions).
- Remaining: ops/governance deferrals only (prod object store swap, external alerting, runbooks, DR, release sign-offs).

### 2026-06-28 — Sprint 05 (TASK-06) — **DONE** (core scope)

- **Reports + evidence packages**: POST `/reports` (7 types: inspection-summary, damage-detection, damage-comparison, damage-case, rental-damage-summary, maintenance-handoff, evidence-package), GET `/reports`, GET `/reports/{id}`, POST `/reports/{id}/access-link`. Content built from existing data, stored as JSON on disk, served via **HMAC-signed time-limited** links (`/internal/storage/access`) — no public URLs. AI labelled advisory; ownership boundaries in content (`finalCustomerChargeDecision: NOT_OWNED_BY_DAMAGE_INTELLIGENCE`, Maintenance owns work-order/cost).
- **Monitoring**: GET `/monitoring/metrics` (tenant-scoped workflow/ai/review/cases/reports/integration/security counts) + `/monitoring/dependencies`.
- **Dashboard**: metric tiles + **Integration Health widget** (CROMS check-outs/check-ins, handoffs sent/rejected, callbacks received, idempotency conflicts, tenant-scope violations, unauthorized attempts) with warn highlighting.
- **Security hardening**: removed login pre-fill (empty fields); reports/evidence access controlled, tenant-scoped, authorized (di.reports.*), audited; signature tamper → 403; cross-tenant → 404.
- New `di_reports` collection + audit-action index. Web Reports page (generate/list/access-link).
- Tests: `backend/tests/smoke_sprint05.py` (13 steps green incl. signed-link serve, tamper-reject, authz, tenant isolation, ownership). Regression Sprint 00–04 green. Testing agent iteration_8 — backend 100%, frontend 100%, 0 issues.
- Delivery record: `docs/07-Damage-Intelligence/implementation/SPRINT-05-DELIVERY-NOTES.md`.
- **Deferred (governance/ops, not code)**: production object store swap, external alerting/dashboards (Grafana/Prometheus), runbooks, DR, rollback approvals, formal release-gate sign-offs.

### 2026-06-28 — Sprint 04 (TASK-05) — **DONE**

- **CROMS integration** (service-to-service, JWT + DI_IntegrationService role): check-out / check-in inspection request APIs (store CROMS refs only, baseline link on check-in), rental damage-summary API (returns `finalCustomerChargeDecision: NOT_OWNED_BY_DAMAGE_INTELLIGENCE`), inspection-status API, damage-summary-ready notification (outbound stub).
- **GCU365Maintenance integration**: handoff API (eligibility check, ownership preserved), work-order-reference / repair-status (actual cost stored as **reference only**, owned by Maintenance) / rejection / additional-evidence callbacks, handoff-status aggregation API.
- **Idempotency** (`X-Idempotency-Key`, `di_integration_idempotency_records`): same tenant+key+payload replays stored response; different payload → `IDEMPOTENCY_CONFLICT` (409). Audited.
- **Security & isolation**: integration perms gate every endpoint (non-integration principals 401/403); strict tenant scoping (cross-tenant → 404); no raw objectPath/URLs or secrets in payloads/logs; full integration audit action set.
- New collections: `di_maintenance_handoffs`, `di_maintenance_references`, `di_maintenance_status_updates` (tenant-scoped indexes). Seeded `DI_IntegrationService` accounts per tenant.
- Web: damage-case detail now surfaces read-only **Maintenance integration** context (handoffs, work orders, repair status) via `maintenanceContext` on the case GET.
- Tests: `backend/tests/smoke_sprint04.py` (16 steps green incl. idempotency replay/conflict, ownership boundaries, tenant isolation, security). Regression Sprint 00–03 green. Testing agent iteration_7 — backend 100%, frontend 100%, 0 issues.
- Delivery record: `docs/07-Damage-Intelligence/implementation/SPRINT-04-DELIVERY-NOTES.md`.
- **MOCKED**: outbound CROMS/Maintenance client calls are stubs (`CromsClientStub`/`MaintenanceClientStub`) — inbound APIs + persistence are fully real.

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

### P0 — Next

- **TASK-07 — Full Regression & Production Readiness Validation.** Run all sprint smokes + testing agent across Sprint 01–05 scope; validate tenant isolation, evidence/report access control, audit completeness, safe errors, performance. Confirm production-readiness checklist (DI-SPRINT-05 release gate table).
- **TASK-08 — Final Handover Report.** Consolidate delivery notes (Sprints 00–05), API surface, data model, ownership boundaries, test evidence, and known deferrals into a single handover document.

### Deferred (ops/governance, tracked from Sprint 05)

- Production object store (swap local-disk provider), external monitoring/alerting integration, operational runbooks, DR drills, rollback/release approval sign-offs.
- Optionally populate `reportReference` / `evidencePackageReference` in CROMS damage-summary + Maintenance handoff responses (currently null) by linking generated reports.

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

## Changelog — 2026-06-29

- **Trip Inspection bug fix (verified, iteration_10.json):** Expanded the anonymous Trip
  Inspection damage categories from `DENT/SCRATCH/TIRE` to
  `DENT/SCRATCH/TIRE/GLASS/LIGHT/PART`. Previously broken glass and broken lamps were
  explicitly ignored ("outside requested reporting categories"). Now broken/cracked glass
  (windscreen, rear/side windows), broken/cracked/missing lights (head/tail/brake/indicator),
  and broken/missing parts (bumper, mirror, trim, grille, badge) are detected and surfaced
  as NEW damage with bounding-box markers.
  - Backend: `application/services/trip_inspection_service.py` (SYSTEM_MESSAGE, USER_PROMPT,
    `_CATEGORIES`, `_CATEGORY_SYNONYMS`, dynamic counts).
  - Frontend: `pages/TripInspection.jsx` (`CATEGORY_LABEL`, `CATEGORY_ORDER`, 6 count cards).
  - Verified via testing_agent on PREVIEW with real Gemini — 100% pass. NOT yet redeployed to production.
- **Trip Inspection bounding-box markers:** verified working (iteration prior).

## Changelog — 2026-06-29 (Trip Inspection v2 — verified, iteration_11.json)

- **Expanded exterior categories** to 12: Dents, Scratches, Chips, Tyres, Wheels/rims,
  Glass, Lights, Broken/missing parts, Rust/corrosion, Vandalism/graffiti, Dirt/staining,
  Fluid leaks.
- **Added optional INTERIOR inspection** (6 categories): Seats, Dashboard/console,
  Trim/panels, Stains/dirt, Missing items, Screens/controls. Analyzed only when BOTH
  interior before + after photos are provided; rendered as its own result section with its
  own annotated after image + bounding-box markers.
- **Single-request architecture:** removed the old `/trip-inspection/session` + `/upload`
  endpoints. All images are now sent in ONE multipart `POST /trip-inspection/analyze`
  (fields: exterior_before, exterior_after [required], interior_before, interior_after
  [optional]). Backend writes to a per-request temp dir and deletes it immediately. This
  fixes the production "Both a Before and an After image are required" error caused by
  upload/analyze landing on different backend instances behind the load balancer.
- Result shape changed to `{ sections:[{kind, label, comparable, overall, summary, items,
  counts, newIssueCount}], overall, newIssueCount, modelVersion }`.
- Files: `backend/application/services/trip_inspection_service.py`,
  `backend/api/routes/trip_inspection.py`, `frontend/src/pages/TripInspection.jsx`,
  `frontend/src/constants/testIds.js`.
- Verified via testing_agent on PREVIEW (5/5 flows pass). NOT yet redeployed to production.

## Changelog — 2026-06-29 (Trip Inspection v3 — verified, iteration_12.json)

- **Selectable inspection scope:** user picks which areas to inspect via 'Exterior' /
  'Interior' toggle chips (default Exterior on). Each selected area requires both before+after
  photos; partial areas show an inline amber hint and Analyze stays disabled (no click-time
  error). At least one selected area must be complete. Backend `analyze_trip` now requires at
  least one complete pair and analyzes any combination; route fields all optional.
- **One-click annotated PDF export:** 'Export PDF' on the result builds a client-side report
  (jsPDF) — overall verdict + each section's canvas-composed annotated after-image (numbered
  boxes) + findings list. No server storage, fully ephemeral. Uses a custom `composeAnnotated`
  canvas helper (no html2canvas) for robustness. Added dep: jspdf.
- Files: `frontend/src/pages/TripInspection.jsx`, `frontend/src/constants/testIds.js`,
  `backend/application/services/trip_inspection_service.py`, `backend/api/routes/trip_inspection.py`.
- Verified via testing_agent on PREVIEW: 6/6 flows pass (exterior-only, interior-only, both,
  inline-hint gating, no-selection guard, 2 real PDF downloads). NOT yet redeployed to production.

## Changelog — 2026-06-29 (Trip Inspection v3.1)

- **Parallel area analysis:** `analyze_trip` now runs the exterior and interior Gemini calls
  concurrently via `asyncio.gather` (was sequential). Both-area analysis ~15s instead of ~2x.
- **PDF before + after:** the exported PDF now shows each section's Before photo and the
  annotated After (issues marked) side by side, above the findings list.
- Files: `backend/application/services/trip_inspection_service.py`, `frontend/src/pages/TripInspection.jsx`.
- Verified on PREVIEW: direct API timing + both sections correct; PDF export download succeeds
  cleanly (~437 KB, 4 embedded images). NOT yet redeployed to production.

## Changelog — 2026-06-29 (Trip Inspection v4 — branded signable PDF)

- **Per-tenant branding:** new `di_tenant_branding` collection {tenantId, companyName,
  branchName, logoDataUrl}. New routes `GET /tenant/branding` (di.ai.request) and
  `PUT /tenant/branding` (di.configuration.manage — the path CROMS/Maintenance uses to
  provision branding when creating a tenant). Demo branding (Riyadah Technology + logo)
  seeded idempotently for both tenants at startup (`tenant_branding_seed.py`,
  asset `infrastructure/seed/assets/demo_logo_b64.txt`). Branding is returned inside the
  trip analyze result (`result.branding`), filtered by tenantId.
- **Branded, signable PDF export:** PDF now has a header (tenant logo + company + branch),
  an optional reference block (Customer, Vehicle plate, Make/model, Rental ID, Inspector —
  entered in a new 'Report details' panel on the page), Before + After (issues marked)
  images per section, findings, and optional Customer/Staff signature blocks with date lines.
- **Parallel analysis** (v3.1) retained.
- Files: backend `application/services/tenant_branding_service.py`, `api/routes/tenant.py`,
  `infrastructure/seed/tenant_branding_seed.py`, `server.py`, `trip_inspection_service.py`;
  frontend `pages/TripInspection.jsx`. Dep: jspdf.
- Verified on PREVIEW: rendered the actual PDF (logo + company + refs + before/after + findings
  + signatures all present); backend checks — inspector PUT 403, admin PUT ok, DOH tenant
  isolation, invalid logo 400. NOT yet redeployed to production.

## Changelog — 2026-06-29 (Trip Inspection v5 — cost, photo-guard, condition)

- **A · Severity + repair-cost estimate:** each finding gets a deterministic, advisory repair
  cost range (rule-based table per category × severity factor, currency `DI_TRIP_CURRENCY`,
  default SAR). Result includes `costSummary` (sum of NEW findings). Shown per-finding and as
  a summary in UI + PDF.
- **D · Photo-quality + same-vehicle guard:** each section returns `photoCheck`
  {beforeUsable, afterUsable, issues[], sameVehicle, vehicleMismatchReason}; result has
  `hasPhotoWarnings`. UI shows an amber "Photo check" panel; PDF lists the warnings. Verified
  a different-vehicle pair → sameVehicle=false + warning.
- **E · Condition score + cleanliness:** each section returns `conditionScore` (0-100) and
  `cleanliness` (CLEAN/LIGHT_DIRT/DIRTY/VERY_DIRTY); result aggregates worst score/cleanliness.
  Shown as chips in UI and a summary line in the PDF.
- Files: `backend/application/services/trip_inspection_service.py`,
  `frontend/src/pages/TripInspection.jsx`.
- Verified on PREVIEW (curl payloads + rendered PDF + UI). NOT yet redeployed to production.

## Changelog — 2026-06-29 (Trip Inspection v6 — walkaround, size/replace, integrity, bilingual PDF)

- **F · Guided multi-angle walkaround:** exterior is now angle-based — user selects any of
  Front/Rear/Left/Right/Roof chips; each selected angle gets its own Before/After pair, analyzed
  in parallel as its own section ("Exterior — Front" etc.), plus optional Interior. Result has a
  `coverage` summary (captured/missing angles, interior flag) shown as a chip. Backend route
  fields: ext_{angle}_before/after + interior_*; at least one complete pair required.
- **C · Size + repair/replace:** each finding has `sizeCm` (AI estimate via reference scale) and
  `recommendation` (REPAIR/REPLACE/ASSESS). Shown in UI findings + PDF.
- **E · Integrity / tamper check (advisory):** per-section `integrity` {beforeSuspicious,
  afterSuspicious, aiGeneratedLikelihood, signals}; result `hasIntegrityWarnings`. Amber
  "Integrity check" panel in UI + PDF. NOTE: advisory/heuristic, can false-positive (EXIF is
  stripped by client downscale; detection is content-based).
- **G · Bilingual PDF:** Export in English / Arabic / EN+AR via a language dropdown. PDF rebuilt
  as an HTML report rendered with html2canvas -> jsPDF (multipage), so Arabic shapes/RTL render
  natively. Amiri webfont added to index.html. Branding header, reference fields, per-section
  before+after annotated images, findings table (size/action/cost), warnings, coverage, and
  signature blocks — all localised.
- Files: backend `trip_inspection_service.py`, `api/routes/trip_inspection.py`; frontend
  `pages/TripInspection.jsx`, `constants/testIds.js`, `public/index.html`. Dep: html2canvas (already present).
- Verified via testing_agent (iteration_13.json): 100% (10/10), 5 real PDF downloads, 0 console errors.
  NOT yet redeployed to production.

## Changelog — 2026-06-29 (Trip Inspection v7 — walkaround completeness gate)

- **Completeness gate:** new "Require a full 5-angle walkaround (enforce before analysis)"
  toggle — when on, auto-selects all 5 exterior angles and disables Analyze until every angle
  has both photos (gate hint lists missing angles). When off, a non-blocking amber advisory
  shows for a partial walkaround ("Partial walkaround X/5 … Missing: …").
- **Badge:** result `coverage.fullWalkaround` flag drives a green "✓ Full 5-angle walkaround"
  badge (or amber "Partial walkaround X/5") in the overall card and on the PDF (all languages).
- Files: backend `trip_inspection_service.py` (coverage.fullWalkaround), frontend
  `pages/TripInspection.jsx`.
- Self-verified: gate auto-selects all angles + blocks Analyze when incomplete (screenshot);
  backend coverage flag confirmed. NOT yet redeployed to production.

## Changelog — 2026-06-29 (Trip Inspection v8 — branch walkaround policy)

- **Per-tenant policy:** new `di_tenant_policy` {tenantId, requireFullWalkaround}. Routes
  `GET /tenant/policy` (di.ai.request) and `PUT /tenant/policy` (di.configuration.manage).
- **Admin control:** admins (di.configuration.manage) see a "Branch policy" panel on the Trip
  page to toggle "Require a full 5-angle walkaround for every inspection" and Save.
- **Enforcement:** on page load the policy is fetched; when enforced, the walkaround gate is
  pre-enabled and LOCKED for all staff (green "Branch policy" badge), all 5 angles auto-selected.
- Files: backend `application/services/tenant_policy_service.py`, `api/routes/tenant.py`;
  frontend `pages/TripInspection.jsx`.
- Verified on PREVIEW: GET default false, inspector PUT 403, admin PUT persists; UI shows admin
  panel + locked gate + all 5 angles (screenshot). Demo tenant reset to false. Not redeployed.

## Changelog — 2026-06-29 (Tenant Settings admin screen)

- **New admin-only "Tenant Settings" page** (`/settings`, nav item gated by di.configuration.manage,
  `pages/TenantSettings.jsx`) consolidating per-tenant config in one place:
  - **Report branding:** logo upload (downscaled to PNG data URL), company name, branch name
    → PUT /tenant/branding.
  - **Trip Inspection policy:** require-full-walkaround toggle → PUT /tenant/policy.
- Removed the inline admin policy panel from the Trip page (it now only reads + enforces the
  policy). Admin (ShieldAlert) and Tenant Settings (Settings2) are separate nav items.
- No backend changes (reuses existing /tenant/branding + /tenant/policy endpoints).
- Verified on PREVIEW: settings load (logo/company/branch), branding + policy save with
  confirmation, sidebar link present (screenshot). Demo tenant policy left OFF (default).

## Changelog — 2026-06-29 (Trip auto-route to Damage Case + PDF preview)

- **Auto-route NEW high-value Trip damage → persisted Damage Case (P0, verified iteration_14.json).**
  When an anonymous Trip Inspection finds NEW damage whose summed estimated repair (high end)
  reaches `DI_TRIP_AUTO_CASE_COST_THRESHOLD` (default 1000 SAR), the backend now persists a minimal
  inspection session (SPOT_CHECK / DI-Web) + `di_ai_analyses` + one `di_ai_finding` per NEW item,
  then opens a `REPAIR_RELEVANT` Damage Case (severity = highest NEW finding) linked to those
  findings — bridging the ephemeral trip tool into the main review/case queue.
  - Decisions: 1A=B (build session+findings then normal case), 1B=C (cost-threshold trigger),
    1C=A (report-detail fields → case: vehiclePlate→externalVehicleRef, rentalId→session ref,
    customer/model/inspector into case description; synthetic `TRIP-XXXX` ref when no plate),
    1D=A (UI banner with "View case" link to `/cases/:id`).
  - Auto-routing is best-effort (try/except) and never breaks the advisory analyze response.
  - Files: backend `application/services/trip_inspection_service.py` (`_maybe_auto_create_case`,
    `_AUTO_CASE_COST_THRESHOLD`, category→DamageType map), `api/routes/trip_inspection.py`
    (optional Form fields customer_name/vehicle_plate/vehicle_model/rental_id/inspector_name);
    frontend `pages/TripInspection.jsx` (append report fields to analyze; `trip-autocase-banner`).
  - Verified via testing_agent (iteration_14.json): 5/5 backend scenarios PASS with real Gemini —
    threshold gating, persistence, report-field mapping, synthetic ref fallback, additive shape.
- **PDF preview thumbnail on Tenant Settings (P0).** Live white-background mock of the branded
  PDF header (logo + company + branch + sample report title/refs/verdict) that updates as the
  admin edits branding. Frontend-only (`pages/TenantSettings.jsx`, `tenant-pdf-preview`).
  Verified via screenshot on PREVIEW. NOT yet redeployed to production.

## Changelog — 2026-06-29 (Perf: non-blocking bcrypt + stress findings)

- **Non-blocking bcrypt (auth perf fix).** `application/security/password.py` now exposes
  `hash_password_async` / `verify_password_async` (bcrypt offloaded via `asyncio.to_thread`); the
  login route awaits the async verify. Hash scheme/format unchanged — seeded `$2b$` hashes still
  verify. Verified by testing_agent (iteration_15.json): 10/10 auth regression PASS (all accounts,
  401/403 paths, /me, /refresh, brute-force lockout). NOT yet redeployed to production.
- **Stress test (PREVIEW, single uvicorn worker).** Harness at `backend/tests/stress/`.
  - Auth login (200 req @ 25 concurrent): before fix p50 5.68s / wall 45.9s → after fix
    **p50 2.9s / wall 24.5s** (~2× better; bcrypt threads run in parallel, GIL released).
  - Read mix (500 req @ 40 concurrent): p50 ~0.35s but p95/p99 20–30s with ~5–10% ConnectTimeouts;
    UNCHANGED by the bcrypt fix → confirmed it is **single-worker connection-acceptance
    saturation**, not query speed.
  - AI analyze (Gemini): stable, 0 failures, ~12–13s p50, scales fine 5→10 concurrent (I/O-bound).
- **DI-0042 Production Concurrency & Scaling Guidance** added (`docs/07-Damage-Intelligence/`):
  run multiple workers in production (`gunicorn -k uvicorn.workers.UvicornWorker --workers 2*CPU+1`,
  drop `--reload`), confirm production worker count with Emergent Support; the read-tail/timeout
  issue is expected to clear with multiple workers. App is stateless → scales horizontally.

## Changelog — 2026-06-30 (#8 AI speed: Fast/Thorough tiering + per-section streaming)

- **#8a Model tiering (Fast/Thorough).** Trip analyze takes `mode` (fast|thorough). Fast =
  `gemini-3.5-flash` (env `DI_AI_MODEL_DAMAGE_FAST_NAME`), Thorough = `gemini-3.1-pro-preview`.
  UI: "⚡ Fast / 🔬 Thorough" toggle on `/trip` (default Fast). `_model_for_mode()` in
  `trip_inspection_service.py`; route `mode` Form field.
- **#8b Per-section streaming (Option A).** Frontend analyzes each walkaround area in a separate
  parallel request to new `POST /trip-inspection/analyze-section` (one pair → one section),
  rendering each card as it returns (streaming banner + pending placeholders), then calls new
  `POST /trip-inspection/finalize` (JSON sections+reportFields+mode) which aggregates via extracted
  `_aggregate_result(...)`, attaches branding, runs auto-case routing ONCE. Legacy `/analyze`
  retained. Each request stateless → load-balancer safe.
  - Files: `api/routes/trip_inspection.py` (+analyze-section, +finalize, FinalizeIn),
    `trip_inspection_service.py` (`_aggregate_result`, `analyze_section`, `finalize_trip`),
    `frontend/src/pages/TripInspection.jsx` (streaming `analyze()`, `streaming`/`pending` state).
  - Verified by testing_agent (iteration_16.json): backend 5/5, frontend 12/12 E2E. SAR only,
    no QAR. NOT yet redeployed to production.
- DEFERRED: #8a phase-2 auto-escalation (re-run uncertain Fast sections on Pro); #12 kiosk/gate
  mode (on hold per user).

## Changelog — 2026-06-30 (#8a phase-2: auto-escalation Fast→Pro)

- **Auto-escalation.** In Fast mode, any area whose Flash result looks uncertain/high-risk is
  silently re-analyzed on the Pro model. Trigger (`_should_escalate`): a finding with
  status=UNCERTAIN, OR status=NEW & severity=HIGH, OR status=NEW & confidence < threshold.
  Config: `DI_TRIP_AUTO_ESCALATE` (default true), `DI_TRIP_ESCALATE_CONFIDENCE` (default 0.6).
  New `_analyze_pair_escalating(...)` used by BOTH the streaming (`analyze_section`) and legacy
  (`analyze_trip`) paths; escalated sections carry `escalated:true` and the Pro `modelVersion`.
  UI: a "Pro-verified" badge on escalated section cards (`trip-section-escalated`).
  - Verified via curl (both branches, real Gemini): MEDIUM/0.9 → no escalation (stays Flash, no
    added latency); with threshold raised, NEW/0.9 → escalated=true, model switches to
    gemini-3.1-pro-preview (latency Flash+Pro). Predicate unit-checked. Frontend compiles.
    NOT yet redeployed to production.

## Changelog — 2026-06-30 (User Help & Guide)

- **In-context help drawer + central Help page (frontend-only, bilingual EN/AR).** Per user
  choice: a "?" floating button on every screen (rendered once in `Shell.jsx`) opens a slide-in
  drawer with page-specific tips (auto-detected from the route via `topicForPath`), plus a central
  "Help & Guide" page at `/help` (sidebar nav link) covering the whole app as collapsible sections.
  - Content: `frontend/src/constants/helpContent.js` — task-focused, bilingual (EN + Arabic),
    8 topics (dashboard, trip, inspections, review, cases, reports, settings, admin). Each topic
    has intro + numbered steps + tips. Shared by both the drawer and the page.
  - Components: `components/HelpDrawer.jsx` (FAB + RTL-aware drawer, EN/AR toggle, "Open full
    guide" link), `pages/Help.jsx` (accordion + EN/AR toggle + advisory-boundary note).
  - Wiring: route in `App.js`, nav item + `<HelpDrawer/>` in `Shell.jsx`, testIds added.
  - Verified via screenshots: drawer opens on /trip, renders steps+tips, toggles to full RTL
    Arabic; sidebar "Help & Guide" link present. NOT yet redeployed to production.

## Changelog — 2026-07-02 (Per-inspection AI token telemetry)

- **Real token usage per inspection.** `gemini_client.call_vision_model_multi` now uses
  `LlmChat.send_message_with_tools` and returns the provider `Usage` (input/output/total tokens)
  as a 5th tuple element. `_analyze_pair` attaches `section.tokenUsage {inputTokens,outputTokens,
  totalTokens,calls}`; escalation sums both calls (calls=2); `_aggregate_result` rolls up a
  trip-level `result.tokenUsage`. Shown as a chip on the Trip Inspection result
  (`trip-token-usage`, e.g. "~4,426 AI tokens · 1 call") and written to the audit log
  (`totalTokens`, `aiCalls`).
  - Callers updated for the new 5-tuple: `comparison_service` (usage ignored), `trip_inspection_service`.
  - Verified via curl (analyze-section returned real usage {in 3268/out 801} and finalize
    aggregated it) + UI screenshot (chip renders with live count). Single Fast front-angle ≈ 4k
    tokens (mostly image input). NOT yet redeployed to production.
  - NOTE: exact SAR/credit cost per token is not published by Emergent — use Profile → Universal
    Key for balance; these counts give in-app per-inspection telemetry.

## Changelog — 2026-07-02 (AI Usage mini-dashboard)

- **Admin "AI Usage" dashboard.** New `GET /trip-inspection/usage?days=N` (gated `di.reports.read`)
  aggregates the audit log (`di_audit_records`, action QUICK_TRIP_ANALYSIS_RUN) by day →
  totals {tokens, calls, inspections, avgTokensPerInspection (over inspections with token data)}
  + daily rows. New page `pages/AiUsage.jsx` at `/ai-usage` (sidebar link, di.reports.read):
  stat cards + a dependency-free CSS bar chart of daily tokens + 7/30/90-day range toggle.
  Service `usage_summary()` in `trip_inspection_service.py`.
  - Verified via curl + screenshot: cards show 8,495 tokens / 2 calls / 97 inspections /
    avg 4,248; daily chart + nav link render. Older pre-telemetry runs show 0 tokens (expected).
    NOT yet redeployed to production.

## Changelog — 2026-07-02 (AI budget + projection alert)

- **Monthly AI token budget + in-app projection alert.** Per-tenant budget stored in new
  `di_tenant_ai_budget` {monthlyTokenBudget, costPer1kTokens, currency}. `_budget_status()`
  computes month-to-date tokens (from audit log), linear month-end projection, %used/%projected,
  over/near flags, and optional SAR estimates (via admin-entered cost/1K). Endpoints:
  `GET /trip-inspection/usage` now includes a `budget` block; `PUT /trip-inspection/budget`
  (gated `di.configuration.manage`). Frontend `AiUsage.jsx` `BudgetPanel`: color-coded banner
  (ok/near/over), progress bar, and an admin-only editor (budget + cost/1K). In-app only (no email).
  - Verified via curl (set 500k budget → projected 131,672 = 26%, est 10 SAR budget cost) +
    screenshot (banner + progress bar + admin editor render). NOT yet redeployed to production.

## Changelog — 2026-07-02 (Sidebar budget alert badge)

- **Sidebar "AI Usage" alert dot.** New lightweight `GET /trip-inspection/budget` (di.reports.read,
  no daily aggregation) returns `_budget_status`. `Shell.jsx` fetches it on mount + on route change
  (for users with di.reports.read) and renders a dot on the AI Usage nav item: **red** when
  projected-over-budget, **amber** when approaching. Verified via screenshot (forced low budget →
  red dot visible next to "AI Usage"); reset demo budget to non-alerting 500k. NOT yet redeployed.
