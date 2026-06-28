"""
Repository Traceability:
- Source Documents: DI-SPRINT-00 (Database Setup — migration baseline),
  DI-0014 (tenant-scoped indexes), DI-0015 (audit indexes),
  DI-0034 (login_attempts brute-force store, idempotency records)
- Purpose: Idempotent index creation invoked at startup. Sprint 00 baseline only.
"""
from motor.motor_asyncio import AsyncIOMotorDatabase


async def ensure_indexes(db: AsyncIOMotorDatabase) -> None:
    # --- Schema version (Sprint 00 baseline) ---
    await db.di_schema_version.create_index("version", unique=True)

    # --- System health probes (Sprint 00 baseline) ---
    await db.di_system_health_check.create_index("checkedAt")

    # --- Users (auth baseline) ---
    await db.di_users.create_index([("tenantId", 1), ("email", 1)], unique=True)
    await db.di_users.create_index("email")

    # --- Login attempts (brute-force defence) ---
    await db.di_login_attempts.create_index("identifier")
    await db.di_login_attempts.create_index("lastAttemptAt")

    # --- Audit records (DI-0015) ---
    await db.di_audit_records.create_index([("tenantId", 1), ("objectType", 1), ("objectId", 1)])
    await db.di_audit_records.create_index([("tenantId", 1), ("timestamp", -1)])
    await db.di_audit_records.create_index("correlationId")

    # --- Idempotency records (DI-0034) ---
    await db.di_integration_idempotency_records.create_index(
        [("tenantId", 1), ("idempotencyKey", 1)], unique=True
    )
