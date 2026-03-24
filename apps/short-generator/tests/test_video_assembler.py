"""Tests for video assembler service."""

from unittest.mock import MagicMock, patch

import pytest

from shorts_generator.services.audio_generator import GeneratedAudio
from shorts_generator.services.script_generator import GeneratedScript, ScriptScene
from shorts_generator.services.video_assembler import (
    AssembledVideo,
    VideoAssembler,
)


@pytest.fixture
def assembler():
    """Create a video assembler instance."""
    return VideoAssembler()


@pytest.fixture
def sample_script():
    """Create a sample script for testing."""
    return GeneratedScript(
        lesson_path="test.md",
        lesson_title="Test Video",
        hook=ScriptScene("Hook text", "Visual", 5, "hook"),
        concepts=[
            ScriptScene("Concept 1", "Visual", 15, "concept"),
            ScriptScene("Concept 2", "Visual", 10, "concept"),
        ],
        example=ScriptScene("Example", "Visual", 20, "example"),
        cta=ScriptScene("CTA", "Visual", 10, "cta"),
        total_duration=60,
        model_used="gemini-2.0-flash-exp",
    )


def test_estimate_bitrate_assembler(assembler):
    """Test bitrate estimation for file size constraints."""
    # 60 seconds at 50MB target
    bitrate = assembler._estimate_bitrate(60, 50)
    assert "M" in bitrate or "k" in bitrate

    # Longer duration with same size = lower bitrate
    bitrate_2min = assembler._estimate_bitrate(120, 50)
    # Should be lower bitrate (half the duration)
    # Extract number from bitrate string
    if "M" in bitrate:
        base_bitrate = int(bitrate.replace("M", ""))
    else:
        base_bitrate = int(bitrate.replace("k", "")) / 1000

    if "M" in bitrate_2min:
        new_bitrate = int(bitrate_2min.replace("M", ""))
    else:
        new_bitrate = int(bitrate_2min.replace("k", "")) / 1000

    assert new_bitrate <= base_bitrate


def test_calculate_video_size(assembler):
    """Test video file size estimation."""
    # 60 seconds at 2Mbps
    size = assembler._calculate_video_size(60, 2000)

    # Should be around 14-15MB (2Mbps * 60s / 8 / 1024 / 1024 + 10%)
    assert 10 < size < 20  # Reasonable range


def test_video_specifications():
    """Test that video specifications match requirements."""
    assert VideoAssembler.VIDEO_WIDTH == 1080
    assert VideoAssembler.VIDEO_HEIGHT == 1920
    assert VideoAssembler.VIDEO_FPS == 30
    assert VideoAssembler.VIDEO_CODEC == "libx264"
    assert VideoAssembler.AUDIO_CODEC == "aac"
    assert VideoAssembler.MAX_FILE_SIZE_MB == 50


@pytest.mark.asyncio
async def test_assemble_video_creates_video(assembler, sample_script):
    """Test that assemble_video creates a video file."""
    scene_images = ["file:///path/to/image1.jpg", "file:///path/to/image2.jpg"]
    audio = GeneratedAudio(
        url="file:///path/to/audio.mp3",
        duration_seconds=60.0,
        file_path="/path/to/audio.mp3",
        generation_method="edge_tts",
        voice_used="en-US-AriaNeural",
    )
    captions = "1\n00:00:00,000 --> 00:00:05,000\nHook text\n\n2\n00:00:05,000 --> 00:00:20,000\nConcept text"

    with patch("shorts_generator.services.video_assembler.ffmpeg") as mock_ffmpeg:
        mock_probe = MagicMock()
        mock_probe.format = {"duration": "60.0"}
        mock_ffmpeg.probe = MagicMock(return_value=mock_probe)

        mock_input = MagicMock()
        mock_input.output = MagicMock(return_value=mock_input)
        mock_input.filter_ = MagicMock()
        mock_ffmpeg.input = MagicMock(return_value=mock_input)

        mock_ffmpeg.output = MagicMock()
        mock_output = MagicMock()
        mock_output.overwrite_output = MagicMock()
        mock_ffmpeg.output.return_value = mock_output

        mock_run = MagicMock()
        mock_run.capture_stdout = True
        mock_run.capture_stderr = True
        mock_output.run = mock_run

        with patch.object(assembler, "_generate_thumbnail", return_value="file:///thumbnail.jpg"):
            # Create mock file for testing
            import tempfile

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as mock_audio:
                mock_audio.file_path = mock_audio.name

                with patch.object(assembler, "os") as mock_os:
                    mock_os.path.getsize = MagicMock(return_value=5 * 1024 * 1024)  # 5MB

                    video = await assembler.assemble_video(
                        scene_images=scene_images,
                        audio=audio,
                        script=sample_script,
                        captions=captions,
                    )

                    assert video.file_path.endswith(".mp3")
                    assert video.url == video.file_path
                    assert video.width == 1080
                    assert video.height == 1920
                    assert video.duration_seconds == 60
                    assert 0 < video.file_size_mb < 10  # Should be ~5MB


