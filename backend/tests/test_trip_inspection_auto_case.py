"""
Backend regression tests for Trip Inspection ->  Auto-route NEW high-value damage into
a persisted Damage Case (DECISION-Sprint05: 1A=B / 1B=C / 1C=A / 1D=A).

What this verifies:
  1. Trip analyze with CLEARLY damaged after photo + undamaged before photo + report fields
     -> overall=NEW_DAMAGE_FOUND, costSummary.high >= 1000 QAR, autoCase.created=true with
        damageCaseId, inspectionSessionId, findings>0, severityCode and costHigh.
  2. The created damage case is listed via GET /damage-cases and its detail shows
     caseType=REPAIR_RELEVANT, externalVehicleRef=<plate>, description mentions the trip
     and the provided report fields, and the linked findings are persisted.
  3. Trip analyze with two near-identical undamaged photos -> overall != NEW_DAMAGE_FOUND
     and autoCase.created=false with reason in {below_threshold, no_new_findings}.
     No new damage case is added between before/after listing.
  4. Trip analyze with NO report fields but high-value damage still creates a case;
     externalVehicleRef is a synthetic TRIP-XXXX reference and autoCase.created=true.
  5. The analyze response shape remains intact (sections, coverage, costSummary,
     branding) -- the autoCase block is additive.
"""
import os
import time
import uuid
from pathlib import Path

import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
API = f"{BASE_URL}/api/v1/damage-intelligence"
TENANT_ID = "TENANT-000001"
ADMIN_EMAIL = "admin@riyadah.tech"
ADMIN_PASSWORD = "DamageAdmin#2026"

# Existing real-world test images created by iteration_13.
TRIP_DIR = Path("/tmp/trip")
DAMAGED_BEFORE = TRIP_DIR / "ext_before.png"   # undamaged side of the car
DAMAGED_AFTER = TRIP_DIR / "ext_after.png"     # clearly damaged side of the car

# For the "no damage" case we re-use the SAME undamaged image as both before & after.
UNDAMAGED_IMG = TRIP_DIR / "ext_before.png"

ANALYZE_TIMEOUT = 240  # Gemini multi-pair calls can take 60-120s; allow generous slack.


# --------------------------------------------------------------------------- fixtures
@pytest.fixture(scope="session")
def auth_token() -> str:
    assert BASE_URL, "REACT_APP_BACKEND_URL is not set"
    r = requests.post(
        f"{API}/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=30,
    )
    assert r.status_code == 200, f"login failed {r.status_code} {r.text}"
    data = r.json().get("data") or r.json()
    token = data.get("accessToken") or data.get("token") or data.get("access_token")
    assert token, f"no token in login response: {r.text}"
    return token


@pytest.fixture(scope="session")
def auth_headers(auth_token: str) -> dict:
    return {"Authorization": f"Bearer {auth_token}", "X-Tenant-Id": TENANT_ID}


@pytest.fixture(scope="session", autouse=True)
def _check_assets():
    for p in (DAMAGED_BEFORE, DAMAGED_AFTER, UNDAMAGED_IMG):
        if not p.exists():
            pytest.skip(f"required test asset missing: {p}")


def _analyze(headers: dict, *, before: Path, after: Path, form: dict | None = None) -> dict:
    files = {
        "ext_front_before": (before.name, before.read_bytes(), "image/png"),
        "ext_front_after": (after.name, after.read_bytes(), "image/png"),
    }
    data = form or {}
    r = requests.post(
        f"{API}/trip-inspection/analyze",
        headers=headers, files=files, data=data, timeout=ANALYZE_TIMEOUT,
    )
    assert r.status_code == 200, f"analyze HTTP {r.status_code}: {r.text[:600]}"
    body = r.json()
    assert body.get("success") is True or body.get("ok") is True, f"non-ok envelope: {str(body)[:400]}"
    return body["data"]


