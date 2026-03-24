"""Edge TTS Audio Generation Service (Free Alternative).

This service generates audio for short video narration using Microsoft Edge TTS:
- High-quality neural voices (100+ voices)
- Word-level timing data for precise caption sync
- Completely free — no API key or billing required
- Multiple audio formats

Edge TTS uses the same neural voices as Microsoft Edge's Read Aloud feature.
It provides word-level boundary events with offset and duration data.

Pricing: FREE (no API key needed)
"""

import asyncio
import logging
import tempfile
from typing import Any

import edge_tts
from aiohttp import ClientConnectorDNSError, ClientConnectorError

from shorts_generator.services.google_tts_audio import GoogleTTSResult, WordTiming

logger = logging.getLogger(__name__)


# Voice presets for different use cases
EDGE_VOICE_PRESETS: dict[str, str] = {
    "narration_male": "en-US-GuyNeural",
    "narration_female": "en-US-AriaNeural",
    "news": "en-US-DavisNeural",
    "casual": "en-US-JasonNeural",
    "dramatic": "en-GB-RyanNeural",
}


class EdgeTTSGenerator:
    """Generates audio using Microsoft Edge TTS (free).

    Features:
    - Word-level timing data extraction
    - Multiple high-quality neural voices
    - No API key or billing required
    - Configurable speaking rate and pitch
    """

    def __init__(
        self,
        voice: str = "en-US-AriaNeural",
    ) -> None:
        """Initialize the Edge TTS generator.

        Args:
            voice: Voice name (e.g. 'en-US-AriaNeural', 'en-US-GuyNeural')
        """
        self.voice = voice
        logger.info(f"EdgeTTSGenerator initialized with voice: {voice}")

    async def generate(
        self,
        text: str,
        speaking_rate: float = 1.0,
        pitch: float = 0.0,
        custom_voice: str | None = None,
        ssml: bool = False,
        output_path: str | None = None,
        max_retries: int = 3,
    ) -> GoogleTTSResult:
        """Async implementation of audio generation with retry logic.

        Edge TTS is natively async, so we run the actual work here.
        Retries on network errors with exponential backoff.

        Args:
            text: Text to synthesize
            speaking_rate: Speaking rate (0.25 to 4.0, 1.0 = normal)
            pitch: Pitch adjustment in semitones
            custom_voice: Custom voice name (overrides default)
            ssml: Whether text is SSML formatted
            output_path: Custom output path
            max_retries: Maximum number of retry attempts for network errors

        Returns:
            GoogleTTSResult with audio file and timing data

        Raises:
            ValueError: If text is empty
            TimeoutError: If audio generation times out
            ConnectionError: If network connection fails after retries
        """
        voice = custom_voice or self.voice
        # Resolve preset names (e.g. "narration_male") to actual Edge TTS voice IDs
        voice = EDGE_VOICE_PRESETS.get(voice, voice)

        # Validate text is not empty
        text = text.strip()
        if not text:
            raise ValueError("Cannot generate audio from empty text")

        # Log text stats for debugging
        word_count = len(text.split())
        logger.info(
            f"Generating audio with Edge TTS voice: {voice}, "
            f"text length: {len(text)} chars, {word_count} words"
        )

        # Convert speaking_rate (1.0 = normal) to Edge TTS format ("+0%")
        rate_percent = int((speaking_rate - 1.0) * 100)
        rate_str = f"{rate_percent:+d}%"

        # Convert pitch (semitones) to Edge TTS format ("+0Hz")
        pitch_hz = int(pitch * 10)  # Approximate semitones to Hz
        pitch_str = f"{pitch_hz:+d}Hz"

        # Create output path
        if output_path is None:
            output_path = tempfile.mktemp(suffix=".mp3")

        # Retry logic for network errors
        last_error = None
        base_delay = 1  # Start with 1 second delay

        for attempt in range(max_retries):
            try:
                # Create communicator with word boundary tracking
                communicate = edge_tts.Communicate(
                    text=text,
                    voice=voice,
                    rate=rate_str,
                    pitch=pitch_str,
                    boundary="WordBoundary",
                )

                # Stream audio and collect word boundaries with timeout
                word_timings: list[WordTiming] = []
                raw_timepoints: list[dict[str, Any]] = []
                audio_data = bytearray()

                # Calculate timeout: ~3x the estimated audio duration for safety
                # For short content (30-60 seconds), this is 90-180 seconds
                estimated_duration_seconds = (word_count / 150) * 60  # ~150 words/minute
                stream_timeout = max(60, int(estimated_duration_seconds * 3))  # Minimum 1 minute

                async def stream_audio_with_timeout():
                    """Stream audio from Edge TTS with timeout protection."""
                    async for chunk in communicate.stream():
                        if chunk["type"] == "audio":
                            audio_data.extend(chunk["data"])
                        elif chunk["type"] == "WordBoundary":
                            # Edge TTS provides offset and duration in 100-nanosecond ticks
                            offset_ticks = chunk["offset"]
                            duration_ticks = chunk["duration"]

                            start_time = offset_ticks / 10_000_000  # Convert to seconds
                            end_time = (offset_ticks + duration_ticks) / 10_000_000

                            word = chunk.get("text", "").strip().strip(".,!?;:'\"()[]{}—–-")
                            if not word:
                                continue

                            word_timings.append(WordTiming(
                                word=word,
                                start_time=start_time,
                                end_time=end_time,
                            ))

                            raw_timepoints.append({
                                "text": chunk.get("text", ""),
                                "time_seconds": start_time,
                                "duration_seconds": end_time - start_time,
                            })

                # Run stream with timeout
                await asyncio.wait_for(stream_audio_with_timeout(), timeout=stream_timeout)

                # If we got here, success! Save and return
                with open(output_path, "wb") as f:
                    f.write(audio_data)

                logger.info(f"Audio saved to {output_path}")

                # Get audio duration
                duration = await self._get_audio_duration(output_path)
                if duration == 0:
                    # Fallback: estimate from word count
                    word_count = len(text.split())
                    duration = max(0.5, word_count / 2.5)

                # Fix last word end time using actual duration
                if word_timings and word_timings[-1].end_time < duration:
                    word_timings[-1].end_time = min(
                        word_timings[-1].end_time,
                        duration,
                    )

                result = GoogleTTSResult(
                    audio_path=output_path,
                    duration_seconds=duration,
                    word_timings=word_timings,
                    voice_used=voice,
                    encoding="MP3",
                    sample_rate=24000,
                    raw_timepoints=raw_timepoints,
                )

                logger.info(
                    f"Audio generated: {duration:.2f}s, {len(word_timings)} words, "
                    f"voice={voice}"
                )

                return result

            except (ClientConnectorDNSError, ClientConnectorError) as e:
                last_error = e
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(
                        f"Edge TTS connection failed (attempt {attempt + 1}/{max_retries}): {e}. "
                        f"Retrying in {delay}s..."
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        f"Edge TTS connection failed after {max_retries} attempts: {e}"
                    )
                    # Provide helpful error message
                    if isinstance(e, ClientConnectorDNSError):
                        raise ConnectionError(
                            f"DNS resolution failed for speech.platform.bing.com. "
                            f"Please check your internet connection and DNS settings. "
                            f"Original error: {e}"
                        ) from e
                    else:
                        raise ConnectionError(
                            f"Failed to connect to Edge TTS service after {max_retries} attempts. "
                            f"Please check your internet connection. "
                            f"Original error: {e}"
                        ) from e

            except Exception as e:
                # For non-network errors, don't retry - raise immediately
                logger.error(f"Edge TTS generation failed (non-retryable): {e}")
                raise

        # Should never reach here, but just in case
        raise ConnectionError(f"Failed to connect to Edge TTS: {last_error}")

    async def _get_audio_duration(self, audio_path: str) -> float:
        """Get the actual duration of an audio file using ffprobe."""
        try:
            result = await asyncio.create_subprocess_exec(
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                audio_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await result.communicate()
            if result.returncode == 0 and stdout.strip():
                return float(stdout.strip())
        except Exception as e:
            logger.warning(f"Could not detect audio duration: {e}")
        return 0.0


async def check_edge_tts_connectivity() -> dict[str, Any]:
    """Check if Edge TTS service is reachable.

    Useful for diagnosing DNS and connectivity issues.

    Returns:
        Dict with connectivity status and diagnostic information
    """
    import socket

    result = {
        "service": "Edge TTS",
        "host": "speech.platform.bing.com",
        "port": 443,
        "reachable": False,
        "error": None,
    }

    try:
        # Test DNS resolution
        loop = asyncio.get_event_loop()
        await loop.getaddrinfo("speech.platform.bing.com", 443)
        result["reachable"] = True
        result["message"] = "Edge TTS service is reachable"
        logger.info("Edge TTS connectivity check: PASSED")
    except socket.gaierror as e:
        result["error"] = f"DNS resolution failed: {e}"
        result["message"] = (
            "Cannot resolve speech.platform.bing.com. "
            "Check your internet connection and DNS settings."
        )
        logger.error(f"Edge TTS connectivity check: FAILED - {e}")
    except Exception as e:
        result["error"] = f"Unexpected error: {e}"
        logger.error(f"Edge TTS connectivity check: ERROR - {e}")

    return result