@pytest.mark.asyncio
async def test_generate_thumbnail(assembler):
    """Test thumbnail generation from first scene image."""
    image_url = "file:///path/to/image.jpg"

    with patch("shorts_generator.services.video_assembler.ffmpeg") as mock_ffmpeg:
        mock_input = MagicMock()
        mock_output = MagicMock()
        mock_output.overwrite_output = MagicMock()
        mock_ffmpeg.input = MagicMock(return_value=mock_input)
        mock_ffmpeg.input.return_value = mock_input

        thumbnail_url = await assembler._generate_thumbnail(image_url)

        assert "thumbnail" in thumbnail_url or image_url in thumbnail_url


@pytest.mark.asyncio
async def test_optimize_for_web(assembler):
    """Test video optimization for web delivery."""
    # Create a mock video file for testing
    import tempfile

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_video:
        tmp_video.write(b"MOCK_VIDEO_DATA")
        tmp_video.flush()

        with patch("shorts_generator.services.video_assembler.ffmpeg") as mock_ffmpeg:
            mock_probe = MagicMock()
            mock_probe.format = {"duration": "60.0"}
            mock_ffmpeg.probe = MagicMock(return_value=mock_probe)

            mock_input = MagicMock()
            mock_output = MagicMock()
            mock_output.overwrite_output = MagicMock()
            mock_ffmpeg.input = MagicMock(return_value=mock_input)
            mock_ffmpeg.input.return_value = mock_input

            mock_run = MagicMock()
            mock_output.run = mock_run
            mock_ffmpeg.output.return_value = mock_output

            optimized_path = assembler.optimize_for_web(tmp_video.name, target_size_mb=30)

            assert optimized_path.endswith(".mp3")


def test_assembled_video_dataclass():
    """Test AssembledVideo dataclass."""
    video = AssembledVideo(
        file_path="/path/to/video.mp4",
        url="https://cdn.example.com/video.mp4",
        duration_seconds=60.0,
        file_size_mb=15.5,
        width=1080,
        height=1920,
        thumbnail_url="https://cdn.example.com/thumb.jpg",
    )

    assert video.file_path == "/path/to/video.mp4"
    assert video.url == "https://cdn.example.com/video.mp4"
    assert video.duration_seconds == 60.0
    assert video.file_size_mb == 15.5
    assert video.width == 1080
    assert video.height == 1920


@pytest.mark.asyncio
async def test_assemble_video_handles_ffmpeg_error(assembler, sample_script):
    """Test that FFmpeg errors are handled correctly."""
    scene_images = ["file:///path/to/image.jpg"]
    audio = GeneratedAudio(
        url="file:///path/to/audio.mp3",
        duration_seconds=60.0,
        file_path="/path/to/audio.mp3",
        generation_method="edge_tts",
        voice_used="en-US-AriaNeural",
    )
    captions = "1\n00:00:00,000 --> 00:00:05,000\nCaption text"

    with patch("shorts_generator.services.video_assembler.ffmpeg") as mock_ffmpeg:
        # Make FFmpeg raise an exception
        mock_ffmpeg.input.side_effect = Exception("FFmpeg error")

        with pytest.raises(Exception, match="Video assembly failed"):
            await assembler.assemble_video(
                scene_images=scene_images,
                audio=audio,
                script=sample_script,
                captions=captions,
            )


def test_estimate_bitrate_min_size(assembler):
    """Test bitrate estimation handles minimum file size."""
    # Very short video (5 seconds) with 50MB limit
    bitrate = assembler._estimate_bitrate(5, 50)

    # Should produce high bitrate for short video
    assert "M" in bitrate or "k" in bitrate


def test_estimate_bitrate_long_video(assembler):
    """Test bitrate estimation for long videos."""
    # 3 minute video with 50MB limit
    bitrate = assembler._estimate_bitrate(180, 50)

    # Should produce lower bitrate for long video
    assert "k" in bitrate or bitrate.startswith("0")


@pytest.mark.asyncio
async def test_assemble_video_from_assets(assembler, sample_script):
    """Test assembling video from pre-generated assets."""
    assets = {
        "scene_images": ["file:///scene1.jpg", "file:///scene2.jpg"],
        "audio_path": "file:///audio.mp3",
        "captions": "1\n00:00:00,000 --> 00:00:05,000\nCaption",
    }

    with patch("shorts_generator.services.video_assembler.ffmpeg") as mock_ffmpeg:
        mock_probe = MagicMock()
        mock_probe.format = {"duration": "60.0"}
        mock_ffmpeg.probe = MagicMock(return_value=mock_probe)

        mock_input = MagicMock()
        mock_output = MagicMock()
        mock_output.overwrite_output = MagicMock()
        mock_ffmpeg.input = MagicMock(return_value=mock_input)
        mock_ffmpeg.input.return_value = mock_input

        mock_run = MagicMock()
        mock_output.run = mock_run
        mock_ffmpeg.output.return_value = mock_output

        with patch.object(assembler, "_generate_thumbnail", return_value="file:///thumb.jpg"):
            import tempfile

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as mock_audio:
                # Create mock audio file
                with patch("shorts_generator.services.audio_generator.GeneratedAudio") as mock_audio_cls:
                    # We need to skip the actual audio generation
                    pass

                video = await assembler.assemble_video_from_assets(assets, sample_script)

                assert video.width == 1080
                assert video.height == 1920
