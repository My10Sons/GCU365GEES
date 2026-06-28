"""
Sprint 01 acceptance pytest — validates production inspection + evidence foundation.
Run: pytest /app/backend/tests/test_sprint01_backend.py -v
"""
import os
import time
from typing import Tuple

import httpx
import pytest
from pymongo import MongoClient

BASE_URL = (os.environ.get("DI_SMOKE_BASE_URL") or "http://localhost:8001").rstrip("/")
API = BASE_URL + "/api/v1/damage-intelligence"
ORIGIN = BASE_URL

T1_ADMIN = ("admin@riyadah.tech", "DamageAdmin#2026")
T1_INSP = ("inspector@riyadah.tech", "Inspector#2026")
T1_REV = ("reviewer@riyadah.tech", "Reviewer#2026")
T2_ADMIN = ("doha.admin@riyadah.tech", "DohaAdmin#2026")

TINY_JPEG = bytes.fromhex("FFD8FFE0") + b"pad" * 100


def _login(email: str, password: str) -> Tuple[str, str]:
    r = httpx.post(f"{API}/auth/login", json={"email": email, "password": password}, timeout=15)
    assert r.status_code == 200, r.text
    d = r.json()["data"]
    return d["accessToken"], d["user"]["tenantId"]


def _hdr(token: str, tenant: str) -> dict:
    return {"Authorization": f"Bearer {token}", "X-Tenant-Id": tenant}


@pytest.fixture(scope="module")
def t1():
    tok, tid = _login(*T1_ADMIN)
    return {"tok": tok, "tid": tid, "h": _hdr(tok, tid)}


@pytest.fixture(scope="module")
def t1_inspector():
    tok, tid = _login(*T1_INSP)
    return {"tok": tok, "tid": tid, "h": _hdr(tok, tid)}


@pytest.fixture(scope="module")
def t1_reviewer():
    tok, tid = _login(*T1_REV)
    return {"tok": tok, "tid": tid, "h": _hdr(tok, tid)}


@pytest.fixture(scope="module")
def t2():
    tok, tid = _login(*T2_ADMIN)
    return {"tok": tok, "tid": tid, "h": _hdr(tok, tid)}


@pytest.fixture(scope="module")
def mongo():
    cli = MongoClient(os.environ.get("MONGO_URL", "mongodb://localhost:27017"))
    return cli[os.environ.get("DB_NAME", "damage_intelligence")]


def _create_inspection(h, **overrides):
    body = {
        "inspectionType": "CHECK_OUT",
        "sourceSystem": "GCU365-CROMS",
        "references": {"externalVehicleRef": f"VEH-TEST-{int(time.time()*1000)}"},
    }
    body.update(overrides)
    r = httpx.post(f"{API}/inspection-sessions", headers=h, json=body, timeout=15)
    return r


# -----------------------------------------------------------------------------
# Inspection creation + validation
# -----------------------------------------------------------------------------
class TestInspectionCreation:
    def test_create_draft_persists_tenant_and_refs(self, t1):
        r = _create_inspection(
            t1["h"],
            references={
                "externalVehicleRef": "VEH-AC1",
                "externalRentalAgreementRef": "RA-AC1",
                "externalBranchRef": "BR-AC1",
                "externalMaintenanceRef": "MR-AC1",
                "externalWorkOrderRef": "WO-AC1",
            },
        )
        assert r.status_code == 200, r.text
        d = r.json()["data"]
        assert d["status"] == "DRAFT"
        assert d["tenantId"] == t1["tid"]
        assert d["references"]["externalVehicleRef"] == "VEH-AC1"
        assert d["references"]["externalWorkOrderRef"] == "WO-AC1"

        # GET roundtrip
        got = httpx.get(f"{API}/inspection-sessions/{d['id']}", headers=t1["h"]).json()["data"]
        assert got["id"] == d["id"] and got["status"] == "DRAFT"

    def test_invalid_inspection_type(self, t1):
        r = _create_inspection(t1["h"], inspectionType="GARBAGE")
        assert r.status_code == 400
        assert r.json()["errors"][0]["code"] == "VALIDATION_ERROR"

    def test_invalid_source_system(self, t1):
        r = _create_inspection(t1["h"], sourceSystem="UNKNOWN-SYS")
        assert r.status_code == 400
        assert r.json()["errors"][0]["code"] == "VALIDATION_ERROR"

    def test_missing_external_vehicle_ref(self, t1):
        body = {"inspectionType": "CHECK_OUT", "sourceSystem": "GCU365-CROMS", "references": {}}
        r = httpx.post(f"{API}/inspection-sessions", headers=t1["h"], json=body, timeout=15)
        assert r.status_code == 400
        err = r.json()["errors"][0]
        assert err["code"] == "VALIDATION_ERROR"
        assert err.get("field") == "references.externalVehicleRef"


