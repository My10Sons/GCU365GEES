/*
 * Repository Traceability:
 * - Anonymous "Trip Inspection": guided exterior walkaround (Front/Rear/Left/Right/Roof) +
 *   optional Interior. Each selected area gets a Before/After pair; all are sent in ONE request
 *   and analyzed with the real Gemini engine. Reports damage with bounding-box markers, size
 *   estimate (cm), repair/replace recommendation, advisory repair cost, photo-quality &
 *   image-integrity checks, condition score, cleanliness, and walkaround coverage. Nothing is
 *   stored. Exports a branded, signable PDF in English / Arabic / bilingual.
 */
import React, { useCallback, useEffect, useRef, useState } from "react";
import { jsPDF } from "jspdf";
import html2canvas from "html2canvas";
import { CarFront, Loader2, ImagePlus, RotateCcw, ShieldCheck, AlertTriangle, CheckCircle2, Sparkles, Armchair, FileDown, Check, ScanEye, FolderPlus, ArrowRight, Zap } from "lucide-react";
import { Link } from "react-router-dom";
import { api, envelopeError } from "../lib/api";
import { T } from "../constants/testIds";

async function prepareImage(file) {
  const dataUrl = await new Promise((res, rej) => { const r = new FileReader(); r.onload = () => res(r.result); r.onerror = rej; r.readAsDataURL(file); });
  const img = await loadImage(dataUrl);
  const maxDim = 1600;
  let { width, height } = img;
  if (Math.max(width, height) > maxDim) { const s = maxDim / Math.max(width, height); width = Math.round(width * s); height = Math.round(height * s); }
  const canvas = document.createElement("canvas");
  canvas.width = width; canvas.height = height;
  canvas.getContext("2d").drawImage(img, 0, 0, width, height);
  const blob = await new Promise((res) => canvas.toBlob(res, "image/jpeg", 0.85));
  return { blob, preview: canvas.toDataURL("image/jpeg", 0.7) };
}
function loadImage(src) { return new Promise((res, rej) => { const i = new Image(); i.crossOrigin = "anonymous"; i.onload = () => res(i); i.onerror = rej; i.src = src; }); }

const ANGLES = [
  { key: "FRONT", en: "Front", ar: "الأمام" },
  { key: "REAR", en: "Rear", ar: "الخلف" },
  { key: "LEFT", en: "Left side", ar: "الجانب الأيسر" },
  { key: "RIGHT", en: "Right side", ar: "الجانب الأيمن" },
  { key: "ROOF", en: "Roof", ar: "السقف" },
];

const ALL_ANGLE_KEYS = ANGLES.map((a) => a.key);
const angleLabel = (k) => ANGLES.find((a) => a.key === k)?.en || k;

const CATEGORY_LABEL = {
  DENT: "Dents", SCRATCH: "Scratches", CHIP: "Chips", TIRE: "Tyres", WHEEL: "Wheels / rims",
  GLASS: "Glass", LIGHT: "Lights", PART: "Broken / missing parts", RUST: "Rust / corrosion",
  VANDALISM: "Vandalism / graffiti", DIRT: "Dirt / staining", LEAK: "Fluid leaks",
  SEAT: "Seats", DASHBOARD: "Dashboard / console", TRIM: "Trim / panels", STAIN: "Stains / dirt",
  MISSING: "Missing items", ELECTRONICS: "Screens / controls",
};
const CATEGORY_AR = {
  DENT: "انبعاجات", SCRATCH: "خدوش", CHIP: "رقائق دهان", TIRE: "إطارات", WHEEL: "جنوط",
  GLASS: "زجاج", LIGHT: "أضواء", PART: "أجزاء مكسورة/مفقودة", RUST: "صدأ", VANDALISM: "تخريب",
  DIRT: "اتساخ", LEAK: "تسرب سوائل", SEAT: "مقاعد", DASHBOARD: "لوحة القيادة", TRIM: "كسوة داخلية",
  STAIN: "بقع", MISSING: "عناصر مفقودة", ELECTRONICS: "شاشات/أزرار",
};
const STATUS_TEXT = { NEW: "New (this trip)", PRE_EXISTING: "Pre-existing", RESOLVED: "Resolved", UNCERTAIN: "Uncertain" };
const CLEANLINESS_LABEL = { CLEAN: "Clean", LIGHT_DIRT: "Light dirt", DIRTY: "Dirty", VERY_DIRTY: "Very dirty" };
const REC_LABEL = { REPAIR: "Repair", REPLACE: "Replace", ASSESS: "Assess" };

const fmtCost = (c) => (c && (c.low || c.high) ? `${c.currency} ${Number(c.low).toLocaleString()}–${Number(c.high).toLocaleString()}` : null);
const fmtSize = (cm) => (cm != null ? `~${cm} cm` : null);
const scoreColor = (s) => (s == null ? "text-steel-400" : s >= 80 ? "text-emerald400" : s >= 50 ? "text-amber400" : "text-signal-soft");

function WarningPanel({ testId, title, items }) {
  if (!items || items.length === 0) return null;
  return (
    <div data-testid={testId} className="rounded-md border border-amber400/40 bg-amber400/10 px-3 py-2.5 flex items-start gap-2">
      <AlertTriangle className="size-4 text-amber400 mt-0.5 shrink-0" />
      <div className="text-xs text-amber400">
        <span className="font-semibold">{title}</span>
        <ul className="list-disc ml-4 mt-1 space-y-0.5 text-amber400/90">{items.slice(0, 6).map((p, i) => <li key={i}>{p}</li>)}</ul>
      </div>
    </div>
  );
}

function ScopeChip({ label, active, onClick, testId }) {
  return (
    <button type="button" data-testid={testId} aria-pressed={active} onClick={onClick}
      className={`flex items-center gap-2 px-3.5 py-2 rounded-full border text-sm transition-colors ${active ? "border-signal/50 bg-signal/10 text-white" : "border-ink-700 bg-ink-900/60 text-steel-400 hover:text-steel-200 hover:border-ink-600"}`}>
      <span className={`size-4 grid place-items-center rounded-full border ${active ? "bg-signal border-signal" : "border-ink-600"}`}>{active && <Check className="size-3 text-white" />}</span>
      {label}
    </button>
  );
}

