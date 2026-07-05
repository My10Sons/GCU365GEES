"""
Repository Traceability:
- Purpose: Generates downloadable Markdown "integration packs" per connector type.
  Given to the counterpart developer (e.g. GCU365 CROMS) so they know exactly:
  WHAT WE PROVIDE (API key, signing secret, endpoints, payload schemas, samples)
  and WHAT WE NEED FROM THEM (base URL, credentials, endpoint ack, contacts).
  Secrets are never embedded — only placeholders + where to obtain them.
"""
from __future__ import annotations

from datetime import datetime, timezone

from api.middleware.safe_errors import DomainError
from domain.enums.error_codes import ErrorCode
from infrastructure.db.mongo import get_db

_NAMES = {"GENERIC": "Generic Rental System",
          "SPEED_AUTO": "Speed Auto Systems (CRS/VLS)",
          "GCU365_CROMS": "GCU365 CROMS"}
_EVENT_PATHS = {"GENERIC": "/webhooks/damage-intelligence",
                "SPEED_AUTO": "/api/v1/damage-events",
                "GCU365_CROMS": "/croms/api/v1/damage-events"}
_REPORT_FIELD = {"GENERIC": "data.data.report",
                 "SPEED_AUTO": "data.FindingsReport",
                 "GCU365_CROMS": "data.findingsReport"}

_OUTBOUND_SAMPLES = {
    "GENERIC": """{
  "id": "<uuid — use for de-duplication>",
  "type": "inspection.completed",
  "timestamp": 1751600000,
  "tenantId": "TENANT-000001",
  "data": {
    "type": "inspection.completed",
    "data": {
      "overall": "NEW_DAMAGE_FOUND",
      "newIssueCount": 2,
      "costSummary": { "low": 800, "high": 1300, "currency": "SAR" },
      "plate": "ABC 1234", "vin": "JTDBE32K123456789",
      "vehicleId": "<registry id>", "rentalId": "RA-1001",
      "damageCaseId": "<id or null>",
      "risk": { "level": "HIGH", "label": "Repeat offender", "damagedTrips": 3, "window": 5 },
      "report": { "…": "detailed findings report — full schema in Section 6" }
    }
  }
}""",
    "SPEED_AUTO": """{
  "id": "<uuid>", "type": "inspection.completed", "timestamp": 1751600000,
  "tenantId": "TENANT-000001",
  "data": {
    "EventType": "INSPECTION_COMPLETED",
    "PlateNo": "ABC 1234", "VIN": "JTDBE32K123456789",
    "RentalAgreementNo": "RA-1001",
    "DamageFound": true, "NewDamageCount": 2,
    "EstimatedCostLow": 800, "EstimatedCostHigh": 1300, "Currency": "SAR",
    "DamageCaseRef": "<id or null>",
    "FindingsReport": { "…": "detailed findings report — full schema in Section 6" },
    "SourceSystem": "DamageIntelligence"
  }
}""",
    "GCU365_CROMS": """{
  "id": "<uuid>", "type": "inspection.completed", "timestamp": 1751600000,
  "tenantId": "TENANT-000001",
  "data": {
    "eventType": "inspection.completed",
    "rentalAgreementId": "RA-1001",
    "vehiclePlate": "ABC 1234", "vin": "JTDBE32K123456789",
    "customerName": "…", "inspectorName": "…",
    "overallResult": "NEW_DAMAGE_FOUND", "newIssueCount": 2,
    "advisoryEstimate": { "low": 800, "high": 1300, "currency": "SAR" },
    "damageCaseId": "<id or null>",
    "vehicleRisk": { "level": "HIGH", "label": "Repeat offender",
                     "damagedTrips": 3, "window": 5, "streak": 3,
                     "newIssues": 6, "estCostHigh": 3900, "currency": "SAR" },
    "findingsReport": { "…": "detailed report — full schema in Section 6" },
    "requestedBySystem": "DamageIntelligence"
  }
}""",
}

