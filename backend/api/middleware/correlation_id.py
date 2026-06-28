"""
Repository Traceability:
- Source Documents: DI-0034 (X-Correlation-Id required header in request and response),
  DI-SPRINT-00 (Observability Setup — required correlation ID behavior).
- Purpose: Accept incoming X-Correlation-Id or generate one; expose in response and logs.
"""
import secrets
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from infrastructure.observability.logging import set_correlation_id


CORRELATION_HEADER = "X-Correlation-Id"


def _new_correlation_id() -> str:
    return "CORR-" + secrets.token_hex(8).upper()


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        incoming = request.headers.get(CORRELATION_HEADER) or _new_correlation_id()
        set_correlation_id(incoming)
        request.state.correlation_id = incoming
        response = await call_next(request)
        response.headers[CORRELATION_HEADER] = incoming
        return response
