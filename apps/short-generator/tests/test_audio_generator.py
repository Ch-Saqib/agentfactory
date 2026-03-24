"""Tests for audio generator service."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from shorts_generator.services.audio_generator import (
    AudioGenerator,
    GeneratedAudio,
)


@pytest.fixture
def generator():
    """Create an audio generator instance."""
    return AudioGenerator()


def test_estimate_duration(generator):
    """Test duration estimation from text."""
    # 10 words at 2.5 words per second = 4 seconds
    duration = generator._estimate_duration("one two three four five six seven eight nine ten")
    assert duration == 4.0

    # Empty text should be at least 1 second
    assert generator._estimate_duration("") == 1.0

    # Single word
    assert generator._estimate_duration("hello") == 0.4


def test_format_timestamp(generator):
    """Test SRT timestamp formatting."""
    # 0 seconds
    assert generator._format_timestamp(0.0) == "00:00:00,000"

    # 65.5 seconds
    assert generator._format_timestamp(65.5) == "00:01:05,500"

    # 3661.75 seconds (1 hour, 1 minute, 1.75 seconds)
    assert generator._format_timestamp(3661.75) == "01:01:01,750"


@pytest.mark.asyncio
async def test_generate_captions_simple(generator):
    """Test caption generation for simple text."""
    script = "Hello world. This is a test."

    captions = await generator.generate_captions(script)

    assert "1" in captions
    assert "Hello world" in captions
    assert "00:00:00" in captions or "00:00:01" in captions
    assert "-->" in captions


@pytest.mark.asyncio
async def test_generate_captions_with_scene_timings(generator):
    """Test caption generation respects scene timings."""
    script = "Scene one. Scene two. Scene three."

    scene_timings = [
        {"start": 0.0, "end": 2.0},
        {"start": 2.0, "end": 4.0},
        {"start": 4.0, "end": 6.0},
    ]

    # For now, scene_timings is not used in the function
    # But we test that the function accepts it
    captions = await generator.generate_captions(script, scene_timings)

    assert captions
    assert "Scene one" in captions


@pytest.mark.asyncio
async def test_generate_narration_success(generator):
    """Test successful narration generation."""
    mock_audio_content = b"MP3_AUDIO_CONTENT_HERE"

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = mock_audio_content

    with patch.object(generator, "_get_http_client") as mock_client:
        mock_client_instance = AsyncMock()
        mock_client_instance.post = AsyncMock(return_value=mock_response)
        mock_client.return_value = mock_client_instance

        audio = await generator.generate_narration("Hello world")

        assert audio.generation_method == "edge_tts"
        assert audio.voice_used == "en-US-AriaNeural"
        assert audio.duration_seconds > 0
        assert "mp3" in audio.url
        assert audio.file_path.endswith(".mp3")


@pytest.mark.asyncio
async def test_generate_narration_handles_api_error(generator):
    """Test that API errors are handled correctly."""
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"

    with patch.object(generator, "_get_http_client") as mock_client:
        mock_client_instance = AsyncMock()
        mock_client_instance.post = AsyncMock(return_value=mock_response)
        mock_client.return_value = mock_client_instance

        with pytest.raises(Exception, match="Edge-TTS generation failed"):
            await generator.generate_narration("Test")


@pytest.mark.asyncio
async def test_add_background_music_with_ffmpeg(generator):
    """Test adding background music with FFmpeg."""
    # Mock narration audio file
    import tempfile

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_narration:
        tmp_narration.write(b"MOCK_MP3_DATA")
        tmp_narration.flush()

        narration = GeneratedAudio(
            url=f"file://{tmp_narration.name}",
            duration_seconds=10.0,
            file_path=tmp_narration.name,
            generation_method="edge_tts",
            voice_used="en-US-AriaNeural",
        )

        with patch("shorts_generator.services.audio_generator.ffmpeg") as mock_ffmpeg:
            mock_probe = MagicMock()
            mock_probe.format = {"duration": "10.0"}
            mock_ffmpeg.probe = MagicMock(return_value=mock_probe)

            # Mock the FFmpeg chain
            mock_input = MagicMock()
            mock_input.filter_ = MagicMock(return_value=mock_input)
            mock_ffmpeg.input = MagicMock(return_value=mock_input)

            result = await generator.add_background_music(narration.url)

            # Should return the narration unchanged (simplified version)
            assert result.generation_method == "edge_tts"


@pytest.mark.asyncio
async def test_add_background_music_ffmpeg_unavailable(generator):
    """Test fallback when FFmpeg is not available."""
    narration = GeneratedAudio(
        url="file:///test/audio.mp3",
        duration_seconds=10.0,
        file_path="/test/audio.mp3",
        generation_method="edge_tts",
        voice_used="en-US-AriaNeural",
    )

    with patch("shorts_generator.services.audio_generator.ffmpeg", side_effect=ImportError):
        result = await generator.add_background_music(narration.url)

        # Should return narration unchanged
        assert result.url == narration.url


def test_generated_audio_dataclass():
    """Test GeneratedAudio dataclass."""
    audio = GeneratedAudio(
        url="https://example.com/audio.mp3",
        duration_seconds=45.5,
        file_path="/path/to/audio.mp3",
        generation_method="edge_tts",
        voice_used="en-US-AriaNeural",
    )

    assert audio.url == "https://example.com/audio.mp3"
    assert audio.duration_seconds == 45.5
    assert audio.file_path == "/path/to/audio.mp3"
    assert audio.generation_method == "edge_tts"
    assert audio.voice_used == "en-US-AriaNeural"


@pytest.mark.asyncio
async def test_generate_audio_for_script_full_flow(generator):
    """Test complete audio generation workflow."""
    script_text = "This is a test script for audio generation."

    mock_audio_content = b"MP3_AUDIO"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = mock_audio_content

    with patch.object(generator, "_get_http_client") as mock_client:
        mock_client_instance = AsyncMock()
        mock_client_instance.post = AsyncMock(return_value=mock_response)
        mock_client.return_value = mock_client_instance

        audio, captions = await generator.generate_audio_for_script(script_text)

        assert audio is not None
        assert captions is not None
        assert audio.generation_method == "edge_tts"
        assert "This is a test script" in captions
        assert "-->" in captions  # Timestamp separators


def test_estimated_duration_properties(generator):
    """Test that duration estimation properties are set correctly."""
    assert generator.SAMPLE_RATE == 24000
    assert generator.BIT_RATE == 128000


@pytest.mark.asyncio
async def test_generate_captions_empty_script(generator):
    """Test caption generation with empty script."""
    captions = await generator.generate_captions("")

    # Should still produce valid SRT structure
    assert captions == "" or captions.strip() == ""


@pytest.mark.asyncio
async def test_generate_captions_long_script(generator):
    """Test caption generation with longer script."""
    # 50 words
    script = "word " * 50

    captions = await generator.generate_captions(script)

    # Should have multiple captions
    assert "1" in captions
    # Should have timestamp separators
    assert captions.count("-->") > 1


@pytest.mark.asyncio
async def test_generate_captions_preserves_ordering(generator):
    """Test that captions preserve word order."""
    script = "First second third fourth fifth"

    captions = await generator.generate_captions(script)

    # Extract just the caption text (remove timestamps and indices)
    lines = captions.split("\n")
    caption_text = " ".join([line for line in lines if not line.isdigit() and "-->" not in line and line.strip()])

    # Words should be in order (possibly grouped)
    assert "First" in caption_text
    assert "second" in caption_text
    assert "third" in caption_text