# -----------------------------------------------------------------------------
# Tenant isolation
# -----------------------------------------------------------------------------
class TestTenantIsolation:
    def test_cross_tenant_get_returns_404(self, t1, t2):
        r = _create_inspection(t1["h"], references={"externalVehicleRef": "VEH-ISO-1"})
        sid = r.json()["data"]["id"]
        r2 = httpx.get(f"{API}/inspection-sessions/{sid}", headers=t2["h"])
        assert r2.status_code == 404
        assert r2.json()["errors"][0]["code"] == "NOT_FOUND"

    def test_t2_list_does_not_contain_t1(self, t1, t2):
        _create_inspection(t1["h"], references={"externalVehicleRef": "VEH-ISO-LIST"})
        # T2 list filtered by T1's ref should be empty
        r = httpx.get(
            f"{API}/inspection-sessions",
            headers=t2["h"],
            params={"externalVehicleRef": "VEH-ISO-LIST"},
        )
        assert r.status_code == 200
        d = r.json()["data"]
        assert d["total"] == 0


# -----------------------------------------------------------------------------
# Listing / pagination / filters
# -----------------------------------------------------------------------------
class TestListAndPagination:
    def test_list_envelope(self, t1):
        r = httpx.get(f"{API}/inspection-sessions", headers=t1["h"], params={"page": 1, "pageSize": 5})
        assert r.status_code == 200
        d = r.json()["data"]
        for k in ("items", "page", "pageSize", "total", "totalPages"):
            assert k in d
        assert d["page"] == 1 and d["pageSize"] == 5

    def test_filter_by_external_vehicle_ref(self, t1):
        marker = f"VEH-FILTER-{int(time.time()*1000)}"
        _create_inspection(t1["h"], references={"externalVehicleRef": marker})
        r = httpx.get(
            f"{API}/inspection-sessions", headers=t1["h"], params={"externalVehicleRef": marker}
        )
        d = r.json()["data"]
        assert d["total"] >= 1
        assert all(it["references"]["externalVehicleRef"] == marker for it in d["items"])

    def test_filter_by_status(self, t1):
        r = httpx.get(f"{API}/inspection-sessions", headers=t1["h"], params={"status": "DRAFT"})
        assert r.status_code == 200
        assert all(it["status"] == "DRAFT" for it in r.json()["data"]["items"])


