"""
Repository Traceability:
- Source Documents: DI-0015 (Audit and Traceability), DI-SPRINT-00 (Observability Setup),
  DI-0034 (correlation header)
- Purpose: Structured logging with correlation id. Never logs secrets or raw images.
"""
import json
import logging
import os
import sys
from contextvars import ContextVar
from datetime import datetime, timezone

_correlation_ctx: ContextVar[str] = ContextVar("correlation_id", default="-")


def set_correlation_id(value: str) -> None:
    _correlation_ctx.set(value or "-")


def get_correlation_id() -> str:
    return _correlation_ctx.get()


_SENSITIVE_KEYS = {
    "password",
    "password_hash",
    "passwordhash",
    "authorization",
    "token",
    "access_token",
    "refresh_token",
    "jwt",
    "secret",
    "x-api-key",
    "image",
    "image_bytes",
    "rawimage",
    "raw_image",
    "evidence_url",
    "report_url",
}


def _scrub(value):
    if isinstance(value, dict):
        return {k: ("***REDACTED***" if k.lower() in _SENSITIVE_KEYS else _scrub(v)) for k, v in value.items()}
    if isinstance(value, list):
        return [_scrub(v) for v in value]
    return value


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlationId": get_correlation_id(),
            "service": os.environ.get("DI_SERVICE_NAME", "damage-intelligence-api"),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info).splitlines()[-1]
        extra = getattr(record, "extra", None)
        if extra:
            payload["extra"] = _scrub(extra)
        return json.dumps(payload, default=str)


def configure_logging() -> None:
    root = logging.getLogger()
    for h in list(root.handlers):
        root.removeHandler(h)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root.addHandler(handler)
    root.setLevel(logging.INFO)
    # Quiet noisy libs
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def log_event(logger: logging.Logger, level: int, message: str, **extra) -> None:
    logger.log(level, message, extra={"extra": _scrub(extra)})
