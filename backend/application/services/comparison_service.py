"""
Repository Traceability:
- Source Documents: DI-SPRINT-03 (Damage Comparison Request/Result APIs, baseline
  selection, missing-baseline + NotComparable handling, review routing),
  DI-0006 (Damage Comparison), DI-0014 (tenant isolation), DI-0015 (audit), DI-0034.
- Purpose: Damage-comparison business logic. Real Gemini multimodal vision compares the
  baseline inspection image against the current inspection image per capture position.
  AI output is ADVISORY ONLY.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from bson import ObjectId

from api.middleware.safe_errors import DomainError
from application.ai.gemini_client import call_vision_model_multi
from application.services.audit_service import write_audit
from application.services.inspection_service import _load_session_for_tenant
from domain.enums.ai_codes import ALL_DAMAGE_TYPES, ALL_SEVERITIES, DamageType
from domain.enums.audit_actions import ActorType, AuditAction, ObjectType
from domain.enums.comparison_codes import ComparisonOutcomeCode, ComparisonStatus
from domain.enums.error_codes import ErrorCode
from domain.enums.inspection_status import InspectionStatus
from infrastructure.db.mongo import get_db
from infrastructure.storage.local_storage import storage_root

SYSTEM_MESSAGE = (
    "You are the Damage Intelligence Comparison engine. Your output is ADVISORY ONLY — "
    "you do NOT make liability, charge, or repair-cost decisions. You receive a BASELINE "
    "vehicle photo (earlier inspection) and a CURRENT vehicle photo (later inspection) of "
    "the SAME vehicle at the SAME capture position. Compare them and report damage relative "
    "to the baseline. Respond with STRICT JSON only — no prose, no markdown fences."
)

USER_TEMPLATE = (
    "Capture position: '{capture_position}'.\n"
    "The FIRST image is the BASELINE (earlier). The SECOND image is the CURRENT (later).\n"
    "Compare them and classify each visible damage relative to the baseline. Be conservative.\n\n"
    "Return JSON with EXACTLY this shape:\n"
    "{{\n"
    '  "comparisons": [\n'
    "    {{\n"
    '      "damageType": one of [SCRATCH, DENT, CRACK, BROKEN_PART, PAINT_DAMAGE, RUST, MISSING_PART, OTHER],\n'
    '      "area": short string e.g. "front bumper, driver side",\n'
    '      "comparisonOutcomeCode": one of [NEW, PRE_EXISTING, CHANGED, REPAIRED, UNCERTAIN],\n'
    '      "confidence": number 0..1,\n'
    '      "severity": one of [LOW, MEDIUM, HIGH] or null\n'
    "    }}\n"
    "  ],\n"
    '  "uncertaintyReason": short string explaining uncertainty, or null\n'
    "}}\n\n"
    "NEW = damage present in current but not baseline. PRE_EXISTING = present in both. "
    "CHANGED = present in both but worse/different. REPAIRED = present in baseline but gone now. "
    "If you cannot tell, use UNCERTAIN and lower the confidence. Empty comparisons list is valid."
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _provider() -> str:
    return os.environ.get("DI_AI_MODEL_DAMAGE_PROVIDER", "gemini")


def _model() -> str:
    return os.environ.get("DI_AI_MODEL_DAMAGE_NAME", "gemini-3.1-pro-preview")


async def _tenant_config(tenant_id: str) -> dict:
    db = get_db()
    cfg = await db.di_ai_configuration.find_one({"tenantId": tenant_id}) or {}
    threshold = cfg.get("confidenceThreshold")
    if not isinstance(threshold, (int, float)):
        threshold = float(os.environ.get("DI_AI_DEFAULT_CONFIDENCE_THRESHOLD", "0.70"))
    auto_route = cfg.get("autoRouteLowConfidence")
    if not isinstance(auto_route, bool):
        auto_route = True
    return {"threshold": float(threshold), "autoRoute": auto_route}


def _normalize(parsed: dict | None) -> tuple[list[dict], Optional[str], bool]:
    if not isinstance(parsed, dict):
        return [], "model_unparseable", True
    raw = parsed.get("comparisons")
    if not isinstance(raw, list):
        raw = []
    out: list[dict] = []
    for f in raw[:50]:
        if not isinstance(f, dict):
            continue
        dt = str(f.get("damageType") or "").upper()
        if dt not in ALL_DAMAGE_TYPES:
            dt = DamageType.OTHER
        code = str(f.get("comparisonOutcomeCode") or "").upper()
        if code not in {ComparisonOutcomeCode.NEW, ComparisonOutcomeCode.PRE_EXISTING,
                        ComparisonOutcomeCode.CHANGED, ComparisonOutcomeCode.REPAIRED,
                        ComparisonOutcomeCode.UNCERTAIN}:
            code = ComparisonOutcomeCode.UNCERTAIN
        try:
            conf = max(0.0, min(1.0, float(f.get("confidence") or 0)))
        except (TypeError, ValueError):
            conf = 0.0
        sev = f.get("severity")
        sev = sev.upper() if isinstance(sev, str) and sev.upper() in ALL_SEVERITIES else None
        area = (f.get("area") if isinstance(f.get("area"), str) else "")[:200]
        out.append({"damageType": dt, "area": area, "comparisonOutcomeCode": code,
                    "confidence": conf, "severity": sev})
    uncertainty = parsed.get("uncertaintyReason")
    uncertainty = uncertainty if isinstance(uncertainty, str) else None
    return out, uncertainty, False


async def _select_baseline(*, tenant_id: str, current: dict, explicit_id: Optional[str]) -> tuple[Optional[dict], Optional[str]]:
    db = get_db()
    if explicit_id:
        try:
            oid = ObjectId(explicit_id)
        except Exception:
            raise DomainError(ErrorCode.NOT_FOUND, "Baseline inspection not found.", 404, "baselineInspectionSessionId")
        base = await db.di_inspection_sessions.find_one({"_id": oid, "tenantId": tenant_id})
        if base is None:
            raise DomainError(ErrorCode.NOT_FOUND, "Baseline inspection not found.", 404, "baselineInspectionSessionId")
        if str(base["_id"]) == str(current["_id"]):
            raise DomainError(ErrorCode.VALIDATION_ERROR, "Baseline cannot equal the current inspection.", 400, "baselineInspectionSessionId")
        return base, None
    # Auto-anchor: most recent prior SUBMITTED inspection for the same vehicle (DECISION-Sprint03-a).
    vehicle_ref = (current.get("references") or {}).get("externalVehicleRef")
    if not vehicle_ref:
        return None, "missing_vehicle_reference"
    base = await db.di_inspection_sessions.find_one(
        {
            "tenantId": tenant_id,
            "references.externalVehicleRef": vehicle_ref,
            "status": InspectionStatus.SUBMITTED,
            "_id": {"$ne": current["_id"]},
            "createdAt": {"$lt": current.get("createdAt", _now())},
        },
        sort=[("createdAt", -1)],
    )
    if base is None:
        return None, "no_prior_inspection"
    return base, None


async def _latest_images_by_position(tenant_id: str, session_id: str) -> dict[str, dict]:
    db = get_db()
    by_pos: dict[str, dict] = {}
    cursor = db.di_inspection_images.find(
        {"tenantId": tenant_id, "inspectionSessionId": session_id}
    ).sort("createdAt", -1)
    async for img in cursor:
        pos = img.get("capturePosition") or "UNKNOWN"
        if pos not in by_pos:
            by_pos[pos] = img
    return by_pos


async def request_comparison(
    *,
    principal: dict,
    session_id: str,
    baseline_inspection_session_id: Optional[str],
    comparison_profile_code: Optional[str],
    route_uncertain_to_review: Optional[bool],
    correlation_id: str,
) -> dict:
    db = get_db()
    tenant_id = principal["tenantId"]
    current = await _load_session_for_tenant(tenant_id=tenant_id, session_id=session_id)

    cfg = await _tenant_config(tenant_id)
    route_to_review = cfg["autoRoute"] if route_uncertain_to_review is None else bool(route_uncertain_to_review)
    threshold = cfg["threshold"]

    current_imgs = await _latest_images_by_position(tenant_id, str(current["_id"]))
    if not current_imgs:
        raise DomainError(ErrorCode.VALIDATION_ERROR, "Current inspection has no registered evidence to compare.", 400)

    now = _now()
    base, missing_reason = await _select_baseline(tenant_id=tenant_id, current=current, explicit_id=baseline_inspection_session_id)

    cmp_doc = {
        "tenantId": tenant_id,
        "inspectionSessionId": str(current["_id"]),
        "baselineInspectionSessionId": str(base["_id"]) if base else None,
        "comparisonProfileCode": comparison_profile_code,
        "status": ComparisonStatus.PROCESSING,
        "modelVersion": f"{_provider()}:{_model()}",
        "confidenceThreshold": threshold,
        "routeUncertainToReview": route_to_review,
        "createdAt": now,
        "createdBy": principal["id"],
        "updatedAt": now,
        "updatedBy": principal["id"],
        "correlationId": correlation_id,
    }
    insert = await db.di_damage_comparisons.insert_one(cmp_doc)
    comparison_id = insert.inserted_id

    await write_audit(
        tenant_id=tenant_id, actor_id=principal["id"], actor_type=ActorType.USER,
        action=AuditAction.DAMAGE_COMPARISON_REQUESTED, object_type=ObjectType.DAMAGE_COMPARISON,
        object_id=str(comparison_id), correlation_id=correlation_id,
        safe_metadata={"inspectionSessionId": str(current["_id"]),
                       "baselineInspectionSessionId": str(base["_id"]) if base else None,
                       "auto": baseline_inspection_session_id is None},
    )

    # Missing baseline -> NOT_COMPARABLE (never auto-confirm new damage).
    if base is None:
        await _finalize_not_comparable(comparison_id, tenant_id, missing_reason or "missing_baseline",
                                       principal, route_to_review, str(current["_id"]), correlation_id)
        return await get_comparison(principal=principal, comparison_id=str(comparison_id), correlation_id=correlation_id, audit=False)

    base_imgs = await _latest_images_by_position(tenant_id, str(base["_id"]))
    overlap = [p for p in current_imgs.keys() if p in base_imgs]
    if not overlap:
        await _finalize_not_comparable(comparison_id, tenant_id, "no_overlapping_positions",
                                       principal, route_to_review, str(current["_id"]), correlation_id)
        return await get_comparison(principal=principal, comparison_id=str(comparison_id), correlation_id=correlation_id, audit=False)

    total_pairs = 0
    failed_pairs = 0
    total_results = 0
    total_latency = 0
    review_routed = 0

    for pos in overlap:
        cur_img = current_imgs[pos]
        base_img = base_imgs[pos]
        cur_path = str(storage_root() / cur_img["objectPath"])
        base_path = str(storage_root() / base_img["objectPath"])
        if not Path(cur_path).exists() or not Path(base_path).exists():
            failed_pairs += 1
            continue
        total_pairs += 1
        prompt = USER_TEMPLATE.format(capture_position=pos)
        parsed, model_label, latency_ms, err = await call_vision_model_multi(
            provider=_provider(), model_name=_model(),
            system_message=SYSTEM_MESSAGE, user_prompt=prompt,
            images=[
                {"path": base_path, "mime": base_img.get("contentType") or "image/jpeg"},
                {"path": cur_path, "mime": cur_img.get("contentType") or "image/jpeg"},
            ],
            correlation_id=correlation_id,
        )
        total_latency += latency_ms or 0
        if err is not None:
            failed_pairs += 1
            continue
        results, uncertainty, parse_failed = _normalize(parsed)
        if parse_failed:
            failed_pairs += 1
        for r in results:
            review_required = (
                r["comparisonOutcomeCode"] == ComparisonOutcomeCode.UNCERTAIN
                or r["confidence"] < threshold
                or r["comparisonOutcomeCode"] in (ComparisonOutcomeCode.NEW, ComparisonOutcomeCode.CHANGED)
            )
            res_doc = {
                "tenantId": tenant_id,
                "comparisonId": str(comparison_id),
                "inspectionSessionId": str(current["_id"]),
                "baselineInspectionSessionId": str(base["_id"]),
                "capturePosition": pos,
                "currentInspectionImageId": str(cur_img["_id"]),
                "baselineInspectionImageId": str(base_img["_id"]),
                "damageType": r["damageType"],
                "area": r["area"],
                "comparisonOutcomeCode": r["comparisonOutcomeCode"],
                "confidenceScore": r["confidence"],
                "severity": r["severity"],
                "uncertaintyReason": uncertainty if r["comparisonOutcomeCode"] == ComparisonOutcomeCode.UNCERTAIN else None,
                "reviewRequired": review_required,
                "reviewState": None,
                "confidenceThreshold": threshold,
                "modelVersion": model_label,
                "isAdvisory": True,
                "createdAt": _now(),
                "correlationId": correlation_id,
            }
            res_insert = await db.di_damage_comparison_results.insert_one(res_doc)
            total_results += 1
            if review_required and route_to_review:
                from application.services.review_service import enqueue_review_item
                created = await enqueue_review_item(
                    tenant_id=tenant_id,
                    object_type="COMPARISON_RESULT",
                    object_id=str(res_insert.inserted_id),
                    inspection_session_id=str(current["_id"]),
                    source="COMPARISON",
                    severity_code=r["severity"],
                    priority="HIGH" if r["comparisonOutcomeCode"] in (ComparisonOutcomeCode.NEW, ComparisonOutcomeCode.CHANGED) else "MEDIUM",
                    reason=f"Comparison outcome {r['comparisonOutcomeCode']} requires review.",
                    correlation_id=correlation_id,
                )
                if created:
                    review_routed += 1

    if total_pairs == 0:
        final_status = ComparisonStatus.NOT_COMPARABLE
    elif failed_pairs > 0:
        final_status = ComparisonStatus.COMPLETED_WITH_WARNINGS
    else:
        final_status = ComparisonStatus.COMPLETED

    await db.di_damage_comparisons.update_one(
        {"_id": comparison_id},
        {"$set": {
            "status": final_status, "completedAt": _now(), "updatedAt": _now(),
            "totalPairs": total_pairs, "failedPairs": failed_pairs,
            "totalResults": total_results, "totalLatencyMs": total_latency,
            "reviewItemsRouted": review_routed,
        }},
    )
    await write_audit(
        tenant_id=tenant_id, actor_id=principal["id"], actor_type=ActorType.USER,
        action=AuditAction.DAMAGE_COMPARISON_COMPLETED, object_type=ObjectType.DAMAGE_COMPARISON,
        object_id=str(comparison_id), correlation_id=correlation_id,
        safe_metadata={"status": final_status, "totalPairs": total_pairs, "failedPairs": failed_pairs,
                       "totalResults": total_results, "reviewItemsRouted": review_routed,
                       "modelVersion": f"{_provider()}:{_model()}"},
    )
    return await get_comparison(principal=principal, comparison_id=str(comparison_id), correlation_id=correlation_id, audit=False)


async def _finalize_not_comparable(comparison_id, tenant_id, reason, principal, route_to_review, session_id, correlation_id):
    db = get_db()
    routed = 0
    # Store a single NOT_COMPARABLE result row so the case/review flow can reference it.
    res = await db.di_damage_comparison_results.insert_one({
        "tenantId": tenant_id, "comparisonId": str(comparison_id), "inspectionSessionId": session_id,
        "baselineInspectionSessionId": None, "capturePosition": None,
        "damageType": None, "area": None,
        "comparisonOutcomeCode": ComparisonOutcomeCode.NOT_COMPARABLE,
        "confidenceScore": None, "severity": None, "uncertaintyReason": reason,
        "reviewRequired": True, "reviewState": None, "isAdvisory": True,
        "createdAt": _now(), "correlationId": correlation_id,
    })
    if route_to_review:
        from application.services.review_service import enqueue_review_item
        created = await enqueue_review_item(
            tenant_id=tenant_id, object_type="COMPARISON_RESULT", object_id=str(res.inserted_id),
            inspection_session_id=session_id, source="COMPARISON", severity_code=None,
            priority="MEDIUM", reason=f"NOT_COMPARABLE ({reason}) requires review.",
            correlation_id=correlation_id,
        )
        routed = 1 if created else 0
    await db.di_damage_comparisons.update_one(
        {"_id": comparison_id},
        {"$set": {"status": ComparisonStatus.NOT_COMPARABLE, "completedAt": _now(),
                  "updatedAt": _now(), "notComparableReason": reason,
                  "totalPairs": 0, "totalResults": 1, "reviewItemsRouted": routed}},
    )
    await write_audit(
        tenant_id=tenant_id, actor_id=principal["id"], actor_type=ActorType.USER,
        action=AuditAction.COMPARISON_NOT_COMPARABLE, object_type=ObjectType.DAMAGE_COMPARISON,
        object_id=str(comparison_id), correlation_id=correlation_id,
        safe_metadata={"reason": reason},
    )


def _comparison_to_response(doc: dict, results: list[dict]) -> dict:
    return {
        "comparisonId": str(doc["_id"]),
        "status": doc["status"],
        "currentInspectionSessionId": doc["inspectionSessionId"],
        "baselineInspectionSessionId": doc.get("baselineInspectionSessionId"),
        "comparisonProfileCode": doc.get("comparisonProfileCode"),
        "modelVersion": doc.get("modelVersion"),
        "confidenceThreshold": doc.get("confidenceThreshold"),
        "notComparableReason": doc.get("notComparableReason"),
        "totalPairs": doc.get("totalPairs"),
        "totalResults": doc.get("totalResults"),
        "reviewItemsRouted": doc.get("reviewItemsRouted", 0),
        "createdAt": doc["createdAt"].isoformat() if doc.get("createdAt") else None,
        "completedAt": doc["completedAt"].isoformat() if doc.get("completedAt") else None,
        "isAdvisory": True,
        "outcomes": [_result_to_response(r) for r in results],
    }


def _result_to_response(r: dict) -> dict:
    return {
        "comparisonResultId": str(r["_id"]),
        "capturePosition": r.get("capturePosition"),
        "damageType": r.get("damageType"),
        "area": r.get("area"),
        "comparisonOutcomeCode": r["comparisonOutcomeCode"],
        "confidenceScore": r.get("confidenceScore"),
        "severity": r.get("severity"),
        "uncertaintyReason": r.get("uncertaintyReason"),
        "reviewRequired": r.get("reviewRequired", False),
        "reviewState": r.get("reviewState"),
        "modelVersion": r.get("modelVersion"),
        "isAdvisory": True,
    }


async def get_comparison(*, principal: dict, comparison_id: str, correlation_id: str, audit: bool = True) -> dict:
    db = get_db()
    try:
        oid = ObjectId(comparison_id)
    except Exception:
        raise DomainError(ErrorCode.NOT_FOUND, "Comparison not found.", 404, "comparisonId")
    doc = await db.di_damage_comparisons.find_one({"_id": oid, "tenantId": principal["tenantId"]})
    if doc is None:
        raise DomainError(ErrorCode.NOT_FOUND, "Comparison not found.", 404, "comparisonId")
    results = [r async for r in db.di_damage_comparison_results.find(
        {"tenantId": principal["tenantId"], "comparisonId": comparison_id}
    ).sort("createdAt", 1)]
    return _comparison_to_response(doc, results)


async def list_comparisons(*, principal: dict, session_id: str, correlation_id: str) -> dict:
    db = get_db()
    session = await _load_session_for_tenant(tenant_id=principal["tenantId"], session_id=session_id)
    cursor = db.di_damage_comparisons.find(
        {"tenantId": principal["tenantId"], "inspectionSessionId": str(session["_id"])}
    ).sort("createdAt", -1)
    items = []
    async for d in cursor:
        items.append({
            "comparisonId": str(d["_id"]),
            "status": d["status"],
            "baselineInspectionSessionId": d.get("baselineInspectionSessionId"),
            "totalResults": d.get("totalResults"),
            "modelVersion": d.get("modelVersion"),
            "createdAt": d["createdAt"].isoformat() if d.get("createdAt") else None,
            "completedAt": d["completedAt"].isoformat() if d.get("completedAt") else None,
        })
    return {"items": items, "total": len(items), "isAdvisory": True}
