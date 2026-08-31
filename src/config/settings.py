"""Centralized configuration management using Pydantic Settings."""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """InboxPilot application settings loaded from environment or .env file."""

    # Application Configuration
    app_name: str = "InboxPilot"
    app_env: str = "development"
    host: str = "127.0.0.1"
    port: int = 8000
    log_level: str = "INFO"

    # Google Gemini & ADK Configuration
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.6-flash"

    # Gmail API Configuration
    gmail_credentials_file: str = "credentials.json"
    gmail_token_file: str = "token.json"
    gmail_user_id: str = "me"

    # Notion API Configuration
    notion_api_key: str = ""
    notion_database_id: str = ""

    # Firestore Configuration (Future Memory System)
    firestore_project_id: str = ""
    google_application_credentials: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """Retrieve and cache application settings instance."""
    return Settings()
