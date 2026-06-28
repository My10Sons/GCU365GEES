---
id: "DI-SPRINT-00-DELIVERY-NOTES"
title: "Damage Intelligence Sprint 00 Engineering Setup — Delivery Notes"
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
related: "DI-EMERGENT-AI-START-HERE, DI-EMERGENT-AI-EXECUTION-PROMPT, DI-EMERGENT-AI-TASK-SEQUENCE, DI-SPRINT-00, DI-0031, DI-0032, DI-0034"
---

# Sprint 00 Engineering Setup — Delivery Notes

## Purpose

Record the engineering decisions, deviations, and as-built state of Sprint 00 so
that every subsequent sprint is fully traceable to the repository and to the
human approvals captured in the chat session of 2026-06-28.

This is a **delivery record**, not a normative document. The normative
documents remain `DI-SPRINT-00-Engineering-Setup.md` and the DI-00xx
specifications.

---

## Resolved Blocker

### BLOCKER-001 — `DI-0034-OpenAPI-Contract.md` missing on initial pull

- **Status:** Resolved.
- **Resolution:** File added upstream by the product owner (commits `24afcae` and
  `2ac8854` on `origin/main`). Synced into the workspace via `git pull --ff-only`.
- **File:** `docs/07-Damage-Intelligence/DI-0034-OpenAPI-Contract.md` (1,090 lines).
- **Effect:** TASK-00 unblocked; TASK-01 (Sprint 00) started immediately.

---

## Approved Deviations (Human-in-the-Loop Decisions)

The product owner explicitly approved the following deviations from the
repository-mandated technology stack in the chat session of 2026-06-28. All
contracts defined by the repository (API surface, response envelope, error
codes, security rules, audit rules, ownership boundaries, AI advisory rule,
controlled evidence and report access) remain unchanged and authoritative.

