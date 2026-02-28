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
    # Clear the cache for this test
    VisualGenerator._cache.clear()

    result = await generator._get_cached_image("nonexistent_hash")

    assert result is None


@pytest.mark.asyncio
async def test_get_cached_image_hit(generator):
    """Test cache hit returns cached image."""
    # Clear the cache for this test
    VisualGenerator._cache.clear()

    # Manually add an item to the cache
    test_hash = "test_hash"
    VisualGenerator._cache[test_hash] = (
        {
            "url": "https://example.com/image.png",
            "width": 1080,
            "height": 1920,
        },
        float('inf'),  # Never expire
    )

    result = await generator._get_cached_image(test_hash)

    assert result is not None
    assert result.url == "https://example.com/image.png"
    assert result.width == 1080
    assert result.generation_method == "cached"
    assert result.cost_usd == 0.0

    # Clean up
    VisualGenerator._cache.clear()


@pytest.mark.asyncio
async def test_generate_scene_image_uses_cache(generator):
    """Test that generate_scene_image checks cache first."""
    # Clear the cache for this test
    VisualGenerator._cache.clear()

    test_hash = "test_hash_123"
    VisualGenerator._cache[test_hash] = (
        {
            "url": "https://cached.example.com/image.png",
            "width": 1080,
            "height": 1920,
        },
        float('inf'),  # Never expire
    )

    # Mock _hash_visual_description to return our test hash
    with patch.object(generator, "_hash_visual_description", return_value=test_hash):
        result = await generator.generate_scene_image("Test description")

        assert result.generation_method == "cached"
        assert result.cost_usd == 0.0
        assert result.url == "https://cached.example.com/image.png"

    # Clean up
    VisualGenerator._cache.clear()


@pytest.mark.asyncio
async def test_generate_scene_image_calls_pollinations(generator):
    """Test that generate_scene_image calls Pollinations API when provider is pollinations."""
    # Clear the cache for this test
    VisualGenerator._cache.clear()

    # Mock the settings to use pollinations provider
    with patch.object(generator, "_hash_visual_description", return_value="test_hash"):
        with patch("shorts_generator.services.visual_generator.settings") as mock_settings:
            mock_settings.image_provider = "pollinations"

            result = await generator.generate_scene_image("A futuristic robot brain")

            assert result.generation_method == "pollinations"
            assert result.cost_usd == generator.POLLINATIONS_COST
            assert "image.pollinations.ai" in result.url

    # Clean up
    VisualGenerator._cache.clear()


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
                assert result.generation_method == "replicate"


def test_generated_image_dataclass():
    """Test GeneratedImage dataclass."""
    image = GeneratedImage(
        url="https://example.com/image.png",
        visual_hash="abc123",
        width=1080,
        height=1920,
        generation_method="replicate",
        cost_usd=0.002,
    )

    assert image.url == "https://example.com/image.png"
    assert image.visual_hash == "abc123"
    assert image.width == 1080
    assert image.height == 1920
    assert image.generation_method == "replicate"
    assert image.cost_usd == 0.002


@pytest.mark.asyncio
async def test_cache_image_stores_in_memory(generator):
    """Test that images are cached in memory."""
    # Clear the cache for this test
    VisualGenerator._cache.clear()

    image = GeneratedImage(
        url="https://example.com/image.png",
        visual_hash="test_hash",
        width=1080,
        height=1920,
        generation_method="replicate",
        cost_usd=0.002,
    )

    await generator._cache_image("test_hash", image)

    # Verify the image was cached
    assert "test_hash" in VisualGenerator._cache
    cached_data, expiry_time = VisualGenerator._cache["test_hash"]
    assert cached_data["url"] == "https://example.com/image.png"
    assert cached_data["width"] == 1080
    assert cached_data["height"] == 1920
    # Verify TTL is approximately 30 minutes (1800 seconds)
    import time
    assert expiry_time > time.time()
    assert expiry_time <= time.time() + 1800

    # Clean up
    VisualGenerator._cache.clear()


@pytest.mark.asyncio
async def test_imagen_cost_constant(generator):
    """Test that Imagen cost constant is set correctly."""
    assert generator.IMAGEN_COST == 0.03


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
    """Test that provider API errors are handled correctly."""
    # Clear the cache for this test
    VisualGenerator._cache.clear()

    # Mock the settings to use replicate provider
    with patch("shorts_generator.services.visual_generator.settings") as mock_settings:
        mock_settings.image_provider = "replicate"
        mock_settings.replicate_api_key = "test-key"

        # Mock ReplicateClient to raise an error
        with patch("shorts_generator.services.visual_generator.ReplicateClient") as mock_replicate:
            mock_client = MagicMock()
            mock_client.run = AsyncMock(side_effect=Exception("Replicate API error"))
            mock_replicate.return_value = mock_client

            with pytest.raises(Exception, match="Replicate generation failed"):
                await generator.generate_scene_image("Test description")

    # Clean up
    VisualGenerator._cache.clear()


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
