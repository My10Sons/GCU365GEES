"""
Repository Traceability:
- Source Documents: DI-SPRINT-00 (Minimum Backend Endpoints).
- Purpose: Service version endpoint.
"""
import os
from fastapi import APIRouter, Request

from api.schemas.envelope import ok

router = APIRouter(prefix="/version", tags=["version"])


@router.get("")
async def version(request: Request):
    return ok(
        {
            "service": os.environ.get("DI_SERVICE_NAME", "damage-intelligence-api"),
            "version": os.environ.get("DI_API_VERSION", "1.0.0"),
            "apiBasePath": "/api/v1/damage-intelligence",
        },
        request.state.correlation_id,
    )
