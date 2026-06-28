"""
Repository Traceability:
- Source Documents: DI-SPRINT-03 (Damage Case create/get/list/status APIs, link APIs,
  status history, duplicate prevention, production ownership boundaries), DI-0012, DI-0015, DI-0034.
- Purpose: Damage-case business logic. Damage Intelligence owns case CONTEXT only — it never
  closes rentals, creates customer charges, owns repair cost, or executes work orders.
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId

from api.middleware.safe_errors import DomainError
from application.services.audit_service import write_audit
from application.services.inspection_service import _load_session_for_tenant
from domain.enums.audit_actions import ActorType, AuditAction, ObjectType
from domain.enums.case_codes import (
    ALL_CASE_TYPES,
    CASE_STATUSES_REQUIRING_REASON,
    CaseLinkType,
    DamageCaseStatus,
    TERMINAL_CASE_STATUSES,
    can_case_transition,
)
from domain.enums.ai_codes import ALL_SEVERITIES
from domain.enums.error_codes import ErrorCode
from infrastructure.db.mongo import get_db


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _dedupe_key(session_id: str, finding_ids: list[str], comparison_ids: list[str]) -> str:
    basis = session_id + "|" + ",".join(sorted(finding_ids)) + "|" + ",".join(sorted(comparison_ids))
    return hashlib.sha256(basis.encode()).hexdigest()


async def _verify_ids(db, tenant_id: str, collection, ids: list[str], field: str) -> list[str]:
    valid: list[str] = []
    for raw in ids:
        try:
            oid = ObjectId(raw)
        except Exception:
            raise DomainError(ErrorCode.VALIDATION_ERROR, f"Invalid id in {field}.", 400, field)
        doc = await collection.find_one({"_id": oid, "tenantId": tenant_id})
        if doc is None:
            raise DomainError(ErrorCode.NOT_FOUND, f"Referenced {field} not found.", 404, field)
        valid.append(raw)
    return valid


async def create_case(
    *, principal: dict, inspection_session_id: str, damage_finding_ids: list[str],
    comparison_result_ids: list[str], case_type: str, severity_code: Optional[str],
    description: Optional[str], correlation_id: str,
) -> dict:
    db = get_db()
    tenant_id = principal["tenantId"]
    if case_type not in ALL_CASE_TYPES:
        raise DomainError(ErrorCode.VALIDATION_ERROR, "Invalid caseType.", 400, "caseType")
    if severity_code is not None and severity_code not in ALL_SEVERITIES:
        raise DomainError(ErrorCode.VALIDATION_ERROR, "Invalid severityCode.", 400, "severityCode")

    session = await _load_session_for_tenant(tenant_id=tenant_id, session_id=inspection_session_id)
    finding_ids = await _verify_ids(db, tenant_id, db.di_ai_findings, damage_finding_ids or [], "damageFindingIds")
    comparison_ids = await _verify_ids(db, tenant_id, db.di_damage_comparison_results, comparison_result_ids or [], "comparisonResultIds")
    if not finding_ids and not comparison_ids:
        raise DomainError(ErrorCode.VALIDATION_ERROR,
                          "At least one damageFindingId or comparisonResultId is required.", 400, "damageFindingIds")

    dedupe_key = _dedupe_key(str(session["_id"]), finding_ids, comparison_ids)
    existing = await db.di_damage_cases.find_one(
        {"tenantId": tenant_id, "dedupeKey": dedupe_key,
         "status": {"$nin": list(TERMINAL_CASE_STATUSES)}}
    )
    if existing is not None:
        await write_audit(
            tenant_id=tenant_id, actor_id=principal["id"], actor_type=ActorType.USER,
            action=AuditAction.DUPLICATE_DAMAGE_CASE_PREVENTED, object_type=ObjectType.DAMAGE_CASE,
            object_id=str(existing["_id"]), correlation_id=correlation_id,
            safe_metadata={"inspectionSessionId": str(session["_id"])},
        )
        raise DomainError(ErrorCode.CONFLICT,
                          "An active damage case already exists for the same evidence.", 409, "damageCaseId")

    now = _now()
    doc = {
        "tenantId": tenant_id,
        "inspectionSessionId": str(session["_id"]),
        "externalVehicleRef": (session.get("references") or {}).get("externalVehicleRef"),
        "caseType": case_type,
        "severityCode": severity_code,
        "description": (description or "").strip()[:2000] or None,
        "status": DamageCaseStatus.OPEN,
        "dedupeKey": dedupe_key,
        "createdAt": now,
        "createdBy": principal["id"],
        "updatedAt": now,
        "updatedBy": principal["id"],
        "correlationId": correlation_id,
    }
    insert = await db.di_damage_cases.insert_one(doc)
    case_id = str(insert.inserted_id)

    links: list[dict] = []
    for fid in finding_ids:
        links.append({"tenantId": tenant_id, "damageCaseId": case_id, "linkType": CaseLinkType.FINDING,
                      "linkedId": fid, "createdAt": now, "createdBy": principal["id"], "correlationId": correlation_id})
    for cid in comparison_ids:
        links.append({"tenantId": tenant_id, "damageCaseId": case_id, "linkType": CaseLinkType.COMPARISON_RESULT,
                      "linkedId": cid, "createdAt": now, "createdBy": principal["id"], "correlationId": correlation_id})
    if links:
        await db.di_damage_case_links.insert_many(links)

    await db.di_damage_case_status_history.insert_one({
        "tenantId": tenant_id, "damageCaseId": case_id, "fromStatus": None,
        "toStatus": DamageCaseStatus.OPEN, "reason": None, "actorId": principal["id"],
        "timestamp": now, "correlationId": correlation_id,
    })
    await write_audit(
        tenant_id=tenant_id, actor_id=principal["id"], actor_type=ActorType.USER,
        action=AuditAction.DAMAGE_CASE_CREATED, object_type=ObjectType.DAMAGE_CASE,
        object_id=case_id, correlation_id=correlation_id,
        safe_metadata={"caseType": case_type, "findings": len(finding_ids), "comparisons": len(comparison_ids)},
    )
    return await get_case(principal=principal, case_id=case_id, correlation_id=correlation_id, audit=False)


def _case_to_response(doc: dict, links: list[dict], history: list[dict]) -> dict:
    return {
        "damageCaseId": str(doc["_id"]),
        "tenantId": doc["tenantId"],
        "inspectionSessionId": doc.get("inspectionSessionId"),
        "externalVehicleRef": doc.get("externalVehicleRef"),
        "caseType": doc.get("caseType"),
        "severityCode": doc.get("severityCode"),
        "description": doc.get("description"),
        "status": doc["status"],
        "links": [
            {"linkType": l["linkType"], "linkedId": l["linkedId"]} for l in links
        ],
        "statusHistory": [
            {"fromStatus": h.get("fromStatus"), "toStatus": h["toStatus"], "reason": h.get("reason"),
             "actorId": h.get("actorId"), "timestamp": h["timestamp"].isoformat() if h.get("timestamp") else None}
            for h in history
        ],
        "createdAt": doc["createdAt"].isoformat() if doc.get("createdAt") else None,
        "updatedAt": doc["updatedAt"].isoformat() if doc.get("updatedAt") else None,
        "ownershipNote": "Advisory case context. Final liability, customer charge, repair cost, and work-order execution remain with CROMS / Maintenance / Finance.",
    }


async def _load_case(tenant_id: str, case_id: str) -> dict:
    db = get_db()
    try:
        oid = ObjectId(case_id)
    except Exception:
        raise DomainError(ErrorCode.NOT_FOUND, "Damage case not found.", 404, "damageCaseId")
    doc = await db.di_damage_cases.find_one({"_id": oid, "tenantId": tenant_id})
    if doc is None:
        raise DomainError(ErrorCode.NOT_FOUND, "Damage case not found.", 404, "damageCaseId")
    return doc


async def get_case(*, principal: dict, case_id: str, correlation_id: str, audit: bool = True) -> dict:
    db = get_db()
    doc = await _load_case(principal["tenantId"], case_id)
    links = [l async for l in db.di_damage_case_links.find(
        {"tenantId": principal["tenantId"], "damageCaseId": str(doc["_id"])})]
    history = [h async for h in db.di_damage_case_status_history.find(
        {"tenantId": principal["tenantId"], "damageCaseId": str(doc["_id"])}).sort("timestamp", 1)]
    if audit:
        await write_audit(
            tenant_id=principal["tenantId"], actor_id=principal["id"], actor_type=ActorType.USER,
            action=AuditAction.DAMAGE_CASE_VIEWED, object_type=ObjectType.DAMAGE_CASE,
            object_id=str(doc["_id"]), correlation_id=correlation_id,
        )
    return _case_to_response(doc, links, history)


async def list_cases(
    *, principal: dict, correlation_id: str, status: Optional[str] = None,
    case_type: Optional[str] = None, external_vehicle_ref: Optional[str] = None,
    inspection_session_id: Optional[str] = None, page: int = 1, page_size: int = 20,
) -> dict:
    db = get_db()
    page = max(1, page)
    page_size = max(1, min(100, page_size))
    query: dict = {"tenantId": principal["tenantId"]}
    if status:
        query["status"] = status
    if case_type:
        query["caseType"] = case_type
    if external_vehicle_ref:
        query["externalVehicleRef"] = external_vehicle_ref
    if inspection_session_id:
        query["inspectionSessionId"] = inspection_session_id
    total = await db.di_damage_cases.count_documents(query)
    cursor = (db.di_damage_cases.find(query).sort("createdAt", -1)
              .skip((page - 1) * page_size).limit(page_size))
    items = []
    async for d in cursor:
        items.append({
            "damageCaseId": str(d["_id"]), "inspectionSessionId": d.get("inspectionSessionId"),
            "externalVehicleRef": d.get("externalVehicleRef"), "caseType": d.get("caseType"),
            "severityCode": d.get("severityCode"), "status": d["status"],
            "createdAt": d["createdAt"].isoformat() if d.get("createdAt") else None,
            "updatedAt": d["updatedAt"].isoformat() if d.get("updatedAt") else None,
        })
    return {"items": items, "page": page, "pageSize": page_size, "total": total,
            "totalPages": (total + page_size - 1) // page_size if page_size else 1}


async def update_status(
    *, principal: dict, case_id: str, target_status: str, reason: Optional[str], correlation_id: str,
) -> dict:
    db = get_db()
    tenant_id = principal["tenantId"]
    doc = await _load_case(tenant_id, case_id)
    current = doc["status"]
    if current in TERMINAL_CASE_STATUSES:
        raise DomainError(ErrorCode.INVALID_STATUS_TRANSITION,
                          f"Damage case is already in terminal status {current}.", 409, "status")
    if not can_case_transition(current, target_status):
        raise DomainError(ErrorCode.INVALID_STATUS_TRANSITION,
                          f"Cannot transition from {current} to {target_status}.", 409, "status")
    if target_status in CASE_STATUSES_REQUIRING_REASON and not (reason and reason.strip()):
        raise DomainError(ErrorCode.VALIDATION_ERROR, "reason is required for this status change.", 400, "reason")
    now = _now()
    await db.di_damage_cases.update_one(
        {"_id": doc["_id"], "tenantId": tenant_id},
        {"$set": {"status": target_status, "updatedAt": now, "updatedBy": principal["id"],
                  "statusReason": (reason or "").strip()[:1000] or None}},
    )
    await db.di_damage_case_status_history.insert_one({
        "tenantId": tenant_id, "damageCaseId": str(doc["_id"]), "fromStatus": current,
        "toStatus": target_status, "reason": (reason or "").strip()[:1000] or None,
        "actorId": principal["id"], "timestamp": now, "correlationId": correlation_id,
    })
    await write_audit(
        tenant_id=tenant_id, actor_id=principal["id"], actor_type=ActorType.USER,
        action=AuditAction.DAMAGE_CASE_STATUS_CHANGED, object_type=ObjectType.DAMAGE_CASE,
        object_id=str(doc["_id"]), correlation_id=correlation_id,
        safe_metadata={"fromStatus": current, "toStatus": target_status},
    )
    return await get_case(principal=principal, case_id=case_id, correlation_id=correlation_id, audit=False)


async def add_link(
    *, principal: dict, case_id: str, link_type: str, linked_id: str, correlation_id: str,
) -> dict:
    db = get_db()
    tenant_id = principal["tenantId"]
    doc = await _load_case(tenant_id, case_id)
    if doc["status"] in TERMINAL_CASE_STATUSES:
        raise DomainError(ErrorCode.INVALID_STATUS_TRANSITION, "Cannot modify a terminal damage case.", 409, "status")
    collection_for = {
        CaseLinkType.EVIDENCE: db.di_evidence_references,
        CaseLinkType.FINDING: db.di_ai_findings,
        CaseLinkType.COMPARISON_RESULT: db.di_damage_comparison_results,
    }
    if link_type not in collection_for:
        raise DomainError(ErrorCode.VALIDATION_ERROR, "Invalid linkType.", 400, "linkType")
    await _verify_ids(db, tenant_id, collection_for[link_type], [linked_id], "linkedId")
    existing = await db.di_damage_case_links.find_one(
        {"tenantId": tenant_id, "damageCaseId": str(doc["_id"]), "linkType": link_type, "linkedId": linked_id}
    )
    now = _now()
    if existing is None:
        await db.di_damage_case_links.insert_one({
            "tenantId": tenant_id, "damageCaseId": str(doc["_id"]), "linkType": link_type,
            "linkedId": linked_id, "createdAt": now, "createdBy": principal["id"], "correlationId": correlation_id,
        })
    await db.di_damage_cases.update_one(
        {"_id": doc["_id"], "tenantId": tenant_id}, {"$set": {"updatedAt": now, "updatedBy": principal["id"]}})
    await write_audit(
        tenant_id=tenant_id, actor_id=principal["id"], actor_type=ActorType.USER,
        action=AuditAction.DAMAGE_CASE_LINK_UPDATED, object_type=ObjectType.DAMAGE_CASE,
        object_id=str(doc["_id"]), correlation_id=correlation_id,
        safe_metadata={"linkType": link_type, "added": existing is None},
    )
    return await get_case(principal=principal, case_id=case_id, correlation_id=correlation_id, audit=False)
