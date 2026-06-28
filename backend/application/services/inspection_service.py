"""
Repository Traceability:
- Source Documents: DI-SPRINT-01 (Create/Get/List/Submit/Patch Inspection Session APIs),
  DI-0004 (Inspection Workflow), DI-0012 (Domain Model), DI-0014 (Security and Tenant Isolation),
  DI-0015 (Audit), DI-0034 (Auth, envelope, error codes).
- Purpose: Inspection session business logic. Pure async functions; all reads/writes are
  tenant-scoped against MongoDB.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId

from api.middleware.safe_errors import DomainError
from application.services.audit_service import write_audit
from application.services.external_references_service import write_references
from domain.enums.audit_actions import ActorType, AuditAction, ObjectType
from domain.enums.error_codes import ErrorCode
from domain.enums.inspection_status import (
    ALLOWED_TRANSITIONS,
    TERMINAL_STATUSES,
    InspectionStatus,
    can_transition,
)
from domain.enums.inspection_type import (
    ALL_INSPECTION_TYPES,
    ALL_SOURCE_SYSTEMS,
)
from infrastructure.db.mongo import get_db


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _to_oid(value: str, field: str) -> ObjectId:
    try:
        return ObjectId(value)
    except Exception:
        raise DomainError(ErrorCode.NOT_FOUND, "Inspection session not found.", 404, field)


def _to_response(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "tenantId": doc["tenantId"],
        "inspectionType": doc["inspectionType"],
        "sourceSystem": doc["sourceSystem"],
        "status": doc["status"],
        "references": doc.get("references", {}),
        "imageCount": doc.get("imageCount", 0),
        "registeredImageCount": doc.get("registeredImageCount", 0),
        "submittedAt": doc.get("submittedAt"),
        "cancelledAt": doc.get("cancelledAt"),
        "failedAt": doc.get("failedAt"),
        "statusReason": doc.get("statusReason"),
        "createdAt": doc["createdAt"],
        "createdBy": doc["createdBy"],
        "updatedAt": doc["updatedAt"],
        "updatedBy": doc["updatedBy"],
        "correlationId": doc.get("correlationId"),
    }


def _list_item(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "inspectionType": doc["inspectionType"],
        "sourceSystem": doc["sourceSystem"],
        "status": doc["status"],
        "references": doc.get("references", {}),
        "imageCount": doc.get("imageCount", 0),
        "createdAt": doc["createdAt"],
        "updatedAt": doc["updatedAt"],
    }


async def _record_status_change(
    *,
    tenant_id: str,
    inspection_session_id: ObjectId,
    from_status: Optional[str],
    to_status: str,
    reason: Optional[str],
    actor_id: str,
    correlation_id: str,
) -> None:
    db = get_db()
    await db.di_inspection_status_history.insert_one(
        {
            "tenantId": tenant_id,
            "inspectionSessionId": str(inspection_session_id),
            "fromStatus": from_status,
            "toStatus": to_status,
            "reason": reason,
            "actorId": actor_id,
            "timestamp": _now(),
            "correlationId": correlation_id,
        }
    )


async def create_inspection_session(
    *,
    principal: dict,
    payload: dict,
    correlation_id: str,
) -> dict:
    db = get_db()
    inspection_type = payload.get("inspectionType")
    source_system = payload.get("sourceSystem")
    references = payload.get("references") or {}

    if inspection_type not in ALL_INSPECTION_TYPES:
        raise DomainError(ErrorCode.VALIDATION_ERROR, "Invalid inspectionType.", 400, "inspectionType")
    if source_system not in ALL_SOURCE_SYSTEMS:
        raise DomainError(ErrorCode.VALIDATION_ERROR, "Invalid sourceSystem.", 400, "sourceSystem")
    if not references.get("externalVehicleRef"):
        raise DomainError(
            ErrorCode.VALIDATION_ERROR,
            "externalVehicleRef is required.",
            400,
            "references.externalVehicleRef",
        )

    # Whitelist allowed keys to avoid storing arbitrary client-supplied fields.
    allowed_ref_keys = {
        "externalVehicleRef",
        "externalRentalAgreementRef",
        "externalMaintenanceRef",
        "externalBranchRef",
        "externalWorkOrderRef",
    }
    refs = {k: v for k, v in references.items() if k in allowed_ref_keys and isinstance(v, str) and v.strip()}

    now = _now()
    doc = {
        "tenantId": principal["tenantId"],
        "inspectionType": inspection_type,
        "sourceSystem": source_system,
        "status": InspectionStatus.DRAFT,
        "references": refs,
        "imageCount": 0,
        "registeredImageCount": 0,
        "createdAt": now,
        "createdBy": principal["id"],
        "updatedAt": now,
        "updatedBy": principal["id"],
        "correlationId": correlation_id,
    }
    result = await db.di_inspection_sessions.insert_one(doc)
    doc["_id"] = result.inserted_id

    await _record_status_change(
        tenant_id=principal["tenantId"],
        inspection_session_id=result.inserted_id,
        from_status=None,
        to_status=InspectionStatus.DRAFT,
        reason=None,
        actor_id=principal["id"],
        correlation_id=correlation_id,
    )
    await write_references(
        tenant_id=principal["tenantId"],
        inspection_session_id=str(result.inserted_id),
        refs=refs,
        correlation_id=correlation_id,
    )
    await write_audit(
        tenant_id=principal["tenantId"],
        actor_id=principal["id"],
        actor_type=ActorType.USER,
        action=AuditAction.INSPECTION_CREATED,
        object_type=ObjectType.INSPECTION_SESSION,
        object_id=str(result.inserted_id),
        correlation_id=correlation_id,
        safe_metadata={"inspectionType": inspection_type, "sourceSystem": source_system},
    )
    return _to_response(doc)


async def _load_session_for_tenant(*, tenant_id: str, session_id: str) -> dict:
    db = get_db()
    oid = _to_oid(session_id, "inspectionSessionId")
    doc = await db.di_inspection_sessions.find_one({"_id": oid, "tenantId": tenant_id})
    if doc is None:
        raise DomainError(ErrorCode.NOT_FOUND, "Inspection session not found.", 404)
    return doc


async def get_inspection_session(*, principal: dict, session_id: str, correlation_id: str) -> dict:
    doc = await _load_session_for_tenant(tenant_id=principal["tenantId"], session_id=session_id)
    await write_audit(
        tenant_id=principal["tenantId"],
        actor_id=principal["id"],
        actor_type=ActorType.USER,
        action=AuditAction.INSPECTION_VIEWED,
        object_type=ObjectType.INSPECTION_SESSION,
        object_id=str(doc["_id"]),
        correlation_id=correlation_id,
    )
    return _to_response(doc)


async def list_inspection_sessions(
    *,
    principal: dict,
    correlation_id: str,
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None,
    inspection_type: Optional[str] = None,
    external_vehicle_ref: Optional[str] = None,
    external_rental_agreement_ref: Optional[str] = None,
    external_branch_ref: Optional[str] = None,
    created_from: Optional[datetime] = None,
    created_to: Optional[datetime] = None,
) -> dict:
    db = get_db()
    page = max(1, page)
    page_size = max(1, min(100, page_size))
    query: dict = {"tenantId": principal["tenantId"]}
    if status:
        query["status"] = status
    if inspection_type:
        query["inspectionType"] = inspection_type
    if external_vehicle_ref:
        query["references.externalVehicleRef"] = external_vehicle_ref
    if external_rental_agreement_ref:
        query["references.externalRentalAgreementRef"] = external_rental_agreement_ref
    if external_branch_ref:
        query["references.externalBranchRef"] = external_branch_ref
    if created_from or created_to:
        rng: dict = {}
        if created_from:
            rng["$gte"] = created_from
        if created_to:
            rng["$lte"] = created_to
        query["createdAt"] = rng

    total = await db.di_inspection_sessions.count_documents(query)
    cursor = (
        db.di_inspection_sessions.find(query)
        .sort("createdAt", -1)
        .skip((page - 1) * page_size)
        .limit(page_size)
    )
    items = [_list_item(d) async for d in cursor]
    await write_audit(
        tenant_id=principal["tenantId"],
        actor_id=principal["id"],
        actor_type=ActorType.USER,
        action=AuditAction.INSPECTION_LISTED,
        object_type=ObjectType.INSPECTION_SESSION,
        object_id="LIST",
        correlation_id=correlation_id,
        safe_metadata={"page": page, "pageSize": page_size, "filters": {k: v for k, v in query.items() if k != "tenantId"}},
    )
    return {
        "items": items,
        "page": page,
        "pageSize": page_size,
        "total": total,
        "totalPages": (total + page_size - 1) // page_size if page_size else 1,
    }


async def _transition(
    *,
    principal: dict,
    session_id: str,
    target_status: str,
    reason: Optional[str],
    correlation_id: str,
    audit_action: str,
) -> dict:
    db = get_db()
    doc = await _load_session_for_tenant(tenant_id=principal["tenantId"], session_id=session_id)
    current_status = doc["status"]
    if current_status in TERMINAL_STATUSES:
        raise DomainError(
            ErrorCode.INVALID_STATUS_TRANSITION,
            f"Inspection is already in terminal status {current_status}.",
            409,
            "status",
        )
    if not can_transition(current_status, target_status):
        raise DomainError(
            ErrorCode.INVALID_STATUS_TRANSITION,
            f"Cannot transition from {current_status} to {target_status}.",
            409,
            "status",
        )
    now = _now()
    update: dict = {
        "status": target_status,
        "updatedAt": now,
        "updatedBy": principal["id"],
    }
    if target_status == InspectionStatus.SUBMITTED:
        update["submittedAt"] = now
    if target_status == InspectionStatus.CANCELLED:
        update["cancelledAt"] = now
        update["statusReason"] = reason
    if target_status == InspectionStatus.FAILED:
        update["failedAt"] = now
        update["statusReason"] = reason

    await db.di_inspection_sessions.update_one({"_id": doc["_id"], "tenantId": principal["tenantId"]}, {"$set": update})
    await _record_status_change(
        tenant_id=principal["tenantId"],
        inspection_session_id=doc["_id"],
        from_status=current_status,
        to_status=target_status,
        reason=reason,
        actor_id=principal["id"],
        correlation_id=correlation_id,
    )
    await write_audit(
        tenant_id=principal["tenantId"],
        actor_id=principal["id"],
        actor_type=ActorType.USER,
        action=audit_action,
        object_type=ObjectType.INSPECTION_SESSION,
        object_id=str(doc["_id"]),
        correlation_id=correlation_id,
        safe_metadata={"fromStatus": current_status, "toStatus": target_status, "reason": reason},
    )
    refreshed = await db.di_inspection_sessions.find_one({"_id": doc["_id"]})
    return _to_response(refreshed)


async def submit_inspection_session(*, principal: dict, session_id: str, correlation_id: str) -> dict:
    return await _transition(
        principal=principal,
        session_id=session_id,
        target_status=InspectionStatus.SUBMITTED,
        reason=None,
        correlation_id=correlation_id,
        audit_action=AuditAction.INSPECTION_SUBMITTED,
    )


async def patch_status(*, principal: dict, session_id: str, target_status: str, reason: Optional[str], correlation_id: str) -> dict:
    # PATCH /status is used ONLY for CANCEL or FAIL (or to advance to CAPTURE_IN_PROGRESS
    # if a client wants to mark capture explicitly). It does NOT accept SUBMITTED -
    # submission goes through POST /submit.
    if target_status not in {
        InspectionStatus.CAPTURE_IN_PROGRESS,
        InspectionStatus.CANCELLED,
        InspectionStatus.FAILED,
    }:
        raise DomainError(
            ErrorCode.INVALID_STATUS_TRANSITION,
            "status PATCH supports only CAPTURE_IN_PROGRESS, CANCELLED, FAILED. Use /submit to submit.",
            409,
            "status",
        )
    if target_status in {InspectionStatus.CANCELLED, InspectionStatus.FAILED} and not reason:
        raise DomainError(ErrorCode.VALIDATION_ERROR, "reason is required for CANCELLED/FAILED.", 400, "reason")
    audit_action = {
        InspectionStatus.CAPTURE_IN_PROGRESS: AuditAction.INSPECTION_STATUS_CHANGED,
        InspectionStatus.CANCELLED: AuditAction.INSPECTION_CANCELLED,
        InspectionStatus.FAILED: AuditAction.INSPECTION_FAILED,
    }[target_status]
    return await _transition(
        principal=principal,
        session_id=session_id,
        target_status=target_status,
        reason=reason,
        correlation_id=correlation_id,
        audit_action=audit_action,
    )
