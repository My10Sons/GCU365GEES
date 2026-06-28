"""
Repository Traceability:
- Source Documents: DI-SPRINT-02 (AI analysis + findings + statuses + confidence scoring +
  low-confidence routing + model-version tracking), DI-0005, DI-0006, DI-0014, DI-0034.
- Purpose: Per-image and per-session AI advisory damage detection via Gemini.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

from bson import ObjectId

from application.ai.gemini_client import call_vision_model
from application.services.audit_service import write_audit
from domain.enums.ai_codes import (
    AIAnalysisStatus,
    AIFindingStatus,
    ALL_DAMAGE_TYPES,
    ALL_SEVERITIES,
    DamageType,
)
from infrastructure.db.mongo import get_db
from infrastructure.storage.local_storage import storage_root


SYSTEM_MESSAGE = (
    "You are the Damage Intelligence Damage Detector. "
    "Your output is ADVISORY ONLY — you do NOT make liability or charge decisions. "
    "Inspect the vehicle inspection photograph and list any visible damage you can see. "
    "If nothing damage-like is visible, return an empty findings list. "
    "Respond with STRICT JSON only — no prose, no markdown fences."
)

USER_TEMPLATE = (
    "Inspect this vehicle inspection image captured at position '{capture_position}'.\n"
    "Identify any visible damage on the vehicle. Be conservative — if unsure, lower the confidence.\n\n"
    "Return JSON with EXACTLY this shape:\n"
    "{{\n"
    '  "findings": [\n'
    '    {{\n'
    '      "damageType": one of [SCRATCH, DENT, CRACK, BROKEN_PART, PAINT_DAMAGE, RUST, MISSING_PART, OTHER],\n'
    '      "area": short string e.g. "front bumper, driver side",\n'
    '      "confidence": number 0..1,\n'
    '      "severity": one of [LOW, MEDIUM, HIGH] or null,\n'
    '      "approximateBoundingBox": {{ "x": 0..1, "y": 0..1, "width": 0..1, "height": 0..1 }} or null\n'
    "    }}\n"
    "  ],\n"
    '  "uncertaintyReason": short string explaining uncertainty, or null\n'
    "}}\n\n"
    "Do not invent damage. Empty findings list is valid."
)


def _provider() -> str:
    return os.environ.get("DI_AI_MODEL_DAMAGE_PROVIDER", "gemini")


def _model() -> str:
    return os.environ.get("DI_AI_MODEL_DAMAGE_NAME", "gemini-3.1-pro-preview")


def _coerce_bbox(b: dict | None) -> dict | None:
    if not isinstance(b, dict):
        return None
    out = {}
    for k in ("x", "y", "width", "height"):
        try:
            v = float(b.get(k, 0))
        except (TypeError, ValueError):
            return None
        out[k] = max(0.0, min(1.0, v))
    return out


def _normalize_findings(parsed: dict | None) -> tuple[list[dict], str | None, bool]:
    if not isinstance(parsed, dict):
        return [], "model_unparseable", True
    raw = parsed.get("findings")
    if not isinstance(raw, list):
        raw = []
    out: list[dict] = []
    for f in raw[:50]:
        if not isinstance(f, dict):
            continue
        dt = str(f.get("damageType") or "").upper()
        if dt not in ALL_DAMAGE_TYPES:
            dt = DamageType.OTHER
        try:
            conf = float(f.get("confidence") or 0)
        except (TypeError, ValueError):
            conf = 0.0
        conf = max(0.0, min(1.0, conf))
        sev = f.get("severity")
        sev = sev if isinstance(sev, str) and sev.upper() in ALL_SEVERITIES else None
        if isinstance(sev, str):
            sev = sev.upper()
        area = (f.get("area") if isinstance(f.get("area"), str) else "")[:200]
        bbox = _coerce_bbox(f.get("approximateBoundingBox"))
        out.append({"damageType": dt, "area": area, "confidence": conf, "severity": sev, "approximateBoundingBox": bbox})
    uncertainty = parsed.get("uncertaintyReason")
    uncertainty = uncertainty if isinstance(uncertainty, str) else None
    return out, uncertainty, False


def _status_from_confidence(conf: float, threshold: float) -> str:
    if conf < 0.30:
        return AIFindingStatus.UNCERTAIN
    if conf < threshold:
        return AIFindingStatus.LOW_CONFIDENCE
    return AIFindingStatus.AUTO_ACCEPTABLE


async def _load_tenant_threshold(tenant_id: str) -> float:
    db = get_db()
    cfg = await db.di_ai_configuration.find_one({"tenantId": tenant_id})
    if cfg and isinstance(cfg.get("confidenceThreshold"), (int, float)):
        return float(cfg["confidenceThreshold"])
    return float(os.environ.get("DI_AI_DEFAULT_CONFIDENCE_THRESHOLD", "0.70"))


async def run_analysis_for_session(
    *,
    principal: dict,
    session: dict,
    correlation_id: str,
) -> dict:
    db = get_db()
    threshold = await _load_tenant_threshold(principal["tenantId"])
    now = datetime.now(timezone.utc)

    analysis_doc = {
        "tenantId": principal["tenantId"],
        "inspectionSessionId": str(session["_id"]),
        "status": AIAnalysisStatus.PROCESSING,
        "modelVersion": f"{_provider()}:{_model()}",
        "confidenceThreshold": threshold,
        "startedAt": now,
        "createdBy": principal["id"],
        "correlationId": correlation_id,
    }
    insert = await db.di_ai_analyses.insert_one(analysis_doc)
    analysis_id = insert.inserted_id

    images_cursor = db.di_inspection_images.find(
        {"tenantId": principal["tenantId"], "inspectionSessionId": str(session["_id"])}
    )
    images = [d async for d in images_cursor]
    if not images:
        await db.di_ai_analyses.update_one(
            {"_id": analysis_id},
            {"$set": {"status": AIAnalysisStatus.FAILED, "completedAt": datetime.now(timezone.utc),
                      "error": "no_images", "totalImages": 0, "totalFindings": 0}},
        )
        await write_audit(
            tenant_id=principal["tenantId"], actor_id=principal["id"], actor_type="USER",
            action="AI_ANALYSIS_FAILED", object_type="AI_ANALYSIS",
            object_id=str(analysis_id), correlation_id=correlation_id,
            safe_metadata={"reason": "no_images"},
        )
        return {"id": str(analysis_id), "status": AIAnalysisStatus.FAILED, "totalImages": 0, "totalFindings": 0}

    total_findings = 0
    total_failures = 0
    total_latency = 0
    for img in images:
        image_path = str(storage_root() / img["objectPath"])
        if not Path(image_path).exists():
            total_failures += 1
            continue
        prompt = USER_TEMPLATE.format(capture_position=img.get("capturePosition", "UNKNOWN"))
        parsed, model_label, latency_ms, err = await call_vision_model(
            provider=_provider(), model_name=_model(),
            system_message=SYSTEM_MESSAGE, user_prompt=prompt,
            image_path=image_path,
            mime_type=img.get("contentType") or "image/jpeg",
            correlation_id=correlation_id,
        )
        total_latency += latency_ms or 0
        if err is not None:
            total_failures += 1
            continue
        findings, uncertainty, parse_failed = _normalize_findings(parsed)
        if parse_failed:
            total_failures += 1
        for f in findings:
            status = _status_from_confidence(f["confidence"], threshold)
            doc = {
                "tenantId": principal["tenantId"],
                "aiAnalysisId": str(analysis_id),
                "inspectionSessionId": str(session["_id"]),
                "inspectionImageId": str(img["_id"]),
                "capturePosition": img.get("capturePosition"),
                "damageType": f["damageType"],
                "area": f["area"],
                "confidence": f["confidence"],
                "severity": f["severity"],
                "approximateBoundingBox": f["approximateBoundingBox"],
                "status": status,
                "confidenceThreshold": threshold,
                "modelVersion": model_label,
                "uncertaintyReason": uncertainty,
                "isAdvisory": True,
                "createdAt": datetime.now(timezone.utc),
                "correlationId": correlation_id,
            }
            await db.di_ai_findings.insert_one(doc)
            total_findings += 1

    completed_with_warnings = total_failures > 0
    final_status = (AIAnalysisStatus.COMPLETED_WITH_WARNINGS if completed_with_warnings
                    else AIAnalysisStatus.COMPLETED)
    await db.di_ai_analyses.update_one(
        {"_id": analysis_id},
        {"$set": {
            "status": final_status,
            "completedAt": datetime.now(timezone.utc),
            "totalImages": len(images),
            "totalFindings": total_findings,
            "totalFailures": total_failures,
            "totalLatencyMs": total_latency,
        }},
    )
    await write_audit(
        tenant_id=principal["tenantId"], actor_id=principal["id"], actor_type="USER",
        action="AI_ANALYSIS_COMPLETED", object_type="AI_ANALYSIS",
        object_id=str(analysis_id), correlation_id=correlation_id,
        safe_metadata={"status": final_status, "totalImages": len(images), "totalFindings": total_findings,
                       "totalFailures": total_failures, "modelVersion": f"{_provider()}:{_model()}",
                       "confidenceThreshold": threshold},
    )
    return {
        "id": str(analysis_id), "status": final_status,
        "totalImages": len(images), "totalFindings": total_findings,
        "totalFailures": total_failures, "modelVersion": f"{_provider()}:{_model()}",
        "confidenceThreshold": threshold,
    }


async def retry_analysis(*, principal: dict, analysis_id: str, correlation_id: str) -> dict:
    db = get_db()
    try:
        oid = ObjectId(analysis_id)
    except Exception:
        from api.middleware.safe_errors import DomainError
        from domain.enums.error_codes import ErrorCode
        raise DomainError(ErrorCode.NOT_FOUND, "AI analysis not found.", 404, "aiAnalysisId")
    existing = await db.di_ai_analyses.find_one({"_id": oid, "tenantId": principal["tenantId"]})
    if existing is None:
        from api.middleware.safe_errors import DomainError
        from domain.enums.error_codes import ErrorCode
        raise DomainError(ErrorCode.NOT_FOUND, "AI analysis not found.", 404, "aiAnalysisId")
    session = await db.di_inspection_sessions.find_one(
        {"_id": ObjectId(existing["inspectionSessionId"]), "tenantId": principal["tenantId"]}
    )
    if session is None:
        from api.middleware.safe_errors import DomainError
        from domain.enums.error_codes import ErrorCode
        raise DomainError(ErrorCode.NOT_FOUND, "Inspection session not found.", 404)
    # Clear prior findings for this analysis so the retry produces a fresh set.
    await db.di_ai_findings.delete_many({"tenantId": principal["tenantId"], "aiAnalysisId": analysis_id})
    return await run_analysis_for_session(principal=principal, session=session, correlation_id=correlation_id)
