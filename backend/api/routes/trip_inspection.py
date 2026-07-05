"""
Repository Traceability:
- Purpose: Anonymous "Trip Inspection" quick-analysis route. Upload exterior walkaround photos
  by angle (front/rear/left/right/roof) and optionally interior — each as a Before + After pair
  in a SINGLE multipart request. Analyzed with the real Gemini vision engine; returns an
  advisory damage/condition report (with size, repair/replace, cost, photo + integrity checks,
  condition score, cleanliness, and walkaround coverage). Nothing is persisted.
"""
from __future__ import annotations

import json
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from pydantic import BaseModel

from api.schemas.envelope import ok
from application.security.dependencies import require_permission
from application.services import trip_inspection_service
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
