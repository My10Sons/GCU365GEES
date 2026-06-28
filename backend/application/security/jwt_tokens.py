"""
Repository Traceability:
- Source Documents: DI-0034 (Authorization: Bearer ACCESS_TOKEN, X-Tenant-Id),
  DI-0014 (Authentication, tenant isolation).
- Purpose: JWT issuance and verification. Tenant id is carried in the access token
  to allow X-Tenant-Id header to be cross-checked against the principal.
"""
import os
from datetime import datetime, timezone, timedelta
from typing import Any, Optional

import jwt

JWT_ALGORITHM = "HS256"


def _secret() -> str:
    return os.environ["JWT_SECRET"]


def _access_minutes() -> int:
    return int(os.environ.get("JWT_ACCESS_MINUTES", "60"))


def _refresh_days() -> int:
    return int(os.environ.get("JWT_REFRESH_DAYS", "7"))


def create_access_token(*, user_id: str, email: str, tenant_id: str, roles: list[str]) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": user_id,
        "email": email,
        "tenantId": tenant_id,
        "roles": roles,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=_access_minutes()),
    }
    return jwt.encode(payload, _secret(), algorithm=JWT_ALGORITHM)


def create_refresh_token(*, user_id: str, tenant_id: str) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": user_id,
        "tenantId": tenant_id,
        "type": "refresh",
        "iat": now,
        "exp": now + timedelta(days=_refresh_days()),
    }
    return jwt.encode(payload, _secret(), algorithm=JWT_ALGORITHM)


def decode_token(token: str, *, expected_type: Optional[str] = None) -> dict:
    payload = jwt.decode(token, _secret(), algorithms=[JWT_ALGORITHM])
    if expected_type is not None and payload.get("type") != expected_type:
        raise jwt.InvalidTokenError("Invalid token type")
    return payload