function DropZone({ label, slot, state, onPick, testId }) {
  const ref = useRef(null);
  return (
    <div className="flex-1 min-w-0">
      <div className="text-[11px] uppercase tracking-wider text-steel-400 mb-2">{label}</div>
      <button type="button" onClick={() => ref.current?.click()}
        className="w-full aspect-[4/3] rounded-lg border-2 border-dashed border-ink-700 hover:border-signal/50 bg-ink-900/60 overflow-hidden grid place-items-center transition-colors">
        {state?.preview ? <img src={state.preview} alt={label} className="w-full h-full object-contain bg-ink-950" />
          : <span className="flex flex-col items-center gap-2 text-steel-400 text-xs"><ImagePlus className="size-7" /> Click to add photo</span>}
      </button>
      <input ref={ref} data-testid={testId} type="file" accept="image/jpeg,image/png,image/webp" className="hidden"
        onChange={(e) => e.target.files?.[0] && onPick(slot, e.target.files[0])} />
    </div>
  );
}

async function composeAnnotated(previewUrl, items) {
  const img = await loadImage(previewUrl);
  const canvas = document.createElement("canvas");
  canvas.width = img.naturalWidth; canvas.height = img.naturalHeight;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(img, 0, 0);
  (items || []).forEach((it, i) => {
    if (!it.box) return;
    const x = it.box.x * canvas.width, y = it.box.y * canvas.height, w = it.box.w * canvas.width, h = it.box.h * canvas.height;
    const color = it.status === "NEW" ? "#ef4444" : "#f59e0b";
    ctx.lineWidth = Math.max(2, canvas.width * 0.004); ctx.strokeStyle = color; ctx.strokeRect(x, y, w, h);
    const r = Math.max(11, canvas.width * 0.014);
    ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fillStyle = color; ctx.fill();
    ctx.fillStyle = "#fff"; ctx.font = `bold ${Math.round(r * 1.15)}px sans-serif`; ctx.textAlign = "center"; ctx.textBaseline = "middle";
    ctx.fillText(String(i + 1), x, y);
  });
  return canvas.toDataURL("image/jpeg", 0.85);
}

function StatusBadge({ status }) {
  const cls = status === "NEW" ? "bg-signal/15 text-signal-soft border-signal/40"
    : status === "PRE_EXISTING" ? "bg-ink-800 text-steel-300 border-ink-600"
    : status === "RESOLVED" ? "bg-emerald-400/10 text-emerald400 border-emerald400/40"
    : "bg-amber400/15 text-amber400 border-amber400/40";
  return <span className={`text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded border ${cls}`}>{STATUS_TEXT[status]}</span>;
}

