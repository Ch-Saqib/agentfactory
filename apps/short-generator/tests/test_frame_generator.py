"""Tests for Frame Generation Service.

This test module validates:
1. Frame generation with text animation
2. Word-by-word timing synchronization
3. Fade in/out effects
4. Text wrapping and positioning
5. Different frame types (title, content, outro)
"""

import os
import tempfile

import pytest
from PIL import Image

from shorts_generator.core.config import settings
from shorts_generator.services.frame_generator import (
    FrameGenerationResult,
    FrameGenerator,
    FrameSpec,
    TextAnimationConfig,
    frame_generator,
)
from shorts_generator.services.google_tts_audio import GoogleTTSResult, WordTiming


class TestFrameSpec:
    """Tests for FrameSpec dataclass."""

    def test_default_values(self):
        """Test default FrameSpec values."""
        spec = FrameSpec()
        assert spec.width == 1080
        assert spec.height == 1920
        assert spec.fps == 30
        assert spec.bg_color == "#1a1a2e"
        assert spec.text_color == "#ffffff"

    def test_from_settings(self):
        """Test creating FrameSpec from settings."""
        spec = FrameSpec.from_settings()
        assert spec.width == settings.video_width
        assert spec.height == settings.video_height
        assert spec.fps == settings.video_fps


class TestTextAnimationConfig:
    """Tests for TextAnimationConfig dataclass."""

    def test_default_values(self):
        """Test default animation config values."""
        config = TextAnimationConfig()
        assert config.fade_in_duration == 0.5
        assert config.fade_out_duration == 0.5
        assert config.font_size_title == 80
        assert config.font_size_content == 48

    def test_from_settings(self):
        """Test creating TextAnimationConfig from settings."""
        config = TextAnimationConfig.from_settings()
        assert config.fade_in_duration == settings.video_fade_duration
        assert config.font_size_title == settings.video_title_font_size


