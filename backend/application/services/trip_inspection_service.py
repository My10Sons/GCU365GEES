"""
Repository Traceability:
- Purpose: Anonymous, ephemeral "Trip Inspection" quick analysis. Compares a BEFORE and an
  AFTER rental photo with the real Gemini vision engine and reports dents, scratches, and
  tire issues (NEW vs PRE-EXISTING). NOTHING is persisted — images live in a temp dir for the
  duration of the analysis only and are deleted immediately after. Advisory only.
- Bridges the gap until CROMS/Maintenance integration drives the full inspection lifecycle.
"""
from __future__ import annotations

import os
import shutil
import uuid
from pathlib import Path
from typing import Optional

from api.middleware.safe_errors import DomainError
from application.ai.gemini_client import call_vision_model_multi
from application.services.audit_service import write_audit
from domain.enums.audit_actions import ActorType, AuditAction, ObjectType
from domain.enums.error_codes import ErrorCode

_TMP_ROOT = Path(os.environ.get("DI_TRIP_TMP_DIR", "/tmp/di-trip"))
_MAX_BYTES = 12 * 1024 * 1024  # 12 MB per image safety cap
_ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}

SYSTEM_MESSAGE = (
    "You are the Damage Intelligence rental-trip inspector. Your output is ADVISORY ONLY and "
    "does not decide liability, charges, or repair cost. You receive a BEFORE photo (start of "
    "rental) and an AFTER photo (end of rental) of the same vehicle. Compare them and report "
    "ONLY: dents, scratches, and tyre/tire issues. Respond with STRICT JSON only — no prose."
)

USER_PROMPT = (
    "The FIRST image is BEFORE the trip. The SECOND image is AFTER the trip. Compare them.\n"
    "Report dents, scratches, and tyre/tire issues. Be conservative; if unsure, say UNCERTAIN.\n\n"
    "Return JSON EXACTLY in this shape:\n"
    "{\n"
    '  "comparable": true or false,\n'
    '  "notComparableReason": string or null,\n'
    '  "items": [\n'
    "    {\n"
    '      "category": one of ["DENT","SCRATCH","TIRE"],\n'
    '      "status": one of ["NEW","PRE_EXISTING","RESOLVED","UNCERTAIN"],\n'
    '      "location": short string e.g. "front bumper, driver side" or "rear-left tyre",\n'
    '      "severity": one of ["LOW","MEDIUM","HIGH"] or null,\n'
    '      "confidence": number between 0 and 1,\n'
    '      "detail": short human-readable note\n'
    "    }\n"
    "  ],\n"
    '  "summary": one or two sentence plain-language summary\n'
    "}\n\n"
    "NEW = appeared during the trip (not in BEFORE). PRE_EXISTING = present in both. "
    "RESOLVED = in BEFORE but gone in AFTER. Empty items list is valid (no issues found)."
)

_CATEGORIES = {"DENT", "SCRATCH", "TIRE"}
_STATUSES = {"NEW", "PRE_EXISTING", "RESOLVED", "UNCERTAIN"}
_SEVERITIES = {"LOW", "MEDIUM", "HIGH"}


def _provider() -> str:
    return os.environ.get("DI_AI_MODEL_DAMAGE_PROVIDER", "gemini")


def _model() -> str:
    return os.environ.get("DI_AI_MODEL_DAMAGE_NAME", "gemini-3.1-pro-preview")


def _session_dir(tenant_id: str, token: str) -> Path:
    safe = "".join(ch for ch in token if ch.isalnum())[:40]
    return _TMP_ROOT / tenant_id / safe


def new_token() -> str:
    return uuid.uuid4().hex


async def save_slot(*, tenant_id: str, token: str, slot: str, content: bytes, content_type: Optional[str]) -> dict:
    if slot not in ("before", "after"):
        raise DomainError(ErrorCode.VALIDATION_ERROR, "slot must be 'before' or 'after'.", 400, "slot")
    if (content_type or "").lower() not in _ALLOWED_MIME:
        raise DomainError(ErrorCode.VALIDATION_ERROR, "Only JPEG, PNG, or WEBP images are allowed.", 400, "file")
    if not content:
        raise DomainError(ErrorCode.VALIDATION_ERROR, "Empty file.", 400, "file")
    if len(content) > _MAX_BYTES:
        raise DomainError(ErrorCode.VALIDATION_ERROR, "Image exceeds the 12 MB limit.", 400, "file")
    d = _session_dir(tenant_id, token)
    d.mkdir(parents=True, exist_ok=True)
    ext = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}[content_type.lower()]
    (d / f"{slot}.{ext}").write_bytes(content)
    return {"token": token, "slot": slot, "received": True}


