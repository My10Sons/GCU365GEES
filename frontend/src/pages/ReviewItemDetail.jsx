/*
 * Repository Traceability:
 * - DI-SPRINT-03 (Review item detail, review decision form, additional-evidence request),
 *   DI-0019, DI-0034.
 */
import React, { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ArrowLeft, Loader2, Gavel, FilePlus2, FolderPlus } from "lucide-react";
import { reviewApi, casesApi } from "../lib/sprint03-api";
import { envelopeError } from "../lib/api";
import { useAuth } from "../lib/auth-context";
import { T } from "../constants/testIds";

const DECISIONS = ["CONFIRMED", "REJECTED", "EDITED", "ESCALATED", "ADDITIONAL_EVIDENCE_REQUIRED", "DEFERRED", "DUPLICATE"];
const REASON_REQUIRED = new Set(["REJECTED", "ESCALATED", "ADDITIONAL_EVIDENCE_REQUIRED", "DUPLICATE"]);

function Row({ label, value }) {
  return (
    <div className="flex gap-3 items-baseline">
      <dt className="text-[11px] uppercase tracking-wider text-steel-400 w-32 shrink-0">{label}</dt>
      <dd className="font-mono text-[12px] text-steel-100 flex-1 break-all">{value ?? "—"}</dd>
    </div>
  );
}

