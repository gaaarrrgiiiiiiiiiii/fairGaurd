"""Application configuration via pydantic-settings (reads from .env)."""
import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "FairGuard"
    API_V1_STR: str = "/v1"

    # Database — override in .env for postgres
    DATABASE_URL: str = "sqlite:///./fairguard.db"

    # JWT
    JWT_SECRET: str = "fairguard-dev-secret-change-in-prod"
    JWT_EXPIRY_HOURS: int = 24

    # CORS — comma-separated list of allowed frontend origins
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # LLM API Keys
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    MISTRAL_API_KEY: str = ""


settings = Settings()
