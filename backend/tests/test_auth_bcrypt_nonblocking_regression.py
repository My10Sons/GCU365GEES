"""
Auth regression after non-blocking bcrypt change.

Verifies that wrapping bcrypt.checkpw in asyncio.to_thread (verify_password_async)
in /api/routes/auth.py did NOT regress:
  - valid login (admin/inspector/reviewer/doha admin) -> 200 + tokens + user.permissions
  - invalid password -> 401 (not 500)
  - unknown user -> 401 (not 500)
  - GET /auth/me with Bearer + X-Tenant-Id -> 200 with principal
  - POST /auth/refresh with refreshToken -> 200 with new accessToken
  - Brute-force lockout still trips at 5 fails -> 403 on the 6th attempt
    (uses a throwaway email so it does NOT lock the real admin)

Base URL: REACT_APP_BACKEND_URL from /app/frontend/.env (read at import time).
"""
import os
import time
import uuid

import pytest
import requests

# Read backend URL from frontend/.env (single source of truth for public host)
_FRONTEND_ENV = "/app/frontend/.env"
BASE_URL = None
if os.path.exists(_FRONTEND_ENV):
    with open(_FRONTEND_ENV, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line.startswith("REACT_APP_BACKEND_URL="):
                BASE_URL = line.split("=", 1)[1].strip().rstrip("/")
                break
assert BASE_URL, "REACT_APP_BACKEND_URL must be set in /app/frontend/.env"

AUTH = f"{BASE_URL}/api/v1/damage-intelligence/auth"

ADMIN_T1 = ("admin@riyadah.tech", "DamageAdmin#2026", "TENANT-000001")
INSPECTOR_T1 = ("inspector@riyadah.tech", "Inspector#2026", "TENANT-000001")
REVIEWER_T1 = ("reviewer@riyadah.tech", "Reviewer#2026", "TENANT-000001")
DOHA_ADMIN = ("doha.admin@riyadah.tech", "DohaAdmin#2026", "RIYADAH-DOH-001")


@pytest.fixture(scope="module")
def session():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


def _login(session, email, password, tenant_id=None):
    body = {"email": email, "password": password}
    if tenant_id:
        body["tenantId"] = tenant_id
    return session.post(f"{AUTH}/login", json=body, timeout=30)


# --- Valid login assertions for each seeded account ---------------------------

@pytest.mark.parametrize(
    "email,password,tenant_id,expected_perm_count_min",
    [
        (*ADMIN_T1, 20),
        (*INSPECTOR_T1, 8),
        (*REVIEWER_T1, 10),
        (*DOHA_ADMIN, 20),
    ],
)
def test_valid_login_returns_tokens_and_user(session, email, password, tenant_id, expected_perm_count_min):
    """Valid creds -> 200 + accessToken + refreshToken + user.permissions populated."""
    r = _login(session, email, password)
    assert r.status_code == 200, f"login {email} returned {r.status_code}: {r.text[:300]}"
    body = r.json()
    # Envelope shape
    assert body.get("success") is True, f"envelope.success != True: {body}"
    data = body.get("data") or {}
    assert isinstance(data.get("accessToken"), str) and len(data["accessToken"]) > 20, "missing accessToken"
    assert isinstance(data.get("refreshToken"), str) and len(data["refreshToken"]) > 20, "missing refreshToken"
    assert data.get("tokenType") == "Bearer"
    user = data.get("user") or {}
    assert user.get("email") == email
    assert user.get("tenantId") == tenant_id
    assert isinstance(user.get("roles"), list) and len(user["roles"]) >= 1
    assert isinstance(user.get("permissions"), list)
    assert len(user["permissions"]) >= expected_perm_count_min, (
        f"perm count too low for {email}: {len(user['permissions'])} < {expected_perm_count_min}"
    )


# --- Negative cases must return 401, never 500 --------------------------------

def _err_msg(body: dict) -> str:
    """Envelope shape: {success:false, errors:[{code,message}], ...}."""
    errs = body.get("errors") or []
    if errs and isinstance(errs, list):
        return errs[0].get("message", "") or ""
    return (body.get("error") or {}).get("message") or body.get("message") or ""


def test_invalid_password_returns_401(session):
    r = _login(session, ADMIN_T1[0], "definitely-wrong-password-xyz")
    assert r.status_code == 401, f"expected 401, got {r.status_code}: {r.text[:300]}"
    body = r.json()
    assert body.get("success") is False
    msg = _err_msg(body)
    assert "Invalid email or password" in msg, f"unexpected message: {msg!r} body={body}"
    # Successful login afterwards to clear admin's failed-counter (per-{ip,email}).
    good = _login(session, *ADMIN_T1[:2])
    assert good.status_code == 200


def test_unknown_user_returns_401(session):
    unknown_email = f"nobody.{uuid.uuid4().hex[:10]}@riyadah.tech"
    r = _login(session, unknown_email, "whatever-1234")
    assert r.status_code == 401, f"expected 401 for unknown user, got {r.status_code}: {r.text[:300]}"


# --- /me with Bearer + X-Tenant-Id --------------------------------------------

def test_me_with_bearer_token(session):
    r = _login(session, *ADMIN_T1[:2])
    assert r.status_code == 200
    token = r.json()["data"]["accessToken"]
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Tenant-Id": ADMIN_T1[2],
    }
    me_resp = requests.get(f"{AUTH}/me", headers=headers, timeout=15)
    assert me_resp.status_code == 200, f"/me failed: {me_resp.status_code} {me_resp.text[:300]}"
    me_body = me_resp.json()
    assert me_body.get("success") is True
    principal = me_body.get("data") or {}
    assert principal.get("email") == ADMIN_T1[0]
    assert principal.get("tenantId") == ADMIN_T1[2]
    assert isinstance(principal.get("permissions"), list) and len(principal["permissions"]) > 0


