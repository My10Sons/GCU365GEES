/*
 * Repository Traceability:
 * - Admin-only "Tenant Settings": consolidates per-tenant configuration used across Damage
 *   Intelligence — report branding (company name, branch name, logo) used on exported Trip
 *   Inspection PDFs, and the Trip Inspection branch policy (require a full 5-angle walkaround).
 *   Backed by GET/PUT /tenant/branding and GET/PUT /tenant/policy (di.configuration.manage).
 */
import React, { useEffect, useState } from "react";
import { Building2, ImagePlus, Loader2, Check, ShieldCheck, Settings2, Trash2 } from "lucide-react";
import { api, envelopeError } from "../lib/api";
import { useAuth } from "../lib/auth-context";
import { T } from "../constants/testIds";

async function fileToLogoDataUrl(file) {
  const dataUrl = await new Promise((res, rej) => { const r = new FileReader(); r.onload = () => res(r.result); r.onerror = rej; r.readAsDataURL(file); });
  const img = await new Promise((res, rej) => { const i = new Image(); i.onload = () => res(i); i.onerror = rej; i.src = dataUrl; });
  const maxDim = 320;
  let { width, height } = img;
  if (Math.max(width, height) > maxDim) { const s = maxDim / Math.max(width, height); width = Math.round(width * s); height = Math.round(height * s); }
  const canvas = document.createElement("canvas");
  canvas.width = width; canvas.height = height;
  canvas.getContext("2d").drawImage(img, 0, 0, width, height);
  return canvas.toDataURL("image/png");
}

