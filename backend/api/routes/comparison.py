"""
Repository Traceability:
- Source Documents: DI-SPRINT-03 (Comparison Request/Result APIs), DI-0037 (Per-Vehicle
  Evidence Strip), DI-0006, DI-0034 (paths, envelope, permissions).
- Purpose: REST routes for damage comparison and the per-vehicle evidence strip.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Path, Query, Request
from pydantic import BaseModel, Field

from api.schemas.envelope import ok
from application.security.dependencies import require_permission
from application.services import comparison_service, per_vehicle_service

router = APIRouter(tags=["comparison"])


class ComparisonIn(BaseModel):
    baselineInspectionSessionId: Optional[str] = Field(None, max_length=64)
    comparisonProfileCode: Optional[str] = Field(None, max_length=64)
    routeUncertainToReview: Optional[bool] = None


@router.post("/inspection-sessions/{inspectionSessionId}/comparison")
async def request_comparison(
    request: Request,
    payload: ComparisonIn,
    inspectionSessionId: str = Path(..., min_length=1, max_length=64),
    principal: dict = Depends(require_permission("di.comparison.request")),
):
    data = await comparison_service.request_comparison(
        principal=principal,
        session_id=inspectionSessionId,
        baseline_inspection_session_id=payload.baselineInspectionSessionId,
        comparison_profile_code=payload.comparisonProfileCode,
        route_uncertain_to_review=payload.routeUncertainToReview,
        correlation_id=request.state.correlation_id,
    )
    return ok(data, request.state.correlation_id)


@router.get("/inspection-sessions/{inspectionSessionId}/comparisons")
async def list_comparisons(
    request: Request,
    inspectionSessionId: str = Path(..., min_length=1, max_length=64),
    principal: dict = Depends(require_permission("di.comparison.read")),
):
    data = await comparison_service.list_comparisons(
        principal=principal, session_id=inspectionSessionId,
        correlation_id=request.state.correlation_id,
    )
    return ok(data, request.state.correlation_id)


@router.get("/comparisons/{comparisonId}")
async def get_comparison(
    request: Request,
    comparisonId: str = Path(..., min_length=1, max_length=64),
    principal: dict = Depends(require_permission("di.comparison.read")),
):
    data = await comparison_service.get_comparison(
        principal=principal, comparison_id=comparisonId,
        correlation_id=request.state.correlation_id,
    )
    return ok(data, request.state.correlation_id)


@router.get("/inspection-sessions/{inspectionSessionId}/per-vehicle-strip")
async def per_vehicle_strip(
    request: Request,
    inspectionSessionId: str = Path(..., min_length=1, max_length=64),
    limit: int = Query(12, ge=1, le=50),
    principal: dict = Depends(require_permission("di.images.read")),
):
    data = await per_vehicle_service.per_vehicle_strip(
        principal=principal, session_id=inspectionSessionId, limit=limit,
        correlation_id=request.state.correlation_id,
    )
    return ok(data, request.state.correlation_id)