export default function ReviewItemDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { has } = useAuth();
  const canDecide = has("di.review.decide");
  const canCreateCase = has("di.damagecases.create");

  const [item, setItem] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [decision, setDecision] = useState({ code: "CONFIRMED", reason: "", busy: false, error: "", done: "" });
  const [evidence, setEvidence] = useState({ reason: "", busy: false, error: "", done: "" });
  const [edit, setEdit] = useState({ damageType: "", area: "", severity: "" });
  const [caseMsg, setCaseMsg] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const it = await reviewApi.get(id);
      setItem(it);
      const lo = it.linkedObject || {};
      setEdit({ damageType: lo.damageType || "", area: lo.area || "", severity: lo.severity || "" });
    } catch (err) {
      setError(envelopeError(err, "Could not load review item."));
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => { load(); }, [load]);

  const submitDecision = async () => {
    setDecision((d) => ({ ...d, busy: true, error: "", done: "" }));
    try {
      const body = { decisionCode: decision.code, reason: decision.reason || undefined };
      if (decision.code === "EDITED") {
        body.updatedFinding = { damageType: edit.damageType, area: edit.area, severity: edit.severity };
      }
      const res = await reviewApi.decide(id, body);
      setDecision((d) => ({ ...d, busy: false, done: `Recorded: ${res.decisionCode} → ${res.reviewStatus}` }));
      await load();
    } catch (err) {
      setDecision((d) => ({ ...d, busy: false, error: envelopeError(err, "Decision failed.") }));
    }
  };

  const submitEvidence = async () => {
    setEvidence((e) => ({ ...e, busy: true, error: "", done: "" }));
    try {
      await reviewApi.requestEvidence(id, { reason: evidence.reason });
      setEvidence((e) => ({ ...e, busy: false, done: "Additional evidence requested." }));
      await load();
    } catch (err) {
      setEvidence((e) => ({ ...e, busy: false, error: envelopeError(err, "Request failed.") }));
    }
  };

  const createCase = async () => {
    setCaseMsg("");
    try {
      const lo = item.linkedObject || {};
      const body = {
        inspectionSessionId: item.inspectionSessionId,
        caseType: "REPAIR_RELEVANT",
        severityCode: lo.severity || undefined,
        description: `Created from review item ${item.reviewItemId}.`,
      };
      if (item.objectType === "DAMAGE_FINDING") body.damageFindingIds = [item.objectId];
      else body.comparisonResultIds = [item.objectId];
      const c = await casesApi.create(body);
      setCaseMsg(`Damage case created: ${c.damageCaseId}`);
    } catch (err) {
      setCaseMsg(envelopeError(err, "Could not create damage case."));
    }
  };

  if (loading) return <div className="px-8 py-10 text-steel-300 text-sm">Loading review item…</div>;
  if (error || !item) return (
    <div className="px-8 py-10 max-w-2xl">
      <button onClick={() => navigate("/review")} className="text-sm text-steel-300 hover:text-white mb-4 flex items-center gap-1.5">
        <ArrowLeft className="size-3.5" /> Back to review queue
      </button>
      <div className="text-sm text-signal-soft bg-signal/10 border border-signal/30 rounded-md px-3 py-2">{error || "Not found."}</div>
    </div>
  );

  const lo = item.linkedObject || {};
  const reasonNeeded = REASON_REQUIRED.has(decision.code);

  return (
    <div data-testid={T.reviewItemRoot} className="px-8 py-8 max-w-5xl">
      <button onClick={() => navigate("/review")} data-testid={T.reviewItemBack}
        className="text-xs text-steel-300 hover:text-white mb-3 flex items-center gap-1.5">
        <ArrowLeft className="size-3.5" /> Back to review queue
      </button>
      <div className="flex items-center gap-3 mb-6">
        <h1 className="text-xl font-semibold text-white">Review item</h1>
        <span className="text-[11px] font-mono text-steel-400">{item.reviewStatus} · {item.priority}</span>
      </div>

      <section className="grid grid-cols-1 lg:grid-cols-2 gap-3 mb-6">
        <div className="rounded-lg border border-ink-700/70 bg-ink-900/60 p-5">
          <div className="text-[11px] uppercase tracking-wider text-steel-400 mb-3">Item</div>
          <dl className="space-y-2">
            <Row label="Object type" value={item.objectType} />
            <Row label="Source" value={item.source} />
            <Row label="Inspection" value={item.inspectionSessionId} />
            <Row label="Reason" value={item.reason} />
          </dl>
        </div>
        <div className="rounded-lg border border-ink-700/70 bg-ink-900/60 p-5">
          <div className="text-[11px] uppercase tracking-wider text-steel-400 mb-3">Linked advisory output</div>
          <dl className="space-y-2">
            <Row label="Damage type" value={lo.damageType} />
            <Row label="Area" value={lo.area} />
            <Row label="Outcome" value={lo.comparisonOutcomeCode} />
            <Row label="Confidence" value={lo.confidence != null ? `${(lo.confidence * 100).toFixed(0)}%` : (lo.confidenceScore != null ? `${(lo.confidenceScore * 100).toFixed(0)}%` : null)} />
            <Row label="Severity" value={lo.severity} />
            <Row label="Review state" value={lo.reviewState} />
          </dl>
        </div>
      </section>

      {canDecide && (
        <section className="rounded-lg border border-ink-700/70 bg-ink-900/60 p-5 mb-4">
          <h2 className="text-sm font-semibold text-white flex items-center gap-2 mb-3"><Gavel className="size-4 text-amber400" /> Record decision</h2>
          <div className="flex flex-wrap items-center gap-2 mb-3">
            <select data-testid={T.reviewDecisionCode} value={decision.code}
              onChange={(e) => setDecision((d) => ({ ...d, code: e.target.value }))}
              className="bg-ink-850 border border-ink-700 rounded-md px-2.5 py-1.5 text-xs text-white">
              {DECISIONS.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          {decision.code === "EDITED" && (
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 mb-3">
              <input placeholder="damageType (e.g. SCRATCH)" value={edit.damageType}
                onChange={(e) => setEdit((x) => ({ ...x, damageType: e.target.value }))}
                className="bg-ink-850 border border-ink-700 rounded-md px-2.5 py-1.5 text-xs text-white" />
              <input placeholder="area" value={edit.area}
                onChange={(e) => setEdit((x) => ({ ...x, area: e.target.value }))}
                className="bg-ink-850 border border-ink-700 rounded-md px-2.5 py-1.5 text-xs text-white" />
              <input placeholder="severity (LOW/MEDIUM/HIGH)" value={edit.severity}
                onChange={(e) => setEdit((x) => ({ ...x, severity: e.target.value }))}
                className="bg-ink-850 border border-ink-700 rounded-md px-2.5 py-1.5 text-xs text-white" />
            </div>
          )}
          <textarea data-testid={T.reviewDecisionReason} value={decision.reason}
            onChange={(e) => setDecision((d) => ({ ...d, reason: e.target.value }))}
            placeholder={reasonNeeded ? "Reason (required)" : "Reason (optional)"}
            className="w-full bg-ink-850 border border-ink-700 rounded-md px-3 py-2 text-xs text-white mb-3" rows={2} />
          {decision.error && <div data-testid={T.reviewDecisionError} className="text-xs text-signal-soft mb-2">{decision.error}</div>}
          {decision.done && <div className="text-xs text-emerald-400 mb-2">{decision.done}</div>}
          <button data-testid={T.reviewDecisionSubmit} onClick={submitDecision} disabled={decision.busy}
            className="px-3 py-1.5 rounded-md text-xs bg-signal hover:bg-signal/90 disabled:opacity-50 text-white flex items-center gap-1.5">
            {decision.busy ? <Loader2 className="size-3.5 animate-spin" /> : <Gavel className="size-3.5" />} Submit decision
          </button>
        </section>
      )}

      {canDecide && (
        <section className="rounded-lg border border-ink-700/70 bg-ink-900/60 p-5 mb-4">
          <h2 className="text-sm font-semibold text-white flex items-center gap-2 mb-3"><FilePlus2 className="size-4 text-steel-300" /> Request additional evidence</h2>
          <textarea data-testid={T.reviewEvidenceReason} value={evidence.reason}
            onChange={(e) => setEvidence((x) => ({ ...x, reason: e.target.value }))}
            placeholder="What evidence is needed and why?"
            className="w-full bg-ink-850 border border-ink-700 rounded-md px-3 py-2 text-xs text-white mb-3" rows={2} />
          {evidence.error && <div className="text-xs text-signal-soft mb-2">{evidence.error}</div>}
          {evidence.done && <div className="text-xs text-emerald-400 mb-2">{evidence.done}</div>}
          <button data-testid={T.reviewEvidenceSubmit} onClick={submitEvidence} disabled={evidence.busy || !evidence.reason.trim()}
            className="px-3 py-1.5 rounded-md text-xs bg-ink-800 border border-ink-700 text-steel-100 hover:bg-ink-700/80 disabled:opacity-50 flex items-center gap-1.5">
            {evidence.busy ? <Loader2 className="size-3.5 animate-spin" /> : <FilePlus2 className="size-3.5" />} Request evidence
          </button>
        </section>
      )}

      {canCreateCase && (
        <section className="rounded-lg border border-ink-700/70 bg-ink-900/60 p-5">
          <h2 className="text-sm font-semibold text-white flex items-center gap-2 mb-3"><FolderPlus className="size-4 text-steel-300" /> Create damage case from this item</h2>
          {caseMsg && <div className="text-xs text-steel-300 mb-2 font-mono break-all">{caseMsg}</div>}
          <button data-testid={T.reviewCreateCase} onClick={createCase}
            className="px-3 py-1.5 rounded-md text-xs bg-amber400/20 border border-amber400/40 text-amber400 hover:bg-amber400/30 flex items-center gap-1.5">
            <FolderPlus className="size-3.5" /> Create damage case
          </button>
        </section>
      )}
    </div>
  );
}
