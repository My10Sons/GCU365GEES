"""
Repository Traceability:
- Source Documents: DI-SPRINT-04 (Required CROMS + Maintenance APIs, headers, idempotency),
  DI-0017, DI-0018, DI-0031, DI-0034 (paths, envelope, permissions).
- Purpose: Production service-to-service integration routes for GCU365 CROMS and
  GCU365Maintenance. Authenticated (JWT), tenant-scoped, idempotent on write, audited.
"""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, Header, Path, Request
from pydantic import BaseModel, Field

from api.schemas.envelope import ok
from application.security.dependencies import require_permission
from application.services import integration_service
from domain.enums.inspection_type import InspectionType

router = APIRouter(prefix="/integrations", tags=["integrations"])


# ----------------------------- Schemas -----------------------------

class CustomerRef(BaseModel):
    customerId: Optional[str] = Field(None, max_length=64)


class CheckOutIn(BaseModel):
    rentalAgreementId: str = Field(..., min_length=1, max_length=64)
    vehicleId: str = Field(..., min_length=1, max_length=64)
    branchId: Optional[str] = Field(None, max_length=64)
    customerReference: Optional[CustomerRef] = None
    requestedBySystem: Optional[str] = Field(None, max_length=64)


class CheckInIn(CheckOutIn):
    baselineInspectionSessionId: Optional[str] = Field(None, max_length=64)


class Ref(BaseModel):
    referenceId: Optional[str] = Field(None, max_length=128)
    sourceSystem: Optional[str] = Field(None, max_length=64)


class HandoffIn(BaseModel):
    damageCaseId: str = Field(..., min_length=1, max_length=64)
    vehicleId: Optional[str] = Field(None, max_length=64)
    severityCode: Optional[str] = Field(None, max_length=32)
    evidencePackageReference: Optional[dict] = None
    advisoryEstimateReference: Optional[dict] = None
    requestedBySystem: Optional[str] = Field(None, max_length=64)


class WorkOrderRefIn(BaseModel):
    damageCaseId: str = Field(..., min_length=1, max_length=64)
    maintenanceRequestId: Optional[str] = Field(None, max_length=64)
    workOrderId: str = Field(..., min_length=1, max_length=64)
    status: Optional[str] = Field(None, max_length=64)
    updatedAt: Optional[str] = Field(None, max_length=40)


class RepairStatusIn(BaseModel):
    damageCaseId: str = Field(..., min_length=1, max_length=64)
    workOrderId: Optional[str] = Field(None, max_length=64)
    repairStatus: str = Field(..., min_length=1, max_length=64)
    actualRepairCostReference: Optional[dict] = None
    updatedAt: Optional[str] = Field(None, max_length=40)


class RejectionIn(BaseModel):
    damageCaseId: str = Field(..., min_length=1, max_length=64)
    maintenanceRequestId: Optional[str] = Field(None, max_length=64)
    rejectionCode: str = Field(..., min_length=1, max_length=64)
    rejectionReason: Optional[str] = Field(None, max_length=1000)
    requestedAdditionalEvidence: Optional[bool] = None


class MaintenanceEvidenceIn(BaseModel):
    damageCaseId: str = Field(..., min_length=1, max_length=64)
    reason: str = Field(..., min_length=1, max_length=1000)
    maintenanceRequestId: Optional[str] = Field(None, max_length=64)
    requestedPositions: Optional[List[str]] = None


def _croms():
    return require_permission("di.integrations.croms")


def _maint():
    return require_permission("di.integrations.maintenance")


# ----------------------------- CROMS -----------------------------

@router.post("/croms/check-out-inspections")
async def croms_check_out(
    request: Request, payload: CheckOutIn,
    x_idempotency_key: Optional[str] = Header(None, alias="X-Idempotency-Key"),
    principal: dict = Depends(_croms()),
):
    data = await integration_service.croms_create_inspection(
        principal=principal, inspection_type=InspectionType.CHECK_OUT,
        payload=payload.model_dump(), idempotency_key=x_idempotency_key,
        correlation_id=request.state.correlation_id,
    )
    return ok(data, request.state.correlation_id)


