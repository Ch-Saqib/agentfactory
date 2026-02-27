"""Configuration settings for Lesson Shorts Generator."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Server
    port: int = 8001

    # Gemini API (get from: https://aistudio.google.com/app/apikey)
    gemini_api_key: str = "dev-key"
    gemini_model: str = "gemini-2.0-flash-exp"

    # Pollinations.ai - FREE image generation (no API key needed)
    replicate_api_key: str = ""
    flux_model: str = "black-forest-labs/flux-schnell"

    # Edge-TTS
    edge_tts_voice: str = "en-US-AriaNeural"

    # PostgreSQL (format: postgresql://user:password@host/database)
    shorts_database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/shorts"

    # Cloudflare R2 (for production, use real values)
    r2_account_id: str = "dev-account"
    r2_access_key_id: str = "dev-key"
    r2_secret_access_key: str = "dev-secret"
    r2_bucket_name: str = "agentfactory-shorts"
    r2_public_url: str = "https://dev.r2.dev"
    r2_custom_domain: str = ""

    # Content API
    content_api_url: str = "http://localhost:8000"

    # Security
    allowed_origins: str = "http://localhost:3000,http://localhost:8001"
    admin_secret: str = "dev-secret-change-in-production"

    # Development
    dev_mode: bool = True
    dev_user_id: str = "dev-user-123"
    dev_user_email: str = "dev@example.com"
    dev_user_name: str = "Developer"

    # Cost Control
    max_cost_per_video: float = 0.006
    daily_budget_alert: float = 10.0
    monthly_budget_limit: float = 100.0

    # Generation Settings
    target_duration: int = 60
    max_duration: int = 90
    num_scenes: int = 3

    @property
    def allowed_origins_list(self) -> list[str]:
        """Parse allowed origins from comma-separated string."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]


# Global settings instance
settings = Settings()