# -----------------------------------------------------------------------------
# Status lifecycle
# -----------------------------------------------------------------------------
class TestStatusLifecycle:
    def _upload_and_register(self, h, sid):
        ur = httpx.post(
            f"{API}/inspection-sessions/{sid}/images/upload-request",
            headers=h,
            json={
                "capturePosition": "CAPTURE_FRONT",
                "fileName": "front.jpg",
                "contentType": "image/jpeg",
                "fileSize": len(TINY_JPEG),
            },
        ).json()["data"]
        httpx.put(ORIGIN + ur["uploadUrl"], content=TINY_JPEG, headers={"Content-Type": "image/jpeg"})
        reg = httpx.post(
            f"{API}/inspection-sessions/{sid}/images",
            headers=h,
            json={"uploadRequestId": ur["uploadRequestId"]},
        ).json()["data"]
        return ur, reg

    def test_lifecycle_draft_to_submitted_and_locked(self, t1):
        sid = _create_inspection(t1["h"]).json()["data"]["id"]
        # first upload-request -> CAPTURE_IN_PROGRESS
        ur, reg = self._upload_and_register(t1["h"], sid)
        s = httpx.get(f"{API}/inspection-sessions/{sid}", headers=t1["h"]).json()["data"]
        assert s["status"] == "EVIDENCE_REGISTERED"

        # submit
        sub = httpx.post(f"{API}/inspection-sessions/{sid}/submit", headers=t1["h"])
        assert sub.status_code == 200
        assert sub.json()["data"]["status"] == "SUBMITTED"

        # further submit -> 409
        r = httpx.post(f"{API}/inspection-sessions/{sid}/submit", headers=t1["h"])
        assert r.status_code == 409
        assert r.json()["errors"][0]["code"] == "INVALID_STATUS_TRANSITION"

        # PATCH status -> 409
        r = httpx.patch(
            f"{API}/inspection-sessions/{sid}/status",
            headers=t1["h"],
            json={"status": "CAPTURE_IN_PROGRESS"},
        )
        assert r.status_code == 409

        # upload-request -> 409
        r = httpx.post(
            f"{API}/inspection-sessions/{sid}/images/upload-request",
            headers=t1["h"],
            json={
                "capturePosition": "CAPTURE_REAR",
                "fileName": "x.jpg",
                "contentType": "image/jpeg",
                "fileSize": 1024,
            },
        )
        assert r.status_code == 409

    def test_patch_submitted_returns_409_not_403(self, t1):
        sid = _create_inspection(t1["h"]).json()["data"]["id"]
        r = httpx.patch(
            f"{API}/inspection-sessions/{sid}/status", headers=t1["h"], json={"status": "SUBMITTED"}
        )
        assert r.status_code == 409
        assert r.json()["errors"][0]["code"] == "INVALID_STATUS_TRANSITION"

    def test_cancel_requires_reason(self, t1):
        sid = _create_inspection(t1["h"]).json()["data"]["id"]
        # without reason -> 400
        r = httpx.patch(
            f"{API}/inspection-sessions/{sid}/status", headers=t1["h"], json={"status": "CANCELLED"}
        )
        assert r.status_code == 400
        assert r.json()["errors"][0]["code"] == "VALIDATION_ERROR"
        # with reason
        r = httpx.patch(
            f"{API}/inspection-sessions/{sid}/status",
            headers=t1["h"],
            json={"status": "CANCELLED", "reason": "duplicate"},
        )
        assert r.status_code == 200
        assert r.json()["data"]["status"] == "CANCELLED"

    def test_status_history_written(self, t1, mongo):
        sid = _create_inspection(t1["h"]).json()["data"]["id"]
        httpx.patch(
            f"{API}/inspection-sessions/{sid}/status",
            headers=t1["h"],
            json={"status": "FAILED", "reason": "bad ack"},
        )
        rows = list(mongo["di_inspection_status_history"].find({"inspectionSessionId": sid}))
        assert len(rows) >= 1


# -----------------------------------------------------------------------------
# Upload-request validation
# -----------------------------------------------------------------------------
class TestUploadRequestValidation:
    @pytest.fixture
    def sid(self, t1):
        return _create_inspection(t1["h"]).json()["data"]["id"]

    def test_invalid_capture_position(self, t1, sid):
        r = httpx.post(
            f"{API}/inspection-sessions/{sid}/images/upload-request",
            headers=t1["h"],
            json={
                "capturePosition": "NOT_A_POSITION",
                "fileName": "x.jpg",
                "contentType": "image/jpeg",
                "fileSize": 100,
            },
        )
        assert r.status_code == 400

    def test_unsupported_content_type(self, t1, sid):
        r = httpx.post(
            f"{API}/inspection-sessions/{sid}/images/upload-request",
            headers=t1["h"],
            json={
                "capturePosition": "CAPTURE_FRONT",
                "fileName": "x.gif",
                "contentType": "image/gif",
                "fileSize": 100,
            },
        )
        assert r.status_code == 415

    def test_file_too_large(self, t1, sid):
        r = httpx.post(
            f"{API}/inspection-sessions/{sid}/images/upload-request",
            headers=t1["h"],
            json={
                "capturePosition": "CAPTURE_FRONT",
                "fileName": "x.jpg",
                "contentType": "image/jpeg",
                "fileSize": 26 * 1024 * 1024,
            },
        )
        assert r.status_code == 413

    def test_path_traversal_filename(self, t1, sid):
        r = httpx.post(
            f"{API}/inspection-sessions/{sid}/images/upload-request",
            headers=t1["h"],
            json={
                "capturePosition": "CAPTURE_FRONT",
                "fileName": "../../etc/passwd",
                "contentType": "image/jpeg",
                "fileSize": 100,
            },
        )
        assert r.status_code == 400


