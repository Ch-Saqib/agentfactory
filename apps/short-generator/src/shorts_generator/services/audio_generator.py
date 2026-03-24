"""Audio Generation Service using Microsoft Edge-TTS.

This service generates audio for short video narration:
- Text-to-speech using Edge-TTS (free)
- Background music mixing
- Closed captions generation in SRT format

Cost: FREE
"""

import asyncio
import logging
import math
import os
import tempfile
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import Any

import httpx
import edge_tts

from shorts_generator.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class GeneratedAudio:
    """Represents generated audio.

    Attributes:
        url: URL to the audio file
        duration_seconds: Audio duration in seconds
        file_path: Local file path (for temporary files)
        generation_method: How the audio was generated (edge_tts)
        voice_used: Which voice was used
        word_timings: Optional list of word boundary timings from TTS
    """

    url: str
    duration_seconds: float
    file_path: str
    generation_method: str
    voice_used: str
    word_timings: list[dict[str, Any]] | None = None


class AudioGenerator:
    """Generates audio for short video narration."""

    # Default audio settings
    SAMPLE_RATE = 24000  # Hz
    BIT_RATE = 128000  # bps

    def __init__(self):
        """Initialize the audio generator."""
        self._http_client: httpx.AsyncClient | None = None

    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=60.0)
        return self._http_client

    async def _get_audio_duration(self, audio_path: str) -> float:
        """Get the actual duration of an audio file using ffprobe."""
        try:
            import subprocess

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
                    audio_path,
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0 and result.stdout.strip():
                return float(result.stdout.strip())

            logger.warning(f"ffprobe failed for audio duration: {result.stderr}")
            return 0.0
        except Exception as e:
            logger.warning(f"Could not detect audio duration: {e}")
            return 0.0

    async def _refine_timings_with_alignment(
        self,
        audio_path: str,
        transcript: str,
        word_timings: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Refine word timings using Whisper forced alignment (stable-ts).

        This takes the audio file and known transcript and runs forced alignment
        to get frame-accurate word boundaries — significantly more precise than
        Edge-TTS WordBoundary events.

        Falls back gracefully to the original timings if stable-ts is
        unavailable or alignment fails.

        Args:
            audio_path: Path to the generated audio file
            transcript: The original script text
            word_timings: Word timings from Edge-TTS WordBoundary events

        Returns:
            Refined word timings list (or the original if alignment fails)
        """
        try:
            import stable_whisper  # type: ignore[import-untyped]
        except ImportError:
            logger.info(
                "stable-ts not installed — using Edge-TTS WordBoundary timings. "
                "Install with: pip install stable-ts"
            )
            return word_timings

        try:
            # Use the tiny model — it's sufficient for forced alignment when
            # we already have the correct transcript.  The model is ~39 MB.
            model = await asyncio.to_thread(stable_whisper.load_model, "tiny")
            result = await asyncio.to_thread(
                model.align, audio_path, transcript, language="en"
            )

            refined: list[dict[str, Any]] = []
            for segment in result.segments:
                for word_info in segment.words:
                    w = (word_info.word or "").strip()
                    if not w:
                        continue
                    refined.append(
                        {
                            "word": w,
                            "start": float(word_info.start),
                            "end": float(word_info.end),
                        }
                    )

            if refined:
                logger.info(
                    f"Forced alignment refined {len(refined)} words "
                    f"(was {len(word_timings)} from EdgeTTS)"
                )
                return refined

            logger.warning("Forced alignment returned 0 words — keeping EdgeTTS timings")
            return word_timings

        except Exception as e:
            logger.warning(f"Forced alignment failed, keeping EdgeTTS timings: {e}")
            return word_timings

    def _estimate_duration(self, text: str, words_per_second: float = 2.5) -> float:
        """Estimate spoken duration from text.

        Args:
            text: Text to estimate duration for
            words_per_second: Average speaking rate (default: 2.5)

        Returns:
            Estimated duration in seconds
        """
        word_count = len(text.split())
        # Keep this as a *fallback* only. Real duration should come from ffprobe.
        # Avoid a hard 1.0s minimum because it causes noticeable caption drift on short phrases.
        return max(0.2, word_count / words_per_second)

    async def generate_narration(
        self,
        script_text: str,
        voice: str = "en-US-AriaNeural",
    ) -> GeneratedAudio:
        """Generate narration audio using Edge-TTS.

        Args:
            script_text: Text to convert to speech
            voice: Voice to use (default: en-US-AriaNeural)

        Returns:
            GeneratedAudio object with audio URL

        Raises:
            Exception: If TTS generation fails
        """
        logger.info(f"Generating narration with voice: {voice}")

        try:
            communicate = edge_tts.Communicate(
                text=script_text,
                voice=voice,
                rate='+0%',  # Normal speed
                volume='+0%',  # Normal volume
                pitch='+0Hz',  # Normal pitch
            )

            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                # Use streaming API to collect word boundaries for karaoke sync.
                word_timings: list[dict[str, Any]] = []
                async for chunk in communicate.stream():
                    if chunk.get("type") == "audio":
                        tmp_file.write(chunk.get("data", b""))
                    elif chunk.get("type") == "WordBoundary":
                        # Offsets are in 100-nanosecond units.
                        offset_100ns = chunk.get("offset", 0) or 0
                        duration_100ns = chunk.get("duration", 0) or 0
                        start_s = float(offset_100ns) / 10_000_000.0
                        end_s = float(offset_100ns + duration_100ns) / 10_000_000.0

                        spoken = (chunk.get("text") or "").strip()
                        if spoken:
                            word_timings.append(
                                {
                                    "word": spoken,
                                    "start": start_s,
                                    "end": end_s,
                                }
                            )

                tmp_file.flush()

                # Get file size for logging
                file_size = os.path.getsize(tmp_file.name)

                # Prefer real duration from the audio file (improves caption sync)
                detected_duration = await self._get_audio_duration(tmp_file.name)
                duration = detected_duration if detected_duration > 0 else self._estimate_duration(script_text)

                # Refine word timings using forced alignment (stable-ts)
                # for frame-accurate sync. Falls back to EdgeTTS timings
                # if stable-ts is unavailable or alignment fails.
                if word_timings:
                    word_timings = await self._refine_timings_with_alignment(
                        tmp_file.name, script_text, word_timings
                    )

                audio = GeneratedAudio(
                    url=f"file://{tmp_file.name}",
                    duration_seconds=duration,
                    file_path=tmp_file.name,
                    generation_method="edge_tts",
                    voice_used=voice,
                    word_timings=word_timings or None,
                )

                logger.info(
                    f"Narration generated: {duration:.2f}s (detected={detected_duration:.2f}s), "
                    f"{file_size} bytes, word_timings={len(word_timings)}"
                )

                return audio

        except Exception as e:
            logger.error(f"Narration generation failed: {e}")
            raise

    async def add_background_music(
        self,
        narration_url: str,
        music_track: str = "background_lofi.mp3",
        music_volume: float = 0.3,  # 30% volume
    ) -> GeneratedAudio:
        """Add background music to narration.

        Args:
            narration_url: URL or path to narration audio
            music_track: Path or identifier for background music
            music_volume: Music volume (0.0 to 1.0)

        Returns:
            GeneratedAudio with mixed audio

        Raises:
            Exception: If mixing fails or FFmpeg not available
        """
        logger.info(f"Mixing background music at {music_volume*100}% volume")

        try:
            # Import FFmpeg Python
            import ffmpeg

            # Create output file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                output_path = tmp_file.name

                # Get file paths from URLs
                if narration_url.startswith("file://"):
                    narration_path = narration_url.replace("file://", "")
                else:
                    # Download to temp file
                    narration_path = tempfile.mktemp(suffix=".mp3")
                    # TODO: Implement download from URL

                # Mix audio using FFmpeg
                try:
                    # Get duration of narration
                    probe = ffmpeg.probe(narration_path)
                    narration_duration = float(probe.format["duration"])

                    # Calculate how much music we need (same duration as narration)
                    # In production, you'd loop the music track

                    (
                        ffmpeg
                        .input(narration_path, stream=0, a="apad")
                        .filter_(0, "volume", f"1.0")  # Keep narration at 100%
                    )

                    # For now, just return the narration without music
                    # In production, you'd add: ffmpeg.input(music_track, stream=1, t=loop_duration)
                    # And use: amix=inputs=1, volume=1

                    # Simplified: return narration as-is
                    audio = GeneratedAudio(
                        url=narration_url,
                        duration_seconds=narration_duration,
                        file_path=narration_path,
                        generation_method="edge_tts",  # Still edge_tts since we didn't modify
                        voice_used="en-US-AriaNeural",
                    )

                    return audio

                except ffmpeg.Error as e:
                    logger.error(f"FFmpeg processing failed: {e}")
                    raise Exception(f"Audio mixing failed: {e}")

        except ImportError:
            logger.warning("FFmpeg not available, returning narration without music")
            # Fallback: return narration as-is
            # In production, you'd want to fail gracefully
            return GeneratedAudio(
                url=narration_url,
                duration_seconds=10.0,
                file_path="",
                generation_method="edge_tts",
                voice_used="en-US-AriaNeural",
            )

    def _format_timestamp(self, seconds: float) -> str:
        """Format seconds to SRT timestamp format.

        Args:
            seconds: Time in seconds

        Returns:
            Formatted timestamp (HH:MM:SS,mmm)
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)  # Convert to int
        millis = int((seconds - int(seconds)) * 1000)

        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    async def generate_captions(
        self,
        script_text: str,
        scene_timings: list[dict[str, Any]] | None = None,
        duration_seconds: float | None = None,
    ) -> str:
        """Generate closed captions in SRT format.

        Args:
            script_text: Full script text
            scene_timings: Optional list of scene timings for more accurate captions

        Returns:
            SRT format captions as string
        """
        logger.info("Generating closed captions")

        # Split script into words
        words = script_text.split()
        total_words = len(words)

        if total_words == 0:
            return ""

        # Assume even distribution of words across time
        # In production, you'd use word timings from TTS API if available
        duration_seconds = duration_seconds or self._estimate_duration(script_text)
        time_per_word = duration_seconds / total_words

        # Build SRT content
        srt_lines = []

        # SRT format: 1, 00:00:00,000 --> 00:00:02,500
        current_time = 0.0
        caption_index = 1
        caption_words = []

        for i, word in enumerate(words):
            caption_words.append(word)

            # Create a caption every ~10 words or at end
            if len(caption_words) >= 10 or i == total_words - 1:
                caption_text = " ".join(caption_words)
                word_duration = len(caption_words) * time_per_word
                start_time = current_time
                end_time = current_time + word_duration

                srt_lines.append(f"{caption_index}")
                srt_lines.append(f"{self._format_timestamp(start_time)} --> {self._format_timestamp(end_time)}")
                srt_lines.append(caption_text)
                srt_lines.append("")  # Blank line between captions

                current_time = end_time
                caption_index += 1
                caption_words = []

        return "\n".join(srt_lines)

    async def generate_audio_for_script(
        self,
        script_text: str,
        voice: str = "en-US-AriaNeural",
        add_music: bool = False,
    ) -> tuple[GeneratedAudio, str]:
        """Generate complete audio package for a script.

        Args:
            script_text: Script text to narrate
            voice: Voice to use
            add_music: Whether to add background music

        Returns:
            Tuple of (GeneratedAudio, SRT captions)
        """
        # Generate narration
        narration = await self.generate_narration(script_text, voice)

        # Generate captions
        captions = await self.generate_captions(script_text, duration_seconds=narration.duration_seconds)

        # Add music if requested
        if add_music:
            final_audio = await self.add_background_music(narration.url)
        else:
            final_audio = narration

        return final_audio, captions


# Singleton instance
audio_generator = AudioGenerator()
