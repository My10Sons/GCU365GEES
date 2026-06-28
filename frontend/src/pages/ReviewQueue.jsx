/*
 * Repository Traceability:
 * - DI-SPRINT-03 (Web review queue list), DI-0019, DI-0034 (GET /review-queue).
 */
import React, { useCallback, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { RefreshCcw, ShieldCheck } from "lucide-react";
import { reviewApi } from "../lib/sprint03-api";
import { envelopeError } from "../lib/api";
import { T } from "../constants/testIds";

const STATUSES = ["", "PENDING", "IN_REVIEW", "ESCALATED", "ADDITIONAL_EVIDENCE_REQUIRED", "DECIDED"];
const PRIORITIES = ["", "HIGH", "MEDIUM", "LOW"];

function fmt(d) {
  if (!d) return "—";
  try { return new Date(d).toLocaleString(); } catch { return d; }
}

const priorityCls = (p) =>
  p === "HIGH" ? "bg-signal/15 text-signal-soft border-signal/40"
  : p === "MEDIUM" ? "bg-amber400/15 text-amber400 border-amber400/40"
  : "bg-ink-800 text-steel-300 border-ink-600";

export default function ReviewQueue() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filters, setFilters] = useState({ status: "", priority: "", page: 1, pageSize: 20 });

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const params = {
        page: filters.page, pageSize: filters.pageSize,
        ...(filters.status ? { status: filters.status } : {}),
        ...(filters.priority ? { priority: filters.priority } : {}),
      };
      setData(await reviewApi.queue(params));
    } catch (err) {
      setError(envelopeError(err, "Could not load review queue."));
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => { load(); }, [load]);

  const list = useMemo(() => data?.items || [], [data]);
  const inputCls = "bg-ink-850 border border-ink-700 focus:border-signal/60 outline-none rounded-md px-2.5 py-1.5 text-xs text-white";

  return (
    <div data-testid={T.reviewRoot} className="px-8 py-8 max-w-6xl">
      <div className="flex items-start justify-between gap-4 mb-6">
        <div>
          <div className="text-[11px] uppercase tracking-[0.22em] text-steel-400">Damage Intelligence</div>
          <h1 className="text-2xl font-semibold text-white mt-1 flex items-center gap-3">
            <ShieldCheck className="size-6 text-steel-300" /> Review queue
          </h1>
          <p className="text-sm text-steel-300 mt-2 max-w-2xl">
            AI findings and comparison results flagged low-confidence, uncertain, or new are
            routed here for human review. AI output is advisory until reviewed.
          </p>
        </div>
        <button data-testid={T.reviewRefresh} onClick={load}
          className="px-3 py-1.5 rounded-md text-xs text-steel-200 bg-ink-800 border border-ink-700 hover:bg-ink-700/80 flex items-center gap-1.5">
          <RefreshCcw className="size-3.5" /> Refresh
        </button>
      </div>

      <div className="flex flex-wrap items-center gap-2 mb-4">
        <label className="text-[11px] uppercase tracking-wider text-steel-400">Status</label>
        <select data-testid={T.reviewFilterStatus} value={filters.status} className={inputCls}
          onChange={(e) => setFilters((f) => ({ ...f, status: e.target.value, page: 1 }))}>
          {STATUSES.map((s) => <option key={s} value={s}>{s || "Any"}</option>)}
        </select>
        <label className="text-[11px] uppercase tracking-wider text-steel-400 ml-2">Priority</label>
        <select data-testid={T.reviewFilterPriority} value={filters.priority} className={inputCls}
          onChange={(e) => setFilters((f) => ({ ...f, priority: e.target.value, page: 1 }))}>
          {PRIORITIES.map((s) => <option key={s} value={s}>{s || "Any"}</option>)}
        </select>
        <div className="flex-1" />
        {data && <span className="text-[11px] font-mono text-steel-400">{data.total} total · page {data.page}/{data.totalPages}</span>}
      </div>

      {error && <div className="text-sm text-signal-soft bg-signal/10 border border-signal/30 rounded-md px-3 py-2 mb-4">{error}</div>}

      <div className="rounded-lg border border-ink-700/70 bg-ink-900/60 overflow-hidden">
        <table className="w-full text-sm" data-testid={T.reviewTable}>
          <thead className="bg-ink-900 text-[11px] uppercase tracking-wider text-steel-400">
            <tr>
              <th className="text-left px-4 py-2.5 font-medium">Object</th>
              <th className="text-left px-4 py-2.5 font-medium">Source</th>
              <th className="text-left px-4 py-2.5 font-medium">Priority</th>
              <th className="text-left px-4 py-2.5 font-medium">Severity</th>
              <th className="text-left px-4 py-2.5 font-medium">Status</th>
              <th className="text-left px-4 py-2.5 font-medium">Age (min)</th>
              <th className="text-left px-4 py-2.5 font-medium"></th>
            </tr>
          </thead>
          <tbody>
            {loading && <tr><td colSpan={7} className="px-4 py-10 text-center text-steel-400 text-sm">Loading…</td></tr>}
            {!loading && list.length === 0 && (
              <tr><td colSpan={7} className="px-4 py-10 text-center text-steel-400 text-sm" data-testid={T.reviewEmpty}>
                No review items. Run AI or a comparison to populate the queue.</td></tr>
            )}
            {!loading && list.map((it) => (
              <tr key={it.reviewItemId} data-testid={`${T.reviewRow}-${it.reviewItemId}`}
                className="border-t border-ink-700/60 hover:bg-ink-800/60 transition-colors">
                <td className="px-4 py-3 text-steel-200">{it.objectType?.replace("_", " ")}</td>
                <td className="px-4 py-3 font-mono text-[12px] text-steel-300">{it.source}</td>
                <td className="px-4 py-3"><span className={`text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded border ${priorityCls(it.priority)}`}>{it.priority}</span></td>
                <td className="px-4 py-3 text-steel-300 font-mono text-[12px]">{it.severityCode || "—"}</td>
                <td className="px-4 py-3 text-steel-200 font-mono text-[12px]">{it.reviewStatus}</td>
                <td className="px-4 py-3 text-steel-400 font-mono text-[12px]">{it.ageMinutes ?? "—"}</td>
                <td className="px-4 py-3">
                  <Link to={`/review/${it.reviewItemId}`} data-testid={`${T.reviewLink}-${it.reviewItemId}`}
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
