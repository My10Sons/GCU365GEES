"""
Repository Traceability:
- Source Document: DI-SPRINT-03 §"Sprint 03 Smoke Test" (production review, comparison,
  damage cases).
- Purpose: End-to-end smoke for comparison, review queue, decisions, additional-evidence,
  damage cases + status lifecycle, duplicate prevention, per-vehicle strip, tenant isolation.

Run from /app/backend:
    /root/.venv/bin/python tests/smoke_sprint03.py
"""
import os
import sys
import uuid

import httpx


def base() -> str:
    return (os.environ.get("DI_SMOKE_BASE_URL") or "http://localhost:8001").rstrip("/") + "/api/v1/damage-intelligence"


def login(c, email, password):
    r = c.post("/auth/login", json={"email": email, "password": password})
    r.raise_for_status()
    d = r.json()["data"]
    return d["accessToken"], d["user"]["tenantId"]


def make_session(c, h, api_origin, vehicle_ref, submit=False):
    sid = c.post("/inspection-sessions", headers=h, json={
        "inspectionType": "CHECK_OUT", "sourceSystem": "DI-Web",
        "references": {"externalVehicleRef": vehicle_ref},
    }).json()["data"]["id"]
    ur = c.post(f"/inspection-sessions/{sid}/images/upload-request", headers=h, json={
        "capturePosition": "CAPTURE_FRONT", "fileName": "f.jpg", "contentType": "image/jpeg", "fileSize": 2048,
    }).json()["data"]
    body = b"\xff\xd8\xff\xe0" + b"S03SMOKE" * 200
    c.put(api_origin + ur["uploadUrl"], content=body, headers={"Content-Type": "image/jpeg"}).raise_for_status()
    c.post(f"/inspection-sessions/{sid}/images", headers=h, json={"uploadRequestId": ur["uploadRequestId"]}).raise_for_status()
    if submit:
        c.post(f"/inspection-sessions/{sid}/submit", headers=h).raise_for_status()
    return sid


