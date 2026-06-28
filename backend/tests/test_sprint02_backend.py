"""
Sprint 02 — Production Image Quality + AI Advisory Damage Detection backend tests.

Coverage:
 - Configuration thresholds (GET/PUT, defaults, validation, RBAC)
 - Happy path with a REAL automotive JPEG (~116KB) → quality + AI analysis findings
 - Per-session quality check
 - AI analysis retry refreshes findings
 - Audit trail (QUALITY_CHECK_COMPLETED, AI_ANALYSIS_COMPLETED) with safe metadata
 - Cross-tenant isolation (404)
 - Forbidden Sprint 03-05 scope still 404
 - MongoDB Sprint-02 indexes present

NOTE: AI calls are real (Gemini via EMERGENT_LLM_KEY). Allow up to ~90s per call.
"""
import os
import time
from pathlib import Path

import httpx
import pytest
from pymongo import MongoClient


BACKEND = os.environ.get("REACT_APP_BACKEND_URL") or "http://localhost:8001"
BASE = BACKEND.rstrip("/") + "/api/v1/damage-intelligence"
ORIGIN = BACKEND.rstrip("/")
ASSET_DIR = Path("/app/test_reports/assets")
REAL_CAR_JPG = ASSET_DIR / "car1.jpg"  # 116KB unsplash car photo
DAMAGED_CAR_JPG = ASSET_DIR / "car_damage.jpg"  # 47KB unsplash photo

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "damage_intelligence")


# -------------------- fixtures --------------------

@pytest.fixture(scope="session")
def http_client():
    with httpx.Client(timeout=120.0) as c:
        yield c


def _login(c, email, password):
    r = c.post(f"{BASE}/auth/login", json={"email": email, "password": password})
    r.raise_for_status()
    d = r.json()["data"]
    return d["accessToken"], d["user"]["tenantId"]


@pytest.fixture(scope="session")
def admin_t1(http_client):
    t, tid = _login(http_client, "admin@riyadah.tech", "DamageAdmin#2026")
    return {"headers": {"Authorization": f"Bearer {t}", "X-Tenant-Id": tid}, "tenantId": tid, "token": t}


@pytest.fixture(scope="session")
def inspector_t1(http_client):
    t, tid = _login(http_client, "inspector@riyadah.tech", "Inspector#2026")
    return {"headers": {"Authorization": f"Bearer {t}", "X-Tenant-Id": tid}, "tenantId": tid}


@pytest.fixture(scope="session")
def reviewer_t1(http_client):
    t, tid = _login(http_client, "reviewer@riyadah.tech", "Reviewer#2026")
    return {"headers": {"Authorization": f"Bearer {t}", "X-Tenant-Id": tid}, "tenantId": tid}


@pytest.fixture(scope="session")
def admin_t2(http_client):
    t, tid = _login(http_client, "doha.admin@riyadah.tech", "DohaAdmin#2026")
    return {"headers": {"Authorization": f"Bearer {t}", "X-Tenant-Id": tid}, "tenantId": tid}


def _create_session_with_image(c, headers, image_path: Path, position="CAPTURE_FRONT", ext_ref="VEH-S02-TEST"):
    create = c.post(f"{BASE}/inspection-sessions", headers=headers, json={
        "inspectionType": "CHECK_OUT", "sourceSystem": "DI-Web",
        "references": {"externalVehicleRef": ext_ref},
    })
    create.raise_for_status()
    sid = create.json()["data"]["id"]

    body = image_path.read_bytes()
    ur = c.post(f"{BASE}/inspection-sessions/{sid}/images/upload-request", headers=headers, json={
        "capturePosition": position, "fileName": image_path.name,
        "contentType": "image/jpeg", "fileSize": len(body),
    })
    ur.raise_for_status()
    upload_url = ur.json()["data"]["uploadUrl"]
    upload_req_id = ur.json()["data"]["uploadRequestId"]

    put = c.put(ORIGIN + upload_url, content=body, headers={"Content-Type": "image/jpeg"})
    put.raise_for_status()

    reg = c.post(f"{BASE}/inspection-sessions/{sid}/images", headers=headers,
                 json={"uploadRequestId": upload_req_id})
    reg.raise_for_status()
    image_id = reg.json()["data"]["id"]
    return sid, image_id


# -------------------- session-scoped happy-path session --------------------

