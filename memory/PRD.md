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

## Completed (this fork, 2026-07-04/05)
- DETAILED FINDINGS REPORT IN OUTBOUND EVENTS (curl + Mongo + UI verified):
  - inspection.completed now carries full `report` (analyzedAt, mode, modelVersion, conditionScore,
    cleanliness, coverage, compact sections+items, verification flags + vehicleConsistency) mapped
    per connector: CROMS `data.findingsReport`, Speed `data.FindingsReport`, Generic `data.data.report`.
    Also adds customerName/inspectorName/vehicleRisk to CROMS payload.
  - Integration pack Section 5: complete findingsReport schema tables (all enums: categories,
    NEW/PRE_EXISTING/RESOLVED/UNCERTAIN, LOW/MEDIUM/HIGH, REPAIR/REPLACE/ASSESS), billing rule
    (only NEW items chargeable), populated JSON example, per-connector field path.
  - Deliveries log now stores/returns requestBody (20KB cap) + 'view payload sent' expander in
    Developer console so counterpart devs can inspect exact payloads from sandbox runs.
- API USAGE METERING + INTEGRATION PACKS (curl + UI screenshot verified):
  - GET /developer/usage: per-API-key billing rollup from audit records (actorId=apikey:<id>) —
    inspections (fast/thorough split via model name), OCR calls, tokens, est cost SAR using
    measured rates (Fast 0.20 / Thorough 0.58 / OCR 0.01 SAR). 'Client usage & billing' table
    in Developer console (dev-usage).
  - GET /developer/integration-pack/{ctype}: downloadable Markdown pack per connector
    (integration_pack_service) — checklist of what we provide vs what counterpart (e.g. GCU365
    CROMS dev) must provide, inbound External API curl samples with live host URLs, outbound
    event schema + per-connector payload samples, HMAC verify code, go-live steps. Download
    buttons on each connector card (dev-connector-pack-{TYPE}).
- INTEGRATION PHASE (tested: backend curl-verified + testing agent iteration_19 all pass):
  - EXTERNAL API (/ext/v1, X-API-Key auth): POST /trip-inspections (async job, 12 photo slots,
    report_fields, save_to_vehicle_history) → GET /trip-inspections/{jobId} → GET /vehicles/{plate}/history.
    Tenant API keys (api_key_service, sha256-at-rest, shown once, revoke, last-used) in di_api_keys.
  - RENTAL-SYSTEM CONNECTORS (connector_service, di_connectors + di_connector_deliveries):
    GENERIC (HMAC-SHA256 signed webhooks: X-DI-Signature v1, retry 0/5/25s, events
    inspection.completed / damage_case.created / connection.test, fired from finalize_trip),
    SPEED_AUTO + GCU365_CROMS adapters with field mapping — ⚠️ SANDBOX MODE until customer
    provides credentials (one switch to live; live requires https baseUrl).
  - DEVELOPER CONSOLE (/developer, sidebar 'API & Integrations', di.configuration.manage):
    key management, connector config + test-event, deliveries log, embedded API docs w/ HMAC verify sample.
  - NAJM-STYLE CLAIM EXPORT: GET /damage-cases/{id}/claim-package (NAJM_STYLE_V1 JSON) +
    'Export insurance claim' button on case detail → JSON download + EN/AR PDF (html2canvas/jsPDF).
  - PDPL FACE/PLATE BLURRING (privacy_service): Gemini box_2d detection ([ymin,xmin,ymax,xmax]) +
    Pillow Gaussian blur in place — faces + BYSTANDER plates blurred, subject vehicle plate kept
    (verified on generated test photo: 4 detected, 3 blurred, subject plate preserved).
    Tenant policy autoBlurUploads (auto at image registration, async) + on-demand
    POST /evidence/{id}/blur + per-image button in InspectionDetail + toggle in TenantSettings.
- FLEET RISK OVERVIEW ON DASHBOARD (self-tested via curl + screenshot):
  - GET /vehicles/risk-overview: totals (vehicles, highCount, mediumCount, totalExposure SAR) +
    top-5 riskiest vehicles ranked by level → exposure → damagedTrips.
  - Dashboard section (dashboard-risk-overview, perm di.inspections.read): exposure/offender/watch
    stats + clickable top-vehicle rows with risk badges → /vehicles/{id}; "All vehicles" link.
- REPEAT-OFFENDER / FLEET RISK SCORING (self-tested via curl + screenshots):
  - _risk_profile in vehicle_registry_service: window = last 5 linked trips; HIGH "Repeat offender"
    (>=3 damaged of last 5 OR streak >=2), MEDIUM "Watch list" (2), LOW/NONE. Includes damagedTrips,
    streak, newIssues, estCostHigh.
  - Surfaced in: vehicles list Risk column (vehicle-risk-{id}), vehicle detail header badge + red/amber
    banner with deposit recommendation (vehicle-risk-banner), Trip Inspection result chip
    (trip-repeat-offender-chip) via vehicleLink.risk from finalize.
- PLATE/VIN OCR + VEHICLE-LINKING (P0, tested via testing agent iteration_18 — all pass):
  - POST /trip-inspection/read-plate: dedicated close-up OCR (Gemini Flash) → plate EN/AR, region,
    VIN (17-char validated), basic vehicle info. Audited as PLATE_OCR_RUN (tokens count in budget/usage).
  - Auto-fill: plate read from walkaround photos (vehicleSignature.visiblePlate) or the OCR close-up
    auto-fills the empty Vehicle plate field with a green 'read from photo/close-up' chip; manual
    typing clears the chip.
  - Vehicle registry (vehicle_registry_service.py, di_vehicles + di_vehicle_trips): finalize links
    trips when 'Save to vehicle history' toggle is ON (default) and a plate/VIN exists. VIN wins
    conflicts (plate-change warning); opt-out keeps trips anonymous. Compact trip snapshots power
    the damage-history timeline (delivers part of P1 timeline).
  - New UI: sidebar 'Vehicles' → /vehicles searchable list + /vehicles/:id detail (stats: trips,
    new issues, cases opened, latest condition + chronological trip timeline with case links).
    Result card shows 'Saved to vehicle history · <plate>' chip linking to the vehicle.
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
- P1: Vehicle damage-history timeline (PARTIALLY DONE via /vehicles detail — remaining: pricing API
  integration off the plate, cross-tenant vehicle lookup); customer-facing transparency report +
  e-signature link; accuracy validation harness + benchmark; finer part taxonomy; real-time guided/auto capture.
- P2: Maintenance cost handoff (DI-0041, blocked on GCU365 sign-off); mobile SDK / public API;
  KSA insurance/claims integration; tyre tread / dash-reading OCR.
- On hold: Kiosk capture mode (per user).

## Mocked
- CROMS and Maintenance integration endpoints.

## Credentials
See /app/memory/test_credentials.md. Admin: admin@riyadah.tech / DamageAdmin#2026 / TENANT-000001.
