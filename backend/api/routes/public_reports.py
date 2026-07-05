"""
Repository Traceability:
- Purpose: Public (token-authenticated) hosted trip-inspection reports for external
  counterparts (GCU365 CROMS et al.): rendered HTML page, downloadable PDF, and the
  annotated report images. The unguessable 40-hex token is the credential.
"""
from __future__ import annotations

import asyncio

from fastapi import APIRouter, Path
from fastapi.responses import FileResponse, HTMLResponse, Response

from application.services import ext_report_service

router = APIRouter(prefix="/public/reports", tags=["public-reports"])

_NOT_FOUND = HTMLResponse(
    "<html><body style='font-family:Arial;padding:40px'><h2>Report not found</h2>"
    "<p>This report link is invalid or has been removed.</p></body></html>",
    status_code=404)


@router.get("/{token}", response_class=HTMLResponse)
async def view_report(token: str = Path(..., min_length=8, max_length=64)):
    doc = await ext_report_service.get_report(token)
    if not doc:
        return _NOT_FOUND
    return HTMLResponse(ext_report_service.render_html(doc))


@router.get("/{token}/pdf")
async def report_pdf(token: str = Path(..., min_length=8, max_length=64)):
    doc = await ext_report_service.get_report(token)
    if not doc or not doc.get("result"):
        return _NOT_FOUND
    pdf = await asyncio.to_thread(ext_report_service.render_pdf, doc)
    rid = (doc.get("reportFields") or {}).get("rentalId") or token[:8]
    return Response(content=pdf, media_type="application/pdf",
                    headers={"Content-Disposition":
                             f'attachment; filename="trip-inspection-{rid}.pdf"'})


@router.get("/{token}/images/{name}")
async def report_image(token: str = Path(..., min_length=8, max_length=64),
                       name: str = Path(..., max_length=32)):
    doc = await ext_report_service.get_report(token)
    if not doc:
        return _NOT_FOUND
    p = ext_report_service.image_path(doc, name)
    if not p:
        return _NOT_FOUND
    return FileResponse(str(p), media_type="image/jpeg")
