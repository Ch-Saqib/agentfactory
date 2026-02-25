"""Configuration settings for Lesson Shorts Generator."""

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

    # Gemini API
    gemini_api_key: str
    gemini_model: str = "gemini-2.0-flash-exp"

    # Pollinations.ai - FREE image generation (no API key needed)
    # Optional: Replicate API if you prefer paid service
    replicate_api_key: str = ""  # Optional, not required with Pollinations
    flux_model: str = "black-forest-labs/flux-schnell"  # Only used if replicate_api_key is set

    # Edge-TTS
    edge_tts_voice: str = "en-US-AriaNeural"

    # Redis
    redis_url: str
    redis_password: str

    # PostgreSQL
    shorts_database_url: str

    # Cloudflare R2
    r2_account_id: str
    r2_access_key_id: str
    r2_secret_access_key: str
    r2_bucket_name: str = "agentfactory-shorts"
    r2_public_url: str
    r2_custom_domain: str = ""  # Optional: Custom domain for CDN (e.g., cdn.example.com)

    # Content API
    content_api_url: str = "http://localhost:8000"

    # Security
    allowed_origins: str = "http://localhost:3000,https://agentfactory.panaversity.org"
    admin_secret: str

    # Development
    dev_mode: bool = False
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

    # Celery
    celery_broker_url: str
    celery_result_backend: str

    @property
    def allowed_origins_list(self) -> list[str]:
        """Parse allowed origins from comma-separated string."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]


# Global settings instance
settings = Settings()
