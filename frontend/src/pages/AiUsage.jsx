import React, { useEffect, useState } from "react";
import { Cpu, Coins, ScanEye, TrendingUp, Loader2, Activity, AlertTriangle, CheckCircle2, Target } from "lucide-react";
import { api } from "../lib/api";
import { useAuth } from "../lib/auth-context";
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
  const { has } = useAuth();
  const canEdit = has("di.configuration.manage");
  const [days, setDays] = useState(30);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [budgetInput, setBudgetInput] = useState("");
  const [rateInput, setRateInput] = useState("");
  const [saving, setSaving] = useState(false);

  const load = () => {
    setLoading(true); setError("");
    return api.get(`/trip-inspection/usage?days=${days}`)
      .then(({ data }) => {
        setData(data.data);
        setBudgetInput(String(data.data.budget?.monthlyTokenBudget || ""));
        setRateInput(String(data.data.budget?.costPer1kTokens || ""));
      })
      .catch(() => setError("Could not load usage data."))
      .finally(() => setLoading(false));
  };

  useEffect(() => { let alive = true; if (alive) load(); return () => { alive = false; }; }, [days]);

  const saveBudget = async () => {
    setSaving(true);
    try {
      await api.put("/trip-inspection/budget", {
        monthlyTokenBudget: parseInt(budgetInput || "0", 10) || 0,
        costPer1kTokens: parseFloat(rateInput || "0") || 0,
      });
      await load();
    } catch { setError("Could not save budget."); }
    finally { setSaving(false); }
  };

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

          <BudgetPanel budget={data.budget} canEdit={canEdit} budgetInput={budgetInput}
            setBudgetInput={setBudgetInput} rateInput={rateInput} setRateInput={setRateInput}
            saving={saving} onSave={saveBudget} />

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

function BudgetPanel({ budget, canEdit, budgetInput, setBudgetInput, rateInput, setRateInput, saving, onSave }) {
  const b = budget || {};
  const fmt = (n) => Number(n || 0).toLocaleString();
  const hasBudget = b.monthlyTokenBudget > 0;
  const tone = b.overBudget ? "over" : b.nearBudget ? "near" : "ok";
  const toneCls = {
    over: "border-red-500/40 bg-red-500/10 text-red-300",
    near: "border-amber400/40 bg-amber400/10 text-amber400",
    ok: "border-emerald400/30 bg-emerald-400/5 text-emerald400",
  }[tone];
  const Icon = tone === "ok" ? CheckCircle2 : AlertTriangle;

  return (
    <div data-testid="ai-usage-budget" className="mt-6 rounded-lg border border-ink-700/70 bg-ink-900/60 p-4">
      <div className="flex items-center gap-2 text-[11px] uppercase tracking-wider text-steel-400 mb-3">
        <Target className="size-3.5" /> Monthly budget &amp; alert
      </div>

      {hasBudget ? (
        <>
          <div data-testid="ai-usage-budget-banner" className={`rounded-md border px-4 py-3 flex items-start gap-2.5 ${toneCls}`}>
            <Icon className="size-4 mt-0.5 shrink-0" />
            <div className="text-sm leading-relaxed">
              {b.overBudget
                ? `On track to EXCEED budget: projected ${fmt(b.projectedMonthTokens)} tokens (${b.projectedPercent}%) vs ${fmt(b.monthlyTokenBudget)} budget by month-end.`
                : b.nearBudget
                ? `Approaching budget: projected ${fmt(b.projectedMonthTokens)} tokens (${b.projectedPercent}%) of ${fmt(b.monthlyTokenBudget)} by month-end.`
                : `On budget: projected ${fmt(b.projectedMonthTokens)} tokens (${b.projectedPercent}%) of ${fmt(b.monthlyTokenBudget)} by month-end.`}
              <span className="block text-steel-300 mt-0.5">
                Month-to-date {fmt(b.monthToDateTokens)} tokens ({b.percentUsed}%) · {b.daysLeft} day(s) left
                {b.estCostProjected != null && ` · est. ${b.estCostProjected} ${b.currency} projected`}
              </span>
            </div>
          </div>
          <div className="mt-2.5 h-2 rounded-full bg-ink-800 overflow-hidden">
            <div className={`h-full rounded-full ${b.overBudget ? "bg-red-500" : b.nearBudget ? "bg-amber400" : "bg-signal"}`}
              style={{ width: `${Math.min(100, b.percentUsed)}%` }} />
          </div>
        </>
      ) : (
        <p className="text-sm text-steel-300">No monthly budget set{canEdit ? " — set one below to enable projection alerts." : "."}</p>
      )}

      {canEdit && (
        <div className="mt-4 flex flex-wrap items-end gap-3">
          <div>
            <label className="block text-[11px] uppercase tracking-wider text-steel-400 mb-1">Monthly token budget</label>
            <input data-testid="ai-usage-budget-input" type="number" min="0" value={budgetInput}
              onChange={(e) => setBudgetInput(e.target.value)} placeholder="e.g. 500000"
              className="w-40 px-3 py-2 rounded-md bg-ink-800 border border-ink-700 text-sm text-white" />
          </div>
          <div>
            <label className="block text-[11px] uppercase tracking-wider text-steel-400 mb-1">Cost / 1K tokens (optional)</label>
            <input data-testid="ai-usage-rate-input" type="number" min="0" step="0.001" value={rateInput}
              onChange={(e) => setRateInput(e.target.value)} placeholder={`${b.currency || "SAR"} e.g. 0.02`}
              className="w-44 px-3 py-2 rounded-md bg-ink-800 border border-ink-700 text-sm text-white" />
          </div>
          <button data-testid="ai-usage-budget-save" onClick={onSave} disabled={saving}
            className="px-4 py-2 rounded-md text-sm font-medium bg-signal hover:bg-signal/90 disabled:opacity-50 text-white flex items-center gap-2">
            {saving ? <Loader2 className="size-4 animate-spin" /> : <Target className="size-4" />} Save budget
          </button>
        </div>
      )}
    </div>
  );
}
