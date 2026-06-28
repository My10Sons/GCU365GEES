"""
Repository Traceability:
- Source Documents: DI-0034 (Standard Response Envelope, Standard Error Codes, "no stack
  traces", "no secrets"), DI-0014 (safe errors), DI-SPRINT-00 (safe error baseline).
- Purpose: Global exception handler converting unexpected errors into the safe envelope.
"""
import logging
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from api.schemas.envelope import fail
from domain.enums.error_codes import ErrorCode

logger = logging.getLogger("di.errors")


class DomainError(Exception):
    """Application-layer error carrying a stable code + safe message + http status."""

    def __init__(self, code: str, message: str, status_code: int = 400, field: str | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.field = field


def _correlation_id(request: Request) -> str:
    return getattr(request.state, "correlation_id", "-")


async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=fail(exc.code, exc.message, _correlation_id(request), exc.field),
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    code_map = {
        400: ErrorCode.VALIDATION_ERROR,
        401: ErrorCode.UNAUTHORIZED,
        403: ErrorCode.FORBIDDEN,
        404: ErrorCode.NOT_FOUND,
        409: ErrorCode.CONFLICT,
        413: ErrorCode.PAYLOAD_TOO_LARGE,
        415: ErrorCode.UNSUPPORTED_MEDIA_TYPE,
    }
    code = code_map.get(exc.status_code, ErrorCode.INTERNAL_ERROR)
    message = exc.detail if isinstance(exc.detail, str) else "Request could not be completed."
    return JSONResponse(
        status_code=exc.status_code,
        content=fail(code, message, _correlation_id(request)),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    # Surface only the first validation error to avoid leaking schema internals.
    first_field = None
    first_msg = "Request validation failed."
    errors = exc.errors() or []
    if errors:
        first_msg = errors[0].get("msg") or first_msg
        loc = errors[0].get("loc")
        if isinstance(loc, (list, tuple)) and loc:
            first_field = ".".join(str(p) for p in loc[1:]) if len(loc) > 1 else str(loc[0])
    return JSONResponse(
        status_code=400,
        content=fail(ErrorCode.VALIDATION_ERROR, first_msg, _correlation_id(request), first_field),
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    # Log full exception server-side; never leak details to client.
    logger.exception("Unhandled exception", extra={"extra": {"path": str(request.url.path)}})
    return JSONResponse(
        status_code=500,
        content=fail(ErrorCode.INTERNAL_ERROR, "Internal error.", _correlation_id(request)),
    )
