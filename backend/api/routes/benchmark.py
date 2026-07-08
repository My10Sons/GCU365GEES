"""
Repository Traceability:
- Purpose: Accuracy benchmark API — manage ground-truth cases (before/after pairs +
  expected findings) and run regression scoring against the live analysis pipeline.
"""
from __future__ import annotations

import json

from fastapi import APIRouter, Depends, File, Form, Query, Request, UploadFile
from pydantic import BaseModel

from api.middleware.safe_errors import DomainError
from api.schemas.envelope import ok
from application.security.dependencies import require_permission
from application.services import benchmark_service
from domain.enums.error_codes import ErrorCode

router = APIRouter(prefix="/benchmark", tags=["benchmark"])


@router.get("/cases")
async def list_cases(
    request: Request,
    principal: dict = Depends(require_permission("di.reports.read")),
):
    data = await benchmark_service.list_cases(principal)
    return ok({"cases": data}, request.state.correlation_id)


@router.post("/cases")
async def create_case(
    request: Request,
    name: str = Form(...),
    angle: str = Form("REAR"),
    expected: str = Form(...),
    before: UploadFile = File(...),
    after: UploadFile = File(...),
    principal: dict = Depends(require_permission("di.configuration.manage")),
):
    try:
        exp = json.loads(expected)
    except ValueError:
        raise DomainError(ErrorCode.VALIDATION_ERROR, "expected must be valid JSON.", 400, "expected")
    data = await benchmark_service.create_case(
        principal=principal, name=name, angle=angle, expected=exp,
        before=(await before.read(), before.content_type),
        after=(await after.read(), after.content_type))
    return ok(data, request.state.correlation_id)


@router.delete("/cases/{case_id}")
async def delete_case(
    request: Request,
    case_id: str,
    principal: dict = Depends(require_permission("di.configuration.manage")),
):
    await benchmark_service.delete_case(principal, case_id)
    return ok({"deleted": True}, request.state.correlation_id)


class RunIn(BaseModel):
    mode: str = "fast"


@router.post("/run")
async def start_run(
    request: Request,
    payload: RunIn,
    principal: dict = Depends(require_permission("di.configuration.manage")),
):
    data = await benchmark_service.start_run(
        principal=principal, mode=payload.mode,
        correlation_id=request.state.correlation_id)
    return ok(data, request.state.correlation_id)


@router.get("/runs")
async def list_runs(
    request: Request,
    limit: int = Query(10, ge=1, le=50),
    principal: dict = Depends(require_permission("di.reports.read")),
):
    data = await benchmark_service.list_runs(principal, limit)
    return ok({"runs": data}, request.state.correlation_id)


@router.get("/runs/{run_id}")
async def get_run(
    request: Request,
    run_id: str,
    principal: dict = Depends(require_permission("di.reports.read")),
):
    data = await benchmark_service.get_run(principal, run_id)
    return ok(data, request.state.correlation_id)