def _list_cases(headers: dict, *, page_size: int = 100) -> list[dict]:
    r = requests.get(f"{API}/damage-cases", headers=headers,
                     params={"page": 1, "pageSize": page_size}, timeout=30)
    assert r.status_code == 200, f"list cases HTTP {r.status_code}: {r.text[:400]}"
    body = r.json()
    data = body.get("data") or body
    return data.get("items") or data.get("results") or data.get("cases") or []


# --------------------------------------------------------------------------- shared session state
_state: dict = {}


# --------------------------------------------------------------------------- test 1
def test_1_analyze_damaged_with_report_fields_creates_case(auth_headers):
    plate = f"TEST-{uuid.uuid4().hex[:6].upper()}"
    rental = f"RA-{uuid.uuid4().hex[:8].upper()}"
    customer = "TEST_Auto Case Customer"
    form = {
        "customer_name": customer, "vehicle_plate": plate,
        "vehicle_model": "Toyota Camry", "rental_id": rental,
        "inspector_name": "TEST_Inspector",
    }
    data = _analyze(auth_headers, before=DAMAGED_BEFORE, after=DAMAGED_AFTER, form=form)

    # Response shape preserved (additive autoCase block).
    for key in ("sections", "overall", "coverage", "costSummary", "branding", "isAdvisory"):
        assert key in data, f"missing key '{key}' in analyze response"

    assert data["overall"] == "NEW_DAMAGE_FOUND", f"overall={data.get('overall')} costSummary={data.get('costSummary')}"
    high = (data.get("costSummary") or {}).get("high", 0)
    assert high >= 1000, f"cost high {high} did not reach threshold (sections={data.get('sections')})"

    ac = data.get("autoCase")
    assert ac is not None, "autoCase block missing"
    assert ac.get("created") is True, f"autoCase.created not true: {ac}"
    assert ac.get("damageCaseId"), f"missing damageCaseId: {ac}"
    assert ac.get("inspectionSessionId"), f"missing inspectionSessionId: {ac}"
    assert (ac.get("findings") or 0) > 0, f"findings count not positive: {ac}"
    assert ac.get("severityCode") in {"LOW", "MEDIUM", "HIGH"}, f"bad severityCode: {ac}"
    assert ac.get("costHigh") == high, f"costHigh mismatch ac={ac.get('costHigh')} top={high}"

    _state["case_id"] = ac["damageCaseId"]
    _state["session_id"] = ac["inspectionSessionId"]
    _state["plate"] = plate
    _state["rental"] = rental
    _state["customer"] = customer
    _state["high"] = high


# --------------------------------------------------------------------------- test 2
def test_2_case_is_listed_and_detail_matches(auth_headers):
    case_id = _state.get("case_id")
    if not case_id:
        pytest.skip("no case_id from test 1")

    items = _list_cases(auth_headers, page_size=100)
    ids = [c.get("damageCaseId") or c.get("id") for c in items]
    assert case_id in ids, f"created case {case_id} not in first page list ({len(ids)} items)"

    r = requests.get(f"{API}/damage-cases/{case_id}", headers=auth_headers, timeout=30)
    assert r.status_code == 200, f"get case HTTP {r.status_code}: {r.text[:400]}"
    body = r.json()
    detail = body.get("data") or body
    case = detail.get("case") or detail

    assert case.get("caseType") == "REPAIR_RELEVANT", f"caseType={case.get('caseType')}"
    desc = (case.get("description") or "").lower()
    assert "trip" in desc, f"description does not mention trip: {desc[:200]}"
    assert _state["plate"].lower() in desc or _state["plate"] in (case.get("description") or ""), \
        f"plate not in description: {desc[:200]}"
    assert _state["customer"].lower() in desc, f"customer not in description: {desc[:200]}"
    assert _state["rental"].lower() in desc, f"rentalId not in description: {desc[:200]}"

    # externalVehicleRef came from plate.
    ext_ref = case.get("externalVehicleRef")
    assert ext_ref == _state["plate"], f"externalVehicleRef={ext_ref} expected={_state['plate']}"

    # rentalId is persisted on the underlying inspection session (references.externalRentalAgreementRef).
    # The case description must mention it (the report-fields contract).
    # (Already asserted above via rental.lower() in desc.)

    # Persisted findings present and linked via di_damage_case_links (linkType=FINDING).
    links = case.get("links") or []
    finding_links = [lk for lk in links if (lk.get("linkType") or "").upper() == "FINDING"]
    assert finding_links, f"no FINDING links on case: links={links}"


