/*
 * Repository Traceability:
 * - Source Documents: DI-SPRINT-00 (Web Setup — shell + navigation), DI-0034
 *   (POST /auth/login → token storage), DI-0031 (scope boundary).
 */
import React from "react";
import { BrowserRouter, Routes, Route, Navigate, useLocation } from "react-router-dom";
import { AuthProvider, useAuth } from "./lib/auth-context";
import Login from "./pages/Login";
import Shell from "./components/Shell";
import Dashboard from "./pages/Dashboard";
import Placeholder from "./pages/Placeholder";
import Inspections from "./pages/Inspections";
import InspectionDetail from "./pages/InspectionDetail";

function Protected({ children }) {
  const { status, principal } = useAuth();
  const location = useLocation();
  if (status === "checking") {
    return (
      <div className="min-h-screen bg-ink-950 flex items-center justify-center text-steel-300 text-sm">
        Verifying session…
      </div>
    );
  }
  if (status === "anonymous" || !principal) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }
  return children;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          <Protected>
            <Shell />
          </Protected>
        }
      >
        <Route index element={<Dashboard />} />
        <Route
          path="inspections"
          element={<Inspections />}
        />
        <Route
          path="inspections/:id"
          element={<InspectionDetail />}
        />
        <Route
          path="review"
          element={
            <Placeholder
              title="Review Queue"
              sprint="Sprint 03 — TASK-04"
              doc="DI-0006, DI-0011, DI-0019, DI-0034"
              summary="Human review of AI findings, review decisions, additional-evidence requests, and damage-case linkage — delivered in Sprint 03."
            />
          }
        />
        <Route
          path="cases"
          element={
            <Placeholder
              title="Damage Cases"
              sprint="Sprint 03 — TASK-04"
              doc="DI-0011, DI-0012, DI-0034"
              summary="Damage case context: status history, evidence/finding/comparison links. AI is advisory; final liability and customer charge remain with CROMS/Finance."
            />
          }
        />
        <Route
          path="reports"
          element={
            <Placeholder
              title="Reports & Evidence Packages"
              sprint="Sprint 05 — TASK-06"
              doc="DI-0016, DI-0034"
              summary="Inspection Summary, Damage Detection, Damage Comparison, Damage Case, Rental Damage Summary, Maintenance Handoff, and Evidence Package reports with controlled access links."
            />
          }
        />
        <Route
          path="admin"
          element={
            <Placeholder
              title="Configuration & Administration"
              sprint="Sprint 02 / Sprint 05"
              doc="DI-0024, DI-0034"
              summary="AI threshold tuning, taxonomy management, role assignments, and audit-record review — restricted to DI_Admin and DI_Auditor."
            />
          }
        />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}
