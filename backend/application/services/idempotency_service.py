"""
Repository Traceability:
- Source Documents: DI-SPRINT-04 (Idempotency Implementation), DI-0034 (X-Idempotency-Key,
  IDEMPOTENCY_CONFLICT error code), DI-0015 (audit).
- Purpose: Tenant-scoped idempotency for integration write operations. Same tenant+key+payload
  replays the stored response; same tenant+key+different payload -> IDEMPOTENCY_CONFLICT.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Optional

from api.middleware.safe_errors import DomainError
from application.services.audit_service import write_audit
from domain.enums.audit_actions import ActorType, AuditAction, ObjectType
from domain.enums.error_codes import ErrorCode
from infrastructure.db.mongo import get_db


def request_hash(operation: str, payload: dict) -> str:
    basis = operation + "|" + json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(basis.encode()).hexdigest()


async def check_replay(
    *, tenant_id: str, idempotency_key: Optional[str], operation: str, payload: dict,
    actor_id: str, correlation_id: str,
) -> Optional[dict]:
    """Returns the stored response dict if this is a safe replay; None if it is a fresh request.
    Raises IDEMPOTENCY_CONFLICT if the key was reused with a different payload."""
    if not idempotency_key:
        return None
    db = get_db()
    rec = await db.di_integration_idempotency_records.find_one(
        {"tenantId": tenant_id, "idempotencyKey": idempotency_key}
    )
    if rec is None:
        return None
    rhash = request_hash(operation, payload)
    if rec.get("requestHash") != rhash or rec.get("operation") != operation:
        await write_audit(
            tenant_id=tenant_id, actor_id=actor_id, actor_type=ActorType.SERVICE,
            action=AuditAction.IDEMPOTENCY_CONFLICT_DETECTED, object_type=ObjectType.INTEGRATION,
            object_id=idempotency_key, correlation_id=correlation_id,
            safe_metadata={"operation": operation},
        )
        raise DomainError(
            ErrorCode.IDEMPOTENCY_CONFLICT,
            "Idempotency key reused with a different payload.", 409, "X-Idempotency-Key",
        )
    return rec.get("responseData")


async def store_result(
    *, tenant_id: str, idempotency_key: Optional[str], operation: str, payload: dict,
    response_data: dict, actor_id: str, correlation_id: str,
) -> None:
    if not idempotency_key:
        return
    db = get_db()
    now = datetime.now(timezone.utc)
    try:
        await db.di_integration_idempotency_records.insert_one({
            "tenantId": tenant_id,
            "idempotencyKey": idempotency_key,
            "operation": operation,
            "requestHash": request_hash(operation, payload),
            "responseData": response_data,
            "correlationId": correlation_id,
            "createdBy": actor_id,
            "createdAt": now,
        })
    except Exception:
        # Unique-index race: another concurrent request stored it first. Safe to ignore.
        pass
