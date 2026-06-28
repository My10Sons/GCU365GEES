/*
 * Repository Traceability:
 * - Source Documents: DI-SPRINT-01 (Web Implementation — list/detail/status/evidence
 *   screens), DI-0034 (API paths + envelope).
 * - Purpose: Thin service layer wrapping the Sprint-01 endpoints with envelope handling.
 */
import { api, envelopeError } from "./api";

const unwrap = (resp) => resp.data?.data;

export const inspectionsApi = {
  list: async (params = {}) => {
    const { data } = await api.get("/inspection-sessions", { params });
    return data.data;
  },
  get: async (id) => {
    const { data } = await api.get(`/inspection-sessions/${id}`);
    return data.data;
  },
  create: async (payload) => {
    const { data } = await api.post("/inspection-sessions", payload);
    return data.data;
  },
  submit: async (id) => {
    const { data } = await api.post(`/inspection-sessions/${id}/submit`);
    return data.data;
  },
  patchStatus: async (id, payload) => {
    const { data } = await api.patch(`/inspection-sessions/${id}/status`, payload);
    return data.data;
  },
  uploadRequest: async (id, payload) => {
    const { data } = await api.post(
      `/inspection-sessions/${id}/images/upload-request`,
      payload
    );
    return data.data;
  },
  register: async (id, payload) => {
    const { data } = await api.post(`/inspection-sessions/${id}/images`, payload);
    return data.data;
  },
  listImages: async (id) => {
    const { data } = await api.get(`/inspection-sessions/${id}/images`);
    return data.data;
  },
  capturePositions: async () => {
    const { data } = await api.get("/reference/capture-positions");
    return data.data;
  },
};

export const evidenceApi = {
  accessLink: async (evidenceId, purpose, expiresInMinutes = 15) => {
    const { data } = await api.post(`/evidence/${evidenceId}/access-link`, {
      purpose,
      expiresInMinutes,
    });
    return data.data;
  },
};

export { envelopeError, unwrap };

// Build a full URL out of a relative signed link returned by the server.
export function absoluteUrl(relativeUrl) {
  if (!relativeUrl) return relativeUrl;
  if (/^https?:\/\//i.test(relativeUrl)) return relativeUrl;
  return `${process.env.REACT_APP_BACKEND_URL}${relativeUrl}`;
}
