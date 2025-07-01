from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic import Field, HttpUrl, PositiveInt, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── FastAPI ───────────────────────────────────────────────
    api_title:       str           = "Tutor Virtual API"
    api_version:     str           = "0.1.0"
    cors_origins:    List[HttpUrl] = Field(default_factory=list)
    port:            PositiveInt   = Field(5173, env="PORT")

    # ── DB ────────────────────────────────────────────────────
    database_url:    PostgresDsn   = Field("postgresql+psycopg://user:pass@localhost/test_db", env="DATABASE_URL")
    pool_size:       PositiveInt   = 10

    # ── Auth ─────────────────────────────────────────────────
    jwt_secret:      str           = Field(min_length=32, env="JWT_SECRET")
    jwt_algorithm:   str           = "HS256"
    jwt_access_minutes: PositiveInt = 30
    jwt_refresh_days:   PositiveInt = 3
    bcrypt_rounds:      PositiveInt = 12

    # ── Google OAuth ─────────────────────────────────────────
    google_client_id:     str      = Field("", env="GOOGLE_CLIENT_ID")
    google_client_secret: str      = Field("", env="GOOGLE_CLIENT_SECRET")
    google_redirect_uri:  str      = Field("", env="GOOGLE_REDIRECT_URI")

    # ── Ollama / RAG ─────────────────────────────────────────
    # We keep this as `str` so we don’t get HttpUrl’s extra slash
    ollama_url:      str           = Field("http://localhost:11434", env="OLLAMA_URL")
    api_key:         Optional[str] = Field(None, env="API_KEY")

    # ── Misc ─────────────────────────────────────────────────
    env:             str           = Field("dev", env="ENV")
    auto_create_tables:       bool = Field(False, env="AUTO_CREATE_TABLES")
    run_migrations_on_startup: bool = Field(False, env="RUN_MIGRATIONS")

@lru_cache
def get_settings() -> Settings:
    return Settings()
