/*
 * Repository Traceability:
 * - Source Document: DI-0034 (Standard Headers — Authorization Bearer, X-Tenant-Id,
 *   X-Correlation-Id; Standard Response Envelope; Standard Error Codes).
 * - Purpose: Axios instance that attaches auth + tenant + correlation headers and
 *   surfaces the standard error envelope.
 */
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API_BASE = `${BACKEND_URL}/api/v1/damage-intelligence`;

const TOKEN_KEY = "di.accessToken";
const REFRESH_KEY = "di.refreshToken";
const TENANT_KEY = "di.tenantId";
const USER_KEY = "di.user";

export const tokenStore = {
  get: () => localStorage.getItem(TOKEN_KEY),
  getRefresh: () => localStorage.getItem(REFRESH_KEY),
  getTenant: () => localStorage.getItem(TENANT_KEY),
  getUser: () => {
    try {
      const raw = localStorage.getItem(USER_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  },
  set: ({ accessToken, refreshToken, tenantId, user }) => {
    if (accessToken) localStorage.setItem(TOKEN_KEY, accessToken);
    if (refreshToken) localStorage.setItem(REFRESH_KEY, refreshToken);
    if (tenantId) localStorage.setItem(TENANT_KEY, tenantId);
    if (user) localStorage.setItem(USER_KEY, JSON.stringify(user));
  },
  clear: () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
    localStorage.removeItem(TENANT_KEY);
    localStorage.removeItem(USER_KEY);
  },
};

function newCorrelationId() {
  const bytes = new Uint8Array(8);
  (window.crypto || window.msCrypto).getRandomValues(bytes);
  return (
    "CORR-WEB-" +
    Array.from(bytes)
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("")
      .toUpperCase()
  );
}

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
});

api.interceptors.request.use((config) => {
  const token = tokenStore.get();
  const tenant = tokenStore.getTenant();
  config.headers = config.headers || {};
  if (token) config.headers["Authorization"] = `Bearer ${token}`;
  if (tenant) config.headers["X-Tenant-Id"] = tenant;
  if (!config.headers["X-Correlation-Id"]) {
    config.headers["X-Correlation-Id"] = newCorrelationId();
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error?.response?.status === 401) {
      tokenStore.clear();
      if (window.location.pathname !== "/login") {
        window.location.replace("/login");
      }
    }
    return Promise.reject(error);
  }
);

export function envelopeError(err, fallback = "Something went wrong.") {
  const data = err?.response?.data;
  if (data && Array.isArray(data.errors) && data.errors.length > 0) {
    const e = data.errors[0];
    if (e && typeof e.message === "string") return e.message;
    if (e && typeof e.code === "string") return e.code;
  }
  if (typeof err?.message === "string") return err.message;
  return fallback;
}
