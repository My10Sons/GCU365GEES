"""
Repository Traceability:
- Purpose: Outbound Rental-System Connectors. Three types per tenant:
  * GENERIC       — documented REST + webhook contract (HMAC-SHA256 signed, any KSA system)
  * SPEED_AUTO    — Speed Auto Systems (CRS/VLS) adapter          [SANDBOX until credentials]
  * GCU365_CROMS  — GCU365 CROMS adapter                          [SANDBOX until credentials]
  Sandbox mode simulates the remote call and records the exact payload that WOULD be sent.
  All deliveries (live + sandbox) are logged to di_connector_deliveries with retry support.
"""
from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
import json
import secrets
import uuid
from datetime import datetime, timezone
from typing import Optional

import httpx

from api.middleware.safe_errors import DomainError
from domain.enums.error_codes import ErrorCode
from infrastructure.db.mongo import get_db

CONNECTOR_TYPES = ("GENERIC", "SPEED_AUTO", "GCU365_CROMS")
_RETRY_DELAYS = (0, 5, 25)

_EVENT_PATHS = {
    "SPEED_AUTO": "/api/v1/damage-events",
    "GCU365_CROMS": "/croms/api/v1/damage-events",
}


def sign_payload(secret: str, message_id: str, timestamp: int, raw_body: str) -> str:
    digest = hmac.new(secret.encode("utf-8"),
                      f"{message_id}.{timestamp}.{raw_body}".encode("utf-8"),
                      hashlib.sha256).digest()
    return "v1," + base64.b64encode(digest).decode("utf-8")


def _map_payload(ctype: str, event_type: str, data: dict) -> dict:
    """Adapt the canonical event to each rental system's expected field naming."""
    if ctype == "SPEED_AUTO":
        return {
            "EventType": event_type.upper().replace(".", "_"),
            "PlateNo": data.get("plate"), "VIN": data.get("vin"),
            "RentalAgreementNo": data.get("rentalId"),
            "DamageFound": data.get("overall") == "NEW_DAMAGE_FOUND",
            "NewDamageCount": data.get("newIssueCount"),
            "EstimatedCostLow": (data.get("costSummary") or {}).get("low"),
            "EstimatedCostHigh": (data.get("costSummary") or {}).get("high"),
            "Currency": (data.get("costSummary") or {}).get("currency"),
            "DamageCaseRef": data.get("damageCaseId"),
            "SourceSystem": "DamageIntelligence",
        }
    if ctype == "GCU365_CROMS":
        return {
            "eventType": event_type, "rentalAgreementId": data.get("rentalId"),
            "vehiclePlate": data.get("plate"), "vin": data.get("vin"),
            "overallResult": data.get("overall"), "newIssueCount": data.get("newIssueCount"),
            "advisoryEstimate": data.get("costSummary"), "damageCaseId": data.get("damageCaseId"),
            "requestedBySystem": "DamageIntelligence",
        }
    return {"type": event_type, "data": data}


def _ser_connector(doc: dict) -> dict:
    return {
        "type": doc["type"], "enabled": bool(doc.get("enabled")),
        "mode": doc.get("mode", "sandbox"), "baseUrl": doc.get("baseUrl") or "",
        "hasApiKey": bool(doc.get("apiKey")), "hasSecret": bool(doc.get("secret")),
        "updatedAt": doc["updatedAt"].isoformat() if doc.get("updatedAt") else None,
    }


async def list_connectors(*, principal: dict) -> dict:
    db = get_db()
    rows = await db.di_connectors.find({"tenantId": principal["tenantId"]}).to_list(length=10)
    by_type = {r["type"]: r for r in rows}
    return {"connectors": [
        _ser_connector(by_type.get(t, {"type": t, "enabled": False, "mode": "sandbox"}))
        for t in CONNECTOR_TYPES
    ]}


async def upsert_connector(*, principal: dict, ctype: str, enabled: bool, mode: str,
                           base_url: str, api_key: Optional[str], secret: Optional[str]) -> dict:
    if ctype not in CONNECTOR_TYPES:
        raise DomainError(ErrorCode.VALIDATION_ERROR, "Unknown connector type.", 400, "type")
    if mode not in ("sandbox", "live"):
        raise DomainError(ErrorCode.VALIDATION_ERROR, "Mode must be sandbox or live.", 400, "mode")
    if mode == "live" and not (base_url or "").startswith("https://"):
        raise DomainError(ErrorCode.VALIDATION_ERROR,
                          "Live mode requires an https base URL.", 400, "baseUrl")
    db = get_db()
    sets = {"tenantId": principal["tenantId"], "type": ctype, "enabled": bool(enabled),
            "mode": mode, "baseUrl": (base_url or "").strip()[:300],
            "updatedAt": datetime.now(timezone.utc), "updatedBy": principal["id"]}
    if api_key:
        sets["apiKey"] = api_key.strip()[:200]
    if secret:
        sets["secret"] = secret.strip()[:200]
    if ctype == "GENERIC" and not secret:
        existing = await db.di_connectors.find_one({"tenantId": principal["tenantId"], "type": ctype})
        if not (existing or {}).get("secret"):
            sets["secret"] = "whsec_" + secrets.token_hex(24)  # auto-provision signing secret
    await db.di_connectors.update_one(
        {"tenantId": principal["tenantId"], "type": ctype}, {"$set": sets}, upsert=True)
    doc = await db.di_connectors.find_one({"tenantId": principal["tenantId"], "type": ctype})
    out = _ser_connector(doc)
    if ctype == "GENERIC" and sets.get("secret"):
        out["signingSecret"] = doc.get("secret")  # shown when (re)generated
    return out