def _find_slot(d: Path, slot: str) -> Optional[Path]:
    for ext in ("jpg", "png", "webp"):
        p = d / f"{slot}.{ext}"
        if p.exists():
            return p
    return None


def _normalize(parsed: dict | None) -> dict:
    if not isinstance(parsed, dict):
        return {"comparable": False, "notComparableReason": "model_unparseable", "items": [],
                "summary": "Analysis could not be completed; please retry with clearer photos."}
    items = []
    for it in (parsed.get("items") or [])[:60]:
        if not isinstance(it, dict):
            continue
        cat = str(it.get("category") or "").upper()
        if cat in ("TYRE", "TIRES", "TYRES", "WHEEL"):
            cat = "TIRE"
        if cat not in _CATEGORIES:
            continue
        status = str(it.get("status") or "UNCERTAIN").upper()
        if status not in _STATUSES:
            status = "UNCERTAIN"
        sev = it.get("severity")
        sev = sev.upper() if isinstance(sev, str) and sev.upper() in _SEVERITIES else None
        try:
            conf = max(0.0, min(1.0, float(it.get("confidence") or 0)))
        except (TypeError, ValueError):
            conf = 0.0
        items.append({
            "category": cat, "status": status,
            "location": (it.get("location") if isinstance(it.get("location"), str) else "")[:160],
            "severity": sev, "confidence": conf,
            "detail": (it.get("detail") if isinstance(it.get("detail"), str) else "")[:300],
        })
    return {
        "comparable": bool(parsed.get("comparable", True)),
        "notComparableReason": parsed.get("notComparableReason") if isinstance(parsed.get("notComparableReason"), str) else None,
        "items": items,
        "summary": (parsed.get("summary") if isinstance(parsed.get("summary"), str) else "")[:600],
    }


async def analyze(*, principal: dict, token: str, correlation_id: str) -> dict:
    tenant_id = principal["tenantId"]
    d = _session_dir(tenant_id, token)
    before = _find_slot(d, "before")
    after = _find_slot(d, "after")
    if not before or not after:
        raise DomainError(ErrorCode.VALIDATION_ERROR,
                          "Both a Before and an After image are required.", 400, "images")
    mime_of = {"jpg": "image/jpeg", "png": "image/png", "webp": "image/webp"}
    try:
        parsed, model_label, latency_ms, err = await call_vision_model_multi(
            provider=_provider(), model_name=_model(),
            system_message=SYSTEM_MESSAGE, user_prompt=USER_PROMPT,
            images=[
                {"path": str(before), "mime": mime_of[before.suffix.lstrip(".")]},
                {"path": str(after), "mime": mime_of[after.suffix.lstrip(".")]},
            ],
            correlation_id=correlation_id,
        )
    finally:
        # Ephemeral: never keep the uploaded images.
        shutil.rmtree(d, ignore_errors=True)

    if err is not None:
        raise DomainError(ErrorCode.INTERNAL_ERROR,
                          "The analysis engine is temporarily unavailable. Please retry.", 503)

    result = _normalize(parsed)
    result["modelVersion"] = model_label
    result["isAdvisory"] = True

    counts = {"DENT": {"NEW": 0, "total": 0}, "SCRATCH": {"NEW": 0, "total": 0}, "TIRE": {"NEW": 0, "total": 0}}
    for it in result["items"]:
        counts[it["category"]]["total"] += 1
        if it["status"] == "NEW":
            counts[it["category"]]["NEW"] += 1
    result["counts"] = counts
    new_issues = sum(c["NEW"] for c in counts.values())
    result["overall"] = ("NOT_COMPARABLE" if not result["comparable"]
                         else "NEW_DAMAGE_FOUND" if new_issues > 0
                         else "NO_NEW_DAMAGE")
    result["newIssueCount"] = new_issues

    await write_audit(
        tenant_id=tenant_id, actor_id=principal["id"], actor_type=ActorType.USER,
        action=AuditAction.QUICK_TRIP_ANALYSIS_RUN, object_type=ObjectType.AI_ANALYSIS,
        object_id="trip-quick", correlation_id=correlation_id,
        safe_metadata={"overall": result["overall"], "newIssues": new_issues,
                       "model": model_label, "latencyMs": latency_ms},
    )
    return result
