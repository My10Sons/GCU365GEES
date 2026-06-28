"""
Sprint 00 backend acceptance tests.

Covers AC-DI-S00-001 ... AC-DI-S00-011 (excluding 15-min lockout wall clock).
"""
import os
import time
import uuid

import pytest
import requests
from pymongo import MongoClient

PUBLIC_URL = os.environ.get("REACT_APP_BACKEND_URL", "http://localhost:8001").rstrip("/")
BASE = f"{PUBLIC_URL}/api/v1/damage-intelligence"

ADMIN_EMAIL = "admin@riyadah.tech"
ADMIN_PASSWORD = "DamageAdmin#2026"
INSPECTOR_EMAIL = "inspector@riyadah.tech"
INSPECTOR_PASSWORD = "Inspector#2026"
TENANT = "TENANT-000001"


# ---------- Fixtures ----------

@pytest.fixture(scope="module")
def session():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="module")
def admin_tokens(session):
    r = session.post(f"{BASE}/auth/login",
                     json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["success"] is True
    return body["data"]


@pytest.fixture(scope="module")
def mongo():
    cli = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=3000)
    db = cli["damage_intelligence"]
    return db


# ---------- Health / Version / Envelope ----------

class TestHealth:
    def test_health_ok(self, session):
        r = session.get(f"{BASE}/health")
        assert r.status_code == 200
        b = r.json()
        assert b["success"] is True
        assert b["data"]["status"] == "ok"
        assert b["errors"] == []
        assert b["correlationId"].startswith("CORR-")
        assert "x-correlation-id" in {k.lower() for k in r.headers.keys()}

    def test_health_dependencies(self, session):
        r = session.get(f"{BASE}/health/dependencies")
        assert r.status_code == 200
        d = r.json()["data"]
        assert d["mongo"]["healthy"] is True
        assert d["ai_service"]["mode"] == "in_process_placeholder"
        assert d["object_storage"]["mode"] == "local_dev"

    def test_version(self, session):
        r = session.get(f"{BASE}/version")
        assert r.status_code == 200
        d = r.json()["data"]
        assert d["service"] == "damage-intelligence-api"
        assert d["version"] == "1.0.0"
        assert d["apiBasePath"] == "/api/v1/damage-intelligence"


class TestCorrelationAndErrors:
    def test_correlation_round_trip(self, session):
        corr = "CORR-PYTEST-" + uuid.uuid4().hex[:8].upper()
        r = session.get(f"{BASE}/health", headers={"X-Correlation-Id": corr})
        assert r.headers.get("X-Correlation-Id") == corr
        assert r.json()["correlationId"] == corr

    def test_unknown_path_404_safe(self, session):
        r = session.get(f"{BASE}/does-not-exist")
        assert r.status_code == 404
        b = r.json()
        assert b["success"] is False
        assert b["errors"][0]["code"] == "NOT_FOUND"
        text = r.text.lower()
        # No stack traces / secret leakage
        assert "traceback" not in text
        assert "jwt_secret" not in text
        assert "mongo_url" not in text


# ---------- Auth ----------

