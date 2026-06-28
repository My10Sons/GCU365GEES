"""
Repository Traceability:
- Source Documents: DI-SPRINT-04 (CROMS + Maintenance integration APIs, idempotency,
  ownership boundaries, audit), DI-0017, DI-0018, DI-0031, DI-0034, DI-0014, DI-0015.
- Purpose: Production CROMS / GCU365Maintenance integration business logic. Damage
  Intelligence exchanges references, evidence context, and status only. It never owns
  rental closure, final customer charge, work-order execution, or actual repair cost.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId

from api.middleware.safe_errors import DomainError
from application.services import idempotency_service
from application.services.audit_service import write_audit
from application.services.inspection_service import create_inspection_session, _load_session_for_tenant
from domain.enums.audit_actions import ActorType, AuditAction, ObjectType
from domain.enums.case_codes import TERMINAL_CASE_STATUSES
from domain.enums.error_codes import ErrorCode
from domain.enums.integration_codes import IntegrationOperation, IntegrationStatus, SourceSystemRef
from domain.enums.inspection_type import InspectionType, SourceSystem
from infrastructure.db.mongo import get_db
from infrastructure.integrations.croms_stub import CromsClientStub
from infrastructure.integrations.maintenance_stub import MaintenanceClientStub

NOT_OWNED = "NOT_OWNED_BY_DAMAGE_INTELLIGENCE"


def _now() -> datetime:
    return datetime.now(timezone.utc)


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


# ----------------------------- CROMS -----------------------------

async def croms_create_inspection(
    *, principal: dict, inspection_type: str, payload: dict, idempotency_key: Optional[str], correlation_id: str,
) -> dict:
    tenant_id = principal["tenantId"]
    operation = (IntegrationOperation.CROMS_CHECK_OUT if inspection_type == InspectionType.CHECK_OUT
                 else IntegrationOperation.CROMS_CHECK_IN)
    replay = await idempotency_service.check_replay(
        tenant_id=tenant_id, idempotency_key=idempotency_key, operation=operation,
        payload=payload, actor_id=principal["id"], correlation_id=correlation_id,
    )
    if replay is not None:
        return replay

    rental_agreement_id = payload.get("rentalAgreementId")
    vehicle_id = payload.get("vehicleId")
    if not rental_agreement_id:
        raise DomainError(ErrorCode.VALIDATION_ERROR, "rentalAgreementId is required.", 400, "rentalAgreementId")
    if not vehicle_id:
        raise DomainError(ErrorCode.VALIDATION_ERROR, "vehicleId is required.", 400, "vehicleId")

    baseline_id = payload.get("baselineInspectionSessionId")
    if baseline_id:
        # Validate baseline belongs to same tenant (no cross-tenant references).
        await _load_session_for_tenant(tenant_id=tenant_id, session_id=baseline_id)

    refs = {
        "externalVehicleRef": str(vehicle_id),
        "externalRentalAgreementRef": str(rental_agreement_id),
    }
    if payload.get("branchId"):
        refs["externalBranchRef"] = str(payload["branchId"])

    session = await create_inspection_session(
        principal=principal,
        payload={"inspectionType": inspection_type, "sourceSystem": SourceSystem.CROMS, "references": refs},
        correlation_id=correlation_id,
    )

    if baseline_id:
        db = get_db()
        await db.di_inspection_sessions.update_one(
            {"_id": ObjectId(session["id"]), "tenantId": tenant_id},
            {"$set": {"baselineInspectionSessionId": baseline_id, "updatedAt": _now()}},
        )

    data = {
        "inspectionSessionId": session["id"],
        "inspectionType": inspection_type,
        "status": session["status"],
    }
    if baseline_id:
        data["baselineInspectionSessionId"] = baseline_id

    await write_audit(
        tenant_id=tenant_id, actor_id=principal["id"], actor_type=ActorType.SERVICE,
        action=(AuditAction.CROMS_CHECKOUT_INSPECTION_REQUESTED if inspection_type == InspectionType.CHECK_OUT
                else AuditAction.CROMS_CHECKIN_INSPECTION_REQUESTED),
        object_type=ObjectType.INSPECTION_SESSION, object_id=session["id"], correlation_id=correlation_id,
        safe_metadata={"rentalAgreementRef": str(rental_agreement_id), "sourceSystem": SourceSystemRef.CROMS},
    )
    await idempotency_service.store_result(
        tenant_id=tenant_id, idempotency_key=idempotency_key, operation=operation,
        payload=payload, response_data=data, actor_id=principal["id"], correlation_id=correlation_id,
    )
    return data


async def croms_damage_summary(*, principal: dict, rental_agreement_id: str, correlation_id: str) -> dict:
    db = get_db()
    tenant_id = principal["tenantId"]
    sessions = [s async for s in db.di_inspection_sessions.find(
        {"tenantId": tenant_id, "references.externalRentalAgreementRef": rental_agreement_id}
    ).sort("createdAt", 1)]
    if not sessions:
        raise DomainError(ErrorCode.NOT_FOUND, "No inspections for this rental agreement.", 404, "rentalAgreementId")

    check_out = next((s for s in sessions if s.get("inspectionType") == InspectionType.CHECK_OUT), None)
    check_in = next((s for s in reversed(sessions) if s.get("inspectionType") == InspectionType.CHECK_IN), None)
    session_ids = [str(s["_id"]) for s in sessions]
    vehicle_id = (sessions[0].get("references") or {}).get("externalVehicleRef")

    total_findings = await db.di_ai_findings.count_documents(
        {"tenantId": tenant_id, "inspectionSessionId": {"$in": session_ids}})
    review_required = await db.di_ai_findings.count_documents(
        {"tenantId": tenant_id, "inspectionSessionId": {"$in": session_ids},
         "status": {"$in": ["LOW_CONFIDENCE", "UNCERTAIN"]}})
    latest_cmp = await db.di_damage_comparisons.find_one(
        {"tenantId": tenant_id, "inspectionSessionId": {"$in": session_ids}}, sort=[("createdAt", -1)])
    case_ids = [str(c["_id"]) async for c in db.di_damage_cases.find(
        {"tenantId": tenant_id, "inspectionSessionId": {"$in": session_ids}})]

    summary_status = "REVIEW_REQUIRED" if review_required > 0 else ("DAMAGE_FOUND" if total_findings > 0 else "NO_DAMAGE_DETECTED")

    await write_audit(
        tenant_id=tenant_id, actor_id=principal["id"], actor_type=ActorType.SERVICE,
        action=AuditAction.CROMS_DAMAGE_SUMMARY_ACCESSED, object_type=ObjectType.INTEGRATION,
        object_id=rental_agreement_id, correlation_id=correlation_id,
        safe_metadata={"sessions": len(session_ids), "cases": len(case_ids)},
    )
    return {
        "rentalAgreementId": rental_agreement_id,
        "vehicleId": vehicle_id,
        "checkOutInspectionSessionId": str(check_out["_id"]) if check_out else None,
        "checkInInspectionSessionId": str(check_in["_id"]) if check_in else None,
        "damageSummaryStatus": summary_status,
        "totalFindings": total_findings,
        "damageCaseIds": case_ids,
        "comparisonStatus": (latest_cmp or {}).get("status"),
        "reportReference": None,
        "evidencePackageReference": None,
        "finalCustomerChargeDecision": NOT_OWNED,
        "isAdvisory": True,
    }


async def croms_inspection_status(*, principal: dict, session_id: str, correlation_id: str) -> dict:
    session = await _load_session_for_tenant(tenant_id=principal["tenantId"], session_id=session_id)
    await write_audit(
        tenant_id=principal["tenantId"], actor_id=principal["id"], actor_type=ActorType.SERVICE,
        action=AuditAction.CROMS_INSPECTION_STATUS_ACCESSED, object_type=ObjectType.INSPECTION_SESSION,
        object_id=str(session["_id"]), correlation_id=correlation_id,
    )
    return {
        "inspectionSessionId": str(session["_id"]),
        "inspectionType": session.get("inspectionType"),
        "status": session.get("status"),
        "registeredImageCount": session.get("registeredImageCount", 0),
    }


async def croms_notify_damage_summary_ready(
    *, principal: dict, rental_agreement_id: str, correlation_id: str,
) -> dict:
    client = CromsClientStub()
    result = await client.notify_damage_summary_ready(
        tenant_id=principal["tenantId"], rental_agreement_id=rental_agreement_id,
        damage_summary_ref=f"summary:{rental_agreement_id}", correlation_id=correlation_id,
    )
    await write_audit(
        tenant_id=principal["tenantId"], actor_id=principal["id"], actor_type=ActorType.SERVICE,
        action=AuditAction.CROMS_NOTIFICATION_QUEUED, object_type=ObjectType.INTEGRATION,
        object_id=rental_agreement_id, correlation_id=correlation_id,
        safe_metadata={"delivered": result.get("delivered", False)},
    )
    return {"rentalAgreementId": rental_agreement_id, "queued": True, "delivered": result.get("delivered", False)}


# -------------------------- Maintenance --------------------------

async def maintenance_handoff(
    *, principal: dict, payload: dict, idempotency_key: Optional[str], correlation_id: str,
) -> dict:
    tenant_id = principal["tenantId"]
    replay = await idempotency_service.check_replay(
        tenant_id=tenant_id, idempotency_key=idempotency_key, operation=IntegrationOperation.MAINTENANCE_HANDOFF,
        payload=payload, actor_id=principal["id"], correlation_id=correlation_id,
    )
    if replay is not None:
        return replay

    case_id = payload.get("damageCaseId")
    if not case_id:
        raise DomainError(ErrorCode.VALIDATION_ERROR, "damageCaseId is required.", 400, "damageCaseId")
    case = await _load_case(tenant_id, case_id)
    if case["status"] in TERMINAL_CASE_STATUSES:
        raise DomainError(ErrorCode.CONFLICT, f"Damage case is {case['status']}; not eligible for handoff.", 409, "damageCaseId")

    db = get_db()
    now = _now()
    handoff_doc = {
        "tenantId": tenant_id,
        "damageCaseId": case_id,
        "vehicleId": payload.get("vehicleId") or case.get("externalVehicleRef"),
        "severityCode": payload.get("severityCode") or case.get("severityCode"),
        "evidencePackageReference": payload.get("evidencePackageReference"),
        "advisoryEstimateReference": payload.get("advisoryEstimateReference"),
        "status": IntegrationStatus.SENT,
        "idempotencyKey": idempotency_key,
        "correlationId": correlation_id,
        "createdAt": now,
        "createdBy": principal["id"],
        "updatedAt": now,
    }
    insert = await db.di_maintenance_handoffs.insert_one(handoff_doc)
    handoff_id = str(insert.inserted_id)

    client = MaintenanceClientStub()
    await client.submit_handoff(tenant_id=tenant_id, damage_case_id=case_id, correlation_id=correlation_id)

    data = {"maintenanceHandoffId": handoff_id, "status": IntegrationStatus.SENT, "damageCaseId": case_id,
            "workOrderExecutionOwnedBy": SourceSystemRef.MAINTENANCE}
    await write_audit(
        tenant_id=tenant_id, actor_id=principal["id"], actor_type=ActorType.SERVICE,
        action=AuditAction.MAINTENANCE_HANDOFF_REQUESTED, object_type=ObjectType.MAINTENANCE_HANDOFF,
        object_id=handoff_id, correlation_id=correlation_id, safe_metadata={"damageCaseId": case_id},
    )
    await idempotency_service.store_result(
        tenant_id=tenant_id, idempotency_key=idempotency_key, operation=IntegrationOperation.MAINTENANCE_HANDOFF,
        payload=payload, response_data=data, actor_id=principal["id"], correlation_id=correlation_id,
    )
    return data


async def _store_maintenance_reference(tenant_id: str, case_id: str, ref_doc: dict) -> None:
    db = get_db()
    await db.di_maintenance_references.insert_one({**ref_doc, "tenantId": tenant_id, "damageCaseId": case_id})


async def maintenance_work_order_reference(*, principal: dict, payload: dict, correlation_id: str) -> dict:
    tenant_id = principal["tenantId"]
    case_id = payload.get("damageCaseId")
    work_order_id = payload.get("workOrderId")
    if not case_id or not work_order_id:
        raise DomainError(ErrorCode.VALIDATION_ERROR, "damageCaseId and workOrderId are required.", 400, "workOrderId")
    await _load_case(tenant_id, case_id)
    now = _now()
    await _store_maintenance_reference(tenant_id, case_id, {
        "refType": "WORK_ORDER", "maintenanceRequestId": payload.get("maintenanceRequestId"),
        "workOrderId": work_order_id, "status": payload.get("status") or "WORK_ORDER_CREATED",
        "ownedBy": SourceSystemRef.MAINTENANCE, "correlationId": correlation_id, "createdAt": now,
    })
    await write_audit(
        tenant_id=tenant_id, actor_id=principal["id"], actor_type=ActorType.SERVICE,
        action=AuditAction.MAINTENANCE_WORK_ORDER_REFERENCE_RECEIVED, object_type=ObjectType.DAMAGE_CASE,
        object_id=case_id, correlation_id=correlation_id, safe_metadata={"workOrderId": str(work_order_id)},
    )
    return {"damageCaseId": case_id, "maintenanceRequestId": payload.get("maintenanceRequestId"),
            "workOrderId": work_order_id, "linked": True, "workOrderExecutionOwnedBy": SourceSystemRef.MAINTENANCE}


async def maintenance_repair_status(*, principal: dict, payload: dict, correlation_id: str) -> dict:
    tenant_id = principal["tenantId"]
    case_id = payload.get("damageCaseId")
    repair_status = payload.get("repairStatus")
    if not case_id or not repair_status:
        raise DomainError(ErrorCode.VALIDATION_ERROR, "damageCaseId and repairStatus are required.", 400, "repairStatus")
    await _load_case(tenant_id, case_id)
    db = get_db()
    now = _now()
    await db.di_maintenance_status_updates.insert_one({
        "tenantId": tenant_id, "damageCaseId": case_id, "workOrderId": payload.get("workOrderId"),
        "repairStatus": repair_status,
        "actualRepairCostReference": payload.get("actualRepairCostReference"),  # reference ONLY
        "correlationId": correlation_id, "createdAt": now, "createdBy": principal["id"],
    })
    post_repair_recommended = repair_status in ("REPAIR_COMPLETED", "COMPLETED")
    await write_audit(
        tenant_id=tenant_id, actor_id=principal["id"], actor_type=ActorType.SERVICE,
        action=AuditAction.MAINTENANCE_REPAIR_STATUS_RECEIVED, object_type=ObjectType.DAMAGE_CASE,
        object_id=case_id, correlation_id=correlation_id, safe_metadata={"repairStatus": repair_status},
    )
    return {"damageCaseId": case_id, "repairStatus": repair_status,
            "actualRepairCostOwnedBy": SourceSystemRef.MAINTENANCE,
            "postRepairInspectionRecommended": post_repair_recommended}


async def maintenance_rejection(*, principal: dict, payload: dict, correlation_id: str) -> dict:
    tenant_id = principal["tenantId"]
    case_id = payload.get("damageCaseId")
    rejection_code = payload.get("rejectionCode")
    if not case_id or not rejection_code:
        raise DomainError(ErrorCode.VALIDATION_ERROR, "damageCaseId and rejectionCode are required.", 400, "rejectionCode")
    await _load_case(tenant_id, case_id)
    db = get_db()
    now = _now()
    await db.di_maintenance_references.insert_one({
        "tenantId": tenant_id, "damageCaseId": case_id, "refType": "REJECTION",
        "maintenanceRequestId": payload.get("maintenanceRequestId"),
        "rejectionCode": rejection_code, "rejectionReason": (payload.get("rejectionReason") or "")[:1000],
        "requestedAdditionalEvidence": bool(payload.get("requestedAdditionalEvidence")),
        "correlationId": correlation_id, "createdAt": now,
    })
    # Update the most recent handoff status -> REJECTED (preserves history; case history untouched).
    latest = await db.di_maintenance_handoffs.find_one(
        {"tenantId": tenant_id, "damageCaseId": case_id}, sort=[("createdAt", -1)])
    if latest:
        await db.di_maintenance_handoffs.update_one(
            {"_id": latest["_id"]}, {"$set": {"status": IntegrationStatus.REJECTED, "updatedAt": now}})
    await write_audit(
        tenant_id=tenant_id, actor_id=principal["id"], actor_type=ActorType.SERVICE,
        action=AuditAction.MAINTENANCE_REJECTION_RECEIVED, object_type=ObjectType.DAMAGE_CASE,
        object_id=case_id, correlation_id=correlation_id, safe_metadata={"rejectionCode": rejection_code},
    )
    return {"damageCaseId": case_id, "rejectionCode": rejection_code, "recorded": True}


async def maintenance_additional_evidence_request(*, principal: dict, payload: dict, correlation_id: str) -> dict:
    tenant_id = principal["tenantId"]
    case_id = payload.get("damageCaseId")
    reason = payload.get("reason") or payload.get("rejectionReason")
    if not case_id:
        raise DomainError(ErrorCode.VALIDATION_ERROR, "damageCaseId is required.", 400, "damageCaseId")
    if not reason:
        raise DomainError(ErrorCode.VALIDATION_ERROR, "reason is required.", 400, "reason")
    case = await _load_case(tenant_id, case_id)
    db = get_db()
    now = _now()
    insert = await db.di_additional_evidence_requests.insert_one({
        "tenantId": tenant_id, "reviewItemId": None, "inspectionSessionId": case.get("inspectionSessionId"),
        "objectType": "DAMAGE_CASE", "objectId": case_id, "reason": str(reason)[:1000],
        "requestedPositions": [p for p in (payload.get("requestedPositions") or []) if isinstance(p, str)][:20],
        "source": "MAINTENANCE", "status": "OPEN", "createdAt": now, "createdBy": principal["id"],
        "correlationId": correlation_id,
    })
    await write_audit(
        tenant_id=tenant_id, actor_id=principal["id"], actor_type=ActorType.SERVICE,
        action=AuditAction.MAINTENANCE_ADDITIONAL_EVIDENCE_REQUESTED, object_type=ObjectType.DAMAGE_CASE,
        object_id=case_id, correlation_id=correlation_id, safe_metadata={"requestId": str(insert.inserted_id)},
    )
    return {"additionalEvidenceRequestId": str(insert.inserted_id), "damageCaseId": case_id, "status": "OPEN"}


async def maintenance_handoff_status(*, principal: dict, case_id: str, correlation_id: str) -> dict:
    db = get_db()
    tenant_id = principal["tenantId"]
    await _load_case(tenant_id, case_id)
    handoffs = [h async for h in db.di_maintenance_handoffs.find(
        {"tenantId": tenant_id, "damageCaseId": case_id}).sort("createdAt", -1)]
    refs = [r async for r in db.di_maintenance_references.find(
        {"tenantId": tenant_id, "damageCaseId": case_id}).sort("createdAt", 1)]
    status_updates = [s async for s in db.di_maintenance_status_updates.find(
        {"tenantId": tenant_id, "damageCaseId": case_id}).sort("createdAt", 1)]
    return {
        "damageCaseId": case_id,
        "handoffs": [{"maintenanceHandoffId": str(h["_id"]), "status": h["status"],
                      "createdAt": h["createdAt"].isoformat() if h.get("createdAt") else None} for h in handoffs],
        "references": [{"refType": r.get("refType"), "workOrderId": r.get("workOrderId"),
                        "maintenanceRequestId": r.get("maintenanceRequestId"), "status": r.get("status"),
                        "rejectionCode": r.get("rejectionCode"), "ownedBy": r.get("ownedBy")} for r in refs],
        "repairStatusUpdates": [{"repairStatus": s.get("repairStatus"), "workOrderId": s.get("workOrderId"),
                                 "actualRepairCostReference": s.get("actualRepairCostReference"),
                                 "createdAt": s["createdAt"].isoformat() if s.get("createdAt") else None}
                                for s in status_updates],
        "actualRepairCostOwnedBy": SourceSystemRef.MAINTENANCE,
        "workOrderExecutionOwnedBy": SourceSystemRef.MAINTENANCE,
    }