export default function TenantSettings() {
  const { has, principal } = useAuth();
  const isAdmin = has("di.configuration.manage");

  const [loading, setLoading] = useState(true);
  const [companyName, setCompanyName] = useState("");
  const [branchName, setBranchName] = useState("");
  const [logoDataUrl, setLogoDataUrl] = useState(null);
  const [requireFull, setRequireFull] = useState(false);
  const [savingBranding, setSavingBranding] = useState(false);
  const [savingPolicy, setSavingPolicy] = useState(false);
  const [savedMsg, setSavedMsg] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    Promise.all([api.get("/tenant/branding"), api.get("/tenant/policy")])
      .then(([b, p]) => {
        if (!active) return;
        const bd = b.data?.data || {}; const pd = p.data?.data || {};
        setCompanyName(bd.companyName || ""); setBranchName(bd.branchName || ""); setLogoDataUrl(bd.logoDataUrl || null);
        setRequireFull(!!pd.requireFullWalkaround);
      })
      .catch((err) => setError(envelopeError(err, "Could not load tenant settings.")))
      .finally(() => active && setLoading(false));
    return () => { active = false; };
  }, []);

  const flash = (m) => { setSavedMsg(m); setTimeout(() => setSavedMsg(""), 2500); };

  const onLogoPick = async (file) => {
    setError("");
    try { setLogoDataUrl(await fileToLogoDataUrl(file)); }
    catch { setError("Could not read that image. Please try a different file."); }
  };

  const saveBranding = async () => {
    setSavingBranding(true); setError("");
    try {
      await api.put("/tenant/branding", { companyName, branchName, logoDataUrl });
      flash("Branding saved.");
    } catch (err) { setError(envelopeError(err, "Could not save branding.")); }
    finally { setSavingBranding(false); }
  };

  const savePolicy = async () => {
    setSavingPolicy(true); setError("");
    try {
      await api.put("/tenant/policy", { requireFullWalkaround: requireFull });
      flash("Policy saved.");
    } catch (err) { setError(envelopeError(err, "Could not save policy.")); }
    finally { setSavingPolicy(false); }
  };

  if (!isAdmin) {
    return (
      <div data-testid={T.tenantSettingsRoot} className="px-8 py-8 max-w-3xl">
        <h1 className="text-2xl font-semibold text-white flex items-center gap-3"><Settings2 className="size-6 text-steel-300" /> Tenant Settings</h1>
        <p className="text-sm text-amber400 mt-4">You need administrator permission (di.configuration.manage) to manage tenant settings.</p>
      </div>
    );
  }

  return (
    <div data-testid={T.tenantSettingsRoot} className="px-8 py-8 max-w-3xl">
      <div className="text-[11px] uppercase tracking-[0.22em] text-steel-400">Damage Intelligence</div>
      <h1 className="text-2xl font-semibold text-white mt-1 flex items-center gap-3"><Settings2 className="size-6 text-steel-300" /> Tenant Settings</h1>
      <p className="text-sm text-steel-300 mt-2">Per-tenant configuration for <span className="font-mono text-steel-200">{principal?.tenantId}</span>. Applies to all staff in this tenant.</p>

      {error && <div data-testid="tenant-settings-error" className="mt-4 text-sm text-signal-soft bg-signal/10 border border-signal/30 rounded-md px-3 py-2">{error}</div>}
      {savedMsg && <div data-testid="tenant-settings-saved" className="mt-4 text-sm text-emerald400 bg-emerald-400/10 border border-emerald400/30 rounded-md px-3 py-2">{savedMsg}</div>}

      {loading ? (
        <div className="mt-8 flex items-center gap-2 text-steel-400 text-sm"><Loader2 className="size-4 animate-spin" /> Loading…</div>
      ) : (
        <div className="mt-6 space-y-6">
          {/* Branding */}
          <section className="rounded-lg border border-ink-700/70 bg-ink-900/60 p-5">
            <div className="flex items-center gap-2 mb-4"><Building2 className="size-4 text-steel-300" /><span className="text-sm font-medium text-white">Report branding</span><span className="text-[11px] text-steel-500">printed on exported PDFs</span></div>
            <div className="flex flex-col sm:flex-row gap-6">
              <div className="w-40 shrink-0">
                <div className="text-[11px] uppercase tracking-wider text-steel-400 mb-2">Logo</div>
                <label className="block w-40 h-28 rounded-lg border-2 border-dashed border-ink-700 hover:border-signal/50 bg-ink-950 overflow-hidden cursor-pointer grid place-items-center transition-colors">
                  {logoDataUrl ? <img src={logoDataUrl} alt="Logo" className="w-full h-full object-contain bg-white" />
                    : <span className="flex flex-col items-center gap-1 text-steel-400 text-xs"><ImagePlus className="size-6" /> Upload logo</span>}
                  <input data-testid="tenant-logo-input" type="file" accept="image/png,image/jpeg,image/webp" className="hidden" onChange={(e) => e.target.files?.[0] && onLogoPick(e.target.files[0])} />
                </label>
                {logoDataUrl && (
                  <button data-testid="tenant-logo-remove" onClick={() => setLogoDataUrl(null)} className="mt-2 text-[11px] text-steel-400 hover:text-signal-soft flex items-center gap-1"><Trash2 className="size-3" /> Remove logo</button>
                )}
              </div>
              <div className="flex-1 space-y-3">
                <div>
                  <label className="text-[11px] uppercase tracking-wider text-steel-400">Company name</label>
                  <input data-testid="tenant-company-input" value={companyName} onChange={(e) => setCompanyName(e.target.value)} placeholder="e.g. Riyadah Technology"
                    className="mt-1 w-full rounded-md bg-ink-900/70 border border-ink-700 px-3 py-2 text-sm text-steel-100 placeholder:text-steel-500 focus:outline-none focus:border-signal/50" />
                </div>
                <div>
                  <label className="text-[11px] uppercase tracking-wider text-steel-400">Branch name</label>
                  <input data-testid="tenant-branch-input" value={branchName} onChange={(e) => setBranchName(e.target.value)} placeholder="e.g. Doha — Main Branch"
                    className="mt-1 w-full rounded-md bg-ink-900/70 border border-ink-700 px-3 py-2 text-sm text-steel-100 placeholder:text-steel-500 focus:outline-none focus:border-signal/50" />
                </div>
                <button data-testid="tenant-branding-save" onClick={saveBranding} disabled={savingBranding}
                  className="px-4 py-2 rounded-md text-sm font-medium bg-signal hover:bg-signal/90 disabled:opacity-50 text-white flex items-center gap-2">
                  {savingBranding ? <Loader2 className="size-4 animate-spin" /> : <Check className="size-4" />} Save branding
                </button>
              </div>
            </div>
          </section>

          {/* Policy */}
          <section className="rounded-lg border border-ink-700/70 bg-ink-900/60 p-5">
            <div className="flex items-center gap-2 mb-4"><ShieldCheck className="size-4 text-steel-300" /><span className="text-sm font-medium text-white">Trip Inspection policy</span></div>
            <label className="flex items-center gap-2 text-sm text-steel-300 cursor-pointer w-fit" data-testid="tenant-policy-toggle">
              <input type="checkbox" checked={requireFull} onChange={(e) => setRequireFull(e.target.checked)} className="size-4 accent-signal" />
              Require a full 5-angle walkaround for every inspection
            </label>
            <p className="text-[12px] text-steel-400 mt-2">When enabled, staff must capture all 5 exterior angles (Front, Rear, Left, Right, Roof) before they can run an analysis — the walkaround gate is pre-enabled and locked.</p>
            <button data-testid="tenant-policy-save" onClick={savePolicy} disabled={savingPolicy}
              className="mt-3 px-4 py-2 rounded-md text-sm font-medium bg-signal hover:bg-signal/90 disabled:opacity-50 text-white flex items-center gap-2">
              {savingPolicy ? <Loader2 className="size-4 animate-spin" /> : <Check className="size-4" />} Save policy
            </button>
          </section>

          <p className="text-[11px] text-steel-500">These settings can also be provisioned by the CROMS / Maintenance system via the tenant API.</p>
        </div>
      )}
    </div>
  );
}
