# DI-0041 — Damage Intelligence → GCU365Maintenance Cost-Estimation Interface

**Status:** Draft for GCU365Maintenance team review
**Owner:** Damage Intelligence (DI)
**Related:** DI-0010 (Repair Cost Estimation), DI-0018 (Integration with Maintenance),
DI-0031 (Existing System Integration Scope), DI-0034 (OpenAPI Contract), DI-0012 (Domain Model).

---

## 1. Purpose & ownership boundary

Damage Intelligence detects and describes vehicle damage from inspection photos. It produces
**advisory** findings only. It does **not** own — and will not be the system of record for —
repair cost, parts pricing, labour rates, work-order execution, or the final customer charge.

This document defines the interface by which **DI hands a structured damage package to
GCU365Maintenance**, and **Maintenance returns the repair cost estimate**. Cost estimation logic
(OEM vs aftermarket parts, labour hours, paint, local KSA/GCC rates) lives entirely inside
GCU365Maintenance, which already holds the workshop pricing data, supplier catalogues, and
labour-rate agreements.

```
  ┌────────────────────┐    1. damage package (findings + evidence)   ┌─────────────────────┐
  │  Damage Intelligence│ ───────────────────────────────────────────►│  GCU365Maintenance  │
  │  (advisory only)    │                                              │  (owns cost + work) │
  │                     │◄─────────────────────────────────────────── │                     │
  └────────────────────┘    2. cost estimate (parts/labour/total)      └─────────────────────┘
```

**DI keeps the returned estimate as a reference** (`actualRepairCostReference` /
`advisoryEstimateReference`) attached to the damage case. It never recomputes, overrides, or
charges from it. Final liability and customer charge remain with CROMS/Finance.

---

## 2. Why this split (rationale)

- **Single source of truth for money.** Pricing already exists in Maintenance (supplier
  catalogues, refurbished/aftermarket options, technician labour rates, KSA SAR currency).
  Duplicating it in DI would create drift and disputes.
- **Local accuracy.** GCC repair pricing is relationship- and shop-driven; Maintenance has the
  real rate cards. DI's current rule-based table is a placeholder only.
- **Clean liability story.** DI stays advisory; "the cost came from the workshop system" is
  defensible to customers and auditors.
- **Less vendor spend.** Avoids licensing a US/EU estimatics API (e.g. Audatex) just to
  re-localise its numbers; Maintenance already prices work in-market.

---

## 3. Flow A — Cost-estimation request (DI → Maintenance)

**Direction:** DI calls Maintenance (new endpoint owned by Maintenance), OR DI exposes the package
and Maintenance pulls it. Recommended: **DI POSTs the package to a Maintenance endpoint** so DI
controls when a case is "ready for estimation".

**Trigger:** a DI reviewer (or the auto-routed high-value trip case) marks a damage case
`READY_FOR_MAINTENANCE_REVIEW`. DI sends the estimation request.

### 3.1 Request payload (DI → Maintenance)

```jsonc
{
  "damageCaseId": "665f...e21",            // DI case id (idempotency anchor)
  "tenantId": "TENANT-000001",
  "correlationId": "…",                    // echoed back for traceability
  "vehicle": {
    "externalVehicleRef": "ABC-1234",      // plate / fleet id (may be synthetic TRIP-XXXX)
    "vin": null,                            // populated once VIN/plate OCR ships
    "makeModel": null,                      // optional, free text if known
    "year": null
  },
  "severityCode": "HIGH",                   // worst severity across findings: LOW|MEDIUM|HIGH
  "inspectionSessionId": "665f...a01",
  "evidencePackageReference": {             // signed, time-limited — NO public URLs
    "type": "EVIDENCE_PACKAGE_REPORT",
    "accessLink": "…/internal/storage/access?path=&exp=&sig=",
    "expiresAt": "2026-06-30T12:00:00Z"
  },
  "advisoryEstimateReference": {            // DI's OWN rough estimate, advisory only
    "currency": "SAR",
    "low": 800, "high": 1360,
    "method": "DI_RULE_BASED_PLACEHOLDER"
  },
  "findings": [
    {
      "findingId": "665f...f10",
      "kind": "EXTERIOR",                   // EXTERIOR | INTERIOR
      "capturePosition": "FRONT",           // FRONT|REAR|LEFT|RIGHT|ROOF|INTERIOR
      "category": "DENT",                   // DI damage taxonomy (DI-0008)
      "status": "NEW",                      // NEW|PRE_EXISTING|RESOLVED|UNCERTAIN
      "severity": "HIGH",                   // LOW|MEDIUM|HIGH|null
      "confidence": 0.88,                   // 0..1 advisory confidence
      "location": "front bumper, left",
      "detail": "deep dent with paint scrape",
      "sizeCm": 18.5,                        // est. longest dimension, may be null
      "sizeNote": "scaled against license plate",
      "recommendation": "REPAIR",           // REPAIR|REPLACE|ASSESS (advisory hint only)
      "boundingBox": { "x": 0.31, "y": 0.62, "w": 0.12, "h": 0.08 }  // normalized on after-image
    }
  ],
  "requestedBySystem": "DI-Web",
  "requestedAt": "2026-06-29T21:00:00Z"
}
```

Notes:
- **Advisory labels only.** `severity`, `recommendation`, `advisoryEstimateReference` are hints;
  Maintenance is free to override with its own pricing engine and technician judgement.
- **No raw image bytes.** Photos are reached via signed, expiring `accessLink`s (DI-0014).
- `damageCaseId` + `tenantId` form the **idempotency key**; re-sending the same case must not
  create a duplicate estimate.

---

## 4. Flow B — Cost estimate response (Maintenance → DI)

