"""
Repository Traceability:
- Source Documents: DI-SPRINT-03 (Damage Case create/get/list/status + link APIs),
  DI-0012, DI-0034 (paths, envelope, permissions).
- Purpose: REST routes for damage cases.
"""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, Path, Query, Request
from pydantic import BaseModel, Field

from api.schemas.envelope import ok
from application.security.dependencies import require_permission
from application.services import damage_case_service
from domain.enums.case_codes import CaseLinkType

router = APIRouter(prefix="/damage-cases", tags=["damage-cases"])


class CreateCaseIn(BaseModel):
    inspectionSessionId: str = Field(..., min_length=1, max_length=64)
    damageFindingIds: Optional[List[str]] = None
    comparisonResultIds: Optional[List[str]] = None
    caseType: str = Field(..., max_length=64)
    severityCode: Optional[str] = Field(None, max_length=32)
    description: Optional[str] = Field(None, max_length=2000)


class StatusIn(BaseModel):
    status: str = Field(..., max_length=64)
    reason: Optional[str] = Field(None, max_length=1000)


class LinkIn(BaseModel):
    linkedId: str = Field(..., min_length=1, max_length=64)


@router.post("")
async def create_case(
    request: Request,
    payload: CreateCaseIn,
    principal: dict = Depends(require_permission("di.damagecases.create")),
):
    data = await damage_case_service.create_case(
        principal=principal, inspection_session_id=payload.inspectionSessionId,
        damage_finding_ids=payload.damageFindingIds or [],
        comparison_result_ids=payload.comparisonResultIds or [],
        case_type=payload.caseType, severity_code=payload.severityCode,
        description=payload.description, correlation_id=request.state.correlation_id,
    )
    return ok(data, request.state.correlation_id)


@router.get("")
async def list_cases(
    request: Request,
    status: Optional[str] = Query(None),
    caseType: Optional[str] = Query(None),
    externalVehicleRef: Optional[str] = Query(None),
    inspectionSessionId: Optional[str] = Query(None),
    page: int = Query(1, ge=1, le=10_000),
    pageSize: int = Query(20, ge=1, le=100),
    principal: dict = Depends(require_permission("di.damagecases.read")),
):
    data = await damage_case_service.list_cases(
        principal=principal, correlation_id=request.state.correlation_id, status=status,
        case_type=caseType, external_vehicle_ref=externalVehicleRef,
        inspection_session_id=inspectionSessionId, page=page, page_size=pageSize,
    )
    return ok(data, request.state.correlation_id)


@router.get("/{damageCaseId}")
async def get_case(
    request: Request,
    damageCaseId: str = Path(..., min_length=1, max_length=64),
    principal: dict = Depends(require_permission("di.damagecases.read")),
):
    data = await damage_case_service.get_case(
        principal=principal, case_id=damageCaseId, correlation_id=request.state.correlation_id,
    )
    return ok(data, request.state.correlation_id)


@router.patch("/{damageCaseId}/status")
async def update_status(
    request: Request,
    payload: StatusIn,
    damageCaseId: str = Path(..., min_length=1, max_length=64),
    principal: dict = Depends(require_permission("di.damagecases.update")),
):
    data = await damage_case_service.update_status(
        principal=principal, case_id=damageCaseId, target_status=payload.status,
        reason=payload.reason, correlation_id=request.state.correlation_id,
    )
    return ok(data, request.state.correlation_id)


async def _link(request: Request, case_id: str, link_type: str, payload: LinkIn, principal: dict):
    data = await damage_case_service.add_link(
        principal=principal, case_id=case_id, link_type=link_type, linked_id=payload.linkedId,
        correlation_id=request.state.correlation_id,
    )
    return ok(data, request.state.correlation_id)


@router.post("/{damageCaseId}/link-evidence")
async def link_evidence(
    request: Request, payload: LinkIn,
    damageCaseId: str = Path(..., min_length=1, max_length=64),
    principal: dict = Depends(require_permission("di.damagecases.update")),
):
    return await _link(request, damageCaseId, CaseLinkType.EVIDENCE, payload, principal)


@router.post("/{damageCaseId}/link-finding")
async def link_finding(
    request: Request, payload: LinkIn,
    damageCaseId: str = Path(..., min_length=1, max_length=64),
    principal: dict = Depends(require_permission("di.damagecases.update")),
):
    return await _link(request, damageCaseId, CaseLinkType.FINDING, payload, principal)


@router.post("/{damageCaseId}/link-comparison")
async def link_comparison(
    request: Request, payload: LinkIn,
    damageCaseId: str = Path(..., min_length=1, max_length=64),
    principal: dict = Depends(require_permission("di.damagecases.update")),
):
    return await _link(request, damageCaseId, CaseLinkType.COMPARISON_RESULT, payload, principal)
