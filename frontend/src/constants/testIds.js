/*
 * Repository Traceability:
 * - Source Document: Project-wide convention — every interactive element MUST have a
 *   stable data-testid.
 */

export const T = {
  // Auth
  loginEmail: "login-email-input",
  loginPassword: "login-password-input",
  loginSubmit: "login-submit-button",
  loginError: "login-error-text",
  logoutBtn: "topbar-logout-button",

  // Shell
  shellRoot: "app-shell-root",
  sidebar: "sidebar-nav",
  sidebarDashboard: "sidebar-link-dashboard",
  sidebarInspections: "sidebar-link-inspections",
  sidebarReview: "sidebar-link-review",
  sidebarCases: "sidebar-link-cases",
  sidebarReports: "sidebar-link-reports",
  sidebarAdmin: "sidebar-link-admin",
  topbar: "app-topbar",
  topbarTenant: "topbar-tenant-chip",
  topbarUser: "topbar-user-chip",

  // Dashboard
  dashboardRoot: "dashboard-root",
  cardHealthService: "card-health-service",
  cardHealthMongo: "card-health-mongo",
  cardHealthAi: "card-health-ai",
  cardHealthStorage: "card-health-storage",
  cardScopeBoundary: "card-scope-boundary",
  cardImplementationOrder: "card-implementation-order",

  // Placeholder pages
  placeholderRoot: "placeholder-root",
};
