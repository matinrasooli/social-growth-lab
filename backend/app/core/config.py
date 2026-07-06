"""
Application configuration.

All secrets and provider selection come from environment variables (.env).
No secrets are ever hard-coded here.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "Social Growth Lab"
    ENV: str = "development"
    SECRET_KEY: str = "change-me-in-production"
    DATABASE_URL: str = "sqlite:///./social_growth_lab.db"

    # Auth
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 12

    # LLM provider abstraction
    DEFAULT_LLM_PROVIDER: str = "mock"  # openai | anthropic | ollama | mock
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    ANTHROPIC_API_KEY: str | None = None
    ANTHROPIC_MODEL: str = "claude-sonnet-4-6"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"

    # LLM call safety
    LLM_MAX_CALLS_PER_MINUTE: int = 20
    LLM_MAX_RETRIES: int = 2

    # Uploads
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_MB: int = 200

    # CORS
    FRONTEND_ORIGIN: str = "http://localhost:5173"


@lru_cache
def get_settings() -> Settings:
    return Settings()