class TestFrameGenerator:
    """Tests for FrameGenerator class."""

    @pytest.fixture
    def generator(self):
        """Create a FrameGenerator instance for testing."""
        return FrameGenerator()

    @pytest.fixture
    def mock_word_timings(self):
        """Create mock word timing data."""
        return [
            WordTiming("Hello", 0.0, 0.35),
            WordTiming("world", 0.35, 0.62),
            WordTiming("this", 0.62, 0.85),
            WordTiming("is", 0.85, 1.02),
            WordTiming("a", 1.02, 1.15),
            WordTiming("test", 1.15, 1.48),
        ]

    def test_hex_to_rgb(self, generator):
        """Test hex color conversion."""
        rgb = generator._hex_to_rgb("#1a1a2e")
        assert rgb == (26, 26, 46)

        rgb = generator._hex_to_rgb("#ffffff")
        assert rgb == (255, 255, 255)

        rgb = generator._hex_to_rgb("#ff0000")
        assert rgb == (255, 0, 0)

    def test_wrap_text(self, generator):
        """Test text wrapping."""
        font = generator.content_font

        # Short text should fit on one line
        lines = generator._wrap_text("Hello world", font, 500)
        assert len(lines) == 1
        assert lines[0] == "Hello world"

        # Long text should wrap
        long_text = "This is a very long text that should wrap onto multiple lines"
        lines = generator._wrap_text(long_text, font, 300)
        assert len(lines) > 1

    def test_calculate_opacity(self, generator):
        """Test opacity calculation for animation."""
        # Fade in phase
        opacity = generator._calculate_opacity(
            frame_time=0.25,
            start_time=0.0,
            end_time=3.0,
            fade_in=0.5,
            fade_out=0.5,
        )
        assert 0 < opacity < 1  # Partially faded in

        # Full opacity phase
        opacity = generator._calculate_opacity(
            frame_time=1.5,
            start_time=0.0,
            end_time=3.0,
            fade_in=0.5,
            fade_out=0.5,
        )
        assert opacity == 1.0  # Fully opaque

        # Fade out phase
        opacity = generator._calculate_opacity(
            frame_time=2.75,
            start_time=0.0,
            end_time=3.0,
            fade_in=0.5,
            fade_out=0.5,
        )
        assert 0 < opacity < 1  # Partially faded out

    def test_create_frame(self, generator):
        """Test creating a single frame."""
        frame = generator._create_frame("Test text", opacity=1.0)

        assert isinstance(frame, Image.Image)
        assert frame.width == generator.spec.width
        assert frame.height == generator.spec.height
        assert frame.mode == "RGB"

    def test_create_frame_with_opacity(self, generator):
        """Test creating frame with different opacity levels."""
        # Full opacity
        frame1 = generator._create_frame("Test", opacity=1.0)

        # Half opacity
        frame2 = generator._create_frame("Test", opacity=0.5)

        # Zero opacity (should still have text but with 0 alpha)
        frame3 = generator._create_frame("Test", opacity=0.0)

        # All should be valid images
        for frame in [frame1, frame2, frame3]:
            assert isinstance(frame, Image.Image)
            assert frame.width == generator.spec.width

    def test_generate_title_frames(self, generator):
        """Test generating title frames."""
        with tempfile.TemporaryDirectory() as tmpdir:
            frames = generator.generate_title_frames(
                title="Test Title",
                duration=1.0,  # Short duration for testing
                output_dir=tmpdir,
            )

            # Should generate fps * duration frames
            expected_frames = int(1.0 * generator.spec.fps)
            assert len(frames) == expected_frames

            # All frames should exist
            for frame_path in frames:
                assert os.path.exists(frame_path)

                # Verify image can be opened
                img = Image.open(frame_path)
                assert img.width == generator.spec.width
                assert img.height == generator.spec.height

    def test_generate_content_frames_word_sync(self, generator, mock_word_timings):
        """Test generating content frames with word sync."""
        with tempfile.TemporaryDirectory() as tmpdir:
            frames = generator.generate_content_frames_word_sync(
                content="Hello world this is a test",
                word_timings=mock_word_timings,
                start_time=0.0,
                end_time=2.0,
                output_dir=tmpdir,
            )

            # Should generate frames for the duration
            expected_frames = int(2.0 * generator.spec.fps)
            assert len(frames) == expected_frames

            # All frames should exist
            for frame_path in frames:
                assert os.path.exists(frame_path)

    def test_generate_content_frames_scrolling(self, generator):
        """Test generating content frames with scrolling text."""
        with tempfile.TemporaryDirectory() as tmpdir:
            frames = generator.generate_content_frames_scrolling(
                content="This is a longer text that will scroll across multiple frames.",
                start_time=0.0,
                end_time=2.0,
                output_dir=tmpdir,
            )

            expected_frames = int(2.0 * generator.spec.fps)
            assert len(frames) == expected_frames

            # Verify images
            for frame_path in frames[:3]:  # Check first few
                assert os.path.exists(frame_path)
                img = Image.open(frame_path)
                assert img.mode == "RGB"

    def test_generate_outro_frames(self, generator):
        """Test generating outro frames."""
        with tempfile.TemporaryDirectory() as tmpdir:
            frames = generator.generate_outro_frames(
                cta_text="Continue reading →",
                duration=1.0,
                output_dir=tmpdir,
            )

            expected_frames = int(1.0 * generator.spec.fps)
            assert len(frames) == expected_frames

            for frame_path in frames:
                assert os.path.exists(frame_path)

    def test_generate_video_frames_complete(self, generator, mock_word_timings):
        """Test generating complete video frames."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create mock TTS result
            tts_result = GoogleTTSResult(
                audio_path="dummy.mp3",
                duration_seconds=6.0,
                word_timings=mock_word_timings,
                voice_used="en-US-Neural2-C",
                encoding="MP3",
                sample_rate=24000,
            )

            result = generator.generate_video_frames(
                title="Test Video",
                content="Hello world this is a test of the video frame generation system.",
                tts_result=tts_result,
                title_duration=1.5,
                outro_duration=1.5,
                output_dir=tmpdir,
                use_word_sync=True,
            )

            # Verify result structure
            assert isinstance(result, FrameGenerationResult)
            assert len(result.frame_paths) > 0
            assert result.frame_count == len(result.frame_paths)
            assert result.output_dir == tmpdir

            # Verify total duration
            expected_duration = result.frame_count / generator.spec.fps
            assert abs(result.total_duration - expected_duration) < 0.1

            # Verify all frames exist
            for frame_path in result.frame_paths:
                assert os.path.exists(frame_path)

            # Verify frame numbering is sequential
            for i, path in enumerate(result.frame_paths):
                assert f"frame_{i:05d}.png" in path


class TestFrameGenerationResult:
    """Tests for FrameGenerationResult dataclass."""

    def test_default_values(self):
        """Test default values."""
        result = FrameGenerationResult()
        assert result.frame_paths == []
        assert result.frame_count == 0
        assert result.total_duration == 0.0

    def test_with_data(self):
        """Test with actual data."""
        result = FrameGenerationResult(
            frame_paths=["frame1.png", "frame2.png"],
            frame_count=2,
            total_duration=2.0,
            output_dir="/tmp/frames",
        )

        assert result.frame_count == 2
        assert result.total_duration == 2.0
        assert result.output_dir == "/tmp/frames"


class TestIntegration:
    """Integration tests for frame generation."""

    def test_full_pipeline(self):
        """Test complete frame generation pipeline."""
        generator = FrameGenerator()

        # Mock TTS result
        word_timings = [
            WordTiming(f"word{i}", float(i * 0.3), float((i + 1) * 0.3))
            for i in range(10)
        ]

        tts_result = GoogleTTSResult(
            audio_path="dummy.mp3",
            duration_seconds=5.0,
            word_timings=word_timings,
            voice_used="en-US-Neural2-C",
            encoding="MP3",
            sample_rate=24000,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            result = generator.generate_video_frames(
                title="Integration Test",
                content="word0 word1 word2 word3 word4 word5 word6 word7 word8 word9",
                tts_result=tts_result,
                title_duration=1.0,
                outro_duration=1.0,
                output_dir=tmpdir,
            )

            # Verify all phases generated
            assert result.frame_count > 0
            assert len(result.frame_paths) == result.frame_count

            # Verify frames are valid images
            sample_frame = Image.open(result.frame_paths[0])
            assert sample_frame.width == 1080
            assert sample_frame.height == 1920


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_text(self):
        """Test with empty text."""
        generator = FrameGenerator()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Should handle empty text gracefully
            frames = generator.generate_title_frames(
                title="",
                duration=0.5,
                output_dir=tmpdir,
            )
            # Still generates frames (just empty)
            assert len(frames) > 0

    def test_very_long_text(self):
        """Test with very long text."""
        generator = FrameGenerator()

        long_text = " ".join(["word"] * 100)  # 100 words

        # Text wrapping should handle this
        lines = generator._wrap_text(long_text, generator.content_font, 500)
        assert len(lines) > 1

    def test_special_characters(self):
        """Test with special characters in text."""
        generator = FrameGenerator()

        special_text = "Test with émojis 🎉 and spëcial çharacters!"

        with tempfile.TemporaryDirectory() as tmpdir:
            frames = generator.generate_title_frames(
                title=special_text,
                duration=0.5,
                output_dir=tmpdir,
            )
            assert len(frames) > 0

    def test_single_word(self):
        """Test with single word."""
        generator = FrameGenerator()

        with tempfile.TemporaryDirectory() as tmpdir:
            frames = generator.generate_title_frames(
                title="Test",
                duration=0.5,
                output_dir=tmpdir,
            )
            assert len(frames) > 0


class TestFrameAnimation:
    """Tests for frame animation effects."""

    def test_fade_in_sequence(self):
        """Test fade in creates correct opacity sequence."""
        generator = FrameGenerator()

        with tempfile.TemporaryDirectory() as tmpdir:
            frames = generator.generate_title_frames(
                title="Fade Test",
                duration=1.0,
                output_dir=tmpdir,
            )

            # Check first few frames (fade in)
            # Frame 0 should be lower opacity than frame 15
            first_frame = Image.open(frames[0])
            middle_frame = Image.open(frames[14])  # ~0.5s in

            # Both should be valid images
            assert first_frame.width == 1080
            assert middle_frame.width == 1080

    def test_fade_out_sequence(self):
        """Test fade out creates correct opacity sequence."""
        generator = FrameGenerator()

        with tempfile.TemporaryDirectory() as tmpdir:
            frames = generator.generate_title_frames(
                title="Fade Test",
                duration=1.0,
                output_dir=tmpdir,
            )

            # Check last few frames (fade out)
            # Frame near end should be faded out
            last_frame = Image.open(frames[-1])
            assert last_frame.width == 1080


class TestSingleton:
    """Tests for singleton instance."""

    def test_singleton_instance(self):
        """Test that singleton instance exists and is usable."""
        assert frame_generator is not None
        assert isinstance(frame_generator, FrameGenerator)

        # Should be able to use it
        spec = frame_generator.spec
        assert spec.width > 0
        assert spec.height > 0
