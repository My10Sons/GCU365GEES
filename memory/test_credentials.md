# Test Credentials — Damage Intelligence

Seeded at backend startup by `infrastructure/seed/admin_seed.py` (idempotent).
Passwords come from `/app/backend/.env`.

## Tenants

| Tenant Id | Notes | Sprint introduced |
|-----------|-------|-------------------|
| `TENANT-000001`     | Generic primary tenant — preserved for Sprint-00 regression | Sprint 00 |
| `RIYADAH-DOH-001`   | Riyadah Technology, Doha primary branch — used for multi-tenant isolation tests | Sprint 01 (DECISION-Sprint01-a) |

## Accounts

### Tenant `TENANT-000001`

| Role | Email | Password | Permissions |
|------|-------|----------|-------------|
| **DI_Admin** | `admin@riyadah.tech` | `DamageAdmin#2026` | 21 (every business + di.configuration.manage + di.audit.read) |
| **DI_Inspector** | `inspector@riyadah.tech` | `Inspector#2026` | 9 |
| **DI_Reviewer** | `reviewer@riyadah.tech` | `Reviewer#2026` | 12 |
| **DI_IntegrationService** | `integration.service@riyadah.tech` | `Integration#2026` | di.integrations.croms, di.integrations.maintenance, di.inspections.create, di.inspections.read |

### Tenant `RIYADAH-DOH-001`

| Role | Email | Password | Permissions |
|------|-------|----------|-------------|
| **DI_Admin** | `doha.admin@riyadah.tech` | `DohaAdmin#2026` | 21 |
| **DI_Inspector** | `doha.inspector@riyadah.tech` | `DohaInspector#2026` | 9 |
| **DI_IntegrationService** | `doha.integration.service@riyadah.tech` | `DohaIntegration#2026` | integrations (cross-tenant isolation tests) |

## API base

```
Base URL : ${REACT_APP_BACKEND_URL}/api/v1/damage-intelligence

# Auth (Sprint 00)
POST /auth/login   body: { email, password }
POST /auth/refresh body: { refreshToken }
GET  /auth/me      headers: Authorization: Bearer <token>, X-Tenant-Id: <tenantId>
POST /auth/logout  headers: Authorization: Bearer <token>

# Reference (Sprint 01)
GET  /reference/capture-positions

# Inspection sessions (Sprint 01) — require Authorization + X-Tenant-Id
POST   /inspection-sessions
GET    /inspection-sessions/{id}
GET    /inspection-sessions
POST   /inspection-sessions/{id}/submit
PATCH  /inspection-sessions/{id}/status
POST   /inspection-sessions/{id}/images/upload-request
POST   /inspection-sessions/{id}/images
GET    /inspection-sessions/{id}/images

# Evidence (Sprint 01)
POST   /evidence/{evidenceId}/access-link

# Signed-URL targets (NOT directly called by your client — they're targets of
# the URLs returned by upload-request / access-link). Public-but-signature-bound.
PUT  /internal/storage/upload?path=&exp=&sig=
GET  /internal/storage/access?path=&exp=&sig=

# Health (public)
GET  /health
GET  /health/dependencies
GET  /version

# Integration stubs (Sprint 04 placeholder)
GET  /integrations/croms/ping
GET  /integrations/maintenance/ping
```

## Frontend routes

```
/login                              public
/                                   Dashboard (auth required)
/inspections                        list (di.inspections.read)
/inspections/:id                    detail (di.inspections.read) — + Run comparison + per-vehicle strip (Sprint 03)
/review                             review queue list (di.review.read) — Sprint 03
/review/:id                         review item detail + decision form (di.review.read / di.review.decide) — Sprint 03
/cases                              damage cases list (di.damagecases.read) — Sprint 03
/cases/:id                          damage case detail + status update (di.damagecases.read / .update) — Sprint 03
/reports /admin                     placeholders (Sprint 05)
```

The login form is pre-filled with the primary-tenant admin for Sprint-0x dev convenience.
Remove the pre-fill before any non-dev deployment.
