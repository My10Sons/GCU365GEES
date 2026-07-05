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
      "risk": { "level": "HIGH", "label": "Repeat offender", "damagedTrips": 3, "window": 5 }
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
    "DamageCaseRef": "<id or null>", "SourceSystem": "DamageIntelligence"
  }
}""",
    "GCU365_CROMS": """{
  "id": "<uuid>", "type": "inspection.completed", "timestamp": 1751600000,
  "tenantId": "TENANT-000001",
  "data": {
    "eventType": "inspection.completed",
    "rentalAgreementId": "RA-1001",
    "vehiclePlate": "ABC 1234", "vin": "JTDBE32K123456789",
    "overallResult": "NEW_DAMAGE_FOUND", "newIssueCount": 2,
    "advisoryEstimate": { "low": 800, "high": 1300, "currency": "SAR" },
    "damageCaseId": "<id or null>",
    "requestedBySystem": "DamageIntelligence"
  }
}""",
}


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

## 2 · Calling our External API (inbound — you → us)

Auth: header `X-API-Key: dik_…` on every request. Responses use the envelope
`{{ "success": bool, "data": …, "errors": [...] }}`.

### 2.1 Submit a trip inspection (asynchronous)
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

### 2.2 Poll the job
```bash
curl "{api_base}/trip-inspections/{{jobId}}" -H "X-API-Key: dik_..."
```
`status`: `RUNNING → DONE | FAILED`. `result` contains sections (per-angle findings,
bounding boxes, severities, cost estimates), photo/integrity/metadata verification,
`vehicleConsistency`, `vehicleLink` (registry id + fleet-risk profile), `autoCase`.

### 2.3 Vehicle damage history by plate
```bash
curl "{api_base}/vehicles/ABC1234/history" -H "X-API-Key: dik_..."
```

---

## 3 · Receiving our events (outbound — us → you)

We POST JSON to `{{yourBaseUrl}}{event_path}` for events:

| Event | When |
|---|---|
| `inspection.completed` | Every finalized trip inspection |
| `damage_case.created` | Auto-created damage case (cost threshold breach) |
| `connection.test` | Manual test from our console |

Delivery: retried up to 3 attempts (0s / 5s / 25s). De-duplicate on the `id` field.
{sig_block}

---

## 4 · Event payload sample (`inspection.completed`)

```json
{_OUTBOUND_SAMPLES[ctype]}
```

---

## 5 · Go-live steps
1. Exchange credentials per Section 1 (both directions, via a secure channel).
2. We set the connector to **Sandbox**, you call our External API against real photos.
3. You confirm receipt/handling of `connection.test` + `inspection.completed` payload shape.
4. Tenant admin flips the connector to **Live** (requires your https base URL) — done.

*Advisory notice: analysis results are AI-assisted advisory estimates. Damage Intelligence — generated automatically; do not edit by hand.*
"""
    fname = f"damage-intelligence-integration-{ctype.lower()}.md"
    return fname, md
