"""
Repository Traceability:
- Source Documents: DI-SPRINT-05 (Monitoring dashboards + metrics, dependency health),
  DI-0023, DI-0034.
- Purpose: Tenant-scoped operational metrics for the operator dashboard.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from api.schemas.envelope import ok
from application.security.dependencies import get_current_principal
from application.services import monitoring_service

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.get("/metrics")
async def metrics(request: Request, principal: dict = Depends(get_current_principal)):
    data = await monitoring_service.metrics(principal=principal, correlation_id=request.state.correlation_id)
    return ok(data, request.state.correlation_id)


@router.get("/dependencies")
async def dependencies(request: Request, principal: dict = Depends(get_current_principal)):
    data = await monitoring_service.dependency_health()
    return ok(data, request.state.correlation_id)
