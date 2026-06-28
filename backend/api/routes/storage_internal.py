"""
Repository Traceability:
- Source Documents: DI-SPRINT-01 (Object Storage Implementation — secure upload + access
  via time-limited signed links), DI-0014 (no public URLs).
- Purpose: Internal storage endpoints that honor HMAC-signed time-limited tokens.
  These are the targets of the `uploadUrl` / `accessUrl` returned by the inspection APIs.
"""
from __future__ import annotations

import os
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import FileResponse, JSONResponse

from api.schemas.envelope import fail, ok
from domain.enums.error_codes import ErrorCode
from infrastructure.db.mongo import get_db
from infrastructure.storage.local_storage import storage_root, verify_signature
from datetime import datetime, timezone

router = APIRouter(prefix="/internal/storage", tags=["storage (internal)"])

SUPPORTED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_BYTES = 25 * 1024 * 1024


def _safe_resolve(rel_path: str) -> Path:
    """Resolve `rel_path` strictly under storage_root() to prevent traversal."""
    root = storage_root().resolve()
    target = (root / rel_path).resolve()
    try:
        target.relative_to(root)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid path.")
    return target


@router.put("/upload")
async def upload_object(
    request: Request,
    path: str = Query(..., min_length=10, max_length=512),
    exp: int = Query(...),
    sig: str = Query(..., min_length=8, max_length=128),
):
    correlation_id = request.state.correlation_id
    if not verify_signature(object_path=path, expires_at_epoch=exp, action="PUT", presented=sig):
        return JSONResponse(
            status_code=403,
            content=fail(ErrorCode.FORBIDDEN, "Upload link invalid or expired.", correlation_id),
        )
    if not path.startswith("tenants/"):
        return JSONResponse(
            status_code=400,
            content=fail(ErrorCode.VALIDATION_ERROR, "Invalid storage path.", correlation_id, "path"),
        )
    content_type = (request.headers.get("Content-Type") or "").lower().split(";")[0].strip()
    if content_type not in SUPPORTED_CONTENT_TYPES:
        return JSONResponse(
            status_code=415,
            content=fail(
                ErrorCode.UNSUPPORTED_MEDIA_TYPE,
                "Unsupported content type.",
                correlation_id,
                "Content-Type",
            ),
        )
    target = _safe_resolve(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    total = 0
    try:
        with target.open("wb") as fh:
            async for chunk in request.stream():
                if not chunk:
                    continue
                total += len(chunk)
                if total > MAX_BYTES:
                    fh.close()
                    target.unlink(missing_ok=True)
                    return JSONResponse(
                        status_code=413,
                        content=fail(
                            ErrorCode.PAYLOAD_TOO_LARGE,
                            f"Upload exceeds {MAX_BYTES // (1024*1024)} MB.",
                            correlation_id,
                        ),
                    )
                fh.write(chunk)
    except Exception:
        target.unlink(missing_ok=True)
        return JSONResponse(
            status_code=500,
            content=fail(ErrorCode.INTERNAL_ERROR, "Upload failed.", correlation_id),
        )

    # Mark the corresponding upload-request as UPLOADED so registration can proceed.
    db = get_db()
    await db.di_upload_requests.update_one(
        {"objectPath": path, "status": "REQUESTED"},
        {"$set": {"status": "UPLOADED", "uploadedAt": datetime.now(timezone.utc), "uploadedFileSize": total}},
    )
    return ok({"objectPath": path, "bytesStored": total}, correlation_id)


@router.get("/access")
async def access_object(
    request: Request,
    path: str = Query(..., min_length=10, max_length=512),
    exp: int = Query(...),
    sig: str = Query(..., min_length=8, max_length=128),
):
    correlation_id = request.state.correlation_id
    if not verify_signature(object_path=path, expires_at_epoch=exp, action="GET", presented=sig):
        return JSONResponse(
            status_code=403,
            content=fail(ErrorCode.FORBIDDEN, "Access link invalid or expired.", correlation_id),
        )
    target = _safe_resolve(path)
    if not target.exists() or not target.is_file():
        return JSONResponse(
            status_code=404,
            content=fail(ErrorCode.NOT_FOUND, "Evidence object not found.", correlation_id),
        )
    # Look up content type from the evidence reference for accurate headers.
    db = get_db()
    ev = await db.di_evidence_references.find_one({"objectPath": path})
    media_type = (ev or {}).get("contentType") or "application/octet-stream"
    return FileResponse(target, media_type=media_type)
