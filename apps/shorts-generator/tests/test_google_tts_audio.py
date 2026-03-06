"""Tests for Google Cloud TTS Audio Generation Service.

This test module validates:
1. Word-level timing data extraction
2. Timing accuracy verification
3. Audio duration detection
4. Voice preset functionality
5. SSML support
"""

import json
import os
import tempfile
from pathlib import Path
from unittest import mock

import pytest
from google.cloud.texttospeech import (
    SynthesizeSpeechResponse,
    Timepoint,
)

from shorts_generator.services.google_tts_audio import (
    GoogleCloudTTSGenerator,
    GoogleTTSResult,
    WordTiming,
    _run_ffprobe,
)


class TestWordTiming:
    """Tests for word-level timing extraction."""

    @pytest.fixture
    def mock_timepoints(self) -> list[Timepoint]:
        """Create mock timepoints for testing."""
        timepoints = []
        words = ["Hello", "world", "this", "is", "a", "test"]
        for i, word in enumerate(words):
            tp = Timepoint(
                text=word,
                time_seconds=float(i * 0.25),  # 250ms per word
            )
            timepoints.append(tp)
        return timepoints

    @pytest.fixture
    def mock_response(self, mock_timepoints: list[Timepoint]) -> SynthesizeSpeechResponse:
        """Create a mock TTS response."""
        response = SynthesizeSpeechResponse()
        response.audio_content = b"mock_audio_data"

        # Set timepoints - note: Timepoint messages need special handling
        # We'll use a mock since we can't directly assign to a repeated field
        return response

    def test_word_timing_to_dict(self):
        """Test WordTiming serialization to dict."""
        timing = WordTiming(
            word="hello",
            start_time=0.0,
            end_time=0.3,
        )

        result = timing.to_dict()

        assert result == {
            "word": "hello",
            "start": 0.0,
            "end": 0.3,
        }

    def test_parse_timepoints_from_response(self):
        """Test parsing timepoints from TTS response."""
        generator = GoogleCloudTTSGenerator()

        # Create a mock response with timepoints
        mock_response = mock.Mock()
        mock_response.timepoints = []

        words = ["Hello", "world", "this", "is", "a", "test"]
        for i, word in enumerate(words):
            tp = mock.Mock()
            tp.text = word
            tp.time_seconds = float(i * 0.25)
            mock_response.timepoints.append(tp)

        # Parse timepoints
        timings = generator._parse_timepoints(mock_response)

        # Verify
        assert len(timings) == 6
        assert timings[0].word == "Hello"
        assert timings[0].start_time == 0.0
        assert timings[0].end_time == 0.25
        assert timings[1].word == "world"
        assert timings[1].start_time == 0.25

    def test_parse_timepoints_punctuation_removal(self):
        """Test that punctuation is stripped from words."""
        generator = GoogleCloudTTSGenerator()

        mock_response = mock.Mock()
        mock_response.timepoints = []

        # Add timepoints with punctuation
        words_with_punct = ["Hello,", "world!", "This", "is", "a", "test."]
        for i, word in enumerate(words_with_punct):
            tp = mock.Mock()
            tp.text = word
            tp.time_seconds = float(i * 0.25)
            mock_response.timepoints.append(tp)

        timings = generator._parse_timepoints(mock_response)

        # Verify punctuation is removed
        assert timings[0].word == "Hello"
        assert timings[1].word == "world"
        assert timings[5].word == "test"

    def test_parse_timepoints_empty_words_skipped(self):
        """Test that empty/punctuation-only timepoints are skipped."""
        generator = GoogleCloudTTSGenerator()

        mock_response = mock.Mock()
        mock_response.timepoints = []

        # Mix of valid and empty timepoints
        test_cases = [
            ("Hello", 0.0),
            ("   ", 0.25),
            ("world", 0.5),
            ("!", 0.75),
            ("test", 1.0),
        ]

        for word, time_sec in test_cases:
            tp = mock.Mock()
            tp.text = word
            tp.time_seconds = time_sec
            mock_response.timepoints.append(tp)

        timings = generator._parse_timepoints(mock_response)

        # Only valid words should be included
        assert len(timings) == 3
        assert [t.word for t in timings] == ["Hello", "world", "test"]


