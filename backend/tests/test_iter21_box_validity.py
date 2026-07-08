"""Iteration 21 backend tests: verify bounding-box validity fix in trip inspection detail scan.

Main bug: detail-scan sometimes produced degenerate boxes (w<0.02 or h<0.02) placed off-vehicle.
Fix in _parse_detail_items should drop such boxes (box=None) so no misleading marker is rendered.

Also runs regressions: benchmark endpoints, rental-events, developer/usage.
"""
import os
import time
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

BEFORE_URL = "https://customer-assets.emergentagent.com/job_c57ed0d3-8e93-4f6d-ad9d-dbefa368d472/artifacts/fupk5pro_BaseImage.jpeg"
AFTER_URL = "https://customer-assets.emergentagent.com/job_c57ed0d3-8e93-4f6d-ad9d-dbefa368d472/artifacts/d40t5yp6_Image2WithScratches.jpeg"


@pytest.fixture(scope="module")
def admin_headers():
    r = requests.post(f"{API}/auth/login", json=ADMIN, timeout=30)
    assert r.status_code == 200, r.text
    tok = r.json()["data"]["accessToken"]
    return {"Authorization": f"Bearer {tok}", "X-Tenant-Id": "TENANT-000001"}


@pytest.fixture(scope="module")
def api_key(admin_headers):
    r = requests.post(f"{API}/developer/api-keys", json={"label": "TEST_iter21_box"}, headers=admin_headers, timeout=30)
    assert r.status_code in (200, 201), r.text
    body = r.json()
    key = body.get("data", {}).get("apiKey") or body.get("apiKey")
    assert key and key.startswith("dik_"), body
    return key


@pytest.fixture(scope="module")
def test_images():
    before = requests.get(BEFORE_URL, timeout=60)
    after = requests.get(AFTER_URL, timeout=60)
    assert before.status_code == 200 and len(before.content) > 1000
    assert after.status_code == 200 and len(after.content) > 1000
    return before.content, after.content


@pytest.fixture(scope="module")
def completed_job(api_key, test_images):
    before_bytes, after_bytes = test_images
    files = {
        "before_rear": ("before.jpg", before_bytes, "image/jpeg"),
        "after_rear": ("after.jpg", after_bytes, "image/jpeg"),
    }
    data = {"mode": "fast", "save_to_vehicle_history": "false"}
    headers = {"X-API-Key": api_key}
    r = requests.post(f"{API}/ext/v1/trip-inspections", data=data, files=files, headers=headers, timeout=90)
    assert r.status_code in (200, 201, 202), f"submit failed: {r.status_code} {r.text}"
    body = r.json()
    job_id = body.get("data", {}).get("jobId") or body.get("jobId")
    assert job_id, body

    # Poll up to 4 minutes
    deadline = time.time() + 240
    last = None
    while time.time() < deadline:
        pr = requests.get(f"{API}/ext/v1/trip-inspections/{job_id}", headers=headers, timeout=30)
        assert pr.status_code == 200, pr.text
        pj = pr.json()
        last = pj
        status = (pj.get("data") or pj).get("status")
        if status in ("DONE", "FAILED", "ERROR"):
            break
        time.sleep(10)
    assert last is not None
    d = last.get("data") or last
    assert d.get("status") == "DONE", f"job not DONE: {d.get('status')} — {last}"
    return d


