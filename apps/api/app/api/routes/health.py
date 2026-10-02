from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db import get_db
from app.schemas.health import HealthResponse, ReadinessResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Liveness: the process is up."""
    return HealthResponse(status="ok", service="api", version=settings.version)


@router.get("/health/ready", response_model=ReadinessResponse)
def readiness(response: Response, db: Session = Depends(get_db)) -> ReadinessResponse:
    """Readiness: the database answers queries."""
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return ReadinessResponse(status="unavailable", database="unreachable")
    return ReadinessResponse(status="ok", database="ok")