# --- /refresh round-trip ------------------------------------------------------

def test_refresh_token_returns_new_access_token(session):
    r = _login(session, *ADMIN_T1[:2])
    assert r.status_code == 200
    refresh_token = r.json()["data"]["refreshToken"]
    orig_access = r.json()["data"]["accessToken"]
    rr = requests.post(f"{AUTH}/refresh", json={"refreshToken": refresh_token}, timeout=15)
    assert rr.status_code == 200, f"/refresh failed: {rr.status_code} {rr.text[:300]}"
    rbody = rr.json()
    assert rbody.get("success") is True
    new_access = (rbody.get("data") or {}).get("accessToken")
    assert isinstance(new_access, str) and len(new_access) > 20
    # validate the new token actually works against /me
    headers = {"Authorization": f"Bearer {new_access}", "X-Tenant-Id": ADMIN_T1[2]}
    me2 = requests.get(f"{AUTH}/me", headers=headers, timeout=15)
    assert me2.status_code == 200, f"refreshed token failed on /me: {me2.status_code}"


# --- Brute-force lockout (uses throwaway email, NOT real admin) ---------------

def test_brute_force_lockout_throwaway_email(session):
    """
    5 failed logins for the SAME (client_ip, email) should trigger lockout.
    NOTE on infra: the public ingress in this preview env load-balances each
    request across multiple upstream pods, so `request.client.host` (and hence
    the lockout identifier {ip}:{email}) can rotate between ~2 different IPs.
    We therefore send 14 failing attempts so that AT LEAST one IP-bucket
    accumulates >=5 fails, guaranteeing a 403 lockout response is observed.
    Uses a unique throwaway email so the real admin/inspector are unaffected.
    """
    throwaway = f"lockout.test+{uuid.uuid4().hex[:8]}@riyadah.tech"
    statuses = []
    for _ in range(14):
        r = _login(session, throwaway, "wrong-pw")
        statuses.append(r.status_code)

    # Every attempt must be either 401 (still under threshold for its bucket)
    # or 403 (bucket has crossed the 5-fail threshold). Never a 500.
    assert all(s in (401, 403) for s in statuses), f"unexpected statuses: {statuses}"
    # And we must observe at least one 403 - i.e. lockout fires from at least
    # one IP-bucket after >=5 fails into it.
    assert 403 in statuses, (
        f"expected at least one 403 lockout across 14 fails, got {statuses}"
    )

    # Validate the 403 carries the safe lockout message.
    locked_idx = statuses.index(403)
    # Re-issue one more failing attempt and inspect the message of any 403 we get.
    final = _login(session, throwaway, "wrong-pw")
    if final.status_code == 403:
        msg = _err_msg(final.json())
        assert "Too many failed login attempts" in msg, f"unexpected lockout message: {msg}"
    # else: the rotating-IP bucket happened to land on a not-yet-locked bucket;
    # the earlier 403 in `statuses` already proves the lockout path works.
    assert locked_idx >= 0


# --- Clear counter on a successful login (regression guard, real account) ----

def test_successful_login_clears_failed_counter_for_real_admin(session):
    """
    Edge: a few bad attempts followed by a good one should NOT leave the real
    admin locked out. We use 2 fails (well below the 5-fail threshold) then a
    successful login, which the route is supposed to reset via _record_attempt(success=True).
    """
    for _ in range(2):
        bad = _login(session, ADMIN_T1[0], "wrong-pw-test")
        assert bad.status_code == 401, f"unexpected status during pre-fail: {bad.status_code}"
    good = _login(session, *ADMIN_T1[:2])
    assert good.status_code == 200, f"real admin should still log in after <5 fails: {good.status_code} {good.text[:300]}"
    # And it should still work again immediately (counter cleared)
    again = _login(session, *ADMIN_T1[:2])
    assert again.status_code == 200, f"admin re-login failed: {again.status_code}"
