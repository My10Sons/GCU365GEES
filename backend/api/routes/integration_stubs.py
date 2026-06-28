"""
Repository Traceability:
- Source Document: DI-SPRINT-00 (Integration Stub Setup) — stub endpoints to confirm
  routing only. Real CROMS/Maintenance endpoints are Sprint 04 scope.
- Purpose: Health-only stubs of integration endpoints for Sprint 00 smoke check.
"""
from fastapi import APIRouter, Request

from api.schemas.envelope import ok

router = APIRouter(prefix="/integrations", tags=["integrations (stub)"])


@router.get("/croms/ping")
async def croms_ping(request: Request):
    return ok(
        {
            "system": "GCU365-CROMS",
            "status": "stub",
            "note": "CROMS integration endpoints are wired in Sprint 04 (TASK-05).",
        },
        request.state.correlation_id,
    )


@router.get("/maintenance/ping")
async def maintenance_ping(request: Request):
    return ok(
        {
            "system": "GCU365Maintenance",
            "status": "stub",
            "note": "Maintenance integration endpoints are wired in Sprint 04 (TASK-05).",
        },
        request.state.correlation_id,
    )
