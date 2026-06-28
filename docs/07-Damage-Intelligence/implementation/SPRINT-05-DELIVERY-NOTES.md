---
id: "DI-SPRINT-05-DELIVERY"
title: "Sprint 05 Delivery Notes — Production Reports, Monitoring, Security and Release"
status: "Delivered (core scope)"
created: "2026-06-28"
---

# Sprint 05 Delivery Notes (TASK-06)

Delivered against `implementation/SPRINT-05-Production-Reports-Monitoring-Security-and-Release.md`
(authoritative), DI-0016, DI-0023, DI-0014, DI-0034.

## Endpoints (all under `/api/v1/damage-intelligence`)

```
POST  /reports                          (di.reports.generate)
GET   /reports                          (di.reports.read)
GET   /reports/{reportId}               (di.reports.read)
POST  /reports/{reportId}/access-link   (di.reports.access)  -> signed, time-limited
GET   /monitoring/metrics               (authenticated, tenant-scoped)
GET   /monitoring/dependencies          (authenticated)
```

## Reports

Seven report types: `INSPECTION_SUMMARY_REPORT`, `DAMAGE_DETECTION_REPORT`,
`DAMAGE_COMPARISON_REPORT`, `DAMAGE_CASE_REPORT`, `RENTAL_DAMAGE_SUMMARY_REPORT`,
`MAINTENANCE_HANDOFF_REPORT`, `EVIDENCE_PACKAGE_REPORT`. Generated synchronously from existing
tenant data, stored as JSON under `tenants/{tenant}/damage-intelligence/reports/{id}.json`,
served only through **HMAC-signed time-limited** access links (reuse of the evidence
`/internal/storage/access` mechanism). No public/unrestricted URLs. AI outputs labelled
advisory; ownership boundaries embedded in content.

## Monitoring

Tenant-scoped metrics across workflow, AI, review, cases, reports, integration, and security.
Dependency health (mongo/ai/storage). Surfaced on the Dashboard via metric tiles and the
**Integration Health widget** (CROMS check-outs/check-ins, handoffs sent/rejected, callbacks
received, idempotency conflicts, tenant-scope violations, unauthorized attempts).

## Security hardening

- Login pre-fill removed (empty credential fields).
- Report/evidence access: authorized (di.reports.*), tenant-scoped, audited, signature-gated;
  tamper → 403, cross-tenant → 404, missing reference → 400.
- No raw objectPath / public URLs / secrets in metadata responses or logs.

## Tests

`backend/tests/smoke_sprint05.py` — 13 steps green (generation, evidence package, get/list,
signed-link serve, tamper-reject, authz negative, tenant isolation, validation, ownership,
metrics). Sprint 00–04 regressions green. Testing agent iteration_8 — backend 100%,
frontend 100%, 0 issues.

## Deferred (ops / governance, not application code)

- Production object store provider swap (local-disk abstraction in place).
- External monitoring/alerting (Grafana/Prometheus), operational runbooks, DR drills,
  rollback/release approval sign-offs, formal production release-gate approvals.
- Linking generated reports into CROMS summary / Maintenance handoff `reportReference` /
  `evidencePackageReference` (currently null).
