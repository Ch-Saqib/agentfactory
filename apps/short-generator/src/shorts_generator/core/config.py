"""Configuration settings for Lesson Shorts Generator."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def find_env_file() -> Path:
    """Find .env file by checking current directory and parent directories."""
    current_dir = Path(__file__).parent.parent
    env_paths = [
        current_dir / ".env",
        current_dir / "src" / ".env",
        Path.cwd() / ".env",
        Path.home() / ".env",
    ]
    for path in env_paths:
        if path.exists():
            return path
    # Return default even if it doesn't exist (pydantic will handle missing file)
    return current_dir / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=str(find_env_file()),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Server
    port: int = 8003

    # Gemini API (get from: https://aistudio.google.com/app/apikey)
    # Used for both script generation and image generation
    # Recommended models for free tier:
    #   - gemini-2.0-flash-lite: 15 requests/minute (best for automation)
    #   - gemini-2.0-flash-exp: Good balance of speed and quality
    #   - gemini-1.5-flash: Higher limits, faster but less capable
    #   - gemini-2.5-flash: Most capable but only 20 requests/day on free tier
    gemini_api_key: str = Field(default="", validation_alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="", validation_alias="GEMINI_MODEL")

    # Script Generation Provider (options: gemini, groq, openai)
    # - gemini: Uses Google Gemini (requires GEMINI_API_KEY)
    # - groq: Uses Groq with Llama models (requires GROQ_API_KEY) - BEST FREE TIER
    # - openai: Uses OpenAI (requires OPENAI_API_KEY)
    script_provider: str = "groq"

    # Groq API (get from: https://console.groq.com/keys)
    # Free tier: Very generous - no hard limits for development
    # Models: llama-3.3-70b-versatile, llama-3.1-8b-instant, mixtral-8x7b-32768
    groq_api_key: str = Field(default="", validation_alias="GROQ_API_KEY")
    groq_model: str = "llama-3.3-70b-versatile"

    # Image Generation Provider (options: imagen, replicate, pollinations)
    # - imagen: Google Imagen via Gemini API ($0.03-$0.06/image, uses existing GEMINI_API_KEY)
    # - replicate: Replicate Flux Schnell (~$0.0025/image, requires REPLICATE_API_KEY)
    # - pollinations: Free service (no API key needed)
    image_provider: str = "imagen"

    # Google Imagen Settings (when image_provider=imagen)
    # Imagen model: imagen-3.0-generate-001, imagen-4.0-generate-001 (paid preview)
    imagen_model: str = "imagen-3.0-generate-001"
    # Number of images to generate per prompt (usually 1)
    imagen_num_images: int = 1
    # Aspect ratio for generated images (9:16 for vertical video)
    imagen_aspect_ratio: str = "9:16"

    # Edge-TTS (free alternative)
    edge_tts_voice: str = "en-US-AriaNeural"
    # TTS speaking rate (0.25 to 4.0, 1.0 = normal). < 1.0 is slower.
    tts_speaking_rate: float = 0.85

    # Google Cloud TTS
    # Path to service account credentials JSON file
    # Get from: https://console.cloud.google.com/iam-admin/serviceaccounts
    google_cloud_credentials_path: str = Field(default="", validation_alias="GOOGLE_CLOUD_CREDENTIALS_PATH")
    # TTS provider: "edge_tts" (free) or "google_tts" (paid, better timing)
    tts_provider: str = "edge_tts"
    # Google Cloud TTS voice preset (narration_male, narration_female, news, casual, dramatic)
    google_tts_voice_preset: str = "narration_male"
    # Google Cloud TTS encoding (MP3, WAV, OGG_OPUS)
    google_tts_encoding: str = "MP3"
    # Google Cloud TTS sample rate (16000, 24000, 48000)
    google_tts_sample_rate: int = 24000

    # PostgreSQL (format: postgresql://user:password@host/database)
    shorts_database_url: str = Field(default="postgresql+asyncpg://postgres:postgres@localhost:5432/shorts", validation_alias="SHORTS_DATABASE_URL")

    # Cloudflare R2 (for production, use real values)
    r2_account_id: str = Field(default="", validation_alias="R2_ACCOUNT_ID")
    r2_access_key_id: str = Field(default="", validation_alias="R2_ACCESS_KEY_ID")
    r2_secret_access_key: str = Field(default="", validation_alias="R2_SECRET_ACCESS_KEY")
    r2_bucket_name: str = Field(default="agentfactory-shorts", validation_alias="R2_BUCKET_NAME")
    r2_public_url: str = Field(default="", validation_alias="R2_PUBLIC_URL")
    r2_custom_domain: str = Field(default="", validation_alias="R2_CUSTOM_DOMAIN")

    # Security
    allowed_origins: str = Field(default="http://localhost:3000,http://localhost:8001", validation_alias="ALLOWED_ORIGINS")

    # Cost Control
    max_cost_per_video: float = 0.006

    # Generation Settings
    target_duration: int = 60
    max_duration: int = 90
    num_scenes: int = 3

    # Frame Generation Settings
    # Video dimensions (9:16 aspect ratio for vertical video)
    video_width: int = 1080
    video_height: int = 1920
    video_fps: int = 30
    # Colors (hex format)
    video_bg_color: str = "#1a1a2e"  # Dark blue-black
    video_text_color: str = "#ffffff"  # White
    video_accent_color: str = "#0f3460"  # Dark blue
    # Font settings
    video_title_font_size: int = 80
    video_content_font_size: int = 48
    video_font_path: str = ""  # Empty = use system default
    # Animation settings
    video_fade_duration: float = 0.5  # Fade in/out duration in seconds
    # Text animation mode: "word_sync", "scrolling", or "auto"
    video_text_animation_mode: str = "word_sync"
    # Text settings
    video_max_line_width: int = 980  # Max text width in pixels
    video_line_spacing: float = 1.5  # Line spacing multiplier

    @property
    def allowed_origins_list(self) -> list[str]:
        """Parse allowed origins from comma-separated string."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]


# Global settings instance
settings = Settings()
