"""
Repository Traceability:
- Source Documents: DI-SPRINT-03 (Review Queue, Review Decision, Additional Evidence
  Request, review routing rules), DI-0019, DI-0015 (audit), DI-0034.
- Purpose: Review-queue business logic — auto-routing, queue listing, decisions,
  and additional-evidence requests. AI/comparison outputs remain advisory until reviewed.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId

from api.middleware.safe_errors import DomainError
from application.services.audit_service import write_audit
from domain.enums.ai_codes import ALL_DAMAGE_TYPES, ALL_SEVERITIES
from domain.enums.audit_actions import ActorType, AuditAction, ObjectType
from domain.enums.error_codes import ErrorCode
from domain.enums.review_codes import (
    ALL_DECISION_CODES,
    DECISIONS_REQUIRING_REASON,
    ReviewDecisionCode,
    ReviewItemStatus,
    ReviewObjectType,
    ReviewPriority,
)
from infrastructure.db.mongo import get_db


def _now() -> datetime:
    return datetime.now(timezone.utc)


async def enqueue_review_item(
    *,
    tenant_id: str,
    object_type: str,
    object_id: str,
    inspection_session_id: str,
    source: str,
    severity_code: Optional[str],
    priority: str,
    reason: str,
    correlation_id: str,
) -> bool:
    """Insert a PENDING review item. Idempotent on (tenant, objectType, objectId).
    Returns True if a new item was created."""
    db = get_db()
    existing = await db.di_review_queue_items.find_one(
        {"tenantId": tenant_id, "objectType": object_type, "objectId": object_id}
    )
    if existing is not None:
        return False
    now = _now()
    doc = {
        "tenantId": tenant_id,
        "objectType": object_type,
        "objectId": object_id,
        "inspectionSessionId": inspection_session_id,
        "source": source,
        "priority": priority,
        "severityCode": severity_code,
        "reviewStatus": ReviewItemStatus.PENDING,
        "reason": reason,
        "decisionId": None,
        "createdAt": now,
        "createdBy": "SYSTEM",
        "updatedAt": now,
        "correlationId": correlation_id,
    }
    try:
        insert = await db.di_review_queue_items.insert_one(doc)
    except Exception:
        return False  # unique-index race -> already queued
    await write_audit(
        tenant_id=tenant_id, actor_id="SYSTEM", actor_type=ActorType.SYSTEM,
        action=AuditAction.REVIEW_ITEM_CREATED, object_type=ObjectType.REVIEW_ITEM,
        object_id=str(insert.inserted_id), correlation_id=correlation_id,
        safe_metadata={"objectType": object_type, "source": source, "priority": priority},
    )
    return True


async def auto_route_session_findings(
    *, tenant_id: str, inspection_session_id: str, ai_analysis_id: str, correlation_id: str
) -> int:
    """Auto-route LOW_CONFIDENCE / UNCERTAIN AI findings to the review queue
    (DECISION-Sprint03-b). Honors per-tenant autoRouteLowConfidence switch (default true)."""
    db = get_db()
    cfg = await db.di_ai_configuration.find_one({"tenantId": tenant_id}) or {}
    auto_route = cfg.get("autoRouteLowConfidence")
    if not isinstance(auto_route, bool):
        auto_route = True
    if not auto_route:
        return 0
    routed = 0
    cursor = db.di_ai_findings.find(
        {"tenantId": tenant_id, "aiAnalysisId": ai_analysis_id,
         "status": {"$in": ["LOW_CONFIDENCE", "UNCERTAIN"]}}
    )
    async for f in cursor:
        priority = ReviewPriority.HIGH if f.get("status") == "UNCERTAIN" else ReviewPriority.MEDIUM
        if f.get("severity") == "HIGH":
            priority = ReviewPriority.HIGH
        created = await enqueue_review_item(
            tenant_id=tenant_id, object_type=ReviewObjectType.DAMAGE_FINDING,
            object_id=str(f["_id"]), inspection_session_id=inspection_session_id,
            source="AI_FINDING", severity_code=f.get("severity"), priority=priority,
            reason=f"AI finding flagged {f.get('status')} requires review.",
            correlation_id=correlation_id,
        )
        if created:
            routed += 1
    return routed


def _item_to_response(d: dict) -> dict:
    created = d.get("createdAt")
    age_minutes = None
    if created:
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        age_minutes = int((_now() - created).total_seconds() // 60)
    return {
        "reviewItemId": str(d["_id"]),
        "objectType": d["objectType"],
        "objectId": d["objectId"],
        "inspectionSessionId": d.get("inspectionSessionId"),
        "source": d.get("source"),
        "priority": d.get("priority"),
        "severityCode": d.get("severityCode"),
        "reviewStatus": d["reviewStatus"],
        "reason": d.get("reason"),
        "ageMinutes": age_minutes,
        "decisionId": d.get("decisionId"),
        "createdAt": created.isoformat() if created else None,
    }


async def _load_linked_object(tenant_id: str, item: dict) -> Optional[dict]:
    db = get_db()
    try:
        oid = ObjectId(item["objectId"])
    except Exception:
        return None
    if item["objectType"] == ReviewObjectType.DAMAGE_FINDING:
        d = await db.di_ai_findings.find_one({"_id": oid, "tenantId": tenant_id})
        if not d:
            return None
        return {
            "id": str(d["_id"]), "damageType": d.get("damageType"), "area": d.get("area"),
            "confidence": d.get("confidence"), "severity": d.get("severity"),
            "status": d.get("status"), "capturePosition": d.get("capturePosition"),
            "inspectionImageId": d.get("inspectionImageId"), "reviewState": d.get("reviewState"),
        }
    d = await db.di_damage_comparison_results.find_one({"_id": oid, "tenantId": tenant_id})
    if not d:
        return None
    return {
        "id": str(d["_id"]), "comparisonId": d.get("comparisonId"),
        "comparisonOutcomeCode": d.get("comparisonOutcomeCode"),
        "capturePosition": d.get("capturePosition"), "damageType": d.get("damageType"),
        "area": d.get("area"), "confidenceScore": d.get("confidenceScore"),
        "severity": d.get("severity"), "uncertaintyReason": d.get("uncertaintyReason"),
        "reviewState": d.get("reviewState"),
    }


async def list_review_queue(
    *, principal: dict, correlation_id: str,
    status: Optional[str] = None, priority: Optional[str] = None,
    object_type: Optional[str] = None, inspection_session_id: Optional[str] = None,
    page: int = 1, page_size: int = 20,
) -> dict:
    db = get_db()
    page = max(1, page)
    page_size = max(1, min(100, page_size))
    query: dict = {"tenantId": principal["tenantId"]}
    if status:
        query["reviewStatus"] = status
    if priority:
        query["priority"] = priority
    if object_type:
        query["objectType"] = object_type
    if inspection_session_id:
        query["inspectionSessionId"] = inspection_session_id
    total = await db.di_review_queue_items.count_documents(query)
    cursor = (
        db.di_review_queue_items.find(query)
        .sort([("priority", 1), ("createdAt", 1)])
        .skip((page - 1) * page_size)
        .limit(page_size)
    )
    items = [_item_to_response(d) async for d in cursor]
    return {
        "items": items, "page": page, "pageSize": page_size, "total": total,
        "totalPages": (total + page_size - 1) // page_size if page_size else 1,
    }


async def _load_item(tenant_id: str, review_item_id: str) -> dict:
    db = get_db()
    try:
        oid = ObjectId(review_item_id)
    except Exception:
        raise DomainError(ErrorCode.NOT_FOUND, "Review item not found.", 404, "reviewItemId")
    item = await db.di_review_queue_items.find_one({"_id": oid, "tenantId": tenant_id})
    if item is None:
        raise DomainError(ErrorCode.NOT_FOUND, "Review item not found.", 404, "reviewItemId")
    return item


async def get_review_item(*, principal: dict, review_item_id: str, correlation_id: str) -> dict:
    item = await _load_item(principal["tenantId"], review_item_id)
    linked = await _load_linked_object(principal["tenantId"], item)
    await write_audit(
        tenant_id=principal["tenantId"], actor_id=principal["id"], actor_type=ActorType.USER,
        action=AuditAction.REVIEW_ITEM_VIEWED, object_type=ObjectType.REVIEW_ITEM,
        object_id=str(item["_id"]), correlation_id=correlation_id,
    )
    payload = _item_to_response(item)
    payload["linkedObject"] = linked
    return payload


async def _apply_finding_edit(tenant_id: str, finding_id: str, updated: dict) -> dict:
    """Apply reviewer edits to an AI finding; returns {previous, new}."""
    db = get_db()
    oid = ObjectId(finding_id)
    finding = await db.di_ai_findings.find_one({"_id": oid, "tenantId": tenant_id})
    if finding is None:
        raise DomainError(ErrorCode.NOT_FOUND, "Linked finding not found.", 404)
    allowed = {}
    if isinstance(updated.get("damageType"), str) and updated["damageType"].upper() in ALL_DAMAGE_TYPES:
        allowed["damageType"] = updated["damageType"].upper()
    if isinstance(updated.get("area"), str):
        allowed["area"] = updated["area"][:200]
    if isinstance(updated.get("severity"), str) and updated["severity"].upper() in ALL_SEVERITIES:
        allowed["severity"] = updated["severity"].upper()
    if isinstance(updated.get("vehicleAreaCode"), str):
        allowed["vehicleAreaCode"] = updated["vehicleAreaCode"][:64]
    if not allowed:
        return {"previous": {}, "new": {}}
    previous = {k: finding.get(k) for k in allowed}
    allowed["updatedAt"] = _now()
    await db.di_ai_findings.update_one({"_id": oid, "tenantId": tenant_id}, {"$set": allowed})
    return {"previous": previous, "new": {k: v for k, v in allowed.items() if k != "updatedAt"}}


async def record_decision(
    *, principal: dict, review_item_id: str, decision_code: str,
    reason: Optional[str], updated_finding: Optional[dict], correlation_id: str,
) -> dict:
    db = get_db()
    tenant_id = principal["tenantId"]
    if decision_code not in ALL_DECISION_CODES:
        raise DomainError(ErrorCode.VALIDATION_ERROR, "Invalid decisionCode.", 400, "decisionCode")
    if decision_code in DECISIONS_REQUIRING_REASON and not (reason and reason.strip()):
        raise DomainError(ErrorCode.VALIDATION_ERROR, "reason is required for this decision.", 400, "reason")

    item = await _load_item(tenant_id, review_item_id)
    if item["reviewStatus"] == ReviewItemStatus.DECIDED:
        raise DomainError(ErrorCode.INVALID_STATUS_TRANSITION, "Review item already decided.", 409, "reviewItemId")

    edit_diff = None
    if decision_code == ReviewDecisionCode.EDITED:
        if item["objectType"] != ReviewObjectType.DAMAGE_FINDING:
            raise DomainError(ErrorCode.VALIDATION_ERROR, "EDITED applies only to damage findings.", 400, "decisionCode")
        if not updated_finding:
            raise DomainError(ErrorCode.VALIDATION_ERROR, "updatedFinding is required for EDITED.", 400, "updatedFinding")
        edit_diff = await _apply_finding_edit(tenant_id, item["objectId"], updated_finding)

    now = _now()
    decision_doc = {
        "tenantId": tenant_id,
        "reviewItemId": str(item["_id"]),
        "objectType": item["objectType"],
        "objectId": item["objectId"],
        "decisionCode": decision_code,
        "reason": (reason or "").strip()[:1000] or None,
        "editDiff": edit_diff,
        "decidedBy": principal["id"],
        "recordedAt": now,
        "correlationId": correlation_id,
    }
    decision_insert = await db.di_review_decisions.insert_one(decision_doc)

    # New review-item status from decision code.
    if decision_code == ReviewDecisionCode.ESCALATED:
        new_status = ReviewItemStatus.ESCALATED
    elif decision_code == ReviewDecisionCode.ADDITIONAL_EVIDENCE_REQUIRED:
        new_status = ReviewItemStatus.ADDITIONAL_EVIDENCE_REQUIRED
    elif decision_code == ReviewDecisionCode.DEFERRED:
        new_status = ReviewItemStatus.IN_REVIEW
    else:
        new_status = ReviewItemStatus.DECIDED
    await db.di_review_queue_items.update_one(
        {"_id": item["_id"], "tenantId": tenant_id},
        {"$set": {"reviewStatus": new_status, "decisionId": str(decision_insert.inserted_id),
                  "updatedAt": now, "decidedBy": principal["id"], "lastDecisionCode": decision_code}},
    )

    # Reflect decision on the linked object (advisory -> reviewed state).
    review_state = {"CONFIRMED": "CONFIRMED", "REJECTED": "REJECTED", "EDITED": "EDITED",
                    "DUPLICATE": "DUPLICATE"}.get(decision_code)
    if review_state:
        coll = db.di_ai_findings if item["objectType"] == ReviewObjectType.DAMAGE_FINDING else db.di_damage_comparison_results
        try:
            await coll.update_one(
                {"_id": ObjectId(item["objectId"]), "tenantId": tenant_id},
                {"$set": {"reviewState": review_state, "updatedAt": now}},
            )
        except Exception:
            pass

    audit_action = (AuditAction.REVIEW_ITEM_ESCALATED if decision_code == ReviewDecisionCode.ESCALATED
                    else AuditAction.REVIEW_DECISION_RECORDED)
    await write_audit(
        tenant_id=tenant_id, actor_id=principal["id"], actor_type=ActorType.USER,
        action=audit_action, object_type=ObjectType.REVIEW_ITEM, object_id=str(item["_id"]),
        correlation_id=correlation_id,
        safe_metadata={"decisionCode": decision_code, "newStatus": new_status,
                       "edited": edit_diff is not None},
    )
    return {
        "reviewDecisionId": str(decision_insert.inserted_id),
        "reviewItemId": str(item["_id"]),
        "decisionCode": decision_code,
        "reviewStatus": new_status,
        "editDiff": edit_diff,
        "recordedAt": now.isoformat(),
    }


async def request_additional_evidence(
    *, principal: dict, review_item_id: str, reason: str, requested_positions: Optional[list],
    correlation_id: str,
) -> dict:
    db = get_db()
    tenant_id = principal["tenantId"]
    if not (reason and reason.strip()):
        raise DomainError(ErrorCode.VALIDATION_ERROR, "reason is required.", 400, "reason")
    item = await _load_item(tenant_id, review_item_id)
    now = _now()
    doc = {
        "tenantId": tenant_id,
        "reviewItemId": str(item["_id"]),
        "inspectionSessionId": item.get("inspectionSessionId"),
        "objectType": item["objectType"],
        "objectId": item["objectId"],
        "reason": reason.strip()[:1000],
        "requestedPositions": [p for p in (requested_positions or []) if isinstance(p, str)][:20],
        "status": "OPEN",
        "createdAt": now,
        "createdBy": principal["id"],
        "correlationId": correlation_id,
    }
    insert = await db.di_additional_evidence_requests.insert_one(doc)
    await db.di_review_queue_items.update_one(
        {"_id": item["_id"], "tenantId": tenant_id},
        {"$set": {"reviewStatus": ReviewItemStatus.ADDITIONAL_EVIDENCE_REQUIRED, "updatedAt": now}},
    )
    await write_audit(
        tenant_id=tenant_id, actor_id=principal["id"], actor_type=ActorType.USER,
        action=AuditAction.ADDITIONAL_EVIDENCE_REQUESTED, object_type=ObjectType.REVIEW_ITEM,
        object_id=str(item["_id"]), correlation_id=correlation_id,
        safe_metadata={"requestId": str(insert.inserted_id)},
    )
    return {
        "additionalEvidenceRequestId": str(insert.inserted_id),
        "reviewItemId": str(item["_id"]),
        "status": "OPEN",
        "createdAt": now.isoformat(),
    }
