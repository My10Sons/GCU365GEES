"""
Repository Traceability:
- Purpose: Anonymous "Trip Inspection" quick-analysis route. Upload exterior walkaround photos
  by angle (front/rear/left/right/roof) and optionally interior — each as a Before + After pair
  in a SINGLE multipart request. Analyzed with the real Gemini vision engine; returns an
  advisory damage/condition report (with size, repair/replace, cost, photo + integrity checks,
  condition score, cleanliness, and walkaround coverage). Nothing is persisted.
"""
from __future__ import annotations

import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from pydantic import BaseModel

from api.middleware.safe_errors import DomainError
from api.schemas.envelope import ok
from application.security.dependencies import require_permission
from application.services import trip_inspection_service
from domain.enums.error_codes import ErrorCode
from infrastructure.db.mongo import get_db

router = APIRouter(prefix="/trip-inspection", tags=["trip-inspection"])


async def _read(upload: Optional[UploadFile]):
    if upload is None:
        return None
    return (await upload.read(), upload.content_type)


def _client_meta(raw: Optional[str]) -> Optional[dict]:
    if not raw:
        return None
    try:
        v = json.loads(raw)
        return v if isinstance(v, dict) else None
    except ValueError:
        return None


@router.post("/analyze")
async def analyze(
    request: Request,
    ext_front_before: Optional[UploadFile] = File(None),
    ext_front_after: Optional[UploadFile] = File(None),
    ext_rear_before: Optional[UploadFile] = File(None),
    ext_rear_after: Optional[UploadFile] = File(None),
    ext_left_before: Optional[UploadFile] = File(None),
    ext_left_after: Optional[UploadFile] = File(None),
    ext_right_before: Optional[UploadFile] = File(None),
    ext_right_after: Optional[UploadFile] = File(None),
    ext_roof_before: Optional[UploadFile] = File(None),
    ext_roof_after: Optional[UploadFile] = File(None),
    interior_before: Optional[UploadFile] = File(None),
    interior_after: Optional[UploadFile] = File(None),
    customer_name: Optional[str] = Form(None),
    vehicle_plate: Optional[str] = Form(None),
    vehicle_model: Optional[str] = Form(None),
    rental_id: Optional[str] = Form(None),
    inspector_name: Optional[str] = Form(None),
    mode: Optional[str] = Form("fast"),
    principal: dict = Depends(require_permission("di.ai.request")),
):
    raw = {
        "ext_front_before": ext_front_before, "ext_front_after": ext_front_after,
        "ext_rear_before": ext_rear_before, "ext_rear_after": ext_rear_after,
        "ext_left_before": ext_left_before, "ext_left_after": ext_left_after,
        "ext_right_before": ext_right_before, "ext_right_after": ext_right_after,
        "ext_roof_before": ext_roof_before, "ext_roof_after": ext_roof_after,
        "interior_before": interior_before, "interior_after": interior_after,
    }
    files: dict = {}
    for slot, upload in raw.items():
        payload = await _read(upload)
        if payload is not None:
            files[slot] = payload

    report_fields = {
        "customerName": customer_name, "vehiclePlate": vehicle_plate,
        "vehicleModel": vehicle_model, "rentalId": rental_id, "inspectorName": inspector_name,
    }
    data = await trip_inspection_service.analyze_trip(
        principal=principal, files=files, report_fields=report_fields,
        mode=(mode or "fast"), correlation_id=request.state.correlation_id,
    )
    return ok(data, request.state.correlation_id)


@router.post("/analyze-section")
async def analyze_section(
    request: Request,
    kind: str = Form("EXTERIOR"),
    angle: Optional[str] = Form(None),
    mode: Optional[str] = Form("fast"),
    before: UploadFile = File(...),
    after: UploadFile = File(...),
    before_meta: Optional[str] = Form(None),
    after_meta: Optional[str] = Form(None),
    principal: dict = Depends(require_permission("di.ai.request")),
):
    """Analyze a SINGLE before/after pair → returns one section. Used by the streaming UI."""
    data = await trip_inspection_service.analyze_section(
        principal=principal, kind=kind, angle=angle,
        before=await _read(before), after=await _read(after),
        mode=(mode or "fast"), correlation_id=request.state.correlation_id,
        before_meta=_client_meta(before_meta), after_meta=_client_meta(after_meta),
    )
    return ok(data, request.state.correlation_id)


async def _run_section_job(job_id: str, principal: dict, kind: str, angle: Optional[str],
                           mode: str, before, after, before_meta, after_meta,
                           correlation_id: str):
    db = get_db()
    try:
        data = await trip_inspection_service.analyze_section(
            principal=principal, kind=kind, angle=angle, before=before, after=after,
            mode=mode, correlation_id=correlation_id,
            before_meta=before_meta, after_meta=after_meta)
        await db.di_section_jobs.update_one({"jobId": job_id}, {"$set": {
            "status": "DONE", "section": data, "updatedAt": datetime.now(timezone.utc)}})
    except DomainError as exc:
        await db.di_section_jobs.update_one({"jobId": job_id}, {"$set": {
            "status": "FAILED", "error": exc.message,
            "updatedAt": datetime.now(timezone.utc)}})
    except Exception as exc:
        await db.di_section_jobs.update_one({"jobId": job_id}, {"$set": {
            "status": "FAILED", "error": str(exc)[:300],
            "updatedAt": datetime.now(timezone.utc)}})


