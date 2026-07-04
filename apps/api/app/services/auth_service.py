from dataclasses import dataclass
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.models.organization import MemberRole, Organization, OrganizationMembership, User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse


@dataclass(frozen=True)
class RegistrationResult:
    user: User
    organization: Organization
    membership: OrganizationMembership


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register(self, request: RegisterRequest) -> RegistrationResult:
        slug = self._slugify(request.organization_name)
        user = User(
            email=request.email.lower(),
            display_name=request.display_name,
            password_hash=hash_password(request.password),
        )
        organization = Organization(name=request.organization_name, slug=slug)
        membership = OrganizationMembership(user=user, organization=organization, role=MemberRole.owner)

        self.db.add_all([user, organization, membership])
        self.db.commit()
        self.db.refresh(user)
        self.db.refresh(organization)
        self.db.refresh(membership)
        return RegistrationResult(user=user, organization=organization, membership=membership)

    def login(self, request: LoginRequest) -> TokenResponse | None:
        user = self.db.scalar(select(User).where(User.email == request.email.lower()))
        if user is None or not verify_password(request.password, user.password_hash):
            return None

        access_token = create_access_token(
            subject=str(user.id),
            expires_delta=timedelta(minutes=settings.access_token_minutes),
            claims={"email": user.email},
        )
        refresh_token = create_access_token(
            subject=str(user.id),
            expires_delta=timedelta(days=settings.refresh_token_days),
            claims={"type": "refresh"},
        )
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.access_token_minutes * 60,
        )

    @staticmethod
    def _slugify(value: str) -> str:
        normalized = value.strip().lower()
        cleaned = "".join(char if char.isalnum() else "-" for char in normalized)
        return "-".join(part for part in cleaned.split("-") if part)

