"""Configuration settings for Slothreader loaded from environment and .env."""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Observability
    sentry_dsn: Optional[str] = None
    environment: str = "local-desktop"
    release: str = "slothreader@0.1.0"

    # Local Ollama Inference
    ollama_host: str = "http://localhost:11434"
    gemma_model: str = "gemma2:2b"
    inference_timeout_seconds: float = 120.0

    # Live IMAP Settings (read-only BODY.PEEK[])
    imap_server: str = "imap.gmail.com"
    imap_port: int = 993
    imap_username: Optional[str] = None
    imap_password: Optional[str] = None
    imap_folder: str = "Newsletters"
    imap_max_emails: int = 15


# Singleton settings instance
settings = Settings()
