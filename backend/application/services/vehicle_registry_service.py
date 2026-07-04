"""
Repository Traceability:
- Purpose: Per-tenant vehicle registry + trip-history linking for the Trip Inspection flow.
  Vehicles are identified by VIN (stronger identifier — wins conflicts) or normalized plate.
  Linked trips store a compact snapshot that powers the damage-history timeline.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId

from api.middleware.safe_errors import DomainError
from application.services.audit_service import write_audit
from domain.enums.audit_actions import ActorType, AuditAction, ObjectType
from domain.enums.error_codes import ErrorCode
from infrastructure.db.mongo import get_db


def plate_norm(p) -> str:
    return "".join(ch for ch in str(p or "").upper() if ch.isalnum())


def vin_norm(v) -> str:
    return "".join(ch for ch in str(v or "").upper() if ch.isalnum())


def _iso(v):
    return v.isoformat() if isinstance(v, datetime) else v


def _ser(doc: dict) -> dict:
    out = {k: _iso(v) for k, v in doc.items() if k != "_id"}
    out["id"] = str(doc["_id"])
    return out


def _compact_sections(sections: list[dict]) -> list[dict]:
    out = []
    for s in sections[:8]:
        out.append({
            "label": s.get("label"), "kind": s.get("kind"), "angle": s.get("angle"),
            "newIssueCount": s.get("newIssueCount"), "summary": (s.get("summary") or "")[:300],
            "conditionScore": s.get("conditionScore"), "cleanliness": s.get("cleanliness"),
            "items": [
                {k: it.get(k) for k in ("category", "status", "severity", "location",
                                        "sizeCm", "recommendation", "estimatedCost", "confidence")}
                for it in (s.get("items") or [])[:40]
            ],
        })
    return out


_RISK_WINDOW = 5


def _risk_profile(trips: list[dict]) -> dict:
    """Derive a fleet-risk profile from the vehicle's most recent linked trips (desc order)."""
    recent = trips[:_RISK_WINDOW]
    damaged = [t for t in recent if t.get("overall") == "NEW_DAMAGE_FOUND"]
    streak = 0
    for t in recent:
        if t.get("overall") == "NEW_DAMAGE_FOUND":
            streak += 1
        else:
            break
    new_issues = sum(int(t.get("newIssueCount") or 0) for t in damaged)
    cost_high = sum(int((t.get("costSummary") or {}).get("high") or 0) for t in damaged)
    currency = next(((t.get("costSummary") or {}).get("currency") for t in damaged
                     if (t.get("costSummary") or {}).get("currency")), "SAR")
    n = len(damaged)
    if n >= 3 or streak >= 2:
        level, label = "HIGH", "Repeat offender"
    elif n == 2:
        level, label = "MEDIUM", "Watch list"
    elif n == 1:
        level, label = "LOW", "Normal"
    else:
        level, label = "NONE", "Clean"
    return {
        "level": level, "label": label,
        "damagedTrips": n, "window": len(recent), "streak": streak,
        "newIssues": new_issues, "estCostHigh": cost_high, "currency": currency,
    }


