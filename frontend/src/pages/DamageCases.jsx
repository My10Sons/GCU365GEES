/*
 * Repository Traceability:
 * - DI-SPRINT-03 (Damage case list screen), DI-0012, DI-0034 (GET /damage-cases).
 */
import React, { useCallback, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { RefreshCcw, FolderOpen } from "lucide-react";
import { casesApi } from "../lib/sprint03-api";
import { envelopeError } from "../lib/api";
import { T } from "../constants/testIds";

const STATUSES = ["", "OPEN", "PENDING_REVIEW", "REVIEWED", "ADDITIONAL_EVIDENCE_REQUIRED",
  "READY_FOR_MAINTENANCE_REVIEW", "ROUTED_TO_MAINTENANCE", "CLOSED", "CANCELLED", "REJECTED"];

function fmt(d) {
  if (!d) return "—";
  try { return new Date(d).toLocaleString(); } catch { return d; }
}

export default function DamageCases() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filters, setFilters] = useState({ status: "", page: 1, pageSize: 20 });

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const params = { page: filters.page, pageSize: filters.pageSize, ...(filters.status ? { status: filters.status } : {}) };
      setData(await casesApi.list(params));
    } catch (err) {
      setError(envelopeError(err, "Could not load damage cases."));
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => { load(); }, [load]);

  const list = useMemo(() => data?.items || [], [data]);
  const inputCls = "bg-ink-850 border border-ink-700 focus:border-signal/60 outline-none rounded-md px-2.5 py-1.5 text-xs text-white";

  return (
    <div data-testid={T.casesRoot} className="px-8 py-8 max-w-6xl">
      <div className="flex items-start justify-between gap-4 mb-6">
        <div>
          <div className="text-[11px] uppercase tracking-[0.22em] text-steel-400">Damage Intelligence</div>
          <h1 className="text-2xl font-semibold text-white mt-1 flex items-center gap-3">
            <FolderOpen className="size-6 text-steel-300" /> Damage cases
          </h1>
          <p className="text-sm text-steel-300 mt-2 max-w-2xl">
            Damage case context linked to evidence, findings, and comparison results. Final
            liability, customer charge, and repair cost remain with CROMS / Maintenance / Finance.
          </p>
        </div>
        <button data-testid={T.casesRefresh} onClick={load}
          className="px-3 py-1.5 rounded-md text-xs text-steel-200 bg-ink-800 border border-ink-700 hover:bg-ink-700/80 flex items-center gap-1.5">
          <RefreshCcw className="size-3.5" /> Refresh
        </button>
      </div>

      <div className="flex flex-wrap items-center gap-2 mb-4">
        <label className="text-[11px] uppercase tracking-wider text-steel-400">Status</label>
        <select data-testid={T.casesFilterStatus} value={filters.status} className={inputCls}
          onChange={(e) => setFilters((f) => ({ ...f, status: e.target.value, page: 1 }))}>
          {STATUSES.map((s) => <option key={s} value={s}>{s || "Any"}</option>)}
        </select>
        <div className="flex-1" />
        {data && <span className="text-[11px] font-mono text-steel-400">{data.total} total · page {data.page}/{data.totalPages}</span>}
      </div>

      {error && <div className="text-sm text-signal-soft bg-signal/10 border border-signal/30 rounded-md px-3 py-2 mb-4">{error}</div>}

      <div className="rounded-lg border border-ink-700/70 bg-ink-900/60 overflow-hidden">
        <table className="w-full text-sm" data-testid={T.casesTable}>
          <thead className="bg-ink-900 text-[11px] uppercase tracking-wider text-steel-400">
            <tr>
              <th className="text-left px-4 py-2.5 font-medium">Vehicle</th>
              <th className="text-left px-4 py-2.5 font-medium">Type</th>
              <th className="text-left px-4 py-2.5 font-medium">Severity</th>
              <th className="text-left px-4 py-2.5 font-medium">Status</th>
              <th className="text-left px-4 py-2.5 font-medium">Created</th>
              <th className="text-left px-4 py-2.5 font-medium"></th>
            </tr>
          </thead>
          <tbody>
            {loading && <tr><td colSpan={6} className="px-4 py-10 text-center text-steel-400 text-sm">Loading…</td></tr>}
            {!loading && list.length === 0 && (
              <tr><td colSpan={6} className="px-4 py-10 text-center text-steel-400 text-sm" data-testid={T.casesEmpty}>
                No damage cases yet. Create one from a review item.</td></tr>
            )}
            {!loading && list.map((it) => (
              <tr key={it.damageCaseId} data-testid={`${T.casesRow}-${it.damageCaseId}`}
                className="border-t border-ink-700/60 hover:bg-ink-800/60 transition-colors">
                <td className="px-4 py-3 font-mono text-[12px] text-steel-100">{it.externalVehicleRef || "—"}</td>
                <td className="px-4 py-3 text-steel-200">{it.caseType}</td>
                <td className="px-4 py-3 text-steel-300 font-mono text-[12px]">{it.severityCode || "—"}</td>
                <td className="px-4 py-3 text-steel-200 font-mono text-[12px]">{it.status}</td>
                <td className="px-4 py-3 text-steel-400 text-[12px]">{fmt(it.createdAt)}</td>
                <td className="px-4 py-3">
                  <Link to={`/cases/${it.damageCaseId}`} data-testid={`${T.casesLink}-${it.damageCaseId}`}
                    className="text-signal-soft hover:underline underline-offset-2 text-[12px]">Open</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
