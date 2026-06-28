"""
Repository Traceability:
- Source Documents: DI-0015 (Audit and Traceability — audit record fields, no
  secrets / raw images / unrestricted URLs in audit metadata).
- Purpose: Append-only audit log writer.
"""
from datetime import datetime, timezone
from typing import Any

from infrastructure.db.mongo import get_db


async def write_audit(
    *,
    tenant_id: str,
    actor_id: str,
    actor_type: str,
    action: str,
    object_type: str,
    object_id: str,
    correlation_id: str,
    safe_metadata: dict[str, Any] | None = None,
) -> None:
    db = get_db()
    await db.di_audit_records.insert_one(
        {
            "tenantId": tenant_id,
            "actorId": actor_id,
            "actorType": actor_type,
            "action": action,
            "objectType": object_type,
            "objectId": object_id,
            "timestamp": datetime.now(timezone.utc),
            "correlationId": correlation_id,
            "safeMetadata": safe_metadata or {},
        }
    )
