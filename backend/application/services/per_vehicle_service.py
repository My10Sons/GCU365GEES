"""
Repository Traceability:
- Source Documents: DI-0037 (Per-Vehicle Evidence Strip), DI-0011, DI-0012, DI-0014, DI-0034.
- Purpose: Advisory per-vehicle evidence strip — surfaces the last N images for the SAME
  externalVehicleRef within the principal's tenant, excluding the current session.
  Never crosses tenant boundaries; never exposes raw objectPath or unrestricted URLs.
"""
from __future__ import annotations

from application.services.audit_service import write_audit
from application.services.inspection_service import _load_session_for_tenant
from domain.enums.audit_actions import ActorType, AuditAction, ObjectType
from infrastructure.db.mongo import get_db


async def per_vehicle_strip(*, principal: dict, session_id: str, limit: int, correlation_id: str) -> dict:
    db = get_db()
    tenant_id = principal["tenantId"]
    limit = max(1, min(50, limit))
    current = await _load_session_for_tenant(tenant_id=tenant_id, session_id=session_id)
    vehicle_ref = (current.get("references") or {}).get("externalVehicleRef")
    if not vehicle_ref:
        return {"items": [], "total": 0, "isAdvisory": True}

    # Prior sessions for the same vehicle in this tenant (exclude current).
    prior_sessions = {}
    async for s in db.di_inspection_sessions.find(
        {"tenantId": tenant_id, "references.externalVehicleRef": vehicle_ref,
         "_id": {"$ne": current["_id"]}}
    ):
        prior_sessions[str(s["_id"])] = s
    if not prior_sessions:
        return {"items": [], "total": 0, "isAdvisory": True}

    items = []
    cursor = db.di_inspection_images.find(
        {"tenantId": tenant_id, "inspectionSessionId": {"$in": list(prior_sessions.keys())}}
    ).sort("createdAt", -1).limit(limit)
    async for img in cursor:
        ev = await db.di_evidence_references.find_one(
            {"tenantId": tenant_id, "inspectionImageId": str(img["_id"])}
        )
        sess = prior_sessions.get(img["inspectionSessionId"], {})
        items.append({
            "inspectionSessionId": img["inspectionSessionId"],
            "inspectionType": sess.get("inspectionType"),
            "capturePosition": img.get("capturePosition"),
            "inspectionImageId": str(img["_id"]),
            "evidenceId": str(ev["_id"]) if ev else None,
            "capturedAt": img["createdAt"].isoformat() if img.get("createdAt") else None,
        })

    await write_audit(
        tenant_id=tenant_id, actor_id=principal["id"], actor_type=ActorType.USER,
        action=AuditAction.PER_VEHICLE_STRIP_VIEWED, object_type=ObjectType.INSPECTION_SESSION,
        object_id=str(current["_id"]), correlation_id=correlation_id,
        safe_metadata={"vehicleRef": vehicle_ref, "returned": len(items)},
    )
    return {"items": items, "total": len(items), "isAdvisory": True}
