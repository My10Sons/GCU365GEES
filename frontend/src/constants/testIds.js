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

  // Inspections list
  inspectionsRoot: "inspections-root",
  inspectionsRefresh: "inspections-refresh",
  inspectionsCreateBtn: "inspections-create-btn",
  inspectionsFilterStatus: "inspections-filter-status",
  inspectionsFilterType: "inspections-filter-type",
  inspectionsTable: "inspections-table",
  inspectionsRow: "inspections-row",
  inspectionsLink: "inspections-link",
  inspectionStatus: "inspection-status",
  inspectionsEmpty: "inspections-empty",
  inspectionsPrev: "inspections-prev",
  inspectionsNext: "inspections-next",

  // Create inspection modal
  createInspectionModal: "create-inspection-modal",
  createInspectionType: "create-inspection-type",
  createInspectionSource: "create-inspection-source",
  createInspectionVehicle: "create-inspection-vehicle",
  createInspectionRental: "create-inspection-rental",
  createInspectionBranch: "create-inspection-branch",
  createInspectionSubmit: "create-inspection-submit",
  createInspectionCancel: "create-inspection-cancel",
  createInspectionError: "create-inspection-error",

  // Inspection detail
  inspectionDetailRoot: "inspection-detail-root",
  inspectionDetailBack: "inspection-detail-back",
  inspectionDetailVehicle: "inspection-detail-vehicle",
  inspectionDetailStatus: "inspection-detail-status",
  inspectionDetailRefresh: "inspection-detail-refresh",
  inspectionDetailUpload: "inspection-detail-upload",
  inspectionDetailSubmit: "inspection-detail-submit",
  inspectionDetailCancel: "inspection-detail-cancel",
  inspectionDetailLoading: "inspection-detail-loading",
  inspectionDetailError: "inspection-detail-error",
  inspectionDetailNoImages: "inspection-detail-no-images",
  inspectionDetailImagesGrid: "inspection-detail-images-grid",
  inspectionImageCard: "inspection-image-card",
  inspectionImageAccess: "inspection-image-access",

  // Upload image modal
  uploadImageModal: "upload-image-modal",
  uploadImagePosition: "upload-image-position",
  uploadImageFile: "upload-image-file",
  uploadImageSubmit: "upload-image-submit",
  uploadImageError: "upload-image-error",
};