async def link_trip(*, principal: dict, result: dict, report_fields: Optional[dict],
                    ocr: Optional[dict], correlation_id: str) -> dict:
    rf = report_fields or {}
    ocr = ocr or {}
    vc = result.get("vehicleConsistency") or {}
    plate_display = (rf.get("vehiclePlate") or "").strip() or (str(ocr.get("plate") or "")).strip()
    if not plate_display and vc.get("platesRead"):
        plate_display = vc["platesRead"][0]
    plate = plate_norm(plate_display)
    vin = vin_norm(ocr.get("vin"))
    if not plate and not vin:
        return {"linked": False, "reason": "no_identifier"}

    db = get_db()
    tenant_id = principal["tenantId"]
    now = datetime.now(timezone.utc)
    warnings: list[str] = []

    vehicle = None
    if vin:
        vehicle = await db.di_vehicles.find_one({"tenantId": tenant_id, "vin": vin})
        if vehicle and plate and vehicle.get("plateNormalized") and vehicle["plateNormalized"] != plate:
            warnings.append(
                f"Plate changed for this VIN: previously {vehicle.get('plateDisplay')}, now "
                f"{plate_display}. VIN is treated as the stronger identifier — plate updated."
            )
        if vehicle is None and plate:
            same_plate = await db.di_vehicles.find_one({"tenantId": tenant_id, "plateNormalized": plate})
            if same_plate and vin_norm(same_plate.get("vin")) and vin_norm(same_plate.get("vin")) != vin:
                warnings.append(
                    f"Plate {plate_display} is already registered to a different VIN "
                    f"({same_plate.get('vin')}). A separate vehicle record was kept for this VIN."
                )
            elif same_plate and not vin_norm(same_plate.get("vin")):
                vehicle = same_plate  # same plate, no VIN on record yet → enrich it with the VIN
    elif plate:
        vehicle = await db.di_vehicles.find_one({"tenantId": tenant_id, "plateNormalized": plate})

    model = (rf.get("vehicleModel") or "").strip() or (str(ocr.get("model") or "")).strip()
    colors = vc.get("colors") or []
    bodies = vc.get("bodyTypes") or []
    set_fields: dict = {"tenantId": tenant_id, "lastSeenAt": now, "updatedAt": now}
    if plate:
        set_fields["plateNormalized"] = plate
        set_fields["plateDisplay"] = plate_display[:24]
    if vin:
        set_fields["vin"] = vin
    if model:
        set_fields["model"] = model[:80]
    if len(colors) == 1:
        set_fields["color"] = colors[0]
    if len(bodies) == 1:
        set_fields["bodyType"] = bodies[0]

    is_new = vehicle is None
    if is_new:
        res = await db.di_vehicles.insert_one({
            **set_fields, "firstSeenAt": now, "createdAt": now,
            "createdBy": principal["id"], "inspectionCount": 0,
        })
        vehicle_id = res.inserted_id
    else:
        vehicle_id = vehicle["_id"]
        await db.di_vehicles.update_one({"_id": vehicle_id}, {"$set": set_fields})
    await db.di_vehicles.update_one({"_id": vehicle_id}, {"$inc": {"inspectionCount": 1}})

    auto_case = result.get("autoCase") or {}
    trip_res = await db.di_vehicle_trips.insert_one({
        "tenantId": tenant_id, "vehicleId": str(vehicle_id),
        "plateDisplay": plate_display[:24] or None,
        "overall": result.get("overall"), "newIssueCount": result.get("newIssueCount"),
        "costSummary": result.get("costSummary"), "conditionScore": result.get("conditionScore"),
        "cleanliness": result.get("cleanliness"), "coverage": result.get("coverage"),
        "mode": result.get("mode"), "modelVersion": result.get("modelVersion"),
        "sections": _compact_sections(result.get("sections") or []),
        "reportFields": {k: (rf.get(k) or None) for k in
                         ("customerName", "vehicleModel", "rentalId", "inspectorName")},
        "damageCaseId": auto_case.get("damageCaseId"),
        "inspectionSessionId": auto_case.get("inspectionSessionId"),
        "createdAt": now, "createdBy": principal["id"], "correlationId": correlation_id,
    })

    await write_audit(
        tenant_id=tenant_id, actor_id=principal["id"], actor_type=ActorType.USER,
        action=AuditAction.VEHICLE_LINKED, object_type=ObjectType.VEHICLE,
        object_id=str(vehicle_id), correlation_id=correlation_id,
        safe_metadata={"isNewVehicle": is_new, "hasVin": bool(vin),
                       "overall": result.get("overall"), "warnings": len(warnings)},
    )
    recent = await db.di_vehicle_trips.find(
        {"tenantId": tenant_id, "vehicleId": str(vehicle_id)}
    ).sort("createdAt", -1).limit(_RISK_WINDOW).to_list(length=_RISK_WINDOW)
    return {
        "linked": True, "vehicleId": str(vehicle_id), "tripId": str(trip_res.inserted_id),
        "plate": plate_display[:24] or None, "vin": vin or None,
        "isNewVehicle": is_new, "warnings": warnings,
        "risk": _risk_profile(recent),
    }


