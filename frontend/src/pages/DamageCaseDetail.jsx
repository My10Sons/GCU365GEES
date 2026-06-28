/*
 * Repository Traceability:
 * - DI-SPRINT-03 (Damage case detail, status update + history, links), DI-0012, DI-0034.
 */
import React, { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ArrowLeft, Loader2, ShieldCheck } from "lucide-react";
import { casesApi } from "../lib/sprint03-api";
import { envelopeError } from "../lib/api";
import { useAuth } from "../lib/auth-context";
import { T } from "../constants/testIds";

const STATUSES = ["PENDING_REVIEW", "REVIEWED", "ADDITIONAL_EVIDENCE_REQUIRED",
  "READY_FOR_MAINTENANCE_REVIEW", "ROUTED_TO_MAINTENANCE", "CLOSED", "CANCELLED", "REJECTED"];

function Row({ label, value }) {
  return (
    <div className="flex gap-3 items-baseline">
      <dt className="text-[11px] uppercase tracking-wider text-steel-400 w-28 shrink-0">{label}</dt>
      <dd className="font-mono text-[12px] text-steel-100 flex-1 break-all">{value ?? "—"}</dd>
    </div>
  );
}

function fmt(d) {
  if (!d) return "—";
  try { return new Date(d).toLocaleString(); } catch { return d; }
}

