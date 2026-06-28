---
id: "DI-SPRINT-02-DELIVERY-NOTES"
title: "Damage Intelligence Sprint 02 — Delivery Notes"
version: "1.0.0"
document_class: "Delivery Notes"
status: "Draft"
classification: "Internal"
owner: "Riyadah Technology"
created: "2026-06-28"
updated: "2026-06-28"
authoritative: false
ai_consumable: true
related: "DI-SPRINT-02, DI-0005, DI-0006, DI-0007, DI-0011, DI-0012, DI-0014, DI-0015, DI-0034, DI-0035"
---

# Sprint 02 Delivery Notes — Production Image Quality & AI Advisory Damage Detection

## Approved Decisions

| ID | Decision |
|----|----------|
| DECISION-Sprint02-a | Real model provider wired via Emergent LLM key. No mock. |
| DECISION-Sprint02-b | **Image quality** model: `gemini:gemini-3.5-flash` (fast/cheap, structured boolean). **Damage detection** model: `gemini:gemini-3.1-pro-preview` (more nuanced). Both swappable via `.env` without code change. |
| DECISION-Sprint02-c | Default confidence threshold: **0.70**. Operator-configurable per-tenant from day one via PUT `/configuration/ai-thresholds` (requires `di.configuration.manage`). |
| DECISION-Sprint02-d | DI-0037-Per-Vehicle-Evidence-Strip.md drafted as a feeder for a later sprint (created in this iteration). |

## Backend (as-built)

```
backend/
├── domain/enums/ai_codes.py                   ← 7 quality statuses, 12 reason codes, 8 AI statuses,
│                                                  6 finding statuses, 8 damage types, 3 severities
├── application/ai/
│   ├── gemini_client.py                       ← async Gemini vision wrapper (LlmChat + FileContentWithMimeType),
│   │                                              60s timeout, 1 retry, structured-JSON extraction with fallback
│   ├── image_quality_service.py               ← assess_image_quality(image) — denormalizes onto di_inspection_images
│   └── damage_detection_service.py            ← run_analysis_for_session + retry_analysis (threshold-aware status)
├── api/routes/ai.py                           ← 9 endpoints (quality x3, ai-analysis x4, configuration x2)
├── infrastructure/db/indexes.py               ← +4 collections of indexes (quality_results, ai_analyses,
│                                                  ai_findings, ai_configuration)
└── tests/smoke_sprint02.py                    ← 15-step end-to-end smoke (passes)
```

## APIs (added; under `/api/v1/damage-intelligence`)

```
POST  /images/{inspectionImageId}/quality-check                (di.ai.request)
GET   /images/{inspectionImageId}/quality-result               (di.ai.read)
POST  /inspection-sessions/{id}/quality-check                  (di.ai.request)  — batch
POST  /inspection-sessions/{id}/ai-analysis                    (di.ai.request)
GET   /ai-analysis/{aiAnalysisId}                              (di.ai.read)
GET   /ai-analysis/{aiAnalysisId}/findings                     (di.ai.read)
GET   /inspection-sessions/{id}/ai-findings                    (di.ai.read)
POST  /ai-analysis/{aiAnalysisId}/retry                        (di.ai.request)
GET   /configuration/ai-thresholds                             (authenticated)
PUT   /configuration/ai-thresholds                             (di.configuration.manage)
```

Every response carries `isAdvisory: true`. Every persisted finding/analysis row carries `modelVersion`, `confidenceThreshold`, `correlationId`, `tenantId`.

## New MongoDB collections

- `di_image_quality_results` (tenant+image+createdAt index)
- `di_ai_analyses` (tenant+session+startedAt, tenant+status)
- `di_ai_findings` (tenant+analysis+confidence desc, tenant+session+createdAt, tenant+status)
- `di_ai_configuration` (unique on tenantId)

## Web

`InspectionDetail.jsx` extended with:
- **Quality check** button (Activity icon) — calls `/inspection-sessions/{id}/quality-check`
- **Run AI** button (Sparkles icon, amber) — calls `/inspection-sessions/{id}/ai-analysis`
- AI advisory output panel showing analysis summary card + per-finding cards (damageType, area, confidence%, severity, status pill, modelVersion). Each card has `data-testid="ai-finding-card-{id}"`.
- Top-level "advisory — not a liability decision" microcopy on the AI panel.

## Failure handling

- Gemini timeout / `ChatError` → 1 retry with backoff → falls back to `qualityStatus=ERROR` or `findings=[]` with `uncertaintyReason="model_unparseable"`. Status row written, audit recorded with `reason` in safeMetadata.
- Malformed / non-JSON model output → same fallback (`UNKNOWN_QUALITY_ISSUE` for quality, empty findings for damage).
- Cross-tenant access on any AI endpoint → `404 NOT_FOUND` (no info leak) + audit row (`EVIDENCE_ACCESS_DENIED`-equivalent for AI).

## Acceptance Criteria

All 12 Sprint-02 ACs PASS via the 15-step smoke test against the **live Gemini API**. Latency on `gemini-3.5-flash`: ~2.4s. Latency on `gemini-3.1-pro-preview`: ~2.0s.

## Known limitations

- AI cost / quota guardrails not implemented — pure per-request behavior. Volume budgeting is a Sprint-05 hardening item.
- Findings retry rebuilds findings only (does not re-run quality checks).
- The `gemini-3.1-pro-preview` model name is a 2026-pinned preview; swap to GA via `DI_AI_MODEL_DAMAGE_NAME` env when GA rolls out.

## Sprint 02 smoke test

```bash
cd /app/backend && set -a && source .env && set +a && /root/.venv/bin/python tests/smoke_sprint02.py
```

Expected final line: `Sprint 02 production image quality + AI detection smoke test passed.`
