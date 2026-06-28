"""
Repository Traceability:
- Source Documents: DI-SPRINT-02 (9 APIs for quality + AI analysis + findings + retry +
  thresholds + per-session quality), DI-0034 (paths, envelope, permissions, advisory note).
- Purpose: REST routes for Sprint 02 image quality + AI advisory damage detection.
"""
from __future__ import annotations

import os
from typing import Optional

from bson import ObjectId
from fastapi import APIRouter, Depends, Path, Request
from pydantic import BaseModel, Field

from api.middleware.safe_errors import DomainError
from api.schemas.envelope import ok
from application.ai.damage_detection_service import retry_analysis, run_analysis_for_session
from application.ai.image_quality_service import assess_image_quality
from application.security.dependencies import get_current_principal, require_permission
from application.services.inspection_service import _load_session_for_tenant
from domain.enums.error_codes import ErrorCode
from infrastructure.db.mongo import get_db

router = APIRouter(tags=["ai"])


def _scrub_id(doc: dict) -> dict:
    if "_id" in doc:
        doc = {**doc, "id": str(doc.pop("_id"))}
    return doc


async def _load_image_for_tenant(tenant_id: str, image_id: str) -> dict:
    db = get_db()
    try:
        oid = ObjectId(image_id)
    except Exception:
        raise DomainError(ErrorCode.NOT_FOUND, "Inspection image not found.", 404, "inspectionImageId")
    img = await db.di_inspection_images.find_one({"_id": oid, "tenantId": tenant_id})
    if img is None:
        raise DomainError(ErrorCode.NOT_FOUND, "Inspection image not found.", 404, "inspectionImageId")
    return img


# -------- 1) POST /images/{inspectionImageId}/quality-check --------

@router.post("/images/{inspectionImageId}/quality-check")
async def image_quality_check(
    request: Request,
    inspectionImageId: str = Path(..., min_length=1, max_length=64),
    principal: dict = Depends(require_permission("di.ai.request")),
):
    img = await _load_image_for_tenant(principal["tenantId"], inspectionImageId)
    result = await assess_image_quality(
        principal=principal, inspection_image=img, correlation_id=request.state.correlation_id
    )
    result = _scrub_id(result)
    return ok(
        {
            "inspectionImageId": result["inspectionImageId"],
            "qualityStatus": result["qualityStatus"],
            "qualityScore": result["qualityScore"],
            "scores": result.get("scores", {}),
            "failureReasons": result.get("failureReasons", []),
            "recaptureRequired": result.get("recaptureRequired", False),
            "recaptureRecommendations": result.get("recaptureRecommendations", []),
            "modelVersion": result["modelVersion"],
            "latencyMs": result.get("latencyMs"),
            "isAdvisory": True,
        },
        request.state.correlation_id,
    )


# -------- 2) GET /images/{inspectionImageId}/quality-result --------

@router.get("/images/{inspectionImageId}/quality-result")
async def image_quality_get(
    request: Request,
    inspectionImageId: str = Path(..., min_length=1, max_length=64),
    principal: dict = Depends(require_permission("di.ai.read")),
):
    img = await _load_image_for_tenant(principal["tenantId"], inspectionImageId)
    db = get_db()
    res = await db.di_image_quality_results.find_one(
        {"tenantId": principal["tenantId"], "inspectionImageId": str(img["_id"])},
        sort=[("createdAt", -1)],
    )
    if res is None:
        return ok(
            {"inspectionImageId": str(img["_id"]), "qualityStatus": "NOT_CHECKED", "isAdvisory": True},
            request.state.correlation_id,
        )
    payload = {
        "id": str(res["_id"]),
        "inspectionImageId": res["inspectionImageId"],
        "inspectionSessionId": res.get("inspectionSessionId"),
        "capturePosition": res.get("capturePosition"),
        "qualityStatus": res["qualityStatus"],
        "qualityScore": res.get("qualityScore", 0.0),
        "scores": res.get("scores", {}),
        "failureReasons": res.get("failureReasons", []),
        "recaptureRequired": res.get("recaptureRequired", False),
        "recaptureRecommendations": res.get("recaptureRecommendations", []),
        "modelVersion": res.get("modelVersion"),
        "latencyMs": res.get("latencyMs"),
        "createdAt": res["createdAt"].isoformat() if res.get("createdAt") else None,
        "isAdvisory": True,
    }
    return ok(payload, request.state.correlation_id)


# -------- 3) POST /inspection-sessions/{id}/quality-check --------

