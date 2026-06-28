/*
 * Repository Traceability:
 * - Source Documents: DI-SPRINT-00 (Web Setup — layout, navigation, dashboard
 *   placeholder, role-based menu visibility placeholder, scope boundary).
 */
import React from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import {
  LayoutDashboard,
  ClipboardList,
  ShieldCheck,
  FolderOpen,
  FileBarChart2,
  Settings2,
  LogOut,
  ShieldAlert,
} from "lucide-react";
import { useAuth } from "../lib/auth-context";
import { IntegrationAlertBanner } from "./IntegrationAlertBanner";
import { T } from "../constants/testIds";

const NAV = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, testId: T.sidebarDashboard, perm: null, end: true },
  { to: "/inspections", label: "Inspections", icon: ClipboardList, testId: T.sidebarInspections, perm: "di.inspections.read" },
  { to: "/review", label: "Review Queue", icon: ShieldCheck, testId: T.sidebarReview, perm: "di.review.read" },
  { to: "/cases", label: "Damage Cases", icon: FolderOpen, testId: T.sidebarCases, perm: "di.damagecases.read" },
  { to: "/reports", label: "Reports", icon: FileBarChart2, testId: T.sidebarReports, perm: "di.reports.read" },
  { to: "/admin", label: "Admin", icon: Settings2, testId: T.sidebarAdmin, perm: "di.configuration.manage" },
];

export default function Shell() {
  const { principal, has, logout } = useAuth();
  const navigate = useNavigate();

  const onLogout = async () => {
    await logout();
    navigate("/login", { replace: true });
  };

  return (
    <div
      data-testid={T.shellRoot}
      className="min-h-screen bg-ink-950 text-steel-100 flex"
    >
      {/* Sidebar */}
      <aside
        data-testid={T.sidebar}
        className="w-64 shrink-0 border-r border-ink-700/70 bg-ink-900 flex flex-col"
      >
        <div className="px-5 py-6 border-b border-ink-700/70 flex items-center gap-3">
          <div className="size-9 rounded-md bg-signal/20 border border-signal/40 flex items-center justify-center">
            <ShieldAlert className="size-5 text-signal" aria-hidden />
          </div>
          <div>
            <div className="text-xs uppercase tracking-[0.18em] text-steel-300">
              Damage Intelligence
            </div>
            <div className="text-[11px] text-steel-400 font-mono">
              v{process.env.REACT_APP_DI_VERSION || "0.1"} · Sprint 05
            </div>
          </div>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-1">
          {NAV.map(({ to, label, icon: Icon, testId, perm, end }) => {
            const enabled = !perm || has(perm);
            return (
              <NavLink
                key={to}
                to={to}
                end={end}
                data-testid={testId}
                onClick={(e) => {
                  if (!enabled) e.preventDefault();
                }}
                aria-disabled={!enabled}
                className={({ isActive }) =>
                  [
                    "group flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors",
                    isActive
                      ? "bg-ink-700/80 text-white border border-ink-600/60"
                      : "text-steel-300 hover:bg-ink-800",
                    !enabled && "opacity-40 cursor-not-allowed hover:bg-transparent",
                  ]
                    .filter(Boolean)
                    .join(" ")
                }
              >
                <Icon className="size-4 shrink-0" />
                <span className="flex-1">{label}</span>
                {!enabled && (
                  <span className="text-[10px] uppercase tracking-wider text-steel-400">
                    locked
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>

        <div className="px-4 py-4 border-t border-ink-700/70 text-[11px] text-steel-400 leading-relaxed">
          <div className="font-mono text-steel-300">DI-0031 boundary</div>
          <p>
            Damage Intelligence integrates with existing GCU365 CROMS and
            GCU365Maintenance — it does not replace them.
          </p>
        </div>
      </aside>

      {/* Main */}
      <div className="flex-1 flex flex-col min-w-0">
        <header
          data-testid={T.topbar}
          className="h-14 border-b border-ink-700/70 bg-ink-900/80 backdrop-blur flex items-center px-6 gap-4"
        >
          <div className="text-sm font-mono text-steel-300">
            /api/v1/damage-intelligence
          </div>
          <div className="flex-1" />
          <span
            data-testid={T.topbarTenant}
            className="px-2 py-1 rounded-md text-[11px] font-mono bg-ink-800 border border-ink-700 text-steel-200"
          >
            tenant: {principal?.tenantId || "—"}
          </span>
          <span
            data-testid={T.topbarUser}
            className="px-2 py-1 rounded-md text-[11px] font-mono bg-ink-800 border border-ink-700 text-steel-200"
            title={(principal?.roles || []).join(", ")}
          >
            {principal?.email} · {(principal?.roles || [])[0] || "—"}
          </span>
          <button
            data-testid={T.logoutBtn}
            onClick={onLogout}
            className="px-3 py-1.5 rounded-md text-xs font-medium text-steel-200 bg-ink-800 border border-ink-700 hover:bg-ink-700/80 hover:text-white transition-colors flex items-center gap-1.5"
          >
            <LogOut className="size-3.5" />
            Sign out
          </button>
        </header>

        <main className="flex-1 overflow-auto bg-grid">
          <IntegrationAlertBanner />
          <Outlet />
        </main>
      </div>
    </div>
  );
}
