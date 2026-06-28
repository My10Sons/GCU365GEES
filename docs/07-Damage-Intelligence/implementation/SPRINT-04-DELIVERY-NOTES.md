---
id: "DI-SPRINT-04-DELIVERY"
title: "Sprint 04 Delivery Notes — Production CROMS and Maintenance Integration"
status: "Delivered"
created: "2026-06-28"
---

# Sprint 04 Delivery Notes (TASK-05)

Delivered against `implementation/SPRINT-04-Production-CROMS-and-Maintenance-Integration.md`
(authoritative), DI-0017, DI-0018, DI-0031, DI-0034.

## Endpoints (all under `/api/v1/damage-intelligence`)

```
POST  /integrations/croms/check-out-inspections           (di.integrations.croms, idempotent)
POST  /integrations/croms/check-in-inspections            (di.integrations.croms, idempotent)
GET   /integrations/croms/rental-agreements/{id}/damage-summary
GET   /integrations/croms/inspection-sessions/{id}/status
POST  /integrations/croms/notifications/damage-summary-ready
POST  /integrations/maintenance/handoffs                  (di.integrations.maintenance, idempotent)
POST  /integrations/maintenance/work-order-references
POST  /integrations/maintenance/repair-status-updates
POST  /integrations/maintenance/rejection-reasons
POST  /integrations/maintenance/additional-evidence-requests
GET   /integrations/maintenance/damage-cases/{id}/handoff-status
```

The Sprint 00 `/integrations/croms/ping` and `/integrations/maintenance/ping` stubs remain
for the Sprint 00 routing smoke.

## Idempotency

`X-Idempotency-Key` on write operations. Records in `di_integration_idempotency_records`
(unique on tenant+key). Same key+payload → stored response replayed; same key+different
payload → `IDEMPOTENCY_CONFLICT` (409), audited. SHA-256 request hash.

## Ownership boundaries (enforced & asserted in smoke)

- CROMS damage summary always returns `finalCustomerChargeDecision = NOT_OWNED_BY_DAMAGE_INTELLIGENCE`.
- Maintenance handoff / work-order / repair-status responses carry
  `workOrderExecutionOwnedBy = GCU365Maintenance` and store `actualRepairCostReference`
  as a reference only (`actualRepairCostOwnedBy = GCU365Maintenance`).
- DI stores CROMS/Maintenance data as references; never closes rentals, charges customers,
  executes work orders, or owns repair cost.

## Security & isolation

- Every endpoint gated by `di.integrations.croms` / `di.integrations.maintenance`
  (non-integration principals → 401/403).
- Strict tenant scoping — cross-tenant reads → 404.
- No raw objectPath / unrestricted evidence URLs / secrets in payloads or logs.
- Full audit action set (CROMS_*, MAINTENANCE_*, IDEMPOTENCY_CONFLICT_DETECTED, …).

## Collections (3 new) + seed

`di_maintenance_handoffs`, `di_maintenance_references`, `di_maintenance_status_updates`
(tenant-scoped indexes). `di_integration_idempotency_records` index pre-existed.
Seeded `DI_IntegrationService` accounts in both tenants (see `memory/test_credentials.md`).

## Web

Damage-case detail surfaces read-only Maintenance integration context (handoffs / work
orders / repair status) via `maintenanceContext` on the case GET (`di.damagecases.read`).

## Tests

`backend/tests/smoke_sprint04.py` — 16 steps green (idempotency replay + conflict,
ownership boundaries, tenant isolation, auth). Sprint 00–03 regressions green.
Testing agent iteration_7 — backend 100%, frontend 100%, 0 issues.

## Notes / deferred

- `reportReference` and `evidencePackageReference` in CROMS summary / handoff are currently
  `null` — damage reports + evidence packages are Sprint 05 scope.
- Outbound CROMS/Maintenance delivery is stubbed (`CromsClientStub` / `MaintenanceClientStub`);
  inbound APIs + persistence are fully real.