@router.post("/inspection-sessions/{inspectionSessionId}/quality-check")
async def session_quality_check(
    request: Request,
    inspectionSessionId: str = Path(..., min_length=1, max_length=64),
    principal: dict = Depends(require_permission("di.ai.request")),
):
    session = await _load_session_for_tenant(tenant_id=principal["tenantId"], session_id=inspectionSessionId)
    db = get_db()
    imgs = [d async for d in db.di_inspection_images.find(
        {"tenantId": principal["tenantId"], "inspectionSessionId": str(session["_id"])}
    )]
    if not imgs:
        return ok(
            {"inspectionSessionId": str(session["_id"]), "qualityStatus": "NOT_CHECKED",
             "totalImages": 0, "passedImages": 0, "failedImages": 0, "recaptureRequired": False,
             "failedImageIds": []},
            request.state.correlation_id,
        )
    passed = failed = 0
    failed_ids: list[str] = []
    for img in imgs:
        r = await assess_image_quality(principal=principal, inspection_image=img,
                                       correlation_id=request.state.correlation_id)
        if r["qualityStatus"] == "PASSED":
            passed += 1
        elif r["qualityStatus"] in ("FAILED", "ERROR"):
            failed += 1
            failed_ids.append(str(img["_id"]))
    if failed:
        status = "FAILED" if failed == len(imgs) else "WARNING"
    else:
        status = "PASSED"
    return ok(
        {
            "inspectionSessionId": str(session["_id"]),
            "qualityStatus": status,
            "totalImages": len(imgs),
            "passedImages": passed,
            "failedImages": failed,
            "recaptureRequired": failed > 0,
            "failedImageIds": failed_ids,
            "isAdvisory": True,
        },
        request.state.correlation_id,
    )


# -------- 4) POST /inspection-sessions/{id}/ai-analysis --------

@router.post("/inspection-sessions/{inspectionSessionId}/ai-analysis")
async def session_ai_analysis(
    request: Request,
    inspectionSessionId: str = Path(..., min_length=1, max_length=64),
    principal: dict = Depends(require_permission("di.ai.request")),
):
    session = await _load_session_for_tenant(tenant_id=principal["tenantId"], session_id=inspectionSessionId)
    summary = await run_analysis_for_session(
        principal=principal, session=session, correlation_id=request.state.correlation_id
    )
    summary["isAdvisory"] = True
    return ok(summary, request.state.correlation_id)


# -------- 5) GET /ai-analysis/{id} --------

@router.get("/ai-analysis/{aiAnalysisId}")
async def ai_analysis_get(
    request: Request,
    aiAnalysisId: str = Path(..., min_length=1, max_length=64),
    principal: dict = Depends(require_permission("di.ai.read")),
):
    db = get_db()
    try:
        oid = ObjectId(aiAnalysisId)
    except Exception:
        raise DomainError(ErrorCode.NOT_FOUND, "AI analysis not found.", 404, "aiAnalysisId")
    doc = await db.di_ai_analyses.find_one({"_id": oid, "tenantId": principal["tenantId"]})
    if doc is None:
        raise DomainError(ErrorCode.NOT_FOUND, "AI analysis not found.", 404, "aiAnalysisId")
    payload = {
        "id": str(doc["_id"]),
        "tenantId": doc["tenantId"],
        "inspectionSessionId": doc["inspectionSessionId"],
        "status": doc["status"],
        "modelVersion": doc.get("modelVersion"),
        "confidenceThreshold": doc.get("confidenceThreshold"),
        "startedAt": doc["startedAt"].isoformat() if doc.get("startedAt") else None,
        "completedAt": doc["completedAt"].isoformat() if doc.get("completedAt") else None,
        "totalImages": doc.get("totalImages"),
        "totalFindings": doc.get("totalFindings"),
        "totalFailures": doc.get("totalFailures"),
        "totalLatencyMs": doc.get("totalLatencyMs"),
        "error": doc.get("error"),
        "isAdvisory": True,
    }
    return ok(payload, request.state.correlation_id)


def _finding_to_payload(d: dict) -> dict:
    return {
        "id": str(d["_id"]),
        "aiAnalysisId": d["aiAnalysisId"],
        "inspectionSessionId": d["inspectionSessionId"],
        "inspectionImageId": d["inspectionImageId"],
        "capturePosition": d.get("capturePosition"),
        "damageType": d["damageType"],
        "area": d.get("area"),
        "confidence": d["confidence"],
        "severity": d.get("severity"),
        "approximateBoundingBox": d.get("approximateBoundingBox"),
        "status": d["status"],
        "confidenceThreshold": d.get("confidenceThreshold"),
        "modelVersion": d.get("modelVersion"),
        "uncertaintyReason": d.get("uncertaintyReason"),
        "isAdvisory": True,
        "createdAt": d["createdAt"].isoformat() if d.get("createdAt") else None,
    }


# -------- 6) GET /ai-analysis/{id}/findings --------

