"""
Repository Traceability:
- Purpose: Accuracy validation harness. Tenants store benchmark cases (before/after photo
  pairs + expected findings as ground truth). A run replays every case through the real
  Trip Inspection analysis pipeline and scores recall, so every prompt/model change can be
  regression-checked against known issues before it reaches production.
"""
from __future__ import annotations

import asyncio
import shutil
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from api.middleware.safe_errors import DomainError
from application.services import trip_inspection_service
from domain.enums.error_codes import ErrorCode
from infrastructure.db.mongo import get_db
from infrastructure.storage.local_storage import storage_root

_VALID_ANGLES = {"FRONT", "REAR", "LEFT", "RIGHT", "ROOF"}
_VALID_CATEGORIES = set(trip_inspection_service.EXTERIOR_CATEGORIES) | {"INTERIOR"}


def _bench_dir(tenant_id: str, case_id: str) -> Path:
    return storage_root() / "tenants" / tenant_id / "damage-intelligence" / "benchmark" / case_id


def _norm_expected(expected) -> list[dict]:
    if not isinstance(expected, list) or not expected:
        raise DomainError(ErrorCode.VALIDATION_ERROR,
                          "expected must be a non-empty list of findings.", 400, "expected")
    out = []
    for e in expected[:20]:
        if not isinstance(e, dict):
            continue
        cat = str(e.get("category") or "").upper()
        if cat not in _VALID_CATEGORIES:
            raise DomainError(ErrorCode.VALIDATION_ERROR,
                              f"Unknown expected category '{cat}'.", 400, "expected")
        kws = e.get("keywords") or []
        if isinstance(kws, str):
            kws = [k.strip() for k in kws.split(",") if k.strip()]
        out.append({
            "category": cat,
            "keywords": [str(k).lower()[:40] for k in kws][:10],
            "note": (e.get("note") if isinstance(e.get("note"), str) else "")[:160] or None,
            "optional": bool(e.get("optional")),
        })
    if not out:
        raise DomainError(ErrorCode.VALIDATION_ERROR, "No valid expected findings.", 400, "expected")
    return out


async def create_case(*, principal: dict, name: str, angle: str, expected,
                      before: tuple, after: tuple) -> dict:
    angle = (angle or "REAR").upper()
    if angle not in _VALID_ANGLES:
        raise DomainError(ErrorCode.VALIDATION_ERROR, "Invalid angle.", 400, "angle")
    exp = _norm_expected(expected)
    case_id = uuid.uuid4().hex
    d = _bench_dir(principal["tenantId"], case_id)
    d.mkdir(parents=True, exist_ok=True)
    for which, (content, mime) in (("before", before), ("after", after)):
        ext = "png" if "png" in (mime or "") else "jpg"
        (d / f"{which}.{ext}").write_bytes(content)
    doc = {
        "caseId": case_id, "tenantId": principal["tenantId"],
        "name": (name or "Untitled case").strip()[:120], "angle": angle,
        "expected": exp, "createdAt": datetime.now(timezone.utc),
    }
    await get_db().di_benchmark_cases.insert_one(dict(doc))
    doc["createdAt"] = doc["createdAt"].isoformat()
    return doc


async def list_cases(principal: dict) -> list[dict]:
    cur = get_db().di_benchmark_cases.find(
        {"tenantId": principal["tenantId"]}).sort("createdAt", -1).limit(50)
    out = []
    async for d in cur:
        out.append({"caseId": d["caseId"], "name": d["name"], "angle": d["angle"],
                    "expected": d["expected"], "createdAt": d["createdAt"].isoformat()})
    return out


async def delete_case(principal: dict, case_id: str) -> None:
    res = await get_db().di_benchmark_cases.delete_one(
        {"tenantId": principal["tenantId"], "caseId": case_id})
    if res.deleted_count:
        shutil.rmtree(_bench_dir(principal["tenantId"], case_id), ignore_errors=True)


def _case_images(tenant_id: str, case_id: str) -> Optional[tuple[tuple, tuple]]:
    d = _bench_dir(tenant_id, case_id)
    pair = []
    for which in ("before", "after"):
        p = next((d / f"{which}.{e}" for e in ("jpg", "png") if (d / f"{which}.{e}").exists()), None)
        if not p:
            return None
        mime = "image/png" if p.suffix == ".png" else "image/jpeg"
        pair.append((p.read_bytes(), mime))
    return pair[0], pair[1]


