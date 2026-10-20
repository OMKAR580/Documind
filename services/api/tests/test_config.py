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