# -----------------------------------------------------------------------------
# Storage PUT signed URL behaviour
# -----------------------------------------------------------------------------
class TestSignedStorage:
    @pytest.fixture
    def upload_req(self, t1):
        sid = _create_inspection(t1["h"]).json()["data"]["id"]
        ur = httpx.post(
            f"{API}/inspection-sessions/{sid}/images/upload-request",
            headers=t1["h"],
            json={
                "capturePosition": "CAPTURE_FRONT",
                "fileName": "f.jpg",
                "contentType": "image/jpeg",
                "fileSize": len(TINY_JPEG),
            },
        ).json()["data"]
        return sid, ur

    def test_put_stores_under_tenant_path(self, t1, upload_req):
        sid, ur = upload_req
        r = httpx.put(ORIGIN + ur["uploadUrl"], content=TINY_JPEG, headers={"Content-Type": "image/jpeg"})
        assert r.status_code == 200
        # Verify path
        from urllib.parse import parse_qs, urlparse

        q = parse_qs(urlparse(ur["uploadUrl"]).query)
        path = q["path"][0]
        expected_prefix = f"tenants/{t1['tid']}/damage-intelligence/inspections/{sid}/images/"
        assert path.startswith(expected_prefix)

    def test_put_tampered_signature(self, upload_req):
        _, ur = upload_req
        bad_url = ur["uploadUrl"].replace("sig=", "sig=tampered")
        r = httpx.put(ORIGIN + bad_url, content=TINY_JPEG, headers={"Content-Type": "image/jpeg"})
        assert r.status_code == 403

    def test_put_wrong_content_type(self, upload_req):
        _, ur = upload_req
        r = httpx.put(ORIGIN + ur["uploadUrl"], content=b"hello", headers={"Content-Type": "text/plain"})
        assert r.status_code == 415

    def test_put_oversize_body(self, upload_req):
        _, ur = upload_req
        big = b"\xff\xd8\xff\xe0" + b"x" * (26 * 1024 * 1024)
        r = httpx.put(ORIGIN + ur["uploadUrl"], content=big, headers={"Content-Type": "image/jpeg"})
        assert r.status_code == 413


# -----------------------------------------------------------------------------
# Registration idempotency
# -----------------------------------------------------------------------------
class TestRegistration:
    def test_register_without_put_returns_409(self, t1):
        sid = _create_inspection(t1["h"]).json()["data"]["id"]
        ur = httpx.post(
            f"{API}/inspection-sessions/{sid}/images/upload-request",
            headers=t1["h"],
            json={
                "capturePosition": "CAPTURE_REAR",
                "fileName": "r.jpg",
                "contentType": "image/jpeg",
                "fileSize": 1024,
            },
        ).json()["data"]
        # No PUT
        r = httpx.post(
            f"{API}/inspection-sessions/{sid}/images",
            headers=t1["h"],
            json={"uploadRequestId": ur["uploadRequestId"]},
        )
        assert r.status_code == 409

    def test_list_images_excludes_unsigned_urls(self, t1):
        sid = _create_inspection(t1["h"]).json()["data"]["id"]
        ur = httpx.post(
            f"{API}/inspection-sessions/{sid}/images/upload-request",
            headers=t1["h"],
            json={
                "capturePosition": "CAPTURE_FRONT",
                "fileName": "a.jpg",
                "contentType": "image/jpeg",
                "fileSize": len(TINY_JPEG),
            },
        ).json()["data"]
        httpx.put(ORIGIN + ur["uploadUrl"], content=TINY_JPEG, headers={"Content-Type": "image/jpeg"})
        httpx.post(
            f"{API}/inspection-sessions/{sid}/images",
            headers=t1["h"],
            json={"uploadRequestId": ur["uploadRequestId"]},
        )
        listing = httpx.get(f"{API}/inspection-sessions/{sid}/images", headers=t1["h"]).json()["data"]
        assert listing["total"] >= 1
        for it in listing["items"]:
            assert "objectPath" not in it
            # No absolute URL field
            for v in it.values():
                if isinstance(v, str):
                    assert not v.startswith("http://") and not v.startswith("https://")


