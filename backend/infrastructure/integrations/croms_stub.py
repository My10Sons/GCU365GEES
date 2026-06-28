"""
Repository Traceability:
- Source Documents: DI-0017 (Integration with CROMS), DI-SPRINT-00 (Integration Stub
  Setup — CROMS stub preserving ownership boundaries).
- Purpose: Outbound CROMS client stub. Real wiring is Sprint 04 scope.
"""
from __future__ import annotations

from datetime import datetime, timezone


class CromsClientStub:
    """Sprint 00 stub. CROMS owns rental lifecycle, rental closure, and final customer charge."""

    async def notify_damage_summary_ready(
        self, *, tenant_id: str, rental_agreement_id: str, damage_summary_ref: str, correlation_id: str
    ) -> dict:
        return {
            "delivered": False,
            "stub": True,
            "tenantId": tenant_id,
            "rentalAgreementId": rental_agreement_id,
            "damageSummaryRef": damage_summary_ref,
            "correlationId": correlation_id,
            "queuedAt": datetime.now(timezone.utc).isoformat(),
            "note": "CROMS integration is wired in Sprint 04.",
        }
