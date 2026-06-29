# DI-0042 — Production Concurrency & Scaling Guidance

**Status:** Operational guidance (ops/governance)
**Owner:** Damage Intelligence
**Related:** DI-0014 (Security), DI-0023 (Operational Monitoring), DI-0026 (Deployment),
DI-0027 (Operational Runbook). Source: stress-test findings (preview), 2026-06-29.

---

## 1. Background

A preview stress test showed three concurrency weaknesses, all rooted in **a single backend
worker** (`uvicorn server:app --workers 1 --reload`):

| Symptom | Cause |
|---------|-------|
| Login p50 ~5.7s @ 25 concurrent (100% success, but slow) | bcrypt is CPU-bound and blocked the single async event loop |
| Read endpoints: p50 ~0.35s but p95/p99 = 20–30s + ~5% ConnectTimeouts @ 40 concurrent | single worker connection-acceptance saturation |
| AI analyze: stable (no failures, ~12–13s p50) | I/O-bound (awaits Gemini), so it parallelizes fine even on one worker |

## 2. Fixes

### 2.1 Code fix (shipped) — non-blocking bcrypt
`application/security/password.py` now exposes `verify_password_async` / `hash_password_async`
that run bcrypt via `asyncio.to_thread`, and the login route awaits the async verify. This frees
the event loop during the (intentionally slow) hash, so concurrent logins and other requests are
no longer serialized behind one another **even on a single worker**. Hash scheme/format unchanged
— existing seeded `$2b$` hashes still verify.

### 2.2 Production config — run multiple workers (infra)
`--workers 1 --reload` is a **development** setting. For production:

```
# Recommended production launch (no --reload; multiple workers)
gunicorn server:app \
  -k uvicorn.workers.UvicornWorker \
  --workers $((2 * $(nproc) + 1)) \
  --bind 0.0.0.0:8001 \
  --timeout 120 \
  --graceful-timeout 30 \
  --max-requests 2000 --max-requests-jitter 200
```

- **Workers:** start at `2 × CPU + 1` (e.g. 17 on an 8-core box). Each worker is an independent
  process, so CPU-bound bcrypt on one worker no longer stalls all traffic.
- **Drop `--reload`:** it adds a file-watcher and a reloader process — never for production.
- **`--max-requests`:** periodic worker recycling guards against any slow memory growth.
- **Timeout 120s:** AI analyze calls take ~12–20s; keep generous headroom.

> NOTE: On the Emergent platform the production deployment's worker count and autoscaling are
> managed by the hosting layer, not by `/app` supervisor config. **Confirm the production worker
> count with Emergent Support** and request scaling if login/read concurrency is expected to be high.

## 3. Other hardening (recommended, not yet done)

- **bcrypt cost factor:** keep at the library default (currently 12 rounds). Do not raise without
  load-testing — higher rounds = slower logins. The async offload mitigates latency but not CPU cost.
- **Rate-limit `/auth/login`** at the edge (per-IP) to blunt login storms; brute-force lockout
  already exists per `{ip}:{email}` (5 attempts / 15 min).
- **DB connection pool:** ensure motor's pool (`maxPoolSize`) is sized for `workers × expected
  concurrency`.
- **Horizontal scale:** the app is stateless (bearer JWT, no server sessions, signed storage
  links), so it scales horizontally behind a load balancer without sticky sessions.

## 4. Expected impact

With non-blocking bcrypt (single worker) + multiple workers in production:
- Login latency under concurrency should drop from seconds back toward sub-second.
- Read-endpoint ConnectTimeouts under burst load should disappear.
- AI analyze latency is unaffected (it is Gemini-bound) — addressed separately by model tiering
  + per-section streaming.
