/*
 * Repository Traceability:
 * - DI-SPRINT-01 (Create Inspection Session), DI-0034 (POST /inspection-sessions),
 *   DECISION-Sprint01-b (opaque external string references).
 */
import React, { useState } from "react";
import { Loader2 } from "lucide-react";
import Modal from "../ui/Modal";
import { inspectionsApi, envelopeError } from "../../lib/inspections-api";
import { T } from "../../constants/testIds";

const INSPECTION_TYPES = [
  { code: "CHECK_OUT", label: "Check-out (CROMS)" },
  { code: "CHECK_IN", label: "Check-in (CROMS)" },
  { code: "MAINTENANCE_INTAKE", label: "Maintenance intake" },
  { code: "MAINTENANCE_HANDBACK", label: "Maintenance handback" },
  { code: "SPOT_CHECK", label: "Spot check" },
];

const SOURCE_SYSTEMS = [
  { code: "GCU365-CROMS", label: "GCU365-CROMS" },
  { code: "GCU365Maintenance", label: "GCU365Maintenance" },
  { code: "DI-Web", label: "DI-Web" },
  { code: "DI-Mobile", label: "DI-Mobile" },
];

export default function CreateInspectionModal({ open, onClose, onCreated }) {
  const [form, setForm] = useState({
    inspectionType: "CHECK_OUT",
    sourceSystem: "DI-Web",
    externalVehicleRef: "",
    externalRentalAgreementRef: "",
    externalBranchRef: "",
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const setField = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

  const submit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      const created = await inspectionsApi.create({
        inspectionType: form.inspectionType,
        sourceSystem: form.sourceSystem,
        references: {
          externalVehicleRef: form.externalVehicleRef.trim(),
          externalRentalAgreementRef: form.externalRentalAgreementRef.trim() || undefined,
          externalBranchRef: form.externalBranchRef.trim() || undefined,
        },
      });
      onCreated?.(created);
      onClose?.();
    } catch (err) {
      setError(envelopeError(err, "Could not create inspection."));
    } finally {
      setSubmitting(false);
    }
  };

  const inputCls =
    "w-full bg-ink-850 border border-ink-700 focus:border-signal/60 focus:ring-2 focus:ring-signal/20 outline-none rounded-md px-3 py-2 text-sm text-white placeholder:text-steel-400";
  const labelCls = "block text-[11px] font-medium uppercase tracking-wider text-steel-300 mb-1.5";

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="New inspection session"
      testId={T.createInspectionModal}
      footer={
        <>
          <button
            type="button"
            onClick={onClose}
            className="px-3 py-1.5 rounded-md text-sm text-steel-200 bg-ink-800 border border-ink-700 hover:bg-ink-700/80"
            data-testid={T.createInspectionCancel}
          >
            Cancel
          </button>
          <button
            type="submit"
            form="create-inspection-form"
            disabled={submitting || !form.externalVehicleRef.trim()}
            className="px-3 py-1.5 rounded-md text-sm bg-signal hover:bg-signal/90 disabled:opacity-50 text-white flex items-center gap-1.5"
            data-testid={T.createInspectionSubmit}
          >
            {submitting && <Loader2 className="size-3.5 animate-spin" />}
            Create
          </button>
        </>
      }
    >
      <form id="create-inspection-form" onSubmit={submit} className="space-y-4" noValidate>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className={labelCls}>Inspection type</label>
            <select
              data-testid={T.createInspectionType}
              className={inputCls}
              value={form.inspectionType}
              onChange={setField("inspectionType")}
            >
              {INSPECTION_TYPES.map((o) => (
                <option key={o.code} value={o.code}>
                  {o.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className={labelCls}>Source system</label>
            <select
              data-testid={T.createInspectionSource}
              className={inputCls}
              value={form.sourceSystem}
              onChange={setField("sourceSystem")}
            >
              {SOURCE_SYSTEMS.map((o) => (
                <option key={o.code} value={o.code}>
                  {o.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label className={labelCls}>Vehicle reference (required)</label>
          <input
            data-testid={T.createInspectionVehicle}
            className={inputCls}
            placeholder="e.g. VEH-RAV4-2024-001"
            value={form.externalVehicleRef}
            onChange={setField("externalVehicleRef")}
            required
          />
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className={labelCls}>Rental agreement</label>
            <input
              data-testid={T.createInspectionRental}
              className={inputCls}
              placeholder="(optional) RA-2026-00001"
              value={form.externalRentalAgreementRef}
              onChange={setField("externalRentalAgreementRef")}
            />
          </div>
          <div>
            <label className={labelCls}>Branch</label>
            <input
              data-testid={T.createInspectionBranch}
              className={inputCls}
              placeholder="(optional) BR-DOH-01"
              value={form.externalBranchRef}
              onChange={setField("externalBranchRef")}
            />
          </div>
        </div>

        {error && (
          <div
            data-testid={T.createInspectionError}
            className="text-sm text-signal-soft bg-signal/10 border border-signal/30 rounded-md px-3 py-2"
          >
            {error}
          </div>
        )}

        <p className="text-[11px] text-steel-400 leading-relaxed">
          External references (vehicle, rental, branch) are stored as opaque strings;
          shape alignment with CROMS lives in Sprint 04.
        </p>
      </form>
    </Modal>
  );
}
