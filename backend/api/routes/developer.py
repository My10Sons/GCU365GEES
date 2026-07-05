"""
Repository Traceability:
- Purpose: JWT-protected Developer/Integrations admin routes: tenant API keys
  (create/list/revoke), rental-system connectors (Generic / Speed Auto / GCU365 CROMS),
  connection tests, and delivery logs. Requires di.configuration.manage.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Path, Query, Request
from fastapi.responses import Response
from pydantic import BaseModel, Field

from api.schemas.envelope import ok
from application.security.dependencies import require_permission
from application.services import api_key_service, connector_service, integration_pack_service

router = APIRouter(prefix="/developer", tags=["developer"])
_admin = require_permission("di.configuration.manage")


class CreateKeyIn(BaseModel):
    label: str = Field("API key", max_length=60)


class ConnectorIn(BaseModel):
    enabled: bool = False
    mode: str = Field("sandbox", max_length=10)
    baseUrl: str = Field("", max_length=300)
    apiKey: Optional[str] = Field(None, max_length=200)
    secret: Optional[str] = Field(None, max_length=200)


@router.get("/api-keys")
async def list_keys(request: Request, principal: dict = Depends(_admin)):
    return ok(await api_key_service.list_keys(principal=principal), request.state.correlation_id)


@router.post("/api-keys")
async def create_key(request: Request, payload: CreateKeyIn, principal: dict = Depends(_admin)):
    data = await api_key_service.create_key(principal=principal, label=payload.label)
    return ok(data, request.state.correlation_id)


@router.post("/api-keys/{key_id}/revoke")
async def revoke_key(request: Request, key_id: str = Path(...), principal: dict = Depends(_admin)):
    data = await api_key_service.revoke_key(principal=principal, key_id=key_id)
    return ok(data, request.state.correlation_id)


@router.get("/connectors")
async def list_connectors(request: Request, principal: dict = Depends(_admin)):
    return ok(await connector_service.list_connectors(principal=principal),
              request.state.correlation_id)


@router.put("/connectors/{ctype}")
async def upsert_connector(request: Request, payload: ConnectorIn,
                           ctype: str = Path(...), principal: dict = Depends(_admin)):
    data = await connector_service.upsert_connector(
        principal=principal, ctype=ctype, enabled=payload.enabled, mode=payload.mode,
        base_url=payload.baseUrl, api_key=payload.apiKey, secret=payload.secret)
    return ok(data, request.state.correlation_id)


@router.post("/connectors/{ctype}/test")
async def test_connector(request: Request, ctype: str = Path(...),
                         principal: dict = Depends(_admin)):
    data = await connector_service.test_connector(principal=principal, ctype=ctype)
    return ok(data, request.state.correlation_id)


@router.get("/usage")
async def usage(request: Request, principal: dict = Depends(_admin)):
    """Per-API-key usage & billing rollup (inspections, tokens, est. cost SAR)."""
    return ok(await api_key_service.usage_summary(principal=principal),
              request.state.correlation_id)


@router.get("/integration-pack/{ctype}")
async def integration_pack(request: Request, ctype: str = Path(...),
                           principal: dict = Depends(_admin)):
    """Downloadable Markdown integration pack for the counterpart developer."""
    scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
    host = request.headers.get("x-forwarded-host", request.headers.get("host", ""))
    fname, md = await integration_pack_service.build_pack(
        principal=principal, ctype=ctype, public_base=f"{scheme}://{host}")
    return Response(content=md, media_type="text/markdown; charset=utf-8",
                    headers={"Content-Disposition": f'attachment; filename="{fname}"'})


@router.get("/deliveries")
async def list_deliveries(request: Request, limit: int = Query(30),
                          principal: dict = Depends(_admin)):
    data = await connector_service.list_deliveries(principal=principal, limit=limit)
    return ok(data, request.state.correlation_id)
