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

from fastapi import (APIRouter, Depends, File, Form, Header, Path, Query,
                     Request, UploadFile)
from pydantic import BaseModel, Field

from api.middleware.safe_errors import DomainError
from api.schemas.envelope import ok
from application.services import (api_key_service, ext_report_service,
                                  trip_inspection_service, vehicle_registry_service)
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
                   mode: str, save_history: bool, correlation_id: str, public_base: str):
    db = get_db()
    try:
        sections, images = [], []
        for slot, kind, angle, before, after in pairs:
            s = await trip_inspection_service.analyze_section(
                principal=principal, kind=kind, angle=angle, before=before, after=after,
                mode=mode, correlation_id=correlation_id)
            sections.append(s)
            images.append({"slot": slot, "before": before, "after": after})
        report_links, token = None, None
        try:
            token = await ext_report_service.create_report(
                tenant_id=principal["tenantId"], job_id=job_id,
                report_fields=report_fields, sections=sections, images=images)
            base = f"{public_base}/api/v1/damage-intelligence/public/reports/{token}"
            report_links = {"reportUrl": base, "reportPdfUrl": f"{base}/pdf"}
        except Exception:
            pass
        result = await trip_inspection_service.finalize_trip(
            principal=principal, sections=sections, report_fields=report_fields,
            mode=mode, correlation_id=correlation_id, save_to_history=save_history,
            report_links=report_links)
        if token:
            try:
                await ext_report_service.attach_result(token, result)
            except Exception:
                pass
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
        pairs.append((name, kind, angle, (await b.read(), b.content_type), (await a.read(), a.content_type)))
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
    scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
    host = request.headers.get("x-forwarded-host", request.headers.get("host", ""))
    asyncio.create_task(_run_job(job_id, principal, pairs, rf,
                                 mode if mode in ("fast", "thorough") else "fast",
                                 bool(save_to_vehicle_history), request.state.correlation_id,
                                 f"{scheme}://{host}"))
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


class RentalEventIn(BaseModel):
    eventType: str = Field(..., max_length=40)
    rentalId: str = Field(..., min_length=1, max_length=60)
    plate: Optional[str] = Field(None, max_length=24)
    customerName: Optional[str] = Field(None, max_length=120)
    vehicleModel: Optional[str] = Field(None, max_length=80)
    expectedReturnAt: Optional[str] = Field(None, max_length=40)
    notes: Optional[str] = Field(None, max_length=300)


_RENTAL_EVENTS = {"rental.checked_out": "CHECKED_OUT", "rental.checked_in": "RETURNED"}


@router.post("/rental-events")
async def push_rental_event(
    request: Request,
    payload: RentalEventIn,
    principal: dict = Depends(require_api_key),
):
    """Inbound push from the rental system (CROMS): check-out/check-in events.
    A check-out opens a pending inspection pre-filled with the rental agreement;
    a check-in marks it as returned — staff see it in the Trip Inspection screen."""
    et = payload.eventType.strip().lower()
    if et not in _RENTAL_EVENTS:
        raise DomainError(ErrorCode.VALIDATION_ERROR,
                          "eventType must be 'rental.checked_out' or 'rental.checked_in'.",
                          400, "eventType")
    now = datetime.now(timezone.utc)
    db = get_db()
    rid = payload.rentalId.strip()[:60]
    await db.di_rental_events.insert_one({
        "tenantId": principal["tenantId"], "apiKeyPrincipal": principal["id"],
        "eventType": et, "rentalId": rid, "plate": payload.plate,
        "customerName": payload.customerName, "vehicleModel": payload.vehicleModel,
        "expectedReturnAt": payload.expectedReturnAt, "notes": payload.notes,
        "receivedAt": now,
    })
    status = _RENTAL_EVENTS[et]
    fields = {"status": status, "updatedAt": now}
    for k, v in (("plate", payload.plate), ("customerName", payload.customerName),
                 ("vehicleModel", payload.vehicleModel),
                 ("expectedReturnAt", payload.expectedReturnAt), ("notes", payload.notes)):
        if v:
            fields[k] = v
    fields["checkedOutAt" if status == "CHECKED_OUT" else "checkedInAt"] = now
    await db.di_open_rentals.update_one(
        {"tenantId": principal["tenantId"], "rentalId": rid},
        {"$set": fields, "$setOnInsert": {"createdAt": now}}, upsert=True)
    return ok({"received": True, "rentalId": rid, "status": status,
               "next": ("Inspection staff will see this rental pre-filled in the "
                        "Trip Inspection screen."
                        if status == "CHECKED_OUT" else
                        "Submit the before/after photos to /trip-inspections with "
                        f'report_fields {{"rentalId": "{rid}"}} to run the analysis.')},
              request.state.correlation_id)


@router.get("/rental-events")
async def list_rental_events(
    request: Request,
    limit: int = Query(20, ge=1, le=100),
    principal: dict = Depends(require_api_key),
):
    cur = get_db().di_rental_events.find(
        {"tenantId": principal["tenantId"]}).sort("receivedAt", -1).limit(limit)
    events = []
    async for d in cur:
        events.append({"eventType": d["eventType"], "rentalId": d["rentalId"],
                       "plate": d.get("plate"), "customerName": d.get("customerName"),
                       "vehicleModel": d.get("vehicleModel"),
                       "receivedAt": d["receivedAt"].isoformat()})
    return ok({"events": events}, request.state.correlation_id)
