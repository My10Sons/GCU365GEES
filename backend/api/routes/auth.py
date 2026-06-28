"""
Repository Traceability:
- Source Documents: DI-0034 (Auth endpoints — under /api/v1/damage-intelligence base),
  DI-0014 (Authentication, Authorization, safe errors, brute force defence),
  DI-0015 (Audit critical actions — login success and failure).
- Purpose: Login, refresh, /me, logout. Bearer-token based (no cookies) per DI-0034.
"""
from datetime import datetime, timezone, timedelta
from typing import Optional

import jwt
from bson import ObjectId
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, EmailStr

from api.middleware.safe_errors import DomainError
from api.schemas.envelope import ok
from application.security.dependencies import get_current_principal
from application.security.jwt_tokens import create_access_token, create_refresh_token, decode_token
from application.security.password import verify_password
from application.security.permissions_map import permissions_for_roles
from domain.enums.error_codes import ErrorCode
from infrastructure.db.mongo import get_db
import os

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    tenantId: Optional[str] = None  # required if user belongs to multiple tenants in future


class RefreshRequest(BaseModel):
    refreshToken: str


async def _record_attempt(identifier: str, success: bool) -> None:
    db = get_db()
    now = datetime.now(timezone.utc)
    if success:
        await db.di_login_attempts.delete_many({"identifier": identifier})
        return
    await db.di_login_attempts.update_one(
        {"identifier": identifier},
        {"$inc": {"failedCount": 1}, "$set": {"lastAttemptAt": now}, "$setOnInsert": {"identifier": identifier, "firstAttemptAt": now}},
        upsert=True,
    )


async def _is_locked(identifier: str) -> bool:
    max_attempts = int(os.environ.get("DI_BRUTE_FORCE_MAX_ATTEMPTS", "5"))
    lock_minutes = int(os.environ.get("DI_BRUTE_FORCE_LOCK_MINUTES", "15"))
    db = get_db()
    rec = await db.di_login_attempts.find_one({"identifier": identifier})
    if not rec:
        return False
    if (rec.get("failedCount") or 0) < max_attempts:
        return False
    last_attempt: datetime = rec.get("lastAttemptAt")
    if last_attempt is None:
        return False
    if last_attempt.tzinfo is None:
        last_attempt = last_attempt.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) - last_attempt < timedelta(minutes=lock_minutes):
        return True
    await db.di_login_attempts.delete_many({"identifier": identifier})
    return False


async def _audit(request: Request, action: str, principal_id: Optional[str], success: bool, email: str, tenant_id: Optional[str]) -> None:
    db = get_db()
    await db.di_audit_records.insert_one(
        {
            "tenantId": tenant_id or "-",
            "actorId": principal_id or email,
            "actorType": "USER",
            "action": action,
            "objectType": "AUTH",
            "objectId": email,
            "timestamp": datetime.now(timezone.utc),
            "correlationId": request.state.correlation_id,
            "safeMetadata": {"success": success},
        }
    )


@router.post("/login")
async def login(request: Request, payload: LoginRequest):
    db = get_db()
    email = payload.email.lower().strip()
    client_ip = (request.client.host if request.client else "-") or "-"
    identifier = f"{client_ip}:{email}"

    if await _is_locked(identifier):
        await _audit(request, "AUTH_LOGIN_BLOCKED", None, False, email, payload.tenantId)
        raise DomainError(
            ErrorCode.FORBIDDEN,
            "Too many failed login attempts. Please try again later.",
            403,
        )

    query: dict = {"email": email}
    if payload.tenantId:
        query["tenantId"] = payload.tenantId
    user = await db.di_users.find_one(query)
    if user is None or not verify_password(payload.password, user.get("passwordHash", "")):
        await _record_attempt(identifier, success=False)
        await _audit(request, "AUTH_LOGIN_FAILED", None, False, email, payload.tenantId)
        raise DomainError(ErrorCode.UNAUTHORIZED, "Invalid email or password.", 401)
    if user.get("status") == "DISABLED":
        await _audit(request, "AUTH_LOGIN_DISABLED", str(user["_id"]), False, email, user.get("tenantId"))
        raise DomainError(ErrorCode.FORBIDDEN, "Account disabled.", 403)

    await _record_attempt(identifier, success=True)
    roles = user.get("roles") or []
    access = create_access_token(
        user_id=str(user["_id"]),
        email=user["email"],
        tenant_id=user["tenantId"],
        roles=roles,
    )
    refresh = create_refresh_token(user_id=str(user["_id"]), tenant_id=user["tenantId"])
    await _audit(request, "AUTH_LOGIN_SUCCESS", str(user["_id"]), True, email, user.get("tenantId"))

    return ok(
        {
            "accessToken": access,
            "refreshToken": refresh,
            "tokenType": "Bearer",
            "user": {
                "id": str(user["_id"]),
                "email": user["email"],
                "displayName": user.get("displayName"),
                "tenantId": user["tenantId"],
                "roles": roles,
                "permissions": sorted(permissions_for_roles(roles)),
            },
        },
        request.state.correlation_id,
    )


@router.post("/refresh")
async def refresh(request: Request, payload: RefreshRequest):
    try:
        decoded = decode_token(payload.refreshToken, expected_type="refresh")
    except jwt.ExpiredSignatureError:
        raise DomainError(ErrorCode.UNAUTHORIZED, "Refresh token expired.", 401)
    except jwt.InvalidTokenError:
        raise DomainError(ErrorCode.UNAUTHORIZED, "Invalid refresh token.", 401)

    db = get_db()
    try:
        user = await db.di_users.find_one({"_id": ObjectId(decoded["sub"])})
    except Exception:
        user = None
    if user is None or user.get("tenantId") != decoded.get("tenantId") or user.get("status") == "DISABLED":
        raise DomainError(ErrorCode.UNAUTHORIZED, "Principal not found or disabled.", 401)

    roles = user.get("roles") or []
    access = create_access_token(
        user_id=str(user["_id"]),
        email=user["email"],
        tenant_id=user["tenantId"],
        roles=roles,
    )
    return ok({"accessToken": access, "tokenType": "Bearer"}, request.state.correlation_id)


@router.get("/me")
async def me(request: Request, principal: dict = Depends(get_current_principal)):
    return ok(principal, request.state.correlation_id)


@router.post("/logout")
async def logout(request: Request, principal: dict = Depends(get_current_principal)):
    # Stateless bearer tokens: logout is a client concern (drop the token).
    # Audit the action for traceability.
    await _audit(request, "AUTH_LOGOUT", principal["id"], True, principal["email"], principal["tenantId"])
    return ok({"loggedOut": True}, request.state.correlation_id)
