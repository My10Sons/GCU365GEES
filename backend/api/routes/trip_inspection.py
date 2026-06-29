"""
Repository Traceability:
- Purpose: Anonymous "Trip Inspection" quick-analysis routes. Upload a Before + After photo,
  analyze with the real Gemini vision engine, and return an advisory dents/scratches/tyre
  report. Nothing is persisted (images are deleted right after analysis).
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile

from api.schemas.envelope import ok
from application.security.dependencies import require_permission
from application.services import trip_inspection_service

router = APIRouter(prefix="/trip-inspection", tags=["trip-inspection"])


@router.post("/session")
async def create_session(
    request: Request,
    principal: dict = Depends(require_permission("di.ai.request")),
):
    token = trip_inspection_service.new_token()
    return ok({"token": token}, request.state.correlation_id)


@router.post("/upload")
async def upload_slot(
    request: Request,
    token: str = Form(...),
    slot: str = Form(...),
    file: UploadFile = File(...),
    principal: dict = Depends(require_permission("di.ai.request")),
):
    content = await file.read()
    data = await trip_inspection_service.save_slot(
        tenant_id=principal["tenantId"], token=token, slot=slot,
        content=content, content_type=file.content_type,
    )
    return ok(data, request.state.correlation_id)


@router.post("/analyze")
async def analyze(
    request: Request,
    payload: dict,
    principal: dict = Depends(require_permission("di.ai.request")),
):
    token: Optional[str] = (payload or {}).get("token")
    data = await trip_inspection_service.analyze(
        principal=principal, token=str(token or ""), correlation_id=request.state.correlation_id,
    )
    return ok(data, request.state.correlation_id)
