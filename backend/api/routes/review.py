"""
Repository Traceability:
- Source Documents: DI-SPRINT-03 (Review Queue, Review Decision, Additional Evidence
  Request APIs), DI-0019, DI-0034 (paths, envelope, permissions).
- Purpose: REST routes for the human review queue.
"""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, Path, Query, Request
from pydantic import BaseModel, Field

from api.schemas.envelope import ok
from application.security.dependencies import require_permission
from application.services import review_service

router = APIRouter(tags=["review"])


class UpdatedFinding(BaseModel):
    damageTypeCode: Optional[str] = Field(None, max_length=64)
    damageType: Optional[str] = Field(None, max_length=64)
    vehicleAreaCode: Optional[str] = Field(None, max_length=64)
    area: Optional[str] = Field(None, max_length=200)
    severityCode: Optional[str] = Field(None, max_length=32)
    severity: Optional[str] = Field(None, max_length=32)


class DecisionIn(BaseModel):
    decisionCode: str = Field(..., max_length=64)
    reason: Optional[str] = Field(None, max_length=1000)
    updatedFinding: Optional[UpdatedFinding] = None


class AdditionalEvidenceIn(BaseModel):
    reason: str = Field(..., min_length=1, max_length=1000)
    requestedPositions: Optional[List[str]] = None


@router.get("/review-queue")
async def list_review_queue(
    request: Request,
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    objectType: Optional[str] = Query(None),
    inspectionSessionId: Optional[str] = Query(None),
    page: int = Query(1, ge=1, le=10_000),
    pageSize: int = Query(20, ge=1, le=100),
    principal: dict = Depends(require_permission("di.review.read")),
):
    data = await review_service.list_review_queue(
        principal=principal, correlation_id=request.state.correlation_id,
        status=status, priority=priority, object_type=objectType,
        inspection_session_id=inspectionSessionId, page=page, page_size=pageSize,
    )
    return ok(data, request.state.correlation_id)


@router.get("/review-items/{reviewItemId}")
async def get_review_item(
    request: Request,
    reviewItemId: str = Path(..., min_length=1, max_length=64),
    principal: dict = Depends(require_permission("di.review.read")),
):
    data = await review_service.get_review_item(
        principal=principal, review_item_id=reviewItemId,
        correlation_id=request.state.correlation_id,
    )
    return ok(data, request.state.correlation_id)


@router.post("/review-items/{reviewItemId}/decision")
async def record_decision(
    request: Request,
    payload: DecisionIn,
    reviewItemId: str = Path(..., min_length=1, max_length=64),
    principal: dict = Depends(require_permission("di.review.decide")),
):
    updated = None
    if payload.updatedFinding is not None:
        uf = payload.updatedFinding
        updated = {
            "damageType": uf.damageType or uf.damageTypeCode,
            "area": uf.area,
            "severity": uf.severity or uf.severityCode,
            "vehicleAreaCode": uf.vehicleAreaCode,
        }
    data = await review_service.record_decision(
        principal=principal, review_item_id=reviewItemId, decision_code=payload.decisionCode,
        reason=payload.reason, updated_finding=updated,
        correlation_id=request.state.correlation_id,
    )
    return ok(data, request.state.correlation_id)


@router.post("/review-items/{reviewItemId}/additional-evidence-request")
async def request_additional_evidence(
    request: Request,
    payload: AdditionalEvidenceIn,
    reviewItemId: str = Path(..., min_length=1, max_length=64),
    principal: dict = Depends(require_permission("di.review.decide")),
):
    data = await review_service.request_additional_evidence(
        principal=principal, review_item_id=reviewItemId, reason=payload.reason,
        requested_positions=payload.requestedPositions,
        correlation_id=request.state.correlation_id,
    )
    return ok(data, request.state.correlation_id)
