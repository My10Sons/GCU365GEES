# Damage Intelligence — PRD

## Problem statement
Production-ready, multi-tenant image-analysis and damage-detection platform. Manages inspection
evidence, AI-assisted damage detection (Gemini), damage comparison, review queues, damage cases,
external integrations, light/dark mode, and an anonymous before/after Trip Inspection tool with
visual bounding-box issue markers. Recent focus: AI token telemetry, cost discovery, monthly budget
tracking, per-section streaming, and Fast/Thorough model tiering.

## Stack / Architecture
- Backend: FastAPI, Clean Architecture (api / application / domain / infrastructure), Motor async Mongo.
  Auth = JWT + bcrypt (run via `asyncio.to_thread` — do NOT revert to sync).
- Frontend: React 19, Tailwind. Pages under src/pages, Shell.jsx nav, constants/testIds.js.
- AI: Gemini via emergentintegrations.LlmChat. Fast=gemini-3.5-flash, Thorough=gemini-3.1-pro-preview.
  Per-section concurrent streaming (`analyze-section`) + `finalize`. Token usage from ChatResponse.usage.
- Deployment: user deploys to production `damage-cases.emergent.host`; agent only has PREVIEW. Redeploy needed to propagate.

## Key endpoints
- POST /api/v1/damage-intelligence/trip-inspection/analyze-section
- POST /api/v1/damage-intelligence/trip-inspection/finalize
- GET  /api/v1/damage-intelligence/trip-inspection/usage?days=N
- GET/PUT /api/v1/damage-intelligence/trip-inspection/budget

## Completed (this fork, 2026-07-04)
- IMAGE VERIFICATION EXPANSION (all 10 asks, tested 14/14 via testing agent, iteration_17):
  - AI per-section checks (prompt + normalizers in trip_inspection_service.py): angle-mismatch
    (angleCorrect/angleIssue), framing/cropped parts (fullyVisible/croppedParts), camera distance
    (OK/TOO_CLOSE/TOO_FAR), screen-recapture likelihood, environment (dirtObscuring/wetSurface/glare
    /notes/confidenceReduced), vehicleSignature (color/bodyType/visiblePlate).
  - EXIF metadata verification (exif_check.py): missing EXIF, stale (>72h, DI_TRIP_EXIF_MAX_AGE_HOURS),
    future timestamp, editing software, Before/After chronology. Client extracts EXIF from ORIGINAL
    file via exifr (canvas strips it) and sends before_meta/after_meta JSON to analyze-section.
  - Cross-angle vehicle consistency in finalize: result.vehicleConsistency (colors/bodyTypes/platesRead/
    plateMatch vs entered plate + warnings). UI: green 'Same vehicle verified' chip (>=2 angles or plate
    match) or 'Vehicle identity check' warning panel; 4 section warning panels (photo/integrity/
    environment/metadata); aggregate flags hasEnvironmentWarnings/hasMetadataWarnings; PDF verification
    warnings block (EN/AR).

## Completed (prior fork, 2026-07-03)
- AI Cost Discovery COMPLETE. Empirical rates measured on live Universal Key (USD; SAR at 3.75 peg):
  - Fast (gemini-3.5-flash): 40 calls / 165,501 tok, $0.42 delta → ~$0.00254 (0.0095 SAR) /1K; ~0.20 SAR / 5-angle inspection.
  - Thorough (gemini-3.1-pro-preview): 40 calls / 153,686 tok, $1.24 delta → ~$0.00807 (0.0303 SAR) /1K; ~0.58 SAR / 5-angle inspection.
  - Thorough ≈ 3x Fast. Wired into AiUsage.jsx: two mode cards + full breakdown table + auto-prefill of cost/1K field (SAR) when unset.

## Prior completed work
Auto-route high-severity trip damage to Damage Cases; live PDF preview on Tenant Settings; SAR default
(QAR removed); SEO static files; bcrypt non-blocking fix; AI speed tiering; per-section streaming;
auto-escalate Fast→Pro; bilingual Help; AI token telemetry; AI Usage dashboard + monthly budget + sidebar badge.
Docs: DI-0041 (Maintenance cost interface, awaiting sign-off), DI-0042 (scaling runbook), DI-0043 (cost discovery plan).

## Backlog
- P0: License plate / VIN OCR (auto vehicle-linking + pricing API).
- P1: Vehicle damage-history timeline; customer-facing transparency report + e-signature link;
  accuracy validation harness + benchmark; finer part taxonomy; real-time guided/auto capture.
- P2: Maintenance cost handoff (DI-0041, blocked on GCU365 sign-off); mobile SDK / public API;
  KSA insurance/claims integration; tyre tread / dash-reading OCR.
- On hold: Kiosk capture mode (per user).

## Mocked
- CROMS and Maintenance integration endpoints.

## Credentials
See /app/memory/test_credentials.md. Admin: admin@riyadah.tech / DamageAdmin#2026 / TENANT-000001.