export default function DamageCaseDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { has } = useAuth();
  const canUpdate = has("di.damagecases.update");

  const [item, setItem] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [su, setSu] = useState({ status: "PENDING_REVIEW", reason: "", busy: false, error: "" });

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      setItem(await casesApi.get(id));
    } catch (err) {
      setError(envelopeError(err, "Could not load damage case."));
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => { load(); }, [load]);

  const submitStatus = async () => {
    setSu((s) => ({ ...s, busy: true, error: "" }));
    try {
      const updated = await casesApi.updateStatus(id, { status: su.status, reason: su.reason || undefined });
      setItem(updated);
      setSu((s) => ({ ...s, busy: false, reason: "" }));
    } catch (err) {
      setSu((s) => ({ ...s, busy: false, error: envelopeError(err, "Status update failed.") }));
    }
  };

  if (loading) return <div className="px-8 py-10 text-steel-300 text-sm">Loading damage case…</div>;
  if (error || !item) return (
    <div className="px-8 py-10 max-w-2xl">
      <button onClick={() => navigate("/cases")} className="text-sm text-steel-300 hover:text-white mb-4 flex items-center gap-1.5">
        <ArrowLeft className="size-3.5" /> Back to damage cases
      </button>
      <div className="text-sm text-signal-soft bg-signal/10 border border-signal/30 rounded-md px-3 py-2">{error || "Not found."}</div>
    </div>
  );

  return (
    <div data-testid={T.caseDetailRoot} className="px-8 py-8 max-w-5xl">
      <button onClick={() => navigate("/cases")} data-testid={T.caseDetailBack}
        className="text-xs text-steel-300 hover:text-white mb-3 flex items-center gap-1.5">
        <ArrowLeft className="size-3.5" /> Back to damage cases
      </button>
      <div className="flex items-center gap-3 mb-6">
        <h1 className="text-xl font-semibold text-white font-mono">{item.externalVehicleRef || "—"}</h1>
        <span className="text-[11px] font-mono text-steel-400">{item.status} · {item.caseType}</span>
      </div>

      <section className="grid grid-cols-1 lg:grid-cols-2 gap-3 mb-6">
        <div className="rounded-lg border border-ink-700/70 bg-ink-900/60 p-5">
          <div className="text-[11px] uppercase tracking-wider text-steel-400 mb-3">Case</div>
          <dl className="space-y-2">
            <Row label="Status" value={item.status} />
            <Row label="Type" value={item.caseType} />
            <Row label="Severity" value={item.severityCode} />
            <Row label="Inspection" value={item.inspectionSessionId} />
            <Row label="Description" value={item.description} />
            <Row label="Created" value={fmt(item.createdAt)} />
          </dl>
          <p className="text-[11px] text-steel-400 mt-3 leading-relaxed flex items-start gap-1.5">
            <ShieldCheck className="size-3.5 mt-0.5 text-emerald-400" /> {item.ownershipNote}
          </p>
        </div>
        <div className="rounded-lg border border-ink-700/70 bg-ink-900/60 p-5">
          <div className="text-[11px] uppercase tracking-wider text-steel-400 mb-3">Links ({item.links?.length || 0})</div>
          <ul className="space-y-1.5">
            {(item.links || []).map((l, i) => (
              <li key={i} className="font-mono text-[11px] text-steel-300">
                <span className="text-steel-400">{l.linkType}</span> · {l.linkedId}
              </li>
            ))}
            {(item.links || []).length === 0 && <li className="text-[12px] text-steel-400">No links.</li>}
          </ul>
        </div>
      </section>

      {canUpdate && (
        <section className="rounded-lg border border-ink-700/70 bg-ink-900/60 p-5 mb-6">
          <h2 className="text-sm font-semibold text-white mb-3">Update status</h2>
          <div className="flex flex-wrap items-center gap-2 mb-3">
            <select data-testid={T.caseStatusSelect} value={su.status}
              onChange={(e) => setSu((s) => ({ ...s, status: e.target.value }))}
              className="bg-ink-850 border border-ink-700 rounded-md px-2.5 py-1.5 text-xs text-white">
              {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
          <textarea data-testid={T.caseStatusReason} value={su.reason}
            onChange={(e) => setSu((s) => ({ ...s, reason: e.target.value }))}
            placeholder="Reason (required for some transitions)"
            className="w-full bg-ink-850 border border-ink-700 rounded-md px-3 py-2 text-xs text-white mb-3" rows={2} />
          {su.error && <div data-testid={T.caseStatusError} className="text-xs text-signal-soft mb-2">{su.error}</div>}
          <button data-testid={T.caseStatusSubmit} onClick={submitStatus} disabled={su.busy}
            className="px-3 py-1.5 rounded-md text-xs bg-signal hover:bg-signal/90 disabled:opacity-50 text-white flex items-center gap-1.5">
            {su.busy ? <Loader2 className="size-3.5 animate-spin" /> : null} Update status
          </button>
        </section>
      )}

      {item.maintenanceContext && (item.maintenanceContext.handoffs?.length > 0 || item.maintenanceContext.workOrders?.length > 0 || item.maintenanceContext.repairStatusUpdates?.length > 0) && (
        <section className="mb-6" data-testid={T.caseMaintenanceContext}>
          <h2 className="text-sm font-semibold uppercase tracking-wider text-white mb-3 flex items-center gap-2">
            Maintenance integration
            <span className="text-[11px] font-mono text-steel-400 normal-case tracking-normal">references only · owned by GCU365Maintenance</span>
          </h2>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-3">
            <div className="rounded-lg border border-ink-700/70 bg-ink-900/60 p-4">
              <div className="text-[11px] uppercase tracking-wider text-steel-400 mb-2">Handoffs</div>
              {(item.maintenanceContext.handoffs || []).map((h, i) => (
                <div key={i} className="text-[12px] font-mono text-steel-200">{h.status} · {fmt(h.createdAt)}</div>
              ))}
              {(item.maintenanceContext.handoffs || []).length === 0 && <div className="text-[12px] text-steel-400">None</div>}
            </div>
            <div className="rounded-lg border border-ink-700/70 bg-ink-900/60 p-4">
              <div className="text-[11px] uppercase tracking-wider text-steel-400 mb-2">Work orders</div>
              {(item.maintenanceContext.workOrders || []).map((w, i) => (
                <div key={i} className="text-[12px] font-mono text-steel-200">{w.workOrderId || w.refType} {w.status ? `· ${w.status}` : ""}{w.rejectionCode ? ` · ${w.rejectionCode}` : ""}</div>
              ))}
              {(item.maintenanceContext.workOrders || []).length === 0 && <div className="text-[12px] text-steel-400">None</div>}
            </div>
            <div className="rounded-lg border border-ink-700/70 bg-ink-900/60 p-4">
              <div className="text-[11px] uppercase tracking-wider text-steel-400 mb-2">Repair status</div>
              {(item.maintenanceContext.repairStatusUpdates || []).map((s, i) => (
                <div key={i} className="text-[12px] font-mono text-steel-200">{s.repairStatus}{s.actualRepairCostReference ? ` · cost ref: ${s.actualRepairCostReference.referenceId || "—"}` : ""}</div>
              ))}
              {(item.maintenanceContext.repairStatusUpdates || []).length === 0 && <div className="text-[12px] text-steel-400">None</div>}
            </div>
          </div>
        </section>
      )}

      <section>
        <h2 className="text-sm font-semibold uppercase tracking-wider text-white mb-3">Status history</h2>
        <div className="rounded-lg border border-ink-700/70 bg-ink-900/60 divide-y divide-ink-700/60">
          {(item.statusHistory || []).map((h, i) => (
            <div key={i} className="px-4 py-2.5 text-[12px] flex items-center gap-3">
              <span className="font-mono text-steel-300">{h.fromStatus || "∅"} → {h.toStatus}</span>
              {h.reason && <span className="text-steel-400">· {h.reason}</span>}
              <span className="ml-auto text-steel-500 font-mono text-[11px]">{fmt(h.timestamp)}</span>
            </div>
          ))}
          {(item.statusHistory || []).length === 0 && <div className="px-4 py-3 text-[12px] text-steel-400">No history.</div>}
        </div>
      </section>
    </div>
  );
}
