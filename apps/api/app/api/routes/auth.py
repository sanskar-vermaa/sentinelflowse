from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db import get_db
from app.models.organization import User
from app.schemas.auth import LoginRequest, MeResponse, MembershipRead, RegisterRequest, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)) -> dict[str, str]:
    result = AuthService(db).register(request)
    return {
        "user_id": str(result.user.id),
        "organization_id": str(result.organization.id),
        "role": result.membership.role.value,
    }


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    token = AuthService(db).login(request)
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
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