@router.post("/croms/check-in-inspections")
async def croms_check_in(
    request: Request, payload: CheckInIn,
    x_idempotency_key: Optional[str] = Header(None, alias="X-Idempotency-Key"),
    principal: dict = Depends(_croms()),
):
    data = await integration_service.croms_create_inspection(
        principal=principal, inspection_type=InspectionType.CHECK_IN,
        payload=payload.model_dump(), idempotency_key=x_idempotency_key,
        correlation_id=request.state.correlation_id,
    )
    return ok(data, request.state.correlation_id)


@router.get("/croms/rental-agreements/{rentalAgreementId}/damage-summary")
async def croms_damage_summary(
    request: Request,
    rentalAgreementId: str = Path(..., min_length=1, max_length=64),
    principal: dict = Depends(_croms()),
):
    data = await integration_service.croms_damage_summary(
        principal=principal, rental_agreement_id=rentalAgreementId,
        correlation_id=request.state.correlation_id,
    )
    return ok(data, request.state.correlation_id)


@router.get("/croms/inspection-sessions/{inspectionSessionId}/status")
async def croms_inspection_status(
    request: Request,
    inspectionSessionId: str = Path(..., min_length=1, max_length=64),
    principal: dict = Depends(_croms()),
):
    data = await integration_service.croms_inspection_status(
        principal=principal, session_id=inspectionSessionId,
        correlation_id=request.state.correlation_id,
    )
    return ok(data, request.state.correlation_id)


@router.post("/croms/notifications/damage-summary-ready")
async def croms_notify(
    request: Request,
    body: dict,
    principal: dict = Depends(_croms()),
):
    data = await integration_service.croms_notify_damage_summary_ready(
        principal=principal, rental_agreement_id=str(body.get("rentalAgreementId") or ""),
        correlation_id=request.state.correlation_id,
    )
    return ok(data, request.state.correlation_id)


# -------------------------- Maintenance --------------------------

@router.post("/maintenance/handoffs")
async def maintenance_handoff(
    request: Request, payload: HandoffIn,
    x_idempotency_key: Optional[str] = Header(None, alias="X-Idempotency-Key"),
    principal: dict = Depends(_maint()),
):
    data = await integration_service.maintenance_handoff(
        principal=principal, payload=payload.model_dump(), idempotency_key=x_idempotency_key,
        correlation_id=request.state.correlation_id,
    )
    return ok(data, request.state.correlation_id)


@router.post("/maintenance/work-order-references")
async def maintenance_work_order_reference(
    request: Request, payload: WorkOrderRefIn,
    principal: dict = Depends(_maint()),
):
    data = await integration_service.maintenance_work_order_reference(
        principal=principal, payload=payload.model_dump(), correlation_id=request.state.correlation_id,
    )
    return ok(data, request.state.correlation_id)


@router.post("/maintenance/repair-status-updates")
async def maintenance_repair_status(
    request: Request, payload: RepairStatusIn,
    principal: dict = Depends(_maint()),
):
    data = await integration_service.maintenance_repair_status(
        principal=principal, payload=payload.model_dump(), correlation_id=request.state.correlation_id,
    )
    return ok(data, request.state.correlation_id)


@router.post("/maintenance/rejection-reasons")
async def maintenance_rejection(
    request: Request, payload: RejectionIn,
    principal: dict = Depends(_maint()),
):
    data = await integration_service.maintenance_rejection(
        principal=principal, payload=payload.model_dump(), correlation_id=request.state.correlation_id,
    )
    return ok(data, request.state.correlation_id)


@router.post("/maintenance/additional-evidence-requests")
async def maintenance_additional_evidence(
    request: Request, payload: MaintenanceEvidenceIn,
    principal: dict = Depends(_maint()),
):
    data = await integration_service.maintenance_additional_evidence_request(
        principal=principal, payload=payload.model_dump(), correlation_id=request.state.correlation_id,
    )
    return ok(data, request.state.correlation_id)


@router.get("/maintenance/damage-cases/{damageCaseId}/handoff-status")
async def maintenance_handoff_status(
    request: Request,
    damageCaseId: str = Path(..., min_length=1, max_length=64),
    principal: dict = Depends(_maint()),
):
    data = await integration_service.maintenance_handoff_status(
        principal=principal, case_id=damageCaseId, correlation_id=request.state.correlation_id,
    )
    return ok(data, request.state.correlation_id)
