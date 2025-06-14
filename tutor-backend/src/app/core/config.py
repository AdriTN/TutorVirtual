from pydantic import Field, HttpUrl, PositiveInt, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import List, Optional
from functools import lru_cache

PROJECT_ROOT = Path(__file__).resolve().parents[3]

class Settings(BaseSettings):
    # ── FastAPI ───────────────────────────────────────────────
    api_title: str = "Tutor Virtual API"
    api_version: str = "0.1.0"
    cors_origins: List[HttpUrl] = Field(default_factory=list)
    port: PositiveInt = Field(5173, env="PORT")

    # ── DB ────────────────────────────────────────────────────
    database_url: PostgresDsn = Field(..., env="DATABASE_URL")
    pool_size: PositiveInt = 10

    # ── Auth ─────────────────────────────────────────────────
    jwt_secret: str = Field(..., env="JWT_SECRET", min_length=32)
    jwt_algorithm: str = "HS256"
    jwt_access_minutes: PositiveInt = 30
    jwt_refresh_days: PositiveInt = 3
    bcrypt_rounds: PositiveInt = 12

    # ── Google OAuth ─────────────────────────────────────────
    google_client_id: str = Field(..., env="GOOGLE_CLIENT_ID")
    google_client_secret: str = Field(..., env="GOOGLE_CLIENT_SECRET")

    # ── Ollama / RAG ─────────────────────────────────────────
    ollama_url: HttpUrl = Field(..., env="OLLAMA_URL")
    api_key: Optional[str] = Field(None, env="API_KEY")

    # ── Misc ─────────────────────────────────────────────────
    env: str = Field("dev", env="ENV")

    model_config = SettingsConfigDict(
        env_file        = (PROJECT_ROOT / ".env").as_posix(),
        env_file_encoding = "utf-8",
        case_sensitive  = False,
        extra           = "forbid",
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()
