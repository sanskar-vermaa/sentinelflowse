from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db import get_db
from app.models.organization import OrganizationMembership, User

UNAUTHORIZED_HEADERS = {"WWW-Authenticate": "Bearer"}


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail, headers=UNAUTHORIZED_HEADERS)


def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    db: Session = Depends(get_db),
) -> User:
    if authorization is None or not authorization.lower().startswith("bearer "):
        raise _unauthorized("Missing bearer token")

    token = authorization.split(" ", 1)[1].strip()
    # Only access tokens are accepted here; refresh tokens are rejected.
    payload = decode_access_token(token)
    if payload is None:
        raise _unauthorized("Invalid bearer token")

    try:
        user_id = UUID(str(payload["sub"]))
    except ValueError:
        raise _unauthorized("Invalid bearer token") from None

    user = db.get(User, user_id)
    if user is None:
        raise _unauthorized("User no longer exists")
    return user


def get_membership(db: Session, user_id: UUID, organization_id: UUID) -> OrganizationMembership | None:
    return db.scalar(
        select(OrganizationMembership).where(
            OrganizationMembership.user_id == user_id,
            OrganizationMembership.organization_id == organization_id,
        )
    )
