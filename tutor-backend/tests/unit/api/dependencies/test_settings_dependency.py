# tests/unit/api/dependencies/test_settings.py

import pytest
from src.api.dependencies.settings import settings_dependency
from src.core.config import get_settings, Settings

@pytest.fixture(autouse=True)
def clear_settings_cache():
    # Limpiamos el cache de lru_cache para que cada test 
    # lea de nuevo las variables de entorno
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()

def test_settings_dependency_yields_settings_object(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@localhost/db")
    monkeypatch.setenv("JWT_SECRET", "j" * 32)
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "google-id")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "google-secret")
    monkeypatch.setenv("OLLAMA_URL", "http://ollama.local")

    gen = settings_dependency()
    settings = next(gen)
    assert isinstance(settings, Settings)
    assert settings is get_settings()
    with pytest.raises(StopIteration):
        next(gen)

def test_settings_dependency_reflects_env_values(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://foo:bar@db/test")
    monkeypatch.setenv("JWT_SECRET", "s" * 32)
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "cid")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "csecret")
    monkeypatch.setenv("OLLAMA_URL", "https://ollama.test")
    monkeypatch.setenv("API_KEY", "my-api-key")

    settings = next(settings_dependency())

    # Para PostgresDsn hay que convertir a str
    assert str(settings.database_url) == "postgresql://foo:bar@db/test"
    assert settings.jwt_secret == "s" * 32
    assert settings.google_client_id == "cid"
    assert settings.google_client_secret == "csecret"
    assert settings.ollama_url == "https://ollama.test"
    assert settings.api_key == "my-api-key"
