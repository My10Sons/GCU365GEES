"""
Repository Traceability:
- Source Document: DI-SPRINT-04 §"Sprint 04 Smoke Test" (CROMS + Maintenance integration).
- Purpose: End-to-end smoke for CROMS check-out/check-in/damage-summary/status, idempotency
  (replay + conflict), Maintenance handoff/work-order/repair-status/rejection/additional-evidence,
  ownership-boundary assertions, auth + tenant isolation, and no-URL-leak checks.

Run from /app/backend:
    /root/.venv/bin/python tests/smoke_sprint04.py
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
    return {"Authorization": f"Bearer {d['accessToken']}", "X-Tenant-Id": d["user"]["tenantId"]}, d["user"]["tenantId"]


def main() -> int:
    results: list[str] = []
    api_root = base()
    api_origin = api_root.rsplit("/api/v1/damage-intelligence", 1)[0]
    tag = uuid.uuid4().hex[:8].upper()
    ra = f"RA-S04-{tag}"
    veh = f"VEH-S04-{tag}"

    with httpx.Client(base_url=api_root, timeout=180.0) as c:
        svc, tenant1 = login(c, os.environ["DI_SEED_INTEGRATION_EMAIL"], os.environ["DI_SEED_INTEGRATION_PASSWORD"])
        admin, _ = login(c, os.environ["DI_SEED_ADMIN_EMAIL"], os.environ["DI_SEED_ADMIN_PASSWORD"])
        svc2, tenant2 = login(c, os.environ["DI_SEED_INTEGRATION_EMAIL_2"], os.environ["DI_SEED_INTEGRATION_PASSWORD_2"])
        results.append(f"[OK] integration service + admin + cross-tenant service login ({tenant1} / {tenant2})")

        # 1) CROMS check-out (idempotent).
        k_co = f"{ra}-CHECKOUT"
        h_co = {**svc, "X-Idempotency-Key": k_co}
        co = c.post("/integrations/croms/check-out-inspections", headers=h_co, json={
            "rentalAgreementId": ra, "vehicleId": veh, "branchId": "BR-1", "requestedBySystem": "GCU365-CROMS",
        }).json()["data"]
        assert co["inspectionType"] == "CHECK_OUT" and co["status"] == "DRAFT", co
        co_session = co["inspectionSessionId"]
        results.append(f"[OK] CROMS check-out created session {co_session}")

        # 2) Duplicate check-out, same key + payload -> replay (same session, no duplicate).
        co_dup = c.post("/integrations/croms/check-out-inspections", headers=h_co, json={
            "rentalAgreementId": ra, "vehicleId": veh, "branchId": "BR-1", "requestedBySystem": "GCU365-CROMS",
        }).json()["data"]
        assert co_dup["inspectionSessionId"] == co_session, "idempotent replay must return same session"
        results.append("[OK] CROMS check-out idempotent replay (no duplicate)")

        # 3) Same key, different payload -> IDEMPOTENCY_CONFLICT.
        conflict = c.post("/integrations/croms/check-out-inspections", headers=h_co, json={
            "rentalAgreementId": ra, "vehicleId": veh + "-X", "requestedBySystem": "GCU365-CROMS",
        })
        assert conflict.status_code == 409 and conflict.json()["errors"][0]["code"] == "IDEMPOTENCY_CONFLICT", conflict.text
        results.append("[OK] idempotency conflict detected (409)")

        # 4) CROMS check-in with baseline link.
        ci = c.post("/integrations/croms/check-in-inspections",
                    headers={**svc, "X-Idempotency-Key": f"{ra}-CHECKIN"}, json={
            "rentalAgreementId": ra, "vehicleId": veh, "baselineInspectionSessionId": co_session,
            "requestedBySystem": "GCU365-CROMS",
        }).json()["data"]
        assert ci["inspectionType"] == "CHECK_IN" and ci["baselineInspectionSessionId"] == co_session, ci
        ci_session = ci["inspectionSessionId"]
        results.append(f"[OK] CROMS check-in created session {ci_session} (baseline linked)")

        # 5) CROMS rental damage summary -> never returns a final charge decision.
        summ = c.get(f"/integrations/croms/rental-agreements/{ra}/damage-summary", headers=svc).json()["data"]
        assert summ["finalCustomerChargeDecision"] == "NOT_OWNED_BY_DAMAGE_INTELLIGENCE", summ
        assert summ["checkOutInspectionSessionId"] == co_session
        assert summ["checkInInspectionSessionId"] == ci_session
        results.append(f"[OK] CROMS damage summary (status={summ['damageSummaryStatus']}, charge NOT owned)")

        # 6) CROMS inspection status.
        st = c.get(f"/integrations/croms/inspection-sessions/{co_session}/status", headers=svc).json()["data"]
        assert st["status"] == "DRAFT"
        results.append("[OK] CROMS inspection status")

        # 7) Build a damage case (admin) from a comparison result to drive Maintenance flows.
        ur = c.post(f"/inspection-sessions/{ci_session}/images/upload-request", headers=admin, json={
            "capturePosition": "CAPTURE_FRONT", "fileName": "f.jpg", "contentType": "image/jpeg", "fileSize": 2048,
        }).json()["data"]
        c.put(api_origin + ur["uploadUrl"], content=b"\xff\xd8\xff\xe0" + b"S04" * 400,
              headers={"Content-Type": "image/jpeg"}).raise_for_status()
        c.post(f"/inspection-sessions/{ci_session}/images", headers=admin,
               json={"uploadRequestId": ur["uploadRequestId"]}).raise_for_status()
        cmp_res = c.post(f"/inspection-sessions/{ci_session}/comparison", headers=admin, json={}).json()["data"]
        result_id = cmp_res["outcomes"][0]["comparisonResultId"]
        case = c.post("/damage-cases", headers=admin, json={
            "inspectionSessionId": ci_session, "comparisonResultIds": [result_id],
            "caseType": "REPAIR_RELEVANT", "severityCode": "HIGH",
        }).json()["data"]
        case_id = case["damageCaseId"]
        results.append(f"[OK] damage case prepared for handoff ({case_id})")

        # 8) Maintenance handoff (idempotent).
        k_ho = f"{case_id}-MAINTENANCE-HANDOFF"
        ho = c.post("/integrations/maintenance/handoffs",
                    headers={**svc, "X-Idempotency-Key": k_ho}, json={
            "damageCaseId": case_id, "vehicleId": veh, "severityCode": "HIGH",
            "evidencePackageReference": {"evidencePackageId": "DI-EPK-X"},
            "requestedBySystem": "DamageIntelligence",
        }).json()["data"]
        assert ho["status"] == "SENT" and ho["workOrderExecutionOwnedBy"] == "GCU365Maintenance", ho
        handoff_id = ho["maintenanceHandoffId"]
        ho_dup = c.post("/integrations/maintenance/handoffs",
                        headers={**svc, "X-Idempotency-Key": k_ho}, json={
            "damageCaseId": case_id, "vehicleId": veh, "severityCode": "HIGH",
            "evidencePackageReference": {"evidencePackageId": "DI-EPK-X"},
            "requestedBySystem": "DamageIntelligence",
        }).json()["data"]
        assert ho_dup["maintenanceHandoffId"] == handoff_id, "handoff idempotent replay"
        results.append("[OK] Maintenance handoff SENT + idempotent replay")

        # 9) Work order reference callback.
        wo = c.post("/integrations/maintenance/work-order-references", headers=svc, json={
            "damageCaseId": case_id, "maintenanceRequestId": "MNT-REQ-1", "workOrderId": "WO-1",
            "status": "WORK_ORDER_CREATED",
        }).json()["data"]
        assert wo["linked"] is True and wo["workOrderExecutionOwnedBy"] == "GCU365Maintenance"
        results.append("[OK] Maintenance work order reference linked (not owned)")

        # 10) Repair status callback -> actual cost stored as reference only.
        rs = c.post("/integrations/maintenance/repair-status-updates", headers=svc, json={
            "damageCaseId": case_id, "workOrderId": "WO-1", "repairStatus": "REPAIR_COMPLETED",
            "actualRepairCostReference": {"sourceSystem": "GCU365Maintenance", "referenceId": "MNT-COST-1"},
        }).json()["data"]
        assert rs["actualRepairCostOwnedBy"] == "GCU365Maintenance" and rs["postRepairInspectionRecommended"] is True
        results.append("[OK] Maintenance repair status (actual cost reference only, post-repair recommended)")

        # 11) Rejection + additional-evidence callbacks.
        c.post("/integrations/maintenance/rejection-reasons", headers=svc, json={
            "damageCaseId": case_id, "maintenanceRequestId": "MNT-REQ-1",
            "rejectionCode": "INSUFFICIENT_EVIDENCE", "rejectionReason": "Need close-up.",
            "requestedAdditionalEvidence": True,
        }).raise_for_status()
        aer = c.post("/integrations/maintenance/additional-evidence-requests", headers=svc, json={
            "damageCaseId": case_id, "reason": "Front bumper close-up required.",
        }).json()["data"]
        assert aer["status"] == "OPEN"
        results.append("[OK] Maintenance rejection + additional-evidence request recorded")

        # 12) Handoff status aggregation + no raw URL leak.
        hs = c.get(f"/integrations/maintenance/damage-cases/{case_id}/handoff-status", headers=svc).json()["data"]
        assert len(hs["handoffs"]) >= 1 and len(hs["references"]) >= 1 and len(hs["repairStatusUpdates"]) >= 1
        assert hs["actualRepairCostOwnedBy"] == "GCU365Maintenance"
        blob = str(hs) + str(summ)
        assert "objectPath" not in blob and "/internal/storage" not in blob
        results.append("[OK] handoff status aggregation + no raw evidence URLs")

        # 13) Security: admin (no integration perms) blocked from integration endpoints.
        denied = c.get(f"/integrations/croms/rental-agreements/{ra}/damage-summary", headers=admin)
        assert denied.status_code in (401, 403), denied.status_code
        results.append(f"[OK] non-integration principal rejected ({denied.status_code})")

        # 14) Cross-tenant isolation: tenant2 service cannot see tenant1 data.
        x1 = c.get(f"/integrations/croms/rental-agreements/{ra}/damage-summary", headers=svc2)
        x2 = c.get(f"/integrations/croms/inspection-sessions/{co_session}/status", headers=svc2)
        x3 = c.get(f"/integrations/maintenance/damage-cases/{case_id}/handoff-status", headers=svc2)
        assert x1.status_code == 404 and x2.status_code == 404 and x3.status_code == 404
        results.append("[OK] cross-tenant integration access denied (404)")

        # 15) Maintenance handoff on a missing case -> 404.
        miss = c.post("/integrations/maintenance/handoffs", headers=svc,
                      json={"damageCaseId": "0123456789abcdef01234567"})
        assert miss.status_code == 404
        results.append("[OK] handoff on unknown damage case -> 404")

    print("\n".join(results))
    print("\nSprint 04 production CROMS and Maintenance integration smoke test passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
