/*
 * Repository Traceability:
 * - Anonymous "Trip Inspection": upload exterior Before + After photos (and optionally interior
 *   Before + After), analyze with the real Gemini vision engine, and get an advisory
 *   exterior + interior damage/condition report with numbered bounding-box markers.
 *   All images are sent in ONE request and deleted on the server right after analysis —
 *   nothing is stored. Bridges the gap until CROMS is wired.
 */
import React, { useCallback, useRef, useState } from "react";
import { CarFront, Loader2, ImagePlus, RotateCcw, ShieldCheck, AlertTriangle, CheckCircle2, Sparkles, Car, Armchair } from "lucide-react";
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
  // Exterior
  DENT: "Dents", SCRATCH: "Scratches", CHIP: "Chips", TIRE: "Tyres", WHEEL: "Wheels / rims",
  GLASS: "Glass", LIGHT: "Lights", PART: "Broken / missing parts", RUST: "Rust / corrosion",
  VANDALISM: "Vandalism / graffiti", DIRT: "Dirt / staining", LEAK: "Fluid leaks",
  // Interior
  SEAT: "Seats", DASHBOARD: "Dashboard / console", TRIM: "Trim / panels", STAIN: "Stains / dirt",
  MISSING: "Missing items", ELECTRONICS: "Screens / controls",
};

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

