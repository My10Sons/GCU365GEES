---
id: "DI-SPRINT-03-DELIVERY"
title: "Sprint 03 Delivery Notes — Production Review, Comparison, and Damage Cases"
status: "Delivered"
created: "2026-06-28"
---

# Sprint 03 Delivery Notes (TASK-04)

Delivered against `implementation/SPRINT-03-Production-Review-Comparison-and-Damage-Cases.md`
(authoritative) and the four locked decisions in `memory/PRD.md`.

## Locked decisions honored

- **DECISION-Sprint03-a** — Comparison accepts explicit `baselineInspectionSessionId` OR
  auto-anchors to the most recent prior **SUBMITTED** inspection for the same
  `externalVehicleRef` within the tenant.
- **DECISION-Sprint03-b** — LOW_CONFIDENCE / UNCERTAIN findings auto-route to the review
  queue on Run AI; review-required comparison results auto-route on Run comparison.
  Per-tenant opt-out via `autoRouteLowConfidence` (default true) on `di_ai_configuration`.
- **DECISION-Sprint03-c** — Comparison classification uses the authoritative DI-SPRINT-03
  code set: `NEW, PRE_EXISTING, CHANGED, REPAIRED, UNCERTAIN, NOT_COMPARABLE`
  (the product-owner 4-class names map onto these).
- **DECISION-Sprint03-d** — DI-0037 Per-Vehicle Evidence Strip delivered in this sprint.

## AI

Comparison uses **real Gemini multimodal vision** (`gemini-3.1-pro-preview`) via a new
`call_vision_model_multi` helper — baseline image + current image are sent together per
overlapping capture position. Output is **advisory**. Missing baseline / no overlapping
position → `NOT_COMPARABLE`; never auto-confirms new damage.

## Endpoints (13, all under `/api/v1/damage-intelligence`)

```
POST   /inspection-sessions/{id}/comparison
GET    /inspection-sessions/{id}/comparisons
GET    /comparisons/{comparisonId}
GET    /inspection-sessions/{id}/per-vehicle-strip      (DI-0037)
GET    /review-queue
GET    /review-items/{reviewItemId}
POST   /review-items/{reviewItemId}/decision
POST   /review-items/{reviewItemId}/additional-evidence-request
POST   /damage-cases
GET    /damage-cases
GET    /damage-cases/{damageCaseId}
PATCH  /damage-cases/{damageCaseId}/status
POST   /damage-cases/{damageCaseId}/link-evidence | link-finding | link-comparison
```

## Collections (10 new, tenant-scoped indexes)

`di_damage_comparisons`, `di_damage_comparison_results`, `di_review_queue_items`
(unique on tenant+objectType+objectId), `di_review_decisions`,
`di_additional_evidence_requests`, `di_damage_cases`, `di_damage_case_status_history`,
`di_damage_case_links` (unique on tenant+case+linkType+linkedId).

## Acceptance & tests

All AC-DI-S03-001..011 satisfied. `backend/tests/smoke_sprint03.py` (17 assertion blocks)
green incl. real Gemini comparison + cross-tenant isolation + URL-leak negative checks.
Sprint 00/01/02 regressions green (stale 404 guards updated). Testing agent iteration_6:
backend 100% (17/17), frontend 100% on all ACs, 0 issues.

## Ownership boundary

Damage Intelligence owns comparison/review/case **context** only. No customer charge,
rental closure, actual repair cost, or work-order execution is created — these remain with
CROMS / Maintenance / Finance.
