"""Frame Generation Service for Video Production.

This service generates video frames with text animation:
- Title screens with fade effects
- Content screens with word-by-word timing sync
- Outro/end screens
- Smooth fade in/out animations
- 9:16 aspect ratio (1080x1920) for vertical videos
"""

import logging
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from shorts_generator.core.config import settings
from shorts_generator.services.google_tts_audio import GoogleTTSResult, WordTiming

logger = logging.getLogger(__name__)


@dataclass
class FrameSpec:
    """Specifications for video frame generation.

    Attributes:
        width: Frame width in pixels (default: 1080)
        height: Frame height in pixels (default: 1920)
        fps: Frames per second (default: 30)
        bg_color: Background color (hex format)
        text_color: Text color (hex format)
        accent_color: Accent color (hex format)
    """

    width: int = 1080
    height: int = 1920
    fps: int = 30
    bg_color: str = "#1a1a2e"
    text_color: str = "#ffffff"
    accent_color: str = "#0f3460"

    @classmethod
    def from_settings(cls) -> "FrameSpec":
        """Create FrameSpec from application settings."""
        return cls(
            width=settings.video_width,
            height=settings.video_height,
            fps=settings.video_fps,
            bg_color=settings.video_bg_color,
            text_color=settings.video_text_color,
            accent_color=settings.video_accent_color,
        )


@dataclass
class TextAnimationConfig:
    """Configuration for text animation.

    Attributes:
        fade_in_duration: Fade in duration in seconds
        fade_out_duration: Fade out duration in seconds
        hold_duration: Hold duration in seconds (0 = use remaining time)
        font_size_title: Font size for titles
        font_size_content: Font size for content
        max_line_width: Maximum line width in pixels
        line_spacing: Line spacing multiplier
    """

    fade_in_duration: float = 0.5
    fade_out_duration: float = 0.5
    hold_duration: float = 0.0
    font_size_title: int = 80
    font_size_content: int = 48
    max_line_width: int = 980
    line_spacing: float = 1.5

    @classmethod
    def from_settings(cls) -> "TextAnimationConfig":
        """Create TextAnimationConfig from application settings."""
        return cls(
            fade_in_duration=settings.video_fade_duration,
            fade_out_duration=settings.video_fade_duration,
            font_size_title=settings.video_title_font_size,
            font_size_content=settings.video_content_font_size,
            max_line_width=settings.video_max_line_width,
            line_spacing=settings.video_line_spacing,
        )


@dataclass
class FrameGenerationResult:
    """Result of frame generation.

    Attributes:
        frame_paths: List of paths to generated frame images
        frame_count: Total number of frames generated
        total_duration: Total duration in seconds
        output_dir: Directory containing frames
    """

    frame_paths: list[str] = field(default_factory=list)
    frame_count: int = 0
    total_duration: float = 0.0
    output_dir: str = ""


