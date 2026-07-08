"""Iteration 22 backend tests — async analyze-section-start + section-jobs polling.

Verifies fix for the 60s ingress timeout bug on sync /trip-inspection/analyze-section.
Runs at most 2 real AI jobs (1 fast + 1 thorough) — each takes 60-150s and ~30K tokens.
"""
import os
import time
import uuid
import pytest
import requests


def _load_backend_url():
    v = os.environ.get("REACT_APP_BACKEND_URL")
    if v:
        return v.rstrip("/")
    with open("/app/frontend/.env") as f:
        for line in f:
            if line.startswith("REACT_APP_BACKEND_URL="):
                return line.split("=", 1)[1].strip().rstrip("/")
    raise RuntimeError("REACT_APP_BACKEND_URL not found")


BASE = _load_backend_url()
API = f"{BASE}/api/v1/damage-intelligence"
ADMIN = {"email": "admin@riyadah.tech", "password": "DamageAdmin#2026", "tenantId": "TENANT-000001"}
DOHA_ADMIN = {"email": "doha.admin@riyadah.tech", "password": "DohaAdmin#2026", "tenantId": "RIYADAH-DOH-001"}

BEFORE_URL = "https://customer-assets.emergentagent.com/job_c57ed0d3-8e93-4f6d-ad9d-dbefa368d472/artifacts/oe4ivztc_BaseImage.jpeg"
AFTER_URL = "https://customer-assets.emergentagent.com/job_c57ed0d3-8e93-4f6d-ad9d-dbefa368d472/artifacts/7h8dty35_Image2WithScratches.jpeg"


def _login(creds):
    r = requests.post(f"{API}/auth/login", json=creds, timeout=30)
    assert r.status_code == 200, r.text
    tok = r.json()["data"]["accessToken"]
    return {"Authorization": f"Bearer {tok}", "X-Tenant-Id": creds["tenantId"]}


@pytest.fixture(scope="module")
def admin_headers():
    return _login(ADMIN)


@pytest.fixture(scope="module")
def doha_headers():
    try:
        return _login(DOHA_ADMIN)
    except AssertionError:
        pytest.skip("Doha tenant admin not available")


@pytest.fixture(scope="module")
def test_images():
    b = requests.get(BEFORE_URL, timeout=60)
    a = requests.get(AFTER_URL, timeout=60)
    assert b.status_code == 200 and len(b.content) > 1000
    assert a.status_code == 200 and len(a.content) > 1000
    return b.content, a.content


def _start_job(headers, images, mode):
    before_bytes, after_bytes = images
    files = {
        "before": ("before.jpg", before_bytes, "image/jpeg"),
        "after": ("after.jpg", after_bytes, "image/jpeg"),
    }
    data = {"kind": "EXTERIOR", "angle": "REAR", "mode": mode}
    t0 = time.time()
    r = requests.post(f"{API}/trip-inspection/analyze-section-start",
                      data=data, files=files, headers=headers, timeout=45)
    elapsed = time.time() - t0
    # Critical: this must NOT be a 502 and must return quickly (< 30s)
    assert r.status_code == 200, f"start failed {r.status_code}: {r.text[:400]}"
    assert elapsed < 30, f"start took {elapsed:.1f}s — should be near-instant"
    body = r.json().get("data") or r.json()
    job_id = body.get("jobId")
    assert job_id, body
    assert body.get("status") == "RUNNING"
    return job_id


def _poll(headers, job_id, max_seconds=240):
    deadline = time.time() + max_seconds
    last = None
    while time.time() < deadline:
        r = requests.get(f"{API}/trip-inspection/section-jobs/{job_id}",
                         headers=headers, timeout=30)
        assert r.status_code == 200, r.text
        last = r.json().get("data") or r.json()
        st = last.get("status")
        if st in ("DONE", "FAILED"):
            return last
        time.sleep(10)
    pytest.fail(f"job {job_id} did not complete within {max_seconds}s — last={last}")


def _has_bumper_scratch(section):
    items = section.get("items") or []
    for it in items:
        typ = (it.get("type") or it.get("category") or "").upper()
        text = " ".join(str(it.get(k) or "") for k in ("label", "description", "location", "detail", "name")).lower()
        if "SCRATCH" in typ and "bumper" in text:
            return True, it
    return False, None


def _types_present(section):
    return {(it.get("type") or it.get("category") or "").upper() for it in (section.get("items") or [])}


# ---------------- Bug 1 + Bug 2 (fast) ----------------

@pytest.fixture(scope="module")
def fast_job_result(admin_headers, test_images):
    jid = _start_job(admin_headers, test_images, "fast")
    print(f"[fast] jobId={jid}")
    return _poll(admin_headers, jid, 240), jid


