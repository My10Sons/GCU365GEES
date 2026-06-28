---
id: "DI-0037"
title: "Per-Vehicle Evidence Strip — Inspector Enhancement Brief"
version: "0.1.0"
document_type: "Enhancement Brief"
document_class: "Brief"
status: "Draft"
classification: "Internal"
owner: "Riyadah Technology"
created: "2026-06-28"
updated: "2026-06-28"
authoritative: false
ai_consumable: true
related: "DI-0004, DI-0011, DI-0012, DI-0034, DI-SPRINT-02"
---

# DI-0037 — Per-Vehicle Evidence Strip (Inspector Enhancement Brief)

## Why

In the field, an inspector capturing a `CHECK_OUT` or `CHECK_IN` session has no
visibility into the **same vehicle's previously-registered evidence** in
Damage Intelligence. This leads to (a) double-recording of pre-existing damage,
(b) missed comparison anchors, and (c) more AI false-positives because the
detector has no prior context.

A small, advisory-only widget that surfaces the **last N images for the same
`externalVehicleRef`** within the principal's tenant — without ever crossing
tenant or ownership boundaries — directly improves accuracy of the existing
Sprint-02 AI pipeline AND the Sprint-03 comparison workflow.

## What

A horizontally-scrollable strip on **InspectionDetail** that shows up to 12
thumbnail tiles for the **same `externalVehicleRef`** captured in the same
tenant, in reverse-chronological order, **excluding the current session's
images**. Each tile shows:

- the previous inspection's type (CHECK_OUT / CHECK_IN / SPOT_CHECK / …)
- the capture position
- the registered date
- an "Open" button that requests a fresh time-limited access link
  (`POST /evidence/{evidenceId}/access-link`) — never a long-lived URL.

The strip is **advisory** and **does not pre-decide** that previous damage
is present on the current vehicle. It is a memory aid for the human inspector,
not a charge / liability decision.

## What it must NOT do

- It must not cross tenant boundaries.
- It must not expose raw `objectPath` or unrestricted URLs.
- It must not write to CROMS, Maintenance, or Fleet.
- It must not pre-mark current findings as duplicates of past findings — that
  is Sprint 03's comparison job.
- It must not aggregate or display data the inspector's role does not have
  permission to read.

## API addition

```
GET /api/v1/damage-intelligence/inspection-sessions/{id}/per-vehicle-strip
  ?limit=12&excludeCurrent=true
Permission: di.inspections.read AND di.images.read
Returns: { items: [{ inspectionSessionId, inspectionType, capturePosition,
                     inspectionImageId, evidenceId, capturedAt }], total }
```

## Data already available

- `di_inspection_sessions.references.externalVehicleRef` (indexed,
  tenant-scoped — Sprint 01)
- `di_inspection_images` (tenant + session + createdAt — Sprint 01)
- `di_evidence_references` (image → evidence — Sprint 01)

No new collection is required.

## UI

Place under the Lifecycle / Evidence summary cards on `InspectionDetail`,
above the current `Inspection images` grid. Strip is collapsible. Empty state:
"No prior evidence in this tenant for this vehicle reference."

## Acceptance

- A1. Endpoint returns up to N items for the same `externalVehicleRef`,
  excluding the current session's images.
- A2. Cross-tenant request returns 404.
- A3. Each tile's "Open" button calls `POST /evidence/{id}/access-link` and
  opens a freshly-signed URL in a new tab.
- A4. No raw URLs / object paths appear in the response payload.
- A5. Audit row written for every tile opened.

## Suggested sequencing

Implement in **Sprint 03** alongside the damage comparison workflow — both
share the same per-vehicle-history data model and can be tested together.
Total estimated work: ½ backend day + ½ frontend day + ½ QA day.

## Status

Drafted on 2026-06-28 as a feeder doc per user request after TASK-03
(Sprint 02) completion. Not yet authoritative — promote to authoritative
spec when product owner approves the scope.