async def _log_delivery(db, c: dict, event_type: str, body: dict, status: str,
                        http_status: Optional[int] = None, error: Optional[str] = None,
                        attempt: int = 1):
    await db.di_connector_deliveries.insert_one({
        "tenantId": c["tenantId"], "connectorType": c["type"], "mode": c.get("mode", "sandbox"),
        "event": event_type, "status": status, "httpStatus": http_status, "attempt": attempt,
        "error": (error or "")[:500] or None,
        "requestBody": json.dumps(body)[:4000],
        "targetUrl": (c.get("baseUrl") or "") + _EVENT_PATHS.get(c["type"], "/webhooks/damage-intelligence"),
        "createdAt": datetime.now(timezone.utc),
    })


async def _deliver(c: dict, event_type: str, data: dict):
    db = get_db()
    message_id = uuid.uuid4().hex
    ts = int(datetime.now(timezone.utc).timestamp())
    body = {"id": message_id, "type": event_type, "timestamp": ts,
            "tenantId": c["tenantId"], "data": _map_payload(c["type"], event_type, data)}
    if c.get("mode", "sandbox") == "sandbox":
        await _log_delivery(db, c, event_type, body, "SANDBOX_OK")
        return
    raw = json.dumps(body, separators=(",", ":"))
    headers = {"Content-Type": "application/json", "X-DI-Event": event_type,
               "X-DI-Id": message_id, "X-DI-Timestamp": str(ts)}
    if c["type"] == "GENERIC" and c.get("secret"):
        headers["X-DI-Signature"] = sign_payload(c["secret"], message_id, ts, raw)
    if c.get("apiKey"):
        headers["X-API-Key"] = c["apiKey"]
    url = (c.get("baseUrl") or "").rstrip("/") + _EVENT_PATHS.get(c["type"], "/webhooks/damage-intelligence")
    for attempt, delay in enumerate(_RETRY_DELAYS, start=1):
        if delay:
            await asyncio.sleep(delay)
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, content=raw, headers=headers)
            okish = 200 <= resp.status_code < 300
            await _log_delivery(db, c, event_type, body, "DELIVERED" if okish else "FAILED",
                                http_status=resp.status_code, attempt=attempt)
            if okish:
                return
        except Exception as exc:
            await _log_delivery(db, c, event_type, body, "ERROR", error=repr(exc), attempt=attempt)


async def dispatch_event(tenant_id: str, event_type: str, data: dict):
    """Fan an event out to every enabled connector (fire-and-forget per connector)."""
    try:
        db = get_db()
        connectors = await db.di_connectors.find(
            {"tenantId": tenant_id, "enabled": True}).to_list(length=10)
        for c in connectors:
            asyncio.create_task(_deliver(c, event_type, data))
    except Exception:
        pass  # eventing must never break the primary flow


async def test_connector(*, principal: dict, ctype: str) -> dict:
    db = get_db()
    c = await db.di_connectors.find_one({"tenantId": principal["tenantId"], "type": ctype})
    if not c:
        raise DomainError(ErrorCode.NOT_FOUND, "Connector not configured yet.", 404)
    await _deliver(c, "connection.test", {"plate": "TEST 0000", "overall": "NO_NEW_DAMAGE",
                                          "newIssueCount": 0,
                                          "costSummary": {"low": 0, "high": 0, "currency": "SAR"}})
    row = await db.di_connector_deliveries.find_one(
        {"tenantId": principal["tenantId"], "connectorType": ctype, "event": "connection.test"},
        sort=[("createdAt", -1)])
    return {"status": row.get("status") if row else "UNKNOWN",
            "httpStatus": row.get("httpStatus") if row else None,
            "sandbox": (c.get("mode", "sandbox") == "sandbox")}


async def list_deliveries(*, principal: dict, limit: int = 30) -> dict:
    db = get_db()
    rows = await db.di_connector_deliveries.find({"tenantId": principal["tenantId"]}).sort(
        "createdAt", -1).limit(max(1, min(limit, 100))).to_list(length=100)
    return {"deliveries": [{
        "id": str(r["_id"]), "connectorType": r["connectorType"], "mode": r.get("mode"),
        "event": r["event"], "status": r["status"], "httpStatus": r.get("httpStatus"),
        "attempt": r.get("attempt"), "targetUrl": r.get("targetUrl"), "error": r.get("error"),
        "createdAt": r["createdAt"].isoformat(),
    } for r in rows]}