# -----------------------------------------------------------------------------
# Evidence access link
# -----------------------------------------------------------------------------
class TestEvidenceAccessLink:
    @pytest.fixture(scope="class")
    def evidence(self, t1):
        sid = _create_inspection(t1["h"]).json()["data"]["id"]
        ur = httpx.post(
            f"{API}/inspection-sessions/{sid}/images/upload-request",
            headers=t1["h"],
            json={
                "capturePosition": "CAPTURE_FRONT",
                "fileName": "e.jpg",
                "contentType": "image/jpeg",
                "fileSize": len(TINY_JPEG),
            },
        ).json()["data"]
        httpx.put(ORIGIN + ur["uploadUrl"], content=TINY_JPEG, headers={"Content-Type": "image/jpeg"})
        reg = httpx.post(
            f"{API}/inspection-sessions/{sid}/images",
            headers=t1["h"],
            json={"uploadRequestId": ur["uploadRequestId"]},
        ).json()["data"]
        return reg["evidenceId"], ur["uploadUrl"]

    def test_access_link_validates_expires(self, t1, evidence):
        eid, _ = evidence
        r = httpx.post(
            f"{API}/evidence/{eid}/access-link",
            headers=t1["h"],
            json={"purpose": "test", "expiresInMinutes": 0},
        )
        assert r.status_code == 400
        r = httpx.post(
            f"{API}/evidence/{eid}/access-link",
            headers=t1["h"],
            json={"purpose": "test", "expiresInMinutes": 120},
        )
        assert r.status_code == 400

    def test_access_link_returns_image_bytes(self, t1, evidence):
        eid, _ = evidence
        link = httpx.post(
            f"{API}/evidence/{eid}/access-link",
            headers=t1["h"],
            json={"purpose": "view", "expiresInMinutes": 5},
        ).json()["data"]
        assert link["method"] == "GET"
        r = httpx.get(ORIGIN + link["accessUrl"])
        assert r.status_code == 200
        assert r.headers["content-type"].startswith("image/")

    def test_upload_sig_cannot_be_used_for_get(self, t1, evidence):
        _, upload_url = evidence
        # Swap action: replace 'upload' with 'access' but keep upload sig
        forged = upload_url.replace("/internal/storage/upload", "/internal/storage/access")
        r = httpx.get(ORIGIN + forged)
        assert r.status_code == 403

    def test_forged_get_signature(self, t1, evidence):
        eid, _ = evidence
        link = httpx.post(
            f"{API}/evidence/{eid}/access-link",
            headers=t1["h"],
            json={"purpose": "view", "expiresInMinutes": 5},
        ).json()["data"]
        forged = link["accessUrl"].replace("sig=", "sig=BAD")
        r = httpx.get(ORIGIN + forged)
        assert r.status_code == 403

    def test_cross_tenant_access_link_404_and_audit(self, t1, t2, evidence, mongo):
        eid, _ = evidence
        r = httpx.post(
            f"{API}/evidence/{eid}/access-link", headers=t2["h"], json={"purpose": "sneaky"}
        )
        assert r.status_code == 404
        # Audit: EVIDENCE_ACCESS_DENIED
        time.sleep(0.3)
        rows = list(
            mongo["di_audit_records"].find(
                {"action": "EVIDENCE_ACCESS_DENIED", "objectId": eid}
            )
        )
        assert len(rows) >= 1


