"""
Application configuration — loaded from environment variables via pydantic-settings.

CORS_ORIGINS accepts three formats in the .env file:
  - JSON array:        ["http://localhost:5173","http://localhost:3000"]
  - Comma-separated:  http://localhost:5173,http://localhost:3000
  - Single value:     http://localhost:5173
"""

from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application & Environment
    APP_ENV: str = "development"
    APP_NAME: str = "CloudPulse AI"
    APP_VERSION: str = "1.0.0"
    DEMO_MODE: bool = True

    # Backend
    BACKEND_HOST: str = "0.0.0.0"  # nosec B104
    BACKEND_PORT: int = 8000
    BACKEND_RELOAD: bool = True

    # Database
    DATABASE_URL: str = (
        "postgresql+asyncpg://cloudpulse_user:cloudpulse_dev_password@localhost:5432/cloudpulse"
    )

    # JWT Authentication
    JWT_SECRET_KEY: str = "insecure_default_change_in_production"
    SECRET_KEY: str | None = None
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    @property
    def effective_secret_key(self) -> str:
        return self.SECRET_KEY or self.JWT_SECRET_KEY

    # Gemini AI
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-pro"
    GEMINI_MAX_OUTPUT_TOKENS: int = 8192
    GEMINI_TEMPERATURE: float = 0.7

    # ChromaDB
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8001
    CHROMA_COLLECTION_NAME: str = "cloudpulse_vectors"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS — accepts list[str], JSON string array, comma-separated, or single URL
    CORS_ORIGINS: list[str] | str = ["http://localhost:5173", "http://localhost:3000"]

    @field_validator("CORS_ORIGINS", mode="after")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[str]:
        """
        Accept three formats:
          1. Already a list
          2. JSON array string:  '["http://a","http://b"]'
          3. Comma-separated:   'http://a,http://b'
          4. Single URL:        'http://a'
        """
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            stripped = v.strip()
            if stripped.startswith("["):
                import json

                return json.loads(stripped)
            return [origin.strip() for origin in stripped.split(",") if origin.strip()]
        return ["http://localhost:5173", "http://localhost:3000"]

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "text"

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"

    @field_validator("APP_ENV", mode="after")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        allowed = {"development", "demo", "staging", "production", "test"}
        if v.lower() not in allowed:
            return "development"
        return v.lower()


settings = Settings()

