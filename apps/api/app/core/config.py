from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SentinelFlow API"
    version: str = "0.1.0"
    environment: str = "local"
    enable_docs: bool = True
    database_url: str = "postgresql+psycopg://sentinelflow:sentinelflow@localhost:5432/sentinelflow"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = "replace-me"
    access_token_minutes: int = 30
    refresh_token_days: int = 14
    ai_provider: str = "deterministic"
    gemini_api_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
