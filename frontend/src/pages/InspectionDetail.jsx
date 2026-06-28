/*
 * Repository Traceability:
 * - DI-SPRINT-01 (Inspection detail screen, status view, evidence access action,
 *   submission action), DI-0034 endpoints, DI-0014 (no public URLs).
 */
import React, { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  ArrowLeft, ImagePlus, Send, Ban, Eye, ShieldCheck, AlertTriangle, RefreshCcw, Loader2, Sparkles, Activity, GitCompare, History, ChevronDown, ChevronRight,
} from "lucide-react";
import { inspectionsApi, evidenceApi, envelopeError, absoluteUrl } from "../lib/inspections-api";
import { comparisonApi } from "../lib/sprint03-api";
import { api } from "../lib/api";
import { useAuth } from "../lib/auth-context";
import StatusBadge from "../components/inspection/StatusBadge";
import UploadImageModal from "../components/inspection/UploadImageModal";
import { T } from "../constants/testIds";

const TERMINAL = new Set(["SUBMITTED", "CANCELLED", "FAILED"]);

function fmt(d) {
  if (!d) return "—";
  try { return new Date(d).toLocaleString(); } catch { return d; }
}

export default function InspectionDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { has } = useAuth();
  const [session, setSession] = useState(null);
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [action, setAction] = useState({ busy: false, error: "" });
  const [openUpload, setOpenUpload] = useState(false);
  const [accessByEvidence, setAccessByEvidence] = useState({});

  const canUpload = has("di.images.upload");
  const canSubmit = has("di.inspections.submit");
  const canCancel = has("di.inspections.cancel");
  const canAccess = has("di.evidence.access");
  const canAi = has("di.ai.request");
  const canAiRead = has("di.ai.read");
  const canCompare = has("di.comparison.request");
  const canCompareRead = has("di.comparison.read");

  const [aiBusy, setAiBusy] = useState(false);
  const [aiFindings, setAiFindings] = useState([]);
  const [aiSummary, setAiSummary] = useState(null);
  const [aiError, setAiError] = useState("");

  const [cmpBusy, setCmpBusy] = useState(false);
  const [cmpError, setCmpError] = useState("");
  const [comparison, setComparison] = useState(null);
  const [strip, setStrip] = useState([]);
  const [stripOpen, setStripOpen] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [s, imgs] = await Promise.all([
        inspectionsApi.get(id),
        inspectionsApi.listImages(id),
      ]);
      setSession(s);
      setImages(imgs.items || []);
      if (canAiRead) {
        try {
          const f = await api.get(`/inspection-sessions/${id}/ai-findings`);
          setAiFindings(f.data.data.items || []);
        } catch { /* swallow */ }
      }
      if (canCompareRead) {
        try {
          const cl = await comparisonApi.list(id);
          if (cl.items && cl.items.length > 0) {
            const latest = await comparisonApi.get(cl.items[0].comparisonId);
            setComparison(latest);
          }
        } catch { /* swallow */ }
      }
      try {
        const st = await comparisonApi.perVehicleStrip(id, 12);
        setStrip(st.items || []);
      } catch { /* swallow */ }
    } catch (err) {
      setError(envelopeError(err, "Could not load inspection."));
    } finally {
      setLoading(false);
    }
  }, [id, canAiRead, canCompareRead]);

  const runComparison = async () => {
    setCmpBusy(true);
    setCmpError("");
    try {
      const r = await comparisonApi.request(id, {});
      setComparison(r);
    } catch (err) {
      setCmpError(envelopeError(err, "Comparison failed."));
    } finally {
      setCmpBusy(false);
    }
  };

  const runAi = async () => {
    setAiBusy(true);
    setAiError("");
    setAiSummary(null);
    try {
      const r = await api.post(`/inspection-sessions/${id}/ai-analysis`);
      setAiSummary(r.data.data);
      const f = await api.get(`/inspection-sessions/${id}/ai-findings`);
      setAiFindings(f.data.data.items || []);
    } catch (err) {
      setAiError(envelopeError(err, "AI analysis failed."));
    } finally {
      setAiBusy(false);
    }
  };

  const runQualityCheck = async () => {
    setAiBusy(true);
    setAiError("");
    try {
      const r = await api.post(`/inspection-sessions/${id}/quality-check`);
      setAiSummary({ ...r.data.data, kind: "quality" });
      await load();
    } catch (err) {
      setAiError(envelopeError(err, "Quality check failed."));
    } finally {
      setAiBusy(false);
    }
  };

  useEffect(() => { load(); }, [load]);

  const isTerminal = session && TERMINAL.has(session.status);

  const submit = async () => {
    setAction({ busy: true, error: "" });
    try {
      const updated = await inspectionsApi.submit(id);
      setSession(updated);
    } catch (err) {
      setAction({ busy: false, error: envelopeError(err, "Submission failed.") });
      return;
    }
    setAction({ busy: false, error: "" });
  };

  const cancel = async () => {
    const reason = window.prompt("Reason for cancelling this inspection?");
    if (!reason) return;
    setAction({ busy: true, error: "" });
    try {
      const updated = await inspectionsApi.patchStatus(id, { status: "CANCELLED", reason });
      setSession(updated);
    } catch (err) {
      setAction({ busy: false, error: envelopeError(err, "Cancellation failed.") });
      return;
    }
    setAction({ busy: false, error: "" });
  };

  const requestAccess = async (evidenceId) => {
    try {
      const r = await evidenceApi.accessLink(evidenceId, "Inspector preview", 5);
      setAccessByEvidence((prev) => ({ ...prev, [evidenceId]: r }));
      window.open(absoluteUrl(r.accessUrl), "_blank", "noopener");
    } catch (err) {
      window.alert(envelopeError(err, "Could not generate access link."));
    }
  };

  if (loading) {
    return (
      <div className="px-8 py-10 text-steel-300 text-sm" data-testid={T.inspectionDetailLoading}>
        Loading inspection…
      </div>
    );
  }

  if (error || !session) {
    return (
      <div className="px-8 py-10 max-w-2xl">
        <button onClick={() => navigate("/inspections")} className="text-sm text-steel-300 hover:text-white mb-4 flex items-center gap-1.5">
          <ArrowLeft className="size-3.5" /> Back to inspections
        </button>
        <div className="text-sm text-signal-soft bg-signal/10 border border-signal/30 rounded-md px-3 py-2 flex items-start gap-2" data-testid={T.inspectionDetailError}>
          <AlertTriangle className="size-4 mt-0.5" />
          <div>{error || "Inspection not found."}</div>
        </div>
      </div>
    );
  }

  return (
    <div data-testid={T.inspectionDetailRoot} className="px-8 py-8 max-w-6xl">
      <div className="flex items-start justify-between gap-4 mb-6">
        <div>
          <button
            onClick={() => navigate("/inspections")}
            className="text-xs text-steel-300 hover:text-white mb-3 flex items-center gap-1.5"
            data-testid={T.inspectionDetailBack}
          >
            <ArrowLeft className="size-3.5" /> Back to inspections
          </button>
          <div className="flex items-center gap-3">
            <h1 className="text-xl font-semibold text-white font-mono" data-testid={T.inspectionDetailVehicle}>
              {session.references?.externalVehicleRef || "—"}
            </h1>
            <StatusBadge status={session.status} testId={T.inspectionDetailStatus} />
          </div>
          <div className="mt-1 font-mono text-[11px] text-steel-400">
            {session.inspectionType} · {session.sourceSystem} · created {fmt(session.createdAt)}
          </div>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <button
            onClick={load}
            className="px-3 py-1.5 rounded-md text-xs text-steel-200 bg-ink-800 border border-ink-700 hover:bg-ink-700/80 flex items-center gap-1.5"
            data-testid={T.inspectionDetailRefresh}
          >
            <RefreshCcw className="size-3.5" /> Refresh
          </button>
          {canUpload && !isTerminal && (
            <button
              onClick={() => setOpenUpload(true)}
              className="px-3 py-1.5 rounded-md text-xs bg-ink-800 border border-ink-700 text-steel-100 hover:bg-ink-700/80 flex items-center gap-1.5"
              data-testid={T.inspectionDetailUpload}
            >
              <ImagePlus className="size-3.5" /> Upload image
            </button>
          )}
          {canAi && images.length > 0 && (
            <>
              <button
                onClick={runQualityCheck}
                disabled={aiBusy}
                className="px-3 py-1.5 rounded-md text-xs bg-ink-800 border border-ink-700 text-steel-100 hover:bg-ink-700/80 flex items-center gap-1.5 disabled:opacity-50"
                data-testid="inspection-detail-quality"
              >
                {aiBusy ? <Loader2 className="size-3.5 animate-spin" /> : <Activity className="size-3.5" />}
                Quality check
              </button>
              <button
                onClick={runAi}
                disabled={aiBusy}
                className="px-3 py-1.5 rounded-md text-xs bg-amber400/20 border border-amber400/40 text-amber400 hover:bg-amber400/30 flex items-center gap-1.5 disabled:opacity-50"
                data-testid="inspection-detail-ai"
              >
                {aiBusy ? <Loader2 className="size-3.5 animate-spin" /> : <Sparkles className="size-3.5" />}
                Run AI
              </button>
            </>
          )}
          {canCompare && images.length > 0 && (
            <button
              onClick={runComparison}
              disabled={cmpBusy}
              className="px-3 py-1.5 rounded-md text-xs bg-ink-800 border border-ink-700 text-steel-100 hover:bg-ink-700/80 flex items-center gap-1.5 disabled:opacity-50"
              data-testid={T.inspectionDetailCompare}
            >
              {cmpBusy ? <Loader2 className="size-3.5 animate-spin" /> : <GitCompare className="size-3.5" />}
              Run comparison
            </button>
          )}
          {canSubmit && !isTerminal && (
            <button
              onClick={submit}
              disabled={action.busy || images.length === 0}
              title={images.length === 0 ? "Register at least one image before submitting" : ""}
              className="px-3 py-1.5 rounded-md text-xs bg-signal hover:bg-signal/90 disabled:opacity-50 text-white flex items-center gap-1.5"
              data-testid={T.inspectionDetailSubmit}
            >
              {action.busy ? <Loader2 className="size-3.5 animate-spin" /> : <Send className="size-3.5" />}
              Submit
            </button>
          )}
          {canCancel && !isTerminal && (
            <button
              onClick={cancel}
              disabled={action.busy}
              className="px-3 py-1.5 rounded-md text-xs text-signal-soft bg-signal/10 border border-signal/30 hover:bg-signal/20 flex items-center gap-1.5"
              data-testid={T.inspectionDetailCancel}
            >
              <Ban className="size-3.5" /> Cancel
            </button>
          )}
        </div>
      </div>

      {action.error && (
        <div className="text-sm text-signal-soft bg-signal/10 border border-signal/30 rounded-md px-3 py-2 mb-4">
          {action.error}
        </div>
      )}

      <section className="grid grid-cols-1 lg:grid-cols-3 gap-3 mb-6">
        <div className="rounded-lg border border-ink-700/70 bg-ink-900/60 p-5">
          <div className="text-[11px] uppercase tracking-wider text-steel-400 mb-3">References</div>
          <dl className="space-y-2 text-sm">
            <RefRow label="Vehicle" value={session.references?.externalVehicleRef} />
            <RefRow label="Rental" value={session.references?.externalRentalAgreementRef} />
            <RefRow label="Branch" value={session.references?.externalBranchRef} />
            <RefRow label="Maintenance" value={session.references?.externalMaintenanceRef} />
            <RefRow label="Work order" value={session.references?.externalWorkOrderRef} />
          </dl>
          <p className="text-[11px] text-steel-400 mt-3 leading-relaxed">
            CROMS and Maintenance refs are opaque strings. Real callback/write integrations land in Sprint 04.
          </p>
        </div>

        <div className="rounded-lg border border-ink-700/70 bg-ink-900/60 p-5">
          <div className="text-[11px] uppercase tracking-wider text-steel-400 mb-3">Lifecycle</div>
          <dl className="space-y-2 text-sm">
            <RefRow label="Created" value={fmt(session.createdAt)} />
            <RefRow label="Updated" value={fmt(session.updatedAt)} />
            <RefRow label="Submitted" value={fmt(session.submittedAt)} />
            <RefRow label="Cancelled" value={fmt(session.cancelledAt)} />
            <RefRow label="Failed" value={fmt(session.failedAt)} />
            {session.statusReason && <RefRow label="Reason" value={session.statusReason} />}
          </dl>
        </div>

        <div className="rounded-lg border border-ink-700/70 bg-ink-900/60 p-5">
          <div className="text-[11px] uppercase tracking-wider text-steel-400 mb-3">Evidence</div>
          <div className="text-3xl font-semibold text-white">{session.registeredImageCount || 0}</div>
          <div className="text-xs text-steel-400 mt-1">images registered (of {session.imageCount} total)</div>
          <div className="mt-3 text-[11px] text-steel-400 leading-relaxed flex items-start gap-1.5">
            <ShieldCheck className="size-3.5 mt-0.5 text-emerald-400" />
            Evidence is tenant-scoped. Access links are time-limited and audited.
          </div>
        </div>
      </section>

      {strip.length > 0 && (
        <section className="mb-6" data-testid={T.perVehicleStrip}>
          <button
            onClick={() => setStripOpen((o) => !o)}
            data-testid={T.perVehicleStripToggle}
            className="flex items-center gap-2 mb-3 text-sm font-semibold uppercase tracking-wider text-white"
          >
            {stripOpen ? <ChevronDown className="size-4" /> : <ChevronRight className="size-4" />}
            <History className="size-4 text-steel-300" /> Prior evidence for this vehicle
            <span className="text-[11px] font-mono text-steel-400 normal-case tracking-normal">advisory memory aid · {strip.length}</span>
          </button>
          {stripOpen && (
            <div className="flex gap-3 overflow-x-auto pb-2">
              {strip.map((t) => (
                <div key={t.inspectionImageId} data-testid={`${T.perVehicleTile}-${t.inspectionImageId}`}
                  className="shrink-0 w-44 rounded-lg border border-ink-700/70 bg-ink-900/60 p-3">
                  <div className="text-[11px] font-mono text-steel-300">{t.inspectionType || "—"}</div>
                  <div className="text-[11px] text-steel-400 mt-0.5">{t.capturePosition || "—"}</div>
                  <div className="text-[10px] text-steel-500 mt-1 font-mono">{fmt(t.capturedAt)}</div>
                  {t.evidenceId && canAccess && (
                    <button
                      onClick={() => requestAccess(t.evidenceId)}
                      className="mt-2 px-2 py-1 rounded-md text-[11px] bg-ink-800 border border-ink-700 hover:bg-ink-700/80 text-steel-200 flex items-center gap-1.5"
                    >
                      <Eye className="size-3" /> Open
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </section>
      )}

      <section>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-white">Inspection images</h2>
          <span className="text-[11px] font-mono text-steel-400">{images.length} item(s)</span>
        </div>
        {images.length === 0 ? (
          <div className="rounded-lg border border-ink-700/70 bg-ink-900/60 p-8 text-center text-sm text-steel-400" data-testid={T.inspectionDetailNoImages}>
            No images registered yet. {canUpload && !isTerminal && "Use “Upload image” to add one."}
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3" data-testid={T.inspectionDetailImagesGrid}>
            {images.map((img) => (
              <div key={img.id} data-testid={`${T.inspectionImageCard}-${img.id}`} className="rounded-lg border border-ink-700/70 bg-ink-900/60 p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[11px] font-mono text-steel-300">{img.capturePosition}</span>
                  <StatusBadge status={img.status === "REGISTERED" ? "EVIDENCE_REGISTERED" : img.status} />
                </div>
                <div className="text-[11px] text-steel-400 font-mono leading-relaxed">
                  {img.contentType} · {Math.round((img.fileSize || 0) / 1024)} KB
                  {img.width && img.height && ` · ${img.width}×${img.height}`}
                </div>
                <div className="text-[11px] text-steel-500 mt-1">{fmt(img.createdAt)}</div>
                {img.evidenceId && canAccess && (
                  <div className="mt-3">
                    <button
                      onClick={() => requestAccess(img.evidenceId)}
                      className="px-2.5 py-1 rounded-md text-[11px] bg-ink-800 border border-ink-700 hover:bg-ink-700/80 text-steel-200 flex items-center gap-1.5"
                      data-testid={`${T.inspectionImageAccess}-${img.id}`}
                    >
                      <Eye className="size-3" /> Open evidence
                    </button>
                    {accessByEvidence[img.evidenceId] && (
                      <p className="text-[10px] text-steel-500 mt-1.5 font-mono">
                        link valid until {fmt(accessByEvidence[img.evidenceId].expiresAt)}
                      </p>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </section>

      <UploadImageModal
        open={openUpload}
        onClose={() => setOpenUpload(false)}
        inspectionId={id}
        onUploaded={() => load()}
      />

      {(aiSummary || aiError || aiFindings.length > 0) && (
        <section className="mt-8" data-testid="inspection-detail-ai-section">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-white flex items-center gap-2">
              <Sparkles className="size-4 text-amber400" /> AI advisory output
            </h2>
            <span className="text-[11px] font-mono text-steel-400">advisory — not a liability decision</span>
          </div>
          {aiError && (
            <div className="text-sm text-signal-soft bg-signal/10 border border-signal/30 rounded-md px-3 py-2 mb-3">{aiError}</div>
          )}
          {aiSummary && (
            <div className="rounded-lg border border-ink-700/70 bg-ink-900/60 p-4 mb-3 text-sm">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-[12px]">
                <div><div className="text-steel-400 uppercase tracking-wider text-[10px] mb-0.5">status</div><div className="text-white font-mono">{aiSummary.status}</div></div>
                <div><div className="text-steel-400 uppercase tracking-wider text-[10px] mb-0.5">images</div><div className="text-white font-mono">{aiSummary.totalImages ?? "—"}</div></div>
                <div><div className="text-steel-400 uppercase tracking-wider text-[10px] mb-0.5">findings</div><div className="text-white font-mono">{aiSummary.totalFindings ?? "—"}</div></div>
                <div><div className="text-steel-400 uppercase tracking-wider text-[10px] mb-0.5">model</div><div className="text-white font-mono break-all">{aiSummary.modelVersion || "—"}</div></div>
              </div>
            </div>
          )}
          {aiFindings.length > 0 && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3" data-testid="ai-findings-grid">
              {aiFindings.map((f) => (
                <div key={f.id} data-testid={`ai-finding-card-${f.id}`} className="rounded-lg border border-ink-700/70 bg-ink-900/60 p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[11px] font-mono text-steel-300">{f.damageType}</span>
                    <span className={`text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded border ${
                      f.status === "AUTO_ACCEPTABLE" ? "bg-emerald-400/10 text-emerald-400 border-emerald-400/40"
                      : f.status === "LOW_CONFIDENCE" ? "bg-amber400/15 text-amber400 border-amber400/40"
                      : f.status === "UNCERTAIN" ? "bg-ink-800 text-steel-300 border-ink-600"
                      : "bg-signal/15 text-signal-soft border-signal/40"
                    }`}>{f.status}</span>
                  </div>
                  <div className="text-sm text-steel-100 mb-1">{f.area || "—"}</div>
                  <div className="text-[11px] font-mono text-steel-400">
                    confidence {(f.confidence * 100).toFixed(0)}% · severity {f.severity || "—"}
                  </div>
                  <div className="text-[10px] text-steel-500 mt-1 font-mono break-all">{f.modelVersion}</div>
                </div>
              ))}
            </div>
          )}
        </section>
      )}
      {(cmpError || comparison) && (
        <section className="mt-8" data-testid={T.comparisonSection}>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-white flex items-center gap-2">
              <GitCompare className="size-4 text-steel-300" /> Damage comparison
            </h2>
            <span className="text-[11px] font-mono text-steel-400">advisory — not a liability decision</span>
          </div>
          {cmpError && (
            <div className="text-sm text-signal-soft bg-signal/10 border border-signal/30 rounded-md px-3 py-2 mb-3">{cmpError}</div>
          )}
          {comparison && (
            <>
              <div className="rounded-lg border border-ink-700/70 bg-ink-900/60 p-4 mb-3 text-sm">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-[12px]">
                  <div><div className="text-steel-400 uppercase tracking-wider text-[10px] mb-0.5">status</div><div className="text-white font-mono">{comparison.status}</div></div>
                  <div><div className="text-steel-400 uppercase tracking-wider text-[10px] mb-0.5">baseline</div><div className="text-white font-mono break-all">{comparison.baselineInspectionSessionId || "—"}</div></div>
                  <div><div className="text-steel-400 uppercase tracking-wider text-[10px] mb-0.5">results</div><div className="text-white font-mono">{comparison.totalResults ?? "—"}</div></div>
                  <div><div className="text-steel-400 uppercase tracking-wider text-[10px] mb-0.5">routed to review</div><div className="text-white font-mono">{comparison.reviewItemsRouted ?? 0}</div></div>
                </div>
                {comparison.notComparableReason && (
                  <div className="mt-2 text-[12px] text-amber400">NOT_COMPARABLE: {comparison.notComparableReason}</div>
                )}
              </div>
              {(comparison.outcomes || []).length > 0 && (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                  {comparison.outcomes.map((o) => (
                    <div key={o.comparisonResultId} data-testid={`${T.comparisonResultCard}-${o.comparisonResultId}`}
                      className="rounded-lg border border-ink-700/70 bg-ink-900/60 p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-[11px] font-mono text-steel-300">{o.damageType || "—"}</span>
                        <span className={`text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded border ${
                          o.comparisonOutcomeCode === "NEW" ? "bg-signal/15 text-signal-soft border-signal/40"
                          : o.comparisonOutcomeCode === "PRE_EXISTING" ? "bg-ink-800 text-steel-300 border-ink-600"
                          : o.comparisonOutcomeCode === "REPAIRED" ? "bg-emerald-400/10 text-emerald-400 border-emerald-400/40"
                          : o.comparisonOutcomeCode === "CHANGED" ? "bg-amber400/15 text-amber400 border-amber400/40"
                          : "bg-ink-800 text-steel-400 border-ink-600"
                        }`}>{o.comparisonOutcomeCode}</span>
                      </div>
                      <div className="text-sm text-steel-100 mb-1">{o.area || "—"}</div>
                      <div className="text-[11px] font-mono text-steel-400">
                        {o.confidenceScore != null && `confidence ${(o.confidenceScore * 100).toFixed(0)}% · `}
                        {o.capturePosition || "—"}
                      </div>
                      {o.reviewRequired && <div className="text-[10px] text-amber400 mt-1">review required</div>}
                    </div>
                  ))}
                </div>
              )}
            </>
          )}
        </section>
      )}
    </div>
  );
}

function RefRow({ label, value }) {
  return (
    <div className="flex gap-3 items-baseline">
      <dt className="text-[11px] uppercase tracking-wider text-steel-400 w-24 shrink-0">{label}</dt>
      <dd className="font-mono text-[12px] text-steel-100 flex-1 break-all">{value || "—"}</dd>
    </div>
  );
}
