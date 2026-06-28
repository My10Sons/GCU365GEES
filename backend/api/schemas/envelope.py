"""
Repository Traceability:
- Source Documents: DI-0034 (Standard Response Envelope, Standard Error Codes)
- Purpose: Standard success/error envelope used by every Damage Intelligence API.
"""
from typing import Any, List, Optional
from pydantic import BaseModel, Field


class ApiError(BaseModel):
    code: str
    message: str
    field: Optional[str] = None


class ApiEnvelope(BaseModel):
    success: bool
    correlationId: str
    data: Any = None
    errors: List[ApiError] = Field(default_factory=list)


def ok(data: Any, correlation_id: str) -> dict:
    return {
        "success": True,
        "correlationId": correlation_id,
        "data": data,
        "errors": [],
    }


def fail(code: str, message: str, correlation_id: str, field: Optional[str] = None) -> dict:
    err = {"code": code, "message": message}
    if field is not None:
        err["field"] = field
    return {
        "success": False,
        "correlationId": correlation_id,
        "data": None,
        "errors": [err],
    }
