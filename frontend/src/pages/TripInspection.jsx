/*
 * Repository Traceability:
 * - Anonymous "Trip Inspection": choose which areas to inspect (Exterior and/or Interior),
 *   upload Before + After photos for each selected area, analyze with the real Gemini vision
 *   engine, and get an advisory damage/condition report with numbered bounding-box markers.
 *   All images are sent in ONE request and deleted on the server right after analysis —
 *   nothing is stored. A one-click annotated PDF report can be exported client-side.
 */
import React, { useCallback, useRef, useState } from "react";
import { jsPDF } from "jspdf";
import { CarFront, Loader2, ImagePlus, RotateCcw, ShieldCheck, AlertTriangle, CheckCircle2, Sparkles, Car, Armchair, FileDown, Check } from "lucide-react";
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
  const img = await loadImage(dataUrl);
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
  return { blob, preview: canvas.toDataURL("image/jpeg", 0.7) };
}

function loadImage(src) {
  return new Promise((res, rej) => {
    const i = new Image();
    i.onload = () => res(i);
    i.onerror = rej;
    i.src = src;
  });
}

const CATEGORY_LABEL = {
  DENT: "Dents", SCRATCH: "Scratches", CHIP: "Chips", TIRE: "Tyres", WHEEL: "Wheels / rims",
  GLASS: "Glass", LIGHT: "Lights", PART: "Broken / missing parts", RUST: "Rust / corrosion",
  VANDALISM: "Vandalism / graffiti", DIRT: "Dirt / staining", LEAK: "Fluid leaks",
  SEAT: "Seats", DASHBOARD: "Dashboard / console", TRIM: "Trim / panels", STAIN: "Stains / dirt",
  MISSING: "Missing items", ELECTRONICS: "Screens / controls",
};

const STATUS_TEXT = { NEW: "New (this trip)", PRE_EXISTING: "Pre-existing", RESOLVED: "Resolved", UNCERTAIN: "Uncertain" };

// Compose an annotated JPEG (image + numbered boxes) on a canvas — robust, no html2canvas.
async function composeAnnotated(previewUrl, items) {
  const img = await loadImage(previewUrl);
  const canvas = document.createElement("canvas");
  canvas.width = img.naturalWidth;
  canvas.height = img.naturalHeight;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(img, 0, 0);
  (items || []).forEach((it, i) => {
    if (!it.box) return;
    const x = it.box.x * canvas.width;
    const y = it.box.y * canvas.height;
    const w = it.box.w * canvas.width;
    const h = it.box.h * canvas.height;
    const color = it.status === "NEW" ? "#ef4444" : "#f59e0b";
    ctx.lineWidth = Math.max(2, canvas.width * 0.004);
    ctx.strokeStyle = color;
    ctx.strokeRect(x, y, w, h);
    const r = Math.max(11, canvas.width * 0.014);
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.fillStyle = color;
    ctx.fill();
    ctx.fillStyle = "#fff";
    ctx.font = `bold ${Math.round(r * 1.15)}px sans-serif`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(String(i + 1), x, y);
  });
  return canvas.toDataURL("image/jpeg", 0.85);
}

function StatusBadge({ status }) {
  const cls = status === "NEW"
    ? "bg-signal/15 text-signal-soft border-signal/40"
    : status === "PRE_EXISTING"
    ? "bg-ink-800 text-steel-300 border-ink-600"
    : status === "RESOLVED"
    ? "bg-emerald-400/10 text-emerald400 border-emerald400/40"
    : "bg-amber400/15 text-amber400 border-amber400/40";
  return <span className={`text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded border ${cls}`}>{STATUS_TEXT[status]}</span>;
}

