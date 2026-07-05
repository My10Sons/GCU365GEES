"""
Repository Traceability:
- Purpose: Public External API (/ext/v1) for rental systems / mobile apps.
  Auth: X-API-Key (tenant-managed keys). Async trip-inspection jobs + vehicle
  history lookup by plate. Completion fires `inspection.completed` to connectors.
"""
from __future__ import annotations

import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, Header, Path, Request, UploadFile

from api.middleware.safe_errors import DomainError
from api.schemas.envelope import ok
from application.services import (api_key_service, trip_inspection_service,
                                  vehicle_registry_service)
from domain.enums.error_codes import ErrorCode
from infrastructure.db.mongo import get_db

router = APIRouter(prefix="/ext/v1", tags=["external-api"])


async def require_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")) -> dict:
    if not x_api_key:
        raise DomainError(ErrorCode.UNAUTHORIZED, "X-API-Key header required.", 401, "X-API-Key")
    return await api_key_service.resolve_api_key(x_api_key)


def _job_ser(doc: dict) -> dict:
    return {"jobId": doc["jobId"], "status": doc["status"],
            "createdAt": doc["createdAt"].isoformat(),
            "updatedAt": doc["updatedAt"].isoformat(),
            "error": doc.get("error"), "result": doc.get("result")}


async def _run_job(job_id: str, principal: dict, pairs: list, report_fields: dict,
                   mode: str, save_history: bool, correlation_id: str):
    db = get_db()
    try:
        sections = []
        for kind, angle, before, after in pairs:
            s = await trip_inspection_service.analyze_section(
                principal=principal, kind=kind, angle=angle, before=before, after=after,
                mode=mode, correlation_id=correlation_id)
            sections.append(s)
        result = await trip_inspection_service.finalize_trip(
            principal=principal, sections=sections, report_fields=report_fields,
            mode=mode, correlation_id=correlation_id, save_to_history=save_history)
        await db.di_ext_jobs.update_one({"jobId": job_id}, {"$set": {
            "status": "DONE", "result": result, "updatedAt": datetime.now(timezone.utc)}})
    except DomainError as exc:
        await db.di_ext_jobs.update_one({"jobId": job_id}, {"$set": {
            "status": "FAILED", "error": exc.message, "updatedAt": datetime.now(timezone.utc)}})
    except Exception:
        await db.di_ext_jobs.update_one({"jobId": job_id}, {"$set": {
            "status": "FAILED", "error": "Internal analysis error.",
            "updatedAt": datetime.now(timezone.utc)}})


@router.post("/trip-inspections")
async def submit_trip_inspection(
    request: Request,
    mode: str = Form("fast"),
    report_fields: Optional[str] = Form(None),
    save_to_vehicle_history: bool = Form(True),
    before_front: Optional[UploadFile] = File(None), after_front: Optional[UploadFile] = File(None),
    before_rear: Optional[UploadFile] = File(None), after_rear: Optional[UploadFile] = File(None),
    before_left: Optional[UploadFile] = File(None), after_left: Optional[UploadFile] = File(None),
    before_right: Optional[UploadFile] = File(None), after_right: Optional[UploadFile] = File(None),
    before_roof: Optional[UploadFile] = File(None), after_roof: Optional[UploadFile] = File(None),
    before_interior: Optional[UploadFile] = File(None), after_interior: Optional[UploadFile] = File(None),
    principal: dict = Depends(require_api_key),
):
    """Submit BEFORE/AFTER pairs → async analysis job. Poll GET /trip-inspections/{jobId}
    or receive the `inspection.completed` webhook."""
    slots = {"front": (before_front, after_front), "rear": (before_rear, after_rear),
             "left": (before_left, after_left), "right": (before_right, after_right),
             "roof": (before_roof, after_roof), "interior": (before_interior, after_interior)}
    pairs = []
    for name, (b, a) in slots.items():
        if b is None and a is None:
            continue
        if b is None or a is None:
            raise DomainError(ErrorCode.VALIDATION_ERROR,
                              f"Both before_{name} and after_{name} are required.", 400, name)
        kind = "INTERIOR" if name == "interior" else "EXTERIOR"
        angle = None if name == "interior" else name.upper()
        pairs.append((kind, angle, (await b.read(), b.content_type), (await a.read(), a.content_type)))
    if not pairs:
        raise DomainError(ErrorCode.VALIDATION_ERROR,
                          "At least one before/after pair is required "
                          "(e.g. before_front + after_front).", 400)
    rf = {}
    if report_fields:
        try:
            v = json.loads(report_fields)
            rf = v if isinstance(v, dict) else {}
        except ValueError:
            raise DomainError(ErrorCode.VALIDATION_ERROR, "report_fields must be JSON.", 400)
    job_id = uuid.uuid4().hex
    now = datetime.now(timezone.utc)
    await get_db().di_ext_jobs.insert_one({
        "jobId": job_id, "tenantId": principal["tenantId"], "apiKeyPrincipal": principal["id"],
        "status": "RUNNING", "mode": mode if mode in ("fast", "thorough") else "fast",
        "createdAt": now, "updatedAt": now, "result": None, "error": None,
    })
    asyncio.create_task(_run_job(job_id, principal, pairs, rf,
                                 mode if mode in ("fast", "thorough") else "fast",
                                 bool(save_to_vehicle_history), request.state.correlation_id))
    return ok({"jobId": job_id, "status": "RUNNING",
               "poll": f"/api/v1/damage-intelligence/ext/v1/trip-inspections/{job_id}"},
              request.state.correlation_id)


@router.get("/trip-inspections/{job_id}")
async def get_trip_inspection(
    request: Request,
    job_id: str = Path(..., min_length=8, max_length=64),
    principal: dict = Depends(require_api_key),
):
    doc = await get_db().di_ext_jobs.find_one({"jobId": job_id, "tenantId": principal["tenantId"]})
    if not doc:
        raise DomainError(ErrorCode.NOT_FOUND, "Job not found.", 404)
    return ok(_job_ser(doc), request.state.correlation_id)


@router.get("/vehicles/{plate}/history")
async def vehicle_history_by_plate(
    request: Request,
    plate: str = Path(..., min_length=2, max_length=24),
    principal: dict = Depends(require_api_key),
):
    db = get_db()
    v = await db.di_vehicles.find_one({"tenantId": principal["tenantId"],
                                       "plateNormalized": vehicle_registry_service.plate_norm(plate)})
    if not v:
        raise DomainError(ErrorCode.NOT_FOUND, "No vehicle found for that plate.", 404)
    data = await vehicle_registry_service.get_vehicle(principal=principal, vehicle_id=str(v["_id"]))
    return ok(data, request.state.correlation_id)
