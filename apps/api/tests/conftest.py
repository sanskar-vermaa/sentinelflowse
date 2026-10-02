"""Fixtures for API tests.

Each test gets a fresh database: a temporary SQLite file by default, or the
Postgres database in TEST_DATABASE_URL (CI runs the suite against both).
"""

import os
from uuid import uuid4

# Tests sign tokens with a realistic-length secret (set before app imports).
os.environ.setdefault("JWT_SECRET", "test-secret-key-that-is-long-enough-for-hs256")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import close_all_sessions, sessionmaker

from app import models  # noqa: F401
from app.api.routes.auth import login_limiter
from app.db import get_db
from app.db.base import Base
from app.main import create_app

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")
PASSWORD = "correct-horse-battery"


@pytest.fixture
def engine(tmp_path):
    url = TEST_DATABASE_URL or f"sqlite:///{tmp_path}/test.db"
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    eng = create_engine(url, connect_args=connect_args)
    Base.metadata.drop_all(eng)
    Base.metadata.create_all(eng)
    yield eng
    # Sessions opened directly by tests still hold locks on Postgres, which
    # would block DROP TABLE forever.
    close_all_sessions()
    Base.metadata.drop_all(eng)
    eng.dispose()


@pytest.fixture
def session_factory(engine):
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@pytest.fixture
def client(session_factory):
    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    login_limiter.reset()
    with TestClient(app) as test_client:
        yield test_client


class Account:
    def __init__(self, client: TestClient, email: str, org_id: str, user_id: str, tokens: dict):
        self.client = client
        self.email = email
        self.org_id = org_id
        self.user_id = user_id
        self.tokens = tokens

    @property
    def headers(self) -> dict:
        return {"Authorization": f"Bearer {self.tokens['access_token']}"}

    def url(self, path: str = "") -> str:
        return f"/api/v1/organizations/{self.org_id}{path}"

    def get(self, path, **kw):
        return self.client.get(self.url(path), headers=self.headers, **kw)

    def post(self, path, json=None, **kw):
        return self.client.post(self.url(path), json=json, headers=self.headers, **kw)

    def patch(self, path, json=None, **kw):
        return self.client.patch(self.url(path), json=json, headers=self.headers, **kw)


@pytest.fixture
def register(client):
    def _register(email: str | None = None, org: str = "Acme Corp") -> Account:
        email = email or f"user-{uuid4().hex[:8]}@example.com"
        res = client.post(
            "/api/v1/auth/register",
            json={"email": email, "display_name": "Test User", "password": PASSWORD, "organization_name": org},
        )
        assert res.status_code == 201, res.text
        body = res.json()
        tokens = client.post("/api/v1/auth/login", json={"email": email, "password": PASSWORD}).json()
        return Account(client, email, body["organization_id"], body["user_id"], tokens)

    return _register


@pytest.fixture
def owner(register):
    return register()


@pytest.fixture
def add_member(register, session_factory):
    """Register a user in their own org, then add them to `account`'s org with `role`."""
    from app.models.organization import MemberRole, OrganizationMembership

    def _add(account: Account, role: str) -> Account:
        member = register()
        db = session_factory()
        db.add(OrganizationMembership(user_id=member.user_id, organization_id=account.org_id, role=MemberRole(role)))
        db.commit()
        db.close()
        member.org_id = account.org_id
        return member

    return _add


def incident_payload(**overrides) -> dict:
    return {"title": "Checkout latency", "severity": "high", "dedupe_key": "checkout-latency-1", **overrides}