class TestBoxValidity:
    """MAIN bug fix verification — no degenerate boxes."""

    def test_result_has_sections(self, completed_job):
        result = completed_job.get("result") or {}
        sections = result.get("sections") or []
        assert isinstance(sections, list) and len(sections) >= 1, f"no sections: {result}"

    def test_all_boxes_valid_or_null(self, completed_job):
        result = completed_job.get("result") or {}
        sections = result.get("sections") or []
        total_items = 0
        items_with_box = 0
        items_without_box = 0
        degenerate = []
        for sec in sections:
            for it in (sec.get("items") or []):
                total_items += 1
                box = it.get("box")
                if box is None:
                    items_without_box += 1
                    continue
                items_with_box += 1
                # box may be dict {x,y,w,h} or list [x,y,w,h]
                if isinstance(box, dict):
                    x, y, w, h = box.get("x"), box.get("y"), box.get("w"), box.get("h")
                elif isinstance(box, (list, tuple)) and len(box) == 4:
                    x, y, w, h = box
                else:
                    degenerate.append({"reason": "bad_shape", "box": box, "item": it})
                    continue
                if None in (x, y, w, h):
                    degenerate.append({"reason": "null_field", "box": box})
                    continue
                # Validity rules from bug spec
                if not (0 <= x <= 1 and 0 <= y <= 1):
                    degenerate.append({"reason": "xy_out_of_range", "box": box})
                elif w < 0.02 or h < 0.02:
                    degenerate.append({"reason": "too_small", "box": box, "label": it.get("label") or it.get("description")})
                elif x + w > 1.001 or y + h > 1.001:
                    degenerate.append({"reason": "overflow", "box": box})

        print(f"total_items={total_items} with_box={items_with_box} without_box={items_without_box}")
        for sec in sections:
            print(f"section={sec.get('type') or sec.get('name')} items={len(sec.get('items') or [])}")
            for it in (sec.get("items") or []):
                print(f"  - {it.get('type') or it.get('category')}: box={it.get('box')} desc={(it.get('description') or it.get('label') or '')[:80]}")

        assert not degenerate, f"Degenerate boxes found (bug regression): {degenerate}"
        assert total_items >= 1, "expected at least 1 finding"


class TestReportRendering:
    def test_report_urls_present(self, completed_job):
        result = completed_job.get("result") or {}
        assert result.get("reportUrl"), f"no reportUrl in {result}"
        assert result.get("reportPdfUrl"), f"no reportPdfUrl in {result}"

    def test_public_html_report(self, completed_job):
        url = (completed_job.get("result") or {}).get("reportUrl")
        r = requests.get(url, timeout=30)
        assert r.status_code == 200, r.text[:400]
        assert "Trip Inspection Report" in r.text

    def test_public_pdf_report(self, completed_job):
        url = (completed_job.get("result") or {}).get("reportPdfUrl")
        r = requests.get(url, timeout=60)
        assert r.status_code == 200
        assert r.headers.get("content-type", "").startswith("application/pdf")
        assert r.content[:4] == b"%PDF"

    def test_html_marker_column_matches_box_presence(self, completed_job):
        """Items with box → numeric marker; items without box → '·'."""
        result = completed_job.get("result") or {}
        url = result.get("reportUrl")
        r = requests.get(url, timeout=30)
        assert r.status_code == 200
        html = r.text
        # Count items with/without box
        without_box = 0
        with_box = 0
        for sec in (result.get("sections") or []):
            for it in (sec.get("items") or []):
                if it.get("box") is None:
                    without_box += 1
                else:
                    with_box += 1
        print(f"HTML report — items with_box={with_box} without_box={without_box}")
        # If any item has no box, HTML must contain the '·' marker fallback
        if without_box > 0:
            assert "·" in html, "expected '·' marker for boxless items but not present in HTML"


# ---------------- Regressions ----------------

class TestBenchmarkRegression:
    def test_cases(self, admin_headers):
        r = requests.get(f"{API}/benchmark/cases", headers=admin_headers, timeout=30)
        assert r.status_code == 200, r.text
        data = r.json().get("data") or r.json()
        cases = data if isinstance(data, list) else (data.get("cases") or data.get("items") or [])
        assert len(cases) >= 2, f"expected >=2 seeded cases, got {len(cases)}: {data}"

    def test_runs(self, admin_headers):
        r = requests.get(f"{API}/benchmark/runs", params={"limit": 5}, headers=admin_headers, timeout=30)
        assert r.status_code == 200, r.text
        data = r.json().get("data") or r.json()
        runs = data if isinstance(data, list) else (data.get("runs") or data.get("items") or [])
        assert len(runs) >= 1, f"expected >=1 run: {data}"
        # find at least one with summary.recall
        has_recall = False
        for run in runs:
            summ = run.get("summary") or {}
            if "recall" in summ:
                has_recall = True
                break
        assert has_recall, f"no run with summary.recall found: {runs}"


class TestExtAndDeveloperRegression:
    def test_rental_events_list(self, api_key):
        r = requests.get(f"{API}/ext/v1/rental-events", params={"limit": 5},
                         headers={"X-API-Key": api_key}, timeout=30)
        assert r.status_code == 200, r.text

    def test_developer_usage(self, admin_headers):
        r = requests.get(f"{API}/developer/usage", headers=admin_headers, timeout=30)
        assert r.status_code == 200, r.text
