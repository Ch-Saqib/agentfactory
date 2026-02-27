"""Visual Generation Service using Pollinations.ai (Free) and Carbon.

This service generates visuals for short video scenes:
- Scene images via Pollinations.ai - FREE (no API key needed)
- Code screenshots via carbon.now.sh - Free
- Simple in-memory caching (30-minute TTL)

Target Cost: $0.00 per image (completely free)
"""

import hashlib
import json
import logging
import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

import httpx

from shorts_generator.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class GeneratedImage:
    """Represents a generated image.

    Attributes:
        url: CDN URL or direct URL to the image
        visual_hash: Hash of the visual description (for caching)
        width: Image width in pixels
        height: Image height in pixels
        generation_method: How the image was generated (pollinations, carbon, cached)
        cost_usd: Cost to generate this image in USD
    """

    url: str
    visual_hash: str
    width: int
    height: int
    generation_method: str
    cost_usd: float


class VisualGenerator:
    """Generates visuals for short video scenes."""

    # Carbon.now.sh API endpoint
    CARBON_API = "https://carbon.now.sh/api/cook"

    # Pollinations.ai - FREE, no API key needed
    POLLINATIONS_API = "https://image.pollinations.ai/prompt"

    # Free service - $0 cost
    POLLINATIONS_COST_PER_IMAGE = 0.0

    # Image dimensions for vertical video (9:16 aspect ratio)
    IMAGE_WIDTH = 1080
    IMAGE_HEIGHT = 1920

    # Simple in-memory cache
    _cache: dict[str, tuple[dict, float]] = {}  # {hash: (data, expiry_time)}

    def __init__(self):
        """Initialize the visual generator."""
        self._http_client: httpx.AsyncClient | None = None

    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=60.0)
        return self._http_client

    def _hash_visual_description(self, description: str) -> str:
        """Generate a hash for the visual description.

        Args:
            description: Visual description text

        Returns:
            SHA256 hash of the description
        """
        return hashlib.sha256(description.encode()).hexdigest()

    async def _get_cached_image(self, visual_hash: str) -> GeneratedImage | None:
        """Check if an image exists in cache.

        Args:
            visual_hash: Hash of the visual description

        Returns:
            Cached GeneratedImage if found and not expired, None otherwise
        """
        try:
            cached_data, expiry_time = self._cache.get(visual_hash, (None, 0))

            if cached_data and time.time() < expiry_time:
                logger.info(f"Cache hit for visual: {visual_hash[:8]}...")
                return GeneratedImage(
                    url=cached_data["url"],
                    visual_hash=visual_hash,
                    width=cached_data["width"],
                    height=cached_data["height"],
                    generation_method="cached",
                    cost_usd=0.0,  # No cost for cached images
                )
            elif cached_data:
                # Cache expired, clean it up
                del self._cache[visual_hash]

        except Exception as e:
            logger.warning(f"Cache lookup failed: {e}")

        return None

    async def _cache_image(self, visual_hash: str, image: GeneratedImage) -> None:
        """Cache an image for future use.

        Args:
            visual_hash: Hash of the visual description
            image: GeneratedImage to cache
        """
        try:
            # Cache for 30 minutes (1800 seconds)
            expiry_time = time.time() + 1800

            self._cache[visual_hash] = (
                {
                    "url": image.url,
                    "width": image.width,
                    "height": image.height,
                },
                expiry_time,
            )

            # Clean up old entries periodically
            if len(self._cache) > 1000:
                current_time = time.time()
                expired_keys = [
                    k for k, (_, exp) in self._cache.items()
                    if exp < current_time
                ]
                for k in expired_keys:
                    del self._cache[k]

            logger.info(f"Cached visual: {visual_hash[:8]}...")
        except Exception as e:
            logger.warning(f"Failed to cache image: {e}")

    async def generate_scene_image(
        self,
        visual_description: str,
        style: str = "tech, modern, AI aesthetic",
    ) -> GeneratedImage:
        """Generate a scene image using Pollinations.ai (FREE).

        Args:
            visual_description: Description of the desired image
            style: Style modifier for the image

        Returns:
            GeneratedImage object with image URL

        Raises:
            Exception: If image generation fails
        """
        visual_hash = self._hash_visual_description(visual_description)

        # Check cache first
        cached = await self._get_cached_image(visual_hash)
        if cached:
            return cached

        logger.info(f"Generating scene image: {visual_description[:50]}...")

        # Prepare Pollinations.ai request (FREE, no API key needed)
        prompt = f"{visual_description}, {style}, cinematic, high quality, detailed"

        try:
            # Build URL with parameters
            # Pollinations.ai generates images on-demand with GET requests
            params = {
                "prompt": prompt,
                "width": self.IMAGE_WIDTH,
                "height": self.IMAGE_HEIGHT,
                "seed": str(hash(visual_description) % 1000000),  # Deterministic but varied
                "model": "flux",  # Using Flux model via Pollinations
                "nologo": "true",  # Remove watermark
            }

            # Encode parameters
            encoded_params = "&".join(f"{k}={quote(str(v))}" for k, v in params.items())
            image_url = f"{self.POLLINATIONS_API}?{encoded_params}"

            logger.info(f"Pollinations.ai URL: {image_url[:100]}...")

            # Verify the image is accessible
            client = await self._get_http_client()
            verify_response = await client.head(image_url, timeout=30.0)

            if verify_response.status_code != 200:
                logger.warning(f"Image verification returned {verify_response.status_code}, continuing anyway")

            image = GeneratedImage(
                url=image_url,
                visual_hash=visual_hash,
                width=self.IMAGE_WIDTH,
                height=self.IMAGE_HEIGHT,
                generation_method="pollinations",
                cost_usd=self.POLLINATIONS_COST_PER_IMAGE,  # FREE!
            )

            # Cache the result
            await self._cache_image(visual_hash, image)

            return image

        except Exception as e:
            logger.error(f"Scene image generation failed: {e}")
            raise

    async def generate_code_screenshot(
        self,
        code: str,
        language: str = "python",
    ) -> GeneratedImage:
        """Generate a syntax-highlighted code screenshot via carbon.now.sh.

        Args:
            code: Code to render
            language: Programming language

        Returns:
            GeneratedImage object with screenshot URL

        Raises:
            Exception: If screenshot generation fails
        """
        visual_hash = self._hash_visual_description(f"code:{language}:{code[:100]}")

        # Check cache first
        cached = await self._get_cached_image(visual_hash)
        if cached:
            return cached

        logger.info(f"Generating code screenshot for {language} code")

        try:
            client = await self._get_http_client()

            # Call carbon.now.sh API
            response = await client.post(
                self.CARBON_API,
                json={
                    "code": code,
                    "language": language,
                    "theme": "monokai",
                    "backgroundColor": "#1e1e1e",
                    "windowControls": True,
                    "lineNumbers": True,
                    "width": self.IMAGE_WIDTH,
                    "exportSize": "2x",
                },
                headers={"Content-Type": "application/json"},
                timeout=30.0,
            )

            if response.status_code != 200:
                error_text = response.text
                logger.error(f"Carbon API error: {error_text}")
                raise Exception(f"Carbon generation failed: {error_text}")

            # Carbon returns the SVG directly
            svg_content = response.text

            # For now, we'll return a data URL (in production, you'd upload this to R2)
            # TODO: Upload to R2 and return proper URL
            import base64

            svg_data_url = f"data:image/svg+xml;base64,{base64.b64encode(svg_content.encode()).decode()}"

            image = GeneratedImage(
                url=svg_data_url,
                visual_hash=visual_hash,
                width=self.IMAGE_WIDTH,
                height=self.IMAGE_HEIGHT,  # Approximate
                generation_method="carbon",
                cost_usd=0.0,  # Carbon is free
            )

            # Cache the result
            await self._cache_image(visual_hash, image)

            return image

        except Exception as e:
            logger.error(f"Code screenshot generation failed: {e}")
            raise

    async def generate_thumbnail(
        self,
        first_scene_visual: str,
        lesson_title: str,
    ) -> GeneratedImage:
        """Generate a thumbnail image for the video.

        Args:
            first_scene_visual: Visual description of the first scene
            lesson_title: Title of the lesson

        Returns:
            GeneratedImage for the thumbnail

        Raises:
            Exception: If thumbnail generation fails
        """
        # Create a more visually appealing thumbnail prompt
        thumbnail_prompt = f"""{first_scene_visual}

Add a bold overlay text: "{lesson_title}"

Style: Eye-catching thumbnail for short video platform, with high contrast, modern typography, engaging composition."""

        return await self.generate_scene_image(thumbnail_prompt)


# Singleton instance
visual_generator = VisualGenerator()
