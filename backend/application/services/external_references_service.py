"""
Repository Traceability:
- Source Documents: DI-SPRINT-01 (External Reference Model — opaque strings),
  DECISION-Sprint01-b (Approved 2026-06-28 — opaque string references, alignment in Sprint 04).
- Purpose: External reference storage layer (write-through to di_external_system_references
  for indexable cross-tenant search; the same shape is embedded on the inspection session for fast reads).
"""
from datetime import datetime, timezone

from infrastructure.db.mongo import get_db


async def write_references(*, tenant_id: str, inspection_session_id: str, refs: dict, correlation_id: str) -> None:
    """Idempotent write-through: upsert one row per non-empty ref."""
    db = get_db()
    now = datetime.now(timezone.utc)
    docs = []
    for ref_type, value in refs.items():
        if not value:
            continue
        docs.append(
            {
                "tenantId": tenant_id,
                "inspectionSessionId": inspection_session_id,
                "refType": ref_type,
                "refValue": value,
                "createdAt": now,
                "correlationId": correlation_id,
            }
        )
    if docs:
        await db.di_external_system_references.insert_many(docs)
