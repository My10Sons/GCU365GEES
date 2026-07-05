"""
Repository Traceability:
- Purpose: Hosted external-report service. Persists annotated before/after photos and
  the finalized trip result under a random public token so rental-system counterparts
  (e.g. GCU365 CROMS) can view a rendered report (HTML) or download a PDF without
  building their own UI. The 40-hex-char token IS the credential.
"""
from __future__ import annotations

import html as html_mod
import io
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib import colors as rl_colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (Image as RLImage, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

from infrastructure.db.mongo import get_db
from infrastructure.storage.local_storage import storage_root

_MAX_SIDE = 1280
_IMG_NAME_RE = re.compile(r"^s\d{1,2}_(before|after)\.jpg$")
_STATUS_RGB = {"NEW": (225, 29, 72), "PRE_EXISTING": (100, 116, 139),
               "RESOLVED": (5, 150, 105), "UNCERTAIN": (217, 119, 6)}
_VERDICT = {
    "NEW_DAMAGE_FOUND": ("New damage found", "#be123c", "#fff1f2"),
    "NO_NEW_DAMAGE": ("No new damage", "#047857", "#ecfdf5"),
    "NOT_COMPARABLE": ("Photos not comparable", "#b45309", "#fffbeb"),
}
_SEV_COLOR = {"HIGH": "#be123c", "MEDIUM": "#b45309", "LOW": "#475569"}


def _report_dir(tenant_id: str, token: str) -> Path:
    return storage_root() / "tenants" / tenant_id / "damage-intelligence" / "ext-reports" / token


def _font(size: int):
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
    except OSError:
        try:
            return ImageFont.load_default(size=size)
        except TypeError:
            return ImageFont.load_default()


def _resize(im: Image.Image) -> Image.Image:
    im = im.convert("RGB")
    w, h = im.size
    scale = _MAX_SIDE / max(w, h)
    if scale < 1:
        im = im.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    return im


def _save_plain(raw: bytes, path: Path) -> None:
    _resize(Image.open(io.BytesIO(raw))).save(path, "JPEG", quality=82)


def _save_annotated(raw: bytes, items: list, path: Path) -> None:
    im = _resize(Image.open(io.BytesIO(raw)))
    draw = ImageDraw.Draw(im)
    w, h = im.size
    lw = max(3, int(min(w, h) * 0.005))
    font = _font(max(18, int(min(w, h) * 0.035)))
    for it in items:
        box = it.get("box") or {}
        try:
            x, y = float(box["x"]) * w, float(box["y"]) * h
            bw, bh = float(box["w"]) * w, float(box["h"]) * h
        except (KeyError, TypeError, ValueError):
            continue
        color = _STATUS_RGB.get(it.get("status"), (225, 29, 72))
        draw.rectangle([x, y, x + bw, y + bh], outline=color, width=lw)
        marker = str(it.get("marker") or "")
        if marker:
            tb = draw.textbbox((0, 0), marker, font=font)
            tw, th = tb[2] - tb[0], tb[3] - tb[1]
            pad = max(5, lw)
            bx0 = min(max(0, x), w - tw - 2 * pad)
            by0 = max(0, y - th - 3 * pad)
            draw.rectangle([bx0, by0, bx0 + tw + 2 * pad, by0 + th + 2 * pad], fill=color)
            draw.text((bx0 + pad, by0 + pad - tb[1]), marker, fill=(255, 255, 255), font=font)
    im.save(path, "JPEG", quality=82)


async def create_report(*, tenant_id: str, job_id: str, report_fields: dict,
                        sections: list, images: list) -> str:
    """Assign marker numbers to boxed findings (mutates sections), store annotated
    photos, and insert the report doc. The result is attached after finalize."""
    token = uuid.uuid4().hex + uuid.uuid4().hex[:8]
    d = _report_dir(tenant_id, token)
    d.mkdir(parents=True, exist_ok=True)
    stored = []
    for i, (sec, img) in enumerate(zip(sections, images)):
        boxed = [it for it in (sec.get("items") or []) if isinstance(it.get("box"), dict)]
        for n, it in enumerate(boxed, start=1):
            it["marker"] = n
        before_name, after_name = f"s{i}_before.jpg", f"s{i}_after.jpg"
        try:
            _save_plain(img["before"][0], d / before_name)
            _save_annotated(img["after"][0], boxed, d / after_name)
        except Exception:
            before_name = after_name = None
        stored.append({"index": i, "slot": img.get("slot"), "label": sec.get("label"),
                       "before": before_name, "after": after_name})
    await get_db().di_ext_reports.insert_one({
        "token": token, "tenantId": tenant_id, "jobId": job_id,
        "createdAt": datetime.now(timezone.utc),
        "reportFields": report_fields or {}, "images": stored, "result": None,
    })
    return token


async def attach_result(token: str, result: dict) -> None:
    slim = {k: v for k, v in result.items() if k != "tokenUsage"}
    await get_db().di_ext_reports.update_one({"token": token}, {"$set": {"result": slim}})


async def get_report(token: str) -> Optional[dict]:
    if not re.fullmatch(r"[0-9a-f]{40}", token or ""):
        return None
    return await get_db().di_ext_reports.find_one({"token": token})


def image_path(doc: dict, name: str) -> Optional[Path]:
    if not _IMG_NAME_RE.fullmatch(name or ""):
        return None
    known = {n for img in doc.get("images", []) for n in (img.get("before"), img.get("after")) if n}
    if name not in known:
        return None
    p = _report_dir(doc["tenantId"], doc["token"]) / name
    return p if p.exists() else None


def _esc(v) -> str:
    return html_mod.escape(str(v)) if v not in (None, "") else "—"


def _cost_str(c: Optional[dict]) -> str:
    if not c or (not c.get("low") and not c.get("high")):
        return "—"
    return f"{c.get('low', 0)}–{c.get('high', 0)} {c.get('currency', 'SAR')}"


_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',Arial,Helvetica,sans-serif;background:#f1f5f9;color:#0f172a;line-height:1.5}
.wrap{max-width:960px;margin:0 auto;padding:28px 20px 60px}
.card{background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:22px;margin-bottom:18px}
.hdr{display:flex;align-items:center;gap:14px;flex-wrap:wrap}
.brand{font-size:13px;letter-spacing:.18em;text-transform:uppercase;color:#64748b}
h1{font-size:24px;margin-top:4px}
h2{font-size:15px;margin-bottom:10px;color:#0f172a}
.verdict{display:inline-block;padding:6px 14px;border-radius:999px;font-weight:700;font-size:14px}
.meta{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px;margin-top:14px}
.meta div{background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:8px 12px}
.meta .k{font-size:10px;text-transform:uppercase;letter-spacing:.12em;color:#64748b}
.meta .v{font-size:14px;font-weight:600;margin-top:2px}
table{width:100%;border-collapse:collapse;font-size:12.5px}
th{background:#f8fafc;text-align:left;padding:7px 9px;border-bottom:2px solid #e2e8f0;font-size:10.5px;text-transform:uppercase;letter-spacing:.08em;color:#475569}
td{padding:7px 9px;border-bottom:1px solid #f1f5f9;vertical-align:top}
.imgs{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:12px 0}
.imgs figure img{width:100%;border-radius:8px;border:1px solid #e2e8f0;display:block}
.imgs figcaption{font-size:11px;color:#64748b;margin-top:4px;text-transform:uppercase;letter-spacing:.1em}
.chip{display:inline-block;font-size:10.5px;font-weight:700;padding:2px 9px;border-radius:999px}
.warn{background:#fffbeb;border:1px solid #fcd34d;color:#92400e;border-radius:8px;padding:10px 14px;font-size:13px;margin-top:10px}
.okflag{background:#ecfdf5;border:1px solid #a7f3d0;color:#065f46;border-radius:8px;padding:10px 14px;font-size:13px;margin-top:10px}
.foot{font-size:11px;color:#94a3b8;text-align:center;margin-top:26px}
.actions{margin:14px 0 4px;display:flex;gap:10px}
.btn{display:inline-block;background:#0f172a;color:#fff;text-decoration:none;font-size:13px;font-weight:600;padding:9px 18px;border-radius:8px;border:none;cursor:pointer}
.btn.sec{background:#fff;color:#0f172a;border:1px solid #cbd5e1}
@media print{.actions{display:none}body{background:#fff}.card{border:none;padding:10px 0}}
@media (max-width:640px){.imgs{grid-template-columns:1fr}}
"""


def render_html(doc: dict) -> str:
    token = doc["token"]
    base = f"/api/v1/damage-intelligence/public/reports/{token}"
    result = doc.get("result")
    if not result:
        return ("<!doctype html><html><head><meta charset='utf-8'>"
                "<meta http-equiv='refresh' content='6'><title>Damage Intelligence — Report</title>"
                f"<style>{_CSS}</style></head><body><div class='wrap'><div class='card'>"
                "<div class='brand'>Damage Intelligence</div><h1>Analyzing photos…</h1>"
                "<p style='margin-top:8px;color:#475569'>This inspection is still being processed. "
                "The page refreshes automatically.</p></div></div></body></html>")

    branding = result.get("branding") or {}
    company = branding.get("companyName") or "Damage Intelligence"
    rf = doc.get("reportFields") or {}
    label, color, bg = _VERDICT.get(result.get("overall"), ("Unknown", "#475569", "#f8fafc"))
    cost = result.get("costSummary") or {}
    ver = result.get("verification") or {
        "hasPhotoWarnings": result.get("hasPhotoWarnings"),
        "hasIntegrityWarnings": result.get("hasIntegrityWarnings"),
        "hasEnvironmentWarnings": result.get("hasEnvironmentWarnings"),
        "hasMetadataWarnings": result.get("hasMetadataWarnings"),
    }
    flags = [("Photo quality", ver.get("hasPhotoWarnings")),
             ("Image integrity", ver.get("hasIntegrityWarnings")),
             ("Environment", ver.get("hasEnvironmentWarnings")),
             ("Metadata (EXIF)", ver.get("hasMetadataWarnings"))]
    raised = [n for n, f in flags if f]
    vc = result.get("vehicleConsistency") or {}
    if vc and vc.get("consistent") is False:
        raised.append("Vehicle consistency")

    meta_rows = ""
    for k, v in [("Rental agreement", rf.get("rentalId")), ("Vehicle plate", rf.get("vehiclePlate")),
                 ("Customer", rf.get("customerName")), ("Make / model", rf.get("vehicleModel")),
                 ("Inspector", rf.get("inspectorName")),
                 ("Analyzed", (doc.get("createdAt") or datetime.now(timezone.utc)).strftime("%Y-%m-%d %H:%M UTC")),
                 ("Condition score", result.get("conditionScore")),
                 ("Advisory estimate (new damage)", _cost_str(cost))]:
        if v not in (None, ""):
            meta_rows += f"<div><div class='k'>{_esc(k)}</div><div class='v'>{_esc(v)}</div></div>"

    img_by_idx = {img["index"]: img for img in doc.get("images", [])}
    sections_html = ""
    for i, sec in enumerate(result.get("sections") or []):
        img = img_by_idx.get(i) or {}
        imgs_html = ""
        if img.get("before") and img.get("after"):
            imgs_html = (f"<div class='imgs'>"
                         f"<figure><img src='{base}/images/{img['before']}' alt='Before'/>"
                         f"<figcaption>Before the trip</figcaption></figure>"
                         f"<figure><img src='{base}/images/{img['after']}' alt='After (annotated)'/>"
                         f"<figcaption>After the trip — findings marked</figcaption></figure></div>")
        rows = ""
        for it in (sec.get("items") or []):
            sev = it.get("severity") or "—"
            sev_c = _SEV_COLOR.get(sev, "#475569")
            st = it.get("status") or "—"
            st_rgb = _STATUS_RGB.get(st, (71, 85, 105))
            st_hex = "#%02x%02x%02x" % st_rgb
            rows += (f"<tr><td><b>{_esc(it.get('marker')) if it.get('marker') else '·'}</b></td>"
                     f"<td>{_esc(it.get('category'))}</td>"
                     f"<td><span class='chip' style='background:{st_hex}1a;color:{st_hex}'>{_esc(st)}</span></td>"
                     f"<td style='color:{sev_c};font-weight:600'>{_esc(sev)}</td>"
                     f"<td>{_esc(it.get('location'))}<div style='color:#64748b'>{_esc(it.get('detail')) if it.get('detail') else ''}</div></td>"
                     f"<td>{_esc(it.get('sizeCm'))}{' cm' if it.get('sizeCm') else ''}</td>"
                     f"<td>{_esc(it.get('recommendation'))}</td>"
                     f"<td>{_cost_str(it.get('estimatedCost')) if st == 'NEW' else '—'}</td></tr>")
        table = (f"<table><thead><tr><th>#</th><th>Category</th><th>Status</th><th>Severity</th>"
                 f"<th>Location</th><th>Size</th><th>Action</th><th>Est. cost</th></tr></thead>"
                 f"<tbody>{rows}</tbody></table>") if rows else \
            "<p style='font-size:13px;color:#475569'>No findings in this view.</p>"
        summary = f"<p style='font-size:13px;color:#334155;margin-bottom:8px'>{_esc(sec.get('summary'))}</p>" if sec.get("summary") else ""
        new_n = sec.get("newIssueCount") or 0
        badge = (f"<span class='chip' style='background:#fff1f2;color:#be123c'>{new_n} new</span>"
                 if new_n else "<span class='chip' style='background:#ecfdf5;color:#047857'>no new damage</span>")
        sections_html += (f"<div class='card'><h2>{_esc(sec.get('label'))} {badge}</h2>"
                          f"{summary}{imgs_html}{table}</div>")

    ver_html = (f"<div class='warn'><b>⚠ Review before charging:</b> warnings raised — "
                f"{_esc(', '.join(raised))}. A human should verify the photos.</div>"
                if raised else
                "<div class='okflag'>✓ All photo, integrity, metadata and vehicle-consistency checks passed.</div>")

    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'>
<meta name='viewport' content='width=device-width,initial-scale=1'>
<meta name='robots' content='noindex,nofollow'>
<title>Trip Inspection Report — {_esc(rf.get('rentalId') or token[:8])}</title>
<style>{_CSS}</style></head><body><div class='wrap'>
<div class='card'>
  <div class='hdr'>
    <div style='flex:1'>
      <div class='brand'>{_esc(company)} · Damage Intelligence</div>
      <h1>Trip Inspection Report</h1>
    </div>
    <span class='verdict' style='color:{color};background:{bg};border:1px solid {color}40'>{label}</span>
  </div>
  <div class='meta'>{meta_rows}</div>
  {ver_html}
  <div class='actions'>
    <a class='btn' href='{base}/pdf' data-testid='report-pdf-link'>Download PDF</a>
    <button class='btn sec' onclick='window.print()'>Print</button>
  </div>
</div>
{sections_html}
<div class='foot'>AI-assisted advisory report · generated by Damage Intelligence · results are estimates and require human confirmation before charging.</div>
</div></body></html>"""


def render_pdf(doc: dict) -> bytes:
    result = doc.get("result") or {}
    rf = doc.get("reportFields") or {}
    branding = result.get("branding") or {}
    company = branding.get("companyName") or "Damage Intelligence"
    label, color, _ = _VERDICT.get(result.get("overall"), ("Processing", "#475569", ""))
    styles = getSampleStyleSheet()
    small = ParagraphStyle("small", parent=styles["Normal"], fontSize=8, leading=10)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=12, spaceBefore=10, spaceAfter=4)

    buf = io.BytesIO()
    pdf = SimpleDocTemplate(buf, pagesize=A4, topMargin=1.4 * cm, bottomMargin=1.4 * cm,
                            leftMargin=1.5 * cm, rightMargin=1.5 * cm)
    el = [Paragraph(f"{company} — Trip Inspection Report", styles["Title"]),
          Paragraph(f"<b>Verdict:</b> <font color='{color}'><b>{label}</b></font> · "
                    f"New issues: {result.get('newIssueCount', 0)} · "
                    f"Advisory estimate: {_cost_str(result.get('costSummary'))}", styles["Normal"]),
          Spacer(1, 6)]
    meta = [(k, v) for k, v in [("Rental agreement", rf.get("rentalId")),
                                ("Vehicle plate", rf.get("vehiclePlate")),
                                ("Customer", rf.get("customerName")),
                                ("Make / model", rf.get("vehicleModel")),
                                ("Inspector", rf.get("inspectorName")),
                                ("Condition score", result.get("conditionScore"))] if v not in (None, "")]
    if meta:
        t = Table([[Paragraph(f"<b>{k}</b>", small), Paragraph(str(v), small)] for k, v in meta],
                  colWidths=[4.5 * cm, 12.5 * cm])
        t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.4, rl_colors.HexColor("#e2e8f0")),
                               ("BACKGROUND", (0, 0), (0, -1), rl_colors.HexColor("#f8fafc")),
                               ("VALIGN", (0, 0), (-1, -1), "TOP")]))
        el += [t, Spacer(1, 8)]

    img_by_idx = {img["index"]: img for img in doc.get("images", [])}
    tdir = _report_dir(doc["tenantId"], doc["token"])
    for i, sec in enumerate(result.get("sections") or []):
        el.append(Paragraph(f"{sec.get('label', 'Section')} — {sec.get('newIssueCount', 0)} new issue(s)", h2))
        if sec.get("summary"):
            el.append(Paragraph(html_mod.escape(sec["summary"]), small))
            el.append(Spacer(1, 4))
        img = img_by_idx.get(i) or {}
        cells, caps = [], []
        for which, cap in (("before", "Before the trip"), ("after", "After — findings marked")):
            name = img.get(which)
            p = tdir / name if name else None
            if p and p.exists():
                with Image.open(p) as im:
                    w, h = im.size
                iw = 8.3 * cm
                cells.append(RLImage(str(p), width=iw, height=iw * h / w))
                caps.append(Paragraph(cap, small))
        if cells:
            it = Table([cells, caps], colWidths=[8.6 * cm] * len(cells))
            it.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
            el += [it, Spacer(1, 4)]
        items = sec.get("items") or []
        if items:
            rows = [["#", "Category", "Status", "Sev.", "Location", "Size", "Action", "Est. cost"]]
            for x in items:
                rows.append([str(x.get("marker") or "·"), x.get("category") or "—",
                             x.get("status") or "—", x.get("severity") or "—",
                             Paragraph(html_mod.escape(x.get("location") or "—"), small),
                             f"{x.get('sizeCm')} cm" if x.get("sizeCm") else "—",
                             x.get("recommendation") or "—",
                             _cost_str(x.get("estimatedCost")) if x.get("status") == "NEW" else "—"])
            t = Table(rows, colWidths=[0.8 * cm, 2.2 * cm, 2.4 * cm, 1.4 * cm, 4.6 * cm, 1.5 * cm, 1.8 * cm, 2.3 * cm])
            t.setStyle(TableStyle([
                ("FONTSIZE", (0, 0), (-1, -1), 7.5),
                ("BACKGROUND", (0, 0), (-1, 0), rl_colors.HexColor("#f1f5f9")),
                ("GRID", (0, 0), (-1, -1), 0.4, rl_colors.HexColor("#e2e8f0")),
                ("VALIGN", (0, 0), (-1, -1), "TOP")]))
            el.append(t)
        el.append(Spacer(1, 8))

    el.append(Spacer(1, 10))
    el.append(Paragraph("AI-assisted advisory report generated by Damage Intelligence. "
                        "Results are estimates and require human confirmation before charging.", small))
    pdf.build(el)
    return buf.getvalue()