@router.get("/ai-analysis/{aiAnalysisId}/findings")
async def ai_analysis_findings(
    request: Request,
    aiAnalysisId: str = Path(..., min_length=1, max_length=64),
    principal: dict = Depends(require_permission("di.ai.read")),
):
    db = get_db()
    try:
        oid = ObjectId(aiAnalysisId)
    except Exception:
        raise DomainError(ErrorCode.NOT_FOUND, "AI analysis not found.", 404, "aiAnalysisId")
    analysis = await db.di_ai_analyses.find_one({"_id": oid, "tenantId": principal["tenantId"]})
    if analysis is None:
        raise DomainError(ErrorCode.NOT_FOUND, "AI analysis not found.", 404, "aiAnalysisId")
    cursor = db.di_ai_findings.find(
        {"tenantId": principal["tenantId"], "aiAnalysisId": aiAnalysisId}
    ).sort([("confidence", -1)])
    items = [_finding_to_payload(d) async for d in cursor]
    return ok({"items": items, "total": len(items), "isAdvisory": True}, request.state.correlation_id)


# -------- 7) GET /inspection-sessions/{id}/ai-findings --------

@router.get("/inspection-sessions/{inspectionSessionId}/ai-findings")
async def session_ai_findings(
    request: Request,
    inspectionSessionId: str = Path(..., min_length=1, max_length=64),
    principal: dict = Depends(require_permission("di.ai.read")),
):
    session = await _load_session_for_tenant(tenant_id=principal["tenantId"], session_id=inspectionSessionId)
    db = get_db()
    cursor = db.di_ai_findings.find(
        {"tenantId": principal["tenantId"], "inspectionSessionId": str(session["_id"])}
    ).sort([("createdAt", -1)])
    items = [_finding_to_payload(d) async for d in cursor]
    return ok({"items": items, "total": len(items), "isAdvisory": True}, request.state.correlation_id)


# -------- 8) POST /ai-analysis/{id}/retry --------

@router.post("/ai-analysis/{aiAnalysisId}/retry")
async def ai_analysis_retry(
    request: Request,
    aiAnalysisId: str = Path(..., min_length=1, max_length=64),
    principal: dict = Depends(require_permission("di.ai.request")),
):
    summary = await retry_analysis(
        principal=principal, analysis_id=aiAnalysisId, correlation_id=request.state.correlation_id
    )
    summary["isAdvisory"] = True
    return ok(summary, request.state.correlation_id)


# -------- 9) GET /configuration/ai-thresholds + PUT to update --------

class ThresholdsIn(BaseModel):
    confidenceThreshold: float = Field(..., ge=0.0, le=1.0)
    autoRouteLowConfidence: Optional[bool] = None


@router.get("/configuration/ai-thresholds")
async def get_thresholds(
    request: Request,
    principal: dict = Depends(get_current_principal),
):
    db = get_db()
    cfg = await db.di_ai_configuration.find_one({"tenantId": principal["tenantId"]})
    default = float(os.environ.get("DI_AI_DEFAULT_CONFIDENCE_THRESHOLD", "0.70"))
    auto_route = (cfg or {}).get("autoRouteLowConfidence")
    if not isinstance(auto_route, bool):
        auto_route = True
    return ok(
        {
            "tenantId": principal["tenantId"],
            "confidenceThreshold": (cfg or {}).get("confidenceThreshold", default),
            "autoRouteLowConfidence": auto_route,
            "isTenantOverride": cfg is not None,
            "models": {
                "imageQuality": f"{os.environ.get('DI_AI_MODEL_QUALITY_PROVIDER','gemini')}:{os.environ.get('DI_AI_MODEL_QUALITY_NAME','gemini-3.5-flash')}",
                "damageDetection": f"{os.environ.get('DI_AI_MODEL_DAMAGE_PROVIDER','gemini')}:{os.environ.get('DI_AI_MODEL_DAMAGE_NAME','gemini-3.1-pro-preview')}",
            },
        },
        request.state.correlation_id,
    )


@router.put("/configuration/ai-thresholds")
async def update_thresholds(
    request: Request,
    payload: ThresholdsIn,
    principal: dict = Depends(require_permission("di.configuration.manage")),
):
    db = get_db()
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    set_fields = {"confidenceThreshold": payload.confidenceThreshold, "updatedAt": now,
                  "updatedBy": principal["id"]}
    if payload.autoRouteLowConfidence is not None:
        set_fields["autoRouteLowConfidence"] = payload.autoRouteLowConfidence
    await db.di_ai_configuration.update_one(
        {"tenantId": principal["tenantId"]},
        {"$set": set_fields,
         "$setOnInsert": {"tenantId": principal["tenantId"], "createdAt": now}},
        upsert=True,
    )
    cfg = await db.di_ai_configuration.find_one({"tenantId": principal["tenantId"]})
    return ok(
        {"tenantId": principal["tenantId"], "confidenceThreshold": payload.confidenceThreshold,
         "autoRouteLowConfidence": cfg.get("autoRouteLowConfidence", True),
         "isTenantOverride": True},
        request.state.correlation_id,
    )
