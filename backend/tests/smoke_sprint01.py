"""
Repository Traceability:
- Source Document: DI-SPRINT-01 §"Sprint 01 Smoke Test" (16-step checklist).
- Purpose: End-to-end smoke test for the Sprint 01 inspection + evidence foundation.

Run from /app/backend:
    /root/.venv/bin/python tests/smoke_sprint01.py
"""
import os
import sys

import httpx


def base() -> str:
    return (os.environ.get("DI_SMOKE_BASE_URL") or "http://localhost:8001").rstrip("/") + "/api/v1/damage-intelligence"


def login(client: httpx.Client, email: str, password: str) -> tuple[str, str]:
    r = client.post("/auth/login", json={"email": email, "password": password})
    r.raise_for_status()
    d = r.json()["data"]
    return d["accessToken"], d["user"]["tenantId"]


def headers(token: str, tenant: str) -> dict:
    return {"Authorization": f"Bearer {token}", "X-Tenant-Id": tenant}


def main() -> int:
    results: list[str] = []
    api_root = base()
    api_origin = api_root.rsplit("/api/v1/damage-intelligence", 1)[0]

    with httpx.Client(base_url=api_root, timeout=15.0) as c:
        # 1) Health
        assert c.get("/health").json()["success"] is True
        results.append("[OK] health")

        # 2) Login both tenants
        t1_token, t1_tenant = login(c, os.environ["DI_SEED_ADMIN_EMAIL"], os.environ["DI_SEED_ADMIN_PASSWORD"])
        t2_token, t2_tenant = login(c, os.environ["DI_SEED_ADMIN_EMAIL_2"], os.environ["DI_SEED_ADMIN_PASSWORD_2"])
        assert t1_tenant != t2_tenant
        results.append(f"[OK] login both tenants ({t1_tenant} & {t2_tenant})")

        h1 = headers(t1_token, t1_tenant)
        h2 = headers(t2_token, t2_tenant)

        # 3) Create inspection in T1
        create = c.post(
            "/inspection-sessions",
            headers=h1,
            json={
                "inspectionType": "CHECK_OUT",
                "sourceSystem": "GCU365-CROMS",
                "references": {
                    "externalVehicleRef": "VEH-SMOKE-001",
                    "externalRentalAgreementRef": "RA-SMOKE-001",
                    "externalBranchRef": "BR-DOH-01",
                },
            },
        )
        assert create.status_code == 200, create.text
        session = create.json()["data"]
        assert session["status"] == "DRAFT"
        sid = session["id"]
        results.append(f"[OK] create inspection (status=DRAFT, id={sid})")

        # 4) Retrieve
        got = c.get(f"/inspection-sessions/{sid}", headers=h1).json()["data"]
        assert got["id"] == sid and got["status"] == "DRAFT"
        results.append("[OK] retrieve inspection")

        # 5) Capture positions reference list
        positions = c.get("/reference/capture-positions", headers=h1).json()["data"]
        assert positions["total"] == 12
        results.append("[OK] capture positions reference (12 codes)")

        # 6) Upload request
        ur = c.post(
            f"/inspection-sessions/{sid}/images/upload-request",
            headers=h1,
            json={
                "capturePosition": "CAPTURE_FRONT",
                "fileName": "front.jpg",
                "contentType": "image/jpeg",
                "fileSize": 2048,
            },
        ).json()["data"]
        assert ur["uploadUrl"].startswith("/api/v1/damage-intelligence/internal/storage/upload")
        results.append("[OK] upload-request (signed URL issued)")

        # 7) PUT image to signed URL
        fake_jpeg = b"\xff\xd8\xff\xe0" + b"SMOKETEST" * 200
        put_url = api_origin + ur["uploadUrl"]
        put = c.put(put_url, content=fake_jpeg, headers={"Content-Type": "image/jpeg"})
        assert put.status_code == 200 and put.json()["data"]["bytesStored"] == len(fake_jpeg)
        results.append(f"[OK] PUT to signed storage URL ({len(fake_jpeg)} bytes)")

        # 8) Register uploaded image
        reg = c.post(
            f"/inspection-sessions/{sid}/images",
            headers=h1,
            json={"uploadRequestId": ur["uploadRequestId"], "width": 1920, "height": 1080},
        ).json()["data"]
        assert reg["status"] == "REGISTERED" and reg["evidenceId"]
        evidence_id = reg["evidenceId"]
        results.append("[OK] register image")

        # 9) Idempotent re-registration returns same image
        reg2 = c.post(
            f"/inspection-sessions/{sid}/images",
            headers=h1,
            json={"uploadRequestId": ur["uploadRequestId"]},
        ).json()["data"]
        assert reg2["id"] == reg["id"]
        results.append("[OK] idempotent registration")

        # 10) List images
        imgs = c.get(f"/inspection-sessions/{sid}/images", headers=h1).json()["data"]
        assert imgs["total"] == 1 and imgs["items"][0]["status"] == "REGISTERED"
        results.append("[OK] list inspection images")

        # 11) Evidence access link + GET via signed link
        al = c.post(
            f"/evidence/{evidence_id}/access-link",
            headers=h1,
            json={"purpose": "smoke", "expiresInMinutes": 5},
        ).json()["data"]
        assert al["accessUrl"].startswith("/api/v1/damage-intelligence/internal/storage/access")
        access_resp = c.get(api_origin + al["accessUrl"])
        assert access_resp.status_code == 200 and access_resp.headers["content-type"].startswith("image/")
        results.append("[OK] evidence access link + signed GET")

        # 12) Cross-tenant denial: T2 must not access T1's evidence or session
        cross_session = c.get(f"/inspection-sessions/{sid}", headers=h2)
        assert cross_session.status_code == 404
        cross_ev = c.post(
            f"/evidence/{evidence_id}/access-link",
            headers=h2,
            json={"purpose": "sneaky"},
        )
        assert cross_ev.status_code == 404
        results.append("[OK] cross-tenant access denied (session + evidence)")

        # 13) Invalid status transition (PATCH SUBMITTED)
        bad = c.patch(
            f"/inspection-sessions/{sid}/status",
            headers=h1,
            json={"status": "SUBMITTED"},
        )
        assert bad.status_code == 409 and bad.json()["errors"][0]["code"] == "INVALID_STATUS_TRANSITION"
        results.append("[OK] invalid status transition rejected")

        # 14) Submit via POST /submit
        sub = c.post(f"/inspection-sessions/{sid}/submit", headers=h1).json()["data"]
        assert sub["status"] == "SUBMITTED" and sub["submittedAt"]
        results.append("[OK] submit inspection")

        # 15) Public unrestricted URL is prevented — direct access without a signature must fail
        unsigned = c.get(
            api_origin
            + f"/api/v1/damage-intelligence/internal/storage/access?path=tenants/{t1_tenant}/damage-intelligence/inspections/{sid}/images/{reg['id']}&exp=9999999999&sig=NOTASIGNATURE",
            timeout=10.0,
        )
        assert unsigned.status_code == 403
        results.append("[OK] unsigned/forged evidence URL rejected")

        # 16) Unknown routes still 404 (envelope shape preserved). Reports are live since Sprint 05.
        rv = c.get("/this-route-does-not-exist", headers=h1)
        assert rv.status_code == 404
        results.append("[OK] unknown route 404")

    print("\n".join(results))
    print("\nSprint 01 production inspection and evidence foundation smoke test passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