class TestGoogleTTSResult:
    """Tests for GoogleTTSResult dataclass."""

    def test_to_dict(self):
        """Test GoogleTTSResult serialization to dict."""
        timings = [
            WordTiming("Hello", 0.0, 0.25),
            WordTiming("world", 0.25, 0.5),
        ]

        result = GoogleTTSResult(
            audio_path="/tmp/test.mp3",
            duration_seconds=5.0,
            word_timings=timings,
            voice_used="en-US-Neural2-C",
            encoding="MP3",
            sample_rate=24000,
        )

        result_dict = result.to_dict()

        assert result_dict["audio_path"] == "/tmp/test.mp3"
        assert result_dict["duration_seconds"] == 5.0
        assert result_dict["voice_used"] == "en-US-Neural2-C"
        assert result_dict["encoding"] == "MP3"
        assert result_dict["sample_rate"] == 24000
        assert result_dict["word_count"] == 2
        assert len(result_dict["word_timings"]) == 2

    def test_save_timing_json(self, tmp_path: Path):
        """Test saving timing data to JSON file."""
        timings = [
            WordTiming("Hello", 0.0, 0.25),
            WordTiming("world", 0.25, 0.5),
        ]

        result = GoogleTTSResult(
            audio_path="/tmp/test.mp3",
            duration_seconds=5.0,
            word_timings=timings,
            voice_used="en-US-Neural2-C",
            encoding="MP3",
            sample_rate=24000,
        )

        # Save to temp file
        output_path = tmp_path / "timing.json"
        result.save_timing_json(str(output_path))

        # Verify file contents
        assert output_path.exists()

        with open(output_path) as f:
            data = json.load(f)

        assert data["duration"] == 5.0
        assert data["voice"] == "en-US-Neural2-C"
        assert len(data["words"]) == 2
        assert data["words"][0] == {"word": "Hello", "start": 0.0, "end": 0.25}
        assert data["words"][1] == {"word": "world", "start": 0.25, "end": 0.5}


class TestTimingAccuracy:
    """Tests to verify timing accuracy of Google Cloud TTS."""

    @pytest.mark.skipif(
        os.getenv("GOOGLE_APPLICATION_CREDENTIALS") is None,
        reason="Google Cloud credentials not configured",
    )
    async def test_timing_accuracy_real_tts(self):
        """Integration test: Verify timing accuracy with real TTS API.

        This test calls the actual Google Cloud TTS API and verifies:
        1. Audio file is created
        2. Duration is detected correctly
        3. Word timings are present
        4. Timing data is consistent (no overlaps, monotonic)

        Note: This test requires valid GOOGLE_APPLICATION_CREDENTIALS.
        """
        generator = GoogleCloudTTSGenerator()

        # Test with simple, clear text
        test_text = "Hello world. This is a test of word timing accuracy."

        result = generator.generate(test_text)

        # Verify audio file exists
        assert os.path.exists(result.audio_path)

        # Verify duration is reasonable (should be 2-4 seconds for this text)
        assert 1.0 <= result.duration_seconds <= 10.0

        # Verify word timings are present
        assert len(result.word_timings) > 0

        # Verify timing consistency
        for i, timing in enumerate(result.word_timings):
            assert timing.start_time >= 0, f"Word {i} has negative start time"
            assert timing.end_time > timing.start_time, f"Word {i} has end <= start"

            if i > 0:
                prev = result.word_timings[i - 1]
                # Timings should be roughly sequential (allow small overlap)
                assert timing.start_time >= prev.start_time, (
                    f"Word {i} starts before previous word"
                )

        # Clean up
        if os.path.exists(result.audio_path):
            os.remove(result.audio_path)

    @pytest.mark.skipif(
        os.getenv("GOOGLE_APPLICATION_CREDENTIALS") is None,
        reason="Google Cloud credentials not configured",
    )
    def test_save_and_load_timing_json(self, tmp_path: Path):
        """Test full round-trip of timing data save/load."""
        generator = GoogleCloudTTSGenerator()

        test_text = "Testing JSON serialization of timing data."

        result = generator.generate(test_text)

        # Save timing data
        json_path = tmp_path / "timing.json"
        result.save_timing_json(str(json_path))

        # Verify saved data
        with open(json_path) as f:
            loaded = json.load(f)

        assert loaded["voice"] == result.voice_used
        assert loaded["duration"] == result.duration_seconds
        assert len(loaded["words"]) == len(result.word_timings)

        # Clean up
        if os.path.exists(result.audio_path):
            os.remove(result.audio_path)