# -----------------------------------------------------------------------------
# Reference / capture positions
# -----------------------------------------------------------------------------
class TestReference:
    def test_capture_positions(self, t1):
        r = httpx.get(f"{API}/reference/capture-positions", headers=t1["h"])
        assert r.status_code == 200
        d = r.json()["data"]
        assert d["total"] == 12
        codes = [it["code"] for it in d["items"]]
        expected = {
            "CAPTURE_FRONT", "CAPTURE_REAR", "CAPTURE_LEFT", "CAPTURE_RIGHT",
            "CAPTURE_FRONT_LEFT", "CAPTURE_FRONT_RIGHT", "CAPTURE_REAR_LEFT", "CAPTURE_REAR_RIGHT",
            "CAPTURE_INTERIOR_FRONT", "CAPTURE_INTERIOR_REAR", "CAPTURE_ODOMETER", "CAPTURE_FUEL_OR_CHARGE",
        }
        assert set(codes) == expected
        # required:true for the 6
        req_codes = {it["code"] for it in d["items"] if it.get("required")}
        assert {"CAPTURE_FRONT", "CAPTURE_REAR", "CAPTURE_LEFT", "CAPTURE_RIGHT",
                "CAPTURE_ODOMETER", "CAPTURE_FUEL_OR_CHARGE"} <= req_codes
        # Ordered ascending
        orders = [it["order"] for it in d["items"]]
        assert orders == sorted(orders)
        # Schema
        for it in d["items"]:
            for k in ("code", "label", "group", "order", "required"):
                assert k in it


