"""
Repository Traceability:
- Source Documents: DI-SPRINT-02 (Image quality validation, recapture recommendation,
  quality result model + statuses + reason codes), DI-0014 (no raw images logged),
  DI-0034 (envelope + audit + correlation).
- Purpose: Per-image AI-assisted quality assessment.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

from application.ai.gemini_client import call_vision_model
from application.services.audit_service import write_audit
from domain.enums.ai_codes import (
    ALL_QUALITY_REASONS,
    QualityReason,
    QualityStatus,
)
from infrastructure.db.mongo import get_db
from infrastructure.storage.local_storage import storage_root


SYSTEM_MESSAGE = (
    "You are the Damage Intelligence Image Quality Assessor. "
    "Your sole job is to evaluate vehicle inspection photographs for technical quality "
    "(blur, lighting, framing, occlusion, angle, vehicle visibility). "
    "You DO NOT detect damage. You DO NOT make liability decisions. "
    "Respond with STRICT JSON only — no prose, no markdown fences."
)

USER_TEMPLATE = (
    "Inspect this vehicle inspection image captured at position '{capture_position}'.\n"
    "Decide whether it is usable for damage detection.\n\n"
    "Return JSON with EXACTLY this shape:\n"
    "{{\n"
    '  "overall": "PASS" | "WARNING" | "FAIL",\n'
    '  "qualityScore": <number between 0 and 1>,\n'
    '  "scores": {{ "blur": 0..1, "lighting": 0..1, "framing": 0..1, "occlusion": 0..1 }},\n'
    '  "failureReasons": [list of zero or more stable codes from this set: '
    'BLURRY_IMAGE, LOW_LIGHT, OVEREXPOSED, OBSTRUCTED_VIEW, LOW_RESOLUTION, INVALID_ANGLE, '
    'VEHICLE_NOT_VISIBLE, UNSUPPORTED_FORMAT, FILE_TOO_LARGE, FILE_TOO_SMALL, '
    'POSSIBLE_DUPLICATE, UNKNOWN_QUALITY_ISSUE],\n'
    '  "recaptureRecommendations": [list of short, plain-English sentences a field inspector '
    'can act on; empty list when overall=PASS]\n'
    "}}\n\n"
    "If you cannot evaluate the image, return overall=FAIL with UNKNOWN_QUALITY_ISSUE."
)


def _provider() -> str:
    return os.environ.get("DI_AI_MODEL_QUALITY_PROVIDER", "gemini")


def _model() -> str:
    return os.environ.get("DI_AI_MODEL_QUALITY_NAME", "gemini-3.5-flash")


def _normalize(parsed: dict | None) -> tuple[str, float, dict, list[str], list[str], str | None]:
    if not isinstance(parsed, dict):
        return (
            QualityStatus.ERROR, 0.0, {}, [QualityReason.UNKNOWN_QUALITY_ISSUE],
            ["AI model returned an unparseable response. Please retake the photograph."],
            "model_unparseable",
        )
    overall_raw = str(parsed.get("overall") or "").upper()
    overall = {
        "PASS": QualityStatus.PASSED,
        "WARNING": QualityStatus.WARNING,
        "FAIL": QualityStatus.FAILED,
    }.get(overall_raw, QualityStatus.WARNING)

    try:
        score = float(parsed.get("qualityScore") or 0.0)
    except (TypeError, ValueError):
        score = 0.0
    score = max(0.0, min(1.0, score))

    scores_raw = parsed.get("scores") or {}
    scores: dict[str, float] = {}
    for k in ("blur", "lighting", "framing", "occlusion"):
        try:
            v = float(scores_raw.get(k, 0.0))
        except (TypeError, ValueError):
            v = 0.0
        scores[k] = max(0.0, min(1.0, v))

    reasons_raw = parsed.get("failureReasons") or []
    reasons: list[str] = []
    for r in reasons_raw if isinstance(reasons_raw, list) else []:
        if isinstance(r, str) and r in ALL_QUALITY_REASONS:
            reasons.append(r)
    # Dedup, preserve order
    reasons = list(dict.fromkeys(reasons))

    recs_raw = parsed.get("recaptureRecommendations") or []
    recs: list[str] = []
    for r in recs_raw if isinstance(recs_raw, list) else []:
        if isinstance(r, str) and r.strip():
            recs.append(r.strip()[:200])
    recs = recs[:6]

    return overall, score, scores, reasons, recs, None


async def assess_image_quality(
    *,
    principal: dict,
    inspection_image: dict,
    correlation_id: str,
) -> dict:
    """
    Runs the image-quality assessment for one registered inspection image.
    Persists a row in di_image_quality_results, updates the image's qualityStatus,
    writes audit + processing-attempt records.
    Returns the result document (without ObjectId).
    """
    db = get_db()
    image_path = str(storage_root() / inspection_image["objectPath"])
    if not Path(image_path).exists():
        result = {
            "tenantId": principal["tenantId"],
            "inspectionSessionId": inspection_image["inspectionSessionId"],
            "inspectionImageId": str(inspection_image["_id"]),
            "qualityStatus": QualityStatus.ERROR,
            "qualityScore": 0.0,
            "scores": {},
            "failureReasons": [QualityReason.UNKNOWN_QUALITY_ISSUE],
            "recaptureRequired": True,
            "recaptureRecommendations": ["Underlying image object is missing — recapture required."],
            "modelVersion": "n/a",
            "latencyMs": 0,
            "createdAt": datetime.now(timezone.utc),
            "createdBy": principal["id"],
            "correlationId": correlation_id,
        }
        await db.di_image_quality_results.insert_one(result)
        await write_audit(
            tenant_id=principal["tenantId"], actor_id=principal["id"], actor_type="USER",
            action="QUALITY_CHECK_ERROR", object_type="INSPECTION_IMAGE",
            object_id=str(inspection_image["_id"]),
            correlation_id=correlation_id,
            safe_metadata={"reason": "image_object_missing"},
        )
        result.pop("_id", None)
        return result

    mime = inspection_image.get("contentType") or "image/jpeg"
    prompt = USER_TEMPLATE.format(capture_position=inspection_image.get("capturePosition", "UNKNOWN"))
    parsed, model_label, latency_ms, err = await call_vision_model(
        provider=_provider(),
        model_name=_model(),
        system_message=SYSTEM_MESSAGE,
        user_prompt=prompt,
        image_path=image_path,
        mime_type=mime,
        correlation_id=correlation_id,
    )
    overall, score, scores, reasons, recs, parse_err = _normalize(parsed)
    if err is not None:
        # Hard failure path: ensure ERROR status + readable rec.
        overall = QualityStatus.ERROR
        if not recs:
            recs = ["AI quality check failed. Please retry."]
        if QualityReason.UNKNOWN_QUALITY_ISSUE not in reasons:
            reasons.append(QualityReason.UNKNOWN_QUALITY_ISSUE)

    recapture = overall in (QualityStatus.FAILED, QualityStatus.ERROR)
    now = datetime.now(timezone.utc)
    result = {
        "tenantId": principal["tenantId"],
        "inspectionSessionId": inspection_image["inspectionSessionId"],
        "inspectionImageId": str(inspection_image["_id"]),
        "capturePosition": inspection_image.get("capturePosition"),
        "qualityStatus": overall,
        "qualityScore": score,
        "scores": scores,
        "failureReasons": reasons,
        "recaptureRequired": recapture,
        "recaptureRecommendations": recs,
        "modelVersion": model_label,
        "latencyMs": latency_ms,
        "error": err or parse_err,
        "createdAt": now,
        "createdBy": principal["id"],
        "correlationId": correlation_id,
    }
    insert = await db.di_image_quality_results.insert_one(result)
    result["_id"] = insert.inserted_id

    # Update image with latest quality status (denormalized for fast list rendering).
    await db.di_inspection_images.update_one(
        {"_id": inspection_image["_id"], "tenantId": principal["tenantId"]},
        {"$set": {"qualityStatus": overall, "qualityScore": score, "lastQualityCheckAt": now}},
    )

    await write_audit(
        tenant_id=principal["tenantId"], actor_id=principal["id"], actor_type="USER",
        action="QUALITY_CHECK_COMPLETED", object_type="INSPECTION_IMAGE",
        object_id=str(inspection_image["_id"]),
        correlation_id=correlation_id,
        safe_metadata={
            "qualityStatus": overall, "qualityScore": score, "modelVersion": model_label,
            "latencyMs": latency_ms, "reasonCount": len(reasons),
        },
    )
    return result
