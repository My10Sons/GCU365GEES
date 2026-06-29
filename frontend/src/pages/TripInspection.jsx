/*
 * Repository Traceability:
 * - Anonymous "Trip Inspection": upload a Before + After photo, analyze with the real Gemini
 *   vision engine, and get an advisory dents / scratches / tyre report. Nothing is stored —
 *   images are deleted on the server right after analysis. Bridges the gap until CROMS is wired.
 */
import React, { useCallback, useRef, useState } from "react";
import { CarFront, Loader2, ImagePlus, RotateCcw, ShieldCheck, AlertTriangle, CheckCircle2, Sparkles } from "lucide-react";
import { api, envelopeError } from "../lib/api";
import { T } from "../constants/testIds";

// Downscale + recompress to keep uploads small/fast and within proxy limits.
async function prepareImage(file) {
  const dataUrl = await new Promise((res, rej) => {
    const r = new FileReader();
    r.onload = () => res(r.result);
    r.onerror = rej;
    r.readAsDataURL(file);
  });
  const img = await new Promise((res, rej) => {
    const i = new Image();
    i.onload = () => res(i);
    i.onerror = rej;
    i.src = dataUrl;
  });
  const maxDim = 1600;
  let { width, height } = img;
  if (Math.max(width, height) > maxDim) {
    const scale = maxDim / Math.max(width, height);
    width = Math.round(width * scale);
    height = Math.round(height * scale);
  }
  const canvas = document.createElement("canvas");
  canvas.width = width;
  canvas.height = height;
  canvas.getContext("2d").drawImage(img, 0, 0, width, height);
  const blob = await new Promise((res) => canvas.toBlob(res, "image/jpeg", 0.85));
  return { blob, preview: canvas.toDataURL("image/jpeg", 0.6) };
}

const CATEGORY_LABEL = {
  DENT: "Dents",
  SCRATCH: "Scratches",
  TIRE: "Tyres / wheels",
  GLASS: "Glass",
  LIGHT: "Lights",
  PART: "Broken / missing parts",
};
const CATEGORY_ORDER = ["DENT", "SCRATCH", "TIRE", "GLASS", "LIGHT", "PART"];

function StatusBadge({ status }) {
  const cls = status === "NEW"
    ? "bg-signal/15 text-signal-soft border-signal/40"
    : status === "PRE_EXISTING"
    ? "bg-ink-800 text-steel-300 border-ink-600"
    : status === "RESOLVED"
    ? "bg-emerald-400/10 text-emerald400 border-emerald400/40"
    : "bg-amber400/15 text-amber400 border-amber400/40";
  const label = status === "NEW" ? "New (this trip)" : status === "PRE_EXISTING" ? "Pre-existing" : status === "RESOLVED" ? "Resolved" : "Uncertain";
  return <span className={`text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded border ${cls}`}>{label}</span>;
}

function DropZone({ label, slot, state, onPick, testId }) {
  const ref = useRef(null);
  return (
    <div className="flex-1">
      <div className="text-[11px] uppercase tracking-wider text-steel-400 mb-2">{label}</div>
      <button
        type="button"
        onClick={() => ref.current?.click()}
        className="w-full aspect-[4/3] rounded-lg border-2 border-dashed border-ink-700 hover:border-signal/50 bg-ink-900/60 overflow-hidden grid place-items-center transition-colors"
      >
        {state.preview ? (
          <img src={state.preview} alt={label} className="w-full h-full object-contain bg-ink-950" />
        ) : (
          <span className="flex flex-col items-center gap-2 text-steel-400 text-xs">
            <ImagePlus className="size-7" />
            Click to add photo
          </span>
        )}
      </button>
      <input
        ref={ref}
        data-testid={testId}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        className="hidden"
        onChange={(e) => e.target.files?.[0] && onPick(slot, e.target.files[0])}
      />
    </div>
  );
}