def main() -> int:
    results: list[str] = []
    api_root = base()
    api_origin = api_root.rsplit("/api/v1/damage-intelligence", 1)[0]
    tag = uuid.uuid4().hex[:8].upper()

    with httpx.Client(base_url=api_root, timeout=180.0) as c:
        t1, tenant1 = login(c, os.environ["DI_SEED_ADMIN_EMAIL"], os.environ["DI_SEED_ADMIN_PASSWORD"])
        t2, tenant2 = login(c, os.environ["DI_SEED_ADMIN_EMAIL_2"], os.environ["DI_SEED_ADMIN_PASSWORD_2"])
        h1 = {"Authorization": f"Bearer {t1}", "X-Tenant-Id": tenant1}
        h2 = {"Authorization": f"Bearer {t2}", "X-Tenant-Id": tenant2}
        results.append(f"[OK] login both tenants ({tenant1} & {tenant2})")

        # 1) Comparison with NO baseline -> NOT_COMPARABLE, auto-routes a review item.
        veh_a = f"VEH-S03-{tag}-A"
        cur = make_session(c, h1, api_origin, veh_a)
        cmp1 = c.post(f"/inspection-sessions/{cur}/comparison", headers=h1, json={}).json()["data"]
        assert cmp1["status"] == "NOT_COMPARABLE", cmp1["status"]
        assert cmp1["notComparableReason"], cmp1
        assert len(cmp1["outcomes"]) >= 1
        comparison_id = cmp1["comparisonId"]
        result_id = cmp1["outcomes"][0]["comparisonResultId"]
        results.append(f"[OK] missing-baseline comparison NOT_COMPARABLE (reason={cmp1['notComparableReason']}, routed={cmp1['reviewItemsRouted']})")

        # 2) Get comparison + cross-tenant denied.
        got = c.get(f"/comparisons/{comparison_id}", headers=h1).json()["data"]
        assert got["isAdvisory"] is True
        assert c.get(f"/comparisons/{comparison_id}", headers=h2).status_code == 404
        results.append("[OK] comparison get + cross-tenant 404")

        # 3) Review queue shows the auto-routed comparison item.
        queue = c.get("/review-queue", headers=h1, params={"inspectionSessionId": cur}).json()["data"]
        items = [i for i in queue["items"] if i["objectType"] == "COMPARISON_RESULT"]
        assert items, queue
        review_item_id = items[0]["reviewItemId"]
        results.append(f"[OK] review queue auto-routed item present (total={queue['total']})")

        # 4) Review item get + cross-tenant denied.
        ri = c.get(f"/review-items/{review_item_id}", headers=h1).json()["data"]
        assert ri["objectId"] == result_id
        assert c.get(f"/review-items/{review_item_id}", headers=h2).status_code == 404
        results.append("[OK] review item get + cross-tenant 404")

        # 5) Decision requiring reason without reason -> 400.
        bad = c.post(f"/review-items/{review_item_id}/decision", headers=h1, json={"decisionCode": "REJECTED"})
        assert bad.status_code == 400 and bad.json()["errors"][0]["code"] == "VALIDATION_ERROR"
        results.append("[OK] decision reason-required validation (400)")

        # 6) Additional evidence request.
        aer = c.post(f"/review-items/{review_item_id}/additional-evidence-request", headers=h1,
                     json={"reason": "Need a clearer rear shot."}).json()["data"]
        assert aer["status"] == "OPEN"
        results.append("[OK] additional-evidence request")

        # 7) Record CONFIRMED decision.
        dec = c.post(f"/review-items/{review_item_id}/decision", headers=h1,
                     json={"decisionCode": "CONFIRMED", "reason": "Confirmed for case context."}).json()["data"]
        assert dec["reviewStatus"] == "DECIDED"
        results.append("[OK] review decision CONFIRMED recorded")

        # 8) Create damage case from the comparison result.
        case = c.post("/damage-cases", headers=h1, json={
            "inspectionSessionId": cur, "comparisonResultIds": [result_id],
            "caseType": "REPAIR_RELEVANT", "severityCode": "MEDIUM",
            "description": "Smoke case from comparison.",
        }).json()["data"]
        case_id = case["damageCaseId"]
        assert case["status"] == "OPEN"
        assert len(case["links"]) >= 1
        results.append(f"[OK] damage case created ({case_id}, status=OPEN)")

        # 9) Duplicate prevention -> 409.
        dup = c.post("/damage-cases", headers=h1, json={
            "inspectionSessionId": cur, "comparisonResultIds": [result_id],
            "caseType": "REPAIR_RELEVANT",
        })
        assert dup.status_code == 409 and dup.json()["errors"][0]["code"] == "CONFLICT"
        results.append("[OK] duplicate damage case prevented (409)")

        # 10) Status lifecycle OPEN -> REVIEWED -> CLOSED, with history.
        c.patch(f"/damage-cases/{case_id}/status", headers=h1, json={"status": "REVIEWED"}).raise_for_status()
        bad_close = c.patch(f"/damage-cases/{case_id}/status", headers=h1, json={"status": "CLOSED"})
        assert bad_close.status_code == 400, "CLOSED requires a reason"
        closed = c.patch(f"/damage-cases/{case_id}/status", headers=h1,
                         json={"status": "CLOSED", "reason": "Resolved in smoke."}).json()["data"]
        assert closed["status"] == "CLOSED"
        assert len(closed["statusHistory"]) >= 3
        results.append("[OK] damage case status lifecycle + history + reason enforcement")

        # 11) Invalid transition on terminal case -> 409.
        bad_tr = c.patch(f"/damage-cases/{case_id}/status", headers=h1, json={"status": "OPEN"})
        assert bad_tr.status_code == 409
        results.append("[OK] terminal case transition blocked (409)")

        # 12) Cross-tenant case get denied.
        assert c.get(f"/damage-cases/{case_id}", headers=h2).status_code == 404
        results.append("[OK] cross-tenant damage case 404")

        # 13) Baseline-anchored comparison (real Gemini multi-image call).
        veh_b = f"VEH-S03-{tag}-B"
        make_session(c, h1, api_origin, veh_b, submit=True)  # baseline (submitted)
        cur_b = make_session(c, h1, api_origin, veh_b)        # current
        cmp2 = c.post(f"/inspection-sessions/{cur_b}/comparison", headers=h1, json={}).json()["data"]
        assert cmp2["baselineInspectionSessionId"], "auto-anchor should pick the prior submitted inspection"
        assert cmp2["status"] in ("COMPLETED", "COMPLETED_WITH_WARNINGS", "NOT_COMPARABLE"), cmp2["status"]
        results.append(f"[OK] baseline auto-anchor comparison (status={cmp2['status']}, model={cmp2['modelVersion']})")

        # 14) Per-vehicle evidence strip (DI-0037) — prior evidence for same vehicle, no raw URLs.
        cur_b2 = make_session(c, h1, api_origin, veh_b)
        strip = c.get(f"/inspection-sessions/{cur_b2}/per-vehicle-strip", headers=h1, params={"limit": 12}).json()["data"]
        assert strip["isAdvisory"] is True
        assert strip["total"] >= 1, strip
        for it in strip["items"]:
            assert "objectPath" not in it and "accessUrl" not in it
        results.append(f"[OK] per-vehicle evidence strip ({strip['total']} prior items, no raw URLs)")

        # 15) No public evidence URL leaks in comparison/case payloads.
        for payload in (got, closed):
            blob = str(payload)
            assert "objectPath" not in blob and "/internal/storage" not in blob
        results.append("[OK] no raw object paths / unrestricted URLs in payloads")

        # 16) AI auto-route field present on analysis run.
        an = c.post(f"/inspection-sessions/{cur_b}/ai-analysis", headers=h1).json()["data"]
        assert "reviewItemsRouted" in an
        results.append(f"[OK] AI analysis auto-route field present (routed={an['reviewItemsRouted']})")

    print("\n".join(results))
    print("\nSprint 03 production review comparison and damage cases smoke test passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
