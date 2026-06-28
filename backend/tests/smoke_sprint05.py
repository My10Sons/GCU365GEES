"""
Repository Traceability:
- Source Document: DI-SPRINT-05 §"Sprint 05 Smoke Test" (reports, monitoring, security, release).
- Purpose: End-to-end smoke for report generation/retrieval/access-link, evidence package,
  monitoring metrics + dependency health, controlled access (no public URLs), tenant isolation,
  authorization, and ownership-boundary preservation.

Run from /app/backend:
    /root/.venv/bin/python tests/smoke_sprint05.py
"""
import os
import sys
import uuid

import httpx


def base() -> str:
    return (os.environ.get("DI_SMOKE_BASE_URL") or "http://localhost:8001").rstrip("/") + "/api/v1/damage-intelligence"


def login(c, email, password):
    d = c.post("/auth/login", json={"email": email, "password": password}).json()["data"]
    return {"Authorization": f"Bearer {d['accessToken']}", "X-Tenant-Id": d["user"]["tenantId"]}, d["user"]["tenantId"]


def main() -> int:
    results: list[str] = []
    api_root = base()
    api_origin = api_root.rsplit("/api/v1/damage-intelligence", 1)[0]
    tag = uuid.uuid4().hex[:8].upper()

    with httpx.Client(base_url=api_root, timeout=180.0) as c:
        admin, tenant1 = login(c, os.environ["DI_SEED_ADMIN_EMAIL"], os.environ["DI_SEED_ADMIN_PASSWORD"])
        insp, _ = login(c, os.environ["DI_SEED_INSPECTOR_EMAIL"], os.environ["DI_SEED_INSPECTOR_PASSWORD"])
        admin2, tenant2 = login(c, os.environ["DI_SEED_ADMIN_EMAIL_2"], os.environ["DI_SEED_ADMIN_PASSWORD_2"])
        results.append(f"[OK] login admin + inspector + cross-tenant admin ({tenant1} / {tenant2})")

        # 1) Health + dependency health + monitoring metrics.
        assert c.get("/health").json()["data"]["status"] == "ok"
        deps = c.get("/monitoring/dependencies", headers=admin).json()["data"]
        assert deps["mongo"]["healthy"] is True
        metrics = c.get("/monitoring/metrics", headers=admin).json()["data"]
        assert "integration" in metrics and "workflow" in metrics and "security" in metrics
        results.append("[OK] health, dependency health, and monitoring metrics")

        # 2) Build a small inspection with an image (admin).
        sid = c.post("/inspection-sessions", headers=admin, json={
            "inspectionType": "CHECK_OUT", "sourceSystem": "DI-Web",
            "references": {"externalVehicleRef": f"VEH-S05-{tag}"},
        }).json()["data"]["id"]
        ur = c.post(f"/inspection-sessions/{sid}/images/upload-request", headers=admin, json={
            "capturePosition": "CAPTURE_FRONT", "fileName": "f.jpg", "contentType": "image/jpeg", "fileSize": 2048,
        }).json()["data"]
        c.put(api_origin + ur["uploadUrl"], content=b"\xff\xd8\xff\xe0" + b"S05" * 300,
              headers={"Content-Type": "image/jpeg"}).raise_for_status()
        c.post(f"/inspection-sessions/{sid}/images", headers=admin, json={"uploadRequestId": ur["uploadRequestId"]}).raise_for_status()
        results.append("[OK] inspection + evidence prepared")

        # 3) Generate an inspection summary report.
        rep = c.post("/reports", headers=admin, json={
            "reportType": "INSPECTION_SUMMARY_REPORT", "inspectionSessionId": sid,
        }).json()["data"]
        assert rep["status"] == "COMPLETED"
        report_id = rep["reportId"]
        results.append(f"[OK] inspection summary report generated ({report_id})")

        # 4) Generate an evidence package report.
        epkg = c.post("/reports", headers=admin, json={
            "reportType": "EVIDENCE_PACKAGE_REPORT", "inspectionSessionId": sid,
        }).json()["data"]
        assert epkg["status"] == "COMPLETED"
        results.append("[OK] evidence package report generated")

        # 5) Get + list reports.
        got = c.get(f"/reports/{report_id}", headers=admin).json()["data"]
        assert got["reportType"] == "INSPECTION_SUMMARY_REPORT"
        lst = c.get("/reports", headers=admin, params={"page": 1, "pageSize": 50}).json()["data"]
        assert lst["total"] >= 2
        # No public/unrestricted URLs or raw object paths leaked in metadata.
        blob = str(got) + str(lst)
        assert "objectPath" not in blob and "http://" not in blob and "https://" not in blob
        results.append("[OK] report get + list, no URL/path leak in metadata")

        # 6) Controlled, time-limited access link (signed; not a public URL).
        link = c.post(f"/reports/{report_id}/access-link", headers=admin, json={"purpose": "review"}).json()["data"]
        assert link["accessUrl"].startswith("/api/v1/damage-intelligence/internal/storage/access?")
        assert "sig=" in link["accessUrl"] and "exp=" in link["accessUrl"] and link["expiresInSeconds"] > 0
        # The signed link actually serves the report content.
        served = c.get(api_origin + link["accessUrl"])
        assert served.status_code == 200 and b"INSPECTION_SUMMARY_REPORT" in served.content
        results.append("[OK] controlled time-limited report access link works (signed)")

        # 7) Tampered signature is rejected.
        bad = c.get(api_origin + link["accessUrl"][:-3] + "000")
        assert bad.status_code == 403
        results.append("[OK] tampered report access link rejected (403)")

        # 8) Authorization: inspector lacks reports.generate -> 403.
        denied = c.post("/reports", headers=insp, json={"reportType": "INSPECTION_SUMMARY_REPORT", "inspectionSessionId": sid})
        assert denied.status_code in (401, 403)
        results.append(f"[OK] report generation denied for non-authorized role ({denied.status_code})")

        # 9) Tenant isolation: cross-tenant report get + access-link -> 404.
        assert c.get(f"/reports/{report_id}", headers=admin2).status_code == 404
        assert c.post(f"/reports/{report_id}/access-link", headers=admin2, json={}).status_code == 404
        results.append("[OK] cross-tenant report access denied (404)")

        # 10) Validation: missing required reference -> 400.
        v = c.post("/reports", headers=admin, json={"reportType": "DAMAGE_CASE_REPORT"})
        assert v.status_code == 400 and v.json()["errors"][0]["code"] == "VALIDATION_ERROR"
        results.append("[OK] report validation (missing reference -> 400)")

        # 11) Ownership boundary preserved in rental damage summary report content.
        ra = f"RA-S05-{tag}"
        c.post("/inspection-sessions", headers=admin, json={
            "inspectionType": "CHECK_IN", "sourceSystem": "GCU365-CROMS",
            "references": {"externalVehicleRef": f"VEH-S05-{tag}", "externalRentalAgreementRef": ra},
        }).raise_for_status()
        rsum = c.post("/reports", headers=admin, json={"reportType": "RENTAL_DAMAGE_SUMMARY_REPORT", "rentalAgreementId": ra}).json()["data"]
        rsum_link = c.post(f"/reports/{rsum['reportId']}/access-link", headers=admin, json={}).json()["data"]
        body = c.get(api_origin + rsum_link["accessUrl"]).content
        assert b"NOT_OWNED_BY_DAMAGE_INTELLIGENCE" in body
        results.append("[OK] rental damage summary report preserves ownership boundary")

        # 12) Monitoring reflects generated reports count increased.
        m2 = c.get("/monitoring/metrics", headers=admin).json()["data"]
        assert m2["reports"]["generated"] >= 3
        results.append(f"[OK] monitoring metrics reflect activity (reports={m2['reports']['generated']})")

    print("\n".join(results))
    print("\nSprint 05 production reports monitoring security and release smoke test passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