@pytest.fixture(scope="session")
def happy_session(http_client, admin_t1):
    """Create one session w/ real car image; reused across happy-path assertions."""
    assert REAL_CAR_JPG.exists() and REAL_CAR_JPG.stat().st_size > 50_000, \
        f"Real car JPG missing or too small: {REAL_CAR_JPG}"
    sid, iid = _create_session_with_image(http_client, admin_t1["headers"], REAL_CAR_JPG,
                                          ext_ref="VEH-S02-HAPPY")
    return {"sid": sid, "image_id": iid}


# -------------------- AC: Configuration thresholds --------------------

class TestConfigurationThresholds:

    def test_get_default_threshold_envelope(self, http_client, admin_t1):
        # Reset to 0.70 default first
        http_client.put(f"{BASE}/configuration/ai-thresholds", headers=admin_t1["headers"],
                        json={"confidenceThreshold": 0.70}).raise_for_status()
        r = http_client.get(f"{BASE}/configuration/ai-thresholds", headers=admin_t1["headers"])
        assert r.status_code == 200
        env = r.json()
        assert env["success"] is True
        data = env["data"]
        assert data["confidenceThreshold"] == 0.70
        assert isinstance(data.get("models"), dict)
        assert data["models"].get("imageQuality") == "gemini:gemini-3.5-flash"
        assert data["models"].get("damageDetection") == "gemini:gemini-3.1-pro-preview"

    def test_put_threshold_persists(self, http_client, admin_t1):
        http_client.put(f"{BASE}/configuration/ai-thresholds", headers=admin_t1["headers"],
                        json={"confidenceThreshold": 0.85}).raise_for_status()
        r = http_client.get(f"{BASE}/configuration/ai-thresholds", headers=admin_t1["headers"])
        assert r.json()["data"]["confidenceThreshold"] == 0.85
        # restore for downstream tests
        http_client.put(f"{BASE}/configuration/ai-thresholds", headers=admin_t1["headers"],
                        json={"confidenceThreshold": 0.70}).raise_for_status()

    def test_put_threshold_invalid_high(self, http_client, admin_t1):
        r = http_client.put(f"{BASE}/configuration/ai-thresholds", headers=admin_t1["headers"],
                            json={"confidenceThreshold": 1.5})
        assert r.status_code == 400
        assert r.json()["errors"][0]["code"] == "VALIDATION_ERROR"

    def test_put_threshold_invalid_low(self, http_client, admin_t1):
        r = http_client.put(f"{BASE}/configuration/ai-thresholds", headers=admin_t1["headers"],
                            json={"confidenceThreshold": -0.1})
        assert r.status_code == 400
        assert r.json()["errors"][0]["code"] == "VALIDATION_ERROR"

    def test_inspector_put_forbidden(self, http_client, inspector_t1):
        r = http_client.put(f"{BASE}/configuration/ai-thresholds", headers=inspector_t1["headers"],
                            json={"confidenceThreshold": 0.5})
        assert r.status_code == 403
        assert r.json()["errors"][0]["code"] == "FORBIDDEN"

    def test_inspector_get_allowed(self, http_client, inspector_t1):
        r = http_client.get(f"{BASE}/configuration/ai-thresholds", headers=inspector_t1["headers"])
        assert r.status_code == 200
        assert r.json()["success"] is True


# -------------------- AC: Happy path image quality --------------------

class TestHappyPathQuality:

    def test_quality_check_real_image(self, http_client, admin_t1, happy_session):
        r = http_client.post(f"{BASE}/images/{happy_session['image_id']}/quality-check",
                             headers=admin_t1["headers"], timeout=120.0)
        assert r.status_code == 200, r.text
        data = r.json()["data"]
        # AC: modelVersion, latencyMs, isAdvisory, qualityStatus
        assert data["isAdvisory"] is True
        assert data["modelVersion"] == "gemini:gemini-3.5-flash"
        assert isinstance(data.get("latencyMs"), (int, float)) and data["latencyMs"] > 0
        assert data["qualityStatus"] in ("PASSED", "WARNING", "FAILED", "ERROR")
        # Happy-path expectation: with a real 116KB photo, expect non-ERROR
        if data["qualityStatus"] == "ERROR":
            pytest.fail(f"Quality check returned ERROR on a real automotive image. "
                        f"recaptureRecommendations={data.get('recaptureRecommendations')}")
        # qualityScore should be numeric
        assert isinstance(data.get("qualityScore"), (int, float))
        # scores dict should contain numeric blur/lighting/framing/occlusion
        scores = data.get("scores") or {}
        for k in ("blur", "lighting", "framing", "occlusion"):
            assert k in scores, f"missing score key: {k}"
            assert isinstance(scores[k], (int, float))


