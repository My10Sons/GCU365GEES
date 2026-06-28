"""
Repository Traceability:
- Source Document: DI-SPRINT-02 §"Sprint 02 Smoke Test" (production-ready AI foundation).
- Purpose: End-to-end smoke for Sprint 02 image quality + AI advisory damage detection.

Run from /app/backend:
    /root/.venv/bin/python tests/smoke_sprint02.py
"""
import os
import sys
import httpx


def base() -> str:
    return (os.environ.get("DI_SMOKE_BASE_URL") or "http://localhost:8001").rstrip("/") + "/api/v1/damage-intelligence"


def login(c, email, password):
    r = c.post("/auth/login", json={"email": email, "password": password})
    r.raise_for_status()
    d = r.json()["data"]
    return d["accessToken"], d["user"]["tenantId"]


def main() -> int:
    results: list[str] = []
    api_root = base()
    api_origin = api_root.rsplit("/api/v1/damage-intelligence", 1)[0]

    with httpx.Client(base_url=api_root, timeout=120.0) as c:
        t1, tenant1 = login(c, os.environ["DI_SEED_ADMIN_EMAIL"], os.environ["DI_SEED_ADMIN_PASSWORD"])
        t2, tenant2 = login(c, os.environ["DI_SEED_ADMIN_EMAIL_2"], os.environ["DI_SEED_ADMIN_PASSWORD_2"])
        h1 = {"Authorization": f"Bearer {t1}", "X-Tenant-Id": tenant1}
        h2 = {"Authorization": f"Bearer {t2}", "X-Tenant-Id": tenant2}
        results.append(f"[OK] login both tenants ({tenant1} & {tenant2})")

        # 1) Thresholds default
        r = c.get("/configuration/ai-thresholds", headers=h1).json()["data"]
        assert r["confidenceThreshold"] == 0.7 or r["isTenantOverride"] is True
        results.append(f"[OK] thresholds default ({r['confidenceThreshold']}, isOverride={r['isTenantOverride']})")

        # 2) Threshold update
        c.put("/configuration/ai-thresholds", headers=h1, json={"confidenceThreshold": 0.6}).raise_for_status()
        results.append("[OK] threshold update")

        # 3) Threshold validation 422 bounds → 400
        bad = c.put("/configuration/ai-thresholds", headers=h1, json={"confidenceThreshold": 1.5})
        assert bad.status_code == 400 and bad.json()["errors"][0]["code"] == "VALIDATION_ERROR"
        results.append("[OK] threshold validation (>1 returns 400)")

        # 4) Set up an inspection + upload one tiny fake image (sufficient to exercise the chain;
        #    Gemini will produce ERROR/0 findings on synthetic data — that's correct).
        create = c.post("/inspection-sessions", headers=h1, json={
            "inspectionType": "CHECK_OUT", "sourceSystem": "DI-Web",
            "references": {"externalVehicleRef": "VEH-S02-SMOKE-001"},
        }).json()["data"]
        sid = create["id"]
        ur = c.post(f"/inspection-sessions/{sid}/images/upload-request", headers=h1, json={
            "capturePosition": "CAPTURE_FRONT", "fileName": "f.jpg", "contentType": "image/jpeg", "fileSize": 2048,
        }).json()["data"]
        body = b"\xff\xd8\xff\xe0" + b"S02SMOKE" * 200
        c.put(api_origin + ur["uploadUrl"], content=body, headers={"Content-Type": "image/jpeg"}).raise_for_status()
        reg = c.post(f"/inspection-sessions/{sid}/images", headers=h1, json={"uploadRequestId": ur["uploadRequestId"]}).json()["data"]
        image_id = reg["id"]
        results.append(f"[OK] prep: created session {sid} + registered image {image_id}")

        # 5) Image quality check (real Gemini call)
        q = c.post(f"/images/{image_id}/quality-check", headers=h1).json()["data"]
        assert q["isAdvisory"] is True
        assert q["modelVersion"].startswith("gemini:")
        assert "qualityStatus" in q
        results.append(f"[OK] image quality check (status={q['qualityStatus']}, model={q['modelVersion']})")

        # 6) Latest quality result
        q2 = c.get(f"/images/{image_id}/quality-result", headers=h1).json()["data"]
        assert q2.get("isAdvisory") is True
        results.append("[OK] image quality result retrieval")

        # 7) Cross-tenant denied
        cross = c.post(f"/images/{image_id}/quality-check", headers=h2)
        assert cross.status_code == 404
        results.append("[OK] cross-tenant quality check denied")

        # 8) AI analysis on the session (real Gemini call)
        an = c.post(f"/inspection-sessions/{sid}/ai-analysis", headers=h1).json()["data"]
        assert an["isAdvisory"] is True
        assert an["modelVersion"].startswith("gemini:")
        assert an["totalImages"] == 1
        aid = an["id"]
        results.append(f"[OK] AI analysis run (status={an['status']}, model={an['modelVersion']}, findings={an['totalFindings']})")

        # 9) Get analysis
        get_an = c.get(f"/ai-analysis/{aid}", headers=h1).json()["data"]
        assert get_an["isAdvisory"] is True
        results.append("[OK] AI analysis get")

        # 10) Get findings
        findings = c.get(f"/ai-analysis/{aid}/findings", headers=h1).json()["data"]
        assert findings["isAdvisory"] is True
        results.append(f"[OK] AI analysis findings (total={findings['total']})")

        # 11) Cross-tenant denied for findings
        cross2 = c.get(f"/ai-analysis/{aid}/findings", headers=h2)
        assert cross2.status_code == 404
        results.append("[OK] cross-tenant findings denied")

        # 12) Session-level AI findings
        sf = c.get(f"/inspection-sessions/{sid}/ai-findings", headers=h1).json()["data"]
        assert sf["isAdvisory"] is True
        results.append("[OK] session-level AI findings")

        # 13) Retry
        re_an = c.post(f"/ai-analysis/{aid}/retry", headers=h1).json()["data"]
        assert re_an["isAdvisory"] is True
        results.append("[OK] AI analysis retry")

        # 14) Reports remain out-of-scope until Sprint 05 (404). Comparison/review/cases now exist (Sprint 03).
        assert c.get("/reports", headers=h1).status_code == 404
        results.append("[OK] reports out-of-scope (Sprint 05) still 404")

    print("\n".join(results))
    print("\nSprint 02 production image quality + AI detection smoke test passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