function ScopeToggle({ label, icon: Icon, active, onClick, testId }) {
  return (
    <button
      type="button"
      data-testid={testId}
      aria-pressed={active}
      onClick={onClick}
      className={`flex items-center gap-2 px-3.5 py-2 rounded-full border text-sm transition-colors ${
        active
          ? "border-signal/50 bg-signal/10 text-white"
          : "border-ink-700 bg-ink-900/60 text-steel-400 hover:text-steel-200 hover:border-ink-600"
      }`}
    >
      <span className={`size-4 grid place-items-center rounded-full border ${active ? "bg-signal border-signal" : "border-ink-600"}`}>
        {active && <Check className="size-3 text-white" />}
      </span>
      <Icon className="size-4" />
      {label}
    </button>
  );
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
        {!section.comparable && <span className="text-[10px] uppercase tracking-wider text-amber400 ml-auto">Not comparable</span>}
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
                    style={{ left: `${it.box.x * 100}%`, top: `${it.box.y * 100}%`, width: `${it.box.w * 100}%`, height: `${it.box.h * 100}%` }}
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
  const [scope, setScope] = useState({ exterior: true, interior: false });
  const [reportFields, setReportFields] = useState({
    customerName: "", vehiclePlate: "", vehicleModel: "", rentalId: "", inspectorName: "",
  });
  const [includeSignatures, setIncludeSignatures] = useState(true);
  const [extBefore, setExtBefore] = useState(EMPTY);
  const [extAfter, setExtAfter] = useState(EMPTY);
  const [intBefore, setIntBefore] = useState(EMPTY);
  const [intAfter, setIntAfter] = useState(EMPTY);
  const [busy, setBusy] = useState(false);
  const [exporting, setExporting] = useState(false);
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

  const toggleScope = (key) => {
    setError("");
    setResult(null);
    setScope((s) => {
      const next = { ...s, [key]: !s[key] };
      if (!next[key]) {
        if (key === "exterior") { setExtBefore(EMPTY); setExtAfter(EMPTY); }
        else { setIntBefore(EMPTY); setIntAfter(EMPTY); }
      }
      return next;
    });
  };

  const reset = () => {
    setExtBefore(EMPTY); setExtAfter(EMPTY); setIntBefore(EMPTY); setIntAfter(EMPTY);
    setResult(null); setError(""); setStage("");
  };

  const extComplete = !!(extBefore.blob && extAfter.blob);
  const intComplete = !!(intBefore.blob && intAfter.blob);
  const extIncomplete = scope.exterior && !extComplete;
  const intIncomplete = scope.interior && !intComplete;
  const anySelected = scope.exterior || scope.interior;
  const anyComplete = (scope.exterior && extComplete) || (scope.interior && intComplete);
  const canAnalyze = !busy && anySelected && !extIncomplete && !intIncomplete && anyComplete;

  const analyze = async () => {
    setBusy(true);
    setError("");
    setResult(null);
    try {
      setStage("Analyzing with AI (this can take up to a minute)…");
      const fd = new FormData();
      if (scope.exterior && extComplete) {
        fd.append("exterior_before", extBefore.blob, "exterior_before.jpg");
        fd.append("exterior_after", extAfter.blob, "exterior_after.jpg");
      }
      if (scope.interior && intComplete) {
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

  const afterPreviewFor = (kind) => (kind === "INTERIOR" ? intAfter.preview : extAfter.preview);

  const exportPdf = async () => {
    if (!result) return;
    setExporting(true);
    try {
      const doc = new jsPDF({ unit: "pt", format: "a4" });
      const pageW = doc.internal.pageSize.getWidth();
      const pageH = doc.internal.pageSize.getHeight();
      const M = 40;
      let y = M;
      const write = (text, size, color, gap, bold) => {
        doc.setFont("helvetica", bold ? "bold" : "normal");
        doc.setFontSize(size);
        doc.setTextColor(color[0], color[1], color[2]);
        doc.splitTextToSize(text, pageW - 2 * M).forEach((l) => {
          if (y > pageH - M) { doc.addPage(); y = M; }
          doc.text(l, M, y);
          y += gap;
        });
      };

      // --- Branded header (tenant logo + company / branch) ---
      const b = result.branding || {};
      let headerBottom = y;
      let textX = M;
      if (b.logoDataUrl) {
        try {
          const li = await loadImage(b.logoDataUrl);
          const lw = 56;
          const lh = lw * (li.naturalHeight / li.naturalWidth);
          const fmt = /^data:image\/(jpeg|jpg)/i.test(b.logoDataUrl) ? "JPEG" : /^data:image\/webp/i.test(b.logoDataUrl) ? "WEBP" : "PNG";
          doc.addImage(b.logoDataUrl, fmt, M, y, lw, lh);
          textX = M + lw + 14;
          headerBottom = y + lh;
        } catch { /* ignore bad logo */ }
      }
      let ty = y + 4;
      if (b.companyName) {
        doc.setFont("helvetica", "bold"); doc.setFontSize(15); doc.setTextColor(17, 17, 17);
        doc.text(b.companyName, textX, ty + 10); ty += 20;
      }
      if (b.branchName) {
        doc.setFont("helvetica", "normal"); doc.setFontSize(10); doc.setTextColor(110, 110, 110);
        doc.text(b.branchName, textX, ty + 6); ty += 14;
      }
      y = Math.max(headerBottom, ty) + 14;
      doc.setDrawColor(220, 220, 220); doc.line(M, y, pageW - M, y); y += 20;

      // --- Title + meta ---
      write("Trip Inspection Report", 18, [17, 17, 17], 22, true);
      write(`Generated ${new Date().toLocaleString()}  ·  ${result.modelVersion}`, 9, [120, 120, 120], 12);
      write("Advisory AI result. Final liability, customer charge, and repair decisions are not made here.", 8, [150, 150, 150], 16);

      // --- Reference fields ---
      const f = reportFields;
      const refs = [];
      if (f.customerName) refs.push(["Customer", f.customerName]);
      if (f.vehiclePlate) refs.push(["Vehicle plate", f.vehiclePlate]);
      if (f.vehicleModel) refs.push(["Make / model", f.vehicleModel]);
      if (f.rentalId) refs.push(["Rental ID", f.rentalId]);
      if (f.inspectorName) refs.push(["Inspector", f.inspectorName]);
      if (refs.length > 0) {
        y += 4;
        const colW = (pageW - 2 * M) / 2;
        for (let i = 0; i < refs.length; i += 2) {
          if (y > pageH - M) { doc.addPage(); y = M; }
          [refs[i], refs[i + 1]].forEach((r, c) => {
            if (!r) return;
            const x = M + c * colW;
            doc.setFont("helvetica", "bold"); doc.setFontSize(9); doc.setTextColor(110, 110, 110);
            doc.text(`${r[0]}:`, x, y);
            doc.setFont("helvetica", "normal"); doc.setTextColor(30, 30, 30);
            doc.text(String(r[1]), x + 78, y);
          });
          y += 15;
        }
      }
      y += 6;
      const verdict = result.overall === "NEW_DAMAGE_FOUND" ? "New damage detected this trip"
        : result.overall === "NO_NEW_DAMAGE" ? "No new damage detected" : "Could not compare the photos";
      write(verdict, 14, result.overall === "NEW_DAMAGE_FOUND" ? [200, 40, 40] : [20, 120, 60], 18, true);
      if (result.newIssueCount > 0) write(`${result.newIssueCount} new issue(s) found across the inspected areas.`, 10, [60, 60, 60], 16);
      y += 6;

      for (const s of result.sections || []) {
        if (y > pageH - 140) { doc.addPage(); y = M; }
        write(`${s.label}${!s.comparable ? "  (not comparable)" : ""}`, 13, [17, 17, 17], 18, true);
        if (s.summary) write(s.summary, 10, [60, 60, 60], 14);

        const beforeP = s.kind === "INTERIOR" ? intBefore.preview : extBefore.preview;
        const afterP = afterPreviewFor(s.kind);
        if (afterP) {
          const annotated = await composeAnnotated(afterP, s.items);
          const gap = 12;
          const colW = (pageW - 2 * M - gap) / 2;
          const afterImg = await loadImage(annotated);
          const beforeImg = beforeP ? await loadImage(beforeP) : null;
          const hA = colW * (afterImg.naturalHeight / afterImg.naturalWidth);
          const hB = beforeImg ? colW * (beforeImg.naturalHeight / beforeImg.naturalWidth) : 0;
          const rowH = Math.max(hA, hB);
          if (y + rowH + 16 > pageH - M) { doc.addPage(); y = M; }
          doc.setFont("helvetica", "bold");
          doc.setFontSize(9);
          doc.setTextColor(90, 90, 90);
          doc.text("Before", M, y);
          doc.text("After (issues marked)", M + colW + gap, y);
          const imgY = y + 5;
          if (beforeImg) doc.addImage(beforeP, "JPEG", M, imgY, colW, hB);
          doc.addImage(annotated, "JPEG", M + colW + gap, imgY, colW, hA);
          y = imgY + rowH + 14;
        }

        if (y > pageH - 60) { doc.addPage(); y = M; }
        write(`Findings (${(s.items || []).length})`, 11, [17, 17, 17], 16, true);
        if ((s.items || []).length === 0) {
          write("No issues found.", 10, [120, 120, 120], 14);
        } else {
          s.items.forEach((it, i) => {
            if (y > pageH - 40) { doc.addPage(); y = M; }
            const sev = it.severity ? `  ·  ${it.severity}` : "";
            write(`${i + 1}.  ${CATEGORY_LABEL[it.category] || it.category}  ·  ${STATUS_TEXT[it.status]}${sev}  ·  ${(it.confidence * 100).toFixed(0)}%`, 10, [30, 30, 30], 13, true);
            write(`${it.location || "—"}${it.detail ? `  —  ${it.detail}` : ""}`, 9, [90, 90, 90], 13);
          });
        }
        y += 10;
      }

      if (includeSignatures) {
        const blockTop = pageH - 96;
        if (y > blockTop - 10) { doc.addPage(); y = M; }
        const sy = Math.max(y + 10, blockTop);
        const gap = 30;
        const colW = (pageW - 2 * M - gap) / 2;
        doc.setDrawColor(120, 120, 120);
        doc.line(M, sy, M + colW, sy);
        doc.line(M + colW + gap, sy, pageW - M, sy);
        doc.setFont("helvetica", "normal"); doc.setFontSize(9); doc.setTextColor(90, 90, 90);
        doc.text("Customer signature", M, sy + 13);
        doc.text("Staff signature", M + colW + gap, sy + 13);
        doc.text("Date: ____________________", M, sy + 30);
        doc.text("Date: ____________________", M + colW + gap, sy + 30);
      }

      doc.save(`trip-inspection-report-${Date.now()}.pdf`);
    } catch (e) {
      console.error("PDF export failed", e);
      setError("Could not generate the PDF. Please try again.");
    } finally {
      setExporting(false);
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
        <div className="flex-1">
          <div className="text-base font-semibold">{o.title}</div>
          {result.newIssueCount > 0 && (
            <p className="text-sm text-steel-300 mt-1">{result.newIssueCount} new issue{result.newIssueCount > 1 ? "s" : ""} found across the inspected areas.</p>
          )}
        </div>
        <button
          data-testid={T.tripExportPdf}
          onClick={exportPdf}
          disabled={exporting}
          className="shrink-0 px-3 py-2 rounded-md text-xs font-medium bg-ink-800 border border-ink-700 hover:bg-ink-700/80 text-steel-100 flex items-center gap-1.5 disabled:opacity-50"
        >
          {exporting ? <Loader2 className="size-3.5 animate-spin" /> : <FileDown className="size-3.5" />}
          {exporting ? "Exporting…" : "Export PDF"}
        </button>
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
        Choose what to inspect, then add before/after photos and analyze. Exterior covers dents,
        scratches, chips, tyres, wheels, glass, lights, broken/missing parts, rust, vandalism, dirt
        and fluid leaks. Interior covers seats, dashboard, trim, stains, missing items and electronics.
        Advisory only — nothing is stored; your photos are deleted right after analysis.
      </p>

      <section className="mt-6 rounded-lg border border-ink-700/70 bg-ink-900/60 p-5 space-y-6">
        <div>
          <div className="text-[11px] uppercase tracking-wider text-steel-400 mb-2">What to inspect</div>
          <div className="flex gap-2.5 flex-wrap">
            <ScopeToggle label="Exterior" icon={Car} active={scope.exterior} onClick={() => toggleScope("exterior")} testId={T.tripScopeExterior} />
            <ScopeToggle label="Interior" icon={Armchair} active={scope.interior} onClick={() => toggleScope("interior")} testId={T.tripScopeInterior} />
          </div>
          {!anySelected && <p className="text-xs text-amber400 mt-2">Select at least one area to inspect.</p>}
        </div>

        {scope.exterior && (
          <div className="border-t border-ink-700/60 pt-5">
            <div className="flex items-center gap-2 mb-3">
              <Car className="size-4 text-steel-300" />
              <span className="text-sm font-medium text-white">Exterior photos</span>
            </div>
            <div className="flex flex-col sm:flex-row gap-5">
              <DropZone label="Before the trip" slot="extBefore" state={extBefore} onPick={pick} testId={T.tripBeforeInput} />
              <DropZone label="After the trip" slot="extAfter" state={extAfter} onPick={pick} testId={T.tripAfterInput} />
            </div>
            {extIncomplete && <p className="text-xs text-amber400 mt-2">Add both a Before and After exterior photo to include this area.</p>}
          </div>
        )}

        {scope.interior && (
          <div className="border-t border-ink-700/60 pt-5">
            <div className="flex items-center gap-2 mb-3">
              <Armchair className="size-4 text-steel-300" />
              <span className="text-sm font-medium text-white">Interior photos</span>
            </div>
            <div className="flex flex-col sm:flex-row gap-5">
              <DropZone label="Before the trip" hint="interior" slot="intBefore" state={intBefore} onPick={pick} testId={T.tripIntBeforeInput} />
              <DropZone label="After the trip" hint="interior" slot="intAfter" state={intAfter} onPick={pick} testId={T.tripIntAfterInput} />
            </div>
            {intIncomplete && <p className="text-xs text-amber400 mt-2">Add both a Before and After interior photo to include this area.</p>}
          </div>
        )}

        <div className="border-t border-ink-700/60 pt-5">
          <div className="flex items-center gap-2 mb-3">
            <FileDown className="size-4 text-steel-300" />
            <span className="text-sm font-medium text-white">Report details</span>
            <span className="text-[11px] text-steel-500">optional — printed on the exported PDF</span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {[
              ["customerName", "Customer name", "trip-field-customer"],
              ["vehiclePlate", "Vehicle plate", "trip-field-plate"],
              ["vehicleModel", "Make / model", "trip-field-model"],
              ["rentalId", "Rental ID", "trip-field-rental"],
              ["inspectorName", "Inspector name", "trip-field-inspector"],
            ].map(([key, label, tid]) => (
              <div key={key}>
                <label className="text-[11px] uppercase tracking-wider text-steel-400">{label}</label>
                <input
                  data-testid={tid}
                  value={reportFields[key]}
                  onChange={(e) => setReportFields((s) => ({ ...s, [key]: e.target.value }))}
                  className="mt-1 w-full rounded-md bg-ink-900/70 border border-ink-700 px-3 py-2 text-sm text-steel-100 placeholder:text-steel-500 focus:outline-none focus:border-signal/50"
                  placeholder={label}
                />
              </div>
            ))}
          </div>
          <label className="mt-3 flex items-center gap-2 text-sm text-steel-300 cursor-pointer w-fit" data-testid="trip-field-signatures">
            <input
              type="checkbox"
              checked={includeSignatures}
              onChange={(e) => setIncludeSignatures(e.target.checked)}
              className="size-4 accent-signal"
            />
            Include customer &amp; staff signature blocks in the PDF
          </label>
        </div>

        <div className="flex items-center gap-3 flex-wrap border-t border-ink-700/60 pt-5">
          <button
            data-testid={T.tripAnalyze}
            onClick={analyze}
            disabled={!canAnalyze}
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
