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
- Current estimator is a deterministic rule-based QAR table in
  `backend/application/services/trip_inspection_service.py` (`_COST_BASE`, `_SEVERITY_FACTOR`).

## Other deferred (P2 ops/governance)
- Production object-store swap, external alerting/dashboards, runbooks, DR, rollback sign-offs.
