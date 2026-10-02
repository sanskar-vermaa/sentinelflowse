"""Password hashing and JWT handling.

Uses the maintained `bcrypt` and `PyJWT` packages (passlib and python-jose
are unmaintained; python-jose has known algorithm-confusion and DoS CVEs).
Hashes created by the previous passlib setup verify unchanged.
"""

from datetime import UTC, datetime, timedelta
from typing import Any, Literal

import bcrypt
import jwt

from app.core.config import settings

ALGORITHM = "HS256"
TokenType = Literal["access", "refresh"]

# bcrypt only looks at the first 72 bytes; passlib truncated silently and
# bcrypt>=5 raises instead, so truncate explicitly to keep old hashes valid.
_BCRYPT_MAX_BYTES = 72


def _encode_password(password: str) -> bytes:
    return password.encode("utf-8")[:_BCRYPT_MAX_BYTES]


def hash_password(password: str) -> str:
    return bcrypt.hashpw(_encode_password(password), bcrypt.gensalt()).decode("ascii")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(_encode_password(password), password_hash.encode("ascii"))
    except (ValueError, TypeError):
        return False


# A real hash to check against when the user doesn't exist, so login takes
# the same time either way and can't be used to discover registered emails.
DUMMY_PASSWORD_HASH = hash_password("timing-equaliser-not-a-real-password")


def create_token(
    subject: str,
    token_type: TokenType = "access",
    expires_delta: timedelta | None = None,
    claims: dict[str, Any] | None = None,
) -> str:
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        **(claims or {}),
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + (expires_delta or timedelta(minutes=settings.access_token_minutes)),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)


def create_access_token(
    subject: str, expires_delta: timedelta | None = None, claims: dict[str, Any] | None = None
) -> str:
    return create_token(subject, "access", expires_delta, claims)


def decode_token(token: str, expected_type: TokenType = "access") -> dict[str, Any] | None:
    """Return the payload if the signature, expiry and token type are valid."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[ALGORITHM],
            options={"require": ["exp", "sub", "type"]},
        )
    except jwt.PyJWTError:
        return None
    if payload.get("type") != expected_type:
        return None
    return payload


def decode_access_token(token: str) -> dict[str, Any] | None:
    return decode_token(token, "access")
