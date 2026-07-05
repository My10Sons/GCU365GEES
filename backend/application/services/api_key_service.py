"""
Repository Traceability:
- Purpose: Tenant-managed API keys for the public External API (/ext/v1). Keys are
  generated with `secrets`, shown ONCE, stored as SHA-256 hashes (irretrievable),
  with revocation + last-used tracking. Resolves X-API-Key to a tenant principal.
"""
from __future__ import annotations

import hashlib
import secrets
import string
from datetime import datetime, timezone

from bson import ObjectId

from api.middleware.safe_errors import DomainError
from domain.enums.error_codes import ErrorCode
from infrastructure.db.mongo import get_db

_ALPHABET = string.ascii_letters + string.digits
API_KEY_PERMISSIONS = ["di.ai.request", "di.inspections.read"]


def _rand(n: int) -> str:
    return "".join(secrets.choice(_ALPHABET) for _ in range(n))


def _hash(full_key: str) -> str:
    return hashlib.sha256(full_key.encode("utf-8")).hexdigest()


def _ser(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]), "label": doc.get("label"), "keyPrefix": doc.get("keyPrefix"),
        "createdAt": doc["createdAt"].isoformat() if doc.get("createdAt") else None,
        "revokedAt": doc["revokedAt"].isoformat() if doc.get("revokedAt") else None,
        "lastUsedAt": doc["lastUsedAt"].isoformat() if doc.get("lastUsedAt") else None,
        "usageCount": doc.get("usageCount", 0),
    }


async def create_key(*, principal: dict, label: str) -> dict:
    db = get_db()
    prefix = _rand(8)
    full_key = f"dik_{prefix}_{_rand(40)}"
    now = datetime.now(timezone.utc)
    doc = {
        "tenantId": principal["tenantId"], "label": (label or "API key")[:60],
        "keyPrefix": f"dik_{prefix}", "keyHash": _hash(full_key),
        "createdAt": now, "createdBy": principal["id"],
        "revokedAt": None, "lastUsedAt": None, "usageCount": 0,
    }
    res = await db.di_api_keys.insert_one(doc)
    doc["_id"] = res.inserted_id
    return {**_ser(doc), "apiKey": full_key}  # full key returned ONCE


async def list_keys(*, principal: dict) -> dict:
    db = get_db()
    rows = await db.di_api_keys.find({"tenantId": principal["tenantId"]}).sort(
        "createdAt", -1).to_list(length=100)
    return {"keys": [_ser(r) for r in rows]}


async def revoke_key(*, principal: dict, key_id: str) -> dict:
    db = get_db()
    try:
        oid = ObjectId(key_id)
    except Exception:
        raise DomainError(ErrorCode.VALIDATION_ERROR, "Invalid key id.", 400, "keyId")
    res = await db.di_api_keys.update_one(
        {"_id": oid, "tenantId": principal["tenantId"], "revokedAt": None},
        {"$set": {"revokedAt": datetime.now(timezone.utc)}},
    )
    if res.matched_count == 0:
        raise DomainError(ErrorCode.NOT_FOUND, "API key not found or already revoked.", 404)
    return {"id": key_id, "revoked": True}


async def resolve_api_key(api_key: str) -> dict:
    """X-API-Key → tenant principal with a fixed machine permission set."""
    if not api_key or not api_key.startswith("dik_") or api_key.count("_") < 2:
        raise DomainError(ErrorCode.UNAUTHORIZED, "Invalid API key.", 401, "X-API-Key")
    db = get_db()
    doc = await db.di_api_keys.find_one({"keyHash": _hash(api_key), "revokedAt": None})
    if not doc:
        raise DomainError(ErrorCode.UNAUTHORIZED, "Invalid or revoked API key.", 401, "X-API-Key")
    await db.di_api_keys.update_one(
        {"_id": doc["_id"]},
        {"$set": {"lastUsedAt": datetime.now(timezone.utc)}, "$inc": {"usageCount": 1}},
    )
    return {
        "id": f"apikey:{doc['_id']}", "email": None, "tenantId": doc["tenantId"],
        "roles": ["API_CLIENT"], "permissions": API_KEY_PERMISSIONS,
        "displayName": f"API key · {doc.get('label')}",
    }
