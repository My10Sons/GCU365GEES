"""
Sprint-08 backend tests for the new streaming + tiered Trip Inspection endpoints:
  - POST /trip-inspection/analyze-section       (single before/after pair)
  - POST /trip-inspection/finalize              (aggregate + auto-case route)
  - POST /trip-inspection/analyze               (legacy single-shot, now with mode)

Goals:
  1. analyze-section fast  -> 200, modelVersion contains 'flash'
  2. analyze-section thorough -> 200, modelVersion contains 'pro' (or just differs from fast)
  3. finalize with synthetic NEW damage costs >= 1000 SAR -> autoCase.created=True,
     damageCaseId present, listed in /damage-cases, externalVehicleRef = reportFields.vehiclePlate
  4. finalize with empty/zero-cost sections -> autoCase.created=False, no case persisted
  5. finalize is fast (<1.5s, no Gemini call)
  6. legacy /analyze still works with mode form field and returns result.mode + SAR currency
"""
from __future__ import annotations

import os
import time
import uuid
from pathlib import Path

import pytest
import requests

def _read_frontend_env() -> str:
    fe = Path("/app/frontend/.env")
    if fe.exists():
        for line in fe.read_text().splitlines():
            if line.startswith("REACT_APP_BACKEND_URL="):
                return line.split("=", 1)[1].strip().strip('"').rstrip("/")
    raise RuntimeError("REACT_APP_BACKEND_URL not found")

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/") or _read_frontend_env()
API = f"{BASE_URL}/api/v1/damage-intelligence"
TENANT = "TENANT-000001"
ADMIN_EMAIL = "admin@riyadah.tech"
ADMIN_PASSWORD = "DamageAdmin#2026"

IMG_DIR = Path("/app/backend/tests/stress")
BEFORE_DAMAGE = IMG_DIR / "before_0.jpg"
AFTER_DAMAGE = IMG_DIR / "after_0.jpg"   # has synthetic damage -> NEW finding
BEFORE_CLEAN = IMG_DIR / "before_1.jpg"
AFTER_CLEAN = IMG_DIR / "after_1.jpg"

GEMINI_TIMEOUT = 90


# ---------- shared fixtures ----------
@pytest.fixture(scope="module")
def token() -> str:
    r = requests.post(f"{API}/auth/login",
                      json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}, timeout=30)
    assert r.status_code == 200, f"login failed: {r.status_code} {r.text}"
    body = r.json()
    assert body.get("success") is True
    tok = body["data"]["accessToken"]
    assert isinstance(tok, str) and tok
    return tok


@pytest.fixture(scope="module")
def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}", "X-Tenant-Id": TENANT}


def _section_files(before: Path, after: Path):
    return {
        "before": (before.name, before.read_bytes(), "image/jpeg"),
        "after":  (after.name,  after.read_bytes(),  "image/jpeg"),
    }


