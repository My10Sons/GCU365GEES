/*
 * Repository Traceability:
 * - Source Documents: DI-SPRINT-03 (Comparison, Review Queue, Damage Case Web screens),
 *   DI-0037 (Per-Vehicle Evidence Strip), DI-0034 (API paths + envelope).
 * - Purpose: Thin service layer wrapping the Sprint-03 endpoints with envelope handling.
 */
import { api } from "./api";

export const comparisonApi = {
  request: async (sessionId, body = {}) => {
    const { data } = await api.post(`/inspection-sessions/${sessionId}/comparison`, body);
    return data.data;
  },
  list: async (sessionId) => {
    const { data } = await api.get(`/inspection-sessions/${sessionId}/comparisons`);
    return data.data;
  },
  get: async (comparisonId) => {
    const { data } = await api.get(`/comparisons/${comparisonId}`);
    return data.data;
  },
  perVehicleStrip: async (sessionId, limit = 12) => {
    const { data } = await api.get(`/inspection-sessions/${sessionId}/per-vehicle-strip`, {
      params: { limit },
    });
    return data.data;
  },
};

export const reviewApi = {
  queue: async (params = {}) => {
    const { data } = await api.get("/review-queue", { params });
    return data.data;
  },
  get: async (reviewItemId) => {
    const { data } = await api.get(`/review-items/${reviewItemId}`);
    return data.data;
  },
  decide: async (reviewItemId, body) => {
    const { data } = await api.post(`/review-items/${reviewItemId}/decision`, body);
    return data.data;
  },
  requestEvidence: async (reviewItemId, body) => {
    const { data } = await api.post(`/review-items/${reviewItemId}/additional-evidence-request`, body);
    return data.data;
  },
};

export const casesApi = {
  list: async (params = {}) => {
    const { data } = await api.get("/damage-cases", { params });
    return data.data;
  },
  get: async (caseId) => {
    const { data } = await api.get(`/damage-cases/${caseId}`);
    return data.data;
  },
  create: async (body) => {
    const { data } = await api.post("/damage-cases", body);
    return data.data;
  },
  updateStatus: async (caseId, body) => {
    const { data } = await api.patch(`/damage-cases/${caseId}/status`, body);
    return data.data;
  },
  linkEvidence: async (caseId, linkedId) => {
    const { data } = await api.post(`/damage-cases/${caseId}/link-evidence`, { linkedId });
    return data.data;
  },
  linkFinding: async (caseId, linkedId) => {
    const { data } = await api.post(`/damage-cases/${caseId}/link-finding`, { linkedId });
    return data.data;
  },
  linkComparison: async (caseId, linkedId) => {
    const { data } = await api.post(`/damage-cases/${caseId}/link-comparison`, { linkedId });
    return data.data;
  },
};
