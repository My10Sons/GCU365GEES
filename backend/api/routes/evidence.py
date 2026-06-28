"""
Repository Traceability:
- Source Documents: DI-SPRINT-01 (Evidence Access Link), DI-0014 (no public URLs,
  time-limited access), DI-0034 (paths, envelope, permissions).
"""
from typing import Optional

from fastapi import APIRouter, Depends, Path, Request
from pydantic import BaseModel, Field

from api.schemas.envelope import ok
from application.security.dependencies import require_permission
from application.services import image_service

router = APIRouter(prefix="/evidence", tags=["evidence"])


class AccessLinkIn(BaseModel):
    purpose: str = Field(..., min_length=1, max_length=200)
    expiresInMinutes: Optional[int] = Field(None, ge=1, le=60)


@router.post("/{evidenceId}/access-link")
async def access_link(
    request: Request,
    payload: AccessLinkIn,
    evidenceId: str = Path(..., min_length=1, max_length=64),
    principal: dict = Depends(require_permission("di.evidence.access")),
):
    data = await image_service.create_evidence_access_link(
        principal=principal,
        evidence_id=evidenceId,
        purpose=payload.purpose,
        expires_in_minutes=payload.expiresInMinutes,
        correlation_id=request.state.correlation_id,
    )
    return ok(data, request.state.correlation_id)
