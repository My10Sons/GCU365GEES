"""
TASK-07: Targeted regression for the NEW "closing-the-loop" feature added in
`integration_service._latest_report`, `croms_damage_summary`, `maintenance_handoff`.

Confirms:
  * CROMS damage-summary auto-links the latest RENTAL_DAMAGE_SUMMARY_REPORT
    (reportReference) and EVIDENCE_PACKAGE_REPORT (evidencePackageReference)
    after they are generated for a rental agreement.
  * Maintenance handoff (no caller-supplied refs) auto-populates
    evidencePackageReference (latest EVIDENCE_PACKAGE_REPORT for the case's
    inspection session) AND reportReference (latest DAMAGE_CASE_REPORT for the
    case).
  * Idempotent replay returns the same stored response (same references).
  * Caller-supplied evidencePackageReference is preserved (not overwritten by
    the auto-link logic).

Run from /app/backend:
    DI_SMOKE_BASE_URL=$REACT_APP_BACKEND_URL /root/.venv/bin/python tests/test_closing_the_loop.py
"""
from __future__ import annotations

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
    return {"Authorization": f"Bearer {d['accessToken']}", "X-Tenant-Id": d["user"]["tenantId"]}, d["user"]["tenantId"]


def main() -> int:
    results: list[str] = []
    api_root = base()
    api_origin = api_root.rsplit("/api/v1/damage-intelligence", 1)[0]
    tag = uuid.uuid4().hex[:8].upper()
    ra = f"RA-CTL-{tag}"
    veh = f"VEH-CTL-{tag}"

    with httpx.Client(base_url=api_root, timeout=180.0) as c:
        admin, tenant1 = login(c, os.environ["DI_SEED_ADMIN_EMAIL"], os.environ["DI_SEED_ADMIN_PASSWORD"])
        svc, _ = login(c, os.environ["DI_SEED_INTEGRATION_EMAIL"], os.environ["DI_SEED_INTEGRATION_PASSWORD"])
        results.append(f"[OK] login admin + integration service (tenant={tenant1})")

        # 1) Build CHECK_OUT + CHECK_IN sessions linked to a rental agreement.
        co_sid = c.post("/integrations/croms/check-out-inspections",
                        headers={**svc, "X-Idempotency-Key": f"{ra}-CO"},
                        json={"rentalAgreementId": ra, "vehicleId": veh, "branchId": "BR-1",
                              "requestedBySystem": "GCU365-CROMS"}).json()["data"]["inspectionSessionId"]
        ci_sid = c.post("/integrations/croms/check-in-inspections",
                        headers={**svc, "X-Idempotency-Key": f"{ra}-CI"},
                        json={"rentalAgreementId": ra, "vehicleId": veh,
                              "baselineInspectionSessionId": co_sid,
                              "requestedBySystem": "GCU365-CROMS"}).json()["data"]["inspectionSessionId"]
        results.append(f"[OK] CROMS check-out/check-in sessions ({co_sid} / {ci_sid})")

        # 2) BEFORE report generation -> CROMS damage-summary returns reportReference=None
        summ_before = c.get(f"/integrations/croms/rental-agreements/{ra}/damage-summary", headers=svc).json()["data"]
        assert summ_before["reportReference"] is None, summ_before
        assert summ_before["evidencePackageReference"] is None, summ_before
        results.append("[OK] damage-summary before reports: reportReference + evidencePackageReference are null")

        # 3) Upload one image to the check-in session so EVIDENCE_PACKAGE_REPORT has content.
        ur = c.post(f"/inspection-sessions/{ci_sid}/images/upload-request", headers=admin, json={
            "capturePosition": "CAPTURE_FRONT", "fileName": "f.jpg",
            "contentType": "image/jpeg", "fileSize": 2048,
        }).json()["data"]
        c.put(api_origin + ur["uploadUrl"],
              content=b"\xff\xd8\xff\xe0" + b"CTL" * 300,
              headers={"Content-Type": "image/jpeg"}).raise_for_status()
        c.post(f"/inspection-sessions/{ci_sid}/images", headers=admin,
               json={"uploadRequestId": ur["uploadRequestId"]}).raise_for_status()
        results.append("[OK] image registered on check-in session")

        # 4) Generate RENTAL_DAMAGE_SUMMARY_REPORT + EVIDENCE_PACKAGE_REPORT.
        rsum = c.post("/reports", headers=admin, json={
            "reportType": "RENTAL_DAMAGE_SUMMARY_REPORT", "rentalAgreementId": ra,
        }).json()["data"]
        assert rsum["status"] == "COMPLETED", rsum
        epkg = c.post("/reports", headers=admin, json={
            "reportType": "EVIDENCE_PACKAGE_REPORT", "inspectionSessionId": ci_sid,
        }).json()["data"]
        assert epkg["status"] == "COMPLETED", epkg
        results.append(f"[OK] generated rental-summary={rsum['reportId']} + evidence-package={epkg['reportId']}")

        # 5) AFTER report generation -> CROMS damage-summary auto-links both references.
        summ_after = c.get(f"/integrations/croms/rental-agreements/{ra}/damage-summary", headers=svc).json()["data"]
        assert summ_after["reportReference"] is not None, summ_after
        assert summ_after["reportReference"]["reportId"] == rsum["reportId"], summ_after["reportReference"]
        assert summ_after["reportReference"]["reportType"] == "RENTAL_DAMAGE_SUMMARY_REPORT"
        assert summ_after["evidencePackageReference"] is not None, summ_after
        assert summ_after["evidencePackageReference"]["reportId"] == epkg["reportId"], summ_after["evidencePackageReference"]
        assert summ_after["evidencePackageReference"]["reportType"] == "EVIDENCE_PACKAGE_REPORT"
        # Ownership boundary still preserved.
        assert summ_after["finalCustomerChargeDecision"] == "NOT_OWNED_BY_DAMAGE_INTELLIGENCE"
        # No raw URL/path leak.
        blob = str(summ_after)
        assert "objectPath" not in blob and "http://" not in blob and "https://" not in blob
        results.append("[OK] CROMS damage-summary auto-links reportReference + evidencePackageReference")

        # 6) Build a damage case off the check-in session (comparison + create).
        cmp_res = c.post(f"/inspection-sessions/{ci_sid}/comparison", headers=admin, json={}).json()["data"]
        result_id = cmp_res["outcomes"][0]["comparisonResultId"]
        case_id = c.post("/damage-cases", headers=admin, json={
            "inspectionSessionId": ci_sid, "comparisonResultIds": [result_id],
            "caseType": "REPAIR_RELEVANT", "severityCode": "HIGH",
        }).json()["data"]["damageCaseId"]
        results.append(f"[OK] damage case prepared ({case_id})")

        # 7) Generate a DAMAGE_CASE_REPORT for the case so handoff can auto-link reportReference.
        dcr = c.post("/reports", headers=admin, json={
            "reportType": "DAMAGE_CASE_REPORT", "damageCaseId": case_id,
        }).json()["data"]
        assert dcr["status"] == "COMPLETED", dcr
        results.append(f"[OK] damage case report generated ({dcr['reportId']})")

        # 8) Maintenance handoff WITHOUT caller-supplied evidencePackageReference ->
        #    expect both refs auto-populated.
        k_ho = f"{case_id}-CTL-AUTO"
        ho = c.post("/integrations/maintenance/handoffs",
                    headers={**svc, "X-Idempotency-Key": k_ho},
                    json={"damageCaseId": case_id, "vehicleId": veh, "severityCode": "HIGH",
                          "requestedBySystem": "DamageIntelligence"}).json()["data"]
        assert ho["status"] == "SENT", ho
        assert ho["evidencePackageReference"] is not None, ho
        assert ho["evidencePackageReference"]["reportId"] == epkg["reportId"], ho["evidencePackageReference"]
        assert ho["evidencePackageReference"]["reportType"] == "EVIDENCE_PACKAGE_REPORT"
        assert ho["reportReference"] is not None, ho
        assert ho["reportReference"]["reportId"] == dcr["reportId"], ho["reportReference"]
        assert ho["reportReference"]["reportType"] == "DAMAGE_CASE_REPORT"
        results.append("[OK] Maintenance handoff auto-populated evidencePackageReference + reportReference")

        # 9) Idempotent replay -> exact same stored response (same handoffId + refs).
        ho_replay = c.post("/integrations/maintenance/handoffs",
                           headers={**svc, "X-Idempotency-Key": k_ho},
                           json={"damageCaseId": case_id, "vehicleId": veh, "severityCode": "HIGH",
                                 "requestedBySystem": "DamageIntelligence"}).json()["data"]
        assert ho_replay["maintenanceHandoffId"] == ho["maintenanceHandoffId"], ho_replay
        assert ho_replay["evidencePackageReference"] == ho["evidencePackageReference"], ho_replay
        assert ho_replay["reportReference"] == ho["reportReference"], ho_replay
        results.append("[OK] Maintenance handoff idempotent replay returns same stored refs")

        # 10) New handoff (new idempotency key) with caller-supplied evidencePackageReference
        #     -> caller's value MUST be preserved, reportReference still auto-linked.
        caller_evidence = {"evidencePackageId": "EXT-EPK-CTL-OVERRIDE"}
        k_ho2 = f"{case_id}-CTL-OVERRIDE"
        ho2 = c.post("/integrations/maintenance/handoffs",
                     headers={**svc, "X-Idempotency-Key": k_ho2},
                     json={"damageCaseId": case_id, "vehicleId": veh, "severityCode": "HIGH",
                           "evidencePackageReference": caller_evidence,
                           "requestedBySystem": "DamageIntelligence"}).json()["data"]
        assert ho2["evidencePackageReference"] == caller_evidence, ho2
        assert ho2["reportReference"] is not None and ho2["reportReference"]["reportId"] == dcr["reportId"], ho2
        results.append("[OK] caller-supplied evidencePackageReference is preserved; reportReference still auto-linked")

        # 11) Handoff status aggregation reflects both handoffs and contains no raw URL/path leaks.
        hs = c.get(f"/integrations/maintenance/damage-cases/{case_id}/handoff-status", headers=svc).json()["data"]
        assert len(hs["handoffs"]) >= 2, hs
        blob = str(hs)
        assert "objectPath" not in blob and "/internal/storage" not in blob, "no raw URL/path leaks"
        results.append("[OK] handoff status aggregation reflects both handoffs, no URL leaks")

    print("\n".join(results))
    print("\nClosing-the-loop (CROMS damage-summary + Maintenance handoff auto-link) regression PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
