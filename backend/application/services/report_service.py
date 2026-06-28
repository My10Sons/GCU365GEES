"""
Repository Traceability:
- Source Documents: DI-SPRINT-05 (Reporting scope, Report Generation/Retrieval/Access-Link
  APIs, Evidence Package), DI-0016 (Reporting), DI-0014 (controlled access), DI-0015 (audit), DI-0034.
- Purpose: Production-ready damage reports + evidence packages. Tenant-scoped, authorized,
  controlled time-limited access links (no public URLs). AI outputs labelled advisory; no
  final liability, customer charge, or repair-cost ownership.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from bson import ObjectId

from api.middleware.safe_errors import DomainError
from application.services.audit_service import write_audit
from application.services.inspection_service import _load_session_for_tenant
from domain.enums.audit_actions import ActorType, AuditAction, ObjectType
from domain.enums.error_codes import ErrorCode
from infrastructure.db.mongo import get_db
from infrastructure.storage.local_storage import get_storage_provider, storage_root

REPORT_TYPES = {
    "INSPECTION_SUMMARY_REPORT", "DAMAGE_DETECTION_REPORT", "DAMAGE_COMPARISON_REPORT",
    "DAMAGE_CASE_REPORT", "RENTAL_DAMAGE_SUMMARY_REPORT", "MAINTENANCE_HANDOFF_REPORT",
    "EVIDENCE_PACKAGE_REPORT",
}
ADVISORY_NOTE = ("AI findings are advisory. Damage Intelligence does not own rental closure, "
                 "final customer charge, work order execution, or actual repair cost.")
MAX_ACCESS_LINK_SECONDS = int(os.environ.get("DI_REPORT_ACCESS_MAX_SECONDS", "900"))


def _now() -> datetime:
    return datetime.now(timezone.utc)


async def _oid(value: str, field: str) -> ObjectId:
    try:
        return ObjectId(value)
    except Exception:
        raise DomainError(ErrorCode.NOT_FOUND, f"Referenced {field} not found.", 404, field)


async def _build_content(tenant_id: str, report_type: str, refs: dict) -> dict:
    db = get_db()
    content: dict = {"reportType": report_type, "advisoryNote": ADVISORY_NOTE}

    if report_type in ("INSPECTION_SUMMARY_REPORT", "DAMAGE_DETECTION_REPORT",
                        "DAMAGE_COMPARISON_REPORT", "EVIDENCE_PACKAGE_REPORT"):
        sid = refs.get("inspectionSessionId")
        if not sid:
            raise DomainError(ErrorCode.VALIDATION_ERROR, "inspectionSessionId is required for this report.", 400, "inspectionSessionId")
        session = await _load_session_for_tenant(tenant_id=tenant_id, session_id=sid)
        content["inspection"] = {
            "inspectionSessionId": str(session["_id"]),
            "inspectionType": session.get("inspectionType"),
            "status": session.get("status"),
            "references": session.get("references"),
            "registeredImageCount": session.get("registeredImageCount", 0),
        }
        images = [i async for i in db.di_inspection_images.find(
            {"tenantId": tenant_id, "inspectionSessionId": str(session["_id"])})]
        content["evidence"] = [
            {"inspectionImageId": str(i["_id"]), "capturePosition": i.get("capturePosition"),
             "contentType": i.get("contentType")} for i in images]

        if report_type in ("DAMAGE_DETECTION_REPORT", "EVIDENCE_PACKAGE_REPORT"):
            findings = [f async for f in db.di_ai_findings.find(
                {"tenantId": tenant_id, "inspectionSessionId": str(session["_id"])})]
            content["damageFindings"] = [
                {"damageType": f.get("damageType"), "area": f.get("area"),
                 "confidence": f.get("confidence"), "severity": f.get("severity"),
                 "status": f.get("status"), "reviewState": f.get("reviewState"),
                 "advisory": True} for f in findings]

        if report_type in ("DAMAGE_COMPARISON_REPORT", "EVIDENCE_PACKAGE_REPORT"):
            comparisons = [c async for c in db.di_damage_comparisons.find(
                {"tenantId": tenant_id, "inspectionSessionId": str(session["_id"])}).sort("createdAt", -1)]
            cmp_out = []
            for c in comparisons:
                outcomes = [r async for r in db.di_damage_comparison_results.find(
                    {"tenantId": tenant_id, "comparisonId": str(c["_id"])})]
                cmp_out.append({
                    "comparisonId": str(c["_id"]), "status": c.get("status"),
                    "baselineInspectionSessionId": c.get("baselineInspectionSessionId"),
                    "outcomes": [{"comparisonOutcomeCode": o.get("comparisonOutcomeCode"),
                                  "damageType": o.get("damageType"), "area": o.get("area"),
                                  "confidenceScore": o.get("confidenceScore"),
                                  "reviewState": o.get("reviewState"), "advisory": True} for o in outcomes],
                })
            content["comparisons"] = cmp_out

    if report_type in ("DAMAGE_CASE_REPORT", "MAINTENANCE_HANDOFF_REPORT"):
        cid = refs.get("damageCaseId")
        if not cid:
            raise DomainError(ErrorCode.VALIDATION_ERROR, "damageCaseId is required for this report.", 400, "damageCaseId")
        case = await db.di_damage_cases.find_one({"_id": await _oid(cid, "damageCaseId"), "tenantId": tenant_id})
        if case is None:
            raise DomainError(ErrorCode.NOT_FOUND, "Damage case not found.", 404, "damageCaseId")
        history = [h async for h in db.di_damage_case_status_history.find(
            {"tenantId": tenant_id, "damageCaseId": str(case["_id"])}).sort("timestamp", 1)]
        content["damageCase"] = {
            "damageCaseId": str(case["_id"]), "status": case.get("status"),
            "caseType": case.get("caseType"), "severityCode": case.get("severityCode"),
            "externalVehicleRef": case.get("externalVehicleRef"),
            "inspectionSessionId": case.get("inspectionSessionId"),
            "statusHistory": [{"fromStatus": h.get("fromStatus"), "toStatus": h["toStatus"],
                               "timestamp": h["timestamp"].isoformat() if h.get("timestamp") else None}
                              for h in history],
        }
        content["finalCustomerChargeDecision"] = "NOT_OWNED_BY_DAMAGE_INTELLIGENCE"
        if report_type == "MAINTENANCE_HANDOFF_REPORT":
            handoffs = [h async for h in db.di_maintenance_handoffs.find(
                {"tenantId": tenant_id, "damageCaseId": str(case["_id"])})]
            content["maintenanceHandoffs"] = [{"status": h.get("status")} for h in handoffs]
            content["workOrderExecutionOwnedBy"] = "GCU365Maintenance"
            content["actualRepairCostOwnedBy"] = "GCU365Maintenance"

    if report_type == "RENTAL_DAMAGE_SUMMARY_REPORT":
        ra = refs.get("rentalAgreementId")
        if not ra:
            raise DomainError(ErrorCode.VALIDATION_ERROR, "rentalAgreementId is required for this report.", 400, "rentalAgreementId")
        sessions = [s async for s in db.di_inspection_sessions.find(
            {"tenantId": tenant_id, "references.externalRentalAgreementRef": ra})]
        if not sessions:
            raise DomainError(ErrorCode.NOT_FOUND, "No inspections for this rental agreement.", 404, "rentalAgreementId")
        sids = [str(s["_id"]) for s in sessions]
        content["rentalDamageSummary"] = {
            "rentalAgreementId": ra,
            "inspectionSessionIds": sids,
            "totalFindings": await db.di_ai_findings.count_documents(
                {"tenantId": tenant_id, "inspectionSessionId": {"$in": sids}}),
            "damageCaseIds": [str(c["_id"]) async for c in db.di_damage_cases.find(
                {"tenantId": tenant_id, "inspectionSessionId": {"$in": sids}})],
            "finalCustomerChargeDecision": "NOT_OWNED_BY_DAMAGE_INTELLIGENCE",
        }
    return content


async def generate_report(*, principal: dict, report_type: str, refs: dict, fmt: str, locale: str, correlation_id: str) -> dict:
    tenant_id = principal["tenantId"]
    if report_type not in REPORT_TYPES:
        raise DomainError(ErrorCode.VALIDATION_ERROR, "Unsupported reportType.", 400, "reportType")
    db = get_db()
    try:
        content = await _build_content(tenant_id, report_type, refs)
    except DomainError:
        raise
    except Exception:
        raise DomainError(ErrorCode.REPORT_GENERATION_FAILED, "Report generation failed.", 500)

    now = _now()
    doc = {
        "tenantId": tenant_id, "reportType": report_type, "status": "COMPLETED",
        "format": (fmt or "JSON").upper(), "locale": locale or "en",
        "inspectionSessionId": refs.get("inspectionSessionId"),
        "damageCaseId": refs.get("damageCaseId"),
        "rentalAgreementId": refs.get("rentalAgreementId"),
        "createdAt": now, "createdBy": principal["id"], "correlationId": correlation_id,
        "generatedAt": now.isoformat(),
    }
    insert = await db.di_reports.insert_one(doc)
    report_id = str(insert.inserted_id)

    object_path = f"tenants/{tenant_id}/damage-intelligence/reports/{report_id}.json"
    payload = {"reportId": report_id, "generatedAt": now.isoformat(),
               "correlationId": correlation_id, "tenantId": tenant_id, **content}
    target = storage_root() / object_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    await db.di_reports.update_one({"_id": insert.inserted_id}, {"$set": {"objectPath": object_path}})

    action = (AuditAction.EVIDENCE_PACKAGE_GENERATED if report_type == "EVIDENCE_PACKAGE_REPORT"
              else AuditAction.REPORT_GENERATED)
    await write_audit(
        tenant_id=tenant_id, actor_id=principal["id"], actor_type=ActorType.USER,
        action=action, object_type=ObjectType.REPORT, object_id=report_id,
        correlation_id=correlation_id, safe_metadata={"reportType": report_type},
    )
    return {"reportId": report_id, "status": "COMPLETED", "reportType": report_type,
            "format": doc["format"], "generatedAt": now.isoformat()}


def _report_to_response(d: dict) -> dict:
    return {
        "reportId": str(d["_id"]), "reportType": d.get("reportType"), "status": d.get("status"),
        "format": d.get("format"), "locale": d.get("locale"),
        "inspectionSessionId": d.get("inspectionSessionId"), "damageCaseId": d.get("damageCaseId"),
        "rentalAgreementId": d.get("rentalAgreementId"),
        "generatedAt": d.get("generatedAt"),
        "createdAt": d["createdAt"].isoformat() if d.get("createdAt") else None,
    }


async def get_report(*, principal: dict, report_id: str, correlation_id: str) -> dict:
    db = get_db()
    doc = await db.di_reports.find_one({"_id": await _oid(report_id, "reportId"), "tenantId": principal["tenantId"]})
    if doc is None:
        raise DomainError(ErrorCode.NOT_FOUND, "Report not found.", 404, "reportId")
    await write_audit(
        tenant_id=principal["tenantId"], actor_id=principal["id"], actor_type=ActorType.USER,
        action=AuditAction.REPORT_VIEWED, object_type=ObjectType.REPORT, object_id=str(doc["_id"]),
        correlation_id=correlation_id,
    )
    return _report_to_response(doc)


async def list_reports(*, principal: dict, report_type: Optional[str], page: int, page_size: int, correlation_id: str) -> dict:
    db = get_db()
    page = max(1, page)
    page_size = max(1, min(100, page_size))
    query: dict = {"tenantId": principal["tenantId"]}
    if report_type:
        query["reportType"] = report_type
    total = await db.di_reports.count_documents(query)
    cursor = db.di_reports.find(query).sort("createdAt", -1).skip((page - 1) * page_size).limit(page_size)
    items = [_report_to_response(d) async for d in cursor]
    return {"items": items, "page": page, "pageSize": page_size, "total": total,
            "totalPages": (total + page_size - 1) // page_size if page_size else 1}


async def create_access_link(*, principal: dict, report_id: str, purpose: Optional[str], correlation_id: str) -> dict:
    db = get_db()
    doc = await db.di_reports.find_one({"_id": await _oid(report_id, "reportId"), "tenantId": principal["tenantId"]})
    if doc is None:
        raise DomainError(ErrorCode.NOT_FOUND, "Report not found.", 404, "reportId")
    if not doc.get("objectPath"):
        raise DomainError(ErrorCode.CONFLICT, "Report content is not available.", 409, "reportId")
    provider = get_storage_provider()
    url, expires_at = await provider.make_access_link(doc["objectPath"], MAX_ACCESS_LINK_SECONDS)
    await write_audit(
        tenant_id=principal["tenantId"], actor_id=principal["id"], actor_type=ActorType.USER,
        action=AuditAction.REPORT_ACCESS_LINK_CREATED, object_type=ObjectType.REPORT,
        object_id=str(doc["_id"]), correlation_id=correlation_id,
        safe_metadata={"purpose": (purpose or "")[:120], "expiresInSeconds": MAX_ACCESS_LINK_SECONDS},
    )
    return {"reportId": report_id, "accessUrl": url, "expiresAt": expires_at,
            "expiresInSeconds": MAX_ACCESS_LINK_SECONDS}
