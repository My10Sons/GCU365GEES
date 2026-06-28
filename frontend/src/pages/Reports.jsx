/*
 * Repository Traceability:
 * - DI-SPRINT-05 (Reports web screen — generate, list, controlled access link),
 *   DI-0016, DI-0034.
 */
import React, { useCallback, useEffect, useState } from "react";
import { FileText, RefreshCcw, Loader2, Link2, ShieldCheck } from "lucide-react";
import { api, envelopeError } from "../lib/api";
import { absoluteUrl } from "../lib/inspections-api";
import { useAuth } from "../lib/auth-context";
import { T } from "../constants/testIds";

const REPORT_TYPES = [
  { v: "INSPECTION_SUMMARY_REPORT", needs: "session" },
  { v: "DAMAGE_DETECTION_REPORT", needs: "session" },
  { v: "DAMAGE_COMPARISON_REPORT", needs: "session" },
  { v: "EVIDENCE_PACKAGE_REPORT", needs: "session" },
  { v: "DAMAGE_CASE_REPORT", needs: "case" },
  { v: "MAINTENANCE_HANDOFF_REPORT", needs: "case" },
  { v: "RENTAL_DAMAGE_SUMMARY_REPORT", needs: "rental" },
];

function fmt(d) { try { return new Date(d).toLocaleString(); } catch { return d; } }

