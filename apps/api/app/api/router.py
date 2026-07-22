from fastapi import APIRouter

from app.api.routes import alerts, audit, auth, health, incidents

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(health.router, tags=["health"])
api_router.include_router(incidents.router)
api_router.include_router(alerts.router)
api_router.include_router(audit.router)
