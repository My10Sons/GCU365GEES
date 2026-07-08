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
- STEP-BY-STEP DEVELOPER GUIDE IN INTEGRATION PACK (verified: downloaded pack renders with live
  URLs, correct curl + C#/.NET samples): new Section 2 'What your team needs to develop' —
  Step 0 prerequisites, Step 1 photo capture/storage rules (JPEG/PNG/WebP, 12MB, before at
  check-out / after at check-in per angle), Step 2 submit multipart (curl + C# HttpClient),
  Step 3 receive report (webhook receiver spec w/ 2xx-in-10s + dedupe, or polling), Step 4
  how to process the report (NEW items chargeable, verification flags → manual review,
  damageCaseId + vehicleRisk usage), Step 5 error table, Step 6 sandbox acceptance checklist.
  Sections renumbered 1-7. NOTE: inbound CROMS check-out/check-in push endpoint deemed
  unnecessary — flow is CROMS-initiated via External API.
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

## Completed (this fork, 2026-07-09) — Bug fixes: 60s ingress wall + bumper-corner detection
- "Analysis failed. Please retry." root cause: sync POST /trip-inspection/analyze-section exceeded
  the Kubernetes ingress 60s wall (502) after the detail pass lengthened analysis to 70-120s.
  Fix: async job architecture — POST /trip-inspection/analyze-section-start → jobId; GET
  /trip-inspection/section-jobs/{jobId} (di_section_jobs, tenant-isolated); TripInspection.jsx now
  starts + polls every 4s. Old sync endpoint kept for API compat.
- Thorough-mode missed left bumper-corner scratches: prompts now explicitly scan bumper CORNERS/side
  ends (main protocol step 3 + detail-scan half prompt). Verified detected in both fast & thorough.
- Fixed compile-blocking react-hooks lint: renamed TripInspection helper useRental → applyRental.
- Verified: iteration_22 (backend 13/13 pytest incl. tenant isolation, fast+thorough real jobs) and
  iteration_23 (frontend E2E 100%: upload → analyze → streaming → verdict, no error banner).
- Reusable pytest: /app/backend/tests/test_iter22_async_section.py.
- PRODUCTION runs old code — user must REDEPLOY to get these fixes on gcu365-ai-vision.com.

## Completed (this fork, 2026-07-08c) — Bug fix: mispositioned detail-scan finding marker
- User-reported: marker #4 (black-valance scuffs from zoom detail pass) rendered on the pavement.
- Fix: _parse_detail_items drops degenerate/hallucinated boxes (full-coords w or h < 0.02 → box=None,
  finding listed without a misleading marker '·' in report); half-scan prompt now demands a TIGHT
  on-vehicle rectangle with self-verification, null if unsure.
- Verified by testing_agent (iteration_21.json): 10/10 pass, real E2E job with the exact bug images —
  zero degenerate boxes, all findings on-vehicle, reports render, benchmark/rental-events regressions clean.
- Reusable pytest: /app/backend/tests/test_iter21_box_validity.py.
- Follow-up (2026-07-08d): hosted report HTML + PDF now flag unlocalized findings — "!" in the # column
  and an amber "Not visually localized — physically verify: <locations>" note under the section table
  (ext_report_service.render_html/render_pdf). Self-tested with synthetic report doc + screenshot.

## Completed (this fork, 2026-07-08b) — Accuracy validation harness (regression suite)
- benchmark_service.py + routes /benchmark/*: ground-truth cases (before/after pair + expected
  findings with category/keywords/optional flag, images persisted in storage), background runs that
  replay every case through the real analyze_section pipeline, greedy one-to-one matching, per-case
  and overall recall scoring, run history in di_benchmark_runs.
- UI: "Accuracy benchmark" section on AI Usage page — case CRUD, run (fast/thorough), live polling,
  recall badges, per-expected chips (found/missed/optional), run history line.
- Seeded the user's 2 reported photo pairs as permanent cases. First run: 83% required recall (5/6);
  subtle optional detections (black-trim scuffs, replaced right lamp) are ~50% stable run-to-run —
  the harness now quantifies this. NOTE: production DB is separate; cases must be re-added there via UI.

## Completed (this fork, 2026-07-08) — Detection accuracy upgrade (user-reported misses)
User reported 3 missed subtle issues (different right-lamp internals/orange indicator, mismatched
bumper look, faint scratches on black bumper trim). Root causes: satisfaction-of-search bias,
component mismatch never requested, low-contrast blind spots, and cross-image comparison weakness.
Fixes in trip_inspection_service.py:
- Exterior prompt: 4-step comparison protocol (part-by-part, differs-from-before = reportable PART/
  LIGHT item, low-contrast rescan, never stop after obvious damage); LIGHT/PART categories now cover
  replaced/mismatched components; synonyms REPLACED/MISMATCH→PART.
- Mandatory componentCheck JSON (10 components, damaged/differs/note/box; lamp boxes always) —
  server merge (_items_from_component_check) synthesizes items for flagged-but-unreported components.
- Zoom detail pass (_detail_scan, DI_TRIP_DETAIL_SCAN=true, model DI_TRIP_DETAIL_MODEL=pro default):
  2 zoomed half-pair calls (catch faint dark-trim scratches) + per-lamp tight-crop calls with the
  AFTER image SCALE-ALIGNED to BEFORE (key discovery: alignment → 3/3 lamp-swap detection vs 0/3
  unaligned). Runs concurrently; merges deduped items (fromDetailScan flag), recounts section.
- E2E verified with user's own photos: all 5 issues now detected (glass, left lamp, red bumper
  scratches, black valance scuffs, right-lamp orange indicator = possible replaced lamp), rendered
  in hosted report with boxes. Cost: exterior section now ~5-7 AI calls (~30K tokens; detail pass on
  Pro). Tunable via env.

## Completed (prior fork phase, 2026-07-05) — CROMS integration completion
- Hosted report links: every External API job result + inspection.completed webhook now carries
  reportUrl (public rendered HTML report — annotated photos with numbered damage markers, findings
  table, verification warnings, print CSS) and reportPdfUrl (reportlab PDF). Public token-auth routes:
  GET /public/reports/{token} | /pdf | /images/{name}. Service: ext_report_service.py; report doc in
  di_ext_reports (token 40-hex is the credential). GCU365/SpeedAuto webhook mappings include the links.
- Inbound rental events: POST/GET /ext/v1/rental-events (X-API-Key) for rental.checked_out/checked_in →
  di_rental_events + di_open_rentals. Staff JWT endpoints GET /trip-inspection/open-rentals +
  POST .../{rentalId}/dismiss. Trip Inspection page shows "Rentals awaiting inspection" banner with
  Use (pre-fills report fields) / dismiss; finalize_trip auto-closes the open rental (status INSPECTED)
  when rentalId matches.
- Sandbox Playground in Developer Console: paste dik_ key, upload before/after pairs (6 slots), live
  job polling, open hosted report / download PDF / raw JSON; plus rental-events tester form.
- Integration Pack (downloadable MD) fully updated: Step 1.5 rental events, Step 3 Option C (zero-UI
  hosted report), Sections 3.4/3.5, playground note, updated payload samples with reportUrl.
- Help & Guide (bilingual EN/AR) updated to cover all shipped features: new topics Vehicles,
  AI Usage & Budget, API & Integrations (keys/connectors/pack/playground/hosted reports/rental events);
  Trip topic now covers OCR close-up, 10-point verification, open-rentals banner, vehicle history;
  Inspections covers privacy blur; Cases covers Najm claim export. Drawer auto-maps new routes.
- Tested: iteration_20.json — backend 17/17, frontend 100%. reportlab added to requirements.

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
- CROMS and Maintenance integration endpoints (connectors run in SANDBOX until live GCU365 credentials).

## Credentials
See /app/memory/test_credentials.md. Admin: admin@riyadah.tech / DamageAdmin#2026 / TENANT-000001.
