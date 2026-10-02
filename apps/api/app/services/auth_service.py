from dataclasses import dataclass
from datetime import timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    DUMMY_PASSWORD_HASH,
    create_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.organization import (
    MemberRole,
    Organization,
    OrganizationMembership,
    User,
)
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse


class EmailAlreadyRegistered(Exception):
    pass


@dataclass(frozen=True)
class RegistrationResult:
    user: User
    organization: Organization
    membership: OrganizationMembership


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register(self, request: RegisterRequest) -> RegistrationResult:
        email = request.email.lower()
        if self.db.scalar(select(User.id).where(User.email == email)) is not None:
            raise EmailAlreadyRegistered(email)

        user = User(email=email, display_name=request.display_name.strip(), password_hash=hash_password(request.password))
        organization = Organization(
            name=request.organization_name.strip(),
            slug=self._unique_slug(request.organization_name),
        )
        membership = OrganizationMembership(user=user, organization=organization, role=MemberRole.owner)

        self.db.add_all([user, organization, membership])
        try:
            self.db.commit()
        except IntegrityError as exc:  # lost a race with a concurrent registration
            self.db.rollback()
            raise EmailAlreadyRegistered(email) from exc
        self.db.refresh(user)
        self.db.refresh(organization)
        self.db.refresh(membership)
        return RegistrationResult(user=user, organization=organization, membership=membership)

    def login(self, request: LoginRequest) -> TokenResponse | None:
        user = self.db.scalar(select(User).where(User.email == request.email.lower()))
        # Always run a bcrypt check so response time doesn't reveal whether
        # the email is registered.
        password_ok = verify_password(request.password, user.password_hash if user else DUMMY_PASSWORD_HASH)
        if user is None or not password_ok:
            return None
        return self.issue_tokens(user)

    def refresh(self, refresh_token: str) -> TokenResponse | None:
        payload = decode_token(refresh_token, "refresh")
        if payload is None:
            return None
        try:
            user = self.db.get(User, UUID(str(payload["sub"])))
        except ValueError:
            return None
        return self.issue_tokens(user) if user else None

    @staticmethod
    def issue_tokens(user: User) -> TokenResponse:
        access_token = create_token(
            str(user.id),
            "access",
            timedelta(minutes=settings.access_token_minutes),
            claims={"email": user.email},
        )
        refresh_token = create_token(str(user.id), "refresh", timedelta(days=settings.refresh_token_days))
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.access_token_minutes * 60,
        )

    def _unique_slug(self, name: str) -> str:
        base = self._slugify(name) or "org"
        slug, n = base, 2
        while self.db.scalar(select(Organization.id).where(Organization.slug == slug)) is not None:
            slug, n = f"{base}-{n}", n + 1
        return slug

    @staticmethod
    def _slugify(value: str) -> str:
        normalized = value.strip().lower()
        cleaned = "".join(char if char.isalnum() else "-" for char in normalized)
        return "-".join(part for part in cleaned.split("-") if part)[:80]
