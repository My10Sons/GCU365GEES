"""
Repository Traceability:
- Source Documents:
  - DI-0034 (Base API Path: /api/v1/damage-intelligence; Standard Headers; Standard
    Response Envelope; Standard Error Codes; Health APIs; Auth permissions table)
  - DI-SPRINT-00 (Backend Setup, Minimum Backend Endpoints, Identity Baseline,
    Observability Setup, Integration Stub Setup, Definition of Done)
  - DI-0014 (Security and Privacy baseline)
  - DI-0015 (Audit and Traceability baseline)
  - DECISION-001 (Stack substitution — FastAPI replaces ASP.NET Core)
  - DECISION-004 (MongoDB substitution for PostgreSQL)
- Purpose: FastAPI app entry point for the Damage Intelligence backend.
"""
from dotenv import load_dotenv
load_dotenv()  # MUST run before any other module-level imports that read os.environ

# stdlib
import os

# third-party
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# first-party
from api.middleware.correlation_id import CorrelationIdMiddleware
from api.middleware.safe_errors import (
    DomainError,
    domain_error_handler,
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from api.routes import ai as ai_routes
from api.routes import auth as auth_routes
from api.routes import comparison as comparison_routes
from api.routes import damage_cases as damage_case_routes
from api.routes import evidence as evidence_routes
from api.routes import review as review_routes
from api.routes import health as health_routes
from api.routes import inspections as inspection_routes
from api.routes import integration_stubs as integration_stub_routes
from api.routes import integrations as integration_routes
from api.routes import monitoring as monitoring_routes
from api.routes import reports as report_routes
from api.routes import demo as demo_routes
from api.routes import trip_inspection as trip_routes
from api.routes import tenant as tenant_routes
from api.routes import vehicles as vehicle_routes
from api.routes import developer as developer_routes
from api.routes import ext_api as ext_api_routes
from api.routes import public_reports as public_report_routes
from api.routes import benchmark as benchmark_routes
from api.routes import reference as reference_routes
from api.routes import storage_internal as storage_internal_routes
from api.routes import version as version_routes
from infrastructure.db.indexes import ensure_indexes
from infrastructure.db.mongo import close as close_db, get_db
from infrastructure.observability.logging import configure_logging, get_logger, log_event
from infrastructure.seed.admin_seed import seed_baseline_principals
from infrastructure.seed.capture_positions_seed import seed_capture_positions
from infrastructure.seed.tenant_branding_seed import seed_tenant_branding

configure_logging()
logger = get_logger("di.api")

API_BASE_PATH = "/api/v1/damage-intelligence"

app = FastAPI(
    title="Damage Intelligence API",
    version=os.environ.get("DI_API_VERSION", "1.0.0"),
    description=(
        "Damage Intelligence — image analysis and damage detection capability for "
        "existing GCU365 CROMS and GCU365Maintenance systems. See DI-0034 for the "
        "authoritative OpenAPI contract."
    ),
    docs_url=f"{API_BASE_PATH}/docs",
    openapi_url=f"{API_BASE_PATH}/openapi.json",
    redoc_url=None,
)

# Middleware (outermost first when added last). Order: CORS -> CorrelationId.
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ.get("FRONTEND_URL", "http://localhost:3000"), "*"],
    allow_credentials=False,  # Bearer tokens, not cookies
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Correlation-Id"],
)

# Exception handlers — order matters: most specific first.
app.add_exception_handler(DomainError, domain_error_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# Routes (all under DI-0034 base path)
app.include_router(health_routes.router, prefix=API_BASE_PATH)
app.include_router(version_routes.router, prefix=API_BASE_PATH)
app.include_router(auth_routes.router, prefix=API_BASE_PATH)
app.include_router(reference_routes.router, prefix=API_BASE_PATH)
app.include_router(inspection_routes.router, prefix=API_BASE_PATH)
app.include_router(evidence_routes.router, prefix=API_BASE_PATH)
app.include_router(storage_internal_routes.router, prefix=API_BASE_PATH)
app.include_router(integration_stub_routes.router, prefix=API_BASE_PATH)
app.include_router(ai_routes.router, prefix=API_BASE_PATH)
app.include_router(comparison_routes.router, prefix=API_BASE_PATH)
app.include_router(review_routes.router, prefix=API_BASE_PATH)
app.include_router(damage_case_routes.router, prefix=API_BASE_PATH)
app.include_router(integration_routes.router, prefix=API_BASE_PATH)
app.include_router(report_routes.router, prefix=API_BASE_PATH)
app.include_router(monitoring_routes.router, prefix=API_BASE_PATH)
app.include_router(demo_routes.router, prefix=API_BASE_PATH)
app.include_router(trip_routes.router, prefix=API_BASE_PATH)
app.include_router(tenant_routes.router, prefix=API_BASE_PATH)
app.include_router(vehicle_routes.router, prefix=API_BASE_PATH)
app.include_router(developer_routes.router, prefix=API_BASE_PATH)
app.include_router(ext_api_routes.router, prefix=API_BASE_PATH)
app.include_router(public_report_routes.router, prefix=API_BASE_PATH)
app.include_router(benchmark_routes.router, prefix=API_BASE_PATH)


@app.on_event("startup")
async def on_startup() -> None:
    db = get_db()
    await ensure_indexes(db)
    await seed_baseline_principals()
    await seed_capture_positions()
    await seed_tenant_branding()
    await db.di_schema_version.update_one(
        {"version": "sprint-05"},
        {"$setOnInsert": {"version": "sprint-05", "appliedAt": __import__("datetime").datetime.now(__import__("datetime").timezone.utc)}},
        upsert=True,
    )
    log_event(logger, 20, "Damage Intelligence API ready", baseApiPath=API_BASE_PATH)


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await close_db()
    log_event(logger, 20, "Damage Intelligence API shutdown complete")


# Root probe (not under /api — used only by container orchestrators).
@app.get("/")
async def root_probe():
    return {"service": "damage-intelligence-api", "apiBasePath": API_BASE_PATH}