_REPORT_SCHEMA = """### `findingsReport` object (the detailed report)

| Field | Type | Description |
|---|---|---|
| `analyzedAt` | ISO-8601 string | When the analysis was finalized (UTC) |
| `mode` | `"fast"` \\| `"thorough"` | AI tier used |
| `modelVersion` | string | e.g. `gemini:gemini-3.5-flash` |
| `conditionScore` | 0–100 or null | Overall vehicle condition after the trip |
| `cleanliness` | object or null | `{ "score": 0-100, "label": … }` |
| `coverage` | object | Which angles were captured, walkaround completeness |
| `sections[]` | array | One entry per analyzed view (max 8) — see below |
| `verification` | object | Photo/fraud checks — see below |

### `sections[]` entry
| Field | Type | Values / notes |
|---|---|---|
| `label` | string | e.g. `"Exterior — Front"`, `"Interior"` |
| `kind` | enum | `EXTERIOR` \\| `INTERIOR` |
| `angle` | enum or null | `FRONT` \\| `REAR` \\| `LEFT` \\| `RIGHT` \\| `ROOF` (null for interior) |
| `newIssueCount` | int | New issues found in this view |
| `summary` | string | Human-readable summary (≤300 chars) |
| `conditionScore` | 0–100 or null | Per-view condition |
| `cleanliness` | object or null | Per-view cleanliness |
| `items[]` | array (≤40) | Individual findings — see below |

### `items[]` (individual finding)
| Field | Type | Values |
|---|---|---|
| `category` | enum | Exterior: `DENT` `SCRATCH` `CHIP` `TIRE` `WHEEL` `GLASS` `LIGHT` `PART` `RUST` `VANDALISM` `DIRT` `LEAK` · Interior: `SEAT` `DASHBOARD` `TRIM` `STAIN` `MISSING` `ELECTRONICS` |
| `status` | enum | `NEW` (occurred during this rental) \\| `PRE_EXISTING` \\| `RESOLVED` \\| `UNCERTAIN` |
| `severity` | enum or null | `LOW` \\| `MEDIUM` \\| `HIGH` |
| `location` | string | e.g. `"front bumper, left corner"` |
| `sizeCm` | number or null | Approximate size |
| `recommendation` | enum or null | `REPAIR` \\| `REPLACE` \\| `ASSESS` |
| `estimatedCost` | object or null | `{ "low": int, "high": int, "currency": "SAR" }` — advisory |
| `confidence` | 0–1 | AI confidence |

**Billing rule of thumb:** only `status = "NEW"` items are chargeable to the rental;
`advisoryEstimate` at the top level sums the NEW items across all sections.

### `verification` object (anti-fraud / capture quality)
| Field | Type | Meaning |
|---|---|---|
| `hasPhotoWarnings` | bool | Blur / wrong angle / cropped framing / distance issues |
| `hasIntegrityWarnings` | bool | Possible AI-generated, edited, or photo-of-a-screen images |
| `hasEnvironmentWarnings` | bool | Dirt / rain / glare reduced analysis confidence |
| `hasMetadataWarnings` | bool | Missing / stale / edited EXIF, wrong before-after chronology |
| `vehicleConsistency` | object | `{ consistent, colors[], bodyTypes[], platesRead[], enteredPlate, plateMatch, warnings[] }` — cross-angle same-vehicle check |

Treat any `true` warning flag as "review the photos manually before charging the customer".
"""


