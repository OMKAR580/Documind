import pytest

from app.core.config import Settings


def test_default_settings():
    settings = Settings()
    assert settings.PROJECT_NAME == "DocuMind API"
    assert settings.API_V1_STR == "/api/v1"
    assert "postgresql+psycopg2://" in settings.sync_database_url
    assert "documind" in settings.sync_database_url


def test_cors_origins_parsing():
    settings_str = Settings(CORS_ORIGINS="http://localhost:3000,http://example.com")
    assert "http://localhost:3000" in settings_str.CORS_ORIGINS
    assert "http://example.com" in settings_str.CORS_ORIGINS

    settings_list = Settings(CORS_ORIGINS=["http://test.com/"])
    assert settings_list.CORS_ORIGINS == ["http://test.com"]


def test_custom_database_url():
    custom_url = "postgresql://custom_user:custom_pass@db:5432/custom_db"
    settings = Settings(DATABASE_URL=custom_url)
    assert (
        settings.sync_database_url
        == "postgresql+psycopg2://custom_user:custom_pass@db:5432/custom_db"
    )


def test_sanitized_database_url():
    settings = Settings(
        POSTGRES_USER="myuser",
        POSTGRES_PASSWORD="supersecretpassword123",
        POSTGRES_SERVER="db.example.com",
        POSTGRES_DB="production_documind",
    )
    sanitized = settings.sanitized_database_url
    assert "supersecretpassword123" not in sanitized
    assert "myuser:***@db.example.com" in sanitized


def test_production_rejects_default_postgres_password():
    with pytest.raises(ValueError, match="Insecure POSTGRES_PASSWORD"):
        Settings(
            ENVIRONMENT="production",
            POSTGRES_PASSWORD="postgres",
            SECRET_KEY="a-very-secure-random-production-key-12345",
        )


def test_production_rejects_insecure_secret_key():
    with pytest.raises(ValueError, match="Default or insecure SECRET_KEY"):
        Settings(
            ENVIRONMENT="production",
            POSTGRES_PASSWORD="a-strong-unique-db-password-12345",
            SECRET_KEY="insecure-dev-secret-key-change-in-production",
        )


def test_production_valid_configuration():
    settings = Settings(
        ENVIRONMENT="production",
        POSTGRES_PASSWORD="a-strong-unique-db-password-12345",
        SECRET_KEY="a-very-secure-random-production-key-12345",
    )
    assert settings.ENVIRONMENT == "production"
    assert settings.POSTGRES_PASSWORD == "a-strong-unique-db-password-12345"
