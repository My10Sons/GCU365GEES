"""
Repository Traceability:
- Purpose: Anonymous "Trip Inspection" quick-analysis route. Upload exterior walkaround photos
  by angle (front/rear/left/right/roof) and optionally interior — each as a Before + After pair
  in a SINGLE multipart request. Analyzed with the real Gemini vision engine; returns an
  advisory damage/condition report (with size, repair/replace, cost, photo + integrity checks,
  condition score, cleanliness, and walkaround coverage). Nothing is persisted.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile

from api.schemas.envelope import ok
from application.security.dependencies import require_permission
from application.services import trip_inspection_service

router = APIRouter(prefix="/trip-inspection", tags=["trip-inspection"])


async def _read(upload: Optional[UploadFile]):
    if upload is None:
        return None
    return (await upload.read(), upload.content_type)


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
        correlation_id=request.state.correlation_id,
    )
    return ok(data, request.state.correlation_id)
