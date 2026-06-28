"""
Repository Traceability:
- Source Documents: DI-SPRINT-05 (Monitoring + Metrics — service health, workflow, AI,
  review, cases, integrations, reports, security), DI-0023, DI-0016, DI-0034.
- Purpose: Tenant-scoped operational metrics for dashboards. Read-only aggregation; no
  secrets, no raw evidence.
"""
from __future__ import annotations

from datetime import datetime, timezone

from infrastructure.db.mongo import get_db, ping as mongo_ping
from infrastructure.storage.local_storage import storage_root


async def metrics(*, principal: dict, correlation_id: str) -> dict:
    db = get_db()
    t = {"tenantId": principal["tenantId"]}

    inspections_total = await db.di_inspection_sessions.count_documents(t)
    inspections_submitted = await db.di_inspection_sessions.count_documents({**t, "status": "SUBMITTED"})
    images_registered = await db.di_inspection_images.count_documents(t)
    ai_completed = await db.di_ai_analyses.count_documents({**t, "status": {"$in": ["COMPLETED", "COMPLETED_WITH_WARNINGS"]}})
    ai_failed = await db.di_ai_analyses.count_documents({**t, "status": "FAILED"})
    review_pending = await db.di_review_queue_items.count_documents({**t, "reviewStatus": "PENDING"})
    cases_open = await db.di_damage_cases.count_documents({**t, "status": {"$nin": ["CLOSED", "CANCELLED", "REJECTED"]}})
    reports_generated = await db.di_reports.count_documents(t)

    handoffs_sent = await db.di_maintenance_handoffs.count_documents(t)
    handoffs_rejected = await db.di_maintenance_handoffs.count_documents({**t, "status": "REJECTED"})
    maintenance_callbacks = await db.di_maintenance_references.count_documents(t) + await db.di_maintenance_status_updates.count_documents(t)
    idempotency_conflicts = await db.di_audit_records.count_documents({**t, "action": "IDEMPOTENCY_CONFLICT_DETECTED"})
    croms_checkouts = await db.di_audit_records.count_documents({**t, "action": "CROMS_CHECKOUT_INSPECTION_REQUESTED"})
    croms_checkins = await db.di_audit_records.count_documents({**t, "action": "CROMS_CHECKIN_INSPECTION_REQUESTED"})

    tenant_violations = await db.di_audit_records.count_documents({**t, "action": "TENANT_SCOPE_VIOLATION"})
    unauthorized = await db.di_audit_records.count_documents({**t, "action": "UNAUTHORIZED_ACCESS_ATTEMPT"})

    return {
        "tenantId": principal["tenantId"],
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "workflow": {
            "inspectionsTotal": inspections_total,
            "inspectionsSubmitted": inspections_submitted,
            "imagesRegistered": images_registered,
        },
        "ai": {"analysesCompleted": ai_completed, "analysesFailed": ai_failed},
        "review": {"pending": review_pending},
        "cases": {"open": cases_open},
        "reports": {"generated": reports_generated},
        "integration": {
            "cromsCheckOuts": croms_checkouts,
            "cromsCheckIns": croms_checkins,
            "maintenanceHandoffsSent": handoffs_sent,
            "maintenanceHandoffsRejected": handoffs_rejected,
            "maintenanceCallbacksReceived": maintenance_callbacks,
            "idempotencyConflicts": idempotency_conflicts,
        },
        "security": {"tenantScopeViolations": tenant_violations, "unauthorizedAttempts": unauthorized},
    }


async def dependency_health() -> dict:
    mongo_ok = await mongo_ping()
    try:
        storage_ok = storage_root().exists()
    except Exception:
        storage_ok = False
    return {
        "mongo": {"healthy": mongo_ok},
        "ai_service": {"healthy": True, "mode": "in_process"},
        "object_storage": {"healthy": storage_ok, "mode": "local_dev"},
    }
