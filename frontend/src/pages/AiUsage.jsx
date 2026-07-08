import React, { useEffect, useRef, useState } from "react";
import { Cpu, Coins, ScanEye, TrendingUp, Loader2, Activity, AlertTriangle, CheckCircle2, Target, Zap, Gauge, FlaskConical, PlayCircle, Trash2, Plus, ShieldCheck, XCircle } from "lucide-react";
import { api } from "../lib/api";
import { useAuth } from "../lib/auth-context";
import { T } from "../constants/testIds";

const RANGES = [7, 30, 90];

// SAR is pegged to USD; Universal Key balance is billed in USD.
const USD_SAR = 3.75;

// Empirically measured on the live preview (each block = 40 single-angle Before/After
// analyses, no-damage pair so no auto-escalation). Balance read at Profile → Universal Key.
const MEASURED = {
  asOf: "Jun 2026",
  anglesPerWalkaround: 5,
  fast: {
    label: "Fast", model: "gemini-3.5-flash",
    calls: 40, tokens: 165501, deltaUsd: 0.42,
  },
  thorough: {
    label: "Thorough", model: "gemini-3.1-pro-preview",
    calls: 40, tokens: 153686, deltaUsd: 1.24,
  },
};

const rateOf = (m) => {
  const usdPer1k = m.deltaUsd / (m.tokens / 1000);
  const usdPerCall = m.deltaUsd / m.calls;
  const tokensPerSection = m.tokens / m.calls;
  const usdPerInspection = usdPerCall * MEASURED.anglesPerWalkaround;
  return {
    ...m,
    tokensPerSection: Math.round(tokensPerSection),
    tokensPerInspection: Math.round(tokensPerSection * MEASURED.anglesPerWalkaround),
    usdPer1k, sarPer1k: usdPer1k * USD_SAR,
    usdPerInspection, sarPerInspection: usdPerInspection * USD_SAR,
  };
};

const RATES = { fast: rateOf(MEASURED.fast), thorough: rateOf(MEASURED.thorough) };

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
        setRateInput(String(data.data.budget?.costPer1kTokens || RATES.fast.sarPer1k.toFixed(4)));
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

          <MeasuredCostModel />

          <BenchmarkSection canEdit={canEdit} />

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


const BENCH_CATEGORIES = ["DENT", "SCRATCH", "CHIP", "TIRE", "WHEEL", "GLASS", "LIGHT", "PART", "RUST", "VANDALISM", "DIRT", "LEAK"];
const BENCH_ANGLES = ["FRONT", "REAR", "LEFT", "RIGHT", "ROOF"];
const inputSm = "px-2.5 py-1.5 rounded-md bg-ink-800 border border-ink-700 text-xs text-white";

