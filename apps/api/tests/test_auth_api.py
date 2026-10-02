from datetime import timedelta
from uuid import uuid4

import jwt

from app.core.config import settings
from app.core.security import ALGORITHM, create_token
from tests.conftest import PASSWORD

AUTH = "/api/v1/auth"


def test_register_creates_owner_of_new_org(client):
    res = client.post(
        f"{AUTH}/register",
        json={
            "email": "Ana@Example.com",
            "display_name": "Ana",
            "password": PASSWORD,
            "organization_name": "Ana's Org",
        },
    )
    assert res.status_code == 201
    assert res.json()["role"] == "owner"


def test_duplicate_email_is_a_conflict(client, owner):
    res = client.post(
        f"{AUTH}/register",
        json={"email": owner.email.upper(), "display_name": "Dup", "password": PASSWORD, "organization_name": "Other"},
    )
    assert res.status_code == 409


def test_same_org_name_gets_a_unique_slug(register, session_factory):
    from uuid import UUID

    from app.models.organization import Organization

    a, b = register(org="Same Name"), register(org="Same Name")
    with session_factory() as db:
        slugs = {db.get(Organization, UUID(x.org_id)).slug for x in (a, b)}
    assert slugs == {"same-name", "same-name-2"}


def test_register_validates_input(client):
    res = client.post(
        f"{AUTH}/register",
        json={"email": "not-an-email", "display_name": "x", "password": "short", "organization_name": "y"},
    )
    assert res.status_code == 422


def test_login_returns_tokens(client, owner):
    res = client.post(f"{AUTH}/login", json={"email": owner.email, "password": PASSWORD})
    body = res.json()
    assert res.status_code == 200
    assert body["token_type"] == "bearer"
    assert body["expires_in"] == settings.access_token_minutes * 60
    claims = jwt.decode(body["access_token"], settings.jwt_secret, algorithms=[ALGORITHM])
    assert claims["type"] == "access"


def test_login_rejects_wrong_password_and_unknown_email(client, owner):
    assert client.post(f"{AUTH}/login", json={"email": owner.email, "password": "wrong-password"}).status_code == 401
    assert client.post(f"{AUTH}/login", json={"email": "ghost@example.com", "password": PASSWORD}).status_code == 401


def test_failed_logins_are_rate_limited(client, owner):
    for _ in range(settings.login_rate_limit):
        assert client.post(f"{AUTH}/login", json={"email": owner.email, "password": "nope-nope"}).status_code == 401
    blocked = client.post(f"{AUTH}/login", json={"email": owner.email, "password": PASSWORD})
    assert blocked.status_code == 429


def test_me_lists_memberships(client, owner):
    res = client.get(f"{AUTH}/me", headers=owner.headers)
    assert res.status_code == 200
    body = res.json()
    assert body["email"] == owner.email
    assert body["memberships"][0]["organization_id"] == owner.org_id
    assert body["memberships"][0]["role"] == "owner"


def test_refresh_issues_new_tokens(client, owner):
    res = client.post(f"{AUTH}/refresh", json={"refresh_token": owner.tokens["refresh_token"]})
    assert res.status_code == 200
    me = client.get(f"{AUTH}/me", headers={"Authorization": f"Bearer {res.json()['access_token']}"})
    assert me.status_code == 200


def test_refresh_token_is_not_an_access_token(client, owner):
    res = client.get(f"{AUTH}/me", headers={"Authorization": f"Bearer {owner.tokens['refresh_token']}"})
    assert res.status_code == 401


def test_access_token_cannot_refresh(client, owner):
    res = client.post(f"{AUTH}/refresh", json={"refresh_token": owner.tokens["access_token"]})
    assert res.status_code == 401


def test_bad_bearer_tokens(client, owner):
    expired = create_token(owner.user_id, "access", timedelta(seconds=-5))
    not_uuid = create_token("not-a-uuid", "access")
    deleted = create_token(str(uuid4()), "access")
    forged = jwt.encode({"sub": owner.user_id, "type": "access", "exp": 9999999999}, "x" * 40, algorithm=ALGORITHM)
    unsigned = jwt.encode({"sub": owner.user_id, "type": "access", "exp": 9999999999}, None, algorithm="none")
    for token in (expired, not_uuid, deleted, forged, unsigned, "garbage"):
        res = client.get(f"{AUTH}/me", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 401, token
        assert res.headers["WWW-Authenticate"] == "Bearer"
    assert client.get(f"{AUTH}/me").status_code == 401
    assert client.get(f"{AUTH}/me", headers={"Authorization": "Basic abc"}).status_code == 401
