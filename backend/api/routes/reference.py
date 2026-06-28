"""
Repository Traceability:
- Source Document: DI-SPRINT-01 (Capture Positions reference data).
- Purpose: Read-only reference list for the web/mobile client.
"""
from fastapi import APIRouter, Depends, Request

from api.schemas.envelope import ok
from application.security.dependencies import get_current_principal
from infrastructure.db.mongo import get_db

router = APIRouter(prefix="/reference", tags=["reference"])


@router.get("/capture-positions")
async def list_capture_positions(
    request: Request,
    principal: dict = Depends(get_current_principal),
):
    db = get_db()
    cursor = db.di_capture_positions.find({}).sort("order", 1)
    items = []
    async for d in cursor:
        items.append(
            {
                "code": d["code"],
                "label": d["label"],
                "group": d["group"],
                "order": d["order"],
                "required": d.get("required", False),
            }
        )
    return ok({"items": items, "total": len(items)}, request.state.correlation_id)