async def build_pack(*, principal: dict, ctype: str, public_base: str) -> tuple[str, str]:
    if ctype not in _NAMES:
        raise DomainError(ErrorCode.VALIDATION_ERROR, "Unknown connector type.", 400, "type")
    c = await get_db().di_connectors.find_one(
        {"tenantId": principal["tenantId"], "type": ctype}) or {}
    mode = c.get("mode", "sandbox")
    api_base = f"{public_base}/api/v1/damage-intelligence/ext/v1"
    event_path = _EVENT_PATHS[ctype]
    name = _NAMES[ctype]
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    sig_block = ""
    if ctype == "GENERIC":
        sig_block = f"""
### Webhook signature verification (required)
Every outbound POST carries headers `X-DI-Event`, `X-DI-Id`, `X-DI-Timestamp`, `X-DI-Signature`.
Verify with the shared **signing secret** (provided separately by the tenant administrator):

```python
import base64, hashlib, hmac, time

def verify(secret: str, headers: dict, raw_body: str, tolerance: int = 300) -> bool:
    ts = int(headers["X-DI-Timestamp"])
    if abs(time.time() - ts) > tolerance:
        return False
    mac = hmac.new(secret.encode(),
                   f'{{headers["X-DI-Id"]}}.{{ts}}.{{raw_body}}'.encode(),
                   hashlib.sha256).digest()
    expected = "v1," + base64.b64encode(mac).decode()
    return hmac.compare_digest(expected, headers["X-DI-Signature"])
```
"""
    else:
        sig_block = """
### Authentication of our outbound calls
We attach the API key **you provide to us** in the `X-API-Key` header on every event POST.
"""

    md = f"""# Damage Intelligence ↔ {name} — Integration Pack
Generated {generated} · Tenant `{principal["tenantId"]}` · Connector mode: **{mode.upper()}**
{"> ⚠ **SANDBOX**: outbound events are currently simulated and logged in the Damage Intelligence console. Switch the connector to LIVE once credentials are exchanged." if mode == "sandbox" else ""}

---

## 1 · Checklist — what each side provides

### We (Damage Intelligence) provide to you
| Item | How you receive it |
|---|---|
| External API key (`dik_…`) | Created by the tenant admin in **API & Integrations → External API keys** and shared securely (shown once) |
| {"Webhook signing secret (`whsec_…`)" if ctype == "GENERIC" else "Event payload schema (this document)"} | {"Generated on connector save; shared securely by the tenant admin" if ctype == "GENERIC" else "Section 4 below"} |
| External API base URL | `{api_base}` |
| This integration pack + sample payloads | Downloadable from **API & Integrations** |

### You ({name}) provide to us
| Item | Why |
|---|---|
| HTTPS base URL of your environment | We POST events to `{{baseUrl}}{event_path}` |
| API key / credentials for that endpoint | Sent as `X-API-Key` on our outbound calls |
| Confirmation your endpoint replies `2xx` to acknowledge | Non-2xx / timeout triggers retries (0s / 5s / 25s) |
| Technical contact (name + email) | Incident & go-live coordination |
| Optional: IP allowlist requirements | If your gateway restricts callers |

Enter your base URL + API key in **API & Integrations → {name} → Save**, then press **Send test event** — a `connection.test` event is delivered (or simulated in sandbox) and logged.

---

## 2 · Step-by-step: what your team needs to develop

The whole flow is driven by YOUR system: you send the photos → we analyze → we send the
detailed report back. Four things to build:

### Step 0 — Prerequisites (no code)
Receive from the tenant administrator: the External API key (`dik_…`) and this document.
All calls are HTTPS. Keep the key server-side only — never embed it in a mobile/web client.

### Step 1 — Capture & store photos against the rental agreement
| Requirement | Value |
|---|---|
| Formats | JPEG / PNG / WebP |
| Max size | 12 MB per photo (≤1600 px longest side recommended — faster & cheaper) |
| At CHECK-OUT (rental start) | One photo per angle — `front`, `rear`, `left`, `right` (+ `roof`, `interior` optional). Store them in {name} against the rental agreement. |
| At CHECK-IN (return) | The same angles again, fresh. |

Each angle's before/after pair must show the same view of the same vehicle — our AI
verifies this and flags mismatches, wrong angles, screens/prints, and edited photos.

### Step 2 — Submit the analysis request (at check-in)
One multipart POST combining the stored check-out photos (`before_*`) with the fresh
check-in photos (`after_*`):

```bash
curl -X POST "{api_base}/trip-inspections" \\
  -H "X-API-Key: dik_..." \\
  -F "mode=fast" \\
  -F 'report_fields={{"vehiclePlate":"ABC 1234","rentalId":"RA-1001","customerName":"…"}}' \\
  -F "before_front=@out_front.jpg"  -F "after_front=@in_front.jpg" \\
  -F "before_rear=@out_rear.jpg"    -F "after_rear=@in_rear.jpg" \\
  -F "before_left=@out_left.jpg"    -F "after_left=@in_left.jpg" \\
  -F "before_right=@out_right.jpg"  -F "after_right=@in_right.jpg" \\
  -F "before_interior=@out_int.jpg" -F "after_interior=@in_int.jpg"
```

C# / .NET:
```csharp
using var http = new HttpClient();
http.DefaultRequestHeaders.Add("X-API-Key", apiKey);
using var form = new MultipartFormDataContent();
form.Add(new StringContent("fast"), "mode");
form.Add(new StringContent(
    "{{\\"vehiclePlate\\":\\"ABC 1234\\",\\"rentalId\\":\\"RA-1001\\"}}"), "report_fields");
void AddPhoto(byte[] bytes, string slot) {{
    var c = new ByteArrayContent(bytes);
    c.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue("image/jpeg");
    form.Add(c, slot, slot + ".jpg");
}}
AddPhoto(checkOutFrontBytes, "before_front");
AddPhoto(checkInFrontBytes,  "after_front");
// … repeat per captured angle …
var resp = await http.PostAsync("{api_base}/trip-inspections", form);
// → {{ "data": {{ "jobId": "…", "status": "RUNNING" }} }}
```

The response is immediate (`jobId`). Analysis takes ~30–90 s depending on angles and mode
(`fast` recommended; `thorough` for disputes).

### Step 3 — Receive the report (build one or both)
**Option A — Webhook receiver (recommended).** Implement
`POST {{yourBaseUrl}}{event_path}` in {name}:
- Reply `2xx` within 10 s (queue the payload, process asynchronously).
- Non-2xx / timeout → we retry at +5 s and +25 s. De-duplicate on the top-level `id`.
- Payload format: Sections 4–6 of this document.

**Option B — Polling.** `GET {api_base}/trip-inspections/{{jobId}}` every 10 s until
`status` is `DONE` or `FAILED` (give up after 5 min and alert your agent).

### Step 4 — Process the findings report in {name}
1. Read `overallResult`:
   - `NO_NEW_DAMAGE` → close the return; nothing to charge.
   - `NEW_DAMAGE_FOUND` → iterate `findingsReport.sections[].items[]` where
     `status == "NEW"`; show each to your return agent (location, severity, size,
     recommendation, cost range). Use top-level `advisoryEstimate` as the charge basis —
     it is advisory; your agent confirms the final amount.
   - `NOT_COMPARABLE` → photos unusable; prompt the agent to recapture and resubmit.
2. If ANY `verification` flag is `true` → route to manual review before charging
   (possible photo-quality issue or fraud signal).
3. If `damageCaseId` is set → a damage case was auto-opened on our side; store the
   reference on the rental agreement.
4. Optional: use `vehicleRisk` (repeat-offender flag) to adjust the deposit on the
   vehicle's NEXT rental.

### Step 5 — Handle errors
| HTTP | Meaning | Your action |
|---|---|---|
| 401 | invalid / revoked API key | fix configuration, alert ops |
| 400 | incomplete pair or bad field (`errors[].field` says which) | fix the request |
| 413 / 415 | photo too large / unsupported type | re-encode ≤12 MB JPEG |
| 5xx | temporary | retry with backoff |

Job `status = FAILED` returns a human-readable `error` — surface it to the agent and
allow resubmission.

### Step 6 — Sandbox acceptance checklist
- [ ] Submit a job with at least one real before/after pair → `status: DONE`
- [ ] `inspection.completed` received (or payload viewed in our console's delivery log)
- [ ] NEW items + cost ranges rendered correctly in the {name} return screen
- [ ] Webhook `2xx` ack + de-duplication verified (we can resend `connection.test` anytime)
- [ ] `NOT_COMPARABLE` and `FAILED` paths handled

Then follow the go-live steps at the end of this document.

---

## 3 · Calling our External API (inbound — you → us)

Auth: header `X-API-Key: dik_…` on every request. Responses use the envelope
`{{ "success": bool, "data": …, "errors": [...] }}`.

### 3.1 Submit a trip inspection (asynchronous)
```bash
curl -X POST "{api_base}/trip-inspections" \\
  -H "X-API-Key: dik_..." \\
  -F "mode=fast" \\
  -F 'report_fields={{"vehiclePlate":"ABC 1234","rentalId":"RA-1001","customerName":"…"}}' \\
  -F "before_front=@before.jpg" -F "after_front=@after.jpg"
# → {{ "jobId": "…", "status": "RUNNING", "poll": "…" }}
```
Photo slots: `before_front/after_front`, `_rear`, `_left`, `_right`, `_roof`, `_interior`
(≥ 1 complete pair). `mode`: `fast` | `thorough`. `save_to_vehicle_history` (default `true`).

### 3.2 Poll the job
```bash
curl "{api_base}/trip-inspections/{{jobId}}" -H "X-API-Key: dik_..."
```
`status`: `RUNNING → DONE | FAILED`. `result` contains sections (per-angle findings,
bounding boxes, severities, cost estimates), photo/integrity/metadata verification,
`vehicleConsistency`, `vehicleLink` (registry id + fleet-risk profile), `autoCase`.

### 3.3 Vehicle damage history by plate
```bash
curl "{api_base}/vehicles/ABC1234/history" -H "X-API-Key: dik_..."
```

---

## 4 · Receiving our events (outbound — us → you)

We POST JSON to `{{yourBaseUrl}}{event_path}` for events:

| Event | When |
|---|---|
| `inspection.completed` | Every finalized trip inspection |
| `damage_case.created` | Auto-created damage case (cost threshold breach) |
| `connection.test` | Manual test from our console |

Delivery: retried up to 3 attempts (0s / 5s / 25s). De-duplicate on the `id` field.
{sig_block}

---

## 5 · Event payload sample (`inspection.completed`)

```json
{_OUTBOUND_SAMPLES[ctype]}
```

---

## 6 · Detailed findings report — what you receive and in what format

Every `inspection.completed` event carries the **full findings report** at
**`{_REPORT_FIELD[ctype]}`** (JSON, UTF-8).

{_REPORT_SCHEMA}

#### Populated example (one exterior section, abridged)
```json
{{
  "analyzedAt": "2026-07-05T10:41:00+00:00",
  "mode": "fast",
  "modelVersion": "gemini:gemini-3.5-flash",
  "conditionScore": 74,
  "cleanliness": {{ "score": 80, "label": "Clean" }},
  "coverage": {{ "anglesCaptured": ["FRONT"], "fullWalkaround": false }},
  "sections": [
    {{
      "label": "Exterior — Front", "kind": "EXTERIOR", "angle": "FRONT",
      "newIssueCount": 2,
      "summary": "Two new issues: a dent on the front bumper and a scratched headlight.",
      "conditionScore": 70,
      "items": [
        {{
          "category": "DENT", "status": "NEW", "severity": "MEDIUM",
          "location": "front bumper, left corner", "sizeCm": 8,
          "recommendation": "REPAIR",
          "estimatedCost": {{ "low": 500, "high": 800, "currency": "SAR" }},
          "confidence": 0.86
        }},
        {{
          "category": "LIGHT", "status": "NEW", "severity": "LOW",
          "location": "left headlight lens", "sizeCm": 3,
          "recommendation": "ASSESS",
          "estimatedCost": {{ "low": 300, "high": 500, "currency": "SAR" }},
          "confidence": 0.78
        }}
      ]
    }}
  ],
  "verification": {{
    "hasPhotoWarnings": false, "hasIntegrityWarnings": false,
    "hasEnvironmentWarnings": false, "hasMetadataWarnings": false,
    "vehicleConsistency": {{ "consistent": true, "plateMatch": true,
                            "platesRead": ["ABC1234"], "warnings": [] }}
  }}
}}
```

---

## 7 · Go-live steps
1. Exchange credentials per Section 1 (both directions, via a secure channel).
2. We set the connector to **Sandbox**, you call our External API against real photos.
3. You confirm receipt/handling of `connection.test` + `inspection.completed` payload shape.
4. Tenant admin flips the connector to **Live** (requires your https base URL) — done.

*Advisory notice: analysis results are AI-assisted advisory estimates. Damage Intelligence — generated automatically; do not edit by hand.*
"""
    fname = f"damage-intelligence-integration-{ctype.lower()}.md"
    return fname, md
