"""Video Assembly Service using FFmpeg.

This service composes the final video from:
- Scene images
- Audio narration
- Captions/text overlays
- Transitions between scenes

Video Spec:
- Format: MP4 (H.264 codec)
- Resolution: 1080x1920 (9:16 vertical)
- Frame rate: 30fps
- Max file size: 50MB
"""

import asyncio
import logging
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

import httpx

from shorts_generator.services.audio_generator import GeneratedAudio
from shorts_generator.services.script_generator import GeneratedScript
from shorts_generator.services.storage import storage_service

logger = logging.getLogger(__name__)

# Video specifications
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920  # 9:16 aspect ratio
VIDEO_FPS = 30
VIDEO_CODEC = "libx264"
VIDEO_BITRATE = "2M"  # 2 Mbps for good quality
AUDIO_CODEC = "aac"
AUDIO_BITRATE = "128k"
MAX_FILE_SIZE_MB = 50


@dataclass
class AssembledVideo:
    """Represents an assembled video.

    Attributes:
        file_path: Path to the video file
        url: CDN URL for the video
        duration_seconds: Video duration in seconds
        file_size_mb: File size in MB
        width: Video width in pixels
        height: Video height in pixels
        thumbnail_url: URL to the thumbnail image
    """

    file_path: str
    url: str
    duration_seconds: float
    file_size_mb: float
    width: int
    height: int
    thumbnail_url: str