# -------------------- AC: Happy path AI analysis --------------------

class TestHappyPathAIAnalysis:

    @pytest.fixture(scope="class")
    def ai_run(self, http_client, admin_t1, happy_session):
        # Ensure threshold is at default 0.70
        http_client.put(f"{BASE}/configuration/ai-thresholds", headers=admin_t1["headers"],
                        json={"confidenceThreshold": 0.70})
        r = http_client.post(f"{BASE}/inspection-sessions/{happy_session['sid']}/ai-analysis",
                             headers=admin_t1["headers"], timeout=180.0)
        assert r.status_code == 200, r.text
        return r.json()["data"]

    def test_analysis_status_and_model(self, ai_run):
        assert ai_run["isAdvisory"] is True
        assert ai_run["modelVersion"] == "gemini:gemini-3.1-pro-preview"
        assert ai_run["status"] in ("COMPLETED", "COMPLETED_WITH_WARNINGS")
        assert ai_run["totalImages"] >= 1
        assert ai_run["totalFindings"] >= 0

    def test_get_findings_shape(self, http_client, admin_t1, ai_run):
        aid = ai_run["id"]
        r = http_client.get(f"{BASE}/ai-analysis/{aid}/findings", headers=admin_t1["headers"])
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["isAdvisory"] is True
        allowed_damage = {"SCRATCH", "DENT", "CRACK", "BROKEN_PART", "PAINT_DAMAGE",
                          "RUST", "MISSING_PART", "OTHER"}
        allowed_status = {"AUTO_ACCEPTABLE", "LOW_CONFIDENCE", "UNCERTAIN"}
        for f in data.get("findings", []):
            assert f["damageType"] in allowed_damage, f["damageType"]
            assert 0.0 <= float(f["confidence"]) <= 1.0
            assert f["status"] in allowed_status, f["status"]
            assert f.get("isAdvisory") is True or data["isAdvisory"] is True


# -------------------- AC: Per-session quality check --------------------

class TestSessionQualityCheck:

    def test_session_quality_summary(self, http_client, admin_t1, happy_session):
        r = http_client.post(f"{BASE}/inspection-sessions/{happy_session['sid']}/quality-check",
                             headers=admin_t1["headers"], timeout=180.0)
        assert r.status_code == 200, r.text
        data = r.json()["data"]
        assert isinstance(data.get("totalImages"), int) and data["totalImages"] >= 1
        for k in ("passedImages", "failedImages", "recaptureRequired", "failedImageIds"):
            assert k in data, f"missing key {k}"


# -------------------- AC: Retry --------------------

class TestRetry:

    def test_retry_refreshes_findings(self, http_client, admin_t1, happy_session):
        # Kick a fresh analysis
        an = http_client.post(f"{BASE}/inspection-sessions/{happy_session['sid']}/ai-analysis",
                              headers=admin_t1["headers"], timeout=180.0).json()["data"]
        aid = an["id"]
        first_model = an["modelVersion"]
        before = http_client.get(f"{BASE}/ai-analysis/{aid}/findings",
                                 headers=admin_t1["headers"]).json()["data"]
        before_ids = {f["id"] for f in before.get("findings", [])}

        time.sleep(1)
        re_an = http_client.post(f"{BASE}/ai-analysis/{aid}/retry",
                                 headers=admin_t1["headers"], timeout=180.0).json()["data"]
        assert re_an["modelVersion"] == first_model
        assert re_an["status"] in ("COMPLETED", "COMPLETED_WITH_WARNINGS",
                                   "FAILED", "PROCESSING")

        after = http_client.get(f"{BASE}/ai-analysis/{aid}/findings",
                                headers=admin_t1["headers"]).json()["data"]
        after_ids = {f["id"] for f in after.get("findings", [])}
        # Retry should at least not reuse the same finding ids (new rows inserted)
        if before_ids and after_ids:
            assert before_ids.isdisjoint(after_ids), \
                "Retry should produce fresh finding ids, found overlap"


# -------------------- AC: Audit trail --------------------

