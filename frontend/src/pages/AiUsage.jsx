import React, { useEffect, useState } from "react";
import { Cpu, Coins, ScanEye, TrendingUp, Loader2, Activity } from "lucide-react";
import { api } from "../lib/api";
import { T } from "../constants/testIds";

const RANGES = [7, 30, 90];

function Stat({ icon: Icon, label, value, testId, sub }) {
  return (
    <div data-testid={testId} className="rounded-lg border border-ink-700/70 bg-ink-900/60 px-4 py-4">
      <div className="flex items-center gap-2 text-[11px] uppercase tracking-wider text-steel-400">
        <Icon className="size-3.5" /> {label}
      </div>
      <div className="text-2xl font-semibold text-white mt-1.5">{value}</div>
      {sub && <div className="text-[11px] text-steel-400 mt-0.5">{sub}</div>}
    </div>
  );
}

export default function AiUsage() {
  const [days, setDays] = useState(30);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let alive = true;
    setLoading(true); setError("");
    api.get(`/trip-inspection/usage?days=${days}`)
      .then(({ data }) => { if (alive) setData(data.data); })
      .catch(() => { if (alive) setError("Could not load usage data."); })
      .finally(() => { if (alive) setLoading(false); });
    return () => { alive = false; };
  }, [days]);

  const daily = data?.daily || [];
  const maxTokens = Math.max(1, ...daily.map((d) => d.tokens));
  const fmt = (n) => Number(n || 0).toLocaleString();

  return (
    <div data-testid={T.aiUsagePage} className="px-8 py-8 max-w-4xl">
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <div className="text-[11px] uppercase tracking-[0.22em] text-steel-400">Damage Intelligence</div>
          <h1 className="text-2xl font-semibold text-white mt-1 flex items-center gap-3">
            <Activity className="size-6 text-steel-300" /> AI Usage
          </h1>
          <p className="text-sm text-steel-300 mt-2 max-w-2xl">
            AI tokens and calls consumed by Trip Inspection analyses. Billed against your Emergent
            Universal Key balance — use this to watch trends and forecast top-ups.
          </p>
        </div>
        <div data-testid={T.aiUsageRange} className="inline-flex rounded-md border border-ink-700 overflow-hidden self-start">
          {RANGES.map((r) => (
            <button key={r} data-testid={`ai-usage-range-${r}`} onClick={() => setDays(r)} disabled={loading}
              className={`px-3 py-2 text-xs font-medium transition-colors disabled:opacity-50 ${days === r ? "bg-signal text-white" : "bg-ink-800 text-steel-300 hover:bg-ink-700/80"}`}>
              {r}d
            </button>
          ))}
        </div>
      </div>

      {loading && <div className="mt-10 flex items-center gap-3 text-steel-300"><Loader2 className="size-5 animate-spin" /> Loading usage…</div>}
      {error && !loading && <div data-testid="ai-usage-error" className="mt-8 rounded-md border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-300">{error}</div>}

      {!loading && !error && data && (
        <>
          <div className="mt-6 grid grid-cols-2 lg:grid-cols-4 gap-3">
            <Stat icon={Coins} label="Total AI tokens" value={fmt(data.totals.tokens)} testId="ai-usage-total-tokens" sub={`last ${data.days} days`} />
            <Stat icon={Cpu} label="AI calls" value={fmt(data.totals.calls)} testId="ai-usage-total-calls" />
            <Stat icon={ScanEye} label="Inspections" value={fmt(data.totals.inspections)} testId="ai-usage-inspections" />
            <Stat icon={TrendingUp} label="Avg tokens / inspection" value={fmt(data.totals.avgTokensPerInspection)} testId="ai-usage-avg" sub="with token data" />
          </div>

          <div className="mt-8">
            <div className="text-[11px] uppercase tracking-wider text-steel-400 mb-3">Daily tokens</div>
            {daily.length === 0 ? (
              <div className="text-sm text-steel-400">No analyses recorded in this period.</div>
            ) : (
              <div data-testid="ai-usage-chart" className="space-y-2">
                {daily.map((d) => (
                  <div key={d.date} className="flex items-center gap-3">
                    <span className="w-24 shrink-0 text-[11px] text-steel-400 tabular-nums">{d.date}</span>
                    <div className="flex-1 h-6 rounded bg-ink-800/60 overflow-hidden">
                      <div className="h-full bg-signal/70 rounded" style={{ width: `${Math.max(2, (d.tokens / maxTokens) * 100)}%` }} />
                    </div>
                    <span className="w-28 shrink-0 text-right text-xs text-steel-200 tabular-nums">{fmt(d.tokens)} tok</span>
                    <span className="w-24 shrink-0 text-right text-[11px] text-steel-400 tabular-nums">{d.inspections} insp.</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <p className="mt-8 text-[11px] text-steel-400">
            Token counts are reported by the AI provider per call and stored in the audit log.
            Exact per-token cost is set by Emergent — manage balance at Profile → Universal Key.
          </p>
        </>
      )}
    </div>
  );
}
