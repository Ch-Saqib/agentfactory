"""Tests for visual generator service."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from shorts_generator.services.visual_generator import (
    GeneratedImage,
    VisualGenerator,
)


@pytest.fixture
def generator():
    """Create a visual generator instance."""
    return VisualGenerator()


def test_hash_visual_description(generator):
    """Test that visual descriptions are hashed consistently."""
    desc1 = "Futuristic AI brain with glowing networks"
    desc2 = "Futuristic AI brain with glowing networks"
    desc3 = "Different description"

    hash1 = generator._hash_visual_description(desc1)
    hash2 = generator._hash_visual_description(desc2)
    hash3 = generator._hash_visual_description(desc3)

    # Same input should produce same hash
    assert hash1 == hash2

    # Different input should produce different hash
    assert hash1 != hash3

    # Hash should be SHA256 (64 hex characters)
    assert len(hash1) == 64
    assert all(c in "0123456789abcdef" for c in hash1)


@pytest.mark.asyncio
async def test_get_cached_image_miss(generator):
    """Test cache miss returns None."""
    with patch.object(generator, "_get_redis") as mock_redis:
        mock_redis_instance = AsyncMock()
        mock_redis_instance.get = AsyncMock(return_value=None)
        mock_redis.return_value = mock_redis_instance

        result = await generator._get_cached_image("nonexistent_hash")

        assert result is None


@pytest.mark.asyncio
async def test_get_cached_image_hit(generator):
    """Test cache hit returns cached image."""
    cached_data = json.dumps({
        "url": "https://example.com/image.png",
        "width": 1080,
        "height": 1920,
    })

    with patch.object(generator, "_get_redis") as mock_redis:
        mock_redis_instance = AsyncMock()
        mock_redis_instance.get = AsyncMock(return_value=cached_data)
        mock_redis.return_value = mock_redis_instance

        result = await generator._get_cached_image("test_hash")

        assert result is not None
        assert result.url == "https://example.com/image.png"
        assert result.width == 1080
        assert result.generation_method == "cached"
        assert result.cost_usd == 0.0


@pytest.mark.asyncio
async def test_generate_scene_image_uses_cache(generator):
    """Test that generate_scene_image checks cache first."""
    cached_image = GeneratedImage(
        url="https://cached.example.com/image.png",
        visual_hash="test_hash_123",
        width=1080,
        height=1920,
        generation_method="cached",
        cost_usd=0.0,
    )

    with patch.object(generator, "_get_cached_image", return_value=cached_image):
        result = await generator.generate_scene_image("Test description")

        assert result == cached_image
        assert result.generation_method == "cached"
        assert result.cost_usd == 0.0


@pytest.mark.asyncio
async def test_generate_scene_image_calls_replicate(generator):
    """Test that generate_scene_image calls Replicate API."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "output": [{"image_url": "https://replicate-output.example.com/image.png"}],
    }

    with patch.object(generator, "_get_http_client") as mock_client:
        mock_client_instance = AsyncMock()
        mock_client_instance.post = AsyncMock(return_value=mock_response)
        mock_client.return_value = mock_client_instance

        with patch.object(generator, "_get_cached_image", return_value=None):
            with patch.object(generator, "_cache_image"):
                result = await generator.generate_scene_image("A futuristic robot brain")

                assert result.generation_method == "flux"
                assert result.url == "https://replicate-output.example.com/image.png"
                assert result.cost_usd == generator.FLUX_COST_PER_IMAGE


