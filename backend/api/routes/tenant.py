"""
Repository Traceability:
- Purpose: Tenant-level configuration routes. Currently exposes branding (company name,
  branch name, logo) used to brand exported Trip Inspection PDF handover reports. Branding is
  scoped to the caller's tenant (X-Tenant-Id / token tenant). Read requires di.ai.request;
  write requires di.configuration.manage (DI_Admin) — also the path the CROMS / Maintenance
  system uses to provision branding when a tenant is created.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from api.schemas.envelope import ok
from application.security.dependencies import require_permission
from application.services import tenant_branding_service
from application.services import tenant_policy_service
from domain.enums.permissions import Permission

router = APIRouter(prefix="/tenant", tags=["tenant"])


@router.get("/policy")
async def get_policy(
    request: Request,
    principal: dict = Depends(require_permission(Permission.AI_REQUEST)),
):
    data = await tenant_policy_service.get_policy(principal["tenantId"])
    return ok(data, request.state.correlation_id)


@router.put("/policy")
async def put_policy(
    request: Request,
    payload: dict,
    principal: dict = Depends(require_permission(Permission.CONFIGURATION_MANAGE)),
):
    p = payload or {}
    data = await tenant_policy_service.set_policy(
        tenant_id=principal["tenantId"],
        require_full_walkaround=bool(p.get("requireFullWalkaround", False)),
        auto_blur_uploads=bool(p.get("autoBlurUploads", False)),
    )
    return ok(data, request.state.correlation_id)


@router.get("/branding")
async def get_branding(
    request: Request,
    principal: dict = Depends(require_permission(Permission.AI_REQUEST)),
):
    data = await tenant_branding_service.get_branding(principal["tenantId"])
    return ok(data, request.state.correlation_id)


@router.put("/branding")
async def put_branding(
    request: Request,
    payload: dict,
    principal: dict = Depends(require_permission(Permission.CONFIGURATION_MANAGE)),
):
    p = payload or {}
    data = await tenant_branding_service.upsert_branding(
        tenant_id=principal["tenantId"],
        company_name=p.get("companyName"),
        branch_name=p.get("branchName"),
        logo_data_url=p.get("logoDataUrl"),
    )
    return ok(data, request.state.correlation_id)
