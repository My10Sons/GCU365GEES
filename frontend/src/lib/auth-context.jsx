/*
 * Repository Traceability:
 * - Source Document: DI-0034 (Authorization Bearer), DI-SPRINT-00 (Identity Setup).
 * - Purpose: Auth context, login/logout, current principal.
 */
import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { api, envelopeError, tokenStore } from "./api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [principal, setPrincipal] = useState(tokenStore.getUser());
  const [status, setStatus] = useState(tokenStore.get() ? "checking" : "anonymous");

  const refreshMe = useCallback(async () => {
    try {
      const { data } = await api.get("/auth/me");
      setPrincipal(data.data);
      tokenStore.set({ user: data.data, tenantId: data.data.tenantId });
      setStatus("authenticated");
    } catch (e) {
      tokenStore.clear();
      setPrincipal(null);
      setStatus("anonymous");
    }
  }, []);

  useEffect(() => {
    if (tokenStore.get()) {
      refreshMe();
    }
  }, [refreshMe]);

  const login = useCallback(async (email, password) => {
    const { data } = await api.post("/auth/login", { email, password });
    const payload = data.data;
    tokenStore.set({
      accessToken: payload.accessToken,
      refreshToken: payload.refreshToken,
      tenantId: payload.user.tenantId,
      user: payload.user,
    });
    setPrincipal(payload.user);
    setStatus("authenticated");
    return payload.user;
  }, []);

  const logout = useCallback(async () => {
    try {
      await api.post("/auth/logout");
    } catch {
      /* swallow */
    }
    tokenStore.clear();
    setPrincipal(null);
    setStatus("anonymous");
  }, []);

  const has = useCallback(
    (perm) => Array.isArray(principal?.permissions) && principal.permissions.includes(perm),
    [principal]
  );

  const value = useMemo(
    () => ({ principal, status, login, logout, refreshMe, has, envelopeError }),
    [principal, status, login, logout, refreshMe, has]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside <AuthProvider>");
  return ctx;
}
