"""Video Composition Service using FFmpeg.

This service combines video frames and audio into final MP4 videos:
- Combines frame sequences with audio tracks
- Supports multiple video codecs (H.264, H.265)
- Configurable quality settings
- Progress tracking for long renders
- Thumbnail generation
- Duration verification
"""

import asyncio
import json
import logging
import os
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from shorts_generator.services.frame_generator import FrameGenerationResult
from shorts_generator.services.google_tts_audio import GoogleTTSResult

logger = logging.getLogger(__name__)


class VideoCodec(str, Enum):
    """Supported video codecs."""

    H264 = "libx264"  # Most compatible, good quality
    H265 = "libx265"  # Better compression, slower
    VP9 = "libvpx-vp9"  # Open source alternative


class VideoPreset(str, Enum):
    """FFmpeg encoding presets.

    Faster presets = faster encoding but larger files.
    Slower presets = better compression but slower encoding.
    """

    ULTRAFAST = "ultrafast"
    SUPERFAST = "superfast"
    VERYFAST = "veryfast"
    FASTER = "faster"
    FAST = "fast"
    MEDIUM = "medium"  # Default
    SLOW = "slow"
    SLOWER = "slower"
    VERYSLOW = "veryslow"


class VideoQuality(str, Enum):
    """Quality presets for CRF (Constant Rate Factor).

    Lower values = better quality, larger files.
    Higher values = lower quality, smaller files.

    Recommended ranges:
    - H.264: 18-28 (default: 23)
    - H.265: 20-30 (default: 26)
    """

    HIGH = "18"  # Best quality
    GOOD = "20"  # Good quality
    MEDIUM = "23"  # Default
    LOW = "26"  # Lower quality
    MINIMAL = "28"  # Minimal quality


@dataclass
class VideoCompositionConfig:
    """Configuration for video composition.

    Attributes:
        codec: Video codec to use
        preset: Encoding speed preset
        crf: Quality (Constant Rate Factor)
        pixel_format: Pixel format (yuv420p for compatibility)
        audio_bitrate: Audio bitrate in bits
        audio_codec: Audio codec
    """

    codec: VideoCodec = VideoCodec.H264
    preset: VideoPreset = VideoPreset.MEDIUM
    crf: VideoQuality = VideoQuality.MEDIUM
    pixel_format: str = "yuv420p"
    audio_bitrate: str = "128k"
    audio_codec: str = "aac"

    @classmethod
    def from_settings(cls) -> "VideoCompositionConfig":
        """Create config from application settings."""
        return cls()

    def get_ffmpeg_params(self) -> list[str]:
        """Get FFmpeg parameters for this config.

        Returns:
            List of FFmpeg command line arguments
        """
        return [
            "-c:v",
            self.codec.value,
            "-preset",
            self.preset.value,
            "-crf",
            self.crf.value,
            "-pix_fmt",
            self.pixel_format,
            "-c:a",
            self.audio_codec,
            "-b:a",
            self.audio_bitrate,
        ]


@dataclass
class VideoCompositionResult:
    """Result of video composition.

    Attributes:
        video_path: Path to generated video file
        duration_seconds: Video duration in seconds
        file_size_mb: File size in megabytes
        width: Video width
        height: Video height
        fps: Frames per second
        audio_synced: Whether audio was successfully synced
        thumbnail_path: Path to generated thumbnail (if any)
    """

    video_path: str
    duration_seconds: float
    file_size_mb: float
    width: int
    height: int
    fps: int
    audio_synced: bool = True
    thumbnail_path: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "video_path": self.video_path,
            "duration_seconds": self.duration_seconds,
            "file_size_mb": self.file_size_mb,
            "width": self.width,
            "height": self.height,
            "fps": self.fps,
            "audio_synced": self.audio_synced,
            "thumbnail_path": self.thumbnail_path,
            "metadata": self.metadata,
        }


