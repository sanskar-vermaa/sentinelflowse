from fastapi.testclient import TestClient

from app.main import create_app


def test_health_check_returns_ok() -> None:
    client = TestClient(create_app())

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "api", "version": "1.0.0"}
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Request-ID"]


def test_request_id_is_echoed() -> None:
    client = TestClient(create_app())
    response = client.get("/api/v1/health", headers={"X-Request-ID": "abc123"})
    assert response.headers["X-Request-ID"] == "abc123"


def test_readiness_checks_the_database(client) -> None:
    assert client.get("/api/v1/health/ready").json() == {"status": "ok", "database": "ok"}


def test_readiness_reports_an_unreachable_database() -> None:
    from app.db import get_db

    class Down:
        def execute(self, *_):
            raise OSError("connection refused")

    app = create_app()
    app.dependency_overrides[get_db] = lambda: Down()
    res = TestClient(app).get("/api/v1/health/ready")
    assert res.status_code == 503
    assert res.json()["database"] == "unreachable"
