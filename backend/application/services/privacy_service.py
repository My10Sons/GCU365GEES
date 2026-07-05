"""
Repository Traceability:
- Purpose: PDPL/GDPR privacy blurring for persisted evidence images. Detects human
  faces and BYSTANDER vehicle plates (the subject vehicle's own plate is kept for
  OCR/linking) via Gemini, then Gaussian-blurs those regions in place with Pillow.
  Used automatically at image registration (tenant policy `autoBlurUploads`) and
  on demand via POST /evidence/{id}/blur.
"""
from __future__ import annotations

import os

from bson import ObjectId
from PIL import Image, ImageFilter

from api.middleware.safe_errors import DomainError
from application.ai.gemini_client import call_vision_model_multi
from domain.enums.error_codes import ErrorCode
from infrastructure.db.mongo import get_db
from infrastructure.storage.local_storage import storage_root

_SYSTEM = ("You are a privacy-compliance vision agent. You locate regions that must be "
           "blurred in vehicle-inspection photos. Respond with STRICT JSON only.")
_PROMPT = (
    "Find every region in this photo that must be blurred for privacy compliance:\n"
    "1. Human faces (anyone visible).\n"
    "2. License plates of BACKGROUND/BYSTANDER vehicles only — NOT the main subject "
    "vehicle being inspected. The subject vehicle is the one filling most of the frame.\n"
    "Return JSON EXACTLY: {\"regions\": [{\"kind\": \"face\" or \"plate\", "
    "\"box_2d\": [ymin, xmin, ymax, xmax] with coordinates normalized 0-1000, "
    "\"subjectVehicle\": true or false (plates only)}]}\n"
    "If nothing needs blurring return {\"regions\": []}."
)


def _blur_regions(path: str, regions: list[dict]) -> int:
    with Image.open(path) as im:
        im = im.convert("RGB")
        w, h = im.size
        count = 0
        for r in regions:
            box = r.get("box_2d") or r.get("box")
            if not (isinstance(box, list) and len(box) == 4):
                continue
            if r.get("kind") == "plate" and r.get("subjectVehicle"):
                continue
            try:
                y0, x0, y1, x1 = (float(v) for v in box)
            except (TypeError, ValueError):
                continue
            px = (max(0, int(x0 / 1000 * w)), max(0, int(y0 / 1000 * h)),
                  min(w, int(x1 / 1000 * w)), min(h, int(y1 / 1000 * h)))
            if px[2] - px[0] < 4 or px[3] - px[1] < 4:
                continue
            region = im.crop(px).filter(ImageFilter.GaussianBlur(radius=max(8, (px[2] - px[0]) // 6)))
            im.paste(region, px)
            count += 1
        if count:
            im.save(path, format="JPEG", quality=90)
    return count


async def blur_file(path: str, correlation_id: str) -> dict:
    if not os.path.exists(path):
        raise DomainError(ErrorCode.NOT_FOUND, "Stored image file not found.", 404)
    parsed, model_label, _lat, err, _usage = await call_vision_model_multi(
        provider=os.environ.get("DI_AI_MODEL_QUALITY_PROVIDER", "gemini"),
        model_name=os.environ.get("DI_AI_MODEL_DAMAGE_FAST_NAME", "gemini-3.5-flash"),
        system_message=_SYSTEM, user_prompt=_PROMPT,
        images=[{"path": path, "mime": "image/jpeg"}], correlation_id=correlation_id,
    )
    if err is not None:
        raise DomainError(ErrorCode.INTERNAL_ERROR, "Privacy detection unavailable. Retry.", 503)
    regions = (parsed or {}).get("regions") if isinstance(parsed, dict) else []
    regions = regions if isinstance(regions, list) else []
    blurred = _blur_regions(path, regions)
    return {"regionsDetected": len(regions), "regionsBlurred": blurred, "model": model_label}


async def blur_evidence_image(*, principal: dict, evidence_id: str, correlation_id: str) -> dict:
    db = get_db()
    try:
        oid = ObjectId(evidence_id)
    except Exception:
        raise DomainError(ErrorCode.VALIDATION_ERROR, "Invalid evidence id.", 400, "evidenceId")
    img = await db.di_inspection_images.find_one({"_id": oid, "tenantId": principal["tenantId"]})
    if img is None:
        ev = await db.di_evidence_references.find_one({"_id": oid, "tenantId": principal["tenantId"]})
        img = ev
    if img is None or not img.get("objectPath"):
        raise DomainError(ErrorCode.NOT_FOUND, "Evidence image not found.", 404)
    result = await blur_file(str(storage_root() / img["objectPath"]), correlation_id)
    await db.di_inspection_images.update_one(
        {"objectPath": img["objectPath"], "tenantId": principal["tenantId"]},
        {"$set": {"privacyBlurred": True, "privacyBlurInfo": result}})
    return {"evidenceId": evidence_id, **result, "privacyBlurred": True}
