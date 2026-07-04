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

import asyncio
import calendar
import os
import shutil
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from api.middleware.safe_errors import DomainError
from application.ai.gemini_client import call_vision_model_multi
from application.services import damage_case_service, inspection_service, vehicle_registry_service
from application.services.audit_service import write_audit
from application.services.exif_check import build_metadata_check
from application.services.tenant_branding_service import get_branding
from domain.enums.ai_codes import AIFindingStatus, DamageType
from domain.enums.audit_actions import ActorType, AuditAction, ObjectType
from domain.enums.case_codes import CaseType
from domain.enums.error_codes import ErrorCode
from domain.enums.inspection_type import InspectionType, SourceSystem
from infrastructure.db.mongo import get_db

_TMP_ROOT = Path(os.environ.get("DI_TRIP_TMP_DIR", "/tmp/di-trip"))
_MAX_BYTES = 12 * 1024 * 1024  # 12 MB per image safety cap
_ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}
_EXT_OF = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}

_STATUSES = {"NEW", "PRE_EXISTING", "RESOLVED", "UNCERTAIN"}
_SEVERITIES = {"LOW", "MEDIUM", "HIGH"}
_CLEANLINESS = ["CLEAN", "LIGHT_DIRT", "DIRTY", "VERY_DIRTY"]

# Deterministic, advisory repair-cost ranges (MEDIUM-severity baseline) per category.
# Kept rule-based (not model-generated) so estimates are consistent and defensible.
_COST_CURRENCY = os.environ.get("DI_TRIP_CURRENCY", "SAR")
_COST_BASE = {
    "DENT": (300, 800), "SCRATCH": (150, 500), "CHIP": (80, 250), "TIRE": (200, 600),
    "WHEEL": (250, 900), "GLASS": (400, 1500), "LIGHT": (200, 900), "PART": (300, 1200),
    "RUST": (200, 700), "VANDALISM": (200, 900), "DIRT": (50, 200), "LEAK": (150, 700),
    "SEAT": (200, 1000), "DASHBOARD": (300, 1200), "TRIM": (150, 700), "STAIN": (80, 300),
    "MISSING": (100, 600), "ELECTRONICS": (300, 1500),
}
_SEVERITY_FACTOR = {"LOW": 0.5, "MEDIUM": 1.0, "HIGH": 1.7, None: 1.0}

# Auto-route: when a trip finds NEW damage whose total estimated repair cost (high end)
# reaches this threshold, a persisted Damage Case is auto-created (anonymous trip -> review queue).
_AUTO_CASE_COST_THRESHOLD = float(os.environ.get("DI_TRIP_AUTO_CASE_COST_THRESHOLD", "1000"))
_SEVERITY_RANK = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
# Map ephemeral trip categories onto the persisted AI finding DamageType enum.
_CATEGORY_TO_DAMAGE_TYPE = {
    "DENT": DamageType.DENT, "SCRATCH": DamageType.SCRATCH, "CHIP": DamageType.PAINT_DAMAGE,
    "TIRE": DamageType.OTHER, "WHEEL": DamageType.OTHER, "GLASS": DamageType.CRACK,
    "LIGHT": DamageType.BROKEN_PART, "PART": DamageType.BROKEN_PART, "RUST": DamageType.RUST,
    "VANDALISM": DamageType.PAINT_DAMAGE, "DIRT": DamageType.OTHER, "LEAK": DamageType.OTHER,
    "SEAT": DamageType.OTHER, "DASHBOARD": DamageType.OTHER, "TRIM": DamageType.OTHER,
    "STAIN": DamageType.OTHER, "MISSING": DamageType.MISSING_PART, "ELECTRONICS": DamageType.BROKEN_PART,
}


def _estimate_cost(category: str, severity: Optional[str]) -> dict:
    low, high = _COST_BASE.get(category, (150, 600))
    factor = _SEVERITY_FACTOR.get(severity, 1.0)
    return {
        "low": int(round(low * factor / 10.0)) * 10,
        "high": int(round(high * factor / 10.0)) * 10,
        "currency": _COST_CURRENCY,
    }


def _worst_cleanliness(values: list[str]) -> Optional[str]:
    ranked = [v for v in values if v in _CLEANLINESS]
    if not ranked:
        return None
    return max(ranked, key=lambda v: _CLEANLINESS.index(v))

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


def _fast_model() -> str:
    return os.environ.get("DI_AI_MODEL_DAMAGE_FAST_NAME", "gemini-3.5-flash")


def _model_for_mode(mode: str) -> str:
    return _fast_model() if (mode or "fast").lower() == "fast" else _model()


# Auto-escalation: in Fast mode, areas with uncertain or high-severity findings are silently
# re-checked on the Pro model — Flash speed on the easy majority, Pro accuracy where it matters.
_AUTO_ESCALATE = os.environ.get("DI_TRIP_AUTO_ESCALATE", "true").lower() == "true"
_ESCALATE_CONF = float(os.environ.get("DI_TRIP_ESCALATE_CONFIDENCE", "0.6"))


def _should_escalate(section: dict) -> bool:
    for it in section.get("items", []):
        status = it.get("status")
        if status == "UNCERTAIN":
            return True
        if status == "NEW" and it.get("severity") == "HIGH":
            return True
        conf = it.get("confidence")
        if status == "NEW" and conf is not None and conf < _ESCALATE_CONF:
            return True
    return False


_RECOMMENDATIONS = {"REPAIR", "REPLACE", "ASSESS"}
_AI_LIKELIHOOD = {"LOW", "MEDIUM", "HIGH"}
_EXTERIOR_ANGLES = ["FRONT", "REAR", "LEFT", "RIGHT", "ROOF"]
_ANGLE_LABEL = {"FRONT": "Front", "REAR": "Rear", "LEFT": "Left side", "RIGHT": "Right side", "ROOF": "Roof"}


