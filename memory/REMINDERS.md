# Pending reminders (surface these to the user)

## Trip Inspection — repair cost estimates
- **Cost table tenant-config: ON HOLD** (user said "hold off for now" on 2026-06-29).
  When revisited: per-tenant `currency` + per-category low/high rates stored like branding,
  `GET/PUT /tenant/cost-config` (admin/CROMS), optional in-app "Cost settings" admin screen.
- **Live pricing API option — VehicleDatabases.com Repair Pricing API** (researched 2026-06-29):
  - Cost: 15 free credits on signup; free tier $0/mo (10 req/mo); ~$14.99/mo for 300–1,200
    req/mo; $99.90/mo for 5,000; $199.99/mo for ~11,400. Cheap to pilot.
  - Caveats: (1) US-market pricing in USD — needs FX + local adjustment for Qatar/KSA;
    (2) needs VIN or Year/Make/Model input (pairs with the deferred plate/VIN OCR feature).
  - ACTION when user is ready: route via integration flow; user must supply an API key.
  - **US -> GCC localisation factors** (researched 2026-06-29, for converting US-based API
    estimates to local prices; broad averages, vary by brand/model):
    - OEM parts: KSA ~10-20% cheaper than US -> apply **~0.85x** to parts (KSA), similar for QAR.
    - Labour: US is ~2-2.5x more expensive -> apply **~0.45-0.50x** to labour (KSA/GCC).
    - Blended: a $1,000 US job ~= $600-700 in KSA (GCC totals ~30-40% lower overall).
    - Then convert currency USD -> SAR (~3.75) / QAR (~3.64).
    - Note: local dealer rates remain most accurate; treat these as fallback multipliers.
- Current estimator is a deterministic rule-based QAR table in
  `backend/application/services/trip_inspection_service.py` (`_COST_BASE`, `_SEVERITY_FACTOR`).

## Other deferred (P2 ops/governance)
- Production object-store swap, external alerting/dashboards, runbooks, DR, rollback sign-offs.
