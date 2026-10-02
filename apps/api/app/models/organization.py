from enum import StrEnum

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class MemberRole(StrEnum):
    owner = "owner"
    admin = "admin"
    responder = "responder"
    viewer = "viewer"


class User(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(120))
    password_hash: Mapped[str] = mapped_column(String(255))
    memberships: Mapped[list["OrganizationMembership"]] = relationship(back_populates="user")


class Organization(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(160), index=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    memberships: Mapped[list["OrganizationMembership"]] = relationship(back_populates="organization")


class OrganizationMembership(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "organization_memberships"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))
    role: Mapped[MemberRole] = mapped_column(Enum(MemberRole), default=MemberRole.viewer)

    user: Mapped[User] = relationship(back_populates="memberships")
    organization: Mapped[Organization] = relationship(back_populates="memberships")
