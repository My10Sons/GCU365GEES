"""
Repository Traceability:
- Purpose: Deterministic photo-metadata (EXIF) verification for Trip Inspection uploads.
  Flags missing metadata, stale/future capture timestamps, editing software, and
  Before/After chronology problems. Client-extracted metadata (from the ORIGINAL file,
  before browser re-encoding strips EXIF) is merged in as a fallback.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone

from PIL import ExifTags, Image

_EDIT_SOFTWARE = (
    "photoshop", "lightroom", "gimp", "snapseed", "picsart", "canva", "pixlr",
    "affinity", "luminar", "facetune", "photopea", "remini", "polarr",
)

_TAG_DT_ORIGINAL = 36867
_TAG_DT = 306
_TAG_SOFTWARE = 305
_TAG_MAKE = 271
_TAG_MODEL = 272


def _max_age_hours() -> float:
    return float(os.environ.get("DI_TRIP_EXIF_MAX_AGE_HOURS", "72"))


def _to_deg(values, ref):
    try:
        d, m, s = (float(v) for v in values)
        deg = d + m / 60 + s / 3600
        if ref in ("S", "W"):
            deg = -deg
        return round(deg, 6)
    except Exception:
        return None


def extract_photo_meta(path: str) -> dict:
    meta = {"hasExif": False, "capturedAt": None, "gpsLat": None, "gpsLon": None,
            "software": None, "cameraModel": None}
    try:
        with Image.open(path) as im:
            exif = im.getexif()
            if not exif or len(exif) == 0:
                return meta
            meta["hasExif"] = True
            dt = None
            try:
                dt = exif.get_ifd(ExifTags.IFD.Exif).get(_TAG_DT_ORIGINAL)
            except Exception:
                pass
            dt = dt or exif.get(_TAG_DT)
            if isinstance(dt, str):
                try:
                    meta["capturedAt"] = datetime.strptime(
                        dt.strip(), "%Y:%m:%d %H:%M:%S"
                    ).replace(tzinfo=timezone.utc).isoformat()
                except ValueError:
                    pass
            sw = exif.get(_TAG_SOFTWARE)
            if isinstance(sw, str) and sw.strip():
                meta["software"] = sw.strip()[:80]
            cam = f"{exif.get(_TAG_MAKE) or ''} {exif.get(_TAG_MODEL) or ''}".strip()
            if cam:
                meta["cameraModel"] = cam[:80]
            try:
                gps = exif.get_ifd(ExifTags.IFD.GPSInfo)
                if gps:
                    meta["gpsLat"] = _to_deg(gps.get(2), gps.get(1))
                    meta["gpsLon"] = _to_deg(gps.get(4), gps.get(3))
            except Exception:
                pass
    except Exception:
        pass
    return meta


def _merge_client_meta(server_meta: dict, client_meta: dict | None) -> dict:
    # Browser canvas re-encoding strips EXIF, so trust the client's extraction of the
    # ORIGINAL file when the uploaded bytes carry none.
    if server_meta.get("hasExif") or not isinstance(client_meta, dict):
        return server_meta
    merged = dict(server_meta)
    merged["hasExif"] = bool(client_meta.get("hasExif"))
    for k in ("software", "cameraModel"):
        v = client_meta.get(k)
        if isinstance(v, str) and v.strip():
            merged[k] = v.strip()[:80]
    v = client_meta.get("capturedAt")
    if isinstance(v, str) and v.strip():
        merged["capturedAt"] = v.strip()[:40]
    for k in ("gpsLat", "gpsLon"):
        v = client_meta.get(k)
        if isinstance(v, (int, float)):
            merged[k] = round(float(v), 6)
    return merged


def _parse_dt(value) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _evaluate(meta: dict) -> dict:
    out = dict(meta)
    out.update({"ageHours": None, "stale": False, "futureTimestamp": False, "softwareEdited": False})
    warnings: list[str] = []
    cap = _parse_dt(meta.get("capturedAt"))
    if not meta.get("hasExif"):
        warnings.append("no capture metadata (EXIF) — may be a downloaded, forwarded, or screenshot image")
    elif cap is None:
        warnings.append("capture time missing from photo metadata")
    if cap is not None:
        age = (datetime.now(timezone.utc) - cap).total_seconds() / 3600
        out["ageHours"] = round(age, 1)
        if age < -24:
            out["futureTimestamp"] = True
            warnings.append("capture timestamp is in the future — device clock issue or edited metadata")
        elif age > _max_age_hours():
            out["stale"] = True
            warnings.append(f"taken about {int(age // 24)} day(s) ago — not a fresh capture")
    sw = (meta.get("software") or "").lower()
    if sw and any(e in sw for e in _EDIT_SOFTWARE):
        out["softwareEdited"] = True
        warnings.append(f"processed with editing software ({meta['software']})")
    out["warnings"] = warnings
    return out


def build_metadata_check(before_path: str, after_path: str,
                         before_client_meta: dict | None = None,
                         after_client_meta: dict | None = None) -> dict:
    before = _evaluate(_merge_client_meta(extract_photo_meta(before_path), before_client_meta))
    after = _evaluate(_merge_client_meta(extract_photo_meta(after_path), after_client_meta))
    warnings = ([f"Before photo: {w}" for w in before["warnings"]]
                + [f"After photo: {w}" for w in after["warnings"]])
    b, a = _parse_dt(before.get("capturedAt")), _parse_dt(after.get("capturedAt"))
    if b and a and a < b:
        warnings.append("Capture order looks wrong — the After photo was taken before the Before photo.")
    return {"before": before, "after": after, "warnings": warnings[:8]}
