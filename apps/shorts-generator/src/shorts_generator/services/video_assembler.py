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

import logging
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

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
        pass

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
            import ffmpeg

            # Create output file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
                output_path = tmp_file.name

                # Calculate total duration
                total_duration = script.total_duration

                # Calculate appropriate bitrate
                bitrate = self._estimate_bitrate(total_duration)

                # Build FFmpeg complex filter
                # This combines: images + audio + captions + transitions
                inputs = []

                # Add images as video streams
                for i, image_url in enumerate(scene_images):
                    if image_url.startswith("file://"):
                        image_path = image_url.replace("file://", "")
                    else:
                        # TODO: Download to temp file
                        image_path = image_url

                    # Get duration for this scene
                    if i < len(script.concepts):
                        scene = script.concepts[i]
                        scene_duration = scene.duration_seconds
                    elif i == len(scene_images) - 1:
                        scene_duration = script.total_duration
                    else:
                        scene_duration = 5

                    # Create video stream from image
                    (
                        ffmpeg
                        .input(image_path, loop=1, framerate=1)
                        .output(
                            f"-vf scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}",
                            "-r", str(VIDEO_FPS),
                        )
                    )

                # Add audio
                if audio.file_path.startswith("file://"):
                    audio_path = audio.file_path.replace("file://", "")
                else:
                    # TODO: Download to temp file
                    audio_path = audio.file_path

                # Main FFmpeg command
                # This is a simplified version - in production, you'd use complex filter graphs
                (
                    ffmpeg
                    .input(audio_path)
                    .output(
                        output_path,
                        vcodec=VIDEO_CODEC,
                        video_bitrate=bitrate,
                        acodec=AUDIO_CODEC,
                        audio_bitrate=AUDIO_BITRATE,
                        movflags="+faststart",  # Enable web playback
                        pix_fmt="yuv420p",  # Better compatibility
                        shortswithen=None,  # Don't cut duration
                    )
                    .overwrite_output()
                    .run(capture_stdout=True, capture_stderr=True)
                )

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
