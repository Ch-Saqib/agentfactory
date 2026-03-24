"""Tests for configuration settings."""

import os
from unittest.mock import patch

from shorts_generator.core.config import Settings


def test_settings_defaults():
    """Test that settings have correct defaults."""
    with patch.dict(
        os.environ,
        {
            "GEMINI_API_KEY": "test-key",
            "REPLICATE_API_KEY": "test-key",
            "REDIS_URL": "redis://localhost",
            "REDIS_PASSWORD": "test-password",
            "SHORTS_DATABASE_URL": "postgresql://test",
            "R2_ACCOUNT_ID": "test-account",
            "R2_ACCESS_KEY_ID": "test-key",
            "R2_SECRET_ACCESS_KEY": "test-secret",
            "R2_PUBLIC_URL": "https://test.r2.dev",
            "ADMIN_SECRET": "test-secret",
            "CELERY_BROKER_URL": "redis://localhost",
            "CELERY_RESULT_BACKEND": "redis://localhost",
        },
        clear=True,
    ):
        settings = Settings()

        assert settings.port == 8001
        assert settings.gemini_model == "gemini-2.0-flash-exp"
        assert settings.edge_tts_voice == "en-US-AriaNeural"
        assert settings.max_cost_per_video == 0.006
        assert settings.target_duration == 60
        assert settings.max_duration == 90
        assert settings.num_scenes == 3


def test_allowed_origins_parsing():
    """Test that allowed origins are parsed correctly."""
    with patch.dict(
        os.environ,
        {
            "GEMINI_API_KEY": "test-key",
            "REPLICATE_API_KEY": "test-key",
            "REDIS_URL": "redis://localhost",
            "REDIS_PASSWORD": "test-password",
            "SHORTS_DATABASE_URL": "postgresql://test",
            "R2_ACCOUNT_ID": "test-account",
            "R2_ACCESS_KEY_ID": "test-key",
            "R2_SECRET_ACCESS_KEY": "test-secret",
            "R2_PUBLIC_URL": "https://test.r2.dev",
            "ALLOWED_ORIGINS": "http://localhost:3000,https://example.com",
            "ADMIN_SECRET": "test-secret",
            "CELERY_BROKER_URL": "redis://localhost",
            "CELERY_RESULT_BACKEND": "redis://localhost",
        },
        clear=True,
    ):
        settings = Settings()

        assert settings.allowed_origins_list == [
            "http://localhost:3000",
            "https://example.com",
        ]
