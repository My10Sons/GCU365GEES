"""
Repository Traceability:
- Source Documents: DI-0034 (Required Request Headers: Authorization, X-Tenant-Id;
  permission table), DI-0014 (Authentication, Authorization, Tenant isolation),
  DI-0015 (Audit actor identity).
- Purpose: FastAPI dependencies for current user, permission enforcement, and
  X-Tenant-Id <-> principal tenant cross-check.
"""
from typing import Callable

import jwt
from fastapi import Depends, Header, Request
from bson import ObjectId

from api.middleware.safe_errors import DomainError
from application.security.jwt_tokens import decode_token
from application.security.permissions_map import permissions_for_roles
from domain.enums.error_codes import ErrorCode
from infrastructure.db.mongo import get_db


async def get_current_principal(
    request: Request,
    authorization: str | None = Header(default=None, alias="Authorization"),
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-Id"),
) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise DomainError(ErrorCode.UNAUTHORIZED, "Authentication required.", 401)
    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = decode_token(token, expected_type="access")
    except jwt.ExpiredSignatureError:
        raise DomainError(ErrorCode.UNAUTHORIZED, "Access token expired.", 401)
    except jwt.InvalidTokenError:
        raise DomainError(ErrorCode.UNAUTHORIZED, "Invalid access token.", 401)

    user_id = payload.get("sub")
    token_tenant = payload.get("tenantId")
    if not user_id or not token_tenant:
        raise DomainError(ErrorCode.UNAUTHORIZED, "Malformed access token.", 401)

    # Tenant header must match the principal's tenant if supplied.
    if x_tenant_id and x_tenant_id != token_tenant:
        raise DomainError(
            ErrorCode.TENANT_SCOPE_VIOLATION, "Tenant context mismatch.", 403, "X-Tenant-Id"
        )

    db = get_db()
    try:
        user = await db.di_users.find_one({"_id": ObjectId(user_id)})
    except Exception:
        user = None
    if user is None or user.get("status") == "DISABLED":
        raise DomainError(ErrorCode.UNAUTHORIZED, "Principal not found or disabled.", 401)
    if user.get("tenantId") != token_tenant:
        raise DomainError(
            ErrorCode.TENANT_SCOPE_VIOLATION, "Tenant context mismatch.", 403, "X-Tenant-Id"
        )

    roles = user.get("roles") or []
    principal = {
        "id": str(user["_id"]),
        "email": user.get("email"),
        "tenantId": user.get("tenantId"),
        "roles": roles,
        "permissions": sorted(permissions_for_roles(roles)),
        "displayName": user.get("displayName"),
    }
    request.state.principal = principal
    return principal


def require_permission(permission: str) -> Callable:
    async def _checker(principal: dict = Depends(get_current_principal)) -> dict:
        if permission not in principal["permissions"]:
            raise DomainError(
                ErrorCode.FORBIDDEN, f"Missing required permission: {permission}", 403
            )
        return principal

    return _checker


def require_any_permission(*permissions: str) -> Callable:
    async def _checker(principal: dict = Depends(get_current_principal)) -> dict:
        if not set(permissions) & set(principal["permissions"]):
            raise DomainError(
                ErrorCode.FORBIDDEN,
                "Missing required permission.",
                403,
            )
        return principal

    return _checker
