# Test Credentials — Damage Intelligence (Sprint 00 baseline)

These accounts are seeded at backend startup by
`infrastructure/seed/admin_seed.py` (idempotent). Passwords come from
`/app/backend/.env`.

## Tenant

| Tenant Id | Notes |
|-----------|-------|
| `TENANT-000001` | Default tenant for Sprint 00 baseline |

## Accounts

| Role | Email | Password | Permissions |
|------|-------|----------|-------------|
| **DI_Admin** | `admin@riyadah.tech` | `DamageAdmin#2026` | 21 (every business permission + di.configuration.manage + di.audit.read) |
| **DI_Inspector** | `inspector@riyadah.tech` | `Inspector#2026` | 9 (inspection capture + image upload + AI request/read + comparison read + evidence access) |
| **DI_Reviewer** | `reviewer@riyadah.tech` | `Reviewer#2026` | 12 (review queue + decisions + damage cases + reports + comparison) |

## API base

```
Base URL : ${REACT_APP_BACKEND_URL}/api/v1/damage-intelligence
Login    : POST /auth/login   body: { email, password }
Refresh  : POST /auth/refresh body: { refreshToken }
Self     : GET  /auth/me      headers: Authorization: Bearer <token>, X-Tenant-Id: TENANT-000001
Logout   : POST /auth/logout  headers: Authorization: Bearer <token>
Health   : GET  /health, GET /health/dependencies, GET /version (public)
Stubs    : GET  /integrations/croms/ping, GET /integrations/maintenance/ping (public, Sprint-04 deferral note)
```

## Frontend route

```
Login screen : /login
Dashboard    : /            (requires authentication)
Placeholders : /inspections /review /cases /reports /admin
```

The login form is pre-filled with the admin credentials for Sprint 00 dev
convenience. Remove the pre-fill before any production release.