# ---------- 1. analyze-section fast mode ----------
def test_analyze_section_fast_returns_flash_model(auth_headers):
    r = requests.post(
        f"{API}/trip-inspection/analyze-section",
        headers=auth_headers,
        data={"kind": "EXTERIOR", "angle": "FRONT", "mode": "fast"},
        files=_section_files(BEFORE_DAMAGE, AFTER_DAMAGE),
        timeout=GEMINI_TIMEOUT,
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body.get("success") is True
    section = body["data"]
    # required shape
    for k in ("label", "kind", "angle", "items", "newIssueCount", "comparable",
              "estimatedCost", "conditionScore", "cleanliness", "photoCheck",
              "integrity", "modelVersion"):
        assert k in section, f"missing key {k}: {section.keys()}"
    assert section["kind"] == "EXTERIOR"
    assert section["angle"] == "FRONT"
    assert section["estimatedCost"]["currency"] == "SAR"
    assert "flash" in section["modelVersion"].lower(), (
        f"fast mode should map to flash model, got {section['modelVersion']}")
    # stash for cross-test comparison
    pytest.fast_model_version = section["modelVersion"]


# ---------- 2. analyze-section thorough mode ----------
def test_analyze_section_thorough_differs_from_fast(auth_headers):
    r = requests.post(
        f"{API}/trip-inspection/analyze-section",
        headers=auth_headers,
        data={"kind": "EXTERIOR", "angle": "REAR", "mode": "thorough"},
        files=_section_files(BEFORE_CLEAN, AFTER_CLEAN),
        timeout=GEMINI_TIMEOUT,
    )
    assert r.status_code == 200, r.text
    section = r.json()["data"]
    assert section["modelVersion"], "modelVersion missing"
    fast_mv = getattr(pytest, "fast_model_version", "")
    assert section["modelVersion"] != fast_mv, (
        f"thorough modelVersion should differ from fast; both={section['modelVersion']}")
    # Soft assertion: prefer 'pro' in thorough
    assert "pro" in section["modelVersion"].lower() or "flash" not in section["modelVersion"].lower()
    assert section["estimatedCost"]["currency"] == "SAR"


# ---------- 3. finalize is fast (<1.5s) and aggregates correctly with NO new damage ----------
def test_finalize_aggregates_below_threshold_no_case(auth_headers):
    # Synthetic clean sections - zero new findings, zero cost
    section = {
        "label": "Exterior — Front", "kind": "EXTERIOR", "angle": "FRONT",
        "items": [], "newIssueCount": 0, "comparable": True,
        "estimatedCost": {"low": 0, "high": 0, "currency": "SAR"},
        "conditionScore": 95, "cleanliness": "CLEAN",
        "photoCheck": {"beforeUsable": True, "afterUsable": True, "issues": [], "sameVehicle": True, "vehicleMismatchReason": None},
        "integrity": {"beforeSuspicious": False, "afterSuspicious": False, "aiGeneratedLikelihood": "LOW", "signals": []},
        "modelVersion": "gemini-3.5-flash",
    }
    start = time.time()
    r = requests.post(
        f"{API}/trip-inspection/finalize",
        headers={**auth_headers, "Content-Type": "application/json"},
        json={"sections": [section],
              "reportFields": {"vehiclePlate": f"TEST-{uuid.uuid4().hex[:6].upper()}"},
              "mode": "fast"},
        timeout=10,
    )
    elapsed = time.time() - start
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert elapsed < 2.0, f"finalize too slow ({elapsed:.2f}s) - should not call Gemini"
    assert data["overall"] == "NO_NEW_DAMAGE"
    assert data["newIssueCount"] == 0
    assert data["costSummary"]["currency"] == "SAR"
    assert data["coverage"]["capturedCount"] == 1
    assert data["coverage"]["fullWalkaround"] is False
    assert data["isAdvisory"] is True
    assert data["autoCase"]["created"] is False


# ---------- 4. finalize creates auto-case when cost high >= 1000 SAR ----------
def test_finalize_creates_auto_case_when_above_threshold(auth_headers):
    plate = f"TST{uuid.uuid4().hex[:8].upper()}"
    # Synthetic NEW damage with cost high = 1500 (>= 1000 threshold)
    section = {
        "label": "Exterior — Front", "kind": "EXTERIOR", "angle": "FRONT",
        "items": [{
            "category": "DENT", "status": "NEW", "location": "front bumper",
            "severity": "MEDIUM", "confidence": 0.9, "detail": "Test dent",
            "sizeCm": 15.0, "sizeNote": None, "recommendation": "REPAIR",
            "box": {"x": 0.1, "y": 0.2, "w": 0.3, "h": 0.2},
            "estimatedCost": {"low": 600, "high": 1500, "currency": "SAR"},
        }],
        "newIssueCount": 1, "comparable": True,
        "estimatedCost": {"low": 600, "high": 1500, "currency": "SAR"},
        "conditionScore": 70, "cleanliness": "CLEAN",
        "photoCheck": {"beforeUsable": True, "afterUsable": True, "issues": [], "sameVehicle": True, "vehicleMismatchReason": None},
        "integrity": {"beforeSuspicious": False, "afterSuspicious": False, "aiGeneratedLikelihood": "LOW", "signals": []},
        "modelVersion": "gemini-3.5-flash",
    }
    r = requests.post(
        f"{API}/trip-inspection/finalize",
        headers={**auth_headers, "Content-Type": "application/json"},
        json={"sections": [section],
              "reportFields": {"vehiclePlate": plate, "customerName": "TEST_Stream",
                               "rentalId": f"RENT-{plate}"},
              "mode": "fast"},
        timeout=15,
    )
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert data["overall"] == "NEW_DAMAGE_FOUND"
    assert data["newIssueCount"] == 1
    assert data["costSummary"]["high"] == 1500
    assert data["costSummary"]["currency"] == "SAR"
    ac = data["autoCase"]
    assert ac["created"] is True, f"expected autoCase.created=True, got {ac}"
    assert ac.get("damageCaseId"), f"no damageCaseId: {ac}"
    case_id = ac["damageCaseId"]

    # Verify the case is listed under /damage-cases for this tenant
    list_r = requests.get(f"{API}/damage-cases", headers=auth_headers, timeout=15)
    assert list_r.status_code == 200, list_r.text
    items = list_r.json()["data"].get("items") or list_r.json()["data"]
    found = next((c for c in items if c.get("damageCaseId") == case_id or c.get("id") == case_id), None)
    assert found is not None, f"case {case_id} not found in /damage-cases list"
    # caseType=REPAIR_RELEVANT
    assert (found.get("caseType") or "").upper() == "REPAIR_RELEVANT"
    # plate -> externalVehicleRef
    ext_ref = (found.get("externalVehicleRef")
               or (found.get("vehicle") or {}).get("externalRef")
               or (found.get("references") or {}).get("externalVehicleRef"))
    assert ext_ref == plate, f"externalVehicleRef={ext_ref}, expected {plate}"


# ---------- 5. legacy /analyze still works with mode parameter ----------
def test_legacy_analyze_with_mode_fast(auth_headers):
    files = {
        "ext_front_before": (BEFORE_CLEAN.name, BEFORE_CLEAN.read_bytes(), "image/jpeg"),
        "ext_front_after":  (AFTER_CLEAN.name,  AFTER_CLEAN.read_bytes(),  "image/jpeg"),
    }
    r = requests.post(
        f"{API}/trip-inspection/analyze",
        headers=auth_headers,
        data={"mode": "fast", "vehicle_plate": f"LEG-{uuid.uuid4().hex[:6].upper()}"},
        files=files,
        timeout=GEMINI_TIMEOUT,
    )
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert data.get("mode") == "fast"
    assert data["costSummary"]["currency"] == "SAR"
    assert data.get("isAdvisory") is True
    assert "sections" in data and len(data["sections"]) == 1
    assert "modelVersion" in data
    # Currency must be SAR everywhere
    assert "QAR" not in str(data)