# --------------------------------------------------------------------------- test 3
def test_3_no_damage_does_not_create_case(auth_headers):
    cases_before = _list_cases(auth_headers, page_size=100)
    ids_before = {c.get("damageCaseId") or c.get("id") for c in cases_before}

    data = _analyze(auth_headers, before=UNDAMAGED_IMG, after=UNDAMAGED_IMG)

    assert data.get("overall") != "NEW_DAMAGE_FOUND", \
        f"unexpected NEW_DAMAGE_FOUND on identical undamaged pair: cost={data.get('costSummary')}"
    ac = data.get("autoCase")
    assert ac is not None and ac.get("created") is False, f"autoCase should be created=false: {ac}"
    assert ac.get("reason") in {"below_threshold", "no_new_findings"}, \
        f"unexpected autoCase.reason={ac.get('reason')} ac={ac}"

    cases_after = _list_cases(auth_headers, page_size=100)
    ids_after = {c.get("damageCaseId") or c.get("id") for c in cases_after}
    new_ids = ids_after - ids_before
    assert not new_ids, f"unexpected new damage case(s) appeared: {new_ids}"


# --------------------------------------------------------------------------- test 4
def test_4_no_report_fields_uses_synthetic_trip_ref(auth_headers):
    data = _analyze(auth_headers, before=DAMAGED_BEFORE, after=DAMAGED_AFTER, form={})
    assert data.get("overall") == "NEW_DAMAGE_FOUND", f"overall={data.get('overall')}"
    high = (data.get("costSummary") or {}).get("high", 0)
    assert high >= 1000, f"cost high {high} did not reach threshold"

    ac = data.get("autoCase")
    assert ac and ac.get("created") is True, f"autoCase not created without report fields: {ac}"
    case_id = ac.get("damageCaseId")
    assert case_id, f"missing damageCaseId: {ac}"

    # Detail should show a synthetic TRIP-XXXX externalVehicleRef.
    time.sleep(0.5)
    r = requests.get(f"{API}/damage-cases/{case_id}", headers=auth_headers, timeout=30)
    assert r.status_code == 200, r.text[:400]
    body = r.json()
    detail = body.get("data") or body
    case = detail.get("case") or detail
    ext_ref = case.get("externalVehicleRef")
    assert ext_ref and ext_ref.startswith("TRIP-"), f"synthetic ref expected, got {ext_ref!r}"


# --------------------------------------------------------------------------- test 5
def test_5_response_shape_is_intact(auth_headers):
    # Re-use test 1's analyze response semantics on a fresh call.
    data = _analyze(auth_headers, before=DAMAGED_BEFORE, after=DAMAGED_AFTER, form={})
    for key in ("sections", "overall", "newIssueCount", "modelVersion", "isAdvisory",
                "branding", "costSummary", "conditionScore", "cleanliness",
                "hasPhotoWarnings", "hasIntegrityWarnings", "coverage", "autoCase"):
        assert key in data, f"missing key '{key}' in advisory response"
    # Sections themselves have the expected per-section keys.
    assert isinstance(data["sections"], list) and data["sections"], "sections empty"
    s0 = data["sections"][0]
    for k in ("kind", "items", "newIssueCount", "estimatedCost", "photoCheck",
              "integrity", "comparable"):
        assert k in s0, f"section missing key '{k}'"
    # Coverage and costSummary structure.
    cov = data["coverage"]
    for k in ("capturedAngles", "missingAngles", "totalAngles", "capturedCount",
              "interiorCaptured", "fullWalkaround"):
        assert k in cov, f"coverage missing key '{k}'"
    cs = data["costSummary"]
    for k in ("low", "high", "currency"):
        assert k in cs, f"costSummary missing key '{k}'"
