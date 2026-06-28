/*
 * Repository Traceability:
 * - DI-SPRINT-01 (Upload Request + Register Image), DI-0007 (Capture Positions),
 *   DI-0034 (POST /inspection-sessions/{id}/images/upload-request + POST /images).
 * - Uploads via the signed time-limited PUT URL, then registers the image.
 */
import React, { useEffect, useRef, useState } from "react";
import { Loader2, Upload } from "lucide-react";
import Modal from "../ui/Modal";
import { inspectionsApi, envelopeError, absoluteUrl } from "../../lib/inspections-api";
import { tokenStore } from "../../lib/api";
import { T } from "../../constants/testIds";

const ACCEPT = "image/jpeg,image/png,image/webp";

export default function UploadImageModal({ open, onClose, inspectionId, onUploaded }) {
  const [positions, setPositions] = useState([]);
  const [position, setPosition] = useState("");
  const [file, setFile] = useState(null);
  const [progress, setProgress] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const fileRef = useRef(null);

  useEffect(() => {
    if (!open) return undefined;
    setError("");
    setFile(null);
    setProgress(null);
    inspectionsApi
      .capturePositions()
      .then((d) => {
        setPositions(d.items);
        if (!position && d.items.length) setPosition(d.items[0].code);
      })
      .catch(() => setError("Could not load capture positions."));
    return undefined;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  const submit = async (e) => {
    e.preventDefault();
    if (!file || !position) return;
    setBusy(true);
    setError("");
    try {
      const ur = await inspectionsApi.uploadRequest(inspectionId, {
        capturePosition: position,
        fileName: file.name,
        contentType: file.type || "image/jpeg",
        fileSize: file.size,
      });
      setProgress("Uploading…");
      const target = absoluteUrl(ur.uploadUrl);
      const tenant = tokenStore.getTenant();
      const putResp = await fetch(target, {
        method: "PUT",
        headers: {
          "Content-Type": file.type || "image/jpeg",
          // The signed URL is self-authorizing, but tenant header is harmless.
          ...(tenant ? { "X-Tenant-Id": tenant } : {}),
        },
        body: file,
      });
      if (!putResp.ok) {
        const text = await putResp.text();
        throw new Error(`Upload failed (${putResp.status}). ${text.slice(0, 160)}`);
      }
      setProgress("Registering…");
      const registered = await inspectionsApi.register(inspectionId, {
        uploadRequestId: ur.uploadRequestId,
      });
      onUploaded?.(registered);
      onClose?.();
    } catch (err) {
      setError(envelopeError(err, err?.message || "Upload failed."));
    } finally {
      setBusy(false);
      setProgress(null);
    }
  };

  const inputCls =
    "w-full bg-ink-850 border border-ink-700 focus:border-signal/60 focus:ring-2 focus:ring-signal/20 outline-none rounded-md px-3 py-2 text-sm text-white";

  return (
    <Modal
      open={open}
      onClose={busy ? undefined : onClose}
      title="Upload inspection image"
      testId={T.uploadImageModal}
      footer={
        <>
          <button
            type="button"
            onClick={onClose}
            disabled={busy}
            className="px-3 py-1.5 rounded-md text-sm text-steel-200 bg-ink-800 border border-ink-700 hover:bg-ink-700/80 disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            form="upload-image-form"
            disabled={!file || !position || busy}
            data-testid={T.uploadImageSubmit}
            className="px-3 py-1.5 rounded-md text-sm bg-signal hover:bg-signal/90 disabled:opacity-50 text-white flex items-center gap-1.5"
          >
            {busy ? <Loader2 className="size-3.5 animate-spin" /> : <Upload className="size-3.5" />}
            {progress || "Upload"}
          </button>
        </>
      }
    >
      <form id="upload-image-form" onSubmit={submit} className="space-y-4">
        <div>
          <label className="block text-[11px] font-medium uppercase tracking-wider text-steel-300 mb-1.5">
            Capture position
          </label>
          <select
            data-testid={T.uploadImagePosition}
            className={inputCls}
            value={position}
            onChange={(e) => setPosition(e.target.value)}
          >
            {positions.map((p) => (
              <option key={p.code} value={p.code}>
                {p.label} {p.required ? "· required" : ""}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-[11px] font-medium uppercase tracking-wider text-steel-300 mb-1.5">
            Image file (JPEG / PNG / WebP, ≤ 25 MB)
          </label>
          <input
            ref={fileRef}
            data-testid={T.uploadImageFile}
            type="file"
            accept={ACCEPT}
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className="block w-full text-sm text-steel-200 file:mr-3 file:py-2 file:px-3 file:rounded-md file:border file:border-ink-700 file:bg-ink-800 file:text-steel-200 file:cursor-pointer hover:file:bg-ink-700"
          />
          {file && (
            <p className="text-[11px] text-steel-400 mt-1.5 font-mono">
              {file.name} · {(file.size / 1024).toFixed(1)} KB · {file.type || "unknown"}
            </p>
          )}
        </div>

        {error && (
          <div
            data-testid={T.uploadImageError}
            className="text-sm text-signal-soft bg-signal/10 border border-signal/30 rounded-md px-3 py-2"
          >
            {error}
          </div>
        )}
      </form>
    </Modal>
  );
}
