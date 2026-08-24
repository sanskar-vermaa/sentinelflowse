from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models.organization import MemberRole


class RegisterRequest(BaseModel):
    email: EmailStr
    display_name: str = Field(min_length=2, max_length=120)
    password: str = Field(min_length=10, max_length=128)
    organization_name: str = Field(min_length=2, max_length=160)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class MembershipRead(BaseModel):
    organization_id: UUID
    organization_name: str
    role: MemberRole


class MeResponse(BaseModel):
    id: UUID
    email: str
    display_name: str
    memberships: list[MembershipRead]