class TestAuth:
    def test_admin_login_envelope(self, admin_tokens):
        d = admin_tokens
        assert d["tokenType"] == "Bearer"
        assert d["accessToken"] and d["refreshToken"]
        u = d["user"]
        assert u["tenantId"] == TENANT
        assert "DI_Admin" in u["roles"]
        assert "di.configuration.manage" in u["permissions"]
        assert "di.audit.read" in u["permissions"]
        # Admin should NOT have integration-service-only perms
        assert "di.integrations.croms" not in u["permissions"]
        assert "di.integrations.maintenance" not in u["permissions"]
        # admin permissions == 21 per delivery notes
        assert len(u["permissions"]) == 21, f"got {len(u['permissions'])} perms"

    def test_wrong_password_generic_error(self, session):
        r = session.post(f"{BASE}/auth/login",
                         json={"email": ADMIN_EMAIL, "password": "BADPASS!!"})
        b = r.json()
        assert b["success"] is False
        assert b["errors"][0]["code"] == "UNAUTHORIZED"
        msg = b["errors"][0]["message"].lower()
        assert "invalid" in msg
        assert "password" in msg or "email" in msg

    def test_unknown_email_same_error(self, session):
        r = session.post(f"{BASE}/auth/login",
                         json={"email": "nobody-xyz@example.com", "password": "SomePass#2026"})
        b = r.json()
        assert b["success"] is False
        assert b["errors"][0]["code"] == "UNAUTHORIZED"

    def test_me_without_auth(self, session):
        r = session.get(f"{BASE}/auth/me")
        assert r.status_code == 401
        assert r.json()["errors"][0]["code"] == "UNAUTHORIZED"

    def test_me_with_auth(self, session, admin_tokens):
        token = admin_tokens["accessToken"]
        r = session.get(f"{BASE}/auth/me", headers={
            "Authorization": f"Bearer {token}",
            "X-Tenant-Id": TENANT,
        })
        assert r.status_code == 200
        d = r.json()["data"]
        assert d["email"] == ADMIN_EMAIL
        assert d["tenantId"] == TENANT
        assert "DI_Admin" in d["roles"]

    def test_tenant_scope_violation(self, session, admin_tokens):
        token = admin_tokens["accessToken"]
        r = session.get(f"{BASE}/auth/me", headers={
            "Authorization": f"Bearer {token}",
            "X-Tenant-Id": "TENANT-WRONG",
        })
        assert r.status_code == 403
        err = r.json()["errors"][0]
        assert err["code"] == "TENANT_SCOPE_VIOLATION"
        assert err.get("field") == "X-Tenant-Id"

    def test_refresh_valid(self, session, admin_tokens):
        r = session.post(f"{BASE}/auth/refresh",
                         json={"refreshToken": admin_tokens["refreshToken"]})
        assert r.status_code == 200
        assert r.json()["data"]["accessToken"]

    def test_refresh_invalid(self, session):
        r = session.post(f"{BASE}/auth/refresh",
                         json={"refreshToken": "not.a.token"})
        b = r.json()
        assert b["success"] is False
        assert b["errors"][0]["code"] == "UNAUTHORIZED"

    def test_inspector_rbac_scope(self, session):
        r = session.post(f"{BASE}/auth/login",
                         json={"email": INSPECTOR_EMAIL, "password": INSPECTOR_PASSWORD})
        assert r.status_code == 200
        d = r.json()["data"]
        perms = d["user"]["permissions"]
        assert "DI_Inspector" in d["user"]["roles"]
        assert "di.configuration.manage" not in perms
        assert "di.audit.read" not in perms
        # Inspector perm count must be fewer than admin (21)
        assert len(perms) < 21


# ---------- Brute force ----------

class TestBruteForce:
    def test_lockout_on_6th_attempt(self, mongo):
        bf_email = "reviewer@riyadah.tech"
        # Clear any prior lockout state for this identifier (test idempotency)
        mongo["di_login_attempts"].delete_many({"identifier": {"$regex": bf_email}})
        s = requests.Session()
        s.headers.update({"Content-Type": "application/json"})
        codes = []
        for i in range(6):
            r = s.post(f"{BASE}/auth/login",
                       json={"email": bf_email, "password": f"WrongPass#{i}2026"})
            codes.append(r.json()["errors"][0]["code"])
        assert codes[:5] == ["UNAUTHORIZED"] * 5, codes
        assert codes[5] == "FORBIDDEN", f"6th attempt not locked: {codes}"
        # Cleanup so subsequent runs and other tests are unaffected
        mongo["di_login_attempts"].delete_many({"identifier": {"$regex": bf_email}})


# ---------- Integration stubs ----------

class TestIntegrationStubs:
    def test_croms_ping(self, session):
        r = session.get(f"{BASE}/integrations/croms/ping")
        assert r.status_code == 200
        d = r.json()["data"]
        assert d["system"] == "GCU365-CROMS"
        assert d["status"] == "stub"
        assert "sprint" in (d.get("note", "") + str(d)).lower()

    def test_maintenance_ping(self, session):
        r = session.get(f"{BASE}/integrations/maintenance/ping")
        assert r.status_code == 200
        d = r.json()["data"]
        assert d["system"] == "GCU365Maintenance"
        assert d["status"] == "stub"


