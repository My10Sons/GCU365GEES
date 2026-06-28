"""
Repository Traceability:
- Source Documents: DI-SPRINT-05 (Report Generation/Retrieval/Access-Link APIs, Evidence
  Package), DI-0016, DI-0034 (paths, envelope, permissions).
- Purpose: REST routes for damage reports + evidence packages.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Path, Query, Request
from pydantic import BaseModel, Field

from api.schemas.envelope import ok
from application.security.dependencies import require_permission
from application.services import report_service

router = APIRouter(prefix="/reports", tags=["reports"])


class ReportIn(BaseModel):
    reportType: str = Field(..., max_length=64)
    inspectionSessionId: Optional[str] = Field(None, max_length=64)
    damageCaseId: Optional[str] = Field(None, max_length=64)
    rentalAgreementId: Optional[str] = Field(None, max_length=64)
    comparisonId: Optional[str] = Field(None, max_length=64)
    locale: Optional[str] = Field("en", max_length=8)
    format: Optional[str] = Field("JSON", max_length=8)


class AccessLinkIn(BaseModel):
    purpose: Optional[str] = Field(None, max_length=120)


@router.post("")
async def generate_report(
    request: Request, payload: ReportIn,
    principal: dict = Depends(require_permission("di.reports.generate")),
):
    data = await report_service.generate_report(
        principal=principal, report_type=payload.reportType,
        refs={"inspectionSessionId": payload.inspectionSessionId, "damageCaseId": payload.damageCaseId,
              "rentalAgreementId": payload.rentalAgreementId, "comparisonId": payload.comparisonId},
        fmt=payload.format, locale=payload.locale, correlation_id=request.state.correlation_id,
    )
    return ok(data, request.state.correlation_id)


@router.get("")
async def list_reports(
    request: Request,
    reportType: Optional[str] = Query(None),
    page: int = Query(1, ge=1, le=10_000),
    pageSize: int = Query(20, ge=1, le=100),
    principal: dict = Depends(require_permission("di.reports.read")),
):
    data = await report_service.list_reports(
        principal=principal, report_type=reportType, page=page, page_size=pageSize,
        correlation_id=request.state.correlation_id,
    )
    return ok(data, request.state.correlation_id)


@router.get("/{reportId}")
async def get_report(
    request: Request,
    reportId: str = Path(..., min_length=1, max_length=64),
    principal: dict = Depends(require_permission("di.reports.read")),
):
    data = await report_service.get_report(
        principal=principal, report_id=reportId, correlation_id=request.state.correlation_id,
    )
    return ok(data, request.state.correlation_id)


@router.post("/{reportId}/access-link")
async def create_access_link(
    request: Request, payload: AccessLinkIn,
    reportId: str = Path(..., min_length=1, max_length=64),
    principal: dict = Depends(require_permission("di.reports.access")),
):
    data = await report_service.create_access_link(
        principal=principal, report_id=reportId, purpose=payload.purpose,
        correlation_id=request.state.correlation_id,
    )
    return ok(data, request.state.correlation_id)
