"""
Repository Traceability:
- Purpose: Per-tenant branding (company name, branch name, logo) used to brand exported
  Trip Inspection PDF handover reports. Filtered by tenantId. Intended to be provisioned by
  the CROMS / Maintenance system when a tenant is created (PUT /tenant/branding), with a
  demo default seeded at startup.
"""
from __future__ import annotations

import base64
import re
from datetime import datetime, timezone
from typing import Optional

from api.middleware.safe_errors import DomainError
from domain.enums.error_codes import ErrorCode
from infrastructure.db.mongo import get_db

_MAX_LOGO_BYTES = 2 * 1024 * 1024  # 2 MB decoded
_DATA_URL_RE = re.compile(r"^data:image/(png|jpe?g|webp);base64,", re.IGNORECASE)

_DEFAULT = {"companyName": "", "branchName": "", "logoDataUrl": None}


async def get_branding(tenant_id: str) -> dict:
    db = get_db()
    doc = await db.di_tenant_branding.find_one({"tenantId": tenant_id})
    if not doc:
        return dict(_DEFAULT)
    return {
        "companyName": doc.get("companyName") or "",
        "branchName": doc.get("branchName") or "",
        "logoDataUrl": doc.get("logoDataUrl"),
    }


def _validate_logo(logo: Optional[str]) -> Optional[str]:
    if logo is None or logo == "":
        return None
    if not isinstance(logo, str) or not _DATA_URL_RE.match(logo):
        raise DomainError(ErrorCode.VALIDATION_ERROR,
                          "Logo must be a base64 image data URL (png, jpeg, or webp).", 400, "logoDataUrl")
    try:
        raw = base64.b64decode(logo.split(",", 1)[1], validate=True)
    except Exception:
        raise DomainError(ErrorCode.VALIDATION_ERROR, "Logo is not valid base64.", 400, "logoDataUrl")
    if len(raw) > _MAX_LOGO_BYTES:
        raise DomainError(ErrorCode.VALIDATION_ERROR, "Logo exceeds the 2 MB limit.", 400, "logoDataUrl")
    return logo


async def upsert_branding(*, tenant_id: str, company_name: Optional[str],
                          branch_name: Optional[str], logo_data_url: Optional[str]) -> dict:
    db = get_db()
    logo = _validate_logo(logo_data_url)
    now = datetime.now(timezone.utc)
    await db.di_tenant_branding.update_one(
        {"tenantId": tenant_id},
        {"$set": {
            "tenantId": tenant_id,
            "companyName": (company_name or "")[:120],
            "branchName": (branch_name or "")[:120],
            "logoDataUrl": logo,
            "updatedAt": now,
        }, "$setOnInsert": {"createdAt": now}},
        upsert=True,
    )
    return await get_branding(tenant_id)