# ---------- Forbidden scope (Sprint 01-05) ----------

class TestForbiddenScope:
    FORBIDDEN_GET = [
        "/review-queue",
        "/reports",
    ]
    FORBIDDEN_POST = [
        "/inspection-sessions",
        "/inspection-sessions/abc/images/upload-request",
        "/inspection-sessions/abc/ai-analysis",
        "/damage-cases",
        "/integrations/croms/check-out-inspections",
    ]

    def test_get_endpoints_missing(self, session, admin_tokens):
        token = admin_tokens["accessToken"]
        headers = {"Authorization": f"Bearer {token}", "X-Tenant-Id": TENANT}
        for p in self.FORBIDDEN_GET:
            r = session.get(f"{BASE}{p}", headers=headers)
            assert r.status_code == 404, f"{p} unexpectedly exists: {r.status_code}"
            assert r.json()["errors"][0]["code"] == "NOT_FOUND"

    def test_post_endpoints_missing(self, session, admin_tokens):
        token = admin_tokens["accessToken"]
        headers = {"Authorization": f"Bearer {token}", "X-Tenant-Id": TENANT}
        for p in self.FORBIDDEN_POST:
            r = session.post(f"{BASE}{p}", headers=headers, json={})
            assert r.status_code == 404, f"{p} unexpectedly exists: {r.status_code}"
            assert r.json()["errors"][0]["code"] == "NOT_FOUND"


# ---------- Audit trail and MongoDB indexes ----------

class TestPersistence:
    def test_audit_login_success(self, session, mongo):
        corr = "CORR-AUDIT-" + uuid.uuid4().hex[:6].upper()
        r = session.post(f"{BASE}/auth/login",
                         json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
                         headers={"X-Correlation-Id": corr})
        assert r.status_code == 200
        time.sleep(0.5)
        rec = mongo["di_audit_records"].find_one({"correlationId": corr,
                                                  "action": "AUTH_LOGIN_SUCCESS"})
        assert rec is not None, "AUTH_LOGIN_SUCCESS not recorded"
        # No secrets in record
        flat = str(rec).lower()
        assert "damageadmin#2026" not in flat
        assert "accesstoken" not in flat
        assert "refreshtoken" not in flat

    def test_audit_login_failed(self, session, mongo):
        corr = "CORR-AUDFAIL-" + uuid.uuid4().hex[:6].upper()
        session.post(f"{BASE}/auth/login",
                     json={"email": ADMIN_EMAIL, "password": "WRONG-AUDIT"},
                     headers={"X-Correlation-Id": corr})
        time.sleep(0.5)
        rec = mongo["di_audit_records"].find_one({"correlationId": corr,
                                                  "action": "AUTH_LOGIN_FAILED"})
        assert rec is not None, "AUTH_LOGIN_FAILED not recorded"
        assert "wrong-audit" not in str(rec).lower()

    def test_indexes_present(self, mongo):
        users_idx = mongo["di_users"].index_information()
        assert any(
            idx.get("unique") and {"tenantId", "email"} == {k for k, _ in idx["key"]}
            for idx in users_idx.values()
        ), f"missing unique (tenantId,email) on di_users: {users_idx}"

        audit_idx = mongo["di_audit_records"].index_information()
        keys = [tuple(k for k, _ in v["key"]) for v in audit_idx.values()]
        assert any(set(k) >= {"tenantId", "objectType", "objectId"} for k in keys), keys
        assert any(set(k) >= {"tenantId", "timestamp"} for k in keys), keys

        idem_idx = mongo["di_integration_idempotency_records"].index_information()
        assert any(
            idx.get("unique") and {"tenantId", "idempotencyKey"} == {k for k, _ in idx["key"]}
            for idx in idem_idx.values()
        ), f"missing unique (tenantId,idempotencyKey): {idem_idx}"