function DropZone({ label, hint, slot, state, onPick, testId }) {
  const ref = useRef(null);
  return (
    <div className="flex-1 min-w-0">
      <div className="text-[11px] uppercase tracking-wider text-steel-400 mb-2">
        {label}{hint && <span className="text-steel-500 normal-case tracking-normal"> · {hint}</span>}
      </div>
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

const EMPTY = { blob: null, preview: null };

function SectionResult({ section, afterPreview }) {
  const items = section.items || [];
  const nonZero = Object.entries(section.counts || {}).filter(([, c]) => c.total > 0);
  const Icon = section.kind === "INTERIOR" ? Armchair : Car;
  return (
    <div className="rounded-lg border border-ink-700/70 bg-ink-900/60 overflow-hidden" data-testid={`trip-section-${section.kind?.toLowerCase()}`}>
      <div className="px-4 py-3 border-b border-ink-700/60 flex items-center gap-2">
        <Icon className="size-4 text-steel-300" />
        <span className="text-sm font-semibold text-white">{section.label}</span>
        {!section.comparable && (
          <span className="text-[10px] uppercase tracking-wider text-amber400 ml-auto">Not comparable</span>
        )}
      </div>

      <div className="p-4 space-y-4">
        {section.summary && <p className="text-sm text-steel-300">{section.summary}</p>}
        {!section.comparable && section.notComparableReason && (
          <p className="text-xs text-amber400">Reason: {section.notComparableReason}</p>
        )}

        {afterPreview && (
          <div className="rounded-md border border-ink-700/70 bg-ink-950/40 p-2">
            <div className="text-[11px] uppercase tracking-wider text-steel-400 mb-2 px-1">
              {section.label} after — detected issues marked
            </div>
            <div className="relative inline-block max-w-full">
              <img src={afterPreview} alt={`${section.label} after, annotated`} className="block max-w-full rounded-md" />
              {items.map((it, i) =>
                it.box ? (
                  <div
                    key={i}
                    className={`absolute border-2 rounded-sm ${it.status === "NEW" ? "border-signal" : "border-amber400"}`}
                    style={{
                      left: `${it.box.x * 100}%`, top: `${it.box.y * 100}%`,
                      width: `${it.box.w * 100}%`, height: `${it.box.h * 100}%`,
                    }}
                  >
                    <span className={`absolute -top-2 -left-2 size-5 grid place-items-center rounded-full text-[10px] font-bold text-white ${it.status === "NEW" ? "bg-signal" : "bg-amber400"}`}>
                      {i + 1}
                    </span>
                  </div>
                ) : null
              )}
            </div>
          </div>
        )}

        {nonZero.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {nonZero.map(([cat, c]) => (
              <span key={cat} className="text-[11px] rounded-full border border-ink-700 bg-ink-800/70 px-2.5 py-1 text-steel-200">
                {CATEGORY_LABEL[cat] || cat}: <span className="text-white font-semibold">{c.total}</span>
                {c.NEW > 0 && <span className="text-signal-soft"> · {c.NEW} new</span>}
              </span>
            ))}
          </div>
        )}

        <div className="rounded-md border border-ink-700/70 overflow-hidden">
          <div className="px-4 py-2 text-[11px] uppercase tracking-wider text-steel-400 bg-ink-900 border-b border-ink-700/60">
            Findings ({items.length})
          </div>
          {items.length === 0 ? (
            <div className="px-4 py-6 text-center text-steel-400 text-sm">No {section.label.toLowerCase()} issues found.</div>
          ) : (
            <ul className="divide-y divide-ink-700/60">
              {items.map((it, i) => (
                <li key={i} className="px-4 py-3 flex items-start gap-3">
                  <span className={`size-5 mt-0.5 shrink-0 grid place-items-center rounded-full text-[10px] font-bold text-white ${it.status === "NEW" ? "bg-signal" : it.box ? "bg-amber400" : "bg-ink-600"}`}>{i + 1}</span>
                  <span className="text-[11px] font-mono text-steel-300 w-28 shrink-0 mt-0.5">{CATEGORY_LABEL[it.category] || it.category}</span>
                  <div className="flex-1 min-w-0">
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
      </div>
    </div>
  );
}

export default function TripInspection() {
  const [extBefore, setExtBefore] = useState(EMPTY);
  const [extAfter, setExtAfter] = useState(EMPTY);
  const [intBefore, setIntBefore] = useState(EMPTY);
  const [intAfter, setIntAfter] = useState(EMPTY);
  const [busy, setBusy] = useState(false);
  const [stage, setStage] = useState("");
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const setters = { extBefore: setExtBefore, extAfter: setExtAfter, intBefore: setIntBefore, intAfter: setIntAfter };

  const pick = useCallback(async (slot, file) => {
    setError("");
    setResult(null);
    try {
      const prepared = await prepareImage(file);
      setters[slot](prepared);
    } catch {
      setError("Could not read that image. Please try a different photo.");
    }
  }, []);

  const reset = () => {
    setExtBefore(EMPTY); setExtAfter(EMPTY); setIntBefore(EMPTY); setIntAfter(EMPTY);
    setResult(null); setError(""); setStage("");
  };

  const interiorStarted = !!(intBefore.blob || intAfter.blob);
  const interiorIncomplete = interiorStarted && !(intBefore.blob && intAfter.blob);

  const analyze = async () => {
    if (!extBefore.blob || !extAfter.blob) {
      setError("Please add both an exterior Before and After photo.");
      return;
    }
    if (interiorIncomplete) {
      setError("For interior analysis, please add BOTH an interior Before and After photo (or remove the one you added).");
      return;
    }
    setBusy(true);
    setError("");
    setResult(null);
    try {
      setStage("Analyzing with AI (this can take up to a minute)…");
      const fd = new FormData();
      fd.append("exterior_before", extBefore.blob, "exterior_before.jpg");
      fd.append("exterior_after", extAfter.blob, "exterior_after.jpg");
      if (intBefore.blob && intAfter.blob) {
        fd.append("interior_before", intBefore.blob, "interior_before.jpg");
        fd.append("interior_after", intAfter.blob, "interior_after.jpg");
      }
      const { data } = await api.post("/trip-inspection/analyze", fd, {
        headers: { "Content-Type": "multipart/form-data" },
        timeout: 240000,
      });
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
          {result.newIssueCount > 0 && (
            <p className="text-sm text-steel-300 mt-1">{result.newIssueCount} new issue{result.newIssueCount > 1 ? "s" : ""} found across the inspected areas.</p>
          )}
        </div>
      </div>
    );
  };

  const afterPreviewFor = (kind) => (kind === "INTERIOR" ? intAfter.preview : extAfter.preview);

  return (
    <div data-testid={T.tripRoot} className="px-8 py-8 max-w-5xl">
      <div className="text-[11px] uppercase tracking-[0.22em] text-steel-400">Damage Intelligence</div>
      <h1 className="text-2xl font-semibold text-white mt-1 flex items-center gap-3">
        <CarFront className="size-6 text-steel-300" /> Trip Inspection
      </h1>
      <p className="text-sm text-steel-300 mt-2 max-w-2xl flex items-start gap-1.5">
        <ShieldCheck className="size-4 mt-0.5 text-emerald400" />
        Add before/after photos of the vehicle, then analyze. Exterior covers dents, scratches, chips,
        tyres, wheels, glass, lights, broken/missing parts, rust, vandalism, dirt and fluid leaks.
        Interior (optional) covers seats, dashboard, trim, stains, missing items and electronics.
        Advisory only — nothing is stored; your photos are deleted right after analysis.
      </p>

      <section className="mt-6 rounded-lg border border-ink-700/70 bg-ink-900/60 p-5 space-y-6">
        <div>
          <div className="flex items-center gap-2 mb-3">
            <Car className="size-4 text-steel-300" />
            <span className="text-sm font-medium text-white">Exterior</span>
            <span className="text-[11px] text-steel-500">required</span>
          </div>
          <div className="flex flex-col sm:flex-row gap-5">
            <DropZone label="Before the trip" slot="extBefore" state={extBefore} onPick={pick} testId={T.tripBeforeInput} />
            <DropZone label="After the trip" slot="extAfter" state={extAfter} onPick={pick} testId={T.tripAfterInput} />
          </div>
        </div>

        <div className="border-t border-ink-700/60 pt-5">
          <div className="flex items-center gap-2 mb-3">
            <Armchair className="size-4 text-steel-300" />
            <span className="text-sm font-medium text-white">Interior</span>
            <span className="text-[11px] text-steel-500">optional — add both photos to analyze</span>
          </div>
          <div className="flex flex-col sm:flex-row gap-5">
            <DropZone label="Before the trip" hint="interior" slot="intBefore" state={intBefore} onPick={pick} testId={T.tripIntBeforeInput} />
            <DropZone label="After the trip" hint="interior" slot="intAfter" state={intAfter} onPick={pick} testId={T.tripIntAfterInput} />
          </div>
        </div>

        <div className="flex items-center gap-3 flex-wrap">
          <button
            data-testid={T.tripAnalyze}
            onClick={analyze}
            disabled={busy || !extBefore.blob || !extAfter.blob}
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
        {error && <div data-testid={T.tripError} className="text-sm text-signal-soft bg-signal/10 border border-signal/30 rounded-md px-3 py-2">{error}</div>}
      </section>

      {result && (
        <section data-testid={T.tripResult} className="mt-6 space-y-4">
          {overallCard()}
          {(result.sections || []).map((s) => (
            <SectionResult key={s.kind} section={s} afterPreview={afterPreviewFor(s.kind)} />
          ))}
          <p className="text-[11px] text-steel-400">
            Advisory AI result ({result.modelVersion}). Final liability, customer charge, and repair decisions are not made here.
          </p>
        </section>
      )}
    </div>
  );
}
