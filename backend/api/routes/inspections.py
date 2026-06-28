"""
Repository Traceability:
- Source Documents: DI-SPRINT-01 (all 9 inspection/evidence APIs), DI-0034 (paths, headers,
  envelope, error codes, idempotency, permissions), DI-0014 (auth/authz/tenant isolation).
- Purpose: REST routes for inspection sessions, images, and evidence access links.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Path, Query, Request
from pydantic import BaseModel, Field

from api.schemas.envelope import ok
from application.security.dependencies import get_current_principal, require_permission
from application.services import image_service, inspection_service
from domain.enums.inspection_type import ALL_INSPECTION_TYPES, ALL_SOURCE_SYSTEMS
from domain.enums.inspection_status import ALL_STATUSES

router = APIRouter(prefix="/inspection-sessions", tags=["inspections"])


# -------- Schemas --------

class ReferencesIn(BaseModel):
    externalVehicleRef: str = Field(..., min_length=1, max_length=128)
    externalRentalAgreementRef: Optional[str] = Field(None, max_length=128)
    externalMaintenanceRef: Optional[str] = Field(None, max_length=128)
    externalBranchRef: Optional[str] = Field(None, max_length=128)
    externalWorkOrderRef: Optional[str] = Field(None, max_length=128)


class CreateInspectionIn(BaseModel):
    inspectionType: str
    sourceSystem: str
    references: ReferencesIn


class StatusPatchIn(BaseModel):
    status: str
    reason: Optional[str] = Field(None, max_length=500)


class UploadRequestIn(BaseModel):
    capturePosition: str
    fileName: str = Field(..., min_length=1, max_length=256)
    contentType: str = Field(..., max_length=64)
    fileSize: int = Field(..., gt=0)


class RegisterImageIn(BaseModel):
    uploadRequestId: str = Field(..., min_length=1, max_length=64)
    width: Optional[int] = Field(None, ge=1, le=20000)
    height: Optional[int] = Field(None, ge=1, le=20000)
    captureTimestamp: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=1000)


# -------- Routes --------

@router.post("")
async def create_inspection(
    request: Request,
    payload: CreateInspectionIn,
    principal: dict = Depends(require_permission("di.inspections.create")),
):
    data = await inspection_service.create_inspection_session(
        principal=principal,
        payload=payload.model_dump(),
        correlation_id=request.state.correlation_id,
    )
    return ok(data, request.state.correlation_id)


@router.get("")
async def list_inspections(
    request: Request,
    page: int = Query(1, ge=1, le=10_000),
    pageSize: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    inspectionType: Optional[str] = Query(None),
    externalVehicleRef: Optional[str] = Query(None),
    externalRentalAgreementRef: Optional[str] = Query(None),
    externalBranchRef: Optional[str] = Query(None),
    createdFrom: Optional[datetime] = Query(None),
    createdTo: Optional[datetime] = Query(None),
    principal: dict = Depends(require_permission("di.inspections.read")),
):
    if status is not None and status not in ALL_STATUSES:
        from api.middleware.safe_errors import DomainError
        from domain.enums.error_codes import ErrorCode
        raise DomainError(ErrorCode.VALIDATION_ERROR, "Invalid status filter.", 400, "status")
    if inspectionType is not None and inspectionType not in ALL_INSPECTION_TYPES:
        from api.middleware.safe_errors import DomainError
        from domain.enums.error_codes import ErrorCode
        raise DomainError(ErrorCode.VALIDATION_ERROR, "Invalid inspectionType filter.", 400, "inspectionType")
    data = await inspection_service.list_inspection_sessions(
        principal=principal,
        correlation_id=request.state.correlation_id,
        page=page,
        page_size=pageSize,
        status=status,
        inspection_type=inspectionType,
        external_vehicle_ref=externalVehicleRef,
        external_rental_agreement_ref=externalRentalAgreementRef,
        external_branch_ref=externalBranchRef,
        created_from=createdFrom,
        created_to=createdTo,
    )
    return ok(data, request.state.correlation_id)


@router.get("/{inspectionSessionId}")
async def get_inspection(
    request: Request,
    inspectionSessionId: str = Path(..., min_length=1, max_length=64),
    principal: dict = Depends(require_permission("di.inspections.read")),
):
    data = await inspection_service.get_inspection_session(
        principal=principal,
        session_id=inspectionSessionId,
        correlation_id=request.state.correlation_id,
    )
    return ok(data, request.state.correlation_id)


@router.post("/{inspectionSessionId}/submit")
async def submit_inspection(
    request: Request,
    inspectionSessionId: str = Path(..., min_length=1, max_length=64),
    principal: dict = Depends(require_permission("di.inspections.submit")),
):
    data = await inspection_service.submit_inspection_session(
        principal=principal,
        session_id=inspectionSessionId,
        correlation_id=request.state.correlation_id,
    )
    return ok(data, request.state.correlation_id)


@router.patch("/{inspectionSessionId}/status")
async def patch_status(
    request: Request,
    payload: StatusPatchIn,
    inspectionSessionId: str = Path(..., min_length=1, max_length=64),
    principal: dict = Depends(get_current_principal),
):
    # PATCH /status accepts ONLY CAPTURE_IN_PROGRESS, CANCELLED, FAILED.
    # SUBMITTED goes through POST /submit, so reject it with the correct semantic code.
    from api.middleware.safe_errors import DomainError
    from domain.enums.error_codes import ErrorCode
    permission_for = {
        "CAPTURE_IN_PROGRESS": "di.inspections.submit",
        "CANCELLED": "di.inspections.cancel",
        "FAILED": "di.inspections.cancel",
    }
    if payload.status not in permission_for:
        raise DomainError(
            ErrorCode.INVALID_STATUS_TRANSITION,
            "status PATCH supports only CAPTURE_IN_PROGRESS, CANCELLED, FAILED. Use POST /submit to submit.",
            409,
            "status",
        )
    if permission_for[payload.status] not in principal["permissions"]:
        raise DomainError(ErrorCode.FORBIDDEN, "Missing required permission for this status change.", 403)
    data = await inspection_service.patch_status(
        principal=principal,
        session_id=inspectionSessionId,
        target_status=payload.status,
        reason=payload.reason,
        correlation_id=request.state.correlation_id,
    )
    return ok(data, request.state.correlation_id)


@router.post("/{inspectionSessionId}/images/upload-request")
async def upload_request(
    request: Request,
    payload: UploadRequestIn,
    inspectionSessionId: str = Path(..., min_length=1, max_length=64),
    principal: dict = Depends(require_permission("di.images.upload")),
):
    data = await image_service.create_upload_request(
        principal=principal,
        session_id=inspectionSessionId,
        capture_position=payload.capturePosition,
        file_name=payload.fileName,
        content_type=payload.contentType,
        file_size=payload.fileSize,
        correlation_id=request.state.correlation_id,
    )
    return ok(data, request.state.correlation_id)


@router.post("/{inspectionSessionId}/images")
async def register_image(
    request: Request,
    payload: RegisterImageIn,
    inspectionSessionId: str = Path(..., min_length=1, max_length=64),
    principal: dict = Depends(require_permission("di.images.upload")),
):
    data = await image_service.register_uploaded_image(
        principal=principal,
        session_id=inspectionSessionId,
        upload_request_id=payload.uploadRequestId,
        width=payload.width,
        height=payload.height,
        capture_timestamp=payload.captureTimestamp,
        notes=payload.notes,
        correlation_id=request.state.correlation_id,
    )
    return ok(data, request.state.correlation_id)


@router.get("/{inspectionSessionId}/images")
async def list_images(
    request: Request,
    inspectionSessionId: str = Path(..., min_length=1, max_length=64),
    principal: dict = Depends(require_permission("di.images.read")),
):
    data = await image_service.list_inspection_images(
        principal=principal,
        session_id=inspectionSessionId,
        correlation_id=request.state.correlation_id,
    )
    return ok({"items": data, "total": len(data)}, request.state.correlation_id)
