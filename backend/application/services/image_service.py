"""
Repository Traceability:
- Source Documents: DI-SPRINT-01 (Secure Image Upload Request, Register Uploaded Image,
  Get Inspection Images), DI-0007 (Vehicle Capture Standards), DI-0014 (no public URLs,
  tenant isolation), DI-0015 (audit).
- Purpose: Image upload-request + image registration + evidence link generation business logic.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone, timedelta
from typing import Optional

from bson import ObjectId

from api.middleware.safe_errors import DomainError
from application.services.audit_service import write_audit
from application.services.inspection_service import _load_session_for_tenant
from domain.enums.audit_actions import ActorType, AuditAction, ObjectType
from domain.enums.capture_positions import CAPTURE_POSITION_CODES
from domain.enums.error_codes import ErrorCode
from domain.enums.inspection_status import InspectionStatus, TERMINAL_STATUSES
from domain.enums.inspection_type import InspectionImageStatus
from infrastructure.db.mongo import get_db
from infrastructure.storage.local_storage import get_storage_provider

SUPPORTED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_SIZE_MB = 25
MAX_IMAGE_SIZE_BYTES = MAX_IMAGE_SIZE_MB * 1024 * 1024
UPLOAD_LINK_TTL_SECONDS = 600          # 10 minutes
DEFAULT_EVIDENCE_LINK_MINUTES = int(os.environ.get("DI_EVIDENCE_LINK_DEFAULT_MINUTES", "15"))
MAX_EVIDENCE_LINK_MINUTES = int(os.environ.get("DI_EVIDENCE_LINK_MAX_MINUTES", "60"))


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _validate_filename(name: str) -> None:
    if not name or len(name) > 256:
        raise DomainError(ErrorCode.VALIDATION_ERROR, "Invalid file name.", 400, "fileName")
    # Reject path traversal and absolute paths
    if any(ch in name for ch in ("/", "\\", "..", "\x00")):
        raise DomainError(ErrorCode.VALIDATION_ERROR, "Invalid file name.", 400, "fileName")


async def create_upload_request(
    *,
    principal: dict,
    session_id: str,
    capture_position: str,
    file_name: str,
    content_type: str,
    file_size: int,
    correlation_id: str,
) -> dict:
    if capture_position not in CAPTURE_POSITION_CODES:
        raise DomainError(ErrorCode.VALIDATION_ERROR, "Invalid capturePosition.", 400, "capturePosition")
    if content_type not in SUPPORTED_CONTENT_TYPES:
        raise DomainError(
            ErrorCode.UNSUPPORTED_MEDIA_TYPE,
            f"Unsupported content type. Allowed: {sorted(SUPPORTED_CONTENT_TYPES)}.",
            415,
            "contentType",
        )
    if not isinstance(file_size, int) or file_size <= 0:
        raise DomainError(ErrorCode.VALIDATION_ERROR, "fileSize must be a positive integer.", 400, "fileSize")
    if file_size > MAX_IMAGE_SIZE_BYTES:
        raise DomainError(
            ErrorCode.PAYLOAD_TOO_LARGE,
            f"fileSize exceeds {MAX_IMAGE_SIZE_MB} MB.",
            413,
            "fileSize",
        )
    _validate_filename(file_name)

    db = get_db()
    session = await _load_session_for_tenant(tenant_id=principal["tenantId"], session_id=session_id)
    if session["status"] in TERMINAL_STATUSES:
        raise DomainError(
            ErrorCode.INVALID_STATUS_TRANSITION,
            f"Inspection is in terminal status {session['status']}; uploads are not allowed.",
            409,
            "status",
        )

    upload_request_id = ObjectId()
    image_placeholder_id = ObjectId()
    storage = get_storage_provider()
    object_path = storage.evidence_path(
        principal["tenantId"], str(session["_id"]), str(image_placeholder_id)
    )
    instruction = await storage.make_upload_instruction(object_path, UPLOAD_LINK_TTL_SECONDS)

    now = _now()
    await db.di_upload_requests.insert_one(
        {
            "_id": upload_request_id,
            "tenantId": principal["tenantId"],
            "inspectionSessionId": str(session["_id"]),
            "imagePlaceholderId": str(image_placeholder_id),
            "capturePosition": capture_position,
            "fileName": file_name,
            "contentType": content_type,
            "fileSize": file_size,
            "objectPath": object_path,
            "status": "REQUESTED",
            "createdAt": now,
            "createdBy": principal["id"],
            "expiresAt": now + timedelta(seconds=UPLOAD_LINK_TTL_SECONDS),
            "correlationId": correlation_id,
        }
    )

    # Auto-advance DRAFT -> CAPTURE_IN_PROGRESS so the workflow reflects real activity.
    if session["status"] == InspectionStatus.DRAFT:
        await db.di_inspection_sessions.update_one(
            {"_id": session["_id"], "tenantId": principal["tenantId"]},
            {"$set": {"status": InspectionStatus.CAPTURE_IN_PROGRESS, "updatedAt": now, "updatedBy": principal["id"]}},
        )
        await db.di_inspection_status_history.insert_one(
            {
                "tenantId": principal["tenantId"],
                "inspectionSessionId": str(session["_id"]),
                "fromStatus": InspectionStatus.DRAFT,
                "toStatus": InspectionStatus.CAPTURE_IN_PROGRESS,
                "reason": "First upload request triggered capture.",
                "actorId": principal["id"],
                "timestamp": now,
                "correlationId": correlation_id,
            }
        )

    await write_audit(
        tenant_id=principal["tenantId"],
        actor_id=principal["id"],
        actor_type=ActorType.USER,
        action=AuditAction.IMAGE_UPLOAD_REQUESTED,
        object_type=ObjectType.UPLOAD_REQUEST,
        object_id=str(upload_request_id),
        correlation_id=correlation_id,
        safe_metadata={
            "inspectionSessionId": str(session["_id"]),
            "capturePosition": capture_position,
            "contentType": content_type,
            "fileSize": file_size,
        },
    )

    return {
        "uploadRequestId": str(upload_request_id),
        "imagePlaceholderId": str(image_placeholder_id),
        "uploadUrl": instruction.upload_url,
        "method": instruction.method,
        "expiresAt": instruction.expires_at_iso,
        "capturePosition": capture_position,
        "maxBytes": MAX_IMAGE_SIZE_BYTES,
        "supportedContentTypes": sorted(SUPPORTED_CONTENT_TYPES),
    }


async def register_uploaded_image(
    *,
    principal: dict,
    session_id: str,
    upload_request_id: str,
    width: Optional[int] = None,
    height: Optional[int] = None,
    capture_timestamp: Optional[datetime] = None,
    notes: Optional[str] = None,
    correlation_id: str,
) -> dict:
    db = get_db()
    session = await _load_session_for_tenant(tenant_id=principal["tenantId"], session_id=session_id)
    if session["status"] in TERMINAL_STATUSES:
        raise DomainError(
            ErrorCode.INVALID_STATUS_TRANSITION,
            f"Inspection is in terminal status {session['status']}; image registration not allowed.",
            409,
            "status",
        )

    try:
        upload_oid = ObjectId(upload_request_id)
    except Exception:
        raise DomainError(ErrorCode.VALIDATION_ERROR, "Invalid uploadRequestId.", 400, "uploadRequestId")
    upload = await db.di_upload_requests.find_one(
        {"_id": upload_oid, "tenantId": principal["tenantId"], "inspectionSessionId": str(session["_id"])}
    )
    if upload is None:
        raise DomainError(ErrorCode.NOT_FOUND, "Upload request not found.", 404, "uploadRequestId")
    if upload["status"] == "REGISTERED":
        # Idempotent: return the already-registered image instead of duplicating.
        existing = await db.di_inspection_images.find_one(
            {"tenantId": principal["tenantId"], "uploadRequestId": upload_request_id}
        )
        if existing is not None:
            return _image_to_response(existing)
        # Defensive fall-through: race detected, treat as conflict.
        raise DomainError(ErrorCode.IDEMPOTENCY_CONFLICT, "Upload request already registered.", 409, "uploadRequestId")
    if upload["status"] != "UPLOADED":
        raise DomainError(
            ErrorCode.CONFLICT,
            "Upload not completed for this request.",
            409,
            "uploadRequestId",
        )

    now = _now()
    image_id = ObjectId(upload["imagePlaceholderId"])
    image_doc = {
        "_id": image_id,
        "tenantId": principal["tenantId"],
        "inspectionSessionId": str(session["_id"]),
        "uploadRequestId": upload_request_id,
        "capturePosition": upload["capturePosition"],
        "fileName": upload["fileName"],
        "contentType": upload["contentType"],
        "fileSize": upload.get("uploadedFileSize") or upload["fileSize"],
        "objectPath": upload["objectPath"],
        "status": InspectionImageStatus.REGISTERED,
        "width": width,
        "height": height,
        "captureTimestamp": capture_timestamp,
        "notes": (notes or "").strip()[:1000] or None,
        "createdAt": now,
        "createdBy": principal["id"],
        "updatedAt": now,
        "updatedBy": principal["id"],
        "correlationId": correlation_id,
    }
    try:
        await db.di_inspection_images.insert_one(image_doc)
    except Exception:
        raise DomainError(ErrorCode.IDEMPOTENCY_CONFLICT, "Image already registered.", 409, "uploadRequestId")

    evidence_doc = {
        "tenantId": principal["tenantId"],
        "inspectionSessionId": str(session["_id"]),
        "inspectionImageId": str(image_id),
        "objectPath": upload["objectPath"],
        "contentType": upload["contentType"],
        "fileSize": image_doc["fileSize"],
        "capturePosition": upload["capturePosition"],
        "createdAt": now,
        "correlationId": correlation_id,
    }
    evidence_result = await db.di_evidence_references.insert_one(evidence_doc)
    evidence_doc["_id"] = evidence_result.inserted_id

    await db.di_upload_requests.update_one(
        {"_id": upload_oid}, {"$set": {"status": "REGISTERED", "registeredAt": now}}
    )

    # Increment counters and advance status if first registered image.
    inc_update: dict = {"$inc": {"imageCount": 1, "registeredImageCount": 1}, "$set": {"updatedAt": now, "updatedBy": principal["id"]}}
    await db.di_inspection_sessions.update_one(
        {"_id": session["_id"], "tenantId": principal["tenantId"]}, inc_update
    )
    if session["status"] in (InspectionStatus.DRAFT, InspectionStatus.CAPTURE_IN_PROGRESS):
        await db.di_inspection_sessions.update_one(
            {"_id": session["_id"], "tenantId": principal["tenantId"]},
            {"$set": {"status": InspectionStatus.EVIDENCE_REGISTERED, "updatedAt": now, "updatedBy": principal["id"]}},
        )
        await db.di_inspection_status_history.insert_one(
            {
                "tenantId": principal["tenantId"],
                "inspectionSessionId": str(session["_id"]),
                "fromStatus": session["status"],
                "toStatus": InspectionStatus.EVIDENCE_REGISTERED,
                "reason": "First image registered as evidence.",
                "actorId": principal["id"],
                "timestamp": now,
                "correlationId": correlation_id,
            }
        )

    await write_audit(
        tenant_id=principal["tenantId"],
        actor_id=principal["id"],
        actor_type=ActorType.USER,
        action=AuditAction.IMAGE_REGISTERED,
        object_type=ObjectType.INSPECTION_IMAGE,
        object_id=str(image_id),
        correlation_id=correlation_id,
        safe_metadata={
            "inspectionSessionId": str(session["_id"]),
            "capturePosition": upload["capturePosition"],
            "evidenceId": str(evidence_doc["_id"]),
        },
    )
    return _image_to_response(image_doc, evidence_id=str(evidence_doc["_id"]))


def _image_to_response(doc: dict, *, evidence_id: Optional[str] = None) -> dict:
    return {
        "id": str(doc["_id"]),
        "inspectionSessionId": doc["inspectionSessionId"],
        "uploadRequestId": doc.get("uploadRequestId"),
        "capturePosition": doc["capturePosition"],
        "contentType": doc["contentType"],
        "fileSize": doc.get("fileSize"),
        "width": doc.get("width"),
        "height": doc.get("height"),
        "status": doc["status"],
        "captureTimestamp": doc.get("captureTimestamp"),
        "notes": doc.get("notes"),
        "createdAt": doc["createdAt"],
        "createdBy": doc["createdBy"],
        "evidenceId": evidence_id,
    }


async def list_inspection_images(*, principal: dict, session_id: str, correlation_id: str) -> list[dict]:
    db = get_db()
    session = await _load_session_for_tenant(tenant_id=principal["tenantId"], session_id=session_id)
    cursor = db.di_inspection_images.find(
        {"tenantId": principal["tenantId"], "inspectionSessionId": str(session["_id"])}
    ).sort("createdAt", 1)
    items: list[dict] = []
    async for d in cursor:
        ev = await db.di_evidence_references.find_one(
            {"tenantId": principal["tenantId"], "inspectionImageId": str(d["_id"])}
        )
        items.append(_image_to_response(d, evidence_id=str(ev["_id"]) if ev else None))
    return items


async def create_evidence_access_link(
    *,
    principal: dict,
    evidence_id: str,
    purpose: str,
    expires_in_minutes: Optional[int],
    correlation_id: str,
) -> dict:
    if not purpose or not isinstance(purpose, str) or len(purpose) > 200:
        raise DomainError(ErrorCode.VALIDATION_ERROR, "purpose is required (max 200 chars).", 400, "purpose")
    if expires_in_minutes is None:
        minutes = DEFAULT_EVIDENCE_LINK_MINUTES
    else:
        try:
            minutes = int(expires_in_minutes)
        except (TypeError, ValueError):
            raise DomainError(ErrorCode.VALIDATION_ERROR, "expiresInMinutes must be an integer.", 400, "expiresInMinutes")
        if minutes <= 0 or minutes > MAX_EVIDENCE_LINK_MINUTES:
            raise DomainError(
                ErrorCode.VALIDATION_ERROR,
                f"expiresInMinutes must be in 1..{MAX_EVIDENCE_LINK_MINUTES}.",
                400,
                "expiresInMinutes",
            )

    db = get_db()
    try:
        ev_oid = ObjectId(evidence_id)
    except Exception:
        raise DomainError(ErrorCode.NOT_FOUND, "Evidence not found.", 404, "evidenceId")
    ev = await db.di_evidence_references.find_one({"_id": ev_oid, "tenantId": principal["tenantId"]})
    if ev is None:
        # Audit the denied attempt (still scrub details).
        await write_audit(
            tenant_id=principal["tenantId"],
            actor_id=principal["id"],
            actor_type=ActorType.USER,
            action=AuditAction.EVIDENCE_ACCESS_DENIED,
            object_type=ObjectType.EVIDENCE_REFERENCE,
            object_id=evidence_id,
            correlation_id=correlation_id,
            safe_metadata={"reason": "not_found_or_tenant_mismatch"},
        )
        raise DomainError(ErrorCode.NOT_FOUND, "Evidence not found.", 404, "evidenceId")

    storage = get_storage_provider()
    url, expires_at = await storage.make_access_link(ev["objectPath"], minutes * 60)
    await write_audit(
        tenant_id=principal["tenantId"],
        actor_id=principal["id"],
        actor_type=ActorType.USER,
        action=AuditAction.EVIDENCE_ACCESS_LINK_CREATED,
        object_type=ObjectType.EVIDENCE_REFERENCE,
        object_id=str(ev["_id"]),
        correlation_id=correlation_id,
        safe_metadata={"purpose": purpose[:200], "expiresInMinutes": minutes},
    )
    return {
        "evidenceId": str(ev["_id"]),
        "accessUrl": url,
        "expiresAt": expires_at,
        "method": "GET",
        "purpose": purpose[:200],
    }