function SectionResult({ section, afterPreview }) {
  const items = section.items || [];
  const ig = section.integrity || {};
  const photoProbs = [...((section.photoCheck || {}).issues || [])];
  if (section.photoCheck && !section.photoCheck.beforeUsable) photoProbs.push("Before photo may be unusable");
  if (section.photoCheck && !section.photoCheck.afterUsable) photoProbs.push("After photo may be unusable");
  if (section.photoCheck && !section.photoCheck.sameVehicle) photoProbs.push(section.photoCheck.vehicleMismatchReason || "Before/After may be different vehicles");
  const igProbs = [...(ig.signals || [])];
  if (ig.beforeSuspicious) igProbs.push("Before photo shows possible manipulation");
  if (ig.afterSuspicious) igProbs.push("After photo shows possible manipulation");
  if (ig.aiGeneratedLikelihood && ig.aiGeneratedLikelihood !== "LOW") igProbs.push(`AI-generated likelihood: ${ig.aiGeneratedLikelihood}`);

  return (
    <div className="rounded-lg border border-ink-700/70 bg-ink-900/60 overflow-hidden" data-testid={`trip-section-${section.kind?.toLowerCase()}`}>
      <div className="px-4 py-3 border-b border-ink-700/60 flex items-center gap-2">
        <ScanEye className="size-4 text-steel-300" />
        <span className="text-sm font-semibold text-white">{section.label}</span>
        {!section.comparable && <span className="text-[10px] uppercase tracking-wider text-amber400 ml-auto">Not comparable</span>}
      </div>
      <div className="p-4 space-y-4">
        {section.summary && <p className="text-sm text-steel-300">{section.summary}</p>}
        <WarningPanel testId="trip-photo-warning" title="Photo check — results may be less reliable:" items={photoProbs} />
        <WarningPanel testId="trip-integrity-warning" title="Integrity check — possible image manipulation:" items={igProbs} />

        <div className="flex flex-wrap gap-2">
          {section.conditionScore != null && <span className="text-[11px] rounded-full border border-ink-700 bg-ink-800/70 px-2.5 py-1 text-steel-300">Condition: <span className={`font-semibold ${scoreColor(section.conditionScore)}`}>{section.conditionScore}/100</span></span>}
          {section.cleanliness && <span className="text-[11px] rounded-full border border-ink-700 bg-ink-800/70 px-2.5 py-1 text-steel-300">Cleanliness: <span className="text-white font-semibold">{CLEANLINESS_LABEL[section.cleanliness]}</span></span>}
          {fmtCost(section.estimatedCost) && <span className="text-[11px] rounded-full border border-signal/30 bg-signal/10 px-2.5 py-1 text-signal-soft">Est. repair: <span className="font-semibold">{fmtCost(section.estimatedCost)}</span></span>}
        </div>

        {afterPreview && (
          <div className="rounded-md border border-ink-700/70 bg-ink-950/40 p-2">
            <div className="text-[11px] uppercase tracking-wider text-steel-400 mb-2 px-1">{section.label} after — detected issues marked</div>
            <div className="relative inline-block max-w-full">
              <img src={afterPreview} alt={`${section.label} after, annotated`} className="block max-w-full rounded-md" />
              {items.map((it, i) => it.box ? (
                <div key={i} className={`absolute border-2 rounded-sm ${it.status === "NEW" ? "border-signal" : "border-amber400"}`}
                  style={{ left: `${it.box.x * 100}%`, top: `${it.box.y * 100}%`, width: `${it.box.w * 100}%`, height: `${it.box.h * 100}%` }}>
                  <span className={`absolute -top-2 -left-2 size-5 grid place-items-center rounded-full text-[10px] font-bold text-white ${it.status === "NEW" ? "bg-signal" : "bg-amber400"}`}>{i + 1}</span>
                </div>
              ) : null)}
            </div>
          </div>
        )}

        <div className="rounded-md border border-ink-700/70 overflow-hidden">
          <div className="px-4 py-2 text-[11px] uppercase tracking-wider text-steel-400 bg-ink-900 border-b border-ink-700/60">Findings ({items.length})</div>
          {items.length === 0 ? <div className="px-4 py-6 text-center text-steel-400 text-sm">No issues found.</div> : (
            <ul className="divide-y divide-ink-700/60">
              {items.map((it, i) => (
                <li key={i} className="px-4 py-3 flex items-start gap-3">
                  <span className={`size-5 mt-0.5 shrink-0 grid place-items-center rounded-full text-[10px] font-bold text-white ${it.status === "NEW" ? "bg-signal" : it.box ? "bg-amber400" : "bg-ink-600"}`}>{i + 1}</span>
                  <span className="text-[11px] font-mono text-steel-300 w-24 shrink-0 mt-0.5">{CATEGORY_LABEL[it.category] || it.category}</span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <StatusBadge status={it.status} />
                      {it.severity && <span className="text-[10px] uppercase tracking-wider text-steel-400">{it.severity}</span>}
                      {it.recommendation && <span className="text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded border border-steel-500/40 text-steel-200">{REC_LABEL[it.recommendation]}</span>}
                      {fmtSize(it.sizeCm) && <span className="text-[10px] font-mono text-steel-400">{fmtSize(it.sizeCm)}</span>}
                      <span className="text-[11px] font-mono text-steel-400">{(it.confidence * 100).toFixed(0)}%</span>
                      {fmtCost(it.estimatedCost) && <span className="text-[10px] font-mono text-signal-soft ml-auto">~{fmtCost(it.estimatedCost)}</span>}
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

const EMPTY = { blob: null, preview: null };

export default function TripInspection() {
  const [angles, setAngles] = useState(() => ({ FRONT: { before: EMPTY, after: EMPTY } }));
  const [selectedAngles, setSelectedAngles] = useState(["FRONT"]);
  const [interiorOn, setInteriorOn] = useState(false);
  const [requireFull, setRequireFull] = useState(false);
  const [policyEnforced, setPolicyEnforced] = useState(false);
  const [intBefore, setIntBefore] = useState(EMPTY);
  const [intAfter, setIntAfter] = useState(EMPTY);
  const [reportFields, setReportFields] = useState({ customerName: "", vehiclePlate: "", vehicleModel: "", rentalId: "", inspectorName: "" });
  const [includeSignatures, setIncludeSignatures] = useState(true);
  const [pdfLang, setPdfLang] = useState("en");
  const [mode, setMode] = useState("fast");
  const [streaming, setStreaming] = useState(false);
  const [pending, setPending] = useState([]);
  const [busy, setBusy] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [stage, setStage] = useState("");
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const clear = () => { setResult(null); setError(""); };

  const enforceFullSelection = () => {
    setSelectedAngles(ALL_ANGLE_KEYS);
    setAngles((a) => { const n = { ...a }; ALL_ANGLE_KEYS.forEach((k) => { if (!n[k]) n[k] = { before: EMPTY, after: EMPTY }; }); return n; });
  };

  useEffect(() => {
    let active = true;
    api.get("/tenant/policy").then(({ data }) => {
      if (!active) return;
      const enforced = !!data?.data?.requireFullWalkaround;
      setPolicyEnforced(enforced);
      if (enforced) { setRequireFull(true); enforceFullSelection(); }
    }).catch(() => { /* default: no policy */ });
    return () => { active = false; };
  }, []);

  const toggleAngle = (key) => {
    clear();
    setSelectedAngles((cur) => {
      if (cur.includes(key)) { setAngles((a) => { const n = { ...a }; delete n[key]; return n; }); return cur.filter((k) => k !== key); }
      setAngles((a) => ({ ...a, [key]: { before: EMPTY, after: EMPTY } }));
      return [...cur, key];
    });
  };
  const toggleInterior = () => { clear(); setInteriorOn((v) => { if (v) { setIntBefore(EMPTY); setIntAfter(EMPTY); } return !v; }); };
  const toggleRequireFull = (e) => {
    const on = e.target.checked; setRequireFull(on); clear();
    if (on) {
      setSelectedAngles(ALL_ANGLE_KEYS);
      setAngles((a) => { const n = { ...a }; ALL_ANGLE_KEYS.forEach((k) => { if (!n[k]) n[k] = { before: EMPTY, after: EMPTY }; }); return n; });
    }
  };

  const pickAngle = useCallback(async (key, slot, file) => {
    clear();
    try { const p = await prepareImage(file); setAngles((a) => ({ ...a, [key]: { ...(a[key] || {}), [slot]: p } })); }
    catch { setError("Could not read that image. Please try a different photo."); }
  }, []);
  const pickInterior = useCallback(async (slot, file) => {
    clear();
    try { const p = await prepareImage(file); (slot === "before" ? setIntBefore : setIntAfter)(p); }
    catch { setError("Could not read that image. Please try a different photo."); }
  }, []);

  const reset = () => { setAngles({ FRONT: { before: EMPTY, after: EMPTY } }); setSelectedAngles(["FRONT"]); setInteriorOn(false); setIntBefore(EMPTY); setIntAfter(EMPTY); clear(); setStage(""); };

  const angleComplete = (k) => angles[k]?.before?.blob && angles[k]?.after?.blob;
  const intComplete = intBefore.blob && intAfter.blob;
  const incompleteAngles = selectedAngles.filter((k) => !angleComplete(k));
  const intIncomplete = interiorOn && !intComplete;
  const anyComplete = selectedAngles.some(angleComplete) || (interiorOn && intComplete);
  const anySelected = selectedAngles.length > 0 || interiorOn;
  const missingForFull = ALL_ANGLE_KEYS.filter((k) => !angleComplete(k));
  const isFullWalkaround = missingForFull.length === 0;
  const capturedExtCount = ALL_ANGLE_KEYS.filter(angleComplete).length;
  const canAnalyze = !busy && anySelected && incompleteAngles.length === 0 && !intIncomplete && anyComplete && (!requireFull || isFullWalkaround);

  const analyze = async () => {
    setBusy(true); setError(""); setResult(null);
    const jobs = [];
    selectedAngles.forEach((k) => {
      if (angleComplete(k)) jobs.push({
        kind: "EXTERIOR", angle: k, label: `Exterior — ${ANGLES.find((x) => x.key === k)?.en || k}`,
        before: angles[k].before.blob, after: angles[k].after.blob,
      });
    });
    if (interiorOn && intComplete) jobs.push({ kind: "INTERIOR", angle: null, label: "Interior", before: intBefore.blob, after: intAfter.blob });

    setStreaming(true);
    setPending(jobs.map((j) => ({ label: j.label, kind: j.kind, angle: j.angle })));
    setResult({ sections: [], overall: "PENDING", mode, coverage: {}, isAdvisory: true });
    const collected = [];
    try {
      // Analyze each area in parallel; render each section the moment it returns.
      await Promise.all(jobs.map(async (j) => {
        try {
          const fd = new FormData();
          fd.append("kind", j.kind);
          if (j.angle) fd.append("angle", j.angle);
          fd.append("mode", mode);
          fd.append("before", j.before, "before.jpg");
          fd.append("after", j.after, "after.jpg");
          const { data } = await api.post("/trip-inspection/analyze-section", fd, { headers: { "Content-Type": "multipart/form-data" }, timeout: 300000 });
          collected.push(data.data);
          setResult((prev) => ({ ...prev, sections: [...(prev?.sections || []), data.data] }));
        } catch (e) {
          collected.push(null);
        } finally {
          setPending((prev) => prev.filter((p) => p.label !== j.label));
        }
      }));

      const good = collected.filter(Boolean);
      if (good.length === 0) { setError("Analysis failed. Please retry."); setResult(null); return; }
      // Aggregate + auto-case routing once over the whole set.
      const { data } = await api.post("/trip-inspection/finalize", { sections: good, reportFields, mode }, { timeout: 60000 });
      setResult(data.data);
    } catch (err) { setError(envelopeError(err, "Analysis failed. Please retry.")); }
    finally { setBusy(false); setStreaming(false); setPending([]); setStage(""); }
  };

  const afterPreviewFor = (s) => (s.kind === "INTERIOR" ? intAfter.preview : angles[s.angle]?.after?.preview);
  const beforePreviewFor = (s) => (s.kind === "INTERIOR" ? intBefore.preview : angles[s.angle]?.before?.preview);

  const tt = (o, lang) => (lang === "bilingual" ? `${o.en} / ${o.ar}` : o[lang] || o.en);
  const catL = (cat, lang) => (lang === "ar" ? (CATEGORY_AR[cat] || cat) : lang === "bilingual" ? `${CATEGORY_LABEL[cat] || cat} / ${CATEGORY_AR[cat] || cat}` : (CATEGORY_LABEL[cat] || cat));

  const buildReportHtml = (lang, annotated, befores) => {
    const L = {
      title: { en: "Trip Inspection Report", ar: "تقرير فحص الرحلة" },
      advisory: { en: "Advisory AI result. Final liability, charges, and repair decisions are not made here.", ar: "نتيجة استرشادية. لا تُتخذ هنا قرارات المسؤولية أو الرسوم أو الإصلاح." },
      customer: { en: "Customer", ar: "العميل" }, plate: { en: "Vehicle plate", ar: "لوحة المركبة" }, model: { en: "Make / model", ar: "الصنع / الطراز" },
      rentalId: { en: "Rental ID", ar: "رقم الإيجار" }, inspector: { en: "Inspector", ar: "الفاحص" },
      condition: { en: "Overall condition", ar: "الحالة العامة" }, clean: { en: "Cleanliness", ar: "النظافة" }, estCost: { en: "Estimated new-damage repair", ar: "تكلفة الإصلاح المقدّرة" },
      coverage: { en: "Walkaround coverage", ar: "تغطية الفحص" }, before: { en: "Before", ar: "قبل" }, after: { en: "After (issues marked)", ar: "بعد (محددة)" },
      fullWalk: { en: "Full 5-angle walkaround", ar: "فحص محيطي كامل (٥ زوايا)" }, partialWalk: { en: "Incomplete walkaround", ar: "فحص محيطي غير مكتمل" },
      findings: { en: "Findings", ar: "النتائج" }, noIssues: { en: "No issues found.", ar: "لا توجد مشاكل." },
      photoW: { en: "Photo check — results may be less reliable", ar: "فحص الصور — قد تقل الدقة" }, igW: { en: "Integrity check — possible image manipulation", ar: "فحص الأصالة — احتمال تلاعب" },
      custSig: { en: "Customer signature", ar: "توقيع العميل" }, staffSig: { en: "Staff signature", ar: "توقيع الموظف" }, date: { en: "Date", ar: "التاريخ" },
      cat: { en: "Item", ar: "العنصر" }, status: { en: "Status", ar: "الحالة" }, action: { en: "Action", ar: "الإجراء" }, size: { en: "Size", ar: "الحجم" }, cost: { en: "Est. cost", ar: "التكلفة" }, loc: { en: "Location / note", ar: "الموقع / ملاحظة" },
    };
    const CLEAN = { CLEAN: { en: "Clean", ar: "نظيف" }, LIGHT_DIRT: { en: "Light dirt", ar: "اتساخ خفيف" }, DIRTY: { en: "Dirty", ar: "متسخ" }, VERY_DIRTY: { en: "Very dirty", ar: "متسخ جداً" } };
    const REC = { REPAIR: { en: "Repair", ar: "إصلاح" }, REPLACE: { en: "Replace", ar: "استبدال" }, ASSESS: { en: "Assess", ar: "تقييم" } };
    const STAT = { NEW: { en: "New", ar: "جديد" }, PRE_EXISTING: { en: "Pre-existing", ar: "موجود مسبقاً" }, RESOLVED: { en: "Resolved", ar: "أُصلح" }, UNCERTAIN: { en: "Uncertain", ar: "غير مؤكد" } };
    const verdictMap = { NEW_DAMAGE_FOUND: { en: "New damage detected this trip", ar: "تم اكتشاف أضرار جديدة" }, NO_NEW_DAMAGE: { en: "No new damage detected", ar: "لا توجد أضرار جديدة" }, NOT_COMPARABLE: { en: "Could not compare the photos", ar: "تعذّرت المقارنة" } };
    const rtl = lang === "ar";
    const b = result.branding || {};
    const f = reportFields;
    const refs = [];
    if (f.customerName) refs.push([tt(L.customer, lang), f.customerName]);
    if (f.vehiclePlate) refs.push([tt(L.plate, lang), f.vehiclePlate]);
    if (f.vehicleModel) refs.push([tt(L.model, lang), f.vehicleModel]);
    if (f.rentalId) refs.push([tt(L.rentalId, lang), f.rentalId]);
    if (f.inspectorName) refs.push([tt(L.inspector, lang), f.inspectorName]);
    const verdict = tt(verdictMap[result.overall] || verdictMap.NOT_COMPARABLE, lang);
    const verdictColor = result.overall === "NEW_DAMAGE_FOUND" ? "#c62828" : result.overall === "NO_NEW_DAMAGE" ? "#1b7d3f" : "#b26a00";
    const cs = fmtCost(result.costSummary);
    const metrics = [];
    if (result.conditionScore != null) metrics.push(`${tt(L.condition, lang)}: ${result.conditionScore}/100`);
    if (result.cleanliness) metrics.push(`${tt(L.clean, lang)}: ${tt(CLEAN[result.cleanliness] || { en: result.cleanliness, ar: result.cleanliness }, lang)}`);
    if (cs) metrics.push(`${tt(L.estCost, lang)}: ${cs}`);
    const cov = result.coverage || {};
    const covLine = `${tt(L.coverage, lang)}: ${cov.capturedCount || 0}/${cov.totalAngles || 5}${cov.interiorCaptured ? " + Interior" : ""}`;
    const walkBadge = cov.fullWalkaround
      ? `<span style="display:inline-block;margin-top:6px;padding:3px 10px;border-radius:12px;font-size:10px;font-weight:bold;background:#e6f4ea;color:#1b7d3f;border:1px solid #1b7d3f;">✓ ${tt(L.fullWalk, lang)}</span>`
      : `<span style="display:inline-block;margin-top:6px;padding:3px 10px;border-radius:12px;font-size:10px;font-weight:bold;background:#fff4e5;color:#b26a00;border:1px solid #b26a00;">${tt(L.partialWalk, lang)} (${cov.capturedCount || 0}/${cov.totalAngles || 5})</span>`;

    const esc = (s) => String(s == null ? "" : s).replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));

    let sectionsHtml = "";
    for (const s of result.sections || []) {
      const ann = annotated[s.label];
      const bef = befores[s.label];
      const rows = (s.items || []).map((it, i) => `
        <tr>
          <td style="padding:5px 6px;border-bottom:1px solid #eee;text-align:center;">${i + 1}</td>
          <td style="padding:5px 6px;border-bottom:1px solid #eee;">${esc(catL(it.category, lang))}</td>
          <td style="padding:5px 6px;border-bottom:1px solid #eee;">${esc(tt(STAT[it.status] || { en: it.status, ar: it.status }, lang))}${it.severity ? " · " + esc(it.severity) : ""}</td>
          <td style="padding:5px 6px;border-bottom:1px solid #eee;">${it.recommendation ? esc(tt(REC[it.recommendation], lang)) : "—"}</td>
          <td style="padding:5px 6px;border-bottom:1px solid #eee;">${it.sizeCm != null ? "~" + it.sizeCm + " cm" : "—"}</td>
          <td style="padding:5px 6px;border-bottom:1px solid #eee;">${fmtCost(it.estimatedCost) || "—"}</td>
          <td style="padding:5px 6px;border-bottom:1px solid #eee;">${esc(it.location || "—")}${it.detail ? " — " + esc(it.detail) : ""}</td>
        </tr>`).join("");
      sectionsHtml += `
      <div style="margin-top:18px;page-break-inside:avoid;">
        <div style="font-size:15px;font-weight:bold;color:#111;margin-bottom:6px;">${esc(s.label)}${s.comparable ? "" : " (not comparable)"}</div>
        ${s.summary ? `<div style="font-size:11px;color:#444;margin-bottom:8px;">${esc(s.summary)}</div>` : ""}
        <div style="display:flex;gap:10px;">
          <div style="flex:1;"><div style="font-size:9px;color:#666;margin-bottom:3px;">${tt(L.before, lang)}</div>${bef ? `<img src="${bef}" style="width:100%;border:1px solid #ddd;border-radius:4px;"/>` : ""}</div>
          <div style="flex:1;"><div style="font-size:9px;color:#666;margin-bottom:3px;">${tt(L.after, lang)}</div>${ann ? `<img src="${ann}" style="width:100%;border:1px solid #ddd;border-radius:4px;"/>` : ""}</div>
        </div>
        <div style="font-size:10px;color:#333;font-weight:bold;margin:10px 0 4px;">${tt(L.findings, lang)} (${(s.items || []).length})</div>
        ${(s.items || []).length === 0 ? `<div style="font-size:10px;color:#888;">${tt(L.noIssues, lang)}</div>` : `
        <table style="width:100%;border-collapse:collapse;font-size:9.5px;color:#222;${rtl ? "direction:rtl;" : ""}">
          <thead><tr style="background:#f3f3f3;">
            <th style="padding:5px 6px;text-align:${rtl ? "right" : "left"};">#</th>
            <th style="padding:5px 6px;text-align:${rtl ? "right" : "left"};">${tt(L.cat, lang)}</th>
            <th style="padding:5px 6px;text-align:${rtl ? "right" : "left"};">${tt(L.status, lang)}</th>
            <th style="padding:5px 6px;text-align:${rtl ? "right" : "left"};">${tt(L.action, lang)}</th>
            <th style="padding:5px 6px;text-align:${rtl ? "right" : "left"};">${tt(L.size, lang)}</th>
            <th style="padding:5px 6px;text-align:${rtl ? "right" : "left"};">${tt(L.cost, lang)}</th>
            <th style="padding:5px 6px;text-align:${rtl ? "right" : "left"};">${tt(L.loc, lang)}</th>
          </tr></thead><tbody>${rows}</tbody>
        </table>`}
      </div>`;
    }

    const refsHtml = refs.length ? `<div style="display:flex;flex-wrap:wrap;gap:4px 24px;margin-top:10px;font-size:10px;">${refs.map(([k, v]) => `<div><span style="color:#777;font-weight:bold;">${esc(k)}:</span> <span style="color:#222;">${esc(v)}</span></div>`).join("")}</div>` : "";
    const sigHtml = includeSignatures ? `
      <div style="display:flex;gap:40px;margin-top:34px;">
        <div style="flex:1;"><div style="border-top:1px solid #999;padding-top:4px;font-size:10px;color:#555;">${tt(L.custSig, lang)}</div><div style="font-size:9px;color:#888;margin-top:8px;">${tt(L.date, lang)}: ____________</div></div>
        <div style="flex:1;"><div style="border-top:1px solid #999;padding-top:4px;font-size:10px;color:#555;">${tt(L.staffSig, lang)}</div><div style="font-size:9px;color:#888;margin-top:8px;">${tt(L.date, lang)}: ____________</div></div>
      </div>` : "";

    return `
      <div style="padding:30px;font-family:${rtl ? "'Amiri','Helvetica',sans-serif" : "'Helvetica','Arial',sans-serif"};color:#222;${rtl ? "direction:rtl;text-align:right;" : ""}">
        <div style="display:flex;align-items:center;gap:14px;border-bottom:2px solid #e0e0e0;padding-bottom:12px;">
          ${b.logoDataUrl ? `<img src="${b.logoDataUrl}" style="height:54px;width:auto;"/>` : ""}
          <div>${b.companyName ? `<div style="font-size:17px;font-weight:bold;color:#111;">${esc(b.companyName)}</div>` : ""}${b.branchName ? `<div style="font-size:11px;color:#777;">${esc(b.branchName)}</div>` : ""}</div>
        </div>
        <div style="font-size:20px;font-weight:bold;color:#111;margin-top:14px;">${tt(L.title, lang)}</div>
        <div style="font-size:9px;color:#999;margin-top:2px;">${new Date().toLocaleString()} · ${esc(result.modelVersion)}</div>
        <div style="font-size:8px;color:#aaa;margin-top:2px;">${tt(L.advisory, lang)}</div>
        ${refsHtml}
        <div style="font-size:15px;font-weight:bold;color:${verdictColor};margin-top:14px;">${verdict}</div>
        ${metrics.length ? `<div style="font-size:11px;color:#222;font-weight:bold;margin-top:4px;">${metrics.join("&nbsp;&nbsp;·&nbsp;&nbsp;")}</div>` : ""}
        <div style="font-size:10px;color:#555;margin-top:3px;">${covLine}</div>
        <div>${walkBadge}</div>
        ${sectionsHtml}
        ${sigHtml}
      </div>`;
  };

  const exportPdf = async () => {
    if (!result) return;
    setExporting(true);
    try {
      const lang = pdfLang;
      if (lang !== "en") { try { await document.fonts.load("16px Amiri"); await document.fonts.load("bold 16px Amiri"); await document.fonts.ready; } catch { /* fallback */ } }
      const annotated = {}; const befores = {};
      for (const s of result.sections || []) {
        const ap = afterPreviewFor(s);
        annotated[s.label] = ap ? await composeAnnotated(ap, s.items) : null;
        befores[s.label] = beforePreviewFor(s) || null;
      }
      const container = document.createElement("div");
      container.style.cssText = "position:fixed;left:-99999px;top:0;width:794px;background:#ffffff;z-index:-1;";
      container.innerHTML = buildReportHtml(lang, annotated, befores);
      document.body.appendChild(container);
      await new Promise((r) => setTimeout(r, 350));
      const canvas = await html2canvas(container, { scale: 2, backgroundColor: "#ffffff", useCORS: true, logging: false });
      document.body.removeChild(container);
      const pdf = new jsPDF("p", "pt", "a4");
      const pageW = pdf.internal.pageSize.getWidth();
      const pageH = pdf.internal.pageSize.getHeight();
      const imgW = pageW;
      const imgH = (canvas.height * imgW) / canvas.width;
      const img = canvas.toDataURL("image/jpeg", 0.9);
      let position = 0; let heightLeft = imgH;
      pdf.addImage(img, "JPEG", 0, position, imgW, imgH);
      heightLeft -= pageH;
      while (heightLeft > 0) { position -= pageH; pdf.addPage(); pdf.addImage(img, "JPEG", 0, position, imgW, imgH); heightLeft -= pageH; }
      pdf.save(`trip-inspection-report-${Date.now()}.pdf`);
    } catch (e) { console.error("PDF export failed", e); setError("Could not generate the PDF. Please try again."); }
    finally { setExporting(false); }
  };

  const overallCard = () => {
    if (!result) return null;
    const map = {
      NEW_DAMAGE_FOUND: { cls: "bg-signal/10 border-signal/40 text-signal-soft", icon: AlertTriangle, title: "New damage detected this trip" },
      NO_NEW_DAMAGE: { cls: "bg-emerald-400/10 border-emerald400/40 text-emerald400", icon: CheckCircle2, title: "No new damage detected" },
      NOT_COMPARABLE: { cls: "bg-amber400/10 border-amber400/40 text-amber400", icon: AlertTriangle, title: "Could not compare the photos" },
    };
    const o = map[result.overall] || map.NOT_COMPARABLE; const Icon = o.icon; const cov = result.coverage || {};
    return (
      <div className={`rounded-lg border p-5 flex items-start gap-3 ${o.cls}`}>
        <Icon className="size-6 mt-0.5 shrink-0" />
        <div className="flex-1">
          <div className="text-base font-semibold">{o.title}</div>
          {result.newIssueCount > 0 && <p className="text-sm text-steel-300 mt-1">{result.newIssueCount} new issue{result.newIssueCount > 1 ? "s" : ""} found across the inspected areas.</p>}
          <div className="flex flex-wrap gap-x-4 gap-y-1 mt-2 text-xs">
            {result.conditionScore != null && <span className="text-steel-300">Condition <span className={`font-semibold ${scoreColor(result.conditionScore)}`}>{result.conditionScore}/100</span></span>}
            {result.cleanliness && <span className="text-steel-300">Cleanliness <span className="text-white font-semibold">{CLEANLINESS_LABEL[result.cleanliness]}</span></span>}
            {fmtCost(result.costSummary) && <span className="text-steel-300" data-testid="trip-cost-summary">Est. new-damage repair <span className="text-signal-soft font-semibold">{fmtCost(result.costSummary)}</span></span>}
            <span className="text-steel-300" data-testid="trip-coverage">Coverage <span className="text-white font-semibold">{cov.capturedCount || 0}/{cov.totalAngles || 5}{cov.interiorCaptured ? " + Interior" : ""}</span></span>
            <span data-testid="trip-walkaround-badge" className={`text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full border ${cov.fullWalkaround ? "border-emerald400/50 bg-emerald-400/10 text-emerald400" : "border-amber400/50 bg-amber400/10 text-amber400"}`}>
              {cov.fullWalkaround ? "✓ Full 5-angle walkaround" : `Partial walkaround ${cov.capturedCount || 0}/5`}
            </span>
          </div>
          {result.hasPhotoWarnings && <p className="text-[11px] text-amber400 mt-1.5 flex items-center gap-1"><AlertTriangle className="size-3" /> Photo-quality / vehicle-match warnings — see sections below.</p>}
          {result.hasIntegrityWarnings && <p className="text-[11px] text-amber400 mt-1 flex items-center gap-1"><ScanEye className="size-3" /> Image-integrity warnings — see sections below.</p>}
        </div>
        <div className="shrink-0 flex items-center gap-2">
          <select data-testid={T.tripExportLang} value={pdfLang} onChange={(e) => setPdfLang(e.target.value)}
            className="rounded-md bg-ink-800 border border-ink-700 text-xs text-steel-100 px-2 py-2">
            <option value="en">EN</option><option value="ar">AR</option><option value="bilingual">EN+AR</option>
          </select>
          <button data-testid={T.tripExportPdf} onClick={exportPdf} disabled={exporting}
            className="px-3 py-2 rounded-md text-xs font-medium bg-ink-800 border border-ink-700 hover:bg-ink-700/80 text-steel-100 flex items-center gap-1.5 disabled:opacity-50">
            {exporting ? <Loader2 className="size-3.5 animate-spin" /> : <FileDown className="size-3.5" />}{exporting ? "Exporting…" : "Export PDF"}
          </button>
        </div>
      </div>
    );
  };

  return (
    <div data-testid={T.tripRoot} className="px-8 py-8 max-w-5xl">
      <div className="text-[11px] uppercase tracking-[0.22em] text-steel-400">Damage Intelligence</div>
      <h1 className="text-2xl font-semibold text-white mt-1 flex items-center gap-3"><CarFront className="size-6 text-steel-300" /> Trip Inspection</h1>
      <p className="text-sm text-steel-300 mt-2 max-w-2xl flex items-start gap-1.5">
        <ShieldCheck className="size-4 mt-0.5 text-emerald400" />
        Guided walkaround: pick the angles to inspect, add a before/after photo for each, then analyze. You get damage detection with size,
        repair/replace and cost estimates, photo-quality &amp; image-integrity checks, condition &amp; cleanliness scores, and a branded PDF
        (English / Arabic). Advisory only — nothing is stored.
      </p>


      <section className="mt-6 rounded-lg border border-ink-700/70 bg-ink-900/60 p-5 space-y-6">
        <div>
          <div className="text-[11px] uppercase tracking-wider text-steel-400 mb-2">Exterior walkaround — choose angles</div>
          <div className="flex gap-2.5 flex-wrap">
            {ANGLES.map((a) => <ScopeChip key={a.key} label={a.en} active={selectedAngles.includes(a.key)} onClick={() => toggleAngle(a.key)} testId={`trip-angle-${a.key.toLowerCase()}`} />)}
          </div>
          <div className="text-[11px] uppercase tracking-wider text-steel-400 mt-4 mb-2">Interior</div>
          <ScopeChip label="Interior" active={interiorOn} onClick={toggleInterior} testId={T.tripScopeInterior} />
          {!anySelected && <p className="text-xs text-amber400 mt-2">Select at least one area to inspect.</p>}
          <label className="mt-4 flex items-center gap-2 text-sm text-steel-300 cursor-pointer w-fit" data-testid="trip-require-full">
            <input type="checkbox" checked={requireFull} disabled={policyEnforced} onChange={toggleRequireFull} className="size-4 accent-signal disabled:opacity-60" />
            Require a full 5-angle walkaround (enforce before analysis)
            {policyEnforced && <span className="text-[10px] uppercase tracking-wider text-emerald400 border border-emerald400/40 rounded px-1.5 py-0.5">Branch policy</span>}
          </label>
          {requireFull && !isFullWalkaround && (
            <p className="text-xs text-amber400 mt-2" data-testid="trip-walkaround-gate">Full walkaround required — add both photos for: {missingForFull.map(angleLabel).join(", ")}.</p>
          )}
          {!requireFull && capturedExtCount > 0 && !isFullWalkaround && (
            <p className="text-xs text-amber400/90 mt-2" data-testid="trip-walkaround-advisory">Partial walkaround ({capturedExtCount}/5 exterior angles). For a complete handover record, capture all 5 angles. Missing: {missingForFull.map(angleLabel).join(", ")}.</p>
          )}
        </div>

        {selectedAngles.map((k) => {
          const a = ANGLES.find((x) => x.key === k);
          return (
            <div key={k} className="border-t border-ink-700/60 pt-5">
              <div className="text-sm font-medium text-white mb-3">Exterior — {a.en}</div>
              <div className="flex flex-col sm:flex-row gap-5">
                <DropZone label="Before the trip" slot="before" state={angles[k]?.before} onPick={(slot, file) => pickAngle(k, slot, file)} testId={`trip-${k.toLowerCase()}-before`} />
                <DropZone label="After the trip" slot="after" state={angles[k]?.after} onPick={(slot, file) => pickAngle(k, slot, file)} testId={`trip-${k.toLowerCase()}-after`} />
              </div>
              {!angleComplete(k) && <p className="text-xs text-amber400 mt-2">Add both a Before and After photo for {a.en} to include this angle.</p>}
            </div>
          );
        })}

        {interiorOn && (
          <div className="border-t border-ink-700/60 pt-5">
            <div className="flex items-center gap-2 mb-3"><Armchair className="size-4 text-steel-300" /><span className="text-sm font-medium text-white">Interior</span></div>
            <div className="flex flex-col sm:flex-row gap-5">
              <DropZone label="Before the trip" slot="before" state={intBefore} onPick={pickInterior} testId="trip-interior-before" />
              <DropZone label="After the trip" slot="after" state={intAfter} onPick={pickInterior} testId="trip-interior-after" />
            </div>
            {intIncomplete && <p className="text-xs text-amber400 mt-2">Add both a Before and After interior photo to include this area.</p>}
          </div>
        )}

        <div className="border-t border-ink-700/60 pt-5">
          <div className="flex items-center gap-2 mb-3"><FileDown className="size-4 text-steel-300" /><span className="text-sm font-medium text-white">Report details</span><span className="text-[11px] text-steel-500">optional — printed on the PDF</span></div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {[["customerName", "Customer name", "trip-field-customer"], ["vehiclePlate", "Vehicle plate", "trip-field-plate"], ["vehicleModel", "Make / model", "trip-field-model"], ["rentalId", "Rental ID", "trip-field-rental"], ["inspectorName", "Inspector name", "trip-field-inspector"]].map(([key, label, tid]) => (
              <div key={key}>
                <label className="text-[11px] uppercase tracking-wider text-steel-400">{label}</label>
                <input data-testid={tid} value={reportFields[key]} onChange={(e) => setReportFields((s) => ({ ...s, [key]: e.target.value }))}
                  className="mt-1 w-full rounded-md bg-ink-900/70 border border-ink-700 px-3 py-2 text-sm text-steel-100 placeholder:text-steel-500 focus:outline-none focus:border-signal/50" placeholder={label} />
              </div>
            ))}
          </div>
          <label className="mt-3 flex items-center gap-2 text-sm text-steel-300 cursor-pointer w-fit" data-testid="trip-field-signatures">
            <input type="checkbox" checked={includeSignatures} onChange={(e) => setIncludeSignatures(e.target.checked)} className="size-4 accent-signal" />
            Include customer &amp; staff signature blocks in the PDF
          </label>
        </div>

        <div className="flex items-center gap-3 flex-wrap border-t border-ink-700/60 pt-5">
          <div data-testid="trip-mode-toggle" className="inline-flex rounded-md border border-ink-700 overflow-hidden">
            <button type="button" data-testid="trip-mode-fast" onClick={() => { setMode("fast"); clear(); }} disabled={busy}
              className={`px-3 py-2 text-xs font-medium flex items-center gap-1.5 transition-colors disabled:opacity-50 ${mode === "fast" ? "bg-signal text-white" : "bg-ink-800 text-steel-300 hover:bg-ink-700/80"}`}>
              <Zap className="size-3.5" /> Fast
            </button>
            <button type="button" data-testid="trip-mode-thorough" onClick={() => { setMode("thorough"); clear(); }} disabled={busy}
              className={`px-3 py-2 text-xs font-medium flex items-center gap-1.5 transition-colors disabled:opacity-50 ${mode === "thorough" ? "bg-signal text-white" : "bg-ink-800 text-steel-300 hover:bg-ink-700/80"}`}>
              <ScanEye className="size-3.5" /> Thorough
            </button>
          </div>
          <span className="text-[11px] text-steel-400">{mode === "fast" ? "Faster results, lighter model." : "Slower, most accurate model."}</span>
          <button data-testid={T.tripAnalyze} onClick={analyze} disabled={!canAnalyze}
            className="px-4 py-2 rounded-md text-sm font-medium bg-signal hover:bg-signal/90 disabled:opacity-50 text-white flex items-center gap-2">
            {busy ? <Loader2 className="size-4 animate-spin" /> : <Sparkles className="size-4" />}{busy ? "Working…" : "Analyze"}
          </button>
          <button data-testid={T.tripReset} onClick={reset} disabled={busy}
            className="px-3 py-2 rounded-md text-xs text-steel-200 bg-ink-800 border border-ink-700 hover:bg-ink-700/80 disabled:opacity-50 flex items-center gap-1.5">
            <RotateCcw className="size-3.5" /> Reset
          </button>
          {stage && <span className="text-xs text-steel-400">{stage}</span>}
        </div>
        {error && <div data-testid={T.tripError} className="text-sm text-signal-soft bg-signal/10 border border-signal/30 rounded-md px-3 py-2">{error}</div>}
      </section>

      {result && (
        <section data-testid={T.tripResult} className="mt-6 space-y-4">
          {streaming && (
            <div data-testid="trip-streaming-banner" className="rounded-lg border border-ink-700 bg-ink-900/60 p-4 flex items-center gap-3">
              <Loader2 className="size-5 animate-spin text-signal-soft shrink-0" />
              <div className="text-sm text-steel-200">Analyzing areas as you wait…
                <span className="text-steel-400"> ({(result.sections || []).length} done{pending.length ? `, ${pending.length} in progress` : ""})</span>
              </div>
            </div>
          )}
          {!streaming && overallCard()}
          {!streaming && result.autoCase?.created && (
            <div data-testid="trip-autocase-banner" className="rounded-lg border border-signal/40 bg-signal/10 px-4 py-3 flex items-start gap-3">
              <FolderPlus className="size-5 mt-0.5 text-signal-soft shrink-0" />
              <div className="flex-1">
                <div className="text-sm font-semibold text-white">Damage case opened automatically</div>
                <p className="text-xs text-steel-300 mt-0.5">
                  High-value new damage{result.autoCase.severityCode ? ` (${result.autoCase.severityCode} severity)` : ""} was detected
                  {result.autoCase.costHigh ? ` — estimated repair up to ${result.autoCase.costHigh} ${result.autoCase.currency || ""}` : ""}.
                  A damage case with {result.autoCase.findings} linked finding{result.autoCase.findings > 1 ? "s" : ""} was created in the review queue.
                </p>
              </div>
              <Link data-testid="trip-autocase-link" to={`/cases/${result.autoCase.damageCaseId}`}
                className="shrink-0 px-3 py-1.5 rounded-md text-xs font-medium bg-signal hover:bg-signal/90 text-white flex items-center gap-1.5">
                View case <ArrowRight className="size-3.5" />
              </Link>
            </div>
          )}
          {(result.sections || []).map((s) => <SectionResult key={s.label} section={s} afterPreview={afterPreviewFor(s)} />)}
          {streaming && pending.map((p) => (
            <div key={p.label} data-testid={`trip-pending-${p.kind}-${(p.angle || "interior").toLowerCase()}`}
              className="rounded-lg border border-ink-700/60 bg-ink-900/40 p-4 flex items-center gap-3">
              <Loader2 className="size-4 animate-spin text-steel-400 shrink-0" />
              <span className="text-sm text-steel-300">{p.label} — analyzing…</span>
            </div>
          ))}
          {!streaming && <p className="text-[11px] text-steel-400">Advisory AI result ({result.modelVersion}). Final liability, customer charge, and repair decisions are not made here.</p>}
        </section>
      )}
    </div>
  );
}
