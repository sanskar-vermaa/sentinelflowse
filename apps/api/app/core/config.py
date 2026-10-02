from pydantic_settings import BaseSettings, SettingsConfigDict

INSECURE_JWT_SECRETS = {"", "replace-me", "change-me", "secret"}


class Settings(BaseSettings):
    app_name: str = "SentinelFlow API"
    version: str = "1.0.0"
    app_env: str = "local"
    enable_docs: bool = True
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    database_url: str = "postgresql+psycopg://sentinelflow:sentinelflow@localhost:5432/sentinelflow"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "replace-me"
    access_token_minutes: int = 30
    refresh_token_days: int = 14
    # Comma-separated list of browser origins allowed to call the API.
    web_origin: str = "http://localhost:3000"
    login_rate_limit: int = 10  # failed logins per email+IP per 15 minutes
    ai_provider: str = "deterministic"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def environment(self) -> str:
        return self.app_env

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.web_origin.split(",") if origin.strip()]


def validate_settings(config: Settings) -> list[str]:
    """Return configuration problems; in production any problem is fatal."""
    problems: list[str] = []
    if config.jwt_secret in INSECURE_JWT_SECRETS or len(config.jwt_secret) < 32:
        problems.append("JWT_SECRET must be a random value of at least 32 characters")
    if config.ai_provider == "gemini" and not config.gemini_api_key:
        problems.append("AI_PROVIDER=gemini requires GEMINI_API_KEY")
    return problems


settings = Settings()