class TestFastAsyncFlow:
    def test_status_done(self, fast_job_result):
        result, _ = fast_job_result
        assert result.get("status") == "DONE", f"fast job not DONE: {result}"

    def test_section_has_items(self, fast_job_result):
        result, _ = fast_job_result
        section = result.get("section")
        assert section, f"no section on DONE: {result}"
        items = section.get("items") or []
        print(f"[fast] items={len(items)}")
        for it in items:
            print(f"  - {it.get('type') or it.get('category')}: {it.get('label') or it.get('description') or ''}")
        assert len(items) >= 1

    def test_has_bumper_scratch(self, fast_job_result):
        result, _ = fast_job_result
        section = result.get("section")
        found, item = _has_bumper_scratch(section)
        assert found, f"expected SCRATCH mentioning bumper. types={_types_present(section)} items={section.get('items')}"
        print(f"[fast] bumper scratch: {item}")

    def test_has_glass_and_light(self, fast_job_result):
        result, _ = fast_job_result
        types = _types_present(result.get("section"))
        assert "GLASS" in types, f"missing GLASS: {types}"
        assert "LIGHT" in types, f"missing LIGHT: {types}"


# ---------------- Bug 2 (thorough) ----------------

@pytest.fixture(scope="module")
def thorough_job_result(admin_headers, test_images):
    jid = _start_job(admin_headers, test_images, "thorough")
    print(f"[thorough] jobId={jid}")
    return _poll(admin_headers, jid, 300), jid


class TestThoroughAsyncFlow:
    def test_status_done(self, thorough_job_result):
        result, _ = thorough_job_result
        assert result.get("status") == "DONE", f"thorough not DONE: {result}"

    def test_has_bumper_scratch(self, thorough_job_result):
        result, _ = thorough_job_result
        section = result.get("section")
        found, item = _has_bumper_scratch(section)
        assert found, f"thorough missed bumper scratch. types={_types_present(section)} items={section.get('items')}"
        print(f"[thorough] bumper scratch: {item}")

    def test_has_glass_and_light(self, thorough_job_result):
        result, _ = thorough_job_result
        types = _types_present(result.get("section"))
        assert "GLASS" in types
        assert "LIGHT" in types


# ---------------- Bug 3 — 404 / tenant isolation ----------------

class TestSectionJobsErrors:
    def test_nonexistent_returns_404(self, admin_headers):
        bogus = uuid.uuid4().hex
        r = requests.get(f"{API}/trip-inspection/section-jobs/{bogus}",
                         headers=admin_headers, timeout=15)
        assert r.status_code == 404, f"expected 404, got {r.status_code}: {r.text}"

    def test_tenant_isolation(self, admin_headers, doha_headers, fast_job_result):
        _, jid = fast_job_result
        r = requests.get(f"{API}/trip-inspection/section-jobs/{jid}",
                         headers=doha_headers, timeout=15)
        assert r.status_code == 404, f"tenant isolation broken: {r.status_code} {r.text}"


# ---------------- Regressions ----------------

class TestRegression:
    def test_sync_endpoint_still_exists_no_auth(self):
        # No auth → should NOT be 404 (endpoint exists), should be 401 or 403
        r = requests.post(f"{API}/trip-inspection/analyze-section", timeout=15)
        assert r.status_code != 404, "sync endpoint disappeared"
        assert r.status_code in (401, 403, 422), f"expected 401/403/422, got {r.status_code}"

    def test_sync_endpoint_still_exists_with_auth_no_files(self, admin_headers):
        # With auth but no files → 422 (missing required fields), not 404
        r = requests.post(f"{API}/trip-inspection/analyze-section",
                          headers=admin_headers, timeout=15)
        assert r.status_code in (400, 422), f"expected 400/422, got {r.status_code}: {r.text}"

    def test_finalize_with_async_section(self, admin_headers, fast_job_result):
        result, _ = fast_job_result
        section = result.get("section")
        payload = {"sections": [section], "mode": "fast", "saveToVehicleHistory": False}
        r = requests.post(f"{API}/trip-inspection/finalize",
                          json=payload, headers=admin_headers, timeout=60)
        assert r.status_code == 200, f"finalize failed: {r.status_code} {r.text[:400]}"
        body = r.json().get("data") or r.json()
        # overall verdict must be present
        verdict = body.get("verdict") or body.get("overallVerdict") or body.get("overall")
        assert verdict, f"no verdict in finalize response: {body}"
        print(f"[finalize] verdict={verdict}")

    def test_benchmark_cases(self, admin_headers):
        r = requests.get(f"{API}/benchmark/cases", headers=admin_headers, timeout=30)
        assert r.status_code == 200
        data = r.json().get("data") or r.json()
        cases = data if isinstance(data, list) else (data.get("cases") or data.get("items") or [])
        assert len(cases) >= 2, f"expected >=2 cases, got {len(cases)}"
