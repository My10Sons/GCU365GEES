/*
 * Repository Traceability:
 * - DI-SPRINT-01 (Inspection list screen — pagination, filters, permission-aware actions),
 *   DI-0034 (GET /inspection-sessions).
 */
import React, { useCallback, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Plus, RefreshCcw, ClipboardList } from "lucide-react";
import { inspectionsApi, envelopeError } from "../lib/inspections-api";
import { useAuth } from "../lib/auth-context";
import StatusBadge from "../components/inspection/StatusBadge";
import CreateInspectionModal from "../components/inspection/CreateInspectionModal";
import { T } from "../constants/testIds";

const STATUSES = ["", "DRAFT", "CAPTURE_IN_PROGRESS", "EVIDENCE_REGISTERED", "SUBMITTED", "CANCELLED", "FAILED"];
const TYPES = ["", "CHECK_OUT", "CHECK_IN", "MAINTENANCE_INTAKE", "MAINTENANCE_HANDBACK", "SPOT_CHECK"];

function fmt(d) {
  if (!d) return "—";
  try { return new Date(d).toLocaleString(); } catch { return d; }
}

export default function Inspections() {
  const { has } = useAuth();
  const canCreate = has("di.inspections.create");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filters, setFilters] = useState({ status: "", inspectionType: "", page: 1, pageSize: 20 });
  const [openCreate, setOpenCreate] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const params = {
        page: filters.page,
        pageSize: filters.pageSize,
        ...(filters.status ? { status: filters.status } : {}),
        ...(filters.inspectionType ? { inspectionType: filters.inspectionType } : {}),
      };
      const d = await inspectionsApi.list(params);
      setData(d);
    } catch (err) {
      setError(envelopeError(err, "Could not load inspections."));
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => { load(); }, [load]);

  const inputCls =
    "bg-ink-850 border border-ink-700 focus:border-signal/60 focus:ring-2 focus:ring-signal/20 outline-none rounded-md px-2.5 py-1.5 text-xs text-white";

  const totalPages = data?.totalPages || 1;

  const list = useMemo(() => data?.items || [], [data]);

  return (
    <div data-testid={T.inspectionsRoot} className="px-8 py-8 max-w-6xl">
      <div className="flex items-start justify-between gap-4 mb-6">
        <div>
          <div className="text-[11px] uppercase tracking-[0.22em] text-steel-400">
            Damage Intelligence
          </div>
          <h1 className="text-2xl font-semibold text-white mt-1 flex items-center gap-3">
            <ClipboardList className="size-6 text-steel-300" />
            Inspection sessions
          </h1>
          <p className="text-sm text-steel-300 mt-2 max-w-2xl">
            Production inspection foundation. Sessions, evidence, and controlled access links
            are tenant-scoped and audited.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            data-testid={T.inspectionsRefresh}
            onClick={load}
            className="px-3 py-1.5 rounded-md text-xs text-steel-200 bg-ink-800 border border-ink-700 hover:bg-ink-700/80 flex items-center gap-1.5"
          >
            <RefreshCcw className="size-3.5" />
            Refresh
          </button>
          {canCreate && (
            <button
              data-testid={T.inspectionsCreateBtn}
              onClick={() => setOpenCreate(true)}
              className="px-3 py-1.5 rounded-md text-xs bg-signal hover:bg-signal/90 text-white flex items-center gap-1.5"
            >
              <Plus className="size-3.5" />
              New inspection
            </button>
          )}
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-2 mb-4">
        <label className="text-[11px] uppercase tracking-wider text-steel-400">Status</label>
        <select
          data-testid={T.inspectionsFilterStatus}
          value={filters.status}
          onChange={(e) => setFilters((f) => ({ ...f, status: e.target.value, page: 1 }))}
          className={inputCls}
        >
          {STATUSES.map((s) => <option key={s} value={s}>{s || "Any"}</option>)}
        </select>
        <label className="text-[11px] uppercase tracking-wider text-steel-400 ml-2">Type</label>
        <select
          data-testid={T.inspectionsFilterType}
          value={filters.inspectionType}
          onChange={(e) => setFilters((f) => ({ ...f, inspectionType: e.target.value, page: 1 }))}
          className={inputCls}
        >
          {TYPES.map((s) => <option key={s} value={s}>{s || "Any"}</option>)}
        </select>
        <div className="flex-1" />
        {data && (
          <span className="text-[11px] font-mono text-steel-400">
            {data.total} total · page {data.page}/{totalPages}
          </span>
        )}
      </div>

      {error && (
        <div className="text-sm text-signal-soft bg-signal/10 border border-signal/30 rounded-md px-3 py-2 mb-4">
          {error}
        </div>
      )}

      <div className="rounded-lg border border-ink-700/70 bg-ink-900/60 overflow-hidden">
        <table className="w-full text-sm" data-testid={T.inspectionsTable}>
          <thead className="bg-ink-900 text-[11px] uppercase tracking-wider text-steel-400">
            <tr>
              <th className="text-left px-4 py-2.5 font-medium">Vehicle</th>
              <th className="text-left px-4 py-2.5 font-medium">Type</th>
              <th className="text-left px-4 py-2.5 font-medium">Status</th>
              <th className="text-left px-4 py-2.5 font-medium">Images</th>
              <th className="text-left px-4 py-2.5 font-medium">Rental</th>
              <th className="text-left px-4 py-2.5 font-medium">Branch</th>
              <th className="text-left px-4 py-2.5 font-medium">Updated</th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr>
                <td colSpan={7} className="px-4 py-10 text-center text-steel-400 text-sm">
                  Loading…
                </td>
              </tr>
            )}
            {!loading && list.length === 0 && (
              <tr>
                <td colSpan={7} className="px-4 py-10 text-center text-steel-400 text-sm" data-testid={T.inspectionsEmpty}>
                  No inspections in this tenant yet. {canCreate && "Create the first one with “New inspection”."}
                </td>
              </tr>
            )}
            {!loading && list.map((it) => (
              <tr
                key={it.id}
                data-testid={`${T.inspectionsRow}-${it.id}`}
                className="border-t border-ink-700/60 hover:bg-ink-800/60 transition-colors"
              >
                <td className="px-4 py-3 font-mono text-[12px] text-steel-100">
                  <Link to={`/inspections/${it.id}`} className="text-white hover:text-signal-soft underline-offset-2 hover:underline" data-testid={`${T.inspectionsLink}-${it.id}`}>
                    {it.references?.externalVehicleRef || "—"}
                  </Link>
                </td>
                <td className="px-4 py-3 text-steel-200">{it.inspectionType}</td>
                <td className="px-4 py-3"><StatusBadge status={it.status} testId={`${T.inspectionStatus}-${it.id}`} /></td>
                <td className="px-4 py-3 text-steel-200 font-mono">{it.imageCount ?? 0}</td>
                <td className="px-4 py-3 font-mono text-[12px] text-steel-300">{it.references?.externalRentalAgreementRef || "—"}</td>
                <td className="px-4 py-3 font-mono text-[12px] text-steel-300">{it.references?.externalBranchRef || "—"}</td>
                <td className="px-4 py-3 text-[12px] text-steel-400">{fmt(it.updatedAt)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex justify-between items-center mt-4 text-xs">
        <button
          onClick={() => setFilters((f) => ({ ...f, page: Math.max(1, f.page - 1) }))}
          disabled={filters.page <= 1}
          data-testid={T.inspectionsPrev}
          className="px-3 py-1.5 rounded-md text-steel-200 bg-ink-800 border border-ink-700 hover:bg-ink-700/80 disabled:opacity-40"
        >
          Previous
        </button>
        <button
          onClick={() => setFilters((f) => ({ ...f, page: Math.min(totalPages, f.page + 1) }))}
          disabled={filters.page >= totalPages}
          data-testid={T.inspectionsNext}
          className="px-3 py-1.5 rounded-md text-steel-200 bg-ink-800 border border-ink-700 hover:bg-ink-700/80 disabled:opacity-40"
        >
          Next
        </button>
      </div>

      <CreateInspectionModal
        open={openCreate}
        onClose={() => setOpenCreate(false)}
        onCreated={(created) => {
          setData((d) => (d ? { ...d, items: [
            { id: created.id, inspectionType: created.inspectionType, sourceSystem: created.sourceSystem, status: created.status, references: created.references, imageCount: 0, createdAt: created.createdAt, updatedAt: created.updatedAt },
            ...(d.items || []),
          ], total: (d.total || 0) + 1 } : d));
        }}
      />
    </div>
  );
}
