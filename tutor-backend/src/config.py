from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    ollama_url: str = Field(None, env="OLLAMA_URL")
    api_key: str = Field(None, env="API_KEY")


settings = Settings()
