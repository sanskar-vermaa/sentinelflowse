from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models.organization import MemberRole


class RegisterRequest(BaseModel):
    email: EmailStr
    display_name: str = Field(min_length=2, max_length=120)
    password: str = Field(min_length=10, max_length=128)
    organization_name: str = Field(min_length=2, max_length=160)


class RegisterResponse(BaseModel):
    user_id: UUID
    organization_id: UUID
    role: MemberRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(max_length=256)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=1, max_length=4096)


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
