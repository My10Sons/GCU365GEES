/*
 * Minimal status pill used on inspection lists / details.
 * Repository Traceability: DI-SPRINT-01 (Inspection Status Lifecycle).
 */
import React from "react";

const STATUS_STYLE = {
  DRAFT: "bg-ink-700/60 text-steel-200 border-ink-600",
  CAPTURE_IN_PROGRESS: "bg-amber400/15 text-amber400 border-amber400/40",
  EVIDENCE_REGISTERED: "bg-emerald-400/10 text-emerald-400 border-emerald-400/40",
  SUBMITTED: "bg-signal/15 text-signal-soft border-signal/40",
  CANCELLED: "bg-ink-800 text-steel-400 border-ink-600 line-through",
  FAILED: "bg-signal/20 text-signal border-signal/60",
};

const PRETTY = {
  DRAFT: "Draft",
  CAPTURE_IN_PROGRESS: "Capture in progress",
  EVIDENCE_REGISTERED: "Evidence registered",
  SUBMITTED: "Submitted",
  CANCELLED: "Cancelled",
  FAILED: "Failed",
};

export default function StatusBadge({ status, testId }) {
  const cls = STATUS_STYLE[status] || STATUS_STYLE.DRAFT;
  return (
    <span
      data-testid={testId}
      className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-medium uppercase tracking-wider border ${cls}`}
    >
      {PRETTY[status] || status}
    </span>
  );
}
