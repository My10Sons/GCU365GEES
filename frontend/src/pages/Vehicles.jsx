/*
 * Repository Traceability:
 * - Vehicle registry: searchable list of vehicles auto-linked from Trip Inspections
 *   (plate / VIN OCR). Row click opens the vehicle's damage-history timeline.
 */
import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Car, Search, Loader2, ChevronRight, FolderPlus } from "lucide-react";
import { api, envelopeError } from "../lib/api";
import { T } from "../constants/testIds";

const fmtDate = (s) => (s ? new Date(s).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" }) : "—");

export const RISK_STYLE = {
  HIGH: "border-signal/50 bg-signal/10 text-signal-soft",
  MEDIUM: "border-amber400/50 bg-amber400/10 text-amber400",
  LOW: "border-ink-600 bg-ink-800/70 text-steel-400",
  NONE: "border-emerald400/40 bg-emerald-400/10 text-emerald400",
};

export function RiskBadge({ risk, testId }) {
  if (!risk || !risk.window) return <span className="text-xs text-steel-500">—</span>;
  return (
    <span data-testid={testId}
      title={`New damage in ${risk.damagedTrips} of the last ${risk.window} rental(s)${risk.streak >= 2 ? ` · ${risk.streak} in a row` : ""}`}
      className={`text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full border w-fit ${RISK_STYLE[risk.level] || RISK_STYLE.LOW}`}>
      {risk.label}{risk.level === "HIGH" || risk.level === "MEDIUM" ? ` · ${risk.damagedTrips}/${risk.window}` : ""}
    </span>
  );
}

export default function Vehicles() {
  const [rows, setRows] = useState([]);
  const [search, setSearch] = useState("");
  const [busy, setBusy] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let alive = true;
    const t = setTimeout(() => {
      setBusy(true);
      api.get("/vehicles", { params: { search } })
        .then(({ data }) => { if (alive) { setRows(data.data.vehicles || []); setError(""); } })
        .catch((e) => alive && setError(envelopeError(e, "Could not load vehicles.")))
        .finally(() => alive && setBusy(false));
    }, 250);
    return () => { alive = false; clearTimeout(t); };
  }, [search]);

  return (
    <div data-testid={T.vehiclesPage} className="px-8 py-8 max-w-5xl">
      <div className="text-[11px] uppercase tracking-[0.22em] text-steel-400">Damage Intelligence</div>
      <h1 className="text-2xl font-semibold text-white mt-1 flex items-center gap-3"><Car className="size-6 text-steel-300" /> Vehicles</h1>
      <p className="text-sm text-steel-300 mt-2 max-w-2xl">
        Vehicle registry built automatically from Trip Inspections — plates and VINs read from photos.
        Open a vehicle to see its full damage history across rentals.
      </p>

      <div className="mt-6 relative max-w-sm">
        <Search className="size-4 text-steel-400 absolute left-3 top-1/2 -translate-y-1/2" />
        <input data-testid={T.vehiclesSearch} value={search} onChange={(e) => setSearch(e.target.value)}
          placeholder="Search plate, VIN, or model…"
          className="w-full rounded-md bg-ink-900/70 border border-ink-700 pl-9 pr-3 py-2 text-sm text-steel-100 placeholder:text-steel-500 focus:outline-none focus:border-signal/50" />
      </div>

      {error && <p data-testid="vehicles-error" className="text-sm text-signal-soft mt-4">{error}</p>}

      <div className="mt-5 rounded-lg border border-ink-700/70 bg-ink-900/60 overflow-hidden">
        <div className="grid grid-cols-[1.2fr_1.3fr_1.2fr_0.6fr_1fr_1fr_auto] gap-3 px-4 py-2.5 text-[11px] uppercase tracking-wider text-steel-400 bg-ink-900 border-b border-ink-700/60">
          <span>Plate</span><span>VIN</span><span>Vehicle</span><span>Trips</span><span>Risk</span><span>Last seen</span><span />
        </div>
        {busy ? (
          <div className="px-4 py-10 text-center text-steel-400 text-sm flex items-center justify-center gap-2"><Loader2 className="size-4 animate-spin" /> Loading…</div>
        ) : rows.length === 0 ? (
          <div className="px-4 py-10 text-center text-steel-400 text-sm">
            No vehicles yet. Run a Trip Inspection with a plate (typed, read from photos, or via the
            Plate / VIN close-up) and it will appear here.
          </div>
        ) : (
          <ul className="divide-y divide-ink-700/60">
            {rows.map((v) => (
              <li key={v.id}>
                <Link to={`/vehicles/${v.id}`} data-testid={`vehicle-row-${v.id}`}
                  className="grid grid-cols-[1.2fr_1.3fr_1.2fr_0.6fr_1fr_1fr_auto] gap-3 px-4 py-3 items-center hover:bg-ink-800/50 transition-colors">
                  <span className="text-sm font-semibold text-white font-mono">{v.plateDisplay || "—"}</span>
                  <span className="text-xs font-mono text-steel-300 truncate">{v.vin || "—"}</span>
                  <span className="text-xs text-steel-300 truncate">
                    {[v.color, v.bodyType].filter(Boolean).join(" ") || null}
                    {v.model ? `${v.color || v.bodyType ? " · " : ""}${v.model}` : ""}
                    {!v.color && !v.bodyType && !v.model && "—"}
                  </span>
                  <span className="text-sm text-steel-100">{v.inspectionCount || 0}</span>
                  <RiskBadge risk={v.risk} testId={`vehicle-risk-${v.id}`} />
                  <span className="text-xs text-steel-400">{fmtDate(v.lastSeenAt)}</span>
                  <ChevronRight className="size-4 text-steel-500" />
                </Link>
              </li>
            ))}
          </ul>
        )}
      </div>

      <p className="text-[11px] text-steel-500 mt-4 flex items-center gap-1.5">
        <FolderPlus className="size-3.5" /> Vehicles are added when a Trip Inspection is finalized with
        "Save to vehicle history" enabled and a plate or VIN is available.
      </p>
    </div>
  );
}