export default function Reports() {
  const { has } = useAuth();
  const canGenerate = has("di.reports.generate");
  const canAccess = has("di.reports.access");

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [form, setForm] = useState({ type: "INSPECTION_SUMMARY_REPORT", session: "", caseId: "", rental: "", busy: false, error: "" });
  const [linkMsg, setLinkMsg] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const { data } = await api.get("/reports", { params: { page: 1, pageSize: 50 } });
      setData(data.data);
    } catch (err) {
      setError(envelopeError(err, "Could not load reports."));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const needs = REPORT_TYPES.find((r) => r.v === form.type)?.needs;

  const generate = async () => {
    setForm((f) => ({ ...f, busy: true, error: "" }));
    try {
      const body = { reportType: form.type };
      if (needs === "session") body.inspectionSessionId = form.session.trim();
      if (needs === "case") body.damageCaseId = form.caseId.trim();
      if (needs === "rental") body.rentalAgreementId = form.rental.trim();
      await api.post("/reports", body);
      setForm((f) => ({ ...f, busy: false }));
      await load();
    } catch (err) {
      setForm((f) => ({ ...f, busy: false, error: envelopeError(err, "Report generation failed.") }));
    }
  };

  const getLink = async (reportId) => {
    setLinkMsg("");
    try {
      const { data } = await api.post(`/reports/${reportId}/access-link`, { purpose: "review" });
      const full = absoluteUrl(data.data.accessUrl);
      window.open(full, "_blank", "noopener");
      setLinkMsg(`Access link opened (expires in ${data.data.expiresInSeconds}s).`);
    } catch (err) {
      setLinkMsg(envelopeError(err, "Could not create access link."));
    }
  };

  const list = data?.items || [];
  const inputCls = "bg-ink-850 border border-ink-700 focus:border-signal/60 outline-none rounded-md px-2.5 py-1.5 text-xs text-white";

  return (
    <div data-testid={T.reportsRoot} className="px-8 py-8 max-w-6xl">
      <div className="flex items-start justify-between gap-4 mb-6">
        <div>
          <div className="text-[11px] uppercase tracking-[0.22em] text-steel-400">Damage Intelligence</div>
          <h1 className="text-2xl font-semibold text-white mt-1 flex items-center gap-3">
            <FileText className="size-6 text-steel-300" /> Reports & evidence packages
          </h1>
          <p className="text-sm text-steel-300 mt-2 max-w-2xl flex items-start gap-1.5">
            <ShieldCheck className="size-4 mt-0.5 text-emerald-400" />
            Controlled, tenant-scoped reports. AI findings are advisory; access links are time-limited — no public URLs.
          </p>
        </div>
        <button data-testid={T.reportsRefresh} onClick={load}
          className="px-3 py-1.5 rounded-md text-xs text-steel-200 bg-ink-800 border border-ink-700 hover:bg-ink-700/80 flex items-center gap-1.5">
          <RefreshCcw className="size-3.5" /> Refresh
        </button>
      </div>

      {canGenerate && (
        <section className="rounded-lg border border-ink-700/70 bg-ink-900/60 p-5 mb-6">
          <h2 className="text-sm font-semibold text-white mb-3">Generate report</h2>
          <div className="flex flex-wrap items-end gap-3">
            <div>
              <label className="block text-[11px] uppercase tracking-wider text-steel-400 mb-1">Type</label>
              <select data-testid={T.reportTypeSelect} value={form.type} className={inputCls}
                onChange={(e) => setForm((f) => ({ ...f, type: e.target.value }))}>
                {REPORT_TYPES.map((r) => <option key={r.v} value={r.v}>{r.v}</option>)}
              </select>
            </div>
            {needs === "session" && (
              <div>
                <label className="block text-[11px] uppercase tracking-wider text-steel-400 mb-1">Inspection session ID</label>
                <input data-testid={T.reportSessionInput} value={form.session} className={`${inputCls} w-72`}
                  onChange={(e) => setForm((f) => ({ ...f, session: e.target.value }))} placeholder="DI-INS-…" />
              </div>
            )}
            {needs === "case" && (
              <div>
                <label className="block text-[11px] uppercase tracking-wider text-steel-400 mb-1">Damage case ID</label>
                <input data-testid={T.reportCaseInput} value={form.caseId} className={`${inputCls} w-72`}
                  onChange={(e) => setForm((f) => ({ ...f, caseId: e.target.value }))} placeholder="DI-CASE-…" />
              </div>
            )}
            {needs === "rental" && (
              <div>
                <label className="block text-[11px] uppercase tracking-wider text-steel-400 mb-1">Rental agreement ID</label>
                <input data-testid={T.reportRentalInput} value={form.rental} className={`${inputCls} w-72`}
                  onChange={(e) => setForm((f) => ({ ...f, rental: e.target.value }))} placeholder="RA-…" />
              </div>
            )}
            <button data-testid={T.reportGenerate} onClick={generate} disabled={form.busy}
              className="px-3 py-1.5 rounded-md text-xs bg-signal hover:bg-signal/90 disabled:opacity-50 text-white flex items-center gap-1.5">
              {form.busy ? <Loader2 className="size-3.5 animate-spin" /> : <FileText className="size-3.5" />} Generate
            </button>
          </div>
          {form.error && <div data-testid={T.reportError} className="text-xs text-signal-soft mt-2">{form.error}</div>}
        </section>
      )}

      {linkMsg && <div className="text-xs text-steel-300 mb-3 font-mono">{linkMsg}</div>}
      {error && <div className="text-sm text-signal-soft bg-signal/10 border border-signal/30 rounded-md px-3 py-2 mb-4">{error}</div>}

      <div className="rounded-lg border border-ink-700/70 bg-ink-900/60 overflow-hidden">
        <table className="w-full text-sm" data-testid={T.reportsTable}>
          <thead className="bg-ink-900 text-[11px] uppercase tracking-wider text-steel-400">
            <tr>
              <th className="text-left px-4 py-2.5 font-medium">Type</th>
              <th className="text-left px-4 py-2.5 font-medium">Reference</th>
              <th className="text-left px-4 py-2.5 font-medium">Status</th>
              <th className="text-left px-4 py-2.5 font-medium">Generated</th>
              <th className="text-left px-4 py-2.5 font-medium"></th>
            </tr>
          </thead>
          <tbody>
            {loading && <tr><td colSpan={5} className="px-4 py-10 text-center text-steel-400 text-sm">Loading…</td></tr>}
            {!loading && list.length === 0 && (
              <tr><td colSpan={5} className="px-4 py-10 text-center text-steel-400 text-sm" data-testid={T.reportsEmpty}>
                No reports yet. Generate one above.</td></tr>
            )}
            {!loading && list.map((r) => (
              <tr key={r.reportId} data-testid={`${T.reportRow}-${r.reportId}`}
                className="border-t border-ink-700/60 hover:bg-ink-800/60 transition-colors">
                <td className="px-4 py-3 text-steel-200 text-[12px]">{r.reportType}</td>
                <td className="px-4 py-3 font-mono text-[11px] text-steel-300 break-all">{r.inspectionSessionId || r.damageCaseId || r.rentalAgreementId || "—"}</td>
                <td className="px-4 py-3 text-steel-200 font-mono text-[12px]">{r.status}</td>
                <td className="px-4 py-3 text-steel-400 text-[12px]">{fmt(r.createdAt)}</td>
                <td className="px-4 py-3">
                  {canAccess && (
                    <button data-testid={`${T.reportAccessLink}-${r.reportId}`} onClick={() => getLink(r.reportId)}
                      className="text-signal-soft hover:underline underline-offset-2 text-[12px] flex items-center gap-1">
                      <Link2 className="size-3" /> Access link
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
