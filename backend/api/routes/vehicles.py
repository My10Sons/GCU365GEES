"""
Repository Traceability:
- Purpose: Vehicle registry read API — list/search vehicles and view a vehicle's
  trip-inspection damage history (populated by Trip Inspection vehicle-linking).
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Path, Query, Request

from api.schemas.envelope import ok
from application.security.dependencies import require_permission
from application.services import vehicle_registry_service

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.get("")
async def list_vehicles(
    request: Request,
    search: str = Query(""),
    principal: dict = Depends(require_permission("di.inspections.read")),
):
    data = await vehicle_registry_service.list_vehicles(principal=principal, search=search)
    return ok(data, request.state.correlation_id)


@router.get("/risk-overview")
async def risk_overview(
    request: Request,
    top: int = Query(5),
    principal: dict = Depends(require_permission("di.inspections.read")),
):
    data = await vehicle_registry_service.risk_overview(principal=principal, top=top)
    return ok(data, request.state.correlation_id)


@router.get("/{vehicle_id}")
async def get_vehicle(
    request: Request,
    vehicle_id: str = Path(...),
    principal: dict = Depends(require_permission("di.inspections.read")),
):
    data = await vehicle_registry_service.get_vehicle(principal=principal, vehicle_id=vehicle_id)
    return ok(data, request.state.correlation_id)