Maintenance returns the estimate via the existing repair-status / estimate callback into DI
(`POST /integrations/maintenance/repair-status-updates`, gated by `di.integrations.maintenance`).
DI stores it as **reference only**.

### 4.1 Response payload (Maintenance → DI)

```jsonc
{
  "damageCaseId": "665f...e21",
  "tenantId": "TENANT-000001",
  "correlationId": "…",                    // echo the request correlationId
  "estimate": {
    "estimateId": "MNT-EST-99821",         // Maintenance system of record id
    "status": "ESTIMATED",                 // ESTIMATED | NEEDS_MORE_EVIDENCE | DECLINED
    "currency": "SAR",
    "totals": { "parts": 1450, "labour": 600, "paint": 300, "total": 2350 },
    "validUntil": "2026-07-15",
    "lineItems": [
      {
        "findingId": "665f...f10",          // maps back to DI finding (may be null if merged)
        "operation": "REPLACE",             // REPAIR | REPLACE | REFINISH | BLEND
        "partType": "AFTERMARKET",          // OEM | AFTERMARKET | REFURBISHED | NA
        "partCost": 950,
        "labourHours": 2.5,
        "labourCost": 375,
        "paintCost": 150,
        "lineTotal": 1475,
        "note": "left front bumper assembly"
      }
    ],
    "assumptions": "Aftermarket bumper; standard Riyadh labour rate.",
    "estimatedBy": "GCU365Maintenance",
    "estimatedAt": "2026-06-29T21:20:00Z"
  }
}
```

`status` values:
- `ESTIMATED` — full cost returned.
- `NEEDS_MORE_EVIDENCE` — Maintenance wants more/clearer photos; pairs with DI's
  `additional-evidence-requests` flow → DI moves the case to `ADDITIONAL_EVIDENCE_REQUIRED`.
- `DECLINED` — out of scope / not repairable through workshop.

### 4.2 What DI does with the response
- Stores `estimate` against the case as `actualRepairCostReference` (reference only).
- Surfaces it read-only on the Damage Case detail screen ("Maintenance estimate") alongside DI's
  own advisory range, clearly labelled as **owned by GCU365Maintenance**.
- Writes an audit row (`MAINTENANCE_REPAIR_STATUS_UPDATED`). DI never charges from it.

---

## 5. Contract guarantees & non-functional rules

| Topic | Rule |
|-------|------|
| Auth | Service-to-service JWT + `di.integrations.maintenance`; tenant `X-Tenant-Id` cross-checked. |
| Tenant isolation | Estimates are tenant-scoped; cross-tenant access → 404. |
| Idempotency | `damageCaseId` + `tenantId` (+ optional `X-Idempotency-Key`); replays return the stored result. |
| Evidence access | Signed, time-limited links only — no public URLs, no raw bytes in payload or logs. |
| PII / secrets | No customer PII, tokens, stack traces, or object paths in payloads or logs. |
| Currency | Maintenance is authoritative; DI echoes Maintenance's `currency` verbatim. |
| Versioning | `interfaceVersion: "1.0"` header; additive changes only within a major version. |
| Ownership note | Every estimate stored in DI carries `workOrderExecutionOwnedBy: GCU365Maintenance`. |

---

## 6. Mapping to what already exists (so this is low-build)

| Need | Already in the system? |
|------|------------------------|
| Handoff DI → Maintenance | ✅ `POST /integrations/maintenance/handoffs` (carries `advisoryEstimateReference`, `evidencePackageReference`, `severityCode`). |
| Estimate back into DI | ✅ `POST /integrations/maintenance/repair-status-updates` (accepts `actualRepairCostReference`). |
| Read-only estimate on case | ✅ `maintenanceContext` on `GET /damage-cases/{id}`. |
| Structured per-finding package | ⬜ **NEW** — extend the handoff/estimate request with the `findings[]` array above. |
| Dedicated "estimate request" semantics | ⬜ **NEW (optional)** — either reuse `handoffs` or add `POST /integrations/maintenance/cost-estimate-requests`. |
| Per-line-item estimate shape | ⬜ **NEW** — Maintenance to adopt the `lineItems[]` response shape. |

**Net:** the transport, auth, idempotency, evidence-link, and storage mechanisms already exist.
The only additions are the **`findings[]` request array** and the **`lineItems[]` estimate shape** —
and Maintenance owning the estimation logic.

---

## 7. Open questions for the GCU365Maintenance team

1. **Push or pull?** Should DI POST the package to a Maintenance endpoint, or expose it for
   Maintenance to pull on a trigger? (DI recommends push on `READY_FOR_MAINTENANCE_REVIEW`.)
2. **Reuse or new endpoint?** Extend the existing `handoffs` call to carry `findings[]`, or add a
   dedicated `cost-estimate-requests` endpoint? (DI recommends reuse for v1.)
3. **Estimate granularity.** Per-finding line items, or a single case-level total? (DI prefers
   per-finding so it can map costs back to specific damage.)
4. **VIN dependency.** Does Maintenance pricing need VIN/make-model? (Drives priority of DI's
   pending plate/VIN OCR feature.)
5. **SLA.** Expected turnaround for an estimate (sync response vs async callback)? DI assumes
   **async callback**.
6. **Decline / more-evidence loop.** Confirm `NEEDS_MORE_EVIDENCE` should drive DI's
   `ADDITIONAL_EVIDENCE_REQUIRED` case status.

---

## 8. Next steps

1. GCU365Maintenance reviews §3–§4 payloads and answers §7.
2. Freeze `interfaceVersion 1.0`.
3. DI implements the `findings[]` request extension + read-only estimate display.
4. Maintenance implements estimation + `lineItems[]` callback.
5. Joint test against `TENANT-000001` using a real auto-routed trip case.
