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
import os
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from api.middleware.safe_errors import DomainError
from application.ai.gemini_client import call_vision_model_multi
from application.services import damage_case_service, inspection_service
from application.services.audit_service import write_audit
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
        "conservative; if unsure, set status UNCERTAIN.\n"
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
        '     "vehicleMismatchReason": string or null\n'
        "  },\n"
        '  "integrity": {\n'
        '     "beforeSuspicious": true or false (does the BEFORE photo show signs of digital editing, AI generation, or being a photo-of-a-screen),\n'
        '     "afterSuspicious": true or false (same for the AFTER photo),\n'
        '     "aiGeneratedLikelihood": one of ["LOW","MEDIUM","HIGH"] (likelihood either photo is AI-generated or manipulated),\n'
        '     "signals": [ short strings describing any tampering/AI signals e.g. "cloned region", "inconsistent shadows", "screen moire pattern", "warped edges" ]\n'
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


def _normalize_photo_check(parsed: dict, comparable: bool) -> dict:
    pc = parsed.get("photoCheck") if isinstance(parsed.get("photoCheck"), dict) else {}
    issues = pc.get("issues")
    issues = [str(s)[:140] for s in issues if isinstance(s, str)][:6] if isinstance(issues, list) else []
    return {
        "beforeUsable": bool(pc.get("beforeUsable", True)),
        "afterUsable": bool(pc.get("afterUsable", True)),
        "issues": issues,
        "sameVehicle": bool(pc.get("sameVehicle", comparable)),
        "vehicleMismatchReason": pc.get("vehicleMismatchReason") if isinstance(pc.get("vehicleMismatchReason"), str) else None,
    }


def _normalize_integrity(parsed: dict) -> dict:
    ig = parsed.get("integrity") if isinstance(parsed.get("integrity"), dict) else {}
    signals = ig.get("signals")
    signals = [str(s)[:140] for s in signals if isinstance(s, str)][:6] if isinstance(signals, list) else []
    likelihood = ig.get("aiGeneratedLikelihood")
    likelihood = likelihood.upper() if isinstance(likelihood, str) and likelihood.upper() in _AI_LIKELIHOOD else "LOW"
    return {
        "beforeSuspicious": bool(ig.get("beforeSuspicious", False)),
        "afterSuspicious": bool(ig.get("afterSuspicious", False)),
        "aiGeneratedLikelihood": likelihood,
        "signals": signals,
    }


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
            "photoCheck": {"beforeUsable": False, "afterUsable": False, "issues": ["analysis could not be completed"], "sameVehicle": False, "vehicleMismatchReason": None},
            "integrity": {"beforeSuspicious": False, "afterSuspicious": False, "aiGeneratedLikelihood": "LOW", "signals": []},
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
        "conditionScore": score,
        "cleanliness": cleanliness,
        "estimatedCost": {"low": new_low, "high": new_high, "currency": _COST_CURRENCY},
    }


async def _analyze_pair(*, before_path: str, before_mime: str, after_path: str, after_mime: str,
                        kind: str, angle: Optional[str], correlation_id: str) -> tuple[dict, str, int]:
    categories = EXTERIOR_CATEGORIES if kind == "EXTERIOR" else INTERIOR_CATEGORIES
    synonyms = _EXT_SYNONYMS if kind == "EXTERIOR" else _INT_SYNONYMS
    lines = _EXT_PROMPT_LINES if kind == "EXTERIOR" else _INT_PROMPT_LINES
    system = _EXT_SYSTEM if kind == "EXTERIOR" else _INT_SYSTEM
    enum_list = ",".join(f'"{c}"' for c in categories)
    parsed, model_label, latency_ms, err = await call_vision_model_multi(
        provider=_provider(), model_name=_model(),
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


async def analyze_trip(*, principal: dict, files: dict, report_fields: Optional[dict] = None,
                       correlation_id: str) -> dict:
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
            tasks.append(_analyze_pair(
                before_path=b_path, before_mime=b_mime, after_path=a_path, after_mime=a_mime,
                kind=kind, angle=angle, correlation_id=correlation_id,
            ))
        # Analyze every provided pair concurrently to minimize total latency.
        for section, model, lat in await asyncio.gather(*tasks):
            sections.append(section)
            models.append(model)
            total_latency += lat
    finally:
        shutil.rmtree(work, ignore_errors=True)

    new_total = sum(s["newIssueCount"] for s in sections)
    any_comparable = any(s["comparable"] for s in sections)
    overall = ("NEW_DAMAGE_FOUND" if new_total > 0
               else "NO_NEW_DAMAGE" if any_comparable
               else "NOT_COMPARABLE")

    cost_low = sum(s["estimatedCost"]["low"] for s in sections)
    cost_high = sum(s["estimatedCost"]["high"] for s in sections)
    scores = [s["conditionScore"] for s in sections if s.get("conditionScore") is not None]
    condition_score = min(scores) if scores else None
    cleanliness = _worst_cleanliness([s.get("cleanliness") for s in sections])
    photo_warnings = any(
        (not s["photoCheck"]["beforeUsable"]) or (not s["photoCheck"]["afterUsable"])
        or (not s["photoCheck"]["sameVehicle"]) or bool(s["photoCheck"]["issues"])
        for s in sections
    )
    integrity_warnings = any(
        s["integrity"]["beforeSuspicious"] or s["integrity"]["afterSuspicious"]
        or s["integrity"]["aiGeneratedLikelihood"] != "LOW" or bool(s["integrity"]["signals"])
        for s in sections
    )

    captured_angles = [s["angle"] for s in sections if s["kind"] == "EXTERIOR" and s["angle"]]
    coverage = {
        "capturedAngles": captured_angles,
        "missingAngles": [a for a in _EXTERIOR_ANGLES if a not in captured_angles],
        "totalAngles": len(_EXTERIOR_ANGLES),
        "capturedCount": len(captured_angles),
        "interiorCaptured": any(s["kind"] == "INTERIOR" for s in sections),
        "fullWalkaround": len(captured_angles) == len(_EXTERIOR_ANGLES),
    }

    result = {
        "sections": sections,
        "overall": overall,
        "newIssueCount": new_total,
        "modelVersion": models[0] if models else f"{_provider()}:{_model()}",
        "isAdvisory": True,
        "branding": await get_branding(tenant_id),
        "costSummary": {"low": cost_low, "high": cost_high, "currency": _COST_CURRENCY},
        "conditionScore": condition_score,
        "cleanliness": cleanliness,
        "hasPhotoWarnings": photo_warnings,
        "hasIntegrityWarnings": integrity_warnings,
        "coverage": coverage,
    }

    result["autoCase"] = await _maybe_auto_create_case(
        principal=principal, result=result, report_fields=report_fields or {},
        correlation_id=correlation_id,
    )

    await write_audit(
        tenant_id=tenant_id, actor_id=principal["id"], actor_type=ActorType.USER,
        action=AuditAction.QUICK_TRIP_ANALYSIS_RUN, object_type=ObjectType.AI_ANALYSIS,
        object_id="trip-quick", correlation_id=correlation_id,
        safe_metadata={"overall": overall, "newIssues": new_total,
                       "sections": [s["label"] for s in sections],
                       "autoCaseCreated": bool(result["autoCase"].get("created")),
                       "model": result["modelVersion"], "latencyMs": total_latency},
    )
    return result