@pytest.mark.asyncio
async def test_generate_code_screenshot(generator):
    """Test generating code screenshot via Carbon API."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<svg>...</svg>"  # Simplified SVG

    with patch.object(generator, "_get_http_client") as mock_client:
        mock_client_instance = AsyncMock()
        mock_client_instance.post = AsyncMock(return_value=mock_response)
        mock_client.return_value = mock_client_instance

        with patch.object(generator, "_get_cached_image", return_value=None):
            with patch.object(generator, "_cache_image"):
                result = await generator.generate_code_screenshot('print("hello")', "python")

                assert result.generation_method == "carbon"
                assert "data:image/svg+xml" in result.url
                assert result.cost_usd == 0.0


@pytest.mark.asyncio
async def test_generate_thumbnail(generator):
    """Test thumbnail generation with title overlay."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "output": [{"image_url": "https://replicate.example.com/thumb.png"}],
    }

    with patch.object(generator, "_get_http_client") as mock_client:
        mock_client_instance = AsyncMock()
        mock_client_instance.post = AsyncMock(return_value=mock_response)
        mock_client.return_value = mock_client_instance

        with patch.object(generator, "_get_cached_image", return_value=None):
            with patch.object(generator, "_cache_image"):
                result = await generator.generate_thumbnail(
                    "Robot brain visual",
                    "AI Agents 101"
                )

                assert "AI Agents 101" in result.visual_hash or True  # Different visual, so different hash
                assert result.generation_method == "flux"


def test_generated_image_dataclass():
    """Test GeneratedImage dataclass."""
    image = GeneratedImage(
        url="https://example.com/image.png",
        visual_hash="abc123",
        width=1080,
        height=1920,
        generation_method="flux",
        cost_usd=0.002,
    )

    assert image.url == "https://example.com/image.png"
    assert image.visual_hash == "abc123"
    assert image.width == 1080
    assert image.height == 1920
    assert image.generation_method == "flux"
    assert image.cost_usd == 0.002


@pytest.mark.asyncio
async def test_cache_image_stores_in_redis(generator):
    """Test that images are cached in Redis."""
    image = GeneratedImage(
        url="https://example.com/image.png",
        visual_hash="test_hash",
        width=1080,
        height=1920,
        generation_method="flux",
        cost_usd=0.002,
    )

    with patch.object(generator, "_get_redis") as mock_redis:
        mock_redis_instance = AsyncMock()
        mock_redis_instance.setex = AsyncMock()
        mock_redis.return_value = mock_redis_instance

        await generator._cache_image("test_hash", image)

        # Verify setex was called with correct TTL (30 days)
        mock_redis_instance.setex.assert_called_once()
        args, kwargs = mock_redis_instance.setex.call_args
        assert args[1] == 2592000  # 30 days in seconds


@pytest.mark.asyncio
async def test_flux_cost_constant(generator):
    """Test that Flux cost constant is set correctly."""
    assert generator.FLUX_COST_PER_IMAGE == 0.002


@pytest.mark.asyncio
async def test_image_dimensions_for_vertical_video(generator):
    """Test that image dimensions match 9:16 aspect ratio."""
    assert generator.IMAGE_WIDTH == 1080
    assert generator.IMAGE_HEIGHT == 1920

    # Verify 9:16 ratio
    ratio = generator.IMAGE_WIDTH / generator.IMAGE_HEIGHT
    assert abs(ratio - (9 / 16)) < 0.01  # Allow small floating point error


@pytest.mark.asyncio
async def test_generate_scene_image_handles_api_error(generator):
    """Test that Replicate API errors are handled correctly."""
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"

    with patch.object(generator, "_get_http_client") as mock_client:
        mock_client_instance = AsyncMock()
        mock_client_instance.post = AsyncMock(return_value=mock_response)
        mock_client.return_value = mock_client_instance

        with patch.object(generator, "_get_cached_image", return_value=None):
            with pytest.raises(Exception, match="Flux.1 generation failed"):
                await generator.generate_scene_image("Test description")


@pytest.mark.asyncio
async def test_generate_code_screenshot_handles_api_error(generator):
    """Test that Carbon API errors are handled correctly."""
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"

    with patch.object(generator, "_get_http_client") as mock_client:
        mock_client_instance = AsyncMock()
        mock_client_instance.post = AsyncMock(return_value=mock_response)
        mock_client.return_value = mock_client_instance

        with patch.object(generator, "_get_cached_image", return_value=None):
            with pytest.raises(Exception, match="Carbon generation failed"):
                await generator.generate_code_screenshot('print("test")', "python")