class TestAuditTrail:

    def test_audit_records_for_quality_and_analysis(self, http_client, admin_t1, happy_session):
        client = MongoClient(MONGO_URL)
        try:
            db = client[DB_NAME]
            # Trigger a quality check + analysis (idempotent — may already be present)
            http_client.post(f"{BASE}/images/{happy_session['image_id']}/quality-check",
                             headers=admin_t1["headers"], timeout=120.0)
            http_client.post(f"{BASE}/inspection-sessions/{happy_session['sid']}/ai-analysis",
                             headers=admin_t1["headers"], timeout=180.0)
            q_rows = list(db.di_audit_records.find(
                {"tenantId": admin_t1["tenantId"], "action": "QUALITY_CHECK_COMPLETED"}
            ).limit(5))
            a_rows = list(db.di_audit_records.find(
                {"tenantId": admin_t1["tenantId"], "action": "AI_ANALYSIS_COMPLETED"}
            ).limit(5))
            assert len(q_rows) >= 1, "no QUALITY_CHECK_COMPLETED audit row"
            assert len(a_rows) >= 1, "no AI_ANALYSIS_COMPLETED audit row"

            for row in q_rows + a_rows:
                assert row.get("tenantId")
                assert row.get("actorId")
                assert row.get("correlationId")
                meta = row.get("safeMetadata") or {}
                # Must NOT contain raw image bytes or base64 strings
                blob = repr(meta)
                assert "data:image" not in blob, "audit safeMetadata contains base64 image"
                # naive base64 marker checks
                for forbidden in ("base64", "/9j/", "iVBOR"):
                    assert forbidden.lower() not in blob.lower() or len(blob) < 200, \
                        f"audit safeMetadata may contain image bytes ({forbidden})"

            q_meta = q_rows[0].get("safeMetadata") or {}
            assert "modelVersion" in q_meta
            a_meta = a_rows[0].get("safeMetadata") or {}
            assert "modelVersion" in a_meta or "confidenceThreshold" in a_meta
        finally:
            client.close()


# -------------------- AC: Cross-tenant isolation --------------------

class TestCrossTenantIsolation:

    def test_cross_tenant_quality_check_404(self, http_client, admin_t2, happy_session):
        r = http_client.post(f"{BASE}/images/{happy_session['image_id']}/quality-check",
                             headers=admin_t2["headers"])
        assert r.status_code == 404

    def test_cross_tenant_session_ai_analysis_404(self, http_client, admin_t2, happy_session):
        r = http_client.post(f"{BASE}/inspection-sessions/{happy_session['sid']}/ai-analysis",
                             headers=admin_t2["headers"])
        assert r.status_code == 404

    def test_cross_tenant_session_quality_check_404(self, http_client, admin_t2, happy_session):
        r = http_client.post(f"{BASE}/inspection-sessions/{happy_session['sid']}/quality-check",
                             headers=admin_t2["headers"])
        assert r.status_code == 404

    def test_cross_tenant_session_ai_findings_404(self, http_client, admin_t2, happy_session):
        r = http_client.get(f"{BASE}/inspection-sessions/{happy_session['sid']}/ai-findings",
                            headers=admin_t2["headers"])
        assert r.status_code == 404


# -------------------- AC: Forbidden scope still 404 --------------------

class TestForbiddenScope:

    @pytest.mark.parametrize("path", ["/comparisons", "/review-queue", "/damage-cases", "/reports"])
    def test_sprint03_05_still_404(self, http_client, admin_t1, path):
        r = http_client.get(f"{BASE}{path}", headers=admin_t1["headers"])
        assert r.status_code == 404
        assert r.json()["errors"][0]["code"] == "NOT_FOUND"


# -------------------- AC: MongoDB indexes --------------------

class TestMongoIndexes:

    def test_required_indexes_present(self):
        client = MongoClient(MONGO_URL)
        try:
            db = client[DB_NAME]
            iq = db.di_image_quality_results.index_information()
            assert any("inspectionImageId" in str(v["key"]) for v in iq.values()), \
                "missing inspectionImageId index on di_image_quality_results"

            ana = db.di_ai_analyses.index_information()
            assert any("inspectionSessionId" in str(v["key"]) for v in ana.values())
            assert any("status" in str(v["key"]) for v in ana.values())

            fnd = db.di_ai_findings.index_information()
            assert any("aiAnalysisId" in str(v["key"]) for v in fnd.values())
            assert any("status" in str(v["key"]) for v in fnd.values())

            cfg = db.di_ai_configuration.index_information()
            assert any(v.get("unique") and "tenantId" in str(v["key"]) for v in cfg.values()), \
                "di_ai_configuration must have unique index on tenantId"
        finally:
            client.close()
