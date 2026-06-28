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

    # --- Sprint 01: Inspection sessions ---
    await db.di_inspection_sessions.create_index([("tenantId", 1), ("createdAt", -1)])
    await db.di_inspection_sessions.create_index([("tenantId", 1), ("status", 1)])
    await db.di_inspection_sessions.create_index([("tenantId", 1), ("inspectionType", 1)])
    await db.di_inspection_sessions.create_index(
        [("tenantId", 1), ("references.externalVehicleRef", 1)]
    )
    await db.di_inspection_sessions.create_index(
        [("tenantId", 1), ("references.externalRentalAgreementRef", 1)]
    )
    await db.di_inspection_sessions.create_index(
        [("tenantId", 1), ("references.externalBranchRef", 1)]
    )

    # --- Sprint 01: Inspection status history (append-only) ---
    await db.di_inspection_status_history.create_index(
        [("tenantId", 1), ("inspectionSessionId", 1), ("timestamp", 1)]
    )

    # --- Sprint 01: Inspection images ---
    await db.di_inspection_images.create_index(
        [("tenantId", 1), ("inspectionSessionId", 1), ("createdAt", 1)]
    )
    await db.di_inspection_images.create_index(
        [("tenantId", 1), ("inspectionSessionId", 1), ("uploadRequestId", 1)],
        unique=True,
        partialFilterExpression={"uploadRequestId": {"$exists": True}},
    )

    # --- Sprint 01: Evidence references ---
    await db.di_evidence_references.create_index([("tenantId", 1), ("inspectionSessionId", 1)])
    await db.di_evidence_references.create_index([("tenantId", 1), ("inspectionImageId", 1)])

    # --- Sprint 01: Upload requests ---
    await db.di_upload_requests.create_index(
        [("tenantId", 1), ("inspectionSessionId", 1), ("createdAt", -1)]
    )
    await db.di_upload_requests.create_index("expiresAt")

    # --- Sprint 01: External system references (write-through index) ---
    await db.di_external_system_references.create_index(
        [("tenantId", 1), ("refType", 1), ("refValue", 1)]
    )
    await db.di_external_system_references.create_index(
        [("tenantId", 1), ("inspectionSessionId", 1)]
    )

    # --- Sprint 01: Capture positions reference data ---
    await db.di_capture_positions.create_index("code", unique=True)

    # --- Sprint 02: Image quality ---
    await db.di_image_quality_results.create_index(
        [("tenantId", 1), ("inspectionImageId", 1), ("createdAt", -1)]
    )
    await db.di_image_quality_results.create_index(
        [("tenantId", 1), ("inspectionSessionId", 1)]
    )

    # --- Sprint 02: AI analyses ---
    await db.di_ai_analyses.create_index(
        [("tenantId", 1), ("inspectionSessionId", 1), ("startedAt", -1)]
    )
    await db.di_ai_analyses.create_index([("tenantId", 1), ("status", 1)])

    # --- Sprint 02: AI findings ---
    await db.di_ai_findings.create_index(
        [("tenantId", 1), ("aiAnalysisId", 1), ("confidence", -1)]
    )
    await db.di_ai_findings.create_index(
        [("tenantId", 1), ("inspectionSessionId", 1), ("createdAt", -1)]
    )
    await db.di_ai_findings.create_index([("tenantId", 1), ("status", 1)])

    # --- Sprint 02: AI configuration (per tenant) ---
    await db.di_ai_configuration.create_index("tenantId", unique=True)

    # --- Sprint 03: Damage comparisons ---
    await db.di_damage_comparisons.create_index(
        [("tenantId", 1), ("inspectionSessionId", 1), ("createdAt", -1)]
    )
    await db.di_damage_comparisons.create_index([("tenantId", 1), ("status", 1)])
    await db.di_damage_comparison_results.create_index(
        [("tenantId", 1), ("comparisonId", 1), ("createdAt", 1)]
    )
    await db.di_damage_comparison_results.create_index(
        [("tenantId", 1), ("inspectionSessionId", 1)]
    )

    # --- Sprint 03: Review queue (idempotent on object) ---
    await db.di_review_queue_items.create_index(
        [("tenantId", 1), ("objectType", 1), ("objectId", 1)], unique=True
    )
    await db.di_review_queue_items.create_index(
        [("tenantId", 1), ("reviewStatus", 1), ("priority", 1), ("createdAt", 1)]
    )
    await db.di_review_queue_items.create_index([("tenantId", 1), ("inspectionSessionId", 1)])
    await db.di_review_decisions.create_index([("tenantId", 1), ("reviewItemId", 1), ("recordedAt", -1)])
    await db.di_additional_evidence_requests.create_index([("tenantId", 1), ("reviewItemId", 1)])

    # --- Sprint 03: Damage cases ---
    await db.di_damage_cases.create_index([("tenantId", 1), ("createdAt", -1)])
    await db.di_damage_cases.create_index([("tenantId", 1), ("status", 1)])
    await db.di_damage_cases.create_index([("tenantId", 1), ("inspectionSessionId", 1)])
    await db.di_damage_cases.create_index([("tenantId", 1), ("externalVehicleRef", 1)])
    await db.di_damage_cases.create_index([("tenantId", 1), ("dedupeKey", 1)])
    await db.di_damage_case_status_history.create_index(
        [("tenantId", 1), ("damageCaseId", 1), ("timestamp", 1)]
    )
    await db.di_damage_case_links.create_index(
        [("tenantId", 1), ("damageCaseId", 1), ("linkType", 1), ("linkedId", 1)], unique=True
    )