class FrameGenerator:
    """Generates video frames with text animation.

    Features:
    - Title screens with fade in/out
    - Content screens with word-by-word timing
    - Outro screens
    - Configurable colors and fonts
    - Text wrapping and positioning
    """

    # Default animation timeline (for 60-second video)
    # Title: 0-3s
    # Content: 3-54s
    # Outro: 54-60s

    def __init__(
        self,
        spec: FrameSpec | None = None,
        animation_config: TextAnimationConfig | None = None,
    ):
        """Initialize the frame generator.

        Args:
            spec: Frame specifications (default: from settings)
            animation_config: Animation configuration (default: from settings)
        """
        self.spec = spec or FrameSpec.from_settings()
        self.animation_config = animation_config or TextAnimationConfig.from_settings()

        # Load fonts
        self._title_font: ImageFont.FreeTypeFont | ImageFont.ImageFont | None = None
        self._content_font: ImageFont.FreeTypeFont | ImageFont.ImageFont | None = None

    def _get_font(self, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
        """Get font of specified size.

        Args:
            size: Font size in points

        Returns:
            PIL ImageFont object
        """
        # Try custom font path from settings
        if settings.video_font_path and os.path.exists(settings.video_font_path):
            try:
                return ImageFont.truetype(settings.video_font_path, size)
            except Exception as e:
                logger.warning(f"Failed to load custom font: {e}")

        # Try system fonts (common fonts for video subtitles)
        font_candidates = [
            # Linux
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
            # macOS
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/SFNSDisplay.ttf",
            # Windows
            "C:\\Windows\\Fonts\\arialbd.ttf",
            "C:\\Windows\\Fonts\\arial.ttf",
        ]

        for font_path in font_candidates:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, size)
                except Exception:
                    continue

        # Fallback to default font
        logger.warning("Using default PIL font - text may not render optimally")
        return ImageFont.load_default()

    @property
    def title_font(self) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
        """Get title font."""
        if self._title_font is None:
            self._title_font = self._get_font(self.animation_config.font_size_title)
        return self._title_font

    @property
    def content_font(self) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
        """Get content font."""
        if self._content_font is None:
            self._content_font = self._get_font(self.animation_config.font_size_content)
        return self._content_font

    def _hex_to_rgb(self, hex_color: str) -> tuple[int, int, int]:
        """Convert hex color to RGB tuple.

        Args:
            hex_color: Hex color string (e.g., "#1a1a2e")

        Returns:
            RGB tuple
        """
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

    def _wrap_text(
        self,
        text: str,
        font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
        max_width: int,
    ) -> list[str]:
        """Wrap text to fit within max width.

        Args:
            text: Text to wrap
            font: Font to use for measurement
            max_width: Maximum width in pixels

        Returns:
            List of lines
        """
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = " ".join(current_line + [word])
            bbox = ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]

            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]

        if current_line:
            lines.append(" ".join(current_line))

        return lines

    def _calculate_text_position(
        self,
        text_lines: list[str],
        font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
        vertical_offset: int = 0,
    ) -> tuple[int, int]:
        """Calculate centered text position.

        Args:
            text_lines: List of text lines
            font: Font to use for measurement
            vertical_offset: Vertical offset from center (pixels)

        Returns:
            (x, y) position tuple
        """
        # Calculate total text height
        line_height = int(font.size * self.animation_config.line_spacing)
        total_height = len(text_lines) * line_height

        # Center position
        x = (self.spec.width - self.animation_config.max_line_width) // 2
        y = (self.spec.height - total_height) // 2 + vertical_offset

        return (x, y)

    def _create_frame(
        self,
        text: str,
        opacity: float = 1.0,
        font: ImageFont.FreeTypeFont | ImageFont.ImageFont | None = None,
        vertical_offset: int = 0,
        background_color: str | None = None,
    ) -> Image.Image:
        """Create a single frame with text.

        Args:
            text: Text to render
            opacity: Opacity (0.0 to 1.0)
            font: Font to use (default: content font)
            vertical_offset: Vertical offset from center
            background_color: Background color override

        Returns:
            PIL Image object
        """
        font = font or self.content_font
        bg_color = background_color or self.spec.bg_color

        # Create base image
        img = Image.new("RGB", (self.spec.width, self.spec.height), color=bg_color)
        draw = ImageDraw.Draw(img, "RGBA")

        # Wrap text
        lines = self._wrap_text(text, font, self.animation_config.max_line_width)

        # Calculate position
        x, y = self._calculate_text_position(lines, font, vertical_offset)

        # Calculate text color with opacity
        r, g, b = self._hex_to_rgb(self.spec.text_color)
        text_color = (r, g, b, int(255 * opacity))

        # Draw each line
        line_height = int(font.size * self.animation_config.line_spacing)
        for i, line in enumerate(lines):
            line_y = y + (i * line_height)
            draw.text((x, line_y), line, font=font, fill=text_color)

        return img

    def _calculate_opacity(
        self,
        frame_time: float,
        start_time: float,
        end_time: float,
        fade_in: float = 0.5,
        fade_out: float = 0.5,
    ) -> float:
        """Calculate opacity for a frame based on timing.

        Args:
            frame_time: Current frame time in seconds
            start_time: Animation start time in seconds
            end_time: Animation end time in seconds
            fade_in: Fade in duration
            fade_out: Fade out duration

        Returns:
            Opacity value (0.0 to 1.0)
        """
        relative_time = frame_time - start_time
        total_duration = end_time - start_time

        # Fade in
        if relative_time < fade_in:
            return relative_time / fade_in

        # Fade out
        if relative_time > (total_duration - fade_out):
            return max(0, 1.0 - ((relative_time - (total_duration - fade_out)) / fade_out))

        # Full opacity
        return 1.0

    def generate_title_frames(
        self,
        title: str,
        duration: float = 3.0,
        output_dir: str | None = None,
        frame_offset: int = 0,
    ) -> list[str]:
        """Generate title frames with fade in/out.

        Args:
            title: Title text to display
            duration: Duration in seconds
            output_dir: Output directory for frames
            frame_offset: Starting frame number

        Returns:
            List of frame file paths
        """
        if output_dir is None:
            output_dir = tempfile.mkdtemp()

        Path(output_dir).mkdir(parents=True, exist_ok=True)

        frame_paths = []
        frame_count = int(duration * self.spec.fps)

        for frame_num in range(frame_count):
            frame_time = frame_num / self.spec.fps

            # Calculate opacity
            opacity = self._calculate_opacity(
                frame_time,
                0.0,
                duration,
                self.animation_config.fade_in_duration,
                self.animation_config.fade_out_duration,
            )

            # Create frame
            frame = self._create_frame(title, opacity=opacity, font=self.title_font)

            # Save frame
            frame_path = os.path.join(output_dir, f"frame_{frame_offset + frame_num:05d}.png")
            frame.save(frame_path)
            frame_paths.append(frame_path)

        logger.info(f"Generated {len(frame_paths)} title frames")
        return frame_paths

    def generate_content_frames_word_sync(
        self,
        content: str,
        word_timings: list[WordTiming],
        start_time: float,
        end_time: float,
        output_dir: str | None = None,
        frame_offset: int = 0,
    ) -> list[str]:
        """Generate content frames with word-by-word timing synchronization.

        This creates frames that display words as they're spoken in the audio,
        based on the word-level timing data from Google Cloud TTS.

        Args:
            content: Full content text
            word_timings: Word timing data from TTS
            start_time: When content starts (seconds)
            end_time: When content ends (seconds)
            output_dir: Output directory for frames
            frame_offset: Starting frame number

        Returns:
            List of frame file paths
        """
        if output_dir is None:
            output_dir = tempfile.mkdtemp()

        Path(output_dir).mkdir(parents=True, exist_ok=True)

        frame_paths = []
        duration = end_time - start_time
        frame_count = int(duration * self.spec.fps)

        # Build word timing lookup
        words_to_display: list[tuple[float, float, str]] = []  # (start, end, word)
        for timing in word_timings:
            words_to_display.append((timing.start_time, timing.end_time, timing.word))

        for frame_num in range(frame_count):
            frame_time = start_time + (frame_num / self.spec.fps)

            # Find which words should be displayed at this time
            displayed_words = []
            for word_start, word_end, word in words_to_display:
                if word_start <= frame_time < word_end:
                    displayed_words.append(word)
                elif frame_time >= word_end and len(displayed_words) < 50:
                    # Show recent words (karaoke style)
                    displayed_words.append(word)

            # Build display text
            display_text = " ".join(displayed_words[-15:])  # Show last 15 words

            # Create frame with fade effect
            opacity = self._calculate_opacity(
                frame_time,
                start_time,
                end_time,
                self.animation_config.fade_in_duration,
                self.animation_config.fade_out_duration,
            )

            frame = self._create_frame(display_text, opacity=opacity)

            # Save frame
            frame_path = os.path.join(output_dir, f"frame_{frame_offset + frame_num:05d}.png")
            frame.save(frame_path)
            frame_paths.append(frame_path)

        logger.info(f"Generated {len(frame_paths)} content frames (word sync)")
        return frame_paths

    def generate_content_frames_scrolling(
        self,
        content: str,
        start_time: float,
        end_time: float,
        output_dir: str | None = None,
        frame_offset: int = 0,
    ) -> list[str]:
        """Generate content frames with scrolling text.

        Alternative to word sync - displays full content scrolling upward.

        Args:
            content: Content text to scroll
            start_time: When content starts (seconds)
            end_time: When content ends (seconds)
            output_dir: Output directory for frames
            frame_offset: Starting frame number

        Returns:
            List of frame file paths
        """
        if output_dir is None:
            output_dir = tempfile.mkdtemp()

        Path(output_dir).mkdir(parents=True, exist_ok=True)

        frame_paths = []
        duration = end_time - start_time
        frame_count = int(duration * self.spec.fps)

        # Wrap text into lines
        lines = self._wrap_text(content, self.content_font, self.animation_config.max_line_width)

        # Calculate scroll parameters
        line_height = int(self.content_font.size * self.animation_config.line_spacing)
        max_lines = (self.spec.height - 200) // line_height  # Leave margin

        for frame_num in range(frame_count):
            frame_time = start_time + (frame_num / self.spec.fps)
            progress = (frame_time - start_time) / duration

            # Calculate which lines to show
            total_lines = len(lines)
            start_line = int(progress * (total_lines - max_lines))
            start_line = max(0, min(start_line, total_lines - max_lines))
            end_line = min(start_line + max_lines, total_lines)

            visible_lines = lines[start_line:end_line]
            display_text = "\n".join(visible_lines)

            # Calculate opacity
            opacity = self._calculate_opacity(
                frame_time,
                start_time,
                end_time,
                self.animation_config.fade_in_duration,
                self.animation_config.fade_out_duration,
            )

            # Create frame with multiline text
            frame = self._create_multiline_frame(display_text, opacity=opacity)

            # Save frame
            frame_path = os.path.join(output_dir, f"frame_{frame_offset + frame_num:05d}.png")
            frame.save(frame_path)
            frame_paths.append(frame_path)

        logger.info(f"Generated {len(frame_paths)} content frames (scrolling)")
        return frame_paths

    def _create_multiline_frame(
        self,
        text: str,
        opacity: float = 1.0,
        font: ImageFont.FreeTypeFont | ImageFont.ImageFont | None = None,
    ) -> Image.Image:
        """Create frame with multiline text.

        Args:
            text: Multiline text
            opacity: Opacity (0.0 to 1.0)
            font: Font to use

        Returns:
            PIL Image object
        """
        font = font or self.content_font

        # Create base image
        img = Image.new("RGB", (self.spec.width, self.spec.height), color=self.spec.bg_color)
        draw = ImageDraw.Draw(img, "RGBA")

        # Calculate text color with opacity
        r, g, b = self._hex_to_rgb(self.spec.text_color)
        text_color = (r, g, b, int(255 * opacity))

        # Draw each line
        lines = text.split("\n")
        line_height = int(font.size * self.animation_config.line_spacing)
        total_height = len(lines) * line_height

        # Center vertically
        y = (self.spec.height - total_height) // 2

        for line in lines:
            # Center horizontally
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            x = (self.spec.width - line_width) // 2

            draw.text((x, y), line, font=font, fill=text_color)
            y += line_height

        return img

    def generate_outro_frames(
        self,
        cta_text: str = "Continue reading on our website →",
        duration: float = 3.0,
        output_dir: str | None = None,
        frame_offset: int = 0,
    ) -> list[str]:
        """Generate outro/end screen frames.

        Args:
            cta_text: Call-to-action text
            duration: Duration in seconds
            output_dir: Output directory for frames
            frame_offset: Starting frame number

        Returns:
            List of frame file paths
        """
        if output_dir is None:
            output_dir = tempfile.mkdtemp()

        Path(output_dir).mkdir(parents=True, exist_ok=True)

        frame_paths = []
        frame_count = int(duration * self.spec.fps)

        for frame_num in range(frame_count):
            frame_time = frame_num / self.spec.fps

            # Calculate opacity (fade out at end)
            opacity = self._calculate_opacity(
                frame_time,
                0.0,
                duration,
                self.animation_config.fade_in_duration,
                self.animation_config.fade_out_duration,
            )

            # Create frame
            frame = self._create_frame(cta_text, opacity=opacity, font=self.title_font)

            # Save frame
            frame_path = os.path.join(output_dir, f"frame_{frame_offset + frame_num:05d}.png")
            frame.save(frame_path)
            frame_paths.append(frame_path)

        logger.info(f"Generated {len(frame_paths)} outro frames")
        return frame_paths

    def generate_video_frames(
        self,
        title: str,
        content: str,
        tts_result: GoogleTTSResult,
        title_duration: float = 3.0,
        outro_duration: float = 3.0,
        output_dir: str | None = None,
        use_word_sync: bool = True,
    ) -> FrameGenerationResult:
        """Generate all frames for a complete video.

        Args:
            title: Video title
            content: Content text
            tts_result: TTS result with timing data
            title_duration: Title screen duration
            outro_duration: Outro screen duration
            output_dir: Output directory for frames
            use_word_sync: Use word-by-word sync (True) or scrolling (False)

        Returns:
            FrameGenerationResult with all frame paths
        """
        if output_dir is None:
            output_dir = tempfile.mkdtemp()

        Path(output_dir).mkdir(parents=True, exist_ok=True)

        all_frames = []
        frame_offset = 0

        # Phase 1: Title (0 to title_duration)
        logger.info("Generating title frames...")
        title_frames = self.generate_title_frames(
            title,
            duration=title_duration,
            output_dir=output_dir,
            frame_offset=frame_offset,
        )
        all_frames.extend(title_frames)
        frame_offset += len(title_frames)

        # Phase 2: Content (title_duration to total - outro_duration)
        content_start = title_duration
        content_end = tts_result.duration_seconds - outro_duration

        logger.info("Generating content frames...")
        if use_word_sync:
            content_frames = self.generate_content_frames_word_sync(
                content,
                tts_result.word_timings,
                content_start,
                content_end,
                output_dir=output_dir,
                frame_offset=frame_offset,
            )
        else:
            content_frames = self.generate_content_frames_scrolling(
                content,
                content_start,
                content_end,
                output_dir=output_dir,
                frame_offset=frame_offset,
            )
        all_frames.extend(content_frames)
        frame_offset += len(content_frames)

        # Phase 3: Outro (content_end to total_duration)
        logger.info("Generating outro frames...")
        outro_frames = self.generate_outro_frames(
            duration=outro_duration,
            output_dir=output_dir,
            frame_offset=frame_offset,
        )
        all_frames.extend(outro_frames)

        total_duration = len(all_frames) / self.spec.fps

        result = FrameGenerationResult(
            frame_paths=all_frames,
            frame_count=len(all_frames),
            total_duration=total_duration,
            output_dir=output_dir,
        )

        logger.info(
            f"Generated {result.frame_count} frames ({result.total_duration:.2f}s) "
            f"in {result.output_dir}"
        )

        return result


# Singleton instance
frame_generator = FrameGenerator()
