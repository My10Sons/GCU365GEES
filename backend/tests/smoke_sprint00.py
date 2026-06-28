"""
Repository Traceability:
- Source Document: DI-SPRINT-00 (Sprint 00 Smoke Test, AC-DI-S00-011).
- Purpose: Sprint 00 smoke test — verifies the engineering baseline is online.

Run from /app:
    cd /app/backend && /root/.venv/bin/python tests/smoke_sprint00.py
"""
import os
import sys

import httpx


def _base() -> str:
    # Prefer external preview URL when present (matches CRA frontend behaviour),
    # fall back to localhost for in-container smoke runs.
    url = os.environ.get("DI_SMOKE_BASE_URL")
    if not url:
        # Use local in-container loopback for backend-only smoke
        url = "http://localhost:8001"
    return url.rstrip("/") + "/api/v1/damage-intelligence"


def assert_envelope_ok(resp: httpx.Response, name: str) -> dict:
    data = resp.json()
    assert resp.status_code == 200, f"{name}: HTTP {resp.status_code}"
    assert data.get("success") is True, f"{name}: success != True"
    assert isinstance(data.get("correlationId"), str), f"{name}: missing correlationId"
    assert "x-correlation-id" in {k.lower() for k in resp.headers.keys()}, f"{name}: missing X-Correlation-Id header"
    assert data.get("errors") == [], f"{name}: unexpected errors {data.get('errors')}"
    return data


def assert_envelope_fail(resp: httpx.Response, name: str, *, expected_code: str) -> None:
    data = resp.json()
    assert data.get("success") is False, f"{name}: expected failure envelope"
    errors = data.get("errors") or []
    assert errors, f"{name}: missing errors list"
    assert errors[0].get("code") == expected_code, (
        f"{name}: expected code {expected_code}, got {errors[0].get('code')}"
    )


def main() -> int:
    base = _base()
    admin_email = os.environ.get("DI_SEED_ADMIN_EMAIL", "admin@riyadah.tech")
    admin_password = os.environ.get("DI_SEED_ADMIN_PASSWORD", "DamageAdmin#2026")
    results: list[str] = []

    with httpx.Client(base_url=base, timeout=10.0) as client:
        # 1. Health
        r = client.get("/health")
        assert_envelope_ok(r, "health")
        results.append("[OK] /health")

        # 2. Dependency health
        r = client.get("/health/dependencies")
        data = assert_envelope_ok(r, "health/dependencies")
        assert data["data"]["mongo"]["healthy"] is True, "mongo dependency not healthy"
        results.append("[OK] /health/dependencies (mongo healthy)")

        # 3. Version
        r = client.get("/version")
        v = assert_envelope_ok(r, "version")
        assert v["data"]["apiBasePath"] == "/api/v1/damage-intelligence"
        results.append(f"[OK] /version = {v['data']['service']} v{v['data']['version']}")

        # 4. Correlation id round-trip
        r = client.get("/health", headers={"X-Correlation-Id": "CORR-SMOKE-S00"})
        assert r.headers.get("X-Correlation-Id") == "CORR-SMOKE-S00", "correlation id not echoed"
        results.append("[OK] correlation id round-trip")

        # 5. Safe error envelope on unknown path
        r = client.get("/this-route-does-not-exist")
        assert_envelope_fail(r, "unknown path", expected_code="NOT_FOUND")
        results.append("[OK] safe error envelope on NOT_FOUND")

        # 6. Auth — missing token
        r = client.get("/auth/me")
        assert_envelope_fail(r, "missing token", expected_code="UNAUTHORIZED")
        results.append("[OK] UNAUTHORIZED when bearer missing")

        # 7. Auth — login admin
        r = client.post("/auth/login", json={"email": admin_email, "password": admin_password})
        login = assert_envelope_ok(r, "login")
        access = login["data"]["accessToken"]
        refresh = login["data"]["refreshToken"]
        tenant = login["data"]["user"]["tenantId"]
        roles = login["data"]["user"]["roles"]
        perms = login["data"]["user"]["permissions"]
        assert access and refresh and tenant, "login response missing required fields"
        assert "DI_Admin" in roles, "admin login did not return DI_Admin role"
        assert "di.configuration.manage" in perms, "admin missing configuration permission"
        results.append(f"[OK] login admin (roles={roles})")

        # 8. /auth/me with bearer + correct tenant
        r = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {access}", "X-Tenant-Id": tenant},
        )
        me = assert_envelope_ok(r, "me")
        assert me["data"]["email"] == admin_email
        results.append("[OK] /auth/me with bearer + tenant")

        # 9. Tenant scope violation
        r = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {access}", "X-Tenant-Id": "TENANT-WRONG"},
        )
        assert_envelope_fail(r, "tenant mismatch", expected_code="TENANT_SCOPE_VIOLATION")
        results.append("[OK] TENANT_SCOPE_VIOLATION on mismatched header")

        # 10. Refresh
        r = client.post("/auth/refresh", json={"refreshToken": refresh})
        assert_envelope_ok(r, "refresh")
        results.append("[OK] refresh access token")

        # 11. Wrong password (also exercises audit + brute-force counter)
        r = client.post("/auth/login", json={"email": admin_email, "password": "NopeNotIt"})
        assert_envelope_fail(r, "wrong password", expected_code="UNAUTHORIZED")
        results.append("[OK] wrong password -> UNAUTHORIZED (safe message)")

        # 12. Integration stubs (Sprint 04 deferral note)
        for path, system in [
            ("/integrations/croms/ping", "GCU365-CROMS"),
            ("/integrations/maintenance/ping", "GCU365Maintenance"),
        ]:
            r = client.get(path)
            data = assert_envelope_ok(r, path)
            assert data["data"]["status"] == "stub"
            assert data["data"]["system"] == system
        results.append("[OK] CROMS + Maintenance integration stubs respond")

    print("\n".join(results))
    print("\nSprint 00 smoke test passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
