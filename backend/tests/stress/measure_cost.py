"""
Track B cost measurement (DI-0043). Runs a fixed batch of single-angle analyses and reports the
EXACT tokens consumed per model (from the analyze-section tokenUsage). The user reads the Universal
Key balance before/after; effective rate = credits_delta / (tokens/1000).

analyze-section does NOT persist cases or audit rows, so this does not pollute tenant data.
Fast uses a NO-DAMAGE pair so no auto-escalation (pure Flash). Thorough forces Pro.
"""
import argparse
import asyncio
import os
import time

import httpx

BASE = os.environ.get("STRESS_BASE_URL", "https://damage-cases.preview.emergentagent.com")
API = f"{BASE}/api/v1/damage-intelligence"
EMAIL, PASSWORD, TENANT = "admin@riyadah.tech", "DamageAdmin#2026", "TENANT-000001"
IMG = os.path.dirname(__file__)
BEFORE, AFTER = os.path.join(IMG, "before_1.jpg"), os.path.join(IMG, "after_1.jpg")  # no-damage pair


async def login(c):
    r = await c.post(f"{API}/auth/login", json={"email": EMAIL, "password": PASSWORD})
    d = r.json()["data"]
    return d.get("accessToken") or d.get("token")


async def run_block(c, h, mode, n, concurrency):
    sem = asyncio.Semaphore(concurrency)
    stats = {"calls": 0, "tokens": 0, "input": 0, "output": 0, "escalated": 0, "fail": 0}
    with open(BEFORE, "rb") as f:
        bbytes = f.read()
    with open(AFTER, "rb") as f:
        abytes = f.read()

    async def one(i):
        async with sem:
            files = {
                "before": (f"b{i}.jpg", bbytes, "image/jpeg"),
                "after": (f"a{i}.jpg", abytes, "image/jpeg"),
            }
            data = {"kind": "EXTERIOR", "angle": "FRONT", "mode": mode}
            try:
                r = await c.post(f"{API}/trip-inspection/analyze-section", headers=h, data=data, files=files)
                if r.status_code == 200:
                    s = r.json()["data"]
                    u = s.get("tokenUsage") or {}
                    stats["calls"] += 1
                    stats["tokens"] += u.get("totalTokens", 0) or 0
                    stats["input"] += u.get("inputTokens", 0) or 0
                    stats["output"] += u.get("outputTokens", 0) or 0
                    if s.get("escalated"):
                        stats["escalated"] += 1
                else:
                    stats["fail"] += 1
            except Exception:
                stats["fail"] += 1

    await asyncio.gather(*[one(i) for i in range(n)])
    return stats


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fast", type=int, default=30)
    ap.add_argument("--thorough", type=int, default=15)
    ap.add_argument("--concurrency", type=int, default=6)
    args = ap.parse_args()

    async with httpx.AsyncClient(timeout=300) as c:
        tok = await login(c)
        h = {"Authorization": f"Bearer {tok}", "X-Tenant-Id": TENANT}
        t0 = time.perf_counter()
        print(f"Target: {API}")
        fast = await run_block(c, h, "fast", args.fast, args.concurrency)
        print(f"FAST (Flash): calls={fast['calls']} fail={fast['fail']} escalated={fast['escalated']} "
              f"tokens={fast['tokens']} (in={fast['input']} out={fast['output']})")
        pro = await run_block(c, h, "thorough", args.thorough, args.concurrency)
        print(f"THOROUGH (Pro): calls={pro['calls']} fail={pro['fail']} "
              f"tokens={pro['tokens']} (in={pro['input']} out={pro['output']})")
        total = fast["tokens"] + pro["tokens"]
        print(f"\n=== TOTALS ===")
        print(f"Flash calls: {fast['calls']}  Flash tokens: {fast['tokens']}")
        print(f"Pro   calls: {pro['calls']}  Pro   tokens: {pro['tokens']}")
        print(f"GRAND TOTAL tokens consumed: {total}")
        print(f"wall: {time.perf_counter()-t0:.1f}s")


if __name__ == "__main__":
    asyncio.run(main())