def _match(expected: list[dict], items: list[dict]) -> tuple[list[dict], int]:
    """Greedy one-to-one matching of expected findings against detected NEW items."""
    detected = [it for it in items if it.get("status") in ("NEW", "UNCERTAIN")]
    used = set()
    results = []
    # Most specific (more keywords) expectations claim items first.
    order = sorted(range(len(expected)), key=lambda i: -len(expected[i]["keywords"]))
    verdicts = [None] * len(expected)
    for i in order:
        e = expected[i]
        hit = None
        for j, it in enumerate(detected):
            if j in used or it.get("category") != e["category"]:
                continue
            text = f"{it.get('location', '')} {it.get('detail', '')}".lower()
            if not e["keywords"] or any(k in text for k in e["keywords"]):
                hit = j
                break
        if hit is not None:
            used.add(hit)
            verdicts[i] = {"matchedBy": (detected[hit].get("location") or "")[:120]}
    for i, e in enumerate(expected):
        results.append({**e, "found": verdicts[i] is not None,
                        "matchedBy": (verdicts[i] or {}).get("matchedBy")})
    extra = len(detected) - len(used)
    return results, max(0, extra)


async def start_run(*, principal: dict, mode: str, correlation_id: str) -> dict:
    cases = await list_cases(principal)
    if not cases:
        raise DomainError(ErrorCode.VALIDATION_ERROR,
                          "No benchmark cases — add at least one case first.", 400, "cases")
    run_id = uuid.uuid4().hex
    mode = mode if mode in ("fast", "thorough") else "fast"
    doc = {
        "runId": run_id, "tenantId": principal["tenantId"], "status": "RUNNING",
        "mode": mode, "startedAt": datetime.now(timezone.utc), "finishedAt": None,
        "cases": [], "summary": None,
    }
    await get_db().di_benchmark_runs.insert_one(dict(doc))
    asyncio.create_task(_run(run_id, dict(principal), cases, mode, correlation_id))
    return {"runId": run_id, "status": "RUNNING", "mode": mode, "caseCount": len(cases)}


async def _run(run_id: str, principal: dict, cases: list[dict], mode: str,
               correlation_id: str) -> None:
    db = get_db()
    results = []
    for c in cases:
        started = time.monotonic()
        entry = {"caseId": c["caseId"], "name": c["name"], "angle": c["angle"]}
        try:
            pair = _case_images(principal["tenantId"], c["caseId"])
            if not pair:
                raise RuntimeError("Case images missing from storage.")
            section = await trip_inspection_service.analyze_section(
                principal=principal, kind="EXTERIOR", angle=c["angle"],
                before=pair[0], after=pair[1], mode=mode,
                correlation_id=correlation_id)
            expected, extra = _match(c["expected"], section.get("items") or [])
            required = [e for e in expected if not e["optional"]]
            found_req = sum(1 for e in required if e["found"])
            entry.update({
                "status": "DONE", "expected": expected,
                "requiredCount": len(required), "foundRequired": found_req,
                "recall": round(found_req / len(required) * 100) if required else 100,
                "optionalFound": sum(1 for e in expected if e["optional"] and e["found"]),
                "optionalCount": sum(1 for e in expected if e["optional"]),
                "extraDetections": extra,
                "newIssueCount": section.get("newIssueCount"),
                "tokens": (section.get("tokenUsage") or {}).get("totalTokens") or 0,
            })
        except Exception as exc:
            entry.update({"status": "FAILED", "error": str(exc)[:200], "recall": 0,
                          "requiredCount": len([e for e in c["expected"] if not e.get("optional")]),
                          "foundRequired": 0, "expected": c["expected"], "tokens": 0,
                          "extraDetections": 0})
        entry["durationMs"] = int((time.monotonic() - started) * 1000)
        results.append(entry)
        await db.di_benchmark_runs.update_one({"runId": run_id}, {"$set": {"cases": results}})
    total_req = sum(r.get("requiredCount", 0) for r in results)
    total_found = sum(r.get("foundRequired", 0) for r in results)
    summary = {
        "recall": round(total_found / total_req * 100) if total_req else 0,
        "requiredCount": total_req, "foundRequired": total_found,
        "tokens": sum(r.get("tokens", 0) for r in results),
        "failedCases": sum(1 for r in results if r["status"] == "FAILED"),
    }
    await db.di_benchmark_runs.update_one({"runId": run_id}, {"$set": {
        "status": "DONE", "finishedAt": datetime.now(timezone.utc), "summary": summary}})


def _run_ser(d: dict) -> dict:
    return {
        "runId": d["runId"], "status": d["status"], "mode": d["mode"],
        "startedAt": d["startedAt"].isoformat(),
        "finishedAt": d["finishedAt"].isoformat() if d.get("finishedAt") else None,
        "cases": d.get("cases") or [], "summary": d.get("summary"),
    }


async def get_run(principal: dict, run_id: str) -> dict:
    d = await get_db().di_benchmark_runs.find_one(
        {"tenantId": principal["tenantId"], "runId": run_id})
    if not d:
        raise DomainError(ErrorCode.NOT_FOUND, "Run not found.", 404, "runId")
    return _run_ser(d)


async def list_runs(principal: dict, limit: int = 10) -> list[dict]:
    cur = get_db().di_benchmark_runs.find(
        {"tenantId": principal["tenantId"]}).sort("startedAt", -1).limit(limit)
    return [_run_ser(d) async for d in cur]
