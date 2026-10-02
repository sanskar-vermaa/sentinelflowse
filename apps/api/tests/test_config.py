import pytest

from app.core.config import Settings, validate_settings
from app.core.rate_limit import SlidingWindowLimiter
from app.core.security import hash_password, verify_password
from app.main import create_app

STRONG = "s" * 40


def test_validate_settings_flags_weak_secrets_and_missing_ai_key():
    assert validate_settings(Settings(jwt_secret=STRONG)) == []
    assert "JWT_SECRET" in validate_settings(Settings(jwt_secret="replace-me"))[0]
    assert "JWT_SECRET" in validate_settings(Settings(jwt_secret="short"))[0]
    assert validate_settings(Settings(jwt_secret=STRONG, ai_provider="gemini")) == [
        "AI_PROVIDER=gemini requires GEMINI_API_KEY"
    ]


def test_production_refuses_insecure_config():
    with pytest.raises(RuntimeError, match="Refusing to start in production"):
        create_app(Settings(app_env="production", jwt_secret="replace-me"))


def test_production_hides_docs():
    app = create_app(Settings(app_env="production", jwt_secret=STRONG))
    assert app.docs_url is None and app.openapi_url is None
    assert create_app(Settings(jwt_secret=STRONG)).docs_url == "/docs"


def test_cors_origins_are_comma_separated():
    assert Settings(web_origin="https://a.example, https://b.example").cors_origins == [
        "https://a.example",
        "https://b.example",
    ]


def test_rate_limiter_window():
    now = [0.0]
    limiter = SlidingWindowLimiter(limit=2, window_seconds=10, clock=lambda: now[0])
    limiter.hit("k")
    limiter.hit("k")
    assert limiter.is_blocked("k")
    assert not limiter.is_blocked("other")
    now[0] = 10.0
    assert not limiter.is_blocked("k")
    limiter.hit("k")
    limiter.reset("k")
    assert not limiter.is_blocked("k")


def test_long_passwords_and_bad_hashes():
    long_password = "p" * 100
    hashed = hash_password(long_password)
    assert verify_password(long_password, hashed)
    assert not verify_password("anything", "not-a-bcrypt-hash")


def test_stored_bcrypt_hashes_still_verify():
    # A fixed $2b$ cost-12 hash, the format passlib wrote for existing users.
    stored = "$2b$12$.fbk1mHTe17GnBgkOMaxRubhcbh2R1R9X4Mwzig3qapmmp4JSR7Z2"
    assert verify_password("sentinelflow-demo", stored)
    assert not verify_password("sentinelflow-dem0", stored)


def test_platform_postgres_urls_use_psycopg():
    for raw in ("postgres://u:p@h:5432/db", "postgresql://u:p@h/db"):
        assert Settings(database_url=raw).database_url.startswith("postgresql+psycopg://u:p@h")
    assert Settings(database_url="sqlite:///./x.db").database_url == "sqlite:///./x.db"