class VideoAssembler:
    """Assembles videos from scenes, audio, and captions using FFmpeg."""

    def __init__(self):
        """Initialize the video assembler."""
        self._http_client: httpx.AsyncClient | None = None

    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=60.0)
        return self._http_client

    async def _download_image_with_retry(self, image_url: str, max_retries: int = 3) -> str:
        """Download an image to a temp file with retry logic.

        Args:
            image_url: URL of the image to download
            max_retries: Maximum number of retry attempts

        Returns:
            Local file path to the downloaded image

        Raises:
            Exception: If download fails after all retries
        """
        client = await self._get_http_client()

        for attempt in range(max_retries):
            try:
                response = await client.get(image_url, timeout=60.0)
                response.raise_for_status()

                # Save to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
                    tmp_file.write(response.content)
                    tmp_file.flush()
                    return tmp_file.name

            except httpx.HTTPStatusError as e:
                if 500 <= e.response.status_code < 600:
                    # Retry on server errors with exponential backoff
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt  # 1s, 2s, 4s
                        logger.warning(
                            f"Image download failed with {e.response.status_code}, "
                            f"retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})"
                        )
                        await asyncio.sleep(wait_time)
                        continue
                raise
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(f"Image download failed: {e}, retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
                raise

        raise Exception(f"Failed to download image after {max_retries} attempts")

    def _estimate_bitrate(self, duration_seconds: float, max_size_mb: int = MAX_FILE_SIZE_MB) -> str:
        """Estimate video bitrate to fit within file size limit.

        Args:
            duration_seconds: Target video duration
            max_size_mb: Maximum file size in MB

        Returns:
            Bitrate string for FFmpeg (e.g., "2M")
        """
        # Formula: bitrate = (file_size * 8) / duration
        # We use 90% of target size to leave room for overhead
        target_bits = (max_size_mb * 1024 * 1024 * 0.9 * 8) / duration_seconds

        # Convert to bits per second, then to kbps/Mbps
        if target_bits > 1_000_000:
            return f"{int(target_bits / 1_000_000)}M"
        elif target_bits > 1000:
            return f"{int(target_bits / 1000)}k"
        else:
            return f"{int(target_bits)}"

    async def assemble_video(
        self,
        scene_images: list[str],
        audio: GeneratedAudio,
        script: GeneratedScript,
        captions: str,
        transition: str = "fade",
    ) -> AssembledVideo:
        """Assemble video from scenes, audio, and captions.

        Args:
            scene_images: List of image URLs (one per scene)
            audio: GeneratedAudio with narration
            script: GeneratedScript with timing info
            captions: SRT format captions
            transition: Transition type between scenes

        Returns:
            AssembledVideo object with video metadata

        Raises:
            Exception: If video assembly fails
        """
        logger.info(f"Assembling video from {len(scene_images)} scenes")

        try:
            # Create output file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
                output_path = tmp_file.name

                # Calculate total duration
                total_duration = script.total_duration

                # Calculate appropriate bitrate
                bitrate = self._estimate_bitrate(total_duration)

                # Prepare input files
                audio_path = audio.file_path
                if audio_path.startswith("file://"):
                    audio_path = audio_path.replace("file://", "")

                # Build filter complex for combining images
                # For simplicity, we'll use the first image for the entire video duration
                # In production, you'd want to overlay different images at different times

                # Clean up image URLs
                clean_images = []
                for img_url in scene_images[:1]:  # Use first image for now
                    if img_url.startswith("file://"):
                        clean_images.append(img_url.replace("file://", ""))
                    elif img_url.startswith("data:"):
                        # Save data URL to temp file
                        import base64
                        header, data = img_url.split(",", 1)
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as img_tmp:
                            img_tmp.write(base64.b64decode(data))
                            img_tmp.flush()
                            clean_images.append(img_tmp.name)
                    elif img_url.startswith("http://") or img_url.startswith("https://"):
                        # Download remote image with retry logic
                        logger.info(f"Downloading remote image: {img_url[:80]}...")
                        local_path = await self._download_image_with_retry(img_url)
                        clean_images.append(local_path)
                    else:
                        clean_images.append(img_url)

                if not clean_images:
                    raise Exception("No valid images found for video generation")

                # Use subprocess to run ffmpeg directly (more reliable than ffmpeg-python)
                import subprocess

                # Build ffmpeg command
                # Create slideshow from images with audio
                cmd = [
                    "ffmpeg",
                    "-y",  # Overwrite output file
                    "-loop", "1",  # Loop images
                    "-i", clean_images[0],  # Input image
                    "-i", audio_path,  # Input audio
                    "-c:v", "libx264",  # Video codec
                    "-tune", "stillimage",  # Optimize for still images
                    "-pix_fmt", "yuv420p",  # Better compatibility
                    "-vf", f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}",  # Scale resolution
                    "-t", str(total_duration),  # Duration
                    "-c:a", "aac",  # Audio codec
                    "-b:a", "128k",  # Audio bitrate
                    "-shortest",  # End when shortest input ends
                    "-movflags", "+faststart",  # Enable web playback
                    output_path,
                ]

                logger.info(f"Running ffmpeg: {' '.join(cmd[:5])}...")

                # Run ffmpeg
                result = await asyncio.to_thread(
                    subprocess.run,
                    cmd,
                    capture_output=True,
                    text=True,
                )

                if result.returncode != 0:
                    logger.error(f"FFmpeg error: {result.stderr}")
                    raise Exception(f"Video assembly failed: {result.stderr}")

                logger.info(f"Video assembled: {output_path}")

                # Get file size
                file_size_bytes = os.path.getsize(output_path)
                file_size_mb = file_size_bytes / (1024 * 1024)

                # Generate thumbnail from first frame
                thumbnail_path = await self._generate_thumbnail(scene_images[0] if scene_images else "")

                # Upload to R2 storage
                video_id = str(uuid4())  # Generate ID for this video

                # Upload video
                video_upload = await storage_service.upload_video(
                    file_path=output_path,
                    video_id=video_id,
                )

                # Upload thumbnail
                thumbnail_upload = await storage_service.upload_thumbnail(
                    file_path=thumbnail_path.replace("file://", ""),
                    video_id=video_id,
                )

                video = AssembledVideo(
                    file_path=output_path,
                    url=video_upload["cdn_url"],  # R2 CDN URL
                    duration_seconds=total_duration,
                    file_size_mb=file_size_mb,
                    width=VIDEO_WIDTH,
                    height=VIDEO_HEIGHT,
                    thumbnail_url=thumbnail_upload["cdn_url"],  # R2 CDN URL
                )

                logger.info(f"Video assembled: {file_size_mb:.2f}MB, {total_duration}s")

                return video

        except Exception as e:
            logger.error(f"Video assembly failed: {e}")
            raise

    async def _generate_thumbnail(self, first_scene_image_url: str) -> str:
        """Generate a thumbnail from the first scene image.

        Args:
            first_scene_image_url: URL to the first scene image

        Returns:
            Local file path to the generated thumbnail

        Raises:
            Exception: If thumbnail generation fails
        """
        logger.info("Generating thumbnail from first scene")

        try:
            import ffmpeg

            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                output_path = tmp_file.name

                # Get image path
                if first_scene_image_url.startswith("file://"):
                    image_path = first_scene_image_url.replace("file://", "")
                else:
                    # TODO: Download to temp file
                    image_path = first_scene_image_url

                # Extract first frame as thumbnail
                # For static images, we just resize
                (
                    ffmpeg
                    .input(image_path)
                    .output(
                        output_path,
                        vf=f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}",
                        q="2",  # Quality for JPEG
                    )
                    .overwrite_output()
                    .run()
                )

                # Return local path (will be uploaded to R2 later)
                return output_path

        except Exception as e:
            logger.error(f"Thumbnail generation failed: {e}")
            # Fallback: return original image path if it's a local file
            if first_scene_image_url.startswith("file://"):
                return first_scene_image_url.replace("file://", "")
            raise

    def optimize_for_web(
        self,
        video_path: str,
        target_size_mb: int = MAX_FILE_SIZE_MB,
    ) -> str:
        """Optimize video for web delivery.

        Args:
            video_path: Path to the video file
            target_size_mb: Target file size in MB

        Returns:
            Path to optimized video file

        Raises:
            Exception: If optimization fails
        """
        logger.info(f"Optimizing video for web (target: {target_size_mb}MB)")

        try:
            import ffmpeg

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
                output_path = tmp_file.name

                # Probe original video
                probe = ffmpeg.probe(video_path)
                original_duration = float(probe.format["duration"])

                # Calculate new bitrate
                bitrate = self._estimate_bitrate(original_duration, target_size_mb)

                (
                    ffmpeg
                    .input(video_path)
                    .output(
                        output_path,
                        vcodec=VIDEO_CODEC,
                        video_bitrate=bitrate,
                        acodec=AUDIO_CODEC,
                        audio_bitrate=AUDIO_BITRATE,
                        movflags="+faststart",
                        pix_fmt="yuv420p",
                    )
                    .overwrite_output()
                    .run()
                )

                return output_path

        except Exception as e:
            logger.error(f"Video optimization failed: {e}")
            raise

    def _calculate_video_size(self, duration_seconds: float, bitrate_kbps: int) -> float:
        """Estimate video file size.

        Args:
            duration_seconds: Video duration
            bitrate_kbps: Video bitrate in kbps

        Returns:
            Estimated file size in MB
        """
        # Size (bits) = bitrate * duration
        # Add 10% for container overhead
        total_bits = (bitrate_kbps * 1000) * duration_seconds * 1.1
        total_mb = total_bits / (8 * 1024 * 1024)

        return total_mb

    async def assemble_video_from_assets(
        self,
        assets: dict[str, Any],
        script: GeneratedScript,
    ) -> AssembledVideo:
        """Assemble video from pre-generated assets.

        This is a simplified version for testing that takes
        pre-generated images and audio.

        Args:
            assets: Dictionary containing scene_images, audio_path, captions
            script: GeneratedScript

        Returns:
            AssembledVideo object
        """
        scene_images = assets.get("scene_images", [])
        audio_path = assets.get("audio_path")
        captions = assets.get("captions", "")

        # For testing, we'd need to create GeneratedAudio
        from shorts_generator.services.audio_generator import GeneratedAudio as Audio

        if not audio_path:
            # Create dummy audio for testing
            audio = Audio(
                url="file:///dev/null",
                duration_seconds=script.total_duration,
                file_path="/dev/null",
                generation_method="edge_tts",
                voice_used="test",
            )
        else:
            # TODO: Load audio from path
            pass

        return await self.assemble_video(
            scene_images=scene_images,
            audio=audio,
            script=script,
            captions=captions,
        )


# Singleton instance
video_assembler = VideoAssembler()
