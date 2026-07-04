/*
 * Repository Traceability:
 * - Vehicle detail: identity card + chronological damage-history timeline of linked
 *   Trip Inspections (compact snapshots), with links to auto-created Damage Cases.
 */
import React, { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { Car, ArrowLeft, Loader2, AlertTriangle, CheckCircle2, FolderOpen, Zap, ScanEye } from "lucide-react";
import { api, envelopeError } from "../lib/api";
import { T } from "../constants/testIds";

const fmtDT = (s) => (s ? new Date(s).toLocaleString() : "—");
const fmtCost = (c) => (c && (c.low || c.high) ? `${c.currency} ${Number(c.low).toLocaleString()}–${Number(c.high).toLocaleString()}` : null);
const scoreColor = (s) => (s == null ? "text-steel-400" : s >= 80 ? "text-emerald400" : s >= 50 ? "text-amber400" : "text-signal-soft");

const OVERALL = {
  NEW_DAMAGE_FOUND: { label: "New damage", cls: "border-signal/40 bg-signal/10 text-signal-soft", icon: AlertTriangle },
  NO_NEW_DAMAGE: { label: "No new damage", cls: "border-emerald400/40 bg-emerald-400/10 text-emerald400", icon: CheckCircle2 },
  NOT_COMPARABLE: { label: "Not comparable", cls: "border-amber400/40 bg-amber400/10 text-amber400", icon: AlertTriangle },
};

function Stat({ label, value, testId }) {
  return (
    <div data-testid={testId} className="rounded-md border border-ink-700/70 bg-ink-900/60 px-4 py-3">
      <div className="text-[11px] uppercase tracking-wider text-steel-400">{label}</div>
      <div className="text-lg font-semibold text-white mt-0.5">{value}</div>
    </div>
  );
}

export default function VehicleDetail() {
  const { id } = useParams();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let alive = true;
    api.get(`/vehicles/${id}`)
      .then(({ data }) => alive && setData(data.data))
      .catch((e) => alive && setError(envelopeError(e, "Could not load this vehicle.")));
    return () => { alive = false; };
  }, [id]);

  if (error) {
    return (
      <div className="px-8 py-8">
        <p className="text-sm text-signal-soft">{error}</p>
        <Link to="/vehicles" className="text-sm text-steel-300 underline mt-2 inline-block">Back to vehicles</Link>
      </div>
    );
  }
  if (!data) {
    return <div className="px-8 py-10 text-steel-400 text-sm flex items-center gap-2"><Loader2 className="size-4 animate-spin" /> Loading…</div>;
  }

  const v = data.vehicle || {};
  const trips = data.trips || [];

  return (
    <div data-testid={T.vehicleDetailPage} className="px-8 py-8 max-w-5xl">
      <Link to="/vehicles" data-testid="vehicle-back-link" className="text-xs text-steel-400 hover:text-steel-200 flex items-center gap-1.5 w-fit">
        <ArrowLeft className="size-3.5" /> Vehicles
      </Link>
      <h1 className="text-2xl font-semibold text-white mt-2 flex items-center gap-3">
        <Car className="size-6 text-steel-300" /> {v.plateDisplay || v.vin || "Vehicle"}
      </h1>
      <div className="flex flex-wrap gap-x-5 gap-y-1 mt-2 text-xs text-steel-300">
        {v.vin && <span>VIN <span className="font-mono text-steel-100">{v.vin}</span></span>}
        {(v.color || v.bodyType) && <span className="capitalize">{[v.color, v.bodyType].filter(Boolean).join(" ")}</span>}
        {v.model && <span>{v.model}</span>}
        <span>First seen {fmtDT(v.firstSeenAt)}</span>
        <span>Last seen {fmtDT(v.lastSeenAt)}</span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-5">
        <Stat label="Trip inspections" value={v.inspectionCount || 0} testId="vehicle-stat-trips" />
        <Stat label="New issues found" value={data.totalNewIssues || 0} testId="vehicle-stat-issues" />
        <Stat label="Damage cases opened" value={data.casesCreated || 0} testId="vehicle-stat-cases" />
        <Stat label="Latest condition" value={trips[0]?.conditionScore != null ? `${trips[0].conditionScore}/100` : "—"} testId="vehicle-stat-condition" />
      </div>

      <div className="mt-7">
        <div className="text-[11px] uppercase tracking-wider text-steel-400 mb-3">Damage history — most recent first</div>
        {trips.length === 0 ? (
          <div className="rounded-lg border border-ink-700/70 bg-ink-900/60 px-4 py-10 text-center text-steel-400 text-sm">No linked trips yet.</div>
        ) : (
          <ol className="space-y-3" data-testid="vehicle-trip-timeline">
            {trips.map((t) => {
              const o = OVERALL[t.overall] || OVERALL.NOT_COMPARABLE; const Icon = o.icon;
              const newItems = (t.sections || []).flatMap((s) => (s.items || []).filter((it) => it.status === "NEW").map((it) => ({ ...it, sectionLabel: s.label })));
              return (
                <li key={t.id} className="rounded-lg border border-ink-700/70 bg-ink-900/60 p-4" data-testid={`vehicle-trip-${t.id}`}>
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className={`text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full border flex items-center gap-1 ${o.cls}`}>
                      <Icon className="size-3" /> {o.label}{t.newIssueCount > 0 ? ` · ${t.newIssueCount}` : ""}
                    </span>
                    <span className="text-xs text-steel-400">{fmtDT(t.createdAt)}</span>
                    <span className="text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded border border-ink-600 text-steel-400 flex items-center gap-1">
                      {t.mode === "thorough" ? <ScanEye className="size-3" /> : <Zap className="size-3" />}{t.mode || "fast"}
                    </span>
                    {t.conditionScore != null && <span className="text-xs text-steel-300">Condition <span className={`font-semibold ${scoreColor(t.conditionScore)}`}>{t.conditionScore}/100</span></span>}
                    {fmtCost(t.costSummary) && <span className="text-xs text-signal-soft">Est. {fmtCost(t.costSummary)}</span>}
                    {t.damageCaseId && (
                      <Link to={`/cases/${t.damageCaseId}`} className="ml-auto text-xs text-steel-200 border border-ink-600 rounded px-2 py-1 hover:bg-ink-800 flex items-center gap-1.5">
                        <FolderOpen className="size-3.5" /> View case
                      </Link>
                    )}
                  </div>
                  {(t.reportFields?.customerName || t.reportFields?.rentalId || t.reportFields?.inspectorName) && (
                    <div className="text-[11px] text-steel-400 mt-2">
                      {[t.reportFields.customerName && `Customer: ${t.reportFields.customerName}`,
                        t.reportFields.rentalId && `Rental: ${t.reportFields.rentalId}`,
                        t.reportFields.inspectorName && `Inspector: ${t.reportFields.inspectorName}`].filter(Boolean).join(" · ")}
                    </div>
                  )}
                  {newItems.length > 0 && (
                    <ul className="mt-3 space-y-1">
                      {newItems.slice(0, 6).map((it, i) => (
                        <li key={i} className="text-xs text-steel-200 flex items-center gap-2 flex-wrap">
                          <span className="size-1.5 rounded-full bg-signal shrink-0" />
                          <span className="font-mono text-steel-400">{it.category}</span>
                          <span>{it.location || "—"}</span>
                          {it.severity && <span className="text-[10px] uppercase text-steel-400">{it.severity}</span>}
                          {it.sizeCm != null && <span className="text-[10px] font-mono text-steel-400">~{it.sizeCm} cm</span>}
                          <span className="text-[10px] text-steel-500">{it.sectionLabel}</span>
                        </li>
                      ))}
                      {newItems.length > 6 && <li className="text-[11px] text-steel-500 ml-3.5">+{newItems.length - 6} more…</li>}
                    </ul>
                  )}
                </li>
              );
            })}
          </ol>
        )}
      </div>
    </div>
  );
}