def _user_prompt(kind: str, lines: str, enum_list: str, angle: Optional[str]) -> str:
    where = "exterior" if kind == "EXTERIOR" else "interior"
    angle_ctx = ""
    if kind == "EXTERIOR" and angle:
        angle_ctx = f"Both photos show the {_ANGLE_LABEL.get(angle, angle)} view of the vehicle. "
    return (
        f"The FIRST image is the {where} BEFORE the trip. The SECOND image is the {where} AFTER "
        f"the trip. {angle_ctx}Compare them.\n"
        f"Report ALL visible {where} damage and condition issues across these categories. Be "
        "conservative; if unsure, set status UNCERTAIN. Also VERIFY the photos themselves: "
        "correct view/angle, full framing, camera distance, same vehicle, authenticity, and "
        "capture conditions (dirt, rain, glare).\n"
        "Categories:\n" + lines + "\n"
        "Return JSON EXACTLY in this shape:\n"
        "{\n"
        '  "comparable": true or false,\n'
        '  "notComparableReason": string or null,\n'
        '  "photoCheck": {\n'
        '     "beforeUsable": true or false (is the BEFORE photo clear enough to inspect),\n'
        '     "afterUsable": true or false (is the AFTER photo clear enough to inspect),\n'
        '     "issues": [ short strings for any photo problems e.g. "after photo is blurry", "before photo too dark", "view partly obstructed" ],\n'
        '     "sameVehicle": true or false (do BEFORE and AFTER show the SAME vehicle),\n'
        '     "vehicleMismatchReason": string or null,\n'
        '     "angleCorrect": true or false (do BOTH photos actually show the stated view/area; false if e.g. a rear photo was uploaded for the front),\n'
        '     "angleIssue": string or null (which photo shows the wrong view and what it shows instead),\n'
        '     "fullyVisible": true or false (is the stated area fully framed with nothing important cut off),\n'
        '     "croppedParts": [ short strings naming cut-off parts e.g. "front bumper partly cropped" ],\n'
        '     "distance": one of ["OK","TOO_CLOSE","TOO_FAR"] (camera distance in the AFTER photo)\n'
        "  },\n"
        '  "integrity": {\n'
        '     "beforeSuspicious": true or false (does the BEFORE photo show signs of digital editing, AI generation, or being a photo-of-a-screen),\n'
        '     "afterSuspicious": true or false (same for the AFTER photo),\n'
        '     "aiGeneratedLikelihood": one of ["LOW","MEDIUM","HIGH"] (likelihood either photo is AI-generated or manipulated),\n'
        '     "screenRecaptureLikelihood": one of ["LOW","MEDIUM","HIGH"] (likelihood either photo is a photo OF a screen, print, or another photo — look for moire patterns, pixel grids, screen bezels, rectangular glare),\n'
        '     "signals": [ short strings describing any tampering/AI signals e.g. "cloned region", "inconsistent shadows", "screen moire pattern", "warped edges" ]\n'
        "  },\n"
        '  "environment": {\n'
        '     "dirtObscuring": true or false (is dirt/mud heavy enough that it could HIDE damage),\n'
        '     "wetSurface": true or false (rain or water droplets on the vehicle that could hide or mimic damage),\n'
        '     "glare": true or false (strong glare/reflection hotspots that may hide or mimic damage),\n'
        '     "notes": [ short strings saying where, e.g. "heavy glare on the bonnet" ],\n'
        '     "confidenceReduced": true or false (should findings be treated with reduced confidence due to these conditions)\n'
        "  },\n"
        '  "vehicleSignature": {\n'
        '     "color": main body colour as ONE lowercase word (e.g. "white") or null,\n'
        '     "bodyType": one of ["sedan","suv","hatchback","pickup","van","coupe","truck","bus","other"] or null,\n'
        '     "visiblePlate": license-plate text if clearly readable in either photo, else null\n'
        "  },\n"
        '  "conditionScore": integer 0-100 (overall condition of the vehicle in the AFTER photo; 100 = pristine, 0 = severely damaged),\n'
        '  "cleanliness": one of ["CLEAN","LIGHT_DIRT","DIRTY","VERY_DIRTY"] for the AFTER photo,\n'
        '  "items": [\n'
        "    {\n"
        f'      "category": one of [{enum_list}],\n'
        '      "status": one of ["NEW","PRE_EXISTING","RESOLVED","UNCERTAIN"],\n'
        '      "location": short string e.g. "rear window" or "driver seat" or "front bumper",\n'
        '      "severity": one of ["LOW","MEDIUM","HIGH"] or null,\n'
        '      "confidence": number between 0 and 1,\n'
        '      "detail": short human-readable note,\n'
        '      "sizeCm": approximate longest dimension of the damage in centimetres as a number,\n'
        '              estimated using a visible reference for scale (a license plate is ~52 cm\n'
        '              wide, a door handle ~12 cm, a wheel ~45-65 cm). Use null if not estimable.\n'
        '      "sizeNote": short string naming the reference used for scale, or null,\n'
        '      "recommendation": one of ["REPAIR","REPLACE","ASSESS"] (REPLACE for shattered glass,\n'
        '              broken lamps, torn parts; REPAIR for dents/scratches/scuffs; ASSESS if unsure),\n'
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


_DISTANCES = {"OK", "TOO_CLOSE", "TOO_FAR"}
_BODY_TYPES = {"SEDAN", "SUV", "HATCHBACK", "PICKUP", "VAN", "COUPE", "TRUCK", "BUS", "OTHER"}


def _normalize_photo_check(parsed: dict, comparable: bool) -> dict:
    pc = parsed.get("photoCheck") if isinstance(parsed.get("photoCheck"), dict) else {}
    issues = pc.get("issues")
    issues = [str(s)[:140] for s in issues if isinstance(s, str)][:6] if isinstance(issues, list) else []
    cropped = pc.get("croppedParts")
    cropped = [str(s)[:140] for s in cropped if isinstance(s, str)][:5] if isinstance(cropped, list) else []
    distance = pc.get("distance")
    distance = distance.upper() if isinstance(distance, str) and distance.upper() in _DISTANCES else "OK"
    return {
        "beforeUsable": bool(pc.get("beforeUsable", True)),
        "afterUsable": bool(pc.get("afterUsable", True)),
        "issues": issues,
        "sameVehicle": bool(pc.get("sameVehicle", comparable)),
        "vehicleMismatchReason": pc.get("vehicleMismatchReason") if isinstance(pc.get("vehicleMismatchReason"), str) else None,
        "angleCorrect": bool(pc.get("angleCorrect", True)),
        "angleIssue": (pc.get("angleIssue") or None) if isinstance(pc.get("angleIssue"), str) else None,
        "fullyVisible": bool(pc.get("fullyVisible", True)),
        "croppedParts": cropped,
        "distance": distance,
    }


def _normalize_integrity(parsed: dict) -> dict:
    ig = parsed.get("integrity") if isinstance(parsed.get("integrity"), dict) else {}
    signals = ig.get("signals")
    signals = [str(s)[:140] for s in signals if isinstance(s, str)][:6] if isinstance(signals, list) else []
    likelihood = ig.get("aiGeneratedLikelihood")
    likelihood = likelihood.upper() if isinstance(likelihood, str) and likelihood.upper() in _AI_LIKELIHOOD else "LOW"
    screen = ig.get("screenRecaptureLikelihood")
    screen = screen.upper() if isinstance(screen, str) and screen.upper() in _AI_LIKELIHOOD else "LOW"
    return {
        "beforeSuspicious": bool(ig.get("beforeSuspicious", False)),
        "afterSuspicious": bool(ig.get("afterSuspicious", False)),
        "aiGeneratedLikelihood": likelihood,
        "screenRecaptureLikelihood": screen,
        "signals": signals,
    }


def _normalize_environment(parsed: dict) -> dict:
    env = parsed.get("environment") if isinstance(parsed.get("environment"), dict) else {}
    notes = env.get("notes")
    notes = [str(s)[:140] for s in notes if isinstance(s, str)][:6] if isinstance(notes, list) else []
    return {
        "dirtObscuring": bool(env.get("dirtObscuring", False)),
        "wetSurface": bool(env.get("wetSurface", False)),
        "glare": bool(env.get("glare", False)),
        "notes": notes,
        "confidenceReduced": bool(env.get("confidenceReduced", False)),
    }


def _normalize_signature(parsed: dict) -> dict:
    sig = parsed.get("vehicleSignature") if isinstance(parsed.get("vehicleSignature"), dict) else {}
    color = sig.get("color")
    color = color.strip().lower()[:24] if isinstance(color, str) and color.strip() else None
    if color == "grey":
        color = "gray"
    body = sig.get("bodyType")
    body = body.strip().lower() if isinstance(body, str) and body.strip().upper() in _BODY_TYPES else None
    plate = sig.get("visiblePlate")
    plate = plate.strip()[:20] if isinstance(plate, str) and plate.strip() else None
    return {"color": color, "bodyType": body, "visiblePlate": plate}


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
            "photoCheck": {"beforeUsable": False, "afterUsable": False, "issues": ["analysis could not be completed"], "sameVehicle": False, "vehicleMismatchReason": None,
                           "angleCorrect": True, "angleIssue": None, "fullyVisible": True, "croppedParts": [], "distance": "OK"},
            "integrity": {"beforeSuspicious": False, "afterSuspicious": False, "aiGeneratedLikelihood": "LOW", "screenRecaptureLikelihood": "LOW", "signals": []},
            "environment": {"dirtObscuring": False, "wetSurface": False, "glare": False, "notes": [], "confidenceReduced": False},
            "vehicleSignature": {"color": None, "bodyType": None, "visiblePlate": None},
            "conditionScore": None,
            "cleanliness": None,
            "estimatedCost": {"low": 0, "high": 0, "currency": _COST_CURRENCY},
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
        try:
            size_cm = float(it.get("sizeCm")) if it.get("sizeCm") is not None else None
            if size_cm is not None and (size_cm <= 0 or size_cm > 400):
                size_cm = None
            elif size_cm is not None:
                size_cm = round(size_cm, 1)
        except (TypeError, ValueError):
            size_cm = None
        rec = it.get("recommendation")
        rec = rec.upper() if isinstance(rec, str) and rec.upper() in _RECOMMENDATIONS else None
        items.append({
            "category": cat,
            "status": status,
            "location": (it.get("location") if isinstance(it.get("location"), str) else "")[:160],
            "severity": sev,
            "confidence": conf,
            "detail": (it.get("detail") if isinstance(it.get("detail"), str) else "")[:300],
            "sizeCm": size_cm,
            "sizeNote": (it.get("sizeNote") if isinstance(it.get("sizeNote"), str) else "")[:120] or None,
            "recommendation": rec,
            "box": _normalize_box(it.get("box")),
            "estimatedCost": _estimate_cost(cat, sev),
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
    new_low = sum(it["estimatedCost"]["low"] for it in items if it["status"] == "NEW")
    new_high = sum(it["estimatedCost"]["high"] for it in items if it["status"] == "NEW")
    score = parsed.get("conditionScore")
    try:
        score = max(0, min(100, int(score))) if score is not None else None
    except (TypeError, ValueError):
        score = None
    cleanliness = parsed.get("cleanliness")
    cleanliness = cleanliness.upper() if isinstance(cleanliness, str) and cleanliness.upper() in _CLEANLINESS else None
    return {
        "comparable": comparable,
        "notComparableReason": parsed.get("notComparableReason") if isinstance(parsed.get("notComparableReason"), str) else None,
        "items": items,
        "summary": (parsed.get("summary") if isinstance(parsed.get("summary"), str) else "")[:600],
        "counts": counts,
        "newIssueCount": new_issues,
        "overall": overall,
        "photoCheck": _normalize_photo_check(parsed, comparable),
        "integrity": _normalize_integrity(parsed),
        "environment": _normalize_environment(parsed),
        "vehicleSignature": _normalize_signature(parsed),
        "conditionScore": score,
        "cleanliness": cleanliness,
        "estimatedCost": {"low": new_low, "high": new_high, "currency": _COST_CURRENCY},
    }


async def _analyze_pair(*, before_path: str, before_mime: str, after_path: str, after_mime: str,
                        kind: str, angle: Optional[str], model_name: str, correlation_id: str) -> tuple[dict, str, int]:
    categories = EXTERIOR_CATEGORIES if kind == "EXTERIOR" else INTERIOR_CATEGORIES
    synonyms = _EXT_SYNONYMS if kind == "EXTERIOR" else _INT_SYNONYMS
    lines = _EXT_PROMPT_LINES if kind == "EXTERIOR" else _INT_PROMPT_LINES
    system = _EXT_SYSTEM if kind == "EXTERIOR" else _INT_SYSTEM
    enum_list = ",".join(f'"{c}"' for c in categories)
    parsed, model_label, latency_ms, err, usage = await call_vision_model_multi(
        provider=_provider(), model_name=model_name,
        system_message=system, user_prompt=_user_prompt(kind, lines, enum_list, angle),
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
    section["angle"] = angle
    section["tokenUsage"] = {**(usage or {}), "calls": 1}
    if kind == "EXTERIOR":
        section["label"] = f"Exterior — {_ANGLE_LABEL[angle]}" if angle in _ANGLE_LABEL else "Exterior"
    else:
        section["label"] = "Interior"
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


async def _maybe_auto_create_case(
    *, principal: dict, result: dict, report_fields: dict, correlation_id: str,
) -> dict:
    """Decision 1A=B / 1B=C / 1C=A: when NEW damage's estimated repair cost (high end) reaches
    the configured threshold, persist a minimal inspection session + AI findings and open a
    Damage Case so the anonymous trip lands in the main review/case queue."""
    rf = report_fields or {}
    cost_high = (result.get("costSummary") or {}).get("high", 0) or 0
    if result.get("overall") != "NEW_DAMAGE_FOUND" or cost_high < _AUTO_CASE_COST_THRESHOLD:
        return {"created": False, "reason": "below_threshold",
                "thresholdHigh": _AUTO_CASE_COST_THRESHOLD, "currency": _COST_CURRENCY}

    # Collect NEW findings across all sections.
    new_items: list[tuple[dict, dict]] = []  # (section, item)
    for section in result.get("sections", []):
        for it in section.get("items", []):
            if it.get("status") == "NEW":
                new_items.append((section, it))
    if not new_items:
        return {"created": False, "reason": "no_new_findings"}

    db = get_db()
    tenant_id = principal["tenantId"]
    try:
        # 1) Persist a minimal inspection session (anonymous trip → SPOT_CHECK / DI-Web).
        plate = (rf.get("vehiclePlate") or "").strip()
        refs = {"externalVehicleRef": plate or f"TRIP-{uuid.uuid4().hex[:10].upper()}"}
        if (rf.get("rentalId") or "").strip():
            refs["externalRentalAgreementRef"] = rf["rentalId"].strip()
        session = await inspection_service.create_inspection_session(
            principal=principal,
            payload={"inspectionType": InspectionType.SPOT_CHECK,
                     "sourceSystem": SourceSystem.DI_WEB, "references": refs},
            correlation_id=correlation_id,
        )
        session_id = session["id"]

        # 2) Persist a minimal AI analysis + one finding per NEW item.
        ts = datetime.now(timezone.utc)
        analysis = await db.di_ai_analyses.insert_one({
            "tenantId": tenant_id, "inspectionSessionId": session_id,
            "status": "COMPLETED", "source": "TRIP_INSPECTION",
            "modelVersion": result.get("modelVersion"), "totalFindings": len(new_items),
            "isAdvisory": True, "createdAt": ts, "completedAt": ts, "correlationId": correlation_id,
        })
        analysis_id = str(analysis.inserted_id)
        finding_ids: list[str] = []
        max_sev = None
        for section, it in new_items:
            sev = it.get("severity")
            if sev and (max_sev is None or _SEVERITY_RANK.get(sev, 0) > _SEVERITY_RANK.get(max_sev, 0)):
                max_sev = sev
            doc = {
                "tenantId": tenant_id, "aiAnalysisId": analysis_id, "inspectionSessionId": session_id,
                "inspectionImageId": None, "capturePosition": section.get("angle") or section.get("kind"),
                "damageType": _CATEGORY_TO_DAMAGE_TYPE.get(it.get("category"), DamageType.OTHER),
                "area": (it.get("location") or section.get("label") or "")[:160],
                "confidence": it.get("confidence", 0.0), "severity": sev,
                "approximateBoundingBox": it.get("box"), "status": AIFindingStatus.AI_DETECTED,
                "confidenceThreshold": None, "modelVersion": result.get("modelVersion"),
                "uncertaintyReason": None, "isAdvisory": True, "source": "TRIP_INSPECTION",
                "createdAt": ts, "correlationId": correlation_id,
            }
            res = await db.di_ai_findings.insert_one(doc)
            finding_ids.append(str(res.inserted_id))

        # 3) Open the Damage Case linked to the findings.
        descriptor_bits = []
        for k, label in (("customerName", "Customer"), ("vehiclePlate", "Plate"),
                         ("vehicleModel", "Vehicle"), ("rentalId", "Rental"), ("inspectorName", "Inspector")):
            v = (rf.get(k) or "").strip()
            if v:
                descriptor_bits.append(f"{label}: {v}")
        summaries = [s.get("summary") for s in result.get("sections", []) if s.get("summary")]
        description = (
            f"Auto-created from a Trip Inspection — {len(new_items)} new damage finding(s), "
            f"estimated repair up to {cost_high} {_COST_CURRENCY}. "
            + (" | ".join(descriptor_bits) + ". " if descriptor_bits else "")
            + (" ".join(summaries))
        ).strip()[:2000]
        case = await damage_case_service.create_case(
            principal=principal, inspection_session_id=session_id,
            damage_finding_ids=finding_ids, comparison_result_ids=[],
            case_type=CaseType.REPAIR_RELEVANT, severity_code=max_sev,
            description=description, correlation_id=correlation_id,
        )
        return {
            "created": True, "damageCaseId": case.get("damageCaseId"),
            "inspectionSessionId": session_id, "severityCode": max_sev,
            "caseType": CaseType.REPAIR_RELEVANT, "findings": len(finding_ids),
            "costHigh": cost_high, "currency": _COST_CURRENCY,
        }
    except Exception:
        # Auto-routing is best-effort and must never break the advisory analysis response.
        return {"created": False, "reason": "error"}


async def _analyze_pair_escalating(*, before_path: str, before_mime: str, after_path: str,
                                   after_mime: str, kind: str, angle: Optional[str], mode: str,
                                   correlation_id: str, before_client_meta: Optional[dict] = None,
                                   after_client_meta: Optional[dict] = None) -> tuple[dict, str, int]:
    """Analyze a pair on the mode's model; in Fast mode, re-run on Pro when the section looks
    uncertain/high-severity. Returns (section, model_label, total_latency_ms)."""
    section, model, lat = await _analyze_pair(
        before_path=before_path, before_mime=before_mime, after_path=after_path, after_mime=after_mime,
        kind=kind, angle=angle, model_name=_model_for_mode(mode), correlation_id=correlation_id,
    )
    escalated = False
    total = lat
    first_usage = section.get("tokenUsage") or {}
    if (mode or "fast").lower() == "fast" and _AUTO_ESCALATE and _should_escalate(section):
        section2, model, lat2 = await _analyze_pair(
            before_path=before_path, before_mime=before_mime, after_path=after_path, after_mime=after_mime,
            kind=kind, angle=angle, model_name=_model(), correlation_id=correlation_id,
        )
        second_usage = section2.get("tokenUsage") or {}
        section = section2
        section["tokenUsage"] = {
            "inputTokens": (first_usage.get("inputTokens") or 0) + (second_usage.get("inputTokens") or 0),
            "outputTokens": (first_usage.get("outputTokens") or 0) + (second_usage.get("outputTokens") or 0),
            "totalTokens": (first_usage.get("totalTokens") or 0) + (second_usage.get("totalTokens") or 0),
            "calls": 2,
        }
        total += lat2
        escalated = True
    section["escalated"] = escalated
    section["metadataCheck"] = build_metadata_check(
        before_path, after_path, before_client_meta, after_client_meta,
    )
    return section, model, total


async def get_budget(tenant_id: str) -> dict:
    db = get_db()
    doc = await db.di_tenant_ai_budget.find_one({"tenantId": tenant_id}) or {}
    return {
        "monthlyTokenBudget": int(doc.get("monthlyTokenBudget") or 0),
        "costPer1kTokens": float(doc.get("costPer1kTokens") or 0),
        "currency": doc.get("currency") or _COST_CURRENCY,
    }


async def set_budget(*, principal: dict, monthly_token_budget: int, cost_per_1k: float) -> dict:
    db = get_db()
    tenant_id = principal["tenantId"]
    await db.di_tenant_ai_budget.update_one(
        {"tenantId": tenant_id},
        {"$set": {
            "tenantId": tenant_id,
            "monthlyTokenBudget": max(0, int(monthly_token_budget or 0)),
            "costPer1kTokens": max(0.0, float(cost_per_1k or 0)),
            "currency": _COST_CURRENCY,
            "updatedAt": datetime.now(timezone.utc),
            "updatedBy": principal["id"],
        }},
        upsert=True,
    )
    return await _budget_status(tenant_id)


async def _budget_status(tenant_id: str) -> dict:
    db = get_db()
    cfg = await get_budget(tenant_id)
    budget = cfg["monthlyTokenBudget"]
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    days_in_month = calendar.monthrange(now.year, now.month)[1]
    day_of_month = now.day
    rows = await db.di_audit_records.aggregate([
        {"$match": {"tenantId": tenant_id,
                    "action": {"$in": ["QUICK_TRIP_ANALYSIS_RUN", "PLATE_OCR_RUN"]},
                    "timestamp": {"$gte": month_start}}},
        {"$group": {"_id": None, "tokens": {"$sum": {"$ifNull": ["$safeMetadata.totalTokens", 0]}}}},
    ]).to_list(1)
    mtd = rows[0]["tokens"] if rows else 0
    projected = round(mtd / day_of_month * days_in_month) if day_of_month else mtd
    cost_per_1k = cfg["costPer1kTokens"]

    def pct(v):
        return round(v / budget * 100) if budget else 0

    def cost(tok):
        return round(tok / 1000 * cost_per_1k, 2) if cost_per_1k else None

    return {
        "monthlyTokenBudget": budget,
        "costPer1kTokens": cost_per_1k,
        "currency": cfg["currency"],
        "monthToDateTokens": mtd,
        "projectedMonthTokens": projected,
        "daysElapsed": day_of_month,
        "daysInMonth": days_in_month,
        "daysLeft": days_in_month - day_of_month,
        "percentUsed": pct(mtd),
        "projectedPercent": pct(projected),
        "overBudget": bool(budget and projected > budget),
        "nearBudget": bool(budget and projected > budget * 0.8 and projected <= budget),
        "estCostMonthToDate": cost(mtd),
        "estCostProjected": cost(projected),
        "estBudgetCost": cost(budget),
    }


async def usage_summary(*, principal: dict, days: int = 30) -> dict:
    """Aggregate AI token usage from the audit log for the tenant (Trip Inspection runs),
    grouped by day — powers the admin 'AI usage' mini-dashboard."""
    days = max(1, min(int(days or 30), 180))
    db = get_db()
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    pipeline = [
        {"$match": {"tenantId": principal["tenantId"],
                    "action": {"$in": ["QUICK_TRIP_ANALYSIS_RUN", "PLATE_OCR_RUN"]},
                    "timestamp": {"$gte": cutoff}}},
        {"$project": {
            "day": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
            "tokens": {"$ifNull": ["$safeMetadata.totalTokens", 0]},
            "calls": {"$ifNull": ["$safeMetadata.aiCalls", 0]},
            "isTrip": {"$cond": [{"$eq": ["$action", "QUICK_TRIP_ANALYSIS_RUN"]}, 1, 0]},
        }},
        {"$group": {"_id": "$day", "tokens": {"$sum": "$tokens"},
                    "calls": {"$sum": "$calls"}, "inspections": {"$sum": "$isTrip"},
                    "tokenedInspections": {"$sum": {"$cond": [
                        {"$and": [{"$gt": ["$tokens", 0]}, {"$eq": ["$isTrip", 1]}]}, 1, 0]}}}},
        {"$sort": {"_id": 1}},
    ]
    rows = await db.di_audit_records.aggregate(pipeline).to_list(length=200)
    daily = [{"date": r["_id"], "tokens": r["tokens"], "calls": r["calls"],
              "inspections": r["inspections"]} for r in rows]
    total_tokens = sum(d["tokens"] for d in daily)
    total_calls = sum(d["calls"] for d in daily)
    total_inspections = sum(d["inspections"] for d in daily)
    tokened = sum(r.get("tokenedInspections", 0) for r in rows)
    return {
        "days": days,
        "totals": {
            "tokens": total_tokens, "calls": total_calls, "inspections": total_inspections,
            "avgTokensPerInspection": round(total_tokens / tokened) if tokened else 0,
        },
        "daily": daily,
        "budget": await _budget_status(principal["tenantId"]),
    }


async def analyze_trip(*, principal: dict, files: dict, report_fields: Optional[dict] = None,
                       mode: str = "fast", correlation_id: str) -> dict:
    """`files` maps slot -> (bytes, content_type). Supported slots:
    ext_{angle}_before / ext_{angle}_after for angle in front|rear|left|right|roof, and
    interior_before / interior_after. At least one complete pair is required; each provided
    pair is analyzed independently (in parallel)."""
    tenant_id = principal["tenantId"]

    # Discover the complete pairs present in the request.
    pairs = []  # (kind, angle, before_payload, after_payload, slot_prefix)
    for angle in _EXTERIOR_ANGLES:
        a = angle.lower()
        before = files.get(f"ext_{a}_before")
        after = files.get(f"ext_{a}_after")
        if before and after:
            pairs.append(("EXTERIOR", angle, before, after, f"ext_{a}"))
    int_before = files.get("interior_before")
    int_after = files.get("interior_after")
    if int_before and int_after:
        pairs.append(("INTERIOR", None, int_before, int_after, "interior"))

    if not pairs:
        raise DomainError(ErrorCode.VALIDATION_ERROR,
                          "Provide a Before and After photo for at least one area.", 400, "images")

    work = _TMP_ROOT / uuid.uuid4().hex
    work.mkdir(parents=True, exist_ok=True)
    sections: list[dict] = []
    models: list[str] = []
    total_latency = 0
    try:
        tasks = []
        for kind, angle, before, after, prefix in pairs:
            b_path, b_mime = _validate_and_save(work, f"{prefix}_before", before)
            a_path, a_mime = _validate_and_save(work, f"{prefix}_after", after)
            tasks.append(_analyze_pair_escalating(
                before_path=b_path, before_mime=b_mime, after_path=a_path, after_mime=a_mime,
                kind=kind, angle=angle, mode=mode, correlation_id=correlation_id,
            ))
        # Analyze every provided pair concurrently to minimize total latency.
        for section, model, lat in await asyncio.gather(*tasks):
            sections.append(section)
            models.append(model)
            total_latency += lat
    finally:
        shutil.rmtree(work, ignore_errors=True)

    model_version = models[0] if models else f"{_provider()}:{_model()}"
    result = _aggregate_result(sections, mode, model_version, report_fields or {})
    result["branding"] = await get_branding(tenant_id)
    result["autoCase"] = await _maybe_auto_create_case(
        principal=principal, result=result, report_fields=report_fields or {},
        correlation_id=correlation_id,
    )
    await write_audit(
        tenant_id=tenant_id, actor_id=principal["id"], actor_type=ActorType.USER,
        action=AuditAction.QUICK_TRIP_ANALYSIS_RUN, object_type=ObjectType.AI_ANALYSIS,
        object_id="trip-quick", correlation_id=correlation_id,
        safe_metadata={"overall": result["overall"], "newIssues": result["newIssueCount"],
                       "sections": [s.get("label") for s in sections],
                       "autoCaseCreated": bool(result["autoCase"].get("created")),
                       "totalTokens": result["tokenUsage"]["totalTokens"],
                       "aiCalls": result["tokenUsage"]["calls"],
                       "model": result["modelVersion"], "latencyMs": total_latency},
    )
    return result


def _plate_norm(p) -> str:
    return "".join(ch for ch in str(p or "").upper() if ch.isalnum())


def _vehicle_consistency(sections: list[dict], report_fields: Optional[dict]) -> dict:
    """Cross-angle vehicle identity check: compare AI-read colour/body-type/plate across
    exterior sections and against the plate the inspector entered."""
    sigs = [s.get("vehicleSignature") or {} for s in sections if s.get("kind") == "EXTERIOR"]
    colors = sorted({str(g.get("color")).strip().lower() for g in sigs if g.get("color")})
    bodies = sorted({str(g.get("bodyType")).strip().lower() for g in sigs if g.get("bodyType")})
    plates = sorted({_plate_norm(g.get("visiblePlate")) for g in sigs if _plate_norm(g.get("visiblePlate"))})
    warnings: list[str] = []
    if len(colors) > 1:
        warnings.append("Different vehicle colours seen across the photos: " + ", ".join(colors) + ".")
    if len(bodies) > 1:
        warnings.append("Different body types seen across the photos: " + ", ".join(bodies) + ".")
    if len(plates) > 1:
        warnings.append("More than one license plate read across the photos: " + ", ".join(plates) + ".")
    entered_raw = ((report_fields or {}).get("vehiclePlate") or "").strip()
    entered = _plate_norm(entered_raw)
    plate_match = None
    if entered and plates:
        plate_match = entered in plates
        if not plate_match:
            warnings.append(
                f"Entered plate '{entered_raw}' does not match the plate read in the photos "
                f"({', '.join(plates)})."
            )
    return {
        "consistent": len(warnings) == 0,
        "colors": colors, "bodyTypes": bodies, "platesRead": plates,
        "enteredPlate": entered_raw or None, "plateMatch": plate_match,
        "warnings": warnings,
    }


def _aggregate_result(sections: list[dict], mode: str, model_version: str,
                      report_fields: Optional[dict] = None) -> dict:
    """Build the trip-level aggregate from already-analyzed section dicts. Defensive against
    partial/client-supplied sections (used by both the single-shot and streaming flows)."""
    def _ec(s):
        return s.get("estimatedCost") or {"low": 0, "high": 0, "currency": _COST_CURRENCY}
    def _pc(s):
        return s.get("photoCheck") or {}
    def _ig(s):
        return s.get("integrity") or {}
    def _env(s):
        return s.get("environment") or {}

    new_total = sum(int(s.get("newIssueCount") or 0) for s in sections)
    any_comparable = any(s.get("comparable") for s in sections)
    overall = ("NEW_DAMAGE_FOUND" if new_total > 0
               else "NO_NEW_DAMAGE" if any_comparable
               else "NOT_COMPARABLE")
    cost_low = sum(int(_ec(s).get("low") or 0) for s in sections)
    cost_high = sum(int(_ec(s).get("high") or 0) for s in sections)
    scores = [s.get("conditionScore") for s in sections if s.get("conditionScore") is not None]
    condition_score = min(scores) if scores else None
    cleanliness = _worst_cleanliness([s.get("cleanliness") for s in sections])
    photo_warnings = any(
        (not _pc(s).get("beforeUsable", True)) or (not _pc(s).get("afterUsable", True))
        or (not _pc(s).get("sameVehicle", True)) or bool(_pc(s).get("issues"))
        or (not _pc(s).get("angleCorrect", True)) or (not _pc(s).get("fullyVisible", True))
        or ((_pc(s).get("distance") or "OK") != "OK")
        for s in sections
    )
    integrity_warnings = any(
        _ig(s).get("beforeSuspicious") or _ig(s).get("afterSuspicious")
        or (_ig(s).get("aiGeneratedLikelihood") or "LOW") != "LOW"
        or (_ig(s).get("screenRecaptureLikelihood") or "LOW") != "LOW"
        or bool(_ig(s).get("signals"))
        for s in sections
    )
    environment_warnings = any(
        _env(s).get("dirtObscuring") or _env(s).get("wetSurface") or _env(s).get("glare")
        or _env(s).get("confidenceReduced")
        for s in sections
    )
    metadata_warnings = any(
        (s.get("metadataCheck") or {}).get("warnings") for s in sections
    )
    vehicle_consistency = _vehicle_consistency(sections, report_fields)
    captured_angles = [s.get("angle") for s in sections if s.get("kind") == "EXTERIOR" and s.get("angle")]
    escalated_count = sum(1 for s in sections if s.get("escalated"))
    token_usage = {
        "inputTokens": sum((s.get("tokenUsage") or {}).get("inputTokens", 0) or 0 for s in sections),
        "outputTokens": sum((s.get("tokenUsage") or {}).get("outputTokens", 0) or 0 for s in sections),
        "totalTokens": sum((s.get("tokenUsage") or {}).get("totalTokens", 0) or 0 for s in sections),
        "calls": sum((s.get("tokenUsage") or {}).get("calls", 0) or 0 for s in sections),
    }
    coverage = {
        "capturedAngles": captured_angles,
        "missingAngles": [a for a in _EXTERIOR_ANGLES if a not in captured_angles],
        "totalAngles": len(_EXTERIOR_ANGLES),
        "capturedCount": len(captured_angles),
        "interiorCaptured": any(s.get("kind") == "INTERIOR" for s in sections),
        "fullWalkaround": len(captured_angles) == len(_EXTERIOR_ANGLES),
    }
    return {
        "sections": sections,
        "overall": overall,
        "newIssueCount": new_total,
        "modelVersion": model_version,
        "isAdvisory": True,
        "costSummary": {"low": cost_low, "high": cost_high, "currency": _COST_CURRENCY},
        "conditionScore": condition_score,
        "cleanliness": cleanliness,
        "hasPhotoWarnings": photo_warnings,
        "hasIntegrityWarnings": integrity_warnings,
        "hasEnvironmentWarnings": environment_warnings,
        "hasMetadataWarnings": metadata_warnings,
        "vehicleConsistency": vehicle_consistency,
        "coverage": coverage,
        "escalatedCount": escalated_count,
        "tokenUsage": token_usage,
        "mode": (mode or "fast").lower(),
    }


async def analyze_section(*, principal: dict, kind: str, angle: Optional[str],
                          before: tuple, after: tuple, mode: str, correlation_id: str,
                          before_meta: Optional[dict] = None,
                          after_meta: Optional[dict] = None) -> dict:
    """Analyze a SINGLE before/after pair and return just its section (no aggregation, no
    auto-case). Used by the streaming flow so the UI can render each area as it completes."""
    kind = (kind or "EXTERIOR").upper()
    if kind not in ("EXTERIOR", "INTERIOR"):
        raise DomainError(ErrorCode.VALIDATION_ERROR, "Invalid kind.", 400, "kind")
    angle = angle.upper() if (kind == "EXTERIOR" and angle) else None
    if kind == "EXTERIOR" and angle not in _EXTERIOR_ANGLES:
        raise DomainError(ErrorCode.VALIDATION_ERROR, "Invalid angle.", 400, "angle")
    if not before or not after:
        raise DomainError(ErrorCode.VALIDATION_ERROR, "Both a Before and an After photo are required.", 400, "images")

    prefix = f"ext_{angle.lower()}" if kind == "EXTERIOR" else "interior"
    work = _TMP_ROOT / uuid.uuid4().hex
    work.mkdir(parents=True, exist_ok=True)
    try:
        b_path, b_mime = _validate_and_save(work, f"{prefix}_before", before)
        a_path, a_mime = _validate_and_save(work, f"{prefix}_after", after)
        section, model, _lat = await _analyze_pair_escalating(
            before_path=b_path, before_mime=b_mime, after_path=a_path, after_mime=a_mime,
            kind=kind, angle=angle, mode=mode, correlation_id=correlation_id,
            before_client_meta=before_meta, after_client_meta=after_meta,
        )
    finally:
        shutil.rmtree(work, ignore_errors=True)
    section["modelVersion"] = model
    return section


_OCR_SYSTEM = (
    "You are the Damage Intelligence vehicle-identification OCR agent. You read license "
    "plates and VINs from close-up photos. Respond with STRICT JSON only — no prose."
)
_OCR_PROMPT = (
    "Read the vehicle identification from this photo (license plate close-up, windshield VIN "
    "plate, or door-jamb sticker).\n"
    "Return JSON EXACTLY in this shape:\n"
    "{\n"
    '  "plate": { "text": plate in Latin letters/digits (e.g. "ABC 1234") or null, '
    '"textAr": Arabic plate text if printed, else null, '
    '"region": issuing country/state if identifiable else null, "confidence": 0..1 },\n'
    '  "vin": { "text": the 17-character VIN or null, "confidence": 0..1 },\n'
    '  "vehicle": { "color": one lowercase word or null, "make": string or null, '
    '"model": string or null, "year": string or null }\n'
    "}\n"
    "Saudi plates print both Arabic and Latin characters — return the Latin form in plate.text. "
    "If nothing is readable, use nulls."
)


async def read_plate(*, principal: dict, image: tuple, correlation_id: str) -> dict:
    """Dedicated plate/VIN OCR on a single close-up photo (always Fast model)."""
    work = _TMP_ROOT / uuid.uuid4().hex
    work.mkdir(parents=True, exist_ok=True)
    try:
        path, mime = _validate_and_save(work, "plate", image)
        parsed, model_label, latency_ms, err, usage = await call_vision_model_multi(
            provider=_provider(), model_name=_fast_model(),
            system_message=_OCR_SYSTEM, user_prompt=_OCR_PROMPT,
            images=[{"path": path, "mime": mime}], correlation_id=correlation_id,
        )
    finally:
        shutil.rmtree(work, ignore_errors=True)
    if err is not None:
        raise DomainError(ErrorCode.INTERNAL_ERROR,
                          "The OCR engine is temporarily unavailable. Please retry.", 503)
    parsed = parsed if isinstance(parsed, dict) else {}

    def _conf(v):
        try:
            return max(0.0, min(1.0, float(v)))
        except (TypeError, ValueError):
            return 0.0

    pl = parsed.get("plate") if isinstance(parsed.get("plate"), dict) else {}
    plate_text = (pl.get("text") or "").strip().upper()[:24] or None if isinstance(pl.get("text"), str) else None
    vn = parsed.get("vin") if isinstance(parsed.get("vin"), dict) else {}
    vin_text = vehicle_registry_service.vin_norm(vn.get("text")) or None
    veh = parsed.get("vehicle") if isinstance(parsed.get("vehicle"), dict) else {}

    result = {
        "plate": {
            "text": plate_text,
            "textAr": (pl.get("textAr") or "").strip()[:24] or None if isinstance(pl.get("textAr"), str) else None,
            "region": (pl.get("region") or "").strip()[:40] or None if isinstance(pl.get("region"), str) else None,
            "confidence": _conf(pl.get("confidence")),
        },
        "vin": {"text": vin_text, "confidence": _conf(vn.get("confidence")),
                "valid": len(vin_text or "") == 17},
        "vehicle": {k: ((veh.get(k) or "").strip()[:40] or None if isinstance(veh.get(k), str) else None)
                    for k in ("color", "make", "model", "year")},
        "modelVersion": model_label,
        "tokenUsage": {**(usage or {}), "calls": 1},
    }
    await write_audit(
        tenant_id=principal["tenantId"], actor_id=principal["id"], actor_type=ActorType.USER,
        action=AuditAction.PLATE_OCR_RUN, object_type=ObjectType.AI_ANALYSIS,
        object_id="plate-ocr", correlation_id=correlation_id,
        safe_metadata={"plateRead": bool(plate_text), "vinRead": bool(vin_text),
                       "totalTokens": (usage or {}).get("totalTokens", 0), "aiCalls": 1,
                       "model": model_label, "latencyMs": latency_ms},
    )
    return result


async def finalize_trip(*, principal: dict, sections: list[dict], report_fields: Optional[dict],
                        mode: str, correlation_id: str, save_to_history: bool = True,
                        ocr: Optional[dict] = None) -> dict:
    """Aggregate already-analyzed sections (from analyze_section), attach branding, and run
    auto-case routing once over the whole set. Sections are advisory; trip remains anonymous."""
    sections = sections or []
    model_version = next((s.get("modelVersion") for s in sections if s.get("modelVersion")),
                         f"{_provider()}:{_model_for_mode(mode)}")
    result = _aggregate_result(sections, mode, model_version, report_fields or {})
    result["branding"] = await get_branding(principal["tenantId"])
    result["autoCase"] = await _maybe_auto_create_case(
        principal=principal, result=result, report_fields=report_fields or {},
        correlation_id=correlation_id,
    )
    if save_to_history:
        try:
            result["vehicleLink"] = await vehicle_registry_service.link_trip(
                principal=principal, result=result, report_fields=report_fields,
                ocr=ocr, correlation_id=correlation_id,
            )
        except Exception:
            result["vehicleLink"] = {"linked": False, "reason": "error"}
    else:
        result["vehicleLink"] = {"linked": False, "reason": "disabled"}
    await write_audit(
        tenant_id=principal["tenantId"], actor_id=principal["id"], actor_type=ActorType.USER,
        action=AuditAction.QUICK_TRIP_ANALYSIS_RUN, object_type=ObjectType.AI_ANALYSIS,
        object_id="trip-quick", correlation_id=correlation_id,
        safe_metadata={"overall": result["overall"], "newIssues": result["newIssueCount"],
                       "sections": [s.get("label") for s in sections], "streamed": True,
                       "autoCaseCreated": bool(result["autoCase"].get("created")),
                       "vehicleLinked": bool(result["vehicleLink"].get("linked")),
                       "totalTokens": result["tokenUsage"]["totalTokens"],
                       "aiCalls": result["tokenUsage"]["calls"],
                       "model": result["modelVersion"]},
    )
    return result
