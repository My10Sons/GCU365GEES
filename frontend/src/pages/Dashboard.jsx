/*
 * Repository Traceability:
 * - Source Documents: DI-SPRINT-00 (Web Setup — dashboard placeholder), DI-0034
 *   (GET /health, GET /health/dependencies, GET /version), DI-0031 (Scope boundary).
 */
import React, { useEffect, useState } from "react";
import { api } from "../lib/api";
import { T } from "../constants/testIds";
import { Activity, Database, Cpu, HardDrive, Lock, GitBranch, CheckCircle2, XCircle, Plug, AlertTriangle } from "lucide-react";
import { useAuth } from "../lib/auth-context";

const SPRINTS = [
  { id: "SPRINT-00", label: "Engineering Setup", status: "done" },
  { id: "SPRINT-01", label: "Inspection & Evidence Foundation", status: "done" },
  { id: "SPRINT-02", label: "Image Quality & AI Detection", status: "done" },
  { id: "SPRINT-03", label: "Review, Comparison, Damage Cases", status: "done" },
  { id: "SPRINT-04", label: "CROMS & Maintenance Integration", status: "done" },
  { id: "SPRINT-05", label: "Reports, Monitoring, Security, Release", status: "in-progress" },
];

function HealthCard({ testId, icon: Icon, label, healthy, hint }) {
  const Status = healthy ? CheckCircle2 : XCircle;
  return (
    <div
      data-testid={testId}
      className="rounded-lg border border-ink-700/70 bg-ink-900/60 p-4"
    >
      <div className="flex items-start gap-3">
        <div className="size-9 rounded-md bg-ink-800 border border-ink-700 flex items-center justify-center">
          <Icon className="size-4 text-steel-300" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-[11px] uppercase tracking-wider text-steel-400">
            {label}
          </div>
          <div className="flex items-center gap-2 mt-0.5">
            <Status
              className={`size-4 ${healthy ? "text-emerald-400" : "text-signal"}`}
            />
            <span className="text-sm font-medium text-white">
              {healthy ? "Healthy" : "Unavailable"}
            </span>
          </div>
          {hint && (
            <div className="text-[11px] text-steel-400 font-mono mt-1.5 truncate">
              {hint}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function MetricTile({ label, value, sub }) {
  return (
    <div className="rounded-lg border border-ink-700/70 bg-ink-900/60 p-4">
      <div className="text-[11px] uppercase tracking-wider text-steel-400">{label}</div>
      <div className="text-2xl font-semibold text-white mt-1 tabular-nums">{value ?? "—"}</div>
      {sub && <div className="text-[11px] text-steel-400 mt-0.5">{sub}</div>}
    </div>
  );
}

function IntegStat({ label, value, warn }) {
  return (
    <div>
      <div className="text-[11px] uppercase tracking-wider text-steel-400">{label}</div>
      <div className={`text-lg font-semibold tabular-nums mt-0.5 ${warn ? "text-amber400" : "text-white"}`}>{value ?? 0}</div>
    </div>
  );
}

export default function Dashboard() {
  const { principal } = useAuth();
  const [deps, setDeps] = useState(null);
  const [version, setVersion] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const [d, v, m] = await Promise.all([
          api.get("/health/dependencies"),
          api.get("/version"),
          api.get("/monitoring/metrics"),
        ]);
        if (!active) return;
        setDeps(d.data.data);
        setVersion(v.data.data);
        setMetrics(m.data.data);
      } catch (err) {
        if (active) setError(err?.message || "Failed to load dashboard data.");
      }
    })();
    return () => {
      active = false;
    };
  }, []);

  return (
    <div data-testid={T.dashboardRoot} className="px-8 py-8 max-w-6xl">
      <div className="mb-8">
        <div className="text-[11px] uppercase tracking-[0.22em] text-steel-400">
          Operator Console
        </div>
        <h1 className="text-2xl font-semibold text-white mt-1">
          Welcome back, {(principal?.displayName || principal?.email || "").split("@")[0]}
        </h1>
        <p className="text-sm text-steel-300 mt-2 max-w-2xl">
          Inspection, AI damage detection, comparison, review, damage cases, and CROMS
          &amp; Maintenance integration are live. Sprint 05 adds reports, monitoring, and
          release hardening.
        </p>
      </div>

      {error && (
        <div className="text-sm text-signal-soft bg-signal/10 border border-signal/30 rounded-md px-3 py-2 mb-6">
          {error}
        </div>
      )}

      {metrics && (
        <section data-testid={T.dashboardMetrics} className="mb-10">
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 mb-3">
            <MetricTile label="Inspections" value={metrics.workflow?.inspectionsTotal} sub={`${metrics.workflow?.inspectionsSubmitted ?? 0} submitted`} />
            <MetricTile label="Images" value={metrics.workflow?.imagesRegistered} />
            <MetricTile label="AI analyses" value={metrics.ai?.analysesCompleted} sub={`${metrics.ai?.analysesFailed ?? 0} failed`} />
            <MetricTile label="Review pending" value={metrics.review?.pending} />
            <MetricTile label="Open cases" value={metrics.cases?.open} />
            <MetricTile label="Reports" value={metrics.reports?.generated} />
          </div>
          <div data-testid={T.cardIntegrationHealth} className="rounded-lg border border-ink-700/70 bg-ink-900/60 p-5">
            <div className="flex items-center gap-2.5 mb-4">
              <Plug className="size-4 text-steel-300" />
              <h2 className="text-sm font-semibold text-white uppercase tracking-wider">Integration health (CROMS &amp; Maintenance)</h2>
              {(metrics.integration?.idempotencyConflicts > 0 || metrics.security?.tenantScopeViolations > 0) && (
                <AlertTriangle className="size-4 text-amber400" />
              )}
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
              <IntegStat label="CROMS check-outs" value={metrics.integration?.cromsCheckOuts} />
              <IntegStat label="CROMS check-ins" value={metrics.integration?.cromsCheckIns} />
              <IntegStat label="Handoffs sent" value={metrics.integration?.maintenanceHandoffsSent} />
              <IntegStat label="Callbacks received" value={metrics.integration?.maintenanceCallbacksReceived} />
              <IntegStat label="Handoffs rejected" value={metrics.integration?.maintenanceHandoffsRejected} warn={metrics.integration?.maintenanceHandoffsRejected > 0} />
              <IntegStat label="Idempotency conflicts" value={metrics.integration?.idempotencyConflicts} warn={metrics.integration?.idempotencyConflicts > 0} />
            </div>
            <div className="mt-4 pt-3 border-t border-ink-700/60 flex flex-wrap gap-6">
              <IntegStat label="Tenant-scope violations" value={metrics.security?.tenantScopeViolations} warn={metrics.security?.tenantScopeViolations > 0} />
              <IntegStat label="Unauthorized attempts" value={metrics.security?.unauthorizedAttempts} warn={metrics.security?.unauthorizedAttempts > 0} />
            </div>
          </div>
        </section>
      )}

      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mb-10">
        <HealthCard
          testId={T.cardHealthService}
          icon={Activity}
          label="API service"
          healthy={!!version}
          hint={version ? `${version.service} v${version.version}` : "checking…"}
        />
        <HealthCard
          testId={T.cardHealthMongo}
          icon={Database}
          label="MongoDB"
          healthy={!!deps?.mongo?.healthy}
          hint="connection probe"
        />
        <HealthCard
          testId={T.cardHealthAi}
          icon={Cpu}
          label="AI service"
          healthy={!!deps?.ai_service?.healthy}
          hint={deps?.ai_service?.mode || "—"}
        />
        <HealthCard
          testId={T.cardHealthStorage}
          icon={HardDrive}
          label="Object storage"
          healthy={!!deps?.object_storage?.healthy}
          hint={deps?.object_storage?.mode || "—"}
        />
      </section>

      <section className="grid grid-cols-1 lg:grid-cols-2 gap-3">
        <div
          data-testid={T.cardScopeBoundary}
          className="rounded-lg border border-ink-700/70 bg-ink-900/60 p-6"
        >
          <div className="flex items-center gap-2.5 mb-4">
            <Lock className="size-4 text-steel-300" />
            <h2 className="text-sm font-semibold text-white uppercase tracking-wider">
              Scope Boundary (DI-0031)
            </h2>
          </div>
          <ul className="text-sm text-steel-200 space-y-2.5">
            <li className="flex gap-2">
              <span className="text-emerald-400 mt-0.5">●</span>
              <div>
                <span className="font-medium text-white">Damage Intelligence owns:</span>{" "}
                inspection evidence, AI findings (advisory), comparison results,
                review decisions, damage cases, evidence packages, damage reports.
              </div>
            </li>
            <li className="flex gap-2">
              <span className="text-amber400 mt-0.5">●</span>
              <div>
                <span className="font-medium text-white">CROMS owns:</span>{" "}
                rental agreement, rental closure, final customer charge.
              </div>
            </li>
            <li className="flex gap-2">
              <span className="text-amber400 mt-0.5">●</span>
              <div>
                <span className="font-medium text-white">GCU365Maintenance owns:</span>{" "}
                work orders, repair execution, actual repair cost.
              </div>
            </li>
          </ul>
        </div>

        <div
          data-testid={T.cardImplementationOrder}
          className="rounded-lg border border-ink-700/70 bg-ink-900/60 p-6"
        >
          <div className="flex items-center gap-2.5 mb-4">
            <GitBranch className="size-4 text-steel-300" />
            <h2 className="text-sm font-semibold text-white uppercase tracking-wider">
              Implementation Order
            </h2>
          </div>
          <ol className="space-y-2">
            {SPRINTS.map((s) => (
              <li key={s.id} className="flex items-center gap-3">
                <span className="size-1.5 rounded-full bg-steel-400" />
                <span className="font-mono text-[11px] text-steel-400 w-20 shrink-0">
                  {s.id}
                </span>
                <span className="text-sm text-steel-100 flex-1">{s.label}</span>
                <span
                  className={`text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded ${
                    s.status === "in-progress"
                      ? "bg-amber400/15 text-amber400 border border-amber400/30"
                      : s.status === "done"
                      ? "bg-emerald-400/10 text-emerald-400 border border-emerald-400/30"
                      : "bg-ink-800 text-steel-400 border border-ink-700"
                  }`}
                >
                  {s.status}
                </span>
              </li>
            ))}
          </ol>
        </div>
      </section>
    </div>
  );
}
