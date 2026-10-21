from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.logging import sanitize_sensitive_url


class Settings(BaseSettings):
    PROJECT_NAME: str = "DocuMind API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "insecure-dev-secret-key-change-in-production"

    # CORS origins allowed to interact with the API
    CORS_ORIGINS: list[str] | str = ["http://localhost:3000", "http://127.0.0.1:3000"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            if not v.strip():
                return []
            if v.startswith("[") and v.endswith("]"):
                import json

                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return [str(origin).rstrip("/") for origin in v]
        return []

    # Database settings
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "documind"
    DATABASE_URL: str | None = None

    # Connection pool configuration
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800

    @property
    def sync_database_url(self) -> str:
        if self.DATABASE_URL:
            # Normalize schema if needed
            if self.DATABASE_URL.startswith("postgresql://"):
                return self.DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)
            return self.DATABASE_URL
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def sanitized_database_url(self) -> str:
        """Returns database URL with password masked for safe diagnostic logging."""
        return sanitize_sensitive_url(self.sync_database_url)

    # Redis configuration
    REDIS_URL: str = "redis://localhost:6379/0"

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        """Ensures that default development credentials are not used in production."""
        if self.ENVIRONMENT.lower() in ("production", "prod"):
            insecure_passwords = {"postgres", "password", "admin", "root", "", "changeme"}
            if self.POSTGRES_PASSWORD in insecure_passwords and not self.DATABASE_URL:
                raise ValueError(
                    "Insecure POSTGRES_PASSWORD detected in production environment. "
                    "A strong, unique password must be configured."
                )
            if self.SECRET_KEY in (
                "insecure-dev-secret-key-change-in-production",
                "secret",
                "changeme",
            ):
                raise ValueError(
                    "Default or insecure SECRET_KEY cannot be used in production environment."
                )
        return self

    model_config = SettingsConfigDict(
        env_file=(".env", "../../.env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
