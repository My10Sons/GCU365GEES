/*
 * Repository Traceability:
 * - Source Documents: DI-0034 (POST /auth/login), DI-SPRINT-00 (Web auth placeholder).
 */
import React, { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { ShieldAlert, Loader2 } from "lucide-react";
import { useAuth } from "../lib/auth-context";
import { envelopeError } from "../lib/api";
import { T } from "../constants/testIds";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const onSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await login(email.trim(), password);
      const redirect = location.state?.from?.pathname || "/";
      navigate(redirect, { replace: true });
    } catch (err) {
      setError(envelopeError(err, "Sign-in failed."));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-ink-950 bg-grid relative overflow-hidden">
      {/* radial accent */}
      <div
        aria-hidden
        className="absolute -top-32 -left-32 size-[420px] rounded-full opacity-[0.28] blur-3xl"
        style={{
          background:
            "radial-gradient(closest-side, rgba(230,57,70,0.45), rgba(230,57,70,0))",
        }}
      />
      <div
        aria-hidden
        className="absolute -bottom-32 -right-32 size-[460px] rounded-full opacity-20 blur-3xl"
        style={{
          background:
            "radial-gradient(closest-side, rgba(58,66,88,0.7), rgba(58,66,88,0))",
        }}
      />

      <div className="relative min-h-screen flex items-center justify-center px-4">
        <div className="w-full max-w-md">
          <div className="flex items-center gap-3 mb-7">
            <div className="size-10 rounded-md bg-signal/20 border border-signal/40 flex items-center justify-center">
              <ShieldAlert className="size-5 text-signal" aria-hidden />
            </div>
            <div>
              <div className="text-[11px] uppercase tracking-[0.22em] text-steel-300">
                GCU365
              </div>
              <h1 className="text-xl font-semibold text-white">
                Damage Intelligence
              </h1>
            </div>
          </div>

          <div className="glass rounded-xl p-7 shadow-panel">
            <h2 className="text-lg font-medium text-white">Sign in</h2>
            <p className="text-sm text-steel-300 mt-1 mb-6">
              Operator console — sign in to continue.
            </p>

            <form onSubmit={onSubmit} className="space-y-4" noValidate>
              <div>
                <label className="block text-xs font-medium uppercase tracking-wider text-steel-300 mb-1.5">
                  Email
                </label>
                <input
                  data-testid={T.loginEmail}
                  type="email"
                  autoComplete="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-ink-850 border border-ink-700 focus:border-signal/60 focus:ring-2 focus:ring-signal/20 outline-none rounded-md px-3 py-2.5 text-sm text-white placeholder:text-steel-400 transition-colors"
                  placeholder="admin@riyadah.tech"
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-medium uppercase tracking-wider text-steel-300 mb-1.5">
                  Password
                </label>
                <input
                  data-testid={T.loginPassword}
                  type="password"
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-ink-850 border border-ink-700 focus:border-signal/60 focus:ring-2 focus:ring-signal/20 outline-none rounded-md px-3 py-2.5 text-sm text-white placeholder:text-steel-400 transition-colors"
                  required
                />
              </div>

              {error && (
                <div
                  data-testid={T.loginError}
                  role="alert"
                  className="text-sm text-signal-soft bg-signal/10 border border-signal/30 rounded-md px-3 py-2"
                >
                  {error}
                </div>
              )}

              <button
                data-testid={T.loginSubmit}
                type="submit"
                disabled={submitting}
                className="w-full bg-signal hover:bg-signal/90 disabled:opacity-50 disabled:cursor-wait text-white text-sm font-medium rounded-md px-3 py-2.5 transition-colors flex items-center justify-center gap-2"
              >
                {submitting && <Loader2 className="size-4 animate-spin" />}
                {submitting ? "Signing in…" : "Sign in"}
              </button>
            </form>

            <div className="mt-6 pt-5 border-t border-ink-700/60 text-[11px] leading-relaxed text-steel-400 font-mono">
              tenant: TENANT-000001 · base: /api/v1/damage-intelligence
            </div>
          </div>

          <p className="text-[11px] text-steel-400 text-center mt-5 max-w-sm mx-auto leading-relaxed">
            AI outputs are advisory. Damage Intelligence does not own rental
            closure, work order execution, or final customer charge.
          </p>
        </div>
      </div>
    </div>
  );
}
