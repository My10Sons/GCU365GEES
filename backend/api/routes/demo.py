"""
Repository Traceability:
- Purpose: One-click demo data seeder endpoint (admin-only) for stakeholder walkthroughs.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from api.schemas.envelope import ok
from application.security.dependencies import require_permission
from application.services import demo_service

router = APIRouter(prefix="/demo", tags=["demo"])


@router.post("/seed")
async def seed_demo(
    request: Request,
    principal: dict = Depends(require_permission("di.configuration.manage")),
):
    data = await demo_service.seed_demo(principal=principal, correlation_id=request.state.correlation_id)
    return ok(data, request.state.correlation_id)
