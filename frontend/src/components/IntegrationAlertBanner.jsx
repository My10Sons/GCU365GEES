/*
 * Repository Traceability:
 * - DI-SPRINT-05 (Monitoring + Security signals). Lightweight ops banner that lights up when
 *   /monitoring/metrics reports idempotency conflicts or tenant-scope/unauthorized security
 *   events for the current tenant. Polls periodically; dismissible per session.
 */
import React, { useCallback, useEffect, useState } from "react";
import { AlertTriangle, X } from "lucide-react";
import { api } from "../lib/api";

export const IntegrationAlertBanner = () => {
  const [signals, setSignals] = useState(null);
  const [dismissed, setDismissed] = useState(false);

  const poll = useCallback(async () => {
    try {
      const { data } = await api.get("/monitoring/metrics");
      const m = data.data;
      setSignals({
        idempotencyConflicts: m.integration?.idempotencyConflicts || 0,
        handoffsRejected: m.integration?.maintenanceHandoffsRejected || 0,
        tenantScopeViolations: m.security?.tenantScopeViolations || 0,
        unauthorizedAttempts: m.security?.unauthorizedAttempts || 0,
      });
    } catch {
      /* non-blocking */
    }
  }, []);

  useEffect(() => {
    poll();
    const id = setInterval(poll, 60000);
    return () => clearInterval(id);
  }, [poll]);

  if (!signals || dismissed) return null;
  const items = [];
  if (signals.idempotencyConflicts > 0) items.push(`${signals.idempotencyConflicts} idempotency conflict(s)`);
  if (signals.tenantScopeViolations > 0) items.push(`${signals.tenantScopeViolations} tenant-scope violation(s)`);
  if (signals.unauthorizedAttempts > 0) items.push(`${signals.unauthorizedAttempts} unauthorized attempt(s)`);
  if (signals.handoffsRejected > 0) items.push(`${signals.handoffsRejected} rejected handoff(s)`);
  if (items.length === 0) return null;

  return (
    <div
      data-testid="integration-alert-banner"
      className="flex items-center gap-2 px-6 py-2 bg-amber400/10 border-b border-amber400/30 text-amber400 text-[12px]"
    >
      <AlertTriangle className="size-3.5 shrink-0" />
      <span className="font-medium">Integration / security attention:</span>
      <span className="text-amber400/90">{items.join(" · ")}</span>
      <a href="/" className="underline underline-offset-2 hover:text-amber400 ml-1">view dashboard</a>
      <button
        data-testid="integration-alert-dismiss"
        onClick={() => setDismissed(true)}
        className="ml-auto text-amber400/70 hover:text-amber400"
        aria-label="Dismiss"
      >
        <X className="size-3.5" />
      </button>
    </div>
  );
};
