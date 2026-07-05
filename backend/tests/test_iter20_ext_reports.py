"""Iteration 20 backend tests: rental-events, open-rentals, ext trip inspection with hosted reports, public reports, integration pack, developer regression."""
import os
import io
import time
import pytest
import requests
from PIL import Image, ImageDraw

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


@pytest.fixture(scope="module")
def admin_headers():
    r = requests.post(f"{API}/auth/login", json=ADMIN, timeout=30)
    assert r.status_code == 200, r.text
    tok = r.json()["data"]["accessToken"]
    return {"Authorization": f"Bearer {tok}", "X-Tenant-Id": "TENANT-000001"}


@pytest.fixture(scope="module")
def api_key(admin_headers):
    r = requests.post(f"{API}/developer/api-keys", json={"label": "TEST_iter20"}, headers=admin_headers, timeout=30)
    assert r.status_code in (200, 201), r.text
    body = r.json()
    key = body.get("data", {}).get("apiKey") or body.get("apiKey")
    assert key and key.startswith("dik_"), body
    return key


def _mk_jpg(color=(120, 120, 130), text="A"):
    img = Image.new("RGB", (256, 256), color)
    d = ImageDraw.Draw(img)
    d.rectangle([40, 40, 200, 200], outline=(255, 255, 255), width=4)
    d.text((90, 100), text, fill=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


# ---------------- Rental events ----------------

class TestRentalEvents:
    def test_missing_api_key(self):
        r = requests.post(f"{API}/ext/v1/rental-events",
                          json={"eventType": "rental.checked_out", "rentalId": "RA-QA-1"}, timeout=15)
        assert r.status_code == 401

    def test_invalid_event_type(self, api_key):
        r = requests.post(f"{API}/ext/v1/rental-events",
                          headers={"X-API-Key": api_key},
                          json={"eventType": "rental.nope", "rentalId": "RA-QA-1"}, timeout=15)
        assert r.status_code == 400

    def test_checked_out(self, api_key):
        r = requests.post(f"{API}/ext/v1/rental-events",
                          headers={"X-API-Key": api_key},
                          json={"eventType": "rental.checked_out", "rentalId": "RA-QA-1",
                                "plate": "QA 123", "customerName": "QA"}, timeout=15)
        assert r.status_code == 200, r.text
        body = r.json()
        data = body.get("data", body)
        assert data.get("received") is True
        assert data.get("status") == "CHECKED_OUT", body

    def test_checked_in(self, api_key):
        r = requests.post(f"{API}/ext/v1/rental-events",
                          headers={"X-API-Key": api_key},
                          json={"eventType": "rental.checked_in", "rentalId": "RA-QA-1"}, timeout=15)
        assert r.status_code == 200, r.text
        data = r.json().get("data", r.json())
        assert data.get("received") is True
        assert data.get("status") == "RETURNED", data

    def test_list_events(self, api_key):
        r = requests.get(f"{API}/ext/v1/rental-events?limit=5",
                         headers={"X-API-Key": api_key}, timeout=15)
        assert r.status_code == 200, r.text
        data = r.json().get("data", r.json())
        items = data if isinstance(data, list) else data.get("items") or data.get("events") or []
        assert len(items) >= 1


# ---------------- Open rentals ----------------

class TestOpenRentals:
    def test_list_has_qa_rental(self, admin_headers):
        r = requests.get(f"{API}/trip-inspection/open-rentals", headers=admin_headers, timeout=15)
        assert r.status_code == 200, r.text
        data = r.json().get("data", r.json())
        items = data if isinstance(data, list) else (data.get("rentals") or data.get("items") or [])
        ids = [x.get("rentalId") for x in items]
        assert "RA-QA-1" in ids, ids

    def test_dismiss(self, admin_headers):
        r = requests.post(f"{API}/trip-inspection/open-rentals/RA-QA-1/dismiss",
                          headers=admin_headers, timeout=15)
        assert r.status_code == 200, r.text
        data = r.json().get("data", r.json())
        assert data.get("dismissed") is True
        # verify removed
        r2 = requests.get(f"{API}/trip-inspection/open-rentals", headers=admin_headers, timeout=15)
        items = r2.json().get("data", r2.json())
        items = items if isinstance(items, list) else (items.get("rentals") or items.get("items") or [])
        assert "RA-QA-1" not in [x.get("rentalId") for x in items]


# ---------------- External trip inspection with hosted report ----------------

@pytest.fixture(scope="module")
def ext_job(api_key):
    files = {
        "before_front": ("bf.jpg", _mk_jpg((100, 110, 120), "B"), "image/jpeg"),
        "after_front": ("af.jpg", _mk_jpg((110, 100, 110), "A"), "image/jpeg"),
    }
    data = {"mode": "fast", "save_to_vehicle_history": "false"}
    r = requests.post(f"{API}/ext/v1/trip-inspections",
                      headers={"X-API-Key": api_key},
                      files=files, data=data, timeout=60)
    assert r.status_code in (200, 201, 202), r.text
    body = r.json().get("data", r.json())
    job_id = body.get("jobId") or body.get("id")
    assert job_id, body

    deadline = time.time() + 120
    last = None
    while time.time() < deadline:
        g = requests.get(f"{API}/ext/v1/trip-inspections/{job_id}",
                         headers={"X-API-Key": api_key}, timeout=30)
        assert g.status_code == 200, g.text
        last = g.json().get("data", g.json())
        st = (last.get("status") or "").upper()
        if st in ("DONE", "COMPLETED", "FAILED", "ERROR"):
            break
        time.sleep(8)
    assert last and (last.get("status") or "").upper() in ("DONE", "COMPLETED"), last
    return last


class TestExtJobReport:
    def test_urls_present(self, ext_job):
        result = ext_job.get("result", ext_job)
        report_url = ext_job.get("reportUrl") or result.get("reportUrl")
        report_pdf = ext_job.get("reportPdfUrl") or result.get("reportPdfUrl")
        assert report_url and "/public/reports/" in report_url, ext_job
        assert report_pdf, ext_job

    def test_public_html(self, ext_job):
        result = ext_job.get("result", ext_job)
        url = ext_job.get("reportUrl") or result.get("reportUrl")
        r = requests.get(url, timeout=30)
        assert r.status_code == 200
        assert "Trip Inspection Report" in r.text

    def test_public_pdf(self, ext_job):
        result = ext_job.get("result", ext_job)
        url = ext_job.get("reportPdfUrl") or result.get("reportPdfUrl")
        r = requests.get(url, timeout=30)
        assert r.status_code == 200
        assert "application/pdf" in r.headers.get("content-type", "")
        assert r.content.startswith(b"%PDF")

    def test_public_image(self, ext_job):
        result = ext_job.get("result", ext_job)
        url = ext_job.get("reportUrl") or result.get("reportUrl")
        r = requests.get(url + "/images/s0_after.jpg", timeout=30)
        assert r.status_code == 200
        assert "image/jpeg" in r.headers.get("content-type", "")

    def test_invalid_token_404(self):
        r = requests.get(f"{API}/public/reports/{'0' * 40}", timeout=15)
        assert r.status_code == 404


# ---------------- Integration pack ----------------

class TestIntegrationPack:
    def test_gcu365_pack(self, admin_headers):
        r = requests.get(f"{API}/developer/integration-pack/GCU365_CROMS",
                         headers=admin_headers, timeout=15)
        assert r.status_code == 200, r.text
        md = r.text
        for phrase in ["3.4 Hosted report", "3.5 Push rental events", "Sandbox Playground", "Option C"]:
            assert phrase in md, f"missing '{phrase}'"


# ---------------- Developer regression ----------------

class TestDeveloperRegression:
    @pytest.mark.parametrize("path", ["/developer/api-keys", "/developer/usage",
                                       "/developer/connectors", "/developer/deliveries"])
    def test_endpoint(self, admin_headers, path):
        r = requests.get(f"{API}{path}", headers=admin_headers, timeout=20)
        assert r.status_code == 200, f"{path} -> {r.status_code} {r.text[:200]}"