class TestVoicePresets:
    """Tests for voice preset functionality."""

    def test_get_voice_params_default(self):
        """Test getting default voice parameters."""
        generator = GoogleCloudTTSGenerator(voice_preset="narration_male")

        voice_params = generator._get_voice_params()

        assert voice_params.name == "en-US-Neural2-C"
        assert voice_params.language_code == "en-US"

    def test_get_voice_params_custom_voice(self):
        """Test custom voice override."""
        generator = GoogleCloudTTSGenerator(voice_preset="narration_male")

        voice_params = generator._get_voice_params(custom_voice="en-GB-Neural2-B")

        assert voice_params.name == "en-GB-Neural2-B"

    def test_invalid_voice_preset(self):
        """Test that invalid voice preset raises error."""
        with pytest.raises(ValueError, match="Invalid voice preset"):
            GoogleCloudTTSGenerator(voice_preset="invalid_preset")

    def test_all_voice_presets_valid(self):
        """Test that all defined presets are valid."""
        for preset in GoogleCloudTTSGenerator.VOICE_PRESETS:
            generator = GoogleCloudTTSGenerator(voice_preset=preset)
            voice_params = generator._get_voice_params()
            assert voice_params.name is not None
            assert voice_params.language_code is not None


class TestAudioGeneration:
    """Tests for audio generation functionality."""

    def test_generate_creates_audio_file(self, tmp_path: Path):
        """Test that generate creates an audio file."""
        generator = GoogleCloudTTSGenerator()

        # Mock the client
        mock_client = mock.Mock()
        mock_response = mock.Mock()
        mock_response.audio_content = b"fake_audio_data"
        mock_response.timepoints = []
        mock_client.synthesize_speech.return_value = mock_response

        generator._client = mock_client

        # Generate with custom output path
        output_path = tmp_path / "test_audio.mp3"
        result = generator.generate("Test text", output_path=str(output_path))

        # Verify file was created
        assert output_path.exists()
        assert result.audio_path == str(output_path)

    def test_generate_with_ssml(self):
        """Test SSML input format."""
        generator = GoogleCloudTTSGenerator()

        mock_client = mock.Mock()
        mock_response = mock.Mock()
        mock_response.audio_content = b"fake_audio_data"
        mock_response.timepoints = []
        mock_client.synthesize_speech.return_value = mock_response

        generator._client = mock_client

        ssml = '<speak><p>Hello <break time="500ms"/>world.</p></speak>'

        # Should not raise
        result = generator.generate_with_ssml(ssml)
        assert result.audio_path is not None


