import os
import pytest
from pydantic import ValidationError
from src.core.config import Settings, get_settings

@pytest.fixture(autouse=True)
def clear_env(monkeypatch):
    """
    Limpia las env-vars relevantes antes de cada test.
    """
    for var in [
        "DATABASE_URL",
        "JWT_SECRET",
        "GOOGLE_CLIENT_ID",
        "GOOGLE_CLIENT_SECRET",
        "OLLAMA_URL",
        "API_KEY",
        "PORT",
        "ENV",
        "AUTO_CREATE_TABLES",
        "RUN_MIGRATIONS",
    ]:
        monkeypatch.delenv(var, raising=False)
    yield

def test_required_env_provided(monkeypatch):
    """
    Si las env-vars requeridas están, Settings() se instancia correctamente
    y sus defaults y aliases funcionan.
    """
    # set exactly the env‐vars we need
    monkeypatch.setenv("DATABASE_URL",         "postgresql://u:p@localhost/db")
    monkeypatch.setenv("JWT_SECRET",           "s" * 32)
    monkeypatch.setenv("GOOGLE_CLIENT_ID",     "google-id")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "google-secret")
    monkeypatch.setenv("OLLAMA_URL",           "http://localhost:3000")
    monkeypatch.setenv("API_KEY",              "ollama-key")

    # override some defaults
    monkeypatch.setenv("PORT",               "4242")
    monkeypatch.setenv("ENV",                "production")
    monkeypatch.setenv("AUTO_CREATE_TABLES", "yes")
    monkeypatch.setenv("RUN_MIGRATIONS_ON_STARTUP",     "true")

    cfg = Settings()

    # FastAPI defaults
    assert cfg.api_title    == "Tutor Virtual API"
    assert cfg.api_version  == "0.1.0"
    assert cfg.port         == 4242
    assert cfg.env          == "production"

    # DB
    assert str(cfg.database_url) == "postgresql://u:p@localhost/db"
    assert cfg.pool_size          == 10

    # Auth
    assert cfg.jwt_secret        == "s" * 32
    assert cfg.jwt_algorithm     == "HS256"
    assert cfg.bcrypt_rounds     == 12

    # Google
    assert cfg.google_client_id     == "google-id"
    assert cfg.google_client_secret == "google-secret"

    # Ollama
    assert cfg.ollama_url == "http://localhost:3000"
    assert cfg.api_key    == "ollama-key"

    # Flags
    assert cfg.auto_create_tables       is True
    assert cfg.run_migrations_on_startup is True

def test_cors_origins_default(monkeypatch):
    """
    Si no indicas CORS_ORIGINS en .env, debe salir la lista vacía.
    """
    # Solo las vars necesarias para instanciar
    monkeypatch.setenv("DATABASE_URL",         "postgresql://u:p@localhost/db")
    monkeypatch.setenv("JWT_SECRET",           "a"*32)
    monkeypatch.setenv("GOOGLE_CLIENT_ID",     "g")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "s")
    monkeypatch.setenv("OLLAMA_URL",           "http://x")
    cfg = Settings()
    assert cfg.cors_origins == []

def test_get_settings_is_cached(monkeypatch):
    """
    get_settings() usa lru_cache: varias llamadas devuelven la MISMA instancia.
    """
    monkeypatch.setenv("DATABASE_URL",         "postgresql://u:p@localhost/db")
    monkeypatch.setenv("JWT_SECRET",           "b"*32)
    monkeypatch.setenv("GOOGLE_CLIENT_ID",     "id")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "sec")
    monkeypatch.setenv("OLLAMA_URL",           "http://y")
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2

def test_invalid_port(monkeypatch):
    """
    Si PORT no es un int válido, pydantic debe lanzar ValidationError.
    """
    monkeypatch.setenv("DATABASE_URL",         "postgresql://u:p@localhost/db")
    monkeypatch.setenv("JWT_SECRET",           "c"*32)
    monkeypatch.setenv("GOOGLE_CLIENT_ID",     "id")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "sec")
    monkeypatch.setenv("OLLAMA_URL",           "http://z")
    monkeypatch.setenv("PORT", "not-an-int")
    with pytest.raises(ValidationError):
        Settings()