export default function TripInspection() {
  const [before, setBefore] = useState({ blob: null, preview: null });
  const [after, setAfter] = useState({ blob: null, preview: null });
  const [busy, setBusy] = useState(false);
  const [stage, setStage] = useState("");
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const pick = useCallback(async (slot, file) => {
    setError("");
    setResult(null);
    try {
      const prepared = await prepareImage(file);
      (slot === "before" ? setBefore : setAfter)(prepared);
    } catch {
      setError("Could not read that image. Please try a different photo.");
    }
  }, []);

  const reset = () => {
    setBefore({ blob: null, preview: null });
    setAfter({ blob: null, preview: null });
    setResult(null);
    setError("");
    setStage("");
  };

  const analyze = async () => {
    if (!before.blob || !after.blob) {
      setError("Please add both a Before and an After photo.");
      return;
    }
    setBusy(true);
    setError("");
    setResult(null);
    try {
      setStage("Securing session…");
      const { data: sess } = await api.post("/trip-inspection/session", {});
      const token = sess.data.token;

      const upload = async (slot, blob) => {
        const fd = new FormData();
        fd.append("token", token);
        fd.append("slot", slot);
        fd.append("file", blob, `${slot}.jpg`);
        await api.post("/trip-inspection/upload", fd, { headers: { "Content-Type": "multipart/form-data" } });
      };
      setStage("Uploading photos…");
      await upload("before", before.blob);
      await upload("after", after.blob);

      setStage("Analyzing with AI (this can take up to a minute)…");
      const { data } = await api.post("/trip-inspection/analyze", { token }, { timeout: 180000 });
      setResult(data.data);
    } catch (err) {
      setError(envelopeError(err, "Analysis failed. Please retry."));
    } finally {
      setBusy(false);
      setStage("");
    }
  };

  const overallCard = () => {
    if (!result) return null;
    const map = {
      NEW_DAMAGE_FOUND: { cls: "bg-signal/10 border-signal/40 text-signal-soft", icon: AlertTriangle, title: "New damage detected this trip" },
      NO_NEW_DAMAGE: { cls: "bg-emerald-400/10 border-emerald400/40 text-emerald400", icon: CheckCircle2, title: "No new damage detected" },
      NOT_COMPARABLE: { cls: "bg-amber400/10 border-amber400/40 text-amber400", icon: AlertTriangle, title: "Could not compare the photos" },
    };
    const o = map[result.overall] || map.NOT_COMPARABLE;
    const Icon = o.icon;
    return (
      <div className={`rounded-lg border p-5 flex items-start gap-3 ${o.cls}`}>
        <Icon className="size-6 mt-0.5 shrink-0" />
        <div>
          <div className="text-base font-semibold">{o.title}</div>
          {result.summary && <p className="text-sm text-steel-300 mt-1">{result.summary}</p>}
          {result.notComparableReason && <p className="text-xs mt-1">Reason: {result.notComparableReason}</p>}
        </div>
      </div>
    );
  };

  return (
    <div data-testid={T.tripRoot} className="px-8 py-8 max-w-5xl">
      <div className="text-[11px] uppercase tracking-[0.22em] text-steel-400">Damage Intelligence</div>
      <h1 className="text-2xl font-semibold text-white mt-1 flex items-center gap-3">
        <CarFront className="size-6 text-steel-300" /> Trip Inspection
      </h1>
      <p className="text-sm text-steel-300 mt-2 max-w-2xl flex items-start gap-1.5">
        <ShieldCheck className="size-4 mt-0.5 text-emerald400" />
        Add a photo from before and after the rental trip, then analyze. We compare them and report
        dents, scratches, tyre/wheel issues, broken glass, broken lights, and broken or missing parts.
        Advisory only — nothing is stored; your photos are deleted right after analysis.
      </p>

      <section className="mt-6 rounded-lg border border-ink-700/70 bg-ink-900/60 p-5">
        <div className="flex flex-col sm:flex-row gap-5">
          <DropZone label="Before the trip" slot="before" state={before} onPick={pick} testId={T.tripBeforeInput} />
          <DropZone label="After the trip" slot="after" state={after} onPick={pick} testId={T.tripAfterInput} />
        </div>
        <div className="flex items-center gap-3 mt-5">
          <button
            data-testid={T.tripAnalyze}
            onClick={analyze}
            disabled={busy || !before.blob || !after.blob}
            className="px-4 py-2 rounded-md text-sm font-medium bg-signal hover:bg-signal/90 disabled:opacity-50 text-white flex items-center gap-2"
          >
            {busy ? <Loader2 className="size-4 animate-spin" /> : <Sparkles className="size-4" />}
            {busy ? "Working…" : "Analyze"}
          </button>
          <button
            data-testid={T.tripReset}
            onClick={reset}
            disabled={busy}
            className="px-3 py-2 rounded-md text-xs text-steel-200 bg-ink-800 border border-ink-700 hover:bg-ink-700/80 disabled:opacity-50 flex items-center gap-1.5"
          >
            <RotateCcw className="size-3.5" /> Reset
          </button>
          {stage && <span className="text-xs text-steel-400">{stage}</span>}
        </div>
        {error && <div data-testid={T.tripError} className="text-sm text-signal-soft bg-signal/10 border border-signal/30 rounded-md px-3 py-2 mt-3">{error}</div>}
      </section>

      {result && (
        <section data-testid={T.tripResult} className="mt-6 space-y-4">
          {overallCard()}

          {after.preview && (
            <div className="rounded-lg border border-ink-700/70 bg-ink-900/60 p-3">
              <div className="text-[11px] uppercase tracking-wider text-steel-400 mb-2 px-1">
                After photo — detected issues marked
              </div>
              <div className="relative inline-block max-w-full">
                <img src={after.preview} alt="After, annotated" className="block max-w-full rounded-md" />
                {(result.items || []).map((it, i) =>
                  it.box ? (
                    <div
                      key={i}
                      className={`absolute border-2 rounded-sm ${it.status === "NEW" ? "border-signal" : "border-amber400"}`}
                      style={{
                        left: `${it.box.x * 100}%`,
                        top: `${it.box.y * 100}%`,
                        width: `${it.box.w * 100}%`,
                        height: `${it.box.h * 100}%`,
                      }}
                    >
                      <span
                        className={`absolute -top-2 -left-2 size-5 grid place-items-center rounded-full text-[10px] font-bold text-white ${
                          it.status === "NEW" ? "bg-signal" : "bg-amber400"
                        }`}
                      >
                        {i + 1}
                      </span>
                    </div>
                  ) : null
                )}
              </div>
              {(result.items || []).some((it) => !it.box) && (
                <p className="text-[11px] text-steel-400 mt-2 px-1">
                  Some findings could not be precisely located and are listed below without a marker.
                </p>
              )}
            </div>
          )}

          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {CATEGORY_ORDER.map((cat) => {
              const c = result.counts?.[cat] || { NEW: 0, total: 0 };
              return (
                <div key={cat} className="rounded-lg border border-ink-700/70 bg-ink-900/60 p-4">
                  <div className="text-[11px] uppercase tracking-wider text-steel-400">{CATEGORY_LABEL[cat]}</div>
                  <div className="text-2xl font-semibold text-white mt-1">{c.total}</div>
                  <div className={`text-[11px] mt-0.5 ${c.NEW > 0 ? "text-signal-soft" : "text-steel-400"}`}>{c.NEW} new this trip</div>
                </div>
              );
            })}
          </div>

          <div className="rounded-lg border border-ink-700/70 bg-ink-900/60 overflow-hidden">
            <div className="px-4 py-2.5 text-[11px] uppercase tracking-wider text-steel-400 bg-ink-900 border-b border-ink-700/60">
              Findings ({result.items?.length || 0})
            </div>
            {(result.items || []).length === 0 ? (
              <div className="px-4 py-8 text-center text-steel-400 text-sm">No visible damage found.</div>
            ) : (
              <ul className="divide-y divide-ink-700/60">
                {result.items.map((it, i) => (
                  <li key={i} className="px-4 py-3 flex items-start gap-3">
                    <span className={`size-5 mt-0.5 shrink-0 grid place-items-center rounded-full text-[10px] font-bold text-white ${it.status === "NEW" ? "bg-signal" : it.box ? "bg-amber400" : "bg-ink-600"}`}>{i + 1}</span>
                    <span className="text-[11px] font-mono text-steel-300 w-20 shrink-0 mt-0.5">{CATEGORY_LABEL[it.category]?.split(" ")[0]}</span>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 flex-wrap">
                        <StatusBadge status={it.status} />
                        {it.severity && <span className="text-[10px] uppercase tracking-wider text-steel-400">{it.severity}</span>}
                        <span className="text-[11px] font-mono text-steel-400">{(it.confidence * 100).toFixed(0)}%</span>
                      </div>
                      <div className="text-sm text-steel-100 mt-1">{it.location || "—"}</div>
                      {it.detail && <div className="text-[12px] text-steel-400 mt-0.5">{it.detail}</div>}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
          <p className="text-[11px] text-steel-400">
            Advisory AI result ({result.modelVersion}). Final liability, customer charge, and repair decisions are not made here.
          </p>
        </section>
      )}
    </div>
  );
}
