"""
Repository Traceability:
- Source Documents: DI-SPRINT-00 (Identity Setup — recommended initial roles),
  DI-0014 (admin/user provisioning baseline).
- Purpose: Idempotent admin/role seed on application startup. Updates the password
  hash if the configured env password changes.
"""
import os
from datetime import datetime, timezone

from application.security.password import hash_password, verify_password
from domain.enums.roles import Role
from infrastructure.db.mongo import get_db
from infrastructure.observability.logging import get_logger, log_event

logger = get_logger("di.seed")


async def _upsert_user(tenant_id: str, email: str, password: str, display_name: str, roles: list[str]) -> None:
    db = get_db()
    email = email.lower().strip()
    existing = await db.di_users.find_one({"tenantId": tenant_id, "email": email})
    now = datetime.now(timezone.utc)
    if existing is None:
        await db.di_users.insert_one(
            {
                "tenantId": tenant_id,
                "email": email,
                "displayName": display_name,
                "roles": roles,
                "status": "ACTIVE",
                "passwordHash": hash_password(password),
                "createdAt": now,
                "updatedAt": now,
                "seeded": True,
            }
        )
        log_event(logger, 20, "Seeded principal", email=email, roles=roles)
        return
    update: dict = {"updatedAt": now}
    if not verify_password(password, existing.get("passwordHash", "")):
        update["passwordHash"] = hash_password(password)
    if existing.get("status") != "ACTIVE":
        update["status"] = "ACTIVE"
    if set(existing.get("roles") or []) != set(roles):
        update["roles"] = roles
    if existing.get("displayName") != display_name:
        update["displayName"] = display_name
    await db.di_users.update_one({"_id": existing["_id"]}, {"$set": update})
    log_event(logger, 20, "Reconciled seeded principal", email=email)


async def seed_baseline_principals() -> None:
    primary_tenant = os.environ.get("DI_SEED_TENANT_ID", "TENANT-000001")
    secondary_tenant = os.environ.get("DI_SEED_TENANT_ID_SECONDARY", "RIYADAH-DOH-001")

    seeds: list[tuple[str, str | None, str | None, str, list[str]]] = [
        # Primary tenant — preserved from Sprint 00 (regression compatibility)
        (primary_tenant,
         os.environ.get("DI_SEED_ADMIN_EMAIL"), os.environ.get("DI_SEED_ADMIN_PASSWORD"),
         "Damage Intelligence Admin", [Role.DI_ADMIN]),
        (primary_tenant,
         os.environ.get("DI_SEED_INSPECTOR_EMAIL"), os.environ.get("DI_SEED_INSPECTOR_PASSWORD"),
         "Field Inspector", [Role.DI_INSPECTOR]),
        (primary_tenant,
         os.environ.get("DI_SEED_REVIEWER_EMAIL"), os.environ.get("DI_SEED_REVIEWER_PASSWORD"),
         "Damage Reviewer", [Role.DI_REVIEWER]),
        # Secondary tenant — Sprint 01 multi-tenant isolation testing (RIYADAH-DOH-001)
        (secondary_tenant,
         os.environ.get("DI_SEED_ADMIN_EMAIL_2"), os.environ.get("DI_SEED_ADMIN_PASSWORD_2"),
         "Riyadah Doha Admin", [Role.DI_ADMIN]),
        (secondary_tenant,
         os.environ.get("DI_SEED_INSPECTOR_EMAIL_2"), os.environ.get("DI_SEED_INSPECTOR_PASSWORD_2"),
         "Riyadah Doha Inspector", [Role.DI_INSPECTOR]),
        # Integration service accounts (Sprint 04) — CROMS / Maintenance service-to-service callers
        (primary_tenant,
         os.environ.get("DI_SEED_INTEGRATION_EMAIL"), os.environ.get("DI_SEED_INTEGRATION_PASSWORD"),
         "Integration Service", [Role.DI_INTEGRATION_SERVICE]),
        (secondary_tenant,
         os.environ.get("DI_SEED_INTEGRATION_EMAIL_2"), os.environ.get("DI_SEED_INTEGRATION_PASSWORD_2"),
         "Riyadah Doha Integration Service", [Role.DI_INTEGRATION_SERVICE]),
    ]
    for tenant_id, email, password, display_name, roles in seeds:
        if not email or not password:
            continue
        await _upsert_user(tenant_id, email, password, display_name, roles)