async def risk_overview(*, principal: dict, top: int = 5) -> dict:
    """Fleet-level risk rollup for the dashboard: top riskiest vehicles + total exposure."""
    db = get_db()
    tenant_id = principal["tenantId"]
    vehicles = await db.di_vehicles.find({"tenantId": tenant_id}).to_list(length=1000)
    empty_totals = {"vehicles": 0, "highCount": 0, "mediumCount": 0, "totalExposure": 0, "currency": "SAR"}
    if not vehicles:
        return {"totals": empty_totals, "topVehicles": []}
    ids = [str(v["_id"]) for v in vehicles]
    trips = await db.di_vehicle_trips.find(
        {"tenantId": tenant_id, "vehicleId": {"$in": ids}},
        {"vehicleId": 1, "overall": 1, "newIssueCount": 1, "costSummary": 1, "createdAt": 1},
    ).sort("createdAt", -1).to_list(length=5000)
    by_vehicle: dict[str, list] = {}
    for t in trips:
        by_vehicle.setdefault(t["vehicleId"], []).append(t)
    rows = [(v, _risk_profile(by_vehicle.get(str(v["_id"]), []))) for v in vehicles]
    rank = {"HIGH": 3, "MEDIUM": 2, "LOW": 1, "NONE": 0}
    rows.sort(key=lambda x: (rank.get(x[1]["level"], 0), x[1]["estCostHigh"], x[1]["damagedTrips"]),
              reverse=True)
    currency = next((r["currency"] for _, r in rows if r["estCostHigh"]), "SAR")
    return {
        "totals": {
            "vehicles": len(vehicles),
            "highCount": sum(1 for _, r in rows if r["level"] == "HIGH"),
            "mediumCount": sum(1 for _, r in rows if r["level"] == "MEDIUM"),
            "totalExposure": sum(r["estCostHigh"] for _, r in rows),
            "currency": currency,
        },
        "topVehicles": [
            {"id": str(v["_id"]), "plateDisplay": v.get("plateDisplay"), "vin": v.get("vin"),
             "model": v.get("model"), "color": v.get("color"), "bodyType": v.get("bodyType"),
             "inspectionCount": v.get("inspectionCount", 0), "lastSeenAt": _iso(v.get("lastSeenAt")),
             "risk": r}
            for v, r in rows[:max(1, min(top, 20))] if r["window"] > 0
        ],
    }


async def list_vehicles(*, principal: dict, search: str = "", limit: int = 200) -> dict:
    db = get_db()
    q: dict = {"tenantId": principal["tenantId"]}
    s = (search or "").strip()
    if s:
        import re
        rx = {"$regex": re.escape(s), "$options": "i"}
        q["$or"] = [{"plateNormalized": {"$regex": re.escape(plate_norm(s)), "$options": "i"}},
                    {"plateDisplay": rx}, {"vin": rx}, {"model": rx}]
    rows = await db.di_vehicles.find(q).sort("lastSeenAt", -1).limit(max(1, min(limit, 500))).to_list(length=500)
    vehicles = [_ser(r) for r in rows]
    ids = [v["id"] for v in vehicles]
    if ids:
        trips = await db.di_vehicle_trips.find(
            {"tenantId": principal["tenantId"], "vehicleId": {"$in": ids}},
            {"vehicleId": 1, "overall": 1, "newIssueCount": 1, "costSummary": 1, "createdAt": 1},
        ).sort("createdAt", -1).to_list(length=3000)
        by_vehicle: dict[str, list] = {}
        for t in trips:
            by_vehicle.setdefault(t["vehicleId"], []).append(t)
        for v in vehicles:
            v["risk"] = _risk_profile(by_vehicle.get(v["id"], []))
    return {"vehicles": vehicles, "total": len(vehicles)}


async def get_vehicle(*, principal: dict, vehicle_id: str) -> dict:
    db = get_db()
    try:
        oid = ObjectId(vehicle_id)
    except Exception:
        raise DomainError(ErrorCode.VALIDATION_ERROR, "Invalid vehicle id.", 400, "vehicleId")
    vehicle = await db.di_vehicles.find_one({"_id": oid, "tenantId": principal["tenantId"]})
    if not vehicle:
        raise DomainError(ErrorCode.NOT_FOUND, "Vehicle not found.", 404)
    trips = await db.di_vehicle_trips.find(
        {"tenantId": principal["tenantId"], "vehicleId": str(oid)}
    ).sort("createdAt", -1).limit(100).to_list(length=100)
    cases_created = sum(1 for t in trips if t.get("damageCaseId"))
    total_new = sum(int(t.get("newIssueCount") or 0) for t in trips)
    return {
        "vehicle": _ser(vehicle),
        "trips": [_ser(t) for t in trips],
        "casesCreated": cases_created,
        "totalNewIssues": total_new,
        "risk": _risk_profile(trips),
    }