# -----------------------------------------------------------------------------
# Audit + indexes
# -----------------------------------------------------------------------------
class TestAuditAndIndexes:
    def test_audit_actions_recorded(self, t1, mongo):
        # Run a full mini-flow to trigger all actions
        sid = _create_inspection(t1["h"], references={"externalVehicleRef": "VEH-AUDIT-1"}).json()["data"]["id"]
        httpx.get(f"{API}/inspection-sessions/{sid}", headers=t1["h"])
        httpx.get(f"{API}/inspection-sessions", headers=t1["h"], params={"pageSize": 1})
        ur = httpx.post(
            f"{API}/inspection-sessions/{sid}/images/upload-request",
            headers=t1["h"],
            json={
                "capturePosition": "CAPTURE_FRONT",
                "fileName": "a.jpg",
                "contentType": "image/jpeg",
                "fileSize": len(TINY_JPEG),
            },
        ).json()["data"]
        httpx.put(ORIGIN + ur["uploadUrl"], content=TINY_JPEG, headers={"Content-Type": "image/jpeg"})
        reg = httpx.post(
            f"{API}/inspection-sessions/{sid}/images",
            headers=t1["h"],
            json={"uploadRequestId": ur["uploadRequestId"]},
        ).json()["data"]
        httpx.post(
            f"{API}/evidence/{reg['evidenceId']}/access-link",
            headers=t1["h"],
            json={"purpose": "audit-test"},
        )
        httpx.post(f"{API}/inspection-sessions/{sid}/submit", headers=t1["h"])
        time.sleep(0.5)
        expected = {
            "INSPECTION_CREATED",
            "INSPECTION_VIEWED",
            "INSPECTION_LISTED",
            "IMAGE_UPLOAD_REQUESTED",
            "IMAGE_REGISTERED",
            "EVIDENCE_ACCESS_LINK_CREATED",
            "INSPECTION_SUBMITTED",
        }
        found = set(
            d["action"]
            for d in mongo["di_audit_records"].find({"tenantId": t1["tid"]}, {"action": 1})
        )
        missing = expected - found
        assert not missing, f"Missing audit actions: {missing}"

        # No unrestricted URLs / secrets in safeMetadata
        for row in mongo["di_audit_records"].find(
            {"tenantId": t1["tid"]}, {"safeMetadata": 1}
        ).limit(200):
            sm = str(row.get("safeMetadata") or "")
            assert "http://" not in sm and "https://" not in sm
            assert "accessUrl" not in sm
            assert "password" not in sm.lower()

    def test_mongo_indexes_exist(self, mongo):
        def names(col):
            return set(mongo[col].index_information().keys())

        def has_key(col, key_tuple):
            for _, info in mongo[col].index_information().items():
                if tuple(info["key"]) == key_tuple:
                    return True
            return False

        # sessions
        assert has_key("di_inspection_sessions", (("tenantId", 1), ("createdAt", -1)))
        assert has_key("di_inspection_sessions", (("tenantId", 1), ("status", 1)))
        assert has_key("di_inspection_sessions", (("tenantId", 1), ("inspectionType", 1)))
        assert has_key(
            "di_inspection_sessions", (("tenantId", 1), ("references.externalVehicleRef", 1))
        )
        assert has_key(
            "di_inspection_sessions", (("tenantId", 1), ("references.externalRentalAgreementRef", 1))
        )
        assert has_key(
            "di_inspection_sessions", (("tenantId", 1), ("references.externalBranchRef", 1))
        )
        # status history
        assert has_key(
            "di_inspection_status_history",
            (("tenantId", 1), ("inspectionSessionId", 1), ("timestamp", 1)),
        ) or has_key(
            "di_inspection_status_history",
            (("tenantId", 1), ("inspectionSessionId", 1), ("timestamp", -1)),
        )
        # images
        assert has_key(
            "di_inspection_images", (("tenantId", 1), ("inspectionSessionId", 1), ("createdAt", 1))
        ) or has_key(
            "di_inspection_images", (("tenantId", 1), ("inspectionSessionId", 1), ("createdAt", -1))
        )
        # evidence
        assert has_key("di_evidence_references", (("tenantId", 1), ("inspectionSessionId", 1)))
        assert has_key("di_evidence_references", (("tenantId", 1), ("inspectionImageId", 1)))
        # upload requests
        assert "expiresAt_1" in names("di_upload_requests") or any(
            tuple(i["key"]) == (("expiresAt", 1),) for i in mongo["di_upload_requests"].index_information().values()
        )
        # capture positions unique on code
        cp_idx = mongo["di_capture_positions"].index_information()
        assert any(
            tuple(i["key"]) == (("code", 1),) and i.get("unique") for i in cp_idx.values()
        )


# -----------------------------------------------------------------------------
# Permissions
# -----------------------------------------------------------------------------
class TestPermissions:
    def test_inspector_can_create(self, t1_inspector):
        r = _create_inspection(t1_inspector["h"])
        assert r.status_code == 200

    def test_inspector_cannot_cancel(self, t1_inspector):
        sid = _create_inspection(t1_inspector["h"]).json()["data"]["id"]
        r = httpx.patch(
            f"{API}/inspection-sessions/{sid}/status",
            headers=t1_inspector["h"],
            json={"status": "CANCELLED", "reason": "test"},
        )
        assert r.status_code == 403

    def test_reviewer_cannot_create(self, t1_reviewer):
        r = _create_inspection(t1_reviewer["h"])
        assert r.status_code == 403


# -----------------------------------------------------------------------------
# Forbidden scope (Sprint 02-05 still 404)
# -----------------------------------------------------------------------------
class TestForbiddenScope:
    @pytest.mark.parametrize(
        "path",
        [
            "/ai-analysis",
            "/comparisons",
            "/review-queue",
            "/damage-cases",
            "/reports",
            "/integrations/croms/check-out-inspections",
            "/integrations/maintenance/work-orders",
        ],
    )
    def test_forbidden_paths_return_404(self, t1, path):
        r = httpx.get(f"{API}{path}", headers=t1["h"])
        assert r.status_code == 404
        assert r.json()["errors"][0]["code"] == "NOT_FOUND"
