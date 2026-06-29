"""
Stress / load harness for Damage Intelligence (PREVIEW backend only).

Phases:
  1. Auth login throughput (high concurrency, short).
  2. Read-endpoint mix under high concurrency (cases, inspections, metrics, branding, policy).
  3. AI analyze endpoint under modest concurrency (real Gemini, slow + costs budget).

Reports per-phase + per-endpoint latency percentiles, throughput, and error breakdown.
"""
import argparse
import asyncio
import os
import statistics
import time
from collections import defaultdict

import httpx

BASE = os.environ.get("STRESS_BASE_URL", "https://damage-cases.preview.emergentagent.com")
API = f"{BASE}/api/v1/damage-intelligence"
EMAIL = os.environ.get("STRESS_EMAIL", "admin@riyadah.tech")
PASSWORD = os.environ.get("STRESS_PASSWORD", "DamageAdmin#2026")
TENANT = os.environ.get("STRESS_TENANT", "TENANT-000001")
IMG_DIR = os.path.join(os.path.dirname(__file__))

results = defaultdict(list)   # label -> list of (ok: bool, status: int, latency_ms: float, err)
lock = asyncio.Lock()


async def record(label, ok, status, latency_ms, err=None):
    async with lock:
        results[label].append((ok, status, latency_ms, err))


async def login(client):
    r = await client.post(f"{API}/auth/login", json={"email": EMAIL, "password": PASSWORD})
    r.raise_for_status()
    data = r.json()["data"]
    return data.get("accessToken") or data.get("token")


def headers(token):
    return {"Authorization": f"Bearer {token}", "X-Tenant-Id": TENANT}


async def timed(label, coro_factory):
    start = time.perf_counter()
    try:
        r = await coro_factory()
        ms = (time.perf_counter() - start) * 1000
        ok = 200 <= r.status_code < 300
        await record(label, ok, r.status_code, ms, None if ok else r.text[:120])
    except Exception as e:
        ms = (time.perf_counter() - start) * 1000
        await record(label, False, 0, ms, f"{type(e).__name__}:{e}"[:140])


# ---------- Phase 1: auth login load ----------
async def phase_auth(n, concurrency):
    sem = asyncio.Semaphore(concurrency)
    async with httpx.AsyncClient(timeout=30) as client:
        async def one():
            async with sem:
                await timed("POST /auth/login", lambda: client.post(
                    f"{API}/auth/login", json={"email": EMAIL, "password": PASSWORD}))
        await asyncio.gather(*[one() for _ in range(n)])


# ---------- Phase 2: read mix ----------
async def phase_reads(n, concurrency):
    sem = asyncio.Semaphore(concurrency)
    async with httpx.AsyncClient(timeout=30) as client:
        token = await login(client)
        h = headers(token)
        endpoints = [
            ("GET /monitoring/metrics", lambda: client.get(f"{API}/monitoring/metrics", headers=h)),
            ("GET /damage-cases", lambda: client.get(f"{API}/damage-cases?pageSize=20", headers=h)),
            ("GET /inspection-sessions", lambda: client.get(f"{API}/inspection-sessions?pageSize=20", headers=h)),
            ("GET /tenant/branding", lambda: client.get(f"{API}/tenant/branding", headers=h)),
            ("GET /tenant/policy", lambda: client.get(f"{API}/tenant/policy", headers=h)),
        ]

        async def one(i):
            label, factory = endpoints[i % len(endpoints)]
            async with sem:
                await timed(label, factory)
        await asyncio.gather(*[one(i) for i in range(n)])


# ---------- Phase 3: AI analyze load ----------
async def phase_ai(n, concurrency, timeout):
    sem = asyncio.Semaphore(concurrency)
    pairs = [(os.path.join(IMG_DIR, f"before_{i}.jpg"), os.path.join(IMG_DIR, f"after_{i}.jpg"))
             for i in range(5)]
    async with httpx.AsyncClient(timeout=timeout) as client:
        token = await login(client)
        h = headers(token)

        async def one(i):
            before, after = pairs[i % len(pairs)]
            async with sem:
                with open(before, "rb") as bf, open(after, "rb") as af:
                    files = {
                        "ext_front_before": (f"b{i}.jpg", bf.read(), "image/jpeg"),
                        "ext_front_after": (f"a{i}.jpg", af.read(), "image/jpeg"),
                    }
                await timed("POST /trip-inspection/analyze", lambda: client.post(
                    f"{API}/trip-inspection/analyze", headers=h, files=files))
        await asyncio.gather(*[one(i) for i in range(n)])


def pct(values, p):
    if not values:
        return 0
    values = sorted(values)
    k = max(0, min(len(values) - 1, int(round((p / 100) * (len(values) - 1)))))
    return values[k]


def report(phase_name, wall_seconds):
    print(f"\n===== {phase_name} (wall {wall_seconds:.1f}s) =====")
    for label, rows in results.items():
        if not rows:
            continue
        lats = [r[2] for r in rows]
        oks = sum(1 for r in rows if r[0])
        errs = defaultdict(int)
        codes = defaultdict(int)
        for ok, status, ms, err in rows:
            codes[status] += 1
            if not ok:
                errs[(err or f"HTTP{status}")[:60]] += 1
        print(f"\n  {label}")
        print(f"    requests={len(rows)} ok={oks} fail={len(rows)-oks} "
              f"({100*oks/len(rows):.0f}% ok)")
        print(f"    latency ms: min={min(lats):.0f} p50={pct(lats,50):.0f} "
              f"p95={pct(lats,95):.0f} p99={pct(lats,99):.0f} max={max(lats):.0f} "
              f"avg={statistics.mean(lats):.0f}")
        print(f"    status codes: {dict(codes)}")
        if errs:
            print(f"    errors: {dict(errs)}")
    results.clear()


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["auth", "reads", "ai", "all"], default="all")
    ap.add_argument("--auth-n", type=int, default=200)
    ap.add_argument("--auth-c", type=int, default=25)
    ap.add_argument("--reads-n", type=int, default=500)
    ap.add_argument("--reads-c", type=int, default=40)
    ap.add_argument("--ai-n", type=int, default=20)
    ap.add_argument("--ai-c", type=int, default=5)
    ap.add_argument("--ai-timeout", type=float, default=240)
    args = ap.parse_args()

    print(f"Target: {API}  tenant={TENANT}")

    if args.phase in ("auth", "all"):
        t = time.perf_counter()
        await phase_auth(args.auth_n, args.auth_c)
        report(f"PHASE 1 — AUTH LOGIN  (n={args.auth_n}, concurrency={args.auth_c})",
               time.perf_counter() - t)

    if args.phase in ("reads", "all"):
        t = time.perf_counter()
        await phase_reads(args.reads_n, args.reads_c)
        report(f"PHASE 2 — READ MIX  (n={args.reads_n}, concurrency={args.reads_c})",
               time.perf_counter() - t)

    if args.phase in ("ai", "all"):
        t = time.perf_counter()
        await phase_ai(args.ai_n, args.ai_c, args.ai_timeout)
        report(f"PHASE 3 — AI ANALYZE  (n={args.ai_n}, concurrency={args.ai_c})",
               time.perf_counter() - t)


if __name__ == "__main__":
    asyncio.run(main())