class VideoComposer:
    """Composes videos from frames and audio using FFmpeg.

    Features:
    - Frame sequence + audio composition
    - Multiple codec support
    - Quality configuration
    - Thumbnail generation
    - Duration verification
    - Progress tracking
    """

    def __init__(self, config: VideoCompositionConfig | None = None):
        """Initialize the video composer.

        Args:
            config: Composition configuration (default: from settings)
        """
        self.config = config or VideoCompositionConfig.from_settings()

    async def _check_ffmpeg_available(self) -> bool:
        """Check if FFmpeg is available.

        Returns:
            True if FFmpeg is installed and accessible
        """
        try:
            result = await asyncio.to_thread(
                subprocess.run,
                ["ffmpeg", "-version"],
                capture_output=True,
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

    async def _get_video_duration(self, video_path: str) -> float:
        """Get duration of video file using ffprobe.

        Args:
            video_path: Path to video file

        Returns:
            Duration in seconds
        """
        try:
            result = await asyncio.to_thread(
                subprocess.run,
                [
                    "ffprobe",
                    "-v",
                    "error",
                    "-show_entries",
                    "format=duration",
                    "-of",
                    "default=noprint_wrappers=1:nokey=1",
                    video_path,
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0 and result.stdout.strip():
                return float(result.stdout.strip())

        except Exception as e:
            logger.warning(f"Could not get video duration: {e}")

        return 0.0

    async def _get_video_info(self, video_path: str) -> dict[str, Any]:
        """Get detailed video information using ffprobe.

        Args:
            video_path: Path to video file

        Returns:
            Dictionary with video information
        """
        try:
            result = await asyncio.to_thread(
                subprocess.run,
                [
                    "ffprobe",
                    "-v",
                    "error",
                    "-select_streams",
                    "v:0",
                    "-show_entries",
                    "stream=width,height,r_frame_rate",
                    "-show_entries",
                    "format=duration",
                    "-of",
                    "json",
                    video_path,
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                data = json.loads(result.stdout)
                info: dict[str, Any] = {}

                # Extract video stream info
                if "streams" in data and data["streams"]:
                    stream = data["streams"][0]
                    info["width"] = stream.get("width")
                    info["height"] = stream.get("height")
                    # Parse FPS from "num/den" format
                    fps_str = stream.get("r_frame_rate", "30/1")
                    if "/" in fps_str:
                        num, den = fps_str.split("/")
                        info["fps"] = float(num) / float(den)
                    else:
                        info["fps"] = float(fps_str)

                # Extract duration
                if "format" in data:
                    info["duration"] = float(data["format"].get("duration", 0))

                return info

        except Exception as e:
            logger.warning(f"Could not get video info: {e}")

        return {}

    def _build_ffmpeg_command(
        self,
        frames_dir: str,
        audio_path: str,
        output_path: str,
        fps: int = 30,
    ) -> list[str]:
        """Build FFmpeg command for video composition.

        Args:
            frames_dir: Directory containing frame_00000.png, frame_00001.png, etc.
            audio_path: Path to audio file
            output_path: Path for output video
            fps: Frames per second

        Returns:
            FFmpeg command as list of strings
        """
        # Build frame input pattern
        frame_pattern = os.path.join(frames_dir, "frame_%05d.png")

        # Base command
        cmd = [
            "ffmpeg",
            "-y",  # Overwrite output file
            "-framerate",
            str(fps),
            "-i",
            frame_pattern,
            "-i",
            audio_path,
        ]

        # Add codec/config parameters
        cmd.extend(self.config.get_ffmpeg_params())

        # Use shortest stream duration
        cmd.extend(["-shortest"])

        # Output file
        cmd.append(output_path)

        return cmd

    async def compose(
        self,
        frames_dir: str,
        audio_path: str,
        output_path: str,
        fps: int = 30,
        progress_callback: callable[[float], None] | None = None,
    ) -> VideoCompositionResult:
        """Compose video from frames and audio.

        Args:
            frames_dir: Directory containing frame images (frame_00000.png, etc.)
            audio_path: Path to audio file
            output_path: Path for output video file
            fps: Frames per second
            progress_callback: Optional callback for progress updates (0.0 to 1.0)

        Returns:
            VideoCompositionResult with output information

        Raises:
            RuntimeError: If FFmpeg is not available
            subprocess.CalledProcessError: If FFmpeg fails
        """
        logger.info("Starting video composition")
        logger.info(f"  Frames: {frames_dir}")
        logger.info(f"  Audio: {audio_path}")
        logger.info(f"  Output: {output_path}")

        # Check FFmpeg availability
        if not await self._check_ffmpeg_available():
            raise RuntimeError(
                "FFmpeg is not installed or not accessible. "
                "Install with: apt-get install ffmpeg"
            )

        # Build command
        cmd = self._build_ffmpeg_command(frames_dir, audio_path, output_path, fps)

        logger.info(f"Running: {' '.join(cmd)}")

        # Create output directory if needed
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

        # Run FFmpeg
        try:
            if progress_callback:
                # Run with progress tracking
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stderr=asyncio.subprocess.PIPE,
                )

                # Parse progress from stderr
                duration = None
                while True:
                    line = await process.stderr.readline()
                    if not line:
                        break

                    line_str = line.decode("utf-8", errors="ignore")

                    # Parse duration from FFmpeg output
                    if "Duration:" in line_str and duration is None:
                        # Use regex to extract duration more reliably
                        import re
                        dur_match = re.search(r'Duration:\s+(\d+):(\d+):([\d.]+)', line_str)
                        if dur_match:
                            h, m, s = dur_match.groups()
                            duration = int(h) * 3600 + int(m) * 60 + float(s)
                            logger.debug(f"Parsed duration: {duration}s from {h}:{m}:{s}")
                        else:
                            # Try shorter format: MM:SS
                            dur_match = re.search(r'Duration:\s+(\d+):([\d.]+)', line_str)
                            if dur_match:
                                m, s = dur_match.groups()
                                duration = int(m) * 60 + float(s)
                                logger.debug(f"Parsed duration: {duration}s from {m}:{s}")
                            else:
                                logger.warning(f"Could not parse duration from: {line_str[:100]}")

                    # Parse time and report progress
                    if "time=" in line_str:
                        time_match = re.search(r'time=(\d+):(\d+):([\d.]+)', line_str)
                        if not time_match:
                            time_match = re.search(r'time=(\d+):([\d.]+)', line_str)

                        if time_match:
                            try:
                                parts = time_match.groups()
                                if len(parts) == 3:
                                    h, m, s = parts
                                    current_time = int(h) * 3600 + int(m) * 60 + float(s)
                                else:
                                    m, s = parts
                                    current_time = int(m) * 60 + float(s)

                                if duration and duration > 0:
                                    progress = current_time / duration
                                    progress_callback(min(progress, 1.0))
                            except (ValueError, IndexError):
                                pass

                returncode = await process.wait()

            else:
                # Run without progress tracking
                result = await asyncio.to_thread(
                    subprocess.run,
                    cmd,
                    capture_output=True,
                    text=True,
                )
                returncode = result.returncode

            if returncode != 0:
                error_msg = result.stderr if progress_callback else result.stderr
                raise RuntimeError(f"FFmpeg failed with code {returncode}: {error_msg}")

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"FFmpeg failed: {e.stderr}") from e

        # Get video information
        logger.info("Getting video information...")
        video_info = await self._get_video_info(output_path)

        # Get file size
        file_size_bytes = os.path.getsize(output_path)
        file_size_mb = file_size_bytes / (1024 * 1024)

        # Build result
        result = VideoCompositionResult(
            video_path=output_path,
            duration_seconds=video_info.get("duration", 0),
            file_size_mb=file_size_mb,
            width=video_info.get("width", 0),
            height=video_info.get("height", 0),
            fps=video_info.get("fps", fps),
            audio_synced=True,  # TODO: Verify audio sync
            metadata={
                "codec": self.config.codec.value,
                "preset": self.config.preset.value,
                "crf": self.config.crf.value,
            },
        )

        logger.info(
            f"✅ Video composed: {output_path} "
            f"({result.duration_seconds:.2f}s, {file_size_mb:.2f}MB)"
        )

        return result

    async def compose_from_results(
        self,
        frame_result: FrameGenerationResult,
        audio_result: GoogleTTSResult,
        output_path: str,
        progress_callback: callable[[float], None] | None = None,
    ) -> VideoCompositionResult:
        """Compose video from FrameGenerationResult and GoogleTTSResult.

        Convenience method that combines Phase 1 (audio) and Phase 2 (frames) results.

        Args:
            frame_result: Result from frame generation
            audio_result: Result from TTS generation
            output_path: Path for output video
            progress_callback: Optional progress callback

        Returns:
            VideoCompositionResult
        """
        # Extract FPS from frame spec or use default 30
        fps = getattr(frame_result.frame_paths[0].split("/")[-1].split(".")[-2], 30) if frame_result.frame_paths else 30  # noqa: E501

        return await self.compose(
            frames_dir=frame_result.output_dir,
            audio_path=audio_result.audio_path,
            output_path=output_path,
            fps=fps,
            progress_callback=progress_callback,
        )

    async def generate_thumbnail(
        self,
        video_path: str,
        output_path: str | None = None,
        timestamp: float = 1.0,
        width: int = 320,
    ) -> str:
        """Generate thumbnail from video.

        Args:
            video_path: Path to source video
            output_path: Path for thumbnail (default: video_path with .jpg extension)
            timestamp: Timestamp to capture thumbnail from (seconds)
            width: Thumbnail width (height calculated automatically)

        Returns:
            Path to generated thumbnail
        """
        if output_path is None:
            output_path = str(Path(video_path).with_suffix(".jpg"))

        cmd = [
            "ffmpeg",
            "-y",
            "-ss",
            str(timestamp),
            "-i",
            video_path,
            "-vframes",
            "1",
            "-vf",
            f"scale={width}:-1",
            output_path,
        ]

        result = await asyncio.to_thread(
            subprocess.run,
            cmd,
            capture_output=True,
        )

        if result.returncode != 0:
            raise RuntimeError(f"Thumbnail generation failed: {result.stderr.decode()}")

        logger.info(f"✅ Thumbnail generated: {output_path}")
        return output_path

    async def verify_video(
        self,
        video_path: str,
        expected_duration: float | None = None,
        tolerance: float = 0.5,
    ) -> dict[str, Any]:
        """Verify video output meets expectations.

        Args:
            video_path: Path to video file
            expected_duration: Expected duration in seconds
            tolerance: Allowed duration difference in seconds

        Returns:
            Verification results dictionary
        """
        results: dict[str, Any] = {
            "exists": os.path.exists(video_path),
            "readable": False,
            "duration_match": False,
            "has_video": False,
            "has_audio": False,
        }

        if not results["exists"]:
            return results

        try:
            # Get video info
            info = await self._get_video_info(video_path)

            results["readable"] = bool(info)
            results["width"] = info.get("width", 0)
            results["height"] = info.get("height", 0)
            results["fps"] = info.get("fps", 0)
            results["duration"] = info.get("duration", 0)

            results["has_video"] = info.get("width", 0) > 0

            # Check duration match
            if expected_duration is not None:
                actual_duration = info.get("duration", 0)
                duration_diff = abs(actual_duration - expected_duration)
                results["duration_match"] = duration_diff <= tolerance
                results["duration_difference"] = duration_diff

        except Exception as e:
            logger.warning(f"Video verification failed: {e}")
            results["error"] = str(e)

        return results

    async def create_preview(
        self,
        video_path: str,
        output_path: str | None = None,
        duration: float = 5.0,
        start_time: float = 0.0,
    ) -> str:
        """Create a short preview clip from video.

        Args:
            video_path: Path to source video
            output_path: Path for preview video
            duration: Preview duration in seconds
            start_time: Start time for preview

        Returns:
            Path to preview video
        """
        if output_path is None:
            base = Path(video_path).stem
            output_path = str(Path(video_path).parent / f"{base}_preview.mp4")

        cmd = [
            "ffmpeg",
            "-y",
            "-ss",
            str(start_time),
            "-i",
            video_path,
            "-t",
            str(duration),
            "-c",
            "copy",
            output_path,
        ]

        result = await asyncio.to_thread(
            subprocess.run,
            cmd,
            capture_output=True,
        )

        if result.returncode != 0:
            raise RuntimeError(f"Preview creation failed: {result.stderr.decode()}")

        logger.info(f"✅ Preview created: {output_path}")
        return output_path


# Singleton instance
video_composer = VideoComposer()
