"""
Repository Traceability:
- Purpose: Per-tenant Trip Inspection policy. Currently: `requireFullWalkaround` — when set by an
  admin (or the CROMS / Maintenance system), staff at that tenant must capture all 5 exterior
  angles before analysis (the walkaround gate is pre-enabled and locked in the UI). Scoped by
  tenantId, stored in `di_tenant_policy`.
"""
from __future__ import annotations

from datetime import datetime, timezone

from infrastructure.db.mongo import get_db

_DEFAULT = {"requireFullWalkaround": False}


async def get_policy(tenant_id: str) -> dict:
    db = get_db()
    doc = await db.di_tenant_policy.find_one({"tenantId": tenant_id})
    if not doc:
        return dict(_DEFAULT)
    return {"requireFullWalkaround": bool(doc.get("requireFullWalkaround", False))}


async def set_policy(*, tenant_id: str, require_full_walkaround: bool) -> dict:
    db = get_db()
    now = datetime.now(timezone.utc)
    await db.di_tenant_policy.update_one(
        {"tenantId": tenant_id},
        {"$set": {"tenantId": tenant_id, "requireFullWalkaround": bool(require_full_walkaround), "updatedAt": now},
         "$setOnInsert": {"createdAt": now}},
        upsert=True,
    )
    return await get_policy(tenant_id)
