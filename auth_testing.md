# Damage Intelligence — Auth Testing Playbook (Sprint 00)

Repository Traceability: DI-0034 (Authentication, Authorization, Standard Headers),
DI-0014 (Security and Privacy), DI-SPRINT-00 (Identity baseline).

## Test Accounts (seeded by `infrastructure/seed/admin_seed.py`)

| Email | Password | Role | Tenant |
|-------|----------|------|--------|
| admin@riyadah.tech     | DamageAdmin#2026 | DI_Admin    | TENANT-000001 |
| inspector@riyadah.tech | Inspector#2026   | DI_Inspector | TENANT-000001 |
| reviewer@riyadah.tech  | Reviewer#2026    | DI_Reviewer  | TENANT-000001 |

## Auth endpoints (all under `/api/v1/damage-intelligence`)

- `POST /auth/login`      — body: `{ email, password, tenantId? }` → access + refresh tokens + principal
- `POST /auth/refresh`    — body: `{ refreshToken }` → new access token
- `GET  /auth/me`         — header: `Authorization: Bearer <access>` (and `X-Tenant-Id: <tenant>`)
- `POST /auth/logout`     — header: `Authorization: Bearer <access>` (audited)

## Required headers

```
Authorization: Bearer <access_token>     (every protected route)
X-Tenant-Id:   TENANT-000001              (cross-checked against JWT claim)
X-Correlation-Id: <any string>            (generated if missing; echoed in response)
Content-Type: application/json
```

## Response envelope

```json
{ "success": true,  "correlationId": "CORR-...", "data": { ... }, "errors": [] }
{ "success": false, "correlationId": "CORR-...", "data": null,    "errors": [{"code":"...","message":"...","field":"..?"}] }
```

## Step-by-step curl walk-through

```bash
BASE="$REACT_APP_BACKEND_URL/api/v1/damage-intelligence"

# 1. Login admin
LOGIN=$(curl -sS -X POST "$BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@riyadah.tech","password":"DamageAdmin#2026"}')
echo "$LOGIN" | python3 -m json.tool
TOKEN=$(echo "$LOGIN" | python3 -c "import sys,json;print(json.load(sys.stdin)['data']['accessToken'])")

# 2. /auth/me with bearer + correct tenant
curl -sS "$BASE/auth/me" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-Id: TENANT-000001"

# 3. Tenant mismatch (must return TENANT_SCOPE_VIOLATION)
curl -sS "$BASE/auth/me" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-Id: WRONG-TENANT"

# 4. Wrong password (must return UNAUTHORIZED with safe message, no stack trace)
curl -sS -X POST "$BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@riyadah.tech","password":"WrongPassword"}'

# 5. Brute-force: 5 failed attempts in a row -> 6th returns FORBIDDEN (locked)
for i in 1 2 3 4 5; do
  curl -sS -X POST "$BASE/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"admin@riyadah.tech","password":"wrong"}' > /dev/null
done
curl -sS -X POST "$BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@riyadah.tech","password":"wrong"}'
```

## MongoDB verification

```bash
mongosh damage_intelligence --quiet --eval '
  print("--- users ---");
  db.di_users.find({}, {email:1, roles:1, tenantId:1, status:1}).pretty();
  print("--- bcrypt prefix on admin ---");
  print(db.di_users.findOne({email:"admin@riyadah.tech"}).passwordHash.substring(0,4));
  print("--- audit records (latest 5) ---");
  db.di_audit_records.find({}, {action:1,actorId:1,timestamp:1,correlationId:1}).sort({timestamp:-1}).limit(5).pretty();
'
```

Expected: bcrypt prefix `$2b$`, unique index on `(tenantId,email)`, audit records for every login.

## Running the automated smoke test

```bash
cd /app/backend && /root/.venv/bin/python tests/smoke_sprint00.py
```

Expected last line: `Sprint 00 smoke test passed.`
