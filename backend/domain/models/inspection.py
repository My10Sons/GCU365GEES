"""
Repository Traceability:
- Source Document: DI-SPRINT-01 (Database — required columns), DI-0012 (Domain Model).
- Purpose: Pydantic schemas for inspection-session and related Sprint-01 entities.
  These shape API responses; persistence uses plain dicts produced by `.model_dump()`.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ExternalReferences(BaseModel):
    """Opaque string references to systems we do not own (DECISION-Sprint01-b)."""
    externalVehicleRef: str
    externalRentalAgreementRef: Optional[str] = None
    externalMaintenanceRef: Optional[str] = None
    externalBranchRef: Optional[str] = None
    externalWorkOrderRef: Optional[str] = None


class InspectionSessionResponse(BaseModel):
    id: str
    tenantId: str
    inspectionType: str
    sourceSystem: str
    status: str
    references: ExternalReferences
    imageCount: int = 0
    registeredImageCount: int = 0
    submittedAt: Optional[datetime] = None
    cancelledAt: Optional[datetime] = None
    failedAt: Optional[datetime] = None
    statusReason: Optional[str] = None
    createdAt: datetime
    createdBy: str
    updatedAt: datetime
    updatedBy: str
    correlationId: str


class InspectionSessionListItem(BaseModel):
    id: str
    inspectionType: str
    sourceSystem: str
    status: str
    references: ExternalReferences
    imageCount: int = 0
    createdAt: datetime
    updatedAt: datetime


class StatusHistoryItem(BaseModel):
    fromStatus: Optional[str] = None
    toStatus: str
    reason: Optional[str] = None
    actorId: str
    timestamp: datetime
    correlationId: str
