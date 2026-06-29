"""
Repository Traceability:
- Purpose: Idempotent demo tenant-branding seed. Provisions a default company name, branch
  name, and logo per tenant so exported Trip Inspection PDF handover reports are branded out
  of the box. Only inserts when branding is absent — never overwrites branding provisioned by
  an admin or the CROMS / Maintenance system.
"""
import os
from datetime import datetime, timezone
from pathlib import Path

from infrastructure.db.mongo import get_db
from infrastructure.observability.logging import get_logger, log_event

logger = get_logger("di.seed")

_LOGO_FILE = Path(__file__).parent / "assets" / "demo_logo_b64.txt"


def _load_demo_logo() -> str | None:
    try:
        text = _LOGO_FILE.read_text().strip()
        return text or None
    except OSError:
        return None


async def seed_tenant_branding() -> None:
    db = get_db()
    primary = os.environ.get("DI_SEED_TENANT_ID", "TENANT-000001")
    secondary = os.environ.get("DI_SEED_TENANT_ID_SECONDARY", "RIYADAH-DOH-001")
    logo = _load_demo_logo()
    defaults = [
        (primary, "Riyadah Technology", "Doha — Main Branch"),
        (secondary, "Riyadah Technology", "Doha — Airport Branch"),
    ]
    now = datetime.now(timezone.utc)
    for tenant_id, company, branch in defaults:
        existing = await db.di_tenant_branding.find_one({"tenantId": tenant_id})
        if existing is not None:
            continue
        await db.di_tenant_branding.insert_one({
            "tenantId": tenant_id,
            "companyName": company,
            "branchName": branch,
            "logoDataUrl": logo,
            "createdAt": now,
            "updatedAt": now,
            "seeded": True,
        })
        log_event(logger, 20, "Seeded tenant branding", tenantId=tenant_id)
