import logging
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import Settings, settings, validate_settings

logger = logging.getLogger("sentinelflow")


def create_app(config: Settings = settings) -> FastAPI:
    problems = validate_settings(config)
    if problems and config.is_production:
        raise RuntimeError("Refusing to start in production: " + "; ".join(problems))
    for problem in problems:
        logger.warning("Configuration: %s", problem)

    docs = config.enable_docs and not config.is_production
    app = FastAPI(
        title=config.app_name,
        version=config.version,
        description="Incident response API: alert ingestion with deduplication, incidents, workflows and audit logs.",
        docs_url="/docs" if docs else None,
        redoc_url="/redoc" if docs else None,
        openapi_url="/openapi.json" if docs else None,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-API-Key", "X-Request-ID"],
    )

    @app.middleware("http")
    async def request_context(request: Request, call_next):
        # Propagate a request id for log correlation and add hardening headers.
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id[:64]
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault("Cache-Control", "no-store")
        return response

    app.include_router(api_router, prefix="/api/v1")
    return app


app = create_app()