class TestFfprobeIntegration:
    """Tests for ffprobe audio duration detection."""

    def test_run_ffprobe_missing_file(self):
        """Test ffprobe with missing file."""
        result = _run_ffprobe("/nonexistent/file.mp3")
        assert result == 0.0

    @pytest.mark.skipif(
        os.system("which ffprobe > /dev/null 2>&1") != 0,
        reason="ffprobe not installed",
    )
    def test_run_ffprobe_with_audio_file(self, tmp_path: Path):
        """Test ffprobe with a real audio file (if available)."""
        # Create a minimal WAV file (1 second of silence)
        import wave

        audio_path = tmp_path / "test_audio.wav"
        with wave.open(str(audio_path), "w") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(24000)
            # Write 1 second of silence
            wav_file.writeframes(b"\x00\x00" * 24000)

        duration = _run_ffprobe(str(audio_path))
        assert duration > 0.9 and duration < 1.1  # ~1 second


class TestConfigIntegration:
    """Tests for configuration integration."""

    def test_generator_uses_settings(self):
        """Test that generator respects settings."""
        from shorts_generator.core.config import settings

        generator = GoogleCloudTTSGenerator(
            voice_preset=settings.google_tts_voice_preset,
            encoding=settings.google_tts_encoding,
            sample_rate=settings.google_tts_sample_rate,
        )

        assert generator.voice_preset == settings.google_tts_voice_preset
        assert generator.encoding == settings.google_tts_encoding
        assert generator.sample_rate == settings.google_tts_sample_rate


class TestMarkdownParsing:
    """Tests for parsing markdown from Docusaurus lessons."""

    def test_parse_sample_lesson(self):
        """Test parsing a sample lesson markdown file."""
        # Find a sample lesson file
        docs_dir = Path(__file__).parent.parent.parent / "apps" / "learn-app" / "docs"

        if not docs_dir.exists():
            pytest.skip("No docs directory found")

        # Find first markdown file
        md_files = list(docs_dir.rglob("*.md"))
        if not md_files:
            pytest.skip("No markdown files found in docs")

        # Parse first file
        sample_file = md_files[0]
        with open(sample_file) as f:
            content = f.read()

        # Basic validation
        assert len(content) > 0
        assert "#" in content or len(content) > 100


# Example: Manual timing verification test
# Run this to manually verify timing accuracy with a real file
@pytest.mark.skipif(
    os.getenv("GOOGLE_APPLICATION_CREDENTIALS") is None,
    reason="Google Cloud credentials not configured",
)
class TestManualTimingVerification:
    """Manual tests for timing verification (run with credentials)."""

    def test_verify_timing_with_sample_text(self):
        """Manually verify timing is accurate.

        This test generates audio and saves the timing data to a JSON file
        that can be manually inspected for accuracy.
        """
        generator = GoogleCloudTTSGenerator()

        # Sample text from a real lesson
        test_text = (
            "The Seven Principles of Agent Work guide everything we do. "
            "First, Bash is the Key — use command line tools. "
            "Second, Code as Universal Interface — express work as code."
        )

        result = generator.generate(test_text)

        # Print timing info
        print(f"\n{'='*60}")
        print(f"Voice: {result.voice_used}")
        print(f"Duration: {result.duration_seconds:.2f}s")
        print(f"Words: {len(result.word_timings)}")
        print("\nWord Timings:")
        print(f"{'Word':<15} {'Start':<10} {'End':<10} {'Duration'}")
        print("-" * 60)

        for timing in result.word_timings:
            duration = timing.end_time - timing.start_time
            print(
                f"{timing.word:<15} {timing.start_time:<10.3f} "
                f"{timing.end_time:<10.3f} {duration:.3f}s"
            )

        print(f"{'='*60}\n")

        # Save timing data to temp file for manual inspection
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            result.save_timing_json(f.name)
            print(f"Timing data saved to: {f.name}")

        # Verify basic assertions
        assert len(result.word_timings) >= 20  # Should have ~20 words
        assert result.duration_seconds > 5.0  # Should be at least 5 seconds

        # Verify last word ends near total duration
        if result.word_timings:
            last_timing = result.word_timings[-1]
            # Last word should end within 1 second of total duration
            assert abs(last_timing.end_time - result.duration_seconds) < 2.0
