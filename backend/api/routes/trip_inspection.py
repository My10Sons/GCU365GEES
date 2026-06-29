"""
Repository Traceability:
- Purpose: Anonymous "Trip Inspection" quick-analysis route. Upload exterior Before + After
  photos (and optionally interior Before + After) in a SINGLE multipart request, analyze with
  the real Gemini vision engine, and return an advisory damage/condition report. Nothing is
  persisted (images are deleted right after analysis). Single-request design keeps it correct
  behind multi-instance load balancers.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, File, Request, UploadFile

from api.schemas.envelope import ok
from application.security.dependencies import require_permission
from application.services import trip_inspection_service

router = APIRouter(prefix="/trip-inspection", tags=["trip-inspection"])


@router.post("/analyze")
async def analyze(
    request: Request,
    exterior_before: Optional[UploadFile] = File(None),
    exterior_after: Optional[UploadFile] = File(None),
    interior_before: Optional[UploadFile] = File(None),
    interior_after: Optional[UploadFile] = File(None),
    principal: dict = Depends(require_permission("di.ai.request")),
):
    files: dict = {}
    if exterior_before is not None:
        files["exterior_before"] = (await exterior_before.read(), exterior_before.content_type)
    if exterior_after is not None:
        files["exterior_after"] = (await exterior_after.read(), exterior_after.content_type)
    if interior_before is not None:
        files["interior_before"] = (await interior_before.read(), interior_before.content_type)
    if interior_after is not None:
        files["interior_after"] = (await interior_after.read(), interior_after.content_type)

    data = await trip_inspection_service.analyze_trip(
        principal=principal, files=files, correlation_id=request.state.correlation_id,
    )
    return ok(data, request.state.correlation_id)
