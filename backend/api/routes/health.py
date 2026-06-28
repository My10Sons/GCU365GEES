"""
Repository Traceability:
- Source Documents: DI-0034 (GET /health, GET /health/dependencies), DI-SPRINT-00
  (Minimum Backend Endpoints), AC-DI-S00-003 (Health Endpoint Works).
- Purpose: Service and dependency health endpoints. Never exposes secrets.
"""
from fastapi import APIRouter, Request

from api.schemas.envelope import ok
from infrastructure.db.mongo import ping as mongo_ping

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health(request: Request):
    return ok({"status": "ok"}, request.state.correlation_id)


@router.get("/dependencies")
async def health_dependencies(request: Request):
    mongo_ok = await mongo_ping()
    return ok(
        {
            "mongo": {"healthy": mongo_ok},
            "ai_service": {"healthy": True, "mode": "in_process_placeholder"},
            "object_storage": {"healthy": True, "mode": "local_dev"},
        },
        request.state.correlation_id,
    )