@router.post("/analyze-section-start")
async def analyze_section_start(
    request: Request,
    kind: str = Form("EXTERIOR"),
    angle: Optional[str] = Form(None),
    mode: Optional[str] = Form("fast"),
    before: UploadFile = File(...),
    after: UploadFile = File(...),
    before_meta: Optional[str] = Form(None),
    after_meta: Optional[str] = Form(None),
    principal: dict = Depends(require_permission("di.ai.request")),
):
    """Async variant of /analyze-section: full analysis (incl. the zoom detail pass) can
    exceed the ingress's 60s request wall, so the UI starts a job and polls for the result."""
    job_id = uuid.uuid4().hex
    now = datetime.now(timezone.utc)
    await get_db().di_section_jobs.insert_one({
        "jobId": job_id, "tenantId": principal["tenantId"], "status": "RUNNING",
        "createdAt": now, "updatedAt": now})
    before_b, after_b = await _read(before), await _read(after)
    asyncio.create_task(_run_section_job(
        job_id, dict(principal), kind, angle, (mode or "fast"), before_b, after_b,
        _client_meta(before_meta), _client_meta(after_meta),
        request.state.correlation_id))
    return ok({"jobId": job_id, "status": "RUNNING"}, request.state.correlation_id)


@router.get("/section-jobs/{job_id}")
async def get_section_job(
    request: Request,
    job_id: str,
    principal: dict = Depends(require_permission("di.ai.request")),
):
    d = await get_db().di_section_jobs.find_one(
        {"jobId": job_id, "tenantId": principal["tenantId"]})
    if not d:
        raise DomainError(ErrorCode.NOT_FOUND, "Section job not found.", 404, "jobId")
    return ok({"jobId": job_id, "status": d["status"], "section": d.get("section"),
               "error": d.get("error")}, request.state.correlation_id)


class FinalizeIn(BaseModel):
    sections: list[dict] = []
    reportFields: Optional[dict] = None
    mode: Optional[str] = "fast"
    saveToVehicleHistory: bool = True
    ocr: Optional[dict] = None


@router.post("/read-plate")
async def read_plate(
    request: Request,
    image: UploadFile = File(...),
    principal: dict = Depends(require_permission("di.ai.request")),
):
    """Dedicated plate/VIN close-up OCR — returns plate (EN/AR), VIN, and basic vehicle info."""
    data = await trip_inspection_service.read_plate(
        principal=principal, image=await _read(image),
        correlation_id=request.state.correlation_id,
    )
    return ok(data, request.state.correlation_id)


@router.post("/finalize")
async def finalize(
    request: Request,
    payload: FinalizeIn,
    principal: dict = Depends(require_permission("di.ai.request")),
):
    """Aggregate streamed sections + run auto-case routing once over the whole set."""
    data = await trip_inspection_service.finalize_trip(
        principal=principal, sections=payload.sections, report_fields=payload.reportFields,
        mode=(payload.mode or "fast"), correlation_id=request.state.correlation_id,
        save_to_history=payload.saveToVehicleHistory, ocr=payload.ocr,
    )
    return ok(data, request.state.correlation_id)


@router.get("/usage")
async def usage(
    request: Request,
    days: int = 30,
    principal: dict = Depends(require_permission("di.reports.read")),
):
    """AI token/call usage aggregated by day, for the admin usage dashboard."""
    data = await trip_inspection_service.usage_summary(principal=principal, days=days)
    return ok(data, request.state.correlation_id)


@router.get("/budget")
async def get_budget(
    request: Request,
    principal: dict = Depends(require_permission("di.reports.read")),
):
    """Lightweight budget status (no daily aggregation) — used for the sidebar alert badge."""
    data = await trip_inspection_service._budget_status(principal["tenantId"])
    return ok(data, request.state.correlation_id)


class BudgetIn(BaseModel):
    monthlyTokenBudget: int = 0
    costPer1kTokens: float = 0


@router.put("/budget")
async def set_budget(
    request: Request,
    payload: BudgetIn,
    principal: dict = Depends(require_permission("di.configuration.manage")),
):
    """Set the tenant's monthly AI token budget (+ optional cost per 1K tokens for SAR estimates)."""
    data = await trip_inspection_service.set_budget(
        principal=principal, monthly_token_budget=payload.monthlyTokenBudget,
        cost_per_1k=payload.costPer1kTokens,
    )
    return ok(data, request.state.correlation_id)


@router.get("/open-rentals")
async def open_rentals(
    request: Request,
    principal: dict = Depends(require_permission("di.ai.request")),
):
    """Rentals pushed by the rental system (CROMS check-out/check-in events) awaiting
    inspection — used to pre-fill the Trip Inspection report fields."""
    cur = get_db().di_open_rentals.find(
        {"tenantId": principal["tenantId"], "status": {"$in": ["CHECKED_OUT", "RETURNED"]}}
    ).sort("updatedAt", -1).limit(20)
    rentals = []
    async for d in cur:
        rentals.append({
            "rentalId": d["rentalId"], "plate": d.get("plate"),
            "customerName": d.get("customerName"), "vehicleModel": d.get("vehicleModel"),
            "status": d["status"], "expectedReturnAt": d.get("expectedReturnAt"),
            "checkedOutAt": d["checkedOutAt"].isoformat() if d.get("checkedOutAt") else None,
            "checkedInAt": d["checkedInAt"].isoformat() if d.get("checkedInAt") else None,
        })
    return ok({"rentals": rentals}, request.state.correlation_id)


@router.post("/open-rentals/{rental_id}/dismiss")
async def dismiss_open_rental(
    request: Request,
    rental_id: str,
    principal: dict = Depends(require_permission("di.ai.request")),
):
    await get_db().di_open_rentals.update_one(
        {"tenantId": principal["tenantId"], "rentalId": rental_id[:60]},
        {"$set": {"status": "DISMISSED"}})
    return ok({"dismissed": True}, request.state.correlation_id)