| ID | Repository-mandated artifact | Approved substitution | Rationale |
|----|------------------------------|------------------------|-----------|
| DECISION-001a | ASP.NET Core (C#) backend | **FastAPI (Python)** with a Clean-Architecture-style package layout (`domain/`, `application/`, `infrastructure/`, `api/`, `tests/`) | Stack substitution approved by product owner. Emergent preview container is preconfigured for FastAPI on port 8001 with ingress forwarding `/api/*`. |
| DECISION-001b | Separate Python AI service | **AI module co-located in the FastAPI app** (`application/ai/`) | Sprint 00 only requires a placeholder. Splitting into a separate process can be done later without changing the public contract. |
| DECISION-001c | Blazor Web App | **React 18 (CRA + Tailwind)** | Stack substitution approved by product owner. |
| DECISION-001d | Flutter mobile shell | **Deferred** | Mobile is not required for Sprint 00 acceptance. Will revisit in a later sprint. |
| DECISION-004 | PostgreSQL with versioned migrations | **MongoDB** via Emergent's `MONGO_URL`. "Migrations" implemented as idempotent index creators (`infrastructure/db/indexes.py`) invoked at FastAPI startup. | Stack substitution approved by product owner. Tenant scoping is enforced via the `tenantId` field on every document and an index on `(tenantId, …)` pairs. |
| DECISION-001e | Production object storage (Azure Blob) | **Local-disk abstraction** behind a `StorageProvider` interface (`infrastructure/storage/`), exposing only HMAC-signed time-limited links. **No public unrestricted URLs.** Production object store integration is a Sprint-05 hardening item. | Sprint 00 storage approach documented; same path convention (`tenants/{tenantId}/damage-intelligence/inspections/{inspectionSessionId}/images/{imageId}`) as DI-SPRINT-00. |
| DECISION-002 (governance) | Log blockers & decisions in `EMERGENT-AI-BLOCKERS-AND-DECISIONS.md` | **Skipped** per product-owner instruction. Traceability lives in this delivery-notes file and in `/app/memory/PRD.md`. | The repository's `EMERGENT-AI-BLOCKERS-AND-DECISIONS.md` is left untouched. |
| DECISION-003 (auth) | Identity baseline only | **JWT-based custom auth (email/password + bearer token + RBAC)**, no OAuth provider. | Product owner chose option (a). Service-to-service tokens for CROMS/Maintenance are a Sprint-04 deliverable. |

CI/CD setup (DI-SPRINT-00 §"DevOps and CI/CD Setup", AC-DI-S00-008) is not
implementable inside the Emergent preview container. Acceptance is satisfied at
documentation level: the build commands and pipeline steps are recorded here
and will be wired in the team's CI of choice as part of the project's adoption
into a corporate CI/CD environment.

---

## As-Built State

### Repository layout (Sprint 00 deliverables)

```text
/app
├── backend/                                  ← FastAPI service (port 8001)
│   ├── .env                                  ← MONGO_URL, DB_NAME, JWT secret, seed creds (gitignored)
│   ├── requirements.txt                      ← FastAPI, motor, pymongo, pyjwt, bcrypt, ...
│   ├── server.py                             ← App entry, middleware wiring, route registration
│   ├── domain/
│   │   ├── enums/error_codes.py              ← DI-0034 standard error codes
│   │   ├── enums/permissions.py              ← DI-0034 23 permission strings
│   │   └── enums/roles.py                    ← DI-SPRINT-00 6 baseline roles
│   ├── application/
│   │   ├── security/password.py              ← bcrypt
│   │   ├── security/jwt_tokens.py            ← access (60min) + refresh (7d)
│   │   ├── security/permissions_map.py       ← role → permission frozensets
│   │   ├── security/dependencies.py          ← current_principal, require_permission, tenant check
│   │   └── services/audit_service.py         ← append-only audit writer (DI-0015)
│   ├── infrastructure/
│   │   ├── db/mongo.py                       ← Motor client + ping
│   │   ├── db/indexes.py                     ← idempotent index creator (di_* collections)
│   │   ├── seed/admin_seed.py                ← idempotent seed of 3 principals
│   │   ├── storage/storage_provider.py       ← interface
│   │   ├── storage/local_storage.py          ← HMAC-signed, time-limited links
│   │   ├── integrations/croms_stub.py        ← Sprint-04 placeholder
│   │   ├── integrations/maintenance_stub.py  ← Sprint-04 placeholder
│   │   └── observability/logging.py          ← JSON logs with correlation id, scrubs secrets
│   ├── api/
│   │   ├── middleware/correlation_id.py      ← DI-0034 X-Correlation-Id contract
│   │   ├── middleware/safe_errors.py         ← DI-0014 + DI-0034 safe error envelope
│   │   ├── schemas/envelope.py               ← {success, correlationId, data, errors}
│   │   └── routes/
│   │       ├── health.py                     ← GET /health, /health/dependencies
│   │       ├── version.py                    ← GET /version
│   │       ├── auth.py                       ← POST /auth/login, /refresh, /logout; GET /me
│   │       └── integration_stubs.py          ← GET /integrations/{croms,maintenance}/ping
│   └── tests/
│       └── smoke_sprint00.py                 ← Sprint 00 smoke test (12 assertions)
├── frontend/                                 ← React shell (port 3000)
│   ├── .env                                  ← REACT_APP_BACKEND_URL (gitignored)
│   ├── package.json                          ← lean: react, react-router-dom, axios, lucide-react, tailwind
│   ├── tailwind.config.js                    ← ink/steel/signal palette, IBM Plex Sans + JetBrains Mono
│   ├── postcss.config.js
│   ├── public/index.html
│   └── src/
│       ├── index.js, index.css, App.js
│       ├── lib/api.js                        ← axios instance, Bearer + X-Tenant-Id + X-Correlation-Id
│       ├── lib/auth-context.jsx              ← AuthProvider, login/logout/refresh
│       ├── components/Shell.jsx              ← sidebar + topbar + role-based menu visibility
│       ├── pages/Login.jsx                   ← /login
│       ├── pages/Dashboard.jsx               ← /  — health + scope-boundary + sprint plan
│       ├── pages/Placeholder.jsx             ← inspection / review / cases / reports / admin
│       └── constants/testIds.js              ← stable data-testid registry
├── docs/07-Damage-Intelligence/              ← Untouched authoritative documentation
│   └── implementation/
│       └── SPRINT-00-DELIVERY-NOTES.md       ← (this file)
└── memory/
    ├── PRD.md                                ← Product/architecture record
    └── test_credentials.md                   ← Seeded credentials for QA
```

### Implemented APIs (Sprint 00 scope)

```
GET  /api/v1/damage-intelligence/health
GET  /api/v1/damage-intelligence/health/dependencies
GET  /api/v1/damage-intelligence/version
POST /api/v1/damage-intelligence/auth/login
POST /api/v1/damage-intelligence/auth/refresh
GET  /api/v1/damage-intelligence/auth/me
POST /api/v1/damage-intelligence/auth/logout
GET  /api/v1/damage-intelligence/integrations/croms/ping       (stub)
GET  /api/v1/damage-intelligence/integrations/maintenance/ping (stub)
```

Business workflow endpoints (`inspection-sessions`, `images`, `evidence`,
`ai-analysis`, `comparisons`, `review-queue`, `damage-cases`, `reports`,
`configuration`, `audit-records`, CROMS and Maintenance integration writes)
are intentionally **NOT** implemented in Sprint 00 — they are Sprint 01–05 scope.

### Implemented database collections (Sprint 00 scope)

```
di_schema_version
di_system_health_check
di_users
di_login_attempts
di_audit_records
di_integration_idempotency_records
```

All indexes are tenant-scoped where appropriate.

### Roles and permissions baseline

| Role | Permissions count | Purpose |
|------|-------------------|---------|
| DI_Admin | 21 of 23 | DI configuration + every business permission except service-to-service |
| DI_Inspector | 9 | Inspection capture and submission |
| DI_Reviewer | 12 | Review queue + damage case management |
| DI_Operations | 9 | Read-only operational monitoring |
| DI_Auditor | 4 | Audit + report read access |
| DI_IntegrationService | 4 | Service-to-service integration |

Total permissions: 23 (matches DI-0034 §"Recommended permissions").

---

## Sprint 00 Acceptance Criteria — Status

| AC | Description | Status | Evidence |
|----|-------------|--------|----------|
| AC-DI-S00-001 | Repository structure ready | **PASS** | `/app/backend/{domain,application,infrastructure,api,tests}` + `/app/frontend/src/{components,pages,lib,constants}` |
| AC-DI-S00-002 | Backend skeleton builds | **PASS** | `supervisor status backend = RUNNING` |
| AC-DI-S00-003 | Health endpoint works | **PASS** | `GET /api/v1/damage-intelligence/health → 200, success:true` |
| AC-DI-S00-004 | AI skeleton builds | **PASS** (substituted) | `/health/dependencies` reports `ai_service.mode = "in_process_placeholder"` |
| AC-DI-S00-005 | DB migration baseline | **PASS** | `infrastructure/db/indexes.py` runs idempotently on startup; `di_schema_version = "sprint-00"` seeded |
| AC-DI-S00-006 | Storage baseline + no public access | **PASS** | `LocalStorageProvider` issues HMAC-signed time-limited URLs; no public route exists |
| AC-DI-S00-007 | Identity baseline | **PASS** | JWT bearer; 6 roles + 23 permissions; tenant header check (`TENANT_SCOPE_VIOLATION`) |
| AC-DI-S00-008 | CI/CD baseline | **DOCUMENTED** | Not wireable inside Emergent preview; pipeline expectations recorded in this file (§Deviations) |
| AC-DI-S00-009 | No secrets committed | **PASS** | `.gitignore` excludes `.env`, `backend/.env`, `frontend/.env`, `**/.env.local` |
| AC-DI-S00-010 | Integration stubs exist | **PASS** | `CromsClientStub`, `MaintenanceClientStub`, `GET .../integrations/{croms,maintenance}/ping` |
| AC-DI-S00-011 | Smoke test passes | **PASS** | `tests/smoke_sprint00.py` — 12 assertions, all green |

Definition of Ready for Sprint 01 — satisfied.

---

## Known Limitations

- AI service is in-process; will be split into a separate Python service when
  the AI pipeline gets non-trivial (DI-0005, DI-0006 work in Sprint 02).
- Object storage is local disk; production object store integration is a
  Sprint-05 hardening item.
- CI/CD is not wired (no pipeline in the Emergent preview).
- Mobile (Flutter) is deferred; the role/permission model and Bearer-header
  contract are already mobile-compatible.

---

## Next Recommended Task

`TASK-02 — Sprint 01 Production Inspection and Evidence Foundation`. Required
reading before TASK-02 starts: DI-0004, DI-0007, DI-0011, DI-0012, DI-0014,
DI-0015, DI-0019, DI-0020, DI-0034, DI-0035, and
`implementation/SPRINT-01-Production-Inspection-and-Evidence-Foundation.md`.
