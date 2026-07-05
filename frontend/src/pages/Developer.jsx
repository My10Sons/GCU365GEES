/*
 * Repository Traceability:
 * - Developer & Integrations console (admin): tenant API keys (shown once, revoke),
 *   rental-system connectors (Generic webhook contract / Speed Auto / GCU365 CROMS —
 *   SANDBOX until credentials), delivery log, and embedded External API docs.
 */
import React, { useEffect, useRef, useState } from "react";
import { KeyRound, Plug, Loader2, Check, Copy, Trash2, SendHorizonal, BookOpen, RefreshCw, TerminalSquare, FileDown, Coins, FlaskConical, ExternalLink, PlayCircle } from "lucide-react";
import { api, envelopeError } from "../lib/api";
import { useAuth } from "../lib/auth-context";

async function downloadPack(ctype, onError) {
  try {
    const { data } = await api.get(`/developer/integration-pack/${ctype}`, { responseType: "blob" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(data);
    a.download = `damage-intelligence-integration-${ctype.toLowerCase()}.md`;
    a.click();
    URL.revokeObjectURL(a.href);
  } catch (e) { onError(envelopeError(e, "Could not download the integration pack.")); }
}

function UsageSection({ onError }) {
  const [usage, setUsage] = useState(null);
  const load = () => api.get("/developer/usage").then(({ data }) => setUsage(data.data)).catch((e) => onError(envelopeError(e, "Could not load usage.")));
  useEffect(() => { load(); /* eslint-disable-next-line */ }, []);
  if (!usage) return null;
  const t = usage.totals || {};
  return (
    <section className="rounded-lg border border-ink-700/70 bg-ink-900/60 p-5" data-testid="dev-usage">
      <div className="flex items-center gap-2 mb-1"><Coins className="size-4 text-steel-300" /><span className="text-sm font-medium text-white">Client usage &amp; billing</span>
        <button data-testid="dev-usage-refresh" onClick={load} className="ml-auto text-steel-400 hover:text-white"><RefreshCw className="size-3.5" /></button>
      </div>
      <p className="text-[12px] text-steel-400 mb-3">Per-API-key consumption via the External API — bill rental-system clients per inspection. Rates: Fast {usage.rates?.fastPerInspectionSar} SAR · Thorough {usage.rates?.thoroughPerInspectionSar} SAR · Plate OCR {usage.rates?.ocrPerCallSar} SAR (measured).</p>
      <div className="grid grid-cols-[1.4fr_1fr_0.8fr_0.8fr_1fr_0.9fr] gap-2 text-[10px] uppercase tracking-wider text-steel-400 border-b border-ink-700/60 pb-1.5">
        <span>Key</span><span>Inspections</span><span>Thorough</span><span>OCR</span><span>Tokens</span><span className="text-right">Est. cost</span>
      </div>
      <ul className="divide-y divide-ink-700/60 text-xs">
        {(usage.keys || []).map((k) => (
          <li key={k.id} className="grid grid-cols-[1.4fr_1fr_0.8fr_0.8fr_1fr_0.9fr] gap-2 py-2 items-center" data-testid={`dev-usage-row-${k.id}`}>
            <span className="truncate"><span className="font-mono text-steel-100">{k.keyPrefix}…</span> <span className="text-steel-400">{k.label}</span>{k.revokedAt && <span className="text-signal-soft"> (revoked)</span>}</span>
            <span className="text-steel-100">{k.inspections}</span>
            <span className="text-steel-300">{k.thoroughInspections}</span>
            <span className="text-steel-300">{k.ocrCalls}</span>
            <span className="text-steel-300 font-mono">{Number(k.totalTokens).toLocaleString()}</span>
            <span className="text-right font-mono text-emerald400">SAR {k.estCostSar.toFixed(2)}</span>
          </li>
        ))}
        {(usage.keys || []).length === 0 && <li className="py-3 text-steel-500">No API keys yet.</li>}
      </ul>
      {(usage.keys || []).length > 0 && (
        <div className="grid grid-cols-[1.4fr_1fr_0.8fr_0.8fr_1fr_0.9fr] gap-2 pt-2 mt-1 border-t border-ink-600 text-xs font-semibold" data-testid="dev-usage-totals">
          <span className="text-steel-300">Total</span>
          <span className="text-white">{t.inspections}</span><span />
          <span className="text-white">{t.ocrCalls}</span>
          <span className="text-white font-mono">{Number(t.tokens || 0).toLocaleString()}</span>
          <span className="text-right font-mono text-emerald400">SAR {(t.estCostSar || 0).toFixed(2)}</span>
        </div>
      )}
    </section>
  );
}

const CONNECTOR_META = {
  GENERIC: { name: "Generic Rental System Connector", desc: "Documented REST + HMAC-signed webhook contract any KSA rental system can implement." },
  SPEED_AUTO: { name: "Speed Auto Systems (CRS/VLS)", desc: "Adapter for Speed Auto Systems — the dominant KSA rental/leasing ERP." },
  GCU365_CROMS: { name: "GCU365 CROMS", desc: "Adapter for the GCU365 CROMS rental operations system." },
};

const inputCls = "mt-1 w-full rounded-md bg-ink-900/70 border border-ink-700 px-3 py-2 text-sm text-steel-100 placeholder:text-steel-500 focus:outline-none focus:border-signal/50";
const btnCls = "px-3 py-1.5 rounded-md text-xs font-medium bg-signal hover:bg-signal/90 disabled:opacity-50 text-white flex items-center gap-1.5";

function StatusChip({ status }) {
  const cls = status === "DELIVERED" || status === "SANDBOX_OK"
    ? "border-emerald400/40 bg-emerald-400/10 text-emerald400"
    : "border-signal/40 bg-signal/10 text-signal-soft";
  return <span className={`text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded-full border ${cls}`}>{status}</span>;
}

function ApiKeysSection({ onError }) {
  const [keys, setKeys] = useState([]);
  const [label, setLabel] = useState("");
  const [busy, setBusy] = useState(false);
  const [created, setCreated] = useState(null);
  const [copied, setCopied] = useState(false);

  const load = () => api.get("/developer/api-keys").then(({ data }) => setKeys(data.data.keys || [])).catch((e) => onError(envelopeError(e, "Could not load API keys.")));
  useEffect(() => { load(); /* eslint-disable-next-line */ }, []);

  const create = async () => {
    setBusy(true);
    try { const { data } = await api.post("/developer/api-keys", { label: label || "API key" }); setCreated(data.data); setLabel(""); load(); }
    catch (e) { onError(envelopeError(e, "Could not create key.")); }
    finally { setBusy(false); }
  };
  const revoke = async (id) => {
    try { await api.post(`/developer/api-keys/${id}/revoke`); load(); }
    catch (e) { onError(envelopeError(e, "Could not revoke key.")); }
  };

  return (
    <section className="rounded-lg border border-ink-700/70 bg-ink-900/60 p-5" data-testid="dev-api-keys">
      <div className="flex items-center gap-2 mb-1"><KeyRound className="size-4 text-steel-300" /><span className="text-sm font-medium text-white">External API keys</span></div>
      <p className="text-[12px] text-steel-400 mb-4">Used by rental systems / mobile apps to call the External API with the <code className="text-steel-200">X-API-Key</code> header. The full key is shown ONCE at creation.</p>
      <div className="flex gap-2 max-w-md">
        <input data-testid="dev-key-label" value={label} onChange={(e) => setLabel(e.target.value)} placeholder="Key label (e.g. Mobile app — production)" className={inputCls + " mt-0"} />
        <button data-testid="dev-key-create" onClick={create} disabled={busy} className={btnCls + " shrink-0"}>{busy ? <Loader2 className="size-3.5 animate-spin" /> : <Check className="size-3.5" />} Create key</button>
      </div>
      {created && (
        <div data-testid="dev-key-created" className="mt-3 rounded-md border border-emerald400/40 bg-emerald-400/10 p-3">
          <div className="text-xs text-emerald400 font-semibold mb-1.5">Copy this key now — it will not be shown again.</div>
          <div className="flex items-center gap-2">
            <code className="text-xs font-mono text-white break-all bg-ink-950 rounded px-2 py-1.5 flex-1">{created.apiKey}</code>
            <button data-testid="dev-key-copy" onClick={() => { navigator.clipboard?.writeText(created.apiKey); setCopied(true); setTimeout(() => setCopied(false), 1500); }} className="text-steel-300 hover:text-white"><Copy className="size-4" />{copied && <span className="sr-only">copied</span>}</button>
          </div>
        </div>
      )}
      <ul className="mt-4 divide-y divide-ink-700/60 border-t border-ink-700/60">
        {keys.map((k) => (
          <li key={k.id} className="py-2.5 flex items-center gap-3 text-xs">
            <span className="font-mono text-steel-100 w-32 truncate">{k.keyPrefix}…</span>
            <span className="text-steel-300 flex-1 truncate">{k.label}</span>
            <span className="text-steel-500">used {k.usageCount || 0}×</span>
            <span className="text-steel-500 hidden sm:inline">{k.lastUsedAt ? `last ${new Date(k.lastUsedAt).toLocaleDateString()}` : "never used"}</span>
            {k.revokedAt ? <span className="text-signal-soft uppercase text-[10px]">revoked</span> : (
              <button data-testid={`dev-key-revoke-${k.id}`} onClick={() => revoke(k.id)} className="text-steel-400 hover:text-signal-soft flex items-center gap-1"><Trash2 className="size-3.5" /> Revoke</button>
            )}
          </li>
        ))}
        {keys.length === 0 && <li className="py-3 text-xs text-steel-500">No API keys yet.</li>}
      </ul>
    </section>
  );
}

function ConnectorCard({ c, onSave, onTest, onError }) {
  const meta = CONNECTOR_META[c.type] || { name: c.type, desc: "" };
  const [form, setForm] = useState({ enabled: c.enabled, mode: c.mode, baseUrl: c.baseUrl || "", apiKey: "", secret: "" });
  const [busy, setBusy] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState(null);
  const [signingSecret, setSigningSecret] = useState(null);

  const save = async () => {
    setBusy(true);
    try {
      const { data } = await api.put(`/developer/connectors/${c.type}`, form);
      if (data.data.signingSecret) setSigningSecret(data.data.signingSecret);
      onSave();
    } catch (e) { onError(envelopeError(e, "Could not save connector.")); }
    finally { setBusy(false); }
  };
  const test = async () => {
    setTesting(true); setTestResult(null);
    try { const { data } = await api.post(`/developer/connectors/${c.type}/test`); setTestResult(data.data); }
    catch (e) { onError(envelopeError(e, "Test failed.")); }
    finally { setTesting(false); }
  };

  return (
    <div className="rounded-lg border border-ink-700/70 bg-ink-900/60 p-4" data-testid={`dev-connector-${c.type}`}>
      <div className="flex items-center gap-2 flex-wrap">
        <span className="text-sm font-medium text-white">{meta.name}</span>
        {form.mode === "sandbox" && <span className="text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded-full border border-amber400/50 bg-amber400/10 text-amber400">⚠ Sandbox</span>}
        {form.mode === "live" && <span className="text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded-full border border-emerald400/50 bg-emerald-400/10 text-emerald400">Live</span>}
        <label className="ml-auto flex items-center gap-1.5 text-xs text-steel-300 cursor-pointer">
          <input type="checkbox" data-testid={`dev-connector-enable-${c.type}`} checked={form.enabled} onChange={(e) => setForm((f) => ({ ...f, enabled: e.target.checked }))} className="size-3.5 accent-signal" /> Enabled
        </label>
      </div>
      <p className="text-[11px] text-steel-500 mt-1">{meta.desc}</p>
      <div className="grid sm:grid-cols-2 gap-3 mt-3">
        <div>
          <label className="text-[11px] uppercase tracking-wider text-steel-400">Mode</label>
          <select value={form.mode} onChange={(e) => setForm((f) => ({ ...f, mode: e.target.value }))} className={inputCls} data-testid={`dev-connector-mode-${c.type}`}>
            <option value="sandbox">Sandbox (simulated)</option>
            <option value="live">Live</option>
          </select>
        </div>
        <div>
          <label className="text-[11px] uppercase tracking-wider text-steel-400">Base URL</label>
          <input value={form.baseUrl} onChange={(e) => setForm((f) => ({ ...f, baseUrl: e.target.value }))} placeholder="https://their-system.example.com" className={inputCls} />
        </div>
        <div>
          <label className="text-[11px] uppercase tracking-wider text-steel-400">API key {c.hasApiKey && <span className="text-emerald400 normal-case">(set)</span>}</label>
          <input type="password" value={form.apiKey} onChange={(e) => setForm((f) => ({ ...f, apiKey: e.target.value }))} placeholder={c.hasApiKey ? "•••••• (leave blank to keep)" : "Their API key"} className={inputCls} />
        </div>
        {c.type === "GENERIC" && (
          <div>
            <label className="text-[11px] uppercase tracking-wider text-steel-400">Signing secret {c.hasSecret && <span className="text-emerald400 normal-case">(set)</span>}</label>
            <input type="password" value={form.secret} onChange={(e) => setForm((f) => ({ ...f, secret: e.target.value }))} placeholder={c.hasSecret ? "•••••• (leave blank to keep)" : "Auto-generated on save"} className={inputCls} />
          </div>
        )}
      </div>
      {signingSecret && (
        <div className="mt-2 text-xs text-emerald400 bg-emerald-400/10 border border-emerald400/30 rounded px-2 py-1.5">Webhook signing secret: <code className="font-mono break-all">{signingSecret}</code> — share it with the receiving system.</div>
      )}
      <div className="flex items-center gap-2 mt-3 flex-wrap">
        <button data-testid={`dev-connector-save-${c.type}`} onClick={save} disabled={busy} className={btnCls}>{busy ? <Loader2 className="size-3.5 animate-spin" /> : <Check className="size-3.5" />} Save</button>
        <button data-testid={`dev-connector-test-${c.type}`} onClick={test} disabled={testing} className="px-3 py-1.5 rounded-md text-xs font-medium border border-ink-600 text-steel-200 hover:bg-ink-800 flex items-center gap-1.5">{testing ? <Loader2 className="size-3.5 animate-spin" /> : <SendHorizonal className="size-3.5" />} Send test event</button>
        <button data-testid={`dev-connector-pack-${c.type}`} onClick={() => downloadPack(c.type, onError)} className="px-3 py-1.5 rounded-md text-xs font-medium border border-ink-600 text-steel-200 hover:bg-ink-800 flex items-center gap-1.5"><FileDown className="size-3.5" /> Download integration pack</button>
        {testResult && <StatusChip status={testResult.status} />}
      </div>
    </div>
  );
}

const EXT_BASE = `${process.env.REACT_APP_BACKEND_URL}/api/v1/damage-intelligence/ext/v1`;
const PLAY_SLOTS = ["front", "rear", "left", "right", "roof", "interior"];

function PairPicker({ slot, files, setFiles }) {
  const set = (which, f) => setFiles((s) => ({ ...s, [`${which}_${slot}`]: f || null }));
  const b = files[`before_${slot}`], a = files[`after_${slot}`];
  return (
    <div className={`rounded-md border p-2.5 ${b && a ? "border-emerald400/40 bg-emerald-400/5" : "border-ink-700 bg-ink-900/40"}`}>
      <div className="text-[11px] uppercase tracking-wider text-steel-300 mb-1.5 flex items-center gap-1.5">{slot}{b && a && <Check className="size-3 text-emerald400" />}</div>
      {[["before", b], ["after", a]].map(([which, f]) => (
        <label key={which} className="flex items-center gap-1.5 text-[11px] text-steel-400 py-0.5 cursor-pointer">
          <span className="w-11">{which}</span>
          <input data-testid={`play-file-${which}-${slot}`} type="file" accept="image/*" onChange={(e) => set(which, e.target.files?.[0])} className="text-[10px] file:mr-1.5 file:rounded file:border-0 file:bg-ink-700 file:px-2 file:py-0.5 file:text-[10px] file:text-steel-200 w-full" />
          {f && <span className="text-emerald400 truncate max-w-[80px]">{f.name}</span>}
        </label>
      ))}
    </div>
  );
}

function VerdictChip({ overall }) {
  const map = {
    NEW_DAMAGE_FOUND: ["New damage found", "border-signal/50 bg-signal/10 text-signal-soft"],
    NO_NEW_DAMAGE: ["No new damage", "border-emerald400/50 bg-emerald-400/10 text-emerald400"],
    NOT_COMPARABLE: ["Not comparable", "border-amber400/50 bg-amber400/10 text-amber400"],
  };
  const [label, cls] = map[overall] || [overall || "—", "border-ink-600 text-steel-300"];
  return <span className={`text-[11px] font-semibold px-2 py-0.5 rounded-full border ${cls}`}>{label}</span>;
}

function RentalEventTester({ apiKey, onError }) {
  const [form, setForm] = useState({ eventType: "rental.checked_out", rentalId: "", plate: "", customerName: "" });
  const [resp, setResp] = useState(null);
  const [busy, setBusy] = useState(false);
  const send = async () => {
    if (!apiKey.trim()) return onError("Paste an API key first.");
    if (!form.rentalId.trim()) return onError("Rental ID is required for rental events.");
    setBusy(true); setResp(null);
    try {
      const r = await fetch(`${EXT_BASE}/rental-events`, {
        method: "POST",
        headers: { "X-API-Key": apiKey.trim(), "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      setResp({ status: r.status, body: await r.json() });
    } catch (e) { onError(e.message || "Rental event failed."); }
    finally { setBusy(false); }
  };
  return (
    <div className="mt-5 border-t border-ink-700/60 pt-4" data-testid="play-rental-events">
      <div className="text-xs font-semibold text-steel-100 mb-2">Rental events tester — <code className="text-steel-300">POST /ext/v1/rental-events</code></div>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        <select data-testid="play-rental-event-type" value={form.eventType} onChange={(e) => setForm((f) => ({ ...f, eventType: e.target.value }))} className={inputCls + " mt-0"}>
          <option value="rental.checked_out">rental.checked_out</option>
          <option value="rental.checked_in">rental.checked_in</option>
        </select>
        <input data-testid="play-rental-id" value={form.rentalId} onChange={(e) => setForm((f) => ({ ...f, rentalId: e.target.value }))} placeholder="Rental ID (RA-1001)" className={inputCls + " mt-0"} />
        <input data-testid="play-rental-plate" value={form.plate} onChange={(e) => setForm((f) => ({ ...f, plate: e.target.value }))} placeholder="Plate" className={inputCls + " mt-0"} />
        <input data-testid="play-rental-customer" value={form.customerName} onChange={(e) => setForm((f) => ({ ...f, customerName: e.target.value }))} placeholder="Customer" className={inputCls + " mt-0"} />
      </div>
      <button data-testid="play-rental-send" onClick={send} disabled={busy} className={btnCls + " mt-2"}>{busy ? <Loader2 className="size-3.5 animate-spin" /> : <SendHorizonal className="size-3.5" />} Send event</button>
      {resp && (
        <pre data-testid="play-rental-response" className="mt-2 bg-ink-950 rounded p-2 overflow-x-auto text-[10px] font-mono text-steel-300">{`HTTP ${resp.status}\n${JSON.stringify(resp.body, null, 1)}`}</pre>
      )}
    </div>
  );
}

function PlaygroundSection() {
  const [apiKey, setApiKey] = useState("");
  const [mode, setMode] = useState("fast");
  const [plate, setPlate] = useState("");
  const [rentalId, setRentalId] = useState("");
  const [files, setFiles] = useState({});
  const [job, setJob] = useState(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const pollRef = useRef(null);
  useEffect(() => () => clearInterval(pollRef.current), []);

  const pairs = PLAY_SLOTS.filter((s) => files[`before_${s}`] && files[`after_${s}`]);

  const submit = async () => {
    setErr(""); setJob(null); clearInterval(pollRef.current);
    if (!apiKey.trim()) return setErr("Paste an API key (dik_…) — create one in the section above.");
    if (pairs.length === 0) return setErr("Add at least one complete before/after pair.");
    const fd = new FormData();
    fd.append("mode", mode);
    fd.append("save_to_vehicle_history", "false");
    const rf = {};
    if (plate.trim()) rf.vehiclePlate = plate.trim();
    if (rentalId.trim()) rf.rentalId = rentalId.trim();
    fd.append("report_fields", JSON.stringify(rf));
    pairs.forEach((s) => { fd.append(`before_${s}`, files[`before_${s}`]); fd.append(`after_${s}`, files[`after_${s}`]); });
    setBusy(true);
    try {
      const r = await fetch(`${EXT_BASE}/trip-inspections`, { method: "POST", headers: { "X-API-Key": apiKey.trim() }, body: fd });
      const body = await r.json();
      if (!r.ok || !body.success) throw new Error(body.errors?.[0]?.message || `HTTP ${r.status}`);
      const jobId = body.data.jobId;
      setJob({ jobId, status: "RUNNING" });
      pollRef.current = setInterval(async () => {
        try {
          const pr = await fetch(`${EXT_BASE}/trip-inspections/${jobId}`, { headers: { "X-API-Key": apiKey.trim() } });
          const pb = await pr.json();
          if (pb.success) {
            setJob({ jobId, ...pb.data });
            if (pb.data.status !== "RUNNING") { clearInterval(pollRef.current); setBusy(false); }
          }
        } catch { /* keep polling */ }
      }, 5000);
    } catch (e) { setErr(e.message); setBusy(false); }
  };

  const res = job?.result;
  return (
    <section className="rounded-lg border border-ink-700/70 bg-ink-900/60 p-5" data-testid="dev-playground">
      <div className="flex items-center gap-2 mb-1"><FlaskConical className="size-4 text-steel-300" /><span className="text-sm font-medium text-white">Sandbox playground</span></div>
      <p className="text-[12px] text-steel-400 mb-4">Try the External API exactly as CROMS would: paste a <code className="text-steel-200">dik_…</code> key, upload test photos, watch the job run, then open the hosted report the integration receives. Nothing is saved to the vehicle registry.</p>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-3">
        <input data-testid="play-api-key" type="password" value={apiKey} onChange={(e) => setApiKey(e.target.value)} placeholder="X-API-Key (dik_…)" className={inputCls + " mt-0 col-span-2 sm:col-span-1"} />
        <select data-testid="play-mode" value={mode} onChange={(e) => setMode(e.target.value)} className={inputCls + " mt-0"}>
          <option value="fast">fast</option><option value="thorough">thorough</option>
        </select>
        <input data-testid="play-plate" value={plate} onChange={(e) => setPlate(e.target.value)} placeholder="Plate (optional)" className={inputCls + " mt-0"} />
        <input data-testid="play-rental" value={rentalId} onChange={(e) => setRentalId(e.target.value)} placeholder="Rental ID (optional)" className={inputCls + " mt-0"} />
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
        {PLAY_SLOTS.map((s) => <PairPicker key={s} slot={s} files={files} setFiles={setFiles} />)}
      </div>
      <div className="flex items-center gap-3 mt-3">
        <button data-testid="play-submit" onClick={submit} disabled={busy} className={btnCls}>
          {busy ? <Loader2 className="size-3.5 animate-spin" /> : <PlayCircle className="size-3.5" />} Submit to /trip-inspections
        </button>
        <span className="text-[11px] text-steel-500">{pairs.length} complete pair{pairs.length === 1 ? "" : "s"}</span>
      </div>
      {err && <div data-testid="play-error" className="mt-2 text-xs text-signal-soft bg-signal/10 border border-signal/30 rounded px-2.5 py-1.5">{err}</div>}
      {job && (
        <div data-testid="play-job" className="mt-3 rounded-md border border-ink-700 bg-ink-950/60 p-3">
          <div className="flex items-center gap-3 flex-wrap text-xs">
            <span className="font-mono text-steel-400">job {job.jobId.slice(0, 12)}…</span>
            {job.status === "RUNNING" && <span data-testid="play-job-running" className="flex items-center gap-1.5 text-amber400"><Loader2 className="size-3.5 animate-spin" /> Analyzing…</span>}
            {job.status === "FAILED" && <span data-testid="play-job-failed" className="text-signal-soft">FAILED — {job.error}</span>}
            {job.status === "DONE" && res && (
              <>
                <VerdictChip overall={res.overall} />
                <span className="text-steel-300">{res.newIssueCount} new issue{res.newIssueCount === 1 ? "" : "s"}</span>
                {res.costSummary && (res.costSummary.low || res.costSummary.high) ? <span className="text-steel-300 font-mono">{res.costSummary.low}–{res.costSummary.high} {res.costSummary.currency}</span> : null}
              </>
            )}
          </div>
          {job.status === "DONE" && res && (
            <div className="mt-2.5 flex items-center gap-2 flex-wrap">
              {res.reportUrl && <a data-testid="play-report-link" href={res.reportUrl} target="_blank" rel="noreferrer" className={btnCls}><ExternalLink className="size-3.5" /> Open hosted report</a>}
              {res.reportPdfUrl && <a data-testid="play-report-pdf" href={res.reportPdfUrl} className="px-3 py-1.5 rounded-md text-xs font-medium border border-ink-600 text-steel-200 hover:bg-ink-800 flex items-center gap-1.5"><FileDown className="size-3.5" /> Download PDF</a>}
              <details className="w-full mt-1">
                <summary data-testid="play-raw-json" className="text-[11px] text-steel-500 cursor-pointer hover:text-steel-300">view raw JSON result (what CROMS receives)</summary>
                <pre className="mt-1 bg-ink-950 rounded p-2 overflow-x-auto text-[10px] font-mono text-steel-300 max-h-72 overflow-y-auto">{JSON.stringify(res, null, 1)}</pre>
              </details>
            </div>
          )}
        </div>
      )}
      <RentalEventTester apiKey={apiKey} onError={setErr} />
    </section>
  );
}


function DocsSection() {
  const base = `${process.env.REACT_APP_BACKEND_URL}/api/v1/damage-intelligence/ext/v1`;
  return (
    <section className="rounded-lg border border-ink-700/70 bg-ink-900/60 p-5" data-testid="dev-api-docs">
      <div className="flex items-center gap-2 mb-3"><BookOpen className="size-4 text-steel-300" /><span className="text-sm font-medium text-white">External API documentation</span></div>
      <div className="space-y-4 text-xs text-steel-300">
        <div>
          <div className="text-steel-100 font-semibold mb-1">Authentication</div>
          <p>Send your API key in the <code className="text-steel-100">X-API-Key</code> header on every request.</p>
        </div>
        <div>
          <div className="text-steel-100 font-semibold mb-1">1 · Submit a trip inspection (async)</div>
          <pre className="bg-ink-950 rounded p-3 overflow-x-auto text-[11px] font-mono text-steel-200">{`curl -X POST "${base}/trip-inspections" \\
  -H "X-API-Key: dik_..." \\
  -F "mode=fast" \\
  -F 'report_fields={"vehiclePlate":"ABC 1234","rentalId":"RA-1001","customerName":"..."}' \\
  -F "before_front=@before.jpg" -F "after_front=@after.jpg"
# → { "jobId": "…", "status": "RUNNING", "poll": "…" }`}</pre>
          <p className="mt-1">Slots: <code>before_front/after_front</code>, <code>_rear</code>, <code>_left</code>, <code>_right</code>, <code>_roof</code>, <code>_interior</code>. At least one complete pair required. <code>save_to_vehicle_history</code> (default true) links the result to the vehicle registry.</p>
        </div>
        <div>
          <div className="text-steel-100 font-semibold mb-1">2 · Poll the result</div>
          <pre className="bg-ink-950 rounded p-3 overflow-x-auto text-[11px] font-mono text-steel-200">{`curl "${base}/trip-inspections/{jobId}" -H "X-API-Key: dik_..."
# status: RUNNING | DONE | FAILED · result = full analysis (sections, costs, risk, vehicleLink)`}</pre>
        </div>
        <div>
          <div className="text-steel-100 font-semibold mb-1">3 · Vehicle history by plate</div>
          <pre className="bg-ink-950 rounded p-3 overflow-x-auto text-[11px] font-mono text-steel-200">{`curl "${base}/vehicles/ABC1234/history" -H "X-API-Key: dik_..."`}</pre>
        </div>
        <div>
          <div className="text-steel-100 font-semibold mb-1">4 · Hosted report (no login needed)</div>
          <p>Every job result and <code>inspection.completed</code> event includes <code className="text-steel-100">reportUrl</code> (rendered HTML report with annotated photos) and <code className="text-steel-100">reportPdfUrl</code> (PDF download). Share the link with any party — the unguessable token is the credential.</p>
        </div>
        <div>
          <div className="text-steel-100 font-semibold mb-1">5 · Inbound rental events (auto-open inspections)</div>
          <pre className="bg-ink-950 rounded p-3 overflow-x-auto text-[11px] font-mono text-steel-200">{`curl -X POST "${base}/rental-events" -H "X-API-Key: dik_..." \\
  -H "Content-Type: application/json" \\
  -d '{"eventType":"rental.checked_out","rentalId":"RA-1001","plate":"ABC 1234","customerName":"..."}'
# eventType: rental.checked_out | rental.checked_in — pre-fills the Trip Inspection screen`}</pre>
        </div>
        <div>
          <div className="text-steel-100 font-semibold mb-1">Webhooks (Generic connector)</div>
          <p>Events <code>inspection.completed</code>, <code>damage_case.created</code>, <code>connection.test</code> are POSTed to <code>{"{baseUrl}"}/webhooks/damage-intelligence</code> with headers <code>X-DI-Event</code>, <code>X-DI-Id</code>, <code>X-DI-Timestamp</code>, <code>X-DI-Signature</code>. Verify (Python):</p>
          <pre className="bg-ink-950 rounded p-3 overflow-x-auto text-[11px] font-mono text-steel-200 mt-1">{`import base64, hashlib, hmac
def verify(secret, headers, raw_body: str, tolerance=300):
    ts = int(headers["X-DI-Timestamp"])
    assert abs(time.time() - ts) < tolerance, "expired"
    mac = hmac.new(secret.encode(), f'{headers["X-DI-Id"]}.{ts}.{raw_body}'.encode(), hashlib.sha256).digest()
    expected = "v1," + base64.b64encode(mac).decode()
    assert hmac.compare_digest(expected, headers["X-DI-Signature"]), "bad signature"`}</pre>
          <p className="mt-1">Delivery is retried 3× (0s / 5s / 25s). Use <code>X-DI-Id</code> for de-duplication.</p>
        </div>
      </div>
    </section>
  );
}

export default function Developer() {
  const { has } = useAuth();
  const [error, setError] = useState("");
  const [connectors, setConnectors] = useState([]);
  const [deliveries, setDeliveries] = useState([]);

  const loadConnectors = () => api.get("/developer/connectors").then(({ data }) => setConnectors(data.data.connectors || [])).catch((e) => setError(envelopeError(e, "Could not load connectors.")));
  const loadDeliveries = () => api.get("/developer/deliveries").then(({ data }) => setDeliveries(data.data.deliveries || [])).catch(() => {});
  useEffect(() => { if (has("di.configuration.manage")) { loadConnectors(); loadDeliveries(); } /* eslint-disable-next-line */ }, []);

  if (!has("di.configuration.manage")) {
    return <div className="px-8 py-8"><p className="text-sm text-amber400">You need administrator permission (di.configuration.manage) for the Developer console.</p></div>;
  }

  return (
    <div data-testid="developer-page" className="px-8 py-8 max-w-4xl space-y-6">
      <div>
        <div className="text-[11px] uppercase tracking-[0.22em] text-steel-400">Damage Intelligence</div>
        <h1 className="text-2xl font-semibold text-white mt-1 flex items-center gap-3"><TerminalSquare className="size-6 text-steel-300" /> API &amp; Integrations</h1>
        <p className="text-sm text-steel-300 mt-2 max-w-2xl">Connect rental systems (Speed Auto, GCU365 CROMS, or any system via the generic contract), manage External API keys, and monitor event deliveries.</p>
      </div>
      {error && <div data-testid="developer-error" className="text-sm text-signal-soft bg-signal/10 border border-signal/30 rounded-md px-3 py-2">{error}</div>}

      <ApiKeysSection onError={setError} />

      <UsageSection onError={setError} />

      <section className="space-y-3" data-testid="dev-connectors">
        <div className="flex items-center gap-2"><Plug className="size-4 text-steel-300" /><span className="text-sm font-medium text-white">Rental-system connectors</span></div>
        {connectors.map((c) => <ConnectorCard key={c.type} c={c} onSave={loadConnectors} onTest={loadDeliveries} onError={setError} />)}
      </section>

      <PlaygroundSection />

      <section className="rounded-lg border border-ink-700/70 bg-ink-900/60 p-5" data-testid="dev-deliveries">
        <div className="flex items-center gap-2 mb-3">
          <SendHorizonal className="size-4 text-steel-300" /><span className="text-sm font-medium text-white">Recent event deliveries</span>
          <button data-testid="dev-deliveries-refresh" onClick={loadDeliveries} className="ml-auto text-steel-400 hover:text-white"><RefreshCw className="size-3.5" /></button>
        </div>
        <ul className="divide-y divide-ink-700/60 text-xs">
          {deliveries.map((d) => (
            <li key={d.id} className="py-2">
              <div className="flex items-center gap-3">
                <StatusChip status={d.status} />
                <span className="text-steel-200 font-mono">{d.event}</span>
                <span className="text-steel-400">{d.connectorType}</span>
                {d.httpStatus && <span className="text-steel-500">HTTP {d.httpStatus}</span>}
                <span className="text-steel-500 ml-auto">{new Date(d.createdAt).toLocaleString()}</span>
              </div>
              {d.requestBody && (
                <details className="mt-1 ml-1">
                  <summary className="text-[10px] text-steel-500 cursor-pointer hover:text-steel-300" data-testid={`dev-delivery-payload-${d.id}`}>view payload sent</summary>
                  <pre className="mt-1 bg-ink-950 rounded p-2 overflow-x-auto text-[10px] font-mono text-steel-300 max-h-64 overflow-y-auto">{(() => { try { return JSON.stringify(JSON.parse(d.requestBody), null, 1); } catch { return d.requestBody; } })()}</pre>
                </details>
              )}
            </li>
          ))}
          {deliveries.length === 0 && <li className="py-3 text-steel-500">No deliveries yet — enable a connector and run an inspection or send a test event.</li>}
        </ul>
      </section>

      <DocsSection />
    </div>
  );
}
