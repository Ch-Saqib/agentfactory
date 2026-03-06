"""Google Cloud Text-to-Speech Audio Generation Service.

This service generates audio for short video narration using Google Cloud TTS:
- High-quality neural voices
- Word-level timing data (timepoints) for precise sync
- SSML support for advanced speech effects
- Multiple audio formats (MP3, WAV, OGG)

Google Cloud TTS provides accurate word-level timing data directly from the API,
which enables precise word-by-word caption synchronization.

Pricing (as of 2025):
- Standard voices: $4.00 / 1M characters
- Wavenet voices: $16.00 / 1M characters
- Neural2 voices: $16.00 / 1M characters

For a 60-second video (~150 words): ~$0.002 - $0.008 per video
"""

import asyncio
import json
import logging
import os
import tempfile
from dataclasses import dataclass, field
from typing import Any, Literal

from google.cloud import texttospeech
from google.cloud.texttospeech import (
    AudioConfig,
    SsmlVoiceGender,
    SynthesisInput,
    Voice,
    VoiceSelectionParams,
)

logger = logging.getLogger(__name__)


# TTS Encoding types
AudioEncoding = Literal["MP3", "WAV", "OGG_OPUS"]

ENCODING_MAP = {
    "MP3": texttospeech.AudioEncoding.MP3,
    "WAV": texttospeech.AudioEncoding.LINEAR16,
    "OGG_OPUS": texttospeech.AudioEncoding.OGG_OPUS,
}


@dataclass
class WordTiming:
    """Represents timing data for a single word.

    Attributes:
        word: The spoken word
        start_time: Start time in seconds
        end_time: End time in seconds
    """

    word: str
    start_time: float
    end_time: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "word": self.word,
            "start": self.start_time,
            "end": self.end_time,
        }


@dataclass
class GoogleTTSResult:
    """Result from Google Cloud TTS generation.

    Attributes:
        audio_path: Path to generated audio file
        duration_seconds: Audio duration in seconds
        word_timings: List of word-level timings
        voice_used: Which voice was used
        encoding: Audio encoding format
        sample_rate: Sample rate in Hz
    """

    audio_path: str
    duration_seconds: float
    word_timings: list[WordTiming]
    voice_used: str
    encoding: AudioEncoding
    sample_rate: int
    raw_timepoints: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "audio_path": self.audio_path,
            "duration_seconds": self.duration_seconds,
            "word_timings": [w.to_dict() for w in self.word_timings],
            "voice_used": self.voice_used,
            "encoding": self.encoding,
            "sample_rate": self.sample_rate,
            "word_count": len(self.word_timings),
        }

    def save_timing_json(self, output_path: str) -> None:
        """Save timing data to JSON file.

        Args:
            output_path: Path to save JSON file
        """
        timing_data = {
            "duration": self.duration_seconds,
            "voice": self.voice_used,
            "words": [w.to_dict() for w in self.word_timings],
            "raw_timepoints": self.raw_timepoints,
        }

        with open(output_path, "w") as f:
            json.dump(timing_data, f, indent=2)

        logger.info(f"Saved timing data to {output_path}")


