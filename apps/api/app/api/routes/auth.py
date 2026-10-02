from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.rate_limit import SlidingWindowLimiter
from app.db import get_db
from app.models.organization import User
from app.schemas.auth import (
    LoginRequest,
    MembershipRead,
    MeResponse,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
)
from app.services.auth_service import AuthService, EmailAlreadyRegistered

router = APIRouter(prefix="/auth", tags=["auth"])

login_limiter = SlidingWindowLimiter(limit=settings.login_rate_limit, window_seconds=15 * 60)


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)) -> RegisterResponse:
    try:
        result = AuthService(db).register(request)
    except EmailAlreadyRegistered:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered") from None
    return RegisterResponse(
        user_id=result.user.id,
        organization_id=result.organization.id,
        role=result.membership.role,
    )


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, http_request: Request, db: Session = Depends(get_db)) -> TokenResponse:
    client = http_request.client.host if http_request.client else "unknown"
    key = f"{client}:{request.email.lower()}"
    if login_limiter.is_blocked(key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed login attempts. Try again in a few minutes.",
        )

    token = AuthService(db).login(request)
    if token is None:
        login_limiter.hit(key)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    login_limiter.reset(key)
    return token


@router.post("/refresh", response_model=TokenResponse)
def refresh(request: RefreshRequest, db: Session = Depends(get_db)) -> TokenResponse:
    token = AuthService(db).refresh(request.refresh_token)
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    return token


@router.get("/me", response_model=MeResponse)
def me(current_user: Annotated[User, Depends(get_current_user)]) -> MeResponse:
    return MeResponse(
        id=current_user.id,
        email=current_user.email,
        display_name=current_user.display_name,
        memberships=[
            MembershipRead(
                organization_id=membership.organization_id,
                organization_name=membership.organization.name,
                role=membership.role,
            )
            for membership in current_user.memberships
        ],
    )