function BenchmarkSection({ canEdit }) {
  const [cases, setCases] = useState([]);
  const [runs, setRuns] = useState([]);
  const [activeRun, setActiveRun] = useState(null);
  const [mode, setMode] = useState("fast");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const [showAdd, setShowAdd] = useState(false);
  const pollRef = useRef(null);

  const load = () => Promise.all([
    api.get("/benchmark/cases").then(({ data }) => setCases(data.data.cases || [])),
    api.get("/benchmark/runs?limit=5").then(({ data }) => setRuns(data.data.runs || [])),
  ]).catch(() => {});

  useEffect(() => { load(); return () => clearInterval(pollRef.current); }, []);

  const startRun = async () => {
    setErr(""); setBusy(true);
    try {
      const { data } = await api.post("/benchmark/run", { mode });
      const runId = data.data.runId;
      pollRef.current = setInterval(async () => {
        try {
          const r = await api.get(`/benchmark/runs/${runId}`);
          setActiveRun(r.data.data);
          if (r.data.data.status !== "RUNNING") {
            clearInterval(pollRef.current); setBusy(false); load();
          }
        } catch { /* keep polling */ }
      }, 5000);
      setActiveRun({ runId, status: "RUNNING", cases: [] });
    } catch (e) {
      setErr(e.response?.data?.errors?.[0]?.message || "Could not start run."); setBusy(false);
    }
  };

  const deleteCase = async (id) => {
    await api.delete(`/benchmark/cases/${id}`).catch(() => {});
    load();
  };

  const latest = activeRun || runs[0];

  return (
    <div data-testid="benchmark-section" className="mt-10">
      <div className="flex items-center justify-between flex-wrap gap-3 mb-3">
        <div className="flex items-center gap-2 text-[11px] uppercase tracking-wider text-steel-400">
          <ShieldCheck className="size-3.5" /> Accuracy benchmark · regression suite
        </div>
        {canEdit && (
          <div className="flex items-center gap-2">
            <select data-testid="bench-mode" value={mode} onChange={(e) => setMode(e.target.value)} className={inputSm}>
              <option value="fast">fast</option><option value="thorough">thorough</option>
            </select>
            <button data-testid="bench-run" onClick={startRun} disabled={busy || cases.length === 0}
              className="px-3 py-1.5 rounded-md text-xs font-medium bg-signal hover:bg-signal/90 disabled:opacity-50 text-white flex items-center gap-1.5">
              {busy ? <Loader2 className="size-3.5 animate-spin" /> : <PlayCircle className="size-3.5" />} Run benchmark
            </button>
            <button data-testid="bench-add-toggle" onClick={() => setShowAdd((s) => !s)}
              className="px-3 py-1.5 rounded-md text-xs font-medium border border-ink-600 text-steel-200 hover:bg-ink-800 flex items-center gap-1.5">
              <Plus className="size-3.5" /> Add case
            </button>
          </div>
        )}
      </div>
      <p className="text-[12px] text-steel-400 mb-3">
        Each case is a before/after photo pair with ground-truth findings. A run replays every case
        through the live analysis pipeline and scores recall — run it after any prompt or model change.
        Real AI is used (~0.5 SAR per case).
      </p>
      {err && <div data-testid="bench-error" className="mb-3 text-xs text-red-300 bg-red-500/10 border border-red-500/30 rounded px-2.5 py-1.5">{err}</div>}

      {showAdd && canEdit && <AddCaseForm onDone={() => { setShowAdd(false); load(); }} onError={setErr} />}

      <div data-testid="bench-cases" className="rounded-lg border border-ink-700/70 overflow-hidden">
        {cases.length === 0 ? (
          <div className="px-4 py-4 text-sm text-steel-400 bg-ink-900/60">No benchmark cases yet{canEdit ? " — add your first known-issue photo pair." : "."}</div>
        ) : cases.map((c) => (
          <div key={c.caseId} data-testid={`bench-case-${c.caseId}`} className="flex items-center gap-3 px-4 py-2.5 bg-ink-900/60 border-b border-ink-700/50 last:border-0 text-xs flex-wrap">
            <span className="text-steel-100 font-medium">{c.name}</span>
            <span className="text-steel-500 uppercase text-[10px] tracking-wider">{c.angle}</span>
            <span className="text-steel-400">{c.expected.filter((e) => !e.optional).length} required{c.expected.some((e) => e.optional) ? ` + ${c.expected.filter((e) => e.optional).length} optional` : ""} findings</span>
            {canEdit && (
              <button data-testid={`bench-case-delete-${c.caseId}`} onClick={() => deleteCase(c.caseId)} className="ml-auto text-steel-500 hover:text-red-400"><Trash2 className="size-3.5" /></button>
            )}
          </div>
        ))}
      </div>

      {latest && (
        <div data-testid="bench-latest-run" className="mt-4 rounded-lg border border-ink-700/70 bg-ink-900/60 p-4">
          <div className="flex items-center gap-3 flex-wrap text-xs">
            <span className="text-[11px] uppercase tracking-wider text-steel-400">Latest run</span>
            {latest.status === "RUNNING" ? (
              <span data-testid="bench-run-running" className="flex items-center gap-1.5 text-amber400"><Loader2 className="size-3.5 animate-spin" /> Running… {latest.cases?.length || 0} case(s) done</span>
            ) : (
              <>
                <span data-testid="bench-run-recall" className={`font-semibold ${latest.summary?.recall >= 100 ? "text-emerald400" : latest.summary?.recall >= 70 ? "text-amber400" : "text-red-400"}`}>
                  Recall {latest.summary?.recall ?? 0}%
                </span>
                <span className="text-steel-400">{latest.summary?.foundRequired}/{latest.summary?.requiredCount} required findings detected · {latest.mode} mode · {Number(latest.summary?.tokens || 0).toLocaleString()} tokens</span>
              </>
            )}
          </div>
          {(latest.cases || []).map((rc) => (
            <div key={rc.caseId} className="mt-3 border-t border-ink-700/50 pt-2.5">
              <div className="flex items-center gap-2 text-xs">
                <span className="text-steel-100 font-medium">{rc.name}</span>
                {rc.status === "FAILED" ? (
                  <span className="text-red-400">FAILED — {rc.error}</span>
                ) : (
                  <span className={`font-semibold ${rc.recall >= 100 ? "text-emerald400" : "text-amber400"}`}>{rc.foundRequired}/{rc.requiredCount} found</span>
                )}
                {rc.extraDetections > 0 && <span className="text-steel-500">+{rc.extraDetections} extra detection(s)</span>}
              </div>
              <div className="mt-1.5 flex flex-wrap gap-1.5">
                {(rc.expected || []).map((e, i) => (
                  <span key={i} className={`inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-full border ${e.found ? "border-emerald400/40 bg-emerald-400/10 text-emerald400" : e.optional ? "border-ink-600 text-steel-500" : "border-red-500/40 bg-red-500/10 text-red-300"}`}>
                    {e.found ? <CheckCircle2 className="size-3" /> : <XCircle className="size-3" />}
                    {e.category}{e.keywords?.length ? ` (${e.keywords[0]})` : ""}{e.optional ? " · opt" : ""}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {runs.length > 1 && (
        <div data-testid="bench-history" className="mt-3 text-[11px] text-steel-400">
          History: {runs.slice(0, 5).map((r) => `${new Date(r.startedAt).toLocaleDateString()} → ${r.summary?.recall ?? "…"}%`).join(" · ")}
        </div>
      )}
    </div>
  );
}

function AddCaseForm({ onDone, onError }) {
  const [name, setName] = useState("");
  const [angle, setAngle] = useState("REAR");
  const [before, setBefore] = useState(null);
  const [after, setAfter] = useState(null);
  const [rows, setRows] = useState([{ category: "SCRATCH", keywords: "", optional: false }]);
  const [saving, setSaving] = useState(false);

  const save = async () => {
    if (!name.trim() || !before || !after) return onError("Name and both photos are required.");
    setSaving(true);
    try {
      const fd = new FormData();
      fd.append("name", name.trim());
      fd.append("angle", angle);
      fd.append("expected", JSON.stringify(rows.map((r) => ({
        category: r.category, optional: r.optional,
        keywords: r.keywords.split(",").map((k) => k.trim()).filter(Boolean),
      }))));
      fd.append("before", before);
      fd.append("after", after);
      await api.post("/benchmark/cases", fd, { headers: { "Content-Type": "multipart/form-data" } });
      onDone();
    } catch (e) {
      onError(e.response?.data?.errors?.[0]?.message || "Could not create case.");
    } finally { setSaving(false); }
  };

  return (
    <div data-testid="bench-add-form" className="mb-4 rounded-lg border border-ink-700/70 bg-ink-900/60 p-4 space-y-3">
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        <input data-testid="bench-name" value={name} onChange={(e) => setName(e.target.value)} placeholder="Case name" className={inputSm + " col-span-2"} />
        <select data-testid="bench-angle" value={angle} onChange={(e) => setAngle(e.target.value)} className={inputSm}>
          {BENCH_ANGLES.map((a) => <option key={a} value={a}>{a}</option>)}
        </select>
      </div>
      <div className="grid grid-cols-2 gap-2 text-xs text-steel-400">
        <label>Before photo<input data-testid="bench-before" type="file" accept="image/*" onChange={(e) => setBefore(e.target.files?.[0])} className="block mt-1 text-[11px]" /></label>
        <label>After photo<input data-testid="bench-after" type="file" accept="image/*" onChange={(e) => setAfter(e.target.files?.[0])} className="block mt-1 text-[11px]" /></label>
      </div>
      <div>
        <div className="text-[11px] uppercase tracking-wider text-steel-400 mb-1.5">Expected findings (ground truth)</div>
        {rows.map((r, i) => (
          <div key={i} className="flex items-center gap-2 mb-1.5 flex-wrap">
            <select value={r.category} onChange={(e) => setRows((s) => s.map((x, j) => j === i ? { ...x, category: e.target.value } : x))} className={inputSm}>
              {BENCH_CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
            <input value={r.keywords} onChange={(e) => setRows((s) => s.map((x, j) => j === i ? { ...x, keywords: e.target.value } : x))}
              placeholder="location keywords, comma-separated (e.g. left, bumper)" className={inputSm + " flex-1 min-w-[200px]"} />
            <label className="flex items-center gap-1 text-[11px] text-steel-400">
              <input type="checkbox" checked={r.optional} onChange={(e) => setRows((s) => s.map((x, j) => j === i ? { ...x, optional: e.target.checked } : x))} /> optional
            </label>
            {rows.length > 1 && <button onClick={() => setRows((s) => s.filter((_, j) => j !== i))} className="text-steel-500 hover:text-red-400"><Trash2 className="size-3.5" /></button>}
          </div>
        ))}
        <button data-testid="bench-add-row" onClick={() => setRows((s) => [...s, { category: "SCRATCH", keywords: "", optional: false }])}
          className="text-[11px] text-steel-400 hover:text-steel-200 flex items-center gap-1"><Plus className="size-3" /> add finding</button>
      </div>
      <button data-testid="bench-save-case" onClick={save} disabled={saving}
        className="px-3 py-1.5 rounded-md text-xs font-medium bg-signal hover:bg-signal/90 disabled:opacity-50 text-white flex items-center gap-1.5">
        {saving ? <Loader2 className="size-3.5 animate-spin" /> : <Plus className="size-3.5" />} Save case
      </button>
    </div>
  );
}


function ModeCard({ rate, icon: Icon, tone }) {
  const sar = (n) => `${Number(n).toFixed(2)} SAR`;
  return (
    <div data-testid={`ai-cost-card-${rate.label.toLowerCase()}`}
      className={`rounded-lg border p-4 ${tone === "fast" ? "border-signal/40 bg-signal/5" : "border-amber400/40 bg-amber400/5"}`}>
      <div className="flex items-center gap-2">
        <Icon className={`size-4 ${tone === "fast" ? "text-signal" : "text-amber400"}`} />
        <span className="text-sm font-semibold text-white">{rate.label}</span>
        <span className="text-[11px] text-steel-400 font-mono">{rate.model}</span>
      </div>
      <div className="mt-3 text-2xl font-semibold text-white">
        {sar(rate.sarPerInspection)}
        <span className="text-xs font-normal text-steel-400"> / inspection</span>
      </div>
      <div className="text-[11px] text-steel-400 mt-1">
        {MEASURED.anglesPerWalkaround}-angle walkaround · ~{Number(rate.tokensPerInspection).toLocaleString()} tokens
      </div>
      <div className="mt-2 text-[11px] text-steel-400">
        ≈ {rate.sarPer1k.toFixed(4)} SAR / 1K tokens (${rate.usdPer1k.toFixed(5)})
      </div>
    </div>
  );
}

function MeasuredCostModel() {
  const rows = [
    { k: "Tokens / angle", f: Number(RATES.fast.tokensPerSection).toLocaleString(), t: Number(RATES.thorough.tokensPerSection).toLocaleString() },
    { k: "Tokens / 5-angle inspection", f: Number(RATES.fast.tokensPerInspection).toLocaleString(), t: Number(RATES.thorough.tokensPerInspection).toLocaleString() },
    { k: "Cost / 1K tokens", f: `${RATES.fast.sarPer1k.toFixed(4)} SAR`, t: `${RATES.thorough.sarPer1k.toFixed(4)} SAR` },
    { k: "Cost / inspection", f: `${RATES.fast.sarPerInspection.toFixed(2)} SAR`, t: `${RATES.thorough.sarPerInspection.toFixed(2)} SAR` },
    { k: "Cost / inspection (USD)", f: `$${RATES.fast.usdPerInspection.toFixed(3)}`, t: `$${RATES.thorough.usdPerInspection.toFixed(3)}` },
  ];
  return (
    <div data-testid="ai-usage-cost-model" className="mt-8">
      <div className="flex items-center gap-2 text-[11px] uppercase tracking-wider text-steel-400 mb-3">
        <FlaskConical className="size-3.5" /> Measured cost per inspection · {MEASURED.asOf}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <ModeCard rate={RATES.fast} icon={Zap} tone="fast" />
        <ModeCard rate={RATES.thorough} icon={Gauge} tone="thorough" />
      </div>

      <div className="mt-4 overflow-hidden rounded-lg border border-ink-700/70">
        <table data-testid="ai-usage-cost-table" className="w-full text-sm">
          <thead>
            <tr className="bg-ink-900/60 text-steel-400 text-[11px] uppercase tracking-wider">
              <th className="text-left font-medium px-4 py-2.5">Metric</th>
              <th className="text-right font-medium px-4 py-2.5">Fast (Flash)</th>
              <th className="text-right font-medium px-4 py-2.5">Thorough (Pro)</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-ink-700/60">
            {rows.map((r) => (
              <tr key={r.k} className="text-steel-200">
                <td className="px-4 py-2.5 text-steel-300">{r.k}</td>
                <td className="px-4 py-2.5 text-right tabular-nums">{r.f}</td>
                <td className="px-4 py-2.5 text-right tabular-nums">{r.t}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <p className="mt-3 text-[11px] text-steel-400">
        Empirical: {MEASURED.fast.calls} Fast + {MEASURED.thorough.calls} Thorough single-angle analyses
        against the live Universal Key. Balance billed in USD; SAR shown at the fixed 3.75 peg.
        Thorough ≈ {(RATES.thorough.sarPerInspection / RATES.fast.sarPerInspection).toFixed(1)}× the cost of Fast.
        Auto-escalation adds one Pro call per uncertain/high-severity angle.
      </p>
    </div>
  );
}