class GoogleCloudTTSGenerator:
    """Generates audio using Google Cloud Text-to-Speech API.

    Features:
    - Word-level timing data extraction
    - Multiple neural voices
    - SSML support
    - Configurable audio quality
    - Automatic duration detection
    """

    # Default audio settings
    DEFAULT_SAMPLE_RATE = 24000  # Hz
    DEFAULT_ENCODING: AudioEncoding = "MP3"
    DEFAULT_SPEAKING_RATE = 1.0  # Normal speed
    DEFAULT_PITCH = 0.0  # Normal pitch

    # Voice presets for different use cases
    VOICE_PRESETS: dict[str, dict[str, str]] = {
        "narration_male": {
            "language_code": "en-US",
            "name": "en-US-Neural2-C",  # Male voice
        },
        "narration_female": {
            "language_code": "en-US",
            "name": "en-US-Neural2-A",  # Female voice
        },
        "news": {
            "language_code": "en-US",
            "name": "en-US-News-K",  # News style
        },
        "casual": {
            "language_code": "en-US",
            "name": "en-US-Neural2-F",  # Casual, friendly
        },
        "dramatic": {
            "language_code": "en-GB",
            "name": "en-GB-Neural2-B",  # British, dramatic
        },
    }

    def __init__(
        self,
        credentials_path: str | None = None,
        voice_preset: str = "narration_male",
        encoding: AudioEncoding = DEFAULT_ENCODING,
        sample_rate: int = DEFAULT_SAMPLE_RATE,
    ):
        """Initialize the Google Cloud TTS generator.

        Args:
            credentials_path: Path to Google Cloud credentials JSON file.
                If None, uses GOOGLE_APPLICATION_CREDENTIALS env var.
            voice_preset: Voice preset to use (see VOICE_PRESETS)
            encoding: Audio encoding format
            sample_rate: Sample rate in Hz
        """
        self._client: texttospeech.TextToSpeechClient | None = None
        self._credentials_path = credentials_path
        self.voice_preset = voice_preset
        self.encoding = encoding
        self.sample_rate = sample_rate

        # Validate voice preset
        if voice_preset not in self.VOICE_PRESETS:
            raise ValueError(
                f"Invalid voice preset: {voice_preset}. "
                f"Available: {list(self.VOICE_PRESETS.keys())}"
            )

    @property
    def client(self) -> texttospeech.TextToSpeechClient:
        """Get or create TTS client."""
        if self._client is None:
            # Set credentials path if provided
            if self._credentials_path:
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self._credentials_path

            self._client = texttospeech.TextToSpeechClient()
            logger.info("Google Cloud TTS client initialized")

        return self._client

    def _get_voice_params(
        self,
        custom_voice: str | None = None,
        gender: SsmlVoiceGender | None = None,
    ) -> VoiceSelectionParams:
        """Get voice selection parameters.

        Args:
            custom_voice: Custom voice name (overrides preset)
            gender: Voice gender (SSML voice gender enum)

        Returns:
            VoiceSelectionParams object
        """
        preset = self.VOICE_PRESETS[self.voice_preset]

        voice_name = custom_voice or preset["name"]
        language_code = preset["language_code"]

        return VoiceSelectionParams(
            language_code=language_code,
            name=voice_name,
            ssml_gender=gender,
        )

    def _parse_timepoints(
        self,
        response: texttospeech.SynthesizeSpeechResponse,
    ) -> list[WordTiming]:
        """Parse timepoints from TTS response.

        Google Cloud TTS returns timepoints with text and timing info.
        Each timepoint contains the word and its start time in seconds.

        Args:
            response: TTS synthesis response

        Returns:
            List of WordTiming objects
        """
        word_timings: list[WordTiming] = []

        if hasattr(response, "timepoints") and response.timepoints:
            for i, tp in enumerate(response.timepoints):
                # Extract word (remove surrounding punctuation)
                word = tp.text.strip().strip(".,!?;:'\"()[]{}")
                if not word:
                    continue

                # Google provides time in seconds
                start_time = tp.time_seconds
                # Estimate end time from next timepoint or duration
                if i + 1 < len(response.timepoints):
                    end_time = response.timepoints[i + 1].time_seconds
                else:
                    # Last word - use audio duration if available
                    end_time = start_time + 0.3  # Default 300ms per word

                word_timings.append(WordTiming(
                    word=word,
                    start_time=start_time,
                    end_time=end_time,
                ))

        logger.info(f"Parsed {len(word_timings)} word timings from TTS response")
        return word_timings

    async def _get_audio_duration(self, audio_path: str) -> float:
        """Get the actual duration of an audio file using ffprobe.

        Args:
            audio_path: Path to audio file

        Returns:
            Duration in seconds
        """
        try:
            result = await asyncio.to_thread(
                _run_ffprobe,
                audio_path,
            )
            return result
        except Exception as e:
            logger.warning(f"Could not detect audio duration: {e}")
            return 0.0

    def generate(
        self,
        text: str,
        speaking_rate: float = DEFAULT_SPEAKING_RATE,
        pitch: float = DEFAULT_PITCH,
        custom_voice: str | None = None,
        ssml: bool = False,
        output_path: str | None = None,
    ) -> GoogleTTSResult:
        """Generate audio with word-level timing data.

        Args:
            text: Text to synthesize (plain text or SSML if ssml=True)
            speaking_rate: Speaking rate (0.25 to 4.0, 1.0 = normal)
            pitch: Pitch adjustment (-20.0 to 20.0 semitones)
            custom_voice: Custom voice name (overrides preset)
            ssml: Whether text is SSML formatted
            output_path: Custom output path (default: auto-generated temp file)

        Returns:
            GoogleTTSResult with audio file and timing data

        Raises:
            Exception: If TTS generation fails
        """
        logger.info(f"Generating audio with {self.voice_preset} voice")

        # Prepare input
        synthesis_input = SynthesisInput(ssml=text) if ssml else SynthesisInput(text=text)

        # Configure audio output
        audio_config = AudioConfig(
            audio_encoding=ENCODING_MAP[self.encoding],
            sample_rate_hertz=self.sample_rate,
            speaking_rate=speaking_rate,
            pitch=pitch,
        )

        # Get voice parameters
        voice_params = self._get_voice_params(custom_voice=custom_voice)

        # Synthesize speech with timepointing enabled for word-level timing
        try:
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice_params,
                audio_config=audio_config,
                enable_time_pointing=[texttospeech.SynthesizeSpeechRequest.TimepointType.SSML_MARK],
            )
        except Exception as e:
            logger.error(f"Google Cloud TTS synthesis failed: {e}")
            raise

        # Create output file
        if output_path is None:
            output_path = tempfile.mktemp(suffix=f".{self.encoding.lower()}")

        # Save audio
        with open(output_path, "wb") as f:
            f.write(response.audio_content)

        logger.info(f"Audio saved to {output_path}")

        # Get actual duration
        duration = asyncio.run(self._get_audio_duration(output_path))
        if duration == 0:
            # Fallback: estimate from word count
            word_count = len(text.split())
            duration = max(0.5, word_count / 2.5)  # ~2.5 words/second

        # Parse word timings
        word_timings = self._parse_timepoints(response)

        # Extract raw timepoints for debugging
        raw_timepoints = []
        if hasattr(response, "timepoints"):
            for tp in response.timepoints:
                raw_timepoints.append({
                    "text": tp.text,
                    "time_seconds": tp.time_seconds,
                })

        result = GoogleTTSResult(
            audio_path=output_path,
            duration_seconds=duration,
            word_timings=word_timings,
            voice_used=custom_voice or self.VOICE_PRESETS[self.voice_preset]["name"],
            encoding=self.encoding,
            sample_rate=self.sample_rate,
            raw_timepoints=raw_timepoints,
        )

        logger.info(
            f"Audio generated: {duration:.2f}s, {len(word_timings)} words, "
            f"voice={result.voice_used}"
        )

        return result

    def generate_with_ssml(
        self,
        ssml: str,
        output_path: str | None = None,
    ) -> GoogleTTSResult:
        """Generate audio from SSML with advanced speech effects.

        SSML allows for:
        - Pauses and breaks
        - Emphasis on words
        - Pitch and rate changes
        - Pronunciation overrides

        Args:
            ssml: SSML-formatted text
            output_path: Custom output path

        Returns:
            GoogleTTSResult with audio and timing

        Example SSML:
            <speak>
                <p>
                    <emphasis level="strong">Welcome</emphasis>
                    to the <break time="500ms"/>AI Agent Factory.
                </p>
            </speak>
        """
        return self.generate(ssml, ssml=True, output_path=output_path)

    def list_available_voices(self, language_code: str = "en-US") -> list[Voice]:
        """List all available voices for a language.

        Args:
            language_code: Language code (e.g., "en-US", "en-GB")

        Returns:
            List of Voice objects
        """
        response = self.client.list_voices(language_code=language_code)
        return response.voices


def _run_ffprobe(audio_path: str) -> float:
    """Run ffprobe to get audio duration.

    Args:
        audio_path: Path to audio file

    Returns:
        Duration in seconds
    """
    import subprocess

    result = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            audio_path,
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0 and result.stdout.strip():
        return float(result.stdout.strip())

    return 0.0


# Singleton instance
google_tts_generator = GoogleCloudTTSGenerator()
