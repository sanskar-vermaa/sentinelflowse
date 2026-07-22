from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.alerts import AlertIngestRequest, AlertIngestResponse
from app.services.alert_service import AlertService
from app.services.api_key_service import ApiKeyService

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.post("/ingest", response_model=AlertIngestResponse, status_code=status.HTTP_202_ACCEPTED)
def ingest_alert(
    request: AlertIngestRequest,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    db: Session = Depends(get_db),
) -> AlertIngestResponse:
    if not x_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing API key")

    api_key = ApiKeyService(db).authenticate(x_api_key)
    if api_key is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    return AlertService(db).ingest(api_key.organization_id, request)

