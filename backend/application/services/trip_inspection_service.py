"""
Repository Traceability:
- Purpose: Anonymous, ephemeral "Trip Inspection" quick analysis. Compares BEFORE and AFTER
  rental photos with the real Gemini vision engine and reports exterior damage (dents,
  scratches, chips, tyres, wheels, glass, lights, broken/missing parts, rust, vandalism,
  dirt, fluid leaks) and OPTIONAL interior condition (seats, dashboard, trim, stains,
  missing items, electronics), classifying each as NEW vs PRE-EXISTING.
- All images are received in a SINGLE request, written to a per-request temp dir for the
  duration of analysis only, and deleted immediately after. NOTHING is persisted. This also
  keeps the flow correct behind multi-instance load balancers (no cross-request disk state).
- Advisory only. Bridges the gap until CROMS/Maintenance integration drives the full lifecycle.
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
_EXT_OF = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}

_STATUSES = {"NEW", "PRE_EXISTING", "RESOLVED", "UNCERTAIN"}
_SEVERITIES = {"LOW", "MEDIUM", "HIGH"}

EXTERIOR_CATEGORIES = {
    "DENT": "Dents",
    "SCRATCH": "Scratches",
    "CHIP": "Chips",
    "TIRE": "Tyres",
    "WHEEL": "Wheels / rims",
    "GLASS": "Glass",
    "LIGHT": "Lights",
    "PART": "Broken / missing parts",
    "RUST": "Rust / corrosion",
    "VANDALISM": "Vandalism / graffiti",
    "DIRT": "Dirt / staining",
    "LEAK": "Fluid leaks",
}
INTERIOR_CATEGORIES = {
    "SEAT": "Seats",
    "DASHBOARD": "Dashboard / console",
    "TRIM": "Trim / panels",
    "STAIN": "Stains / dirt",
    "MISSING": "Missing items",
    "ELECTRONICS": "Screens / controls",
}

_EXT_SYNONYMS = {
    "TYRE": "TIRE", "TIRES": "TIRE", "TYRES": "TIRE",
    "WHEEL": "WHEEL", "WHEELS": "WHEEL", "RIM": "WHEEL", "RIMS": "WHEEL", "ALLOY": "WHEEL", "ALLOYS": "WHEEL",
    "WINDOW": "GLASS", "WINDOWS": "GLASS", "WINDSHIELD": "GLASS", "WINDSCREEN": "GLASS", "WINDSHEILD": "GLASS",
    "LAMP": "LIGHT", "LAMPS": "LIGHT", "LIGHTS": "LIGHT", "HEADLIGHT": "LIGHT", "HEADLAMP": "LIGHT",
    "TAILLIGHT": "LIGHT", "TAILLAMP": "LIGHT", "BRAKELIGHT": "LIGHT", "BRAKELAMP": "LIGHT", "INDICATOR": "LIGHT",
    "BUMPER": "PART", "MIRROR": "PART", "TRIM": "PART", "GRILLE": "PART", "GRILL": "PART", "BADGE": "PART",
    "HANDLE": "PART", "BROKEN_PART": "PART", "MISSING_PART": "PART", "PARTS": "PART", "PANEL": "PART",
    "CORROSION": "RUST",
    "CHIPS": "CHIP", "STONECHIP": "CHIP", "STONE_CHIP": "CHIP", "PAINTCHIP": "CHIP", "PAINT_CHIP": "CHIP",
    "GRAFFITI": "VANDALISM", "STICKER": "VANDALISM", "STICKERS": "VANDALISM", "DECAL": "VANDALISM",
    "KEYED": "VANDALISM", "KEYING": "VANDALISM",
    "MUD": "DIRT", "DIRTY": "DIRT", "GRIME": "DIRT", "PAINT_DAMAGE": "SCRATCH", "SCUFF": "SCRATCH",
    "LEAKS": "LEAK", "FLUID": "LEAK", "OIL": "LEAK", "COOLANT": "LEAK", "PUDDLE": "LEAK",
}
_INT_SYNONYMS = {
    "SEATS": "SEAT", "UPHOLSTERY": "SEAT", "CUSHION": "SEAT",
    "DASH": "DASHBOARD", "CONSOLE": "DASHBOARD",
    "PANEL": "TRIM", "DOORPANEL": "TRIM", "DOOR_PANEL": "TRIM", "MOLDING": "TRIM", "TRIMS": "TRIM",
    "STAINS": "STAIN", "DIRT": "STAIN", "SPILL": "STAIN", "DIRTY": "STAIN", "MARK": "STAIN", "CARPET": "STAIN",
    "MISSING_ITEM": "MISSING", "FLOORMAT": "MISSING", "MAT": "MISSING", "MATS": "MISSING", "HEADREST": "MISSING",
    "SCREEN": "ELECTRONICS", "INFOTAINMENT": "ELECTRONICS", "CONTROLS": "ELECTRONICS",
    "BUTTON": "ELECTRONICS", "BUTTONS": "ELECTRONICS", "DISPLAY": "ELECTRONICS",
}

_EXT_PROMPT_LINES = (
    "- DENT: dents or deformations in body panels\n"
    "- SCRATCH: scratches, scuffs, or paint scrapes\n"
    "- CHIP: stone chips or small paint chips\n"
    "- TIRE: tyre/tire issues (flat, cuts, bald, missing)\n"
    "- WHEEL: wheel / rim / alloy damage (curb scrapes, cracks, bent)\n"
    "- GLASS: broken, cracked, or shattered glass (windscreen, rear/side windows)\n"
    "- LIGHT: broken, cracked, or missing lights (headlight, tail, brake lamp, indicator)\n"
    "- PART: broken or missing parts (bumper, mirror, trim, grille, badge, door handle)\n"
    "- RUST: rust or corrosion\n"
    "- VANDALISM: graffiti, keying, or unauthorized stickers/decals\n"
    "- DIRT: excessive dirt, mud, or exterior staining\n"
    "- LEAK: fluid leaks or puddles/stains under the vehicle\n"
)
_INT_PROMPT_LINES = (
    "- SEAT: seat tears, burns, rips, or stains\n"
    "- DASHBOARD: dashboard or centre-console cracks or damage\n"
    "- TRIM: door-panel, trim, or interior moulding damage\n"
    "- STAIN: stains, spills, dirt, or marks on interior surfaces/carpet\n"
    "- MISSING: missing interior items (floor mats, headrests, accessories)\n"
    "- ELECTRONICS: damaged screen, infotainment, or controls/buttons\n"
)

_EXT_SYSTEM = (
    "You are the Damage Intelligence rental-trip inspector. Your output is ADVISORY ONLY and "
    "does not decide liability, charges, or repair cost. You receive a BEFORE photo (start of "
    "rental) and an AFTER photo (end of rental) of the EXTERIOR of the same vehicle. Compare "
    "them and report any visible exterior damage or condition issue. Respond with STRICT JSON "
    "only — no prose."
)
_INT_SYSTEM = (
    "You are the Damage Intelligence rental-trip inspector. Your output is ADVISORY ONLY and "
    "does not decide liability, charges, or repair cost. You receive a BEFORE photo (start of "
    "rental) and an AFTER photo (end of rental) of the INTERIOR of the same vehicle. Compare "
    "them and report any visible interior damage or condition issue. Respond with STRICT JSON "
    "only — no prose."
)


def _provider() -> str:
    return os.environ.get("DI_AI_MODEL_DAMAGE_PROVIDER", "gemini")


def _model() -> str:
    return os.environ.get("DI_AI_MODEL_DAMAGE_NAME", "gemini-3.1-pro-preview")


def _user_prompt(kind: str, lines: str, enum_list: str) -> str:
    where = "exterior" if kind == "EXTERIOR" else "interior"
    return (
        f"The FIRST image is the {where} BEFORE the trip. The SECOND image is the {where} AFTER "
        "the trip. Compare them.\n"
        f"Report ALL visible {where} damage and condition issues across these categories. Be "
        "conservative; if unsure, set status UNCERTAIN.\n"
        "Categories:\n" + lines + "\n"
        "Return JSON EXACTLY in this shape:\n"
        "{\n"
        '  "comparable": true or false,\n'
        '  "notComparableReason": string or null,\n'
        '  "items": [\n'
        "    {\n"
        f'      "category": one of [{enum_list}],\n'
        '      "status": one of ["NEW","PRE_EXISTING","RESOLVED","UNCERTAIN"],\n'
        '      "location": short string e.g. "rear window" or "driver seat" or "front bumper",\n'
        '      "severity": one of ["LOW","MEDIUM","HIGH"] or null,\n'
        '      "confidence": number between 0 and 1,\n'
        '      "detail": short human-readable note,\n'
        '      "box": { "x": 0..1, "y": 0..1, "w": 0..1, "h": 0..1 } normalized bounding box of\n'
        '              the issue on the AFTER image (x,y = top-left corner as fractions of\n'
        '              width/height), or null if you cannot localize it\n'
        "    }\n"
        "  ],\n"
        '  "summary": one or two sentence plain-language summary\n'
        "}\n\n"
        "NEW = appeared during the trip (not in BEFORE). PRE_EXISTING = present in both. "
        "RESOLVED = in BEFORE but gone in AFTER. Empty items list is valid (no issues found)."
    )


def _normalize_box(box) -> Optional[dict]:
    if not isinstance(box, dict):
        return None
    try:
        x = float(box.get("x"))
        y = float(box.get("y"))
        w = float(box.get("w"))
        h = float(box.get("h"))
    except (TypeError, ValueError):
        return None
    if not (0 <= x <= 1 and 0 <= y <= 1 and 0 < w <= 1 and 0 < h <= 1):
        return None
    w = min(w, 1 - x)
    h = min(h, 1 - y)
    if w <= 0 or h <= 0:
        return None
    return {"x": round(x, 4), "y": round(y, 4), "w": round(w, 4), "h": round(h, 4)}


def _normalize_section(parsed: dict | None, categories: dict, synonyms: dict) -> dict:
    if not isinstance(parsed, dict):
        return {
            "comparable": False,
            "notComparableReason": "model_unparseable",
            "items": [],
            "summary": "Analysis could not be completed; please retry with clearer photos.",
            "counts": {c: {"NEW": 0, "total": 0} for c in categories},
            "newIssueCount": 0,
            "overall": "NOT_COMPARABLE",
        }
    items = []
    for it in (parsed.get("items") or [])[:80]:
        if not isinstance(it, dict):
            continue
        cat = str(it.get("category") or "").upper()
        cat = synonyms.get(cat, cat)
        if cat not in categories:
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
            "category": cat,
            "status": status,
            "location": (it.get("location") if isinstance(it.get("location"), str) else "")[:160],
            "severity": sev,
            "confidence": conf,
            "detail": (it.get("detail") if isinstance(it.get("detail"), str) else "")[:300],
            "box": _normalize_box(it.get("box")),
        })
    counts = {c: {"NEW": 0, "total": 0} for c in categories}
    for it in items:
        counts[it["category"]]["total"] += 1
        if it["status"] == "NEW":
            counts[it["category"]]["NEW"] += 1
    comparable = bool(parsed.get("comparable", True))
    new_issues = sum(c["NEW"] for c in counts.values())
    overall = ("NOT_COMPARABLE" if not comparable
               else "NEW_DAMAGE_FOUND" if new_issues > 0
               else "NO_NEW_DAMAGE")
    return {
        "comparable": comparable,
        "notComparableReason": parsed.get("notComparableReason") if isinstance(parsed.get("notComparableReason"), str) else None,
        "items": items,
        "summary": (parsed.get("summary") if isinstance(parsed.get("summary"), str) else "")[:600],
        "counts": counts,
        "newIssueCount": new_issues,
        "overall": overall,
    }


async def _analyze_pair(*, before_path: str, before_mime: str, after_path: str, after_mime: str,
                        kind: str, correlation_id: str) -> tuple[dict, str, int]:
    categories = EXTERIOR_CATEGORIES if kind == "EXTERIOR" else INTERIOR_CATEGORIES
    synonyms = _EXT_SYNONYMS if kind == "EXTERIOR" else _INT_SYNONYMS
    lines = _EXT_PROMPT_LINES if kind == "EXTERIOR" else _INT_PROMPT_LINES
    system = _EXT_SYSTEM if kind == "EXTERIOR" else _INT_SYSTEM
    enum_list = ",".join(f'"{c}"' for c in categories)
    parsed, model_label, latency_ms, err = await call_vision_model_multi(
        provider=_provider(), model_name=_model(),
        system_message=system, user_prompt=_user_prompt(kind, lines, enum_list),
        images=[
            {"path": before_path, "mime": before_mime},
            {"path": after_path, "mime": after_mime},
        ],
        correlation_id=correlation_id,
    )
    if err is not None:
        raise DomainError(ErrorCode.INTERNAL_ERROR,
                          "The analysis engine is temporarily unavailable. Please retry.", 503)
    section = _normalize_section(parsed, categories, synonyms)
    section["kind"] = kind
    section["label"] = "Exterior" if kind == "EXTERIOR" else "Interior"
    return section, model_label, latency_ms or 0


def _validate_and_save(work: Path, slot: str, payload: tuple[bytes, Optional[str]]) -> tuple[str, str]:
    content, content_type = payload
    ct = (content_type or "").lower()
    if ct not in _ALLOWED_MIME:
        raise DomainError(ErrorCode.VALIDATION_ERROR, "Only JPEG, PNG, or WEBP images are allowed.", 400, slot)
    if not content:
        raise DomainError(ErrorCode.VALIDATION_ERROR, "Empty file.", 400, slot)
    if len(content) > _MAX_BYTES:
        raise DomainError(ErrorCode.VALIDATION_ERROR, "Image exceeds the 12 MB limit.", 400, slot)
    path = work / f"{slot}.{_EXT_OF[ct]}"
    path.write_bytes(content)
    return str(path), ct


async def analyze_trip(*, principal: dict, files: dict, correlation_id: str) -> dict:
    """`files` maps slot -> (bytes, content_type). At least one complete pair is required:
    exterior_before+exterior_after and/or interior_before+interior_after. Each provided area
    is analyzed independently."""
    tenant_id = principal["tenantId"]
    ext_before = files.get("exterior_before")
    ext_after = files.get("exterior_after")
    int_before = files.get("interior_before")
    int_after = files.get("interior_after")
    has_ext = bool(ext_before and ext_after)
    has_int = bool(int_before and int_after)
    if not has_ext and not has_int:
        raise DomainError(ErrorCode.VALIDATION_ERROR,
                          "Provide a Before and After photo for at least one area (exterior or interior).",
                          400, "images")

    work = _TMP_ROOT / uuid.uuid4().hex
    work.mkdir(parents=True, exist_ok=True)
    sections: list[dict] = []
    models: list[str] = []
    total_latency = 0
    try:
        if has_ext:
            eb_path, eb_mime = _validate_and_save(work, "exterior_before", ext_before)
            ea_path, ea_mime = _validate_and_save(work, "exterior_after", ext_after)
            ext_section, ext_model, ext_lat = await _analyze_pair(
                before_path=eb_path, before_mime=eb_mime, after_path=ea_path, after_mime=ea_mime,
                kind="EXTERIOR", correlation_id=correlation_id,
            )
            sections.append(ext_section)
            models.append(ext_model)
            total_latency += ext_lat

        if has_int:
            ib_path, ib_mime = _validate_and_save(work, "interior_before", int_before)
            ia_path, ia_mime = _validate_and_save(work, "interior_after", int_after)
            int_section, int_model, int_lat = await _analyze_pair(
                before_path=ib_path, before_mime=ib_mime, after_path=ia_path, after_mime=ia_mime,
                kind="INTERIOR", correlation_id=correlation_id,
            )
            sections.append(int_section)
            models.append(int_model)
            total_latency += int_lat
    finally:
        shutil.rmtree(work, ignore_errors=True)

    new_total = sum(s["newIssueCount"] for s in sections)
    any_comparable = any(s["comparable"] for s in sections)
    overall = ("NEW_DAMAGE_FOUND" if new_total > 0
               else "NO_NEW_DAMAGE" if any_comparable
               else "NOT_COMPARABLE")

    result = {
        "sections": sections,
        "overall": overall,
        "newIssueCount": new_total,
        "modelVersion": models[0] if models else f"{_provider()}:{_model()}",
        "isAdvisory": True,
    }

    await write_audit(
        tenant_id=tenant_id, actor_id=principal["id"], actor_type=ActorType.USER,
        action=AuditAction.QUICK_TRIP_ANALYSIS_RUN, object_type=ObjectType.AI_ANALYSIS,
        object_id="trip-quick", correlation_id=correlation_id,
        safe_metadata={"overall": overall, "newIssues": new_total,
                       "sections": [s["kind"] for s in sections],
                       "model": result["modelVersion"], "latencyMs": total_latency},
    )
    return result
