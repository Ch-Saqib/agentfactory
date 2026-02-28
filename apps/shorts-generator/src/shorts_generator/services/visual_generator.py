"""Visual Generation Service supporting multiple providers.

This service generates visuals for short video scenes:
- Scene images via Google Imagen / Replicate / Pollinations.ai
- Code screenshots via carbon.now.sh - Free
- Simple in-memory caching (30-minute TTL)

Providers:
- Google Imagen: ~$0.03-$0.06 per image (via Gemini API)
- Replicate Flux Schnell: ~$0.0025 per image
- Pollinations.ai: FREE (no API key)
"""

import asyncio
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

    # Replicate API
    REPLICATE_MODEL = "black-forest-labs/flux-schnell"  # Fast, affordable
    REPLICATE_TIMEOUT = 120  # 2 minutes timeout

    # Pollinations.ai (free, no API key)
    POLLINATIONS_API = "https://image.pollinations.ai/prompt"

    # Image dimensions for vertical video (9:16 aspect ratio)
    IMAGE_WIDTH = 1080
    IMAGE_HEIGHT = 1920

    # Provider costs (USD per image)
    IMAGEN_COST = 0.03  # Approx $0.03 per image for Imagen 3
    REPLICATE_COST = 0.0025  # Approx $0.0025 per image with Flux Schnell
    POLLINATIONS_COST = 0.0  # Free

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

    async def _generate_with_replicate(
        self,
        prompt: str,
        visual_hash: str,
    ) -> GeneratedImage:
        """Generate image using Replicate API.

        Requires REPLICATE_API_KEY environment variable.
        Uses Flux Schnell model for fast, affordable generation.

        Args:
            prompt: Image generation prompt
            visual_hash: Hash for caching

        Returns:
            GeneratedImage object with image URL

        Raises:
            Exception: If image generation fails
        """
        api_key = getattr(settings, 'replicate_api_key', None)
        if not api_key:
            raise Exception("REPLICATE_API_KEY not configured. Please add it to your .env file.")

        logger.info(f"Submitting to Replicate: {prompt[:50]}...")

        client = await self._get_http_client()

        # Replicate API base URL
        replicate_api = "https://api.replicate.com/v1"

        # Headers for authentication
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Prefer": "wait",  # Synchronous execution
        }

        # Prepare input for Flux Schnell
        input_data = {
            "prompt": prompt,
            "width": self.IMAGE_WIDTH,
            "height": self.IMAGE_HEIGHT,
            "num_outputs": 1,
            "aspect_ratio": "9:16",
        }

        try:
            # Create prediction
            response = await client.post(
                f"{replicate_api}/models/{self.REPLICATE_MODEL}/predictions",
                json={"input": input_data},
                headers=headers,
                timeout=30.0,
            )
            response.raise_for_status()

            prediction = response.json()
            prediction_id = prediction.get("id")

            if not prediction_id:
                raise Exception(f"Invalid response from Replicate: {prediction}")

            logger.info(f"Prediction created: {prediction_id}")

            # Poll for result (up to 2 minutes)
            max_attempts = 40
            for attempt in range(max_attempts):
                await asyncio.sleep(3)  # Wait 3 seconds between polls

                status_response = await client.get(
                    f"{replicate_api}/predictions/{prediction_id}",
                    headers=headers,
                    timeout=10.0,
                )
                status_response.raise_for_status()
                status = status_response.json()

                status_str = status.get("status", "unknown")
                logger.debug(f"Polling attempt {attempt + 1}: status={status_str}")

                if status_str == "succeeded":
                    output = status.get("output")
                    if isinstance(output, list) and len(output) > 0:
                        image_url = output[0]
                        logger.info(f"Replicate generation complete: {image_url[:80]}...")

                        return GeneratedImage(
                            url=image_url,
                            visual_hash=visual_hash,
                            width=self.IMAGE_WIDTH,
                            height=self.IMAGE_HEIGHT,
                            generation_method="replicate",
                            cost_usd=self.REPLICATE_COST,
                        )
                    else:
                        raise Exception(f"Unexpected output format: {type(output)}")

                elif status_str in ["failed", "canceled"]:
                    error = status.get("error", "Unknown error")
                    raise Exception(f"Replicate prediction {status_str}: {error}")

            raise Exception("Replicate prediction timed out after 2 minutes")

        except httpx.HTTPStatusError as e:
            logger.error(f"Replicate API error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Replicate API error: {e.response.status_code}") from e
        except Exception as e:
            logger.error(f"Replicate generation failed: {e}")
            raise

    async def _generate_with_imagen(
        self,
        prompt: str,
        visual_hash: str,
    ) -> GeneratedImage:
        """Generate image using Google Imagen API.

        Requires GEMINI_API_KEY environment variable.
        Uses Imagen 3 model for high-quality generation.

        Note: Imagen requires billing enabled on your Google AI project.
        For free tier, use IMAGE_PROVIDER=pollinations instead.

        Args:
            prompt: Image generation prompt
            visual_hash: Hash for caching

        Returns:
            GeneratedImage object with image URL

        Raises:
            Exception: If image generation fails
        """
        from google import genai
        from google.genai import types

        api_key = getattr(settings, 'gemini_api_key', None)
        if not api_key or api_key == "dev-key":
            raise Exception("GEMINI_API_KEY not configured. Please add it to your .env file.")

        imagen_model = getattr(settings, 'imagen_model', 'imagen-3.0-generate-001')
        aspect_ratio = getattr(settings, 'imagen_aspect_ratio', '9:16')

        logger.info(f"Submitting to Google Imagen ({imagen_model}): {prompt[:50]}...")

        try:
            import asyncio

            # Create the GenAI client
            client = genai.Client(api_key=api_key)

            # Generate image using Imagen - run in thread pool for async
            response = await asyncio.to_thread(
                client.models.generate_images,
                model=imagen_model,
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=getattr(settings, 'imagen_num_images', 1),
                    aspect_ratio=aspect_ratio,
                ),
            )

            # Extract the generated image
            if response.generated_images and len(response.generated_images) > 0:
                # Get the first image
                generated_image = response.generated_images[0]

                # The image bytes are in the image property
                image_bytes = generated_image.image.image_bytes

                # For now, return a base64 data URL (in production, upload to R2)
                import base64

                # Detect image format (usually PNG)
                image_data_url = f"data:image/png;base64,{base64.b64encode(image_bytes).decode()}"

                logger.info(f"Imagen generation complete ({len(image_bytes)} bytes)")

                return GeneratedImage(
                    url=image_data_url,
                    visual_hash=visual_hash,
                    width=self.IMAGE_WIDTH,
                    height=self.IMAGE_HEIGHT,
                    generation_method="imagen",
                    cost_usd=self.IMAGEN_COST,
                )
            else:
                raise Exception("No images generated by Imagen")

        except Exception as e:
            logger.error(f"Imagen generation failed: {e}")
            raise

    async def _generate_with_pollinations(
        self,
        prompt: str,
        visual_hash: str,
        max_retries: int = 1,  # Reduced from 5 to fail faster when service is down
    ) -> GeneratedImage:
        """Generate image using Pollinations.ai (FREE service).

        No API key required - completely free service.
        Images are generated on-demand via URL.

        Note: Pollinations can be unreliable (530 errors). This method includes
        automatic retry with different seeds to improve success rate.

        Args:
            prompt: Image generation prompt
            visual_hash: Hash for caching
            max_retries: Maximum retry attempts with different seeds

        Returns:
            GeneratedImage object with image URL

        Raises:
            Exception: If image generation fails after all retries
        """
        import urllib.parse
        import time

        logger.info(f"Using Pollinations.ai (FREE): {prompt[:50]}...")

        for attempt in range(max_retries):
            try:
                # Use random seed for each retry to avoid cache issues
                seed = (hash(prompt) + attempt * 1000 + int(time.time())) % 1000000

                # Build the Pollinations URL with parameters
                encoded_prompt = urllib.parse.quote(prompt)
                params = {
                    "width": self.IMAGE_WIDTH,
                    "height": self.IMAGE_HEIGHT,
                    "seed": str(seed),
                    "model": "flux",
                }

                query_string = "&".join(f"{k}={v}" for k, v in params.items())
                image_url = f"{self.POLLINATIONS_API}/{encoded_prompt}?{query_string}"

                logger.info(f"Pollinations attempt {attempt + 1}/{max_retries}: seed={seed}")

                # Verify the URL works by making a HEAD request
                client = await self._get_http_client()
                response = await client.head(image_url, timeout=30.0)

                if response.status_code == 200:
                    logger.info(f"Pollinations generation verified: {image_url[:80]}...")
                    return GeneratedImage(
                        url=image_url,
                        visual_hash=visual_hash,
                        width=self.IMAGE_WIDTH,
                        height=self.IMAGE_HEIGHT,
                        generation_method="pollinations",
                        cost_usd=self.POLLINATIONS_COST,  # Free!
                    )
                elif response.status_code >= 500:
                    # Server error, retry with backoff
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt  # 1s, 2s, 4s, 8s, 16s
                        logger.warning(f"Pollinations returned {response.status_code}, retrying in {wait_time}s...")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        raise Exception(f"Pollinations failed after {max_retries} attempts")
                else:
                    raise Exception(f"Pollinations returned unexpected status: {response.status_code}")

            except asyncio.TimeoutError:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(f"Pollinations timeout, retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise Exception("Pollinations timed out after all retries")
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(f"Pollinations attempt {attempt + 1} failed: {e}, retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    logger.error(f"Pollinations generation failed after {max_retries} attempts: {e}")
                    raise

    async def _generate_with_fallback(
        self,
        prompt: str,
        visual_hash: str,
    ) -> GeneratedImage:
        """Generate a fallback image directly.

        External free services (LoremFlickr, Picsum, Unsplash) are unreliable.
        Skip them entirely and go straight to gradient fallback for speed.

        Args:
            prompt: Image generation prompt (used for colors and text)
            visual_hash: Hash for caching

        Returns:
            GeneratedImage object with image URL
        """
        logger.info("Using fallback: Generating context-aware gradient image...")
        return await self._generate_gradient_image(prompt, visual_hash)

    async def _fetch_from_unsplash(
        self,
        prompt: str,
        visual_hash: str,
    ) -> GeneratedImage:
        """Fetch relevant image from multiple free image APIs.

        Tries multiple services in order:
        1. LoremFlickr (reliable, keyword-based images)
        2. Picsum Photos (random quality images)
        3. Unsplash (if available)

        Args:
            prompt: Used to extract search keywords
            visual_hash: Hash for caching

        Returns:
            GeneratedImage with image URL
        """
        import urllib.parse
        import random

        # Extract keywords from prompt
        keywords = self._extract_keywords(prompt)
        encoded_keywords = urllib.parse.quote(keywords.replace(",", " "))

        client = await self._get_http_client()

        # Try different image services in order of reliability
        services = []

        # 1. LoremFlickr with extracted keywords
        services.append(("LoremFlickr", f"https://loremflickr.com/{self.IMAGE_WIDTH}/{self.IMAGE_HEIGHT}/{encoded_keywords}?lock={random.randint(1, 100)}"))

        # 2. LoremFlickr with tech/AI fallback keywords
        services.append(("LoremFlickr (tech)", f"https://loremflickr.com/{self.IMAGE_WIDTH}/{self.IMAGE_HEIGHT}/technology,ai?lock={random.randint(1, 100)}"))

        # 3. Picsum Photos (random quality images)
        services.append(("Picsum", f"https://picsum.photos/{self.IMAGE_WIDTH}/{self.IMAGE_HEIGHT}?random={random.randint(1, 1000)}"))

        # 4. Unsplash (as last resort)
        services.append(("Unsplash", f"https://source.unsplash.com/{self.IMAGE_WIDTH}x{self.IMAGE_HEIGHT}/?{urllib.parse.quote(keywords)}"))

        for service_name, img_url in services:
            try:
                logger.info(f"Trying {service_name}: {img_url[:80]}...")
                response = await client.head(img_url, timeout=30.0)

                if response.status_code == 200:
                    logger.info(f"{service_name} successful!")
                    method_name = "loremflickr" if "loremflickr" in img_url else ("picsum" if "picsum" in img_url else "unsplash")
                    return GeneratedImage(
                        url=img_url,
                        visual_hash=visual_hash,
                        width=self.IMAGE_WIDTH,
                        height=self.IMAGE_HEIGHT,
                        generation_method=method_name,
                        cost_usd=0.0,
                    )
                else:
                    logger.warning(f"{service_name} returned {response.status_code}")
            except Exception as e:
                logger.warning(f"{service_name} failed: {e}")
                continue

        # All services failed
        raise Exception("All free image services unavailable")

    def _extract_keywords(self, prompt: str) -> str:
        """Extract relevant keywords from prompt for image search.

        Args:
            prompt: Full prompt text

        Returns:
            Comma-separated keywords
        """
        # Common tech/AI keywords to prioritize
        priority_keywords = [
            "artificial intelligence", "AI", "machine learning", "neural network",
            "robot", "automation", "code", "programming", "technology",
            "digital", "futuristic", "innovation", "data", "cloud computing",
            "software", "algorithm", "brain", "network"
        ]

        # Find which priority keywords are in the prompt
        found_keywords = []
        prompt_lower = prompt.lower()
        for keyword in priority_keywords:
            if keyword.lower() in prompt_lower:
                found_keywords.append(keyword)

        # If we found relevant keywords, use them
        if found_keywords:
            return ",".join(found_keywords[:3])  # Use top 3

        # Otherwise, use simple keyword extraction (remove common words)
        words = prompt.split()
        # Filter out common adjectives and articles
        stop_words = {"a", "an", "the", "with", "and", "or", "but", "in", "on", "at", "to", "for", "of", "is", "are"}
        keywords = [w for w in words if w.lower() not in stop_words and len(w) > 3]
        return ",".join(keywords[:5]) if keywords else "technology"

    async def _generate_gradient_image(
        self,
        prompt: str,
        visual_hash: str,
    ) -> GeneratedImage:
        """Generate a context-aware gradient image with text overlay.

        Creates visually appealing images with:
- Context-aware colors based on prompt keywords
- Relevant text extracted from prompt
- Decorative elements and professional styling

        Args:
            prompt: Used for colors and text overlay
            visual_hash: Hash for caching

        Returns:
            GeneratedImage with base64 data URL
        """
        logger.warning("Using gradient fallback (context-aware image)")

        try:
            import asyncio
            from PIL import Image, ImageDraw, ImageFont
            import base64
            import random

            img = Image.new("RGB", (self.IMAGE_WIDTH, self.IMAGE_HEIGHT))
            draw = ImageDraw.Draw(img)

            # Determine color scheme based on prompt
            prompt_lower = prompt.lower()
            if any(word in prompt_lower for word in ["error", "warning", "fail", "bug", "issue"]):
                # Red/orange gradient for errors
                color_top = (80, 30, 30)
                color_bottom = (40, 15, 15)
                accent_color = (255, 100, 100)
                title_text = "AI Agent Factory"
                subtitle = "Debugging in Progress"
            elif any(word in prompt_lower for word in ["code", "programming", "script", "function"]):
                # Blue/cyan gradient for code
                color_top = (30, 60, 80)
                color_bottom = (15, 30, 40)
                accent_color = (100, 200, 255)
                title_text = "AI Agent Factory"
                subtitle = "Code Generation"
            elif any(word in prompt_lower for word in ["data", "database", "storage", "cloud"]):
                # Green/teal gradient for data
                color_top = (30, 80, 60)
                color_bottom = (15, 40, 30)
                accent_color = (100, 255, 200)
                title_text = "AI Agent Factory"
                subtitle = "Data Management"
            else:
                # Default purple/blue gradient
                color_top = (50, 30, 80)
                color_bottom = (20, 15, 40)
                accent_color = (200, 150, 255)
                title_text = "AI Agent Factory"
                subtitle = "Automated Generation"

            # Create vertical gradient
            for y in range(self.IMAGE_HEIGHT):
                ratio = y / self.IMAGE_HEIGHT
                r = int(color_top[0] + (color_bottom[0] - color_top[0]) * ratio)
                g = int(color_top[1] + (color_bottom[1] - color_top[1]) * ratio)
                b = int(color_top[2] + (color_bottom[2] - color_top[2]) * ratio)
                for x in range(self.IMAGE_WIDTH):
                    img.putpixel((x, y), (r, g, b))

            # Add decorative pattern (diagonal stripes)
            for i in range(-self.IMAGE_HEIGHT, self.IMAGE_WIDTH, 40):
                for y in range(self.IMAGE_HEIGHT):
                    x = i + y
                    if 0 <= x < self.IMAGE_WIDTH:
                        r, g, b = img.getpixel((x, y))
                        # Make stripes slightly lighter
                        img.putpixel((x, y), (min(255, r + 20), min(255, g + 20), min(255, b + 20)))

            # Add text overlay
            try:
                font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 70)
                font_subtitle = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 35)
            except Exception:
                font_title = ImageFont.load_default()
                font_subtitle = ImageFont.load_default()

            # Draw title text
            title_bbox = draw.textbbox((0, 0), title_text, font=font_title)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = (self.IMAGE_WIDTH - title_width) // 2
            title_y = self.IMAGE_HEIGHT // 2 - 80
            draw.text((title_x, title_y), title_text, fill=(255, 255, 255), font=font_title)

            # Draw subtitle text
            subtitle_bbox = draw.textbbox((0, 0), subtitle, font=font_subtitle)
            subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
            subtitle_x = (self.IMAGE_WIDTH - subtitle_width) // 2
            subtitle_y = self.IMAGE_HEIGHT // 2
            draw.text((subtitle_x, subtitle_y), subtitle, fill=accent_color, font=font_subtitle)

            # Add decorative border
            border_width = 25
            from PIL import ImageOps
            img_with_border = ImageOps.expand(img, border=border_width, fill=accent_color)

            # Convert to bytes
            import io
            buffer = io.BytesIO()
            img_with_border.save(buffer, format="PNG")
            image_bytes = buffer.getvalue()

            # Create base64 data URL
            image_data_url = f"data:image/png;base64,{base64.b64encode(image_bytes).decode()}"

            logger.info(f"Context-aware gradient image generated: {len(image_bytes)} bytes")

            return GeneratedImage(
                url=image_data_url,
                visual_hash=visual_hash,
                width=self.IMAGE_WIDTH,
                height=self.IMAGE_HEIGHT,
                generation_method="fallback-gradient",
                cost_usd=0.0,
            )

        except Exception as e:
            logger.error(f"Gradient fallback failed: {e}")
            # Ultimate fallback - solid color image
            import io
            import base64
            from PIL import Image

            img = Image.new("RGB", (self.IMAGE_WIDTH, self.IMAGE_HEIGHT), (50, 30, 80))
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            image_bytes = buffer.getvalue()
            image_data_url = f"data:image/png;base64,{base64.b64encode(image_bytes).decode()}"

            return GeneratedImage(
                url=image_data_url,
                visual_hash=visual_hash,
                width=self.IMAGE_WIDTH,
                height=self.IMAGE_HEIGHT,
                generation_method="fallback-solid",
                cost_usd=0.0,
            )

            # Draw title text
            title_text = "AI Agent Factory"
            bbox = draw.textbbox((0, 0), title_text, font=font_large)
            text_width = bbox[2] - bbox[0]
            text_x = (self.IMAGE_WIDTH - text_width) // 2
            text_y = self.IMAGE_HEIGHT // 2 - 100
            draw.text((text_x, text_y), title_text, fill=(255, 255, 255), font=font_large)

            # Draw subtitle
            subtitle_text = "Lesson Short"
            bbox = draw.textbbox((0, 0), subtitle_text, font=font_small)
            text_width = bbox[2] - bbox[0]
            text_x = (self.IMAGE_WIDTH - text_width) // 2
            text_y = self.IMAGE_HEIGHT // 2
            draw.text((text_x, text_y), subtitle_text, fill=(200, 200, 255), font=font_small)

            # Add decorative border
            from PIL import ImageOps
            border_width = 20
            img_with_border = ImageOps.expand(img, border=border_width, fill=(100, 50, 150))

            # Convert to bytes
            import io
            buffer = io.BytesIO()
            img_with_border.save(buffer, format="PNG")
            image_bytes = buffer.getvalue()

            # Create base64 data URL
            image_data_url = f"data:image/png;base64,{base64.b64encode(image_bytes).decode()}"

            logger.info(f"Fallback image generated: {len(image_bytes)} bytes")

            return GeneratedImage(
                url=image_data_url,
                visual_hash=visual_hash,
                width=self.IMAGE_WIDTH,
                height=self.IMAGE_HEIGHT,
                generation_method="fallback",
                cost_usd=0.0,
            )

        except Exception as e:
            logger.error(f"Fallback image generation failed: {e}")
            # Even fallback failed - return a minimal solid color image
            import io
            import base64
            from PIL import Image

            img = Image.new("RGB", (self.IMAGE_WIDTH, self.IMAGE_HEIGHT), (50, 30, 80))
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            image_bytes = buffer.getvalue()
            image_data_url = f"data:image/png;base64,{base64.b64encode(image_bytes).decode()}"

            return GeneratedImage(
                url=image_data_url,
                visual_hash=visual_hash,
                width=self.IMAGE_WIDTH,
                height=self.IMAGE_HEIGHT,
                generation_method="fallback",
                cost_usd=0.0,
            )

    async def generate_scene_image(
        self,
        visual_description: str,
        style: str = "tech, modern, AI aesthetic",
    ) -> GeneratedImage:
        """Generate a scene image using the configured provider.

        Provider is set via IMAGE_PROVIDER environment variable:
        - imagen: Google Imagen API (uses GEMINI_API_KEY)
        - replicate: Replicate Flux Schnell (uses REPLICATE_API_KEY)
        - pollinations: Free Pollinations.ai (no API key needed)

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

        # Prepare prompt
        prompt = f"{visual_description}, {style}, cinematic, high quality, detailed"

        # Get the configured provider
        provider = getattr(settings, 'image_provider', 'pollinations').lower()

        # Route to the appropriate provider with automatic fallback
        try:
            if provider == "imagen":
                image = await self._generate_with_imagen(prompt, visual_hash)
            elif provider == "replicate":
                image = await self._generate_with_replicate(prompt, visual_hash)
            elif provider == "pollinations":
                image = await self._generate_with_pollinations(prompt, visual_hash)
            else:
                logger.warning(f"Unknown provider '{provider}', falling back to pollinations")
                image = await self._generate_with_pollinations(prompt, visual_hash)
        except Exception as e:
            # Automatic fallback chain
            error_msg = str(e)
            logger.warning(f"{provider.capitalize()} failed: {error_msg}")

            # Try other providers in order
            if provider != "pollinations":
                logger.info("Falling back to Pollinations...")
                try:
                    image = await self._generate_with_pollinations(prompt, visual_hash)
                except Exception as e2:
                    logger.warning(f"Pollinations also failed: {e2}")
                    image = await self._generate_with_fallback(prompt, visual_hash)
            else:
                # Primary was pollinations and it failed, go to fallback
                logger.info("All external services failed, using fallback image generation...")
                image = await self._generate_with_fallback(prompt, visual_hash)

        # Cache the result
        await self._cache_image(visual_hash, image)

        return image

    async def generate_code_screenshot(
        self,
        code: str,
        language: str = "python",
    ) -> GeneratedImage:
        """Generate a syntax-highlighted code screenshot via carbon.now.sh.
        Falls back to Replicate if Carbon fails.

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
            try:
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
                    # Fall back to generating a regular scene image with code description
                    logger.warning("Falling back to scene image generation for code")
                    return await self.generate_scene_image(
                        f"Code snippet in {language}: {code[:100]}... Syntax highlighted code with dark theme and monokai colors"
                    )
            except Exception as api_error:
                logger.warning(f"Carbon API call failed: {api_error}, falling back to scene image")
                return await self.generate_scene_image(
                    f"Code snippet in {language}: {code[:100]}... Syntax highlighted code with dark theme and monokai colors"
                )

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
