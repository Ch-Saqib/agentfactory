"""Video Generation Service.

This service orchestrates all components of the video generation pipeline:
1. Parse markdown from Docusaurus lessons
2. Generate audio with word-level timing (Google Cloud TTS)
3. Generate frames with text animation
4. Compose video with FFmpeg
5. Upload to R2 storage
6. Save metadata to database

Usage:
    service = VideoGenerationService()
    result = await service.generate_from_markdown(
        markdown_content="# Chapter 1\\nContent here...",
        chapter_id="chapter-1",
        chapter_title="Chapter 1",
    )
"""

import asyncio
import json
import logging
import tempfile
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from shorts_generator.core.config import settings
from shorts_generator.database import VideoCreate, database_manager
from shorts_generator.services.edge_tts_audio import (
    EdgeTTSGenerator,
    check_edge_tts_connectivity,
)
from shorts_generator.services.frame_generator import FrameGenerator
from shorts_generator.services.google_tts_audio import (
    GoogleCloudTTSGenerator,
    GoogleTTSResult,
)
from shorts_generator.services.markdown_parser import MarkdownParser
from shorts_generator.services.script_generator import ScriptGenerator
from shorts_generator.services.content_extractor import ContentExtractor, Concept, CodeBlock, LessonContent
from shorts_generator.services.r2_uploader import R2Uploader
from shorts_generator.services.video_composer import VideoComposer

logger = logging.getLogger(__name__)


@dataclass
class GenerationProgress:
    """Progress update during video generation."""

    step: str
    progress_percent: int
    message: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class GenerationResult:
    """Result of video generation."""

    success: bool
    video_id: int | None = None
    chapter_id: str | None = None
    video_url: str | None = None
    thumbnail_url: str | None = None
    duration_seconds: float | None = None
    file_size_mb: float | None = None
    error_message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class VideoGenerationService:
    """Service for generating short videos from markdown content.

    This service orchestrates the entire pipeline:
    - Markdown parsing
    - Audio generation with word-level timing
    - Frame generation with text animation
    - Video composition with FFmpeg
    - R2 upload
    - Database storage
    """

    def __init__(
        self,
        tts_generator: GoogleCloudTTSGenerator | EdgeTTSGenerator | None = None,
        frame_generator: FrameGenerator | None = None,
        video_composer: VideoComposer | None = None,
        r2_uploader: R2Uploader | None = None,
        output_dir: str | None = None,
    ) -> None:
        """Initialize the video generation service.

        Args:
            tts_generator: TTS generator (default: based on tts_provider setting)
            frame_generator: Frame generator (default: new FrameGenerator)
            video_composer: Video composer (default: new VideoComposer)
            r2_uploader: R2 uploader (default: r2_uploader singleton)
            output_dir: Output directory for temporary files
        """
        self.tts_generator = tts_generator or self._create_tts_generator()
        self.frame_generator = frame_generator or FrameGenerator()
        self.video_composer = video_composer or VideoComposer()
        self.r2_uploader = r2_uploader or self._get_r2_uploader()
        self.output_dir = Path(output_dir or tempfile.gettempdir()) / "shorts_generation"

        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(
            f"VideoGenerationService initialized (TTS provider: {settings.tts_provider})"
        )

    @staticmethod
    def _create_tts_generator() -> GoogleCloudTTSGenerator | EdgeTTSGenerator:
        """Create TTS generator based on config setting."""
        if settings.tts_provider == "google_tts":
            logger.info("Using Google Cloud TTS (paid, requires credentials)")
            return GoogleCloudTTSGenerator(
                credentials_path=settings.google_cloud_credentials_path or None,
                voice_preset=settings.google_tts_voice_preset,
                encoding=settings.google_tts_encoding,
                sample_rate=settings.google_tts_sample_rate,
            )
        else:
            logger.info(f"Using Edge TTS (free, voice: {settings.edge_tts_voice})")
            return EdgeTTSGenerator(voice=settings.edge_tts_voice)

    @staticmethod
    def _get_r2_uploader():
        """Get the R2 uploader singleton (lazy import)."""
        from shorts_generator.services.r2_uploader import get_r2_uploader
        return get_r2_uploader()

    async def generate_from_markdown(
        self,
        markdown_content: str,
        chapter_id: str,
        chapter_title: str,
        chapter_number: int | None = None,
        voice_preset: str | None = None,
        progress_callback: Callable[[GenerationProgress], None] | None = None,
    ) -> GenerationResult:
        """Generate a short video from markdown content.

        Args:
            markdown_content: Markdown content from Docusaurus lesson
            chapter_id: Unique chapter identifier
            chapter_title: Title of the chapter
            chapter_number: Chapter number in sequence
            voice_preset: TTS voice preset (default: from settings)
            progress_callback: Optional callback for progress updates

        Returns:
            GenerationResult with video metadata or error
        """
        temp_dir = None

        try:
            # Create temporary directory for this generation
            temp_dir = self.output_dir / chapter_id
            temp_dir.mkdir(parents=True, exist_ok=True)

            # Step 1: Parse markdown and generate AI summary script
            await self._report_progress(
                progress_callback, "parse_markdown", 10, "Parsing markdown and generating summary"
            )

            # Parse markdown for basic info
            parser = MarkdownParser()
            parsed = parser.parse_content(markdown_content)

            # Create LessonContent from markdown for script generator
            extractor = ContentExtractor()
            frontmatter, body = extractor.parse_frontmatter(markdown_content)

            # Extract key concepts from the lesson
            all_concepts = extractor.extract_headings(body)
            concepts_with_content = extractor.extract_concept_content(body, all_concepts)
            key_concepts = extractor.extract_key_concepts(concepts_with_content)

            # Create LessonContent object
            lesson_content = LessonContent(
                lesson_path=chapter_id,
                frontmatter=frontmatter,
                body=body,
                title=parsed.title or chapter_title,
                concepts=key_concepts,
                code_blocks=extractor.extract_code_blocks(body),
                difficulty_level=extractor.detect_difficulty_level(frontmatter),
                word_count=parsed.word_count,
                is_suitable_for_short=True,
            )

            # Generate AI summary script using Gemini
            logger.info(f"🤖 Generating AI summary for: {parsed.title} (full lesson: {parsed.word_count} words)")
            script_generator = ScriptGenerator()
            generated_script = await script_generator.generate_script(
                lesson=lesson_content,
                target_duration=60,  # 60 seconds target
            )

            # Format script for TTS
            excerpt_content = script_generator.format_for_tts(generated_script)
            excerpt_word_count = len(excerpt_content.split())

            # Derive sections from script scenes (for frame generation)
            sections = [s.strip() for s in excerpt_content.split(". ") if s.strip()]

            logger.info(
                f"✅ AI summary generated: {excerpt_word_count} words (~{excerpt_word_count/150*60:.0f}s) "
                f"from {parsed.word_count} word lesson"
            )

            # Step 2: Generate audio with word-level timing
            await self._report_progress(
                progress_callback, "generate_audio", 20, "Generating audio with TTS"
            )

            audio_path = temp_dir / "audio.mp3"
            timing_path = temp_dir / "timing.json"

            voice = voice_preset or settings.edge_tts_voice

            logger.info(
                f"Starting TTS audio generation with voice: {voice}, "
                f"text length: {len(excerpt_content)} chars"
            )

            # Generate audio — EdgeTTSGenerator is async, GoogleCloudTTSGenerator is sync
            if isinstance(self.tts_generator, EdgeTTSGenerator):
                logger.info("Using EdgeTTSGenerator (async)")
                # Quick connectivity check (non-blocking - just logs warning if fails)
                try:
                    connectivity = await check_edge_tts_connectivity()
                    if not connectivity["reachable"]:
                        logger.warning(
                            f"Edge TTS connectivity check failed: {connectivity.get('message')}. "
                            f"Proceeding anyway - retries will handle transient issues."
                        )
                except Exception as e:
                    logger.warning(f"Connectivity check skipped due to error: {e}")

                tts_result: GoogleTTSResult = await self.tts_generator.generate(
                    text=excerpt_content,
                    speaking_rate=1.0,
                    pitch=0.0,
                    custom_voice=voice,
                    output_path=str(audio_path),
                    max_retries=3,  # Retry on network errors
                )
            else:
                logger.info("Using GoogleCloudTTSGenerator (sync wrapper)")
                tts_result: GoogleTTSResult = await asyncio.to_thread(
                    self.tts_generator.generate,
                    text=excerpt_content,
                    speaking_rate=1.0,
                    pitch=0.0,
                    custom_voice=voice,
                    output_path=str(audio_path),
                )

            logger.info(
                f"TTS generation completed: duration={tts_result.duration_seconds:.2f}s, "
                f"words={len(tts_result.word_timings)}"
            )

            # Save timing data
            with open(timing_path, "w") as f:
                json.dump(
                    [
                        {
                            "word": t.word,
                            "start_time": t.start_time,
                            "end_time": t.end_time,
                        }
                        for t in tts_result.word_timings
                    ],
                    f,
                    indent=2,
                )

            logger.info(f"Generated audio: {tts_result.duration_seconds:.2f}s")

            await self._report_progress(
                progress_callback,
                "generate_audio",
                40,
                f"Audio generated ({tts_result.duration_seconds:.1f}s)",
            )

            # Step 3: Generate frames with text animation
            await self._report_progress(
                progress_callback, "generate_frames", 50, "Generating video frames"
            )

            frames_dir = temp_dir / "frames"
            frames_dir.mkdir(exist_ok=True)

            # Determine animation style based on content length
            use_word_sync = len(tts_result.word_timings) < 100
            logger.info(
                f"Animation mode: {'word_sync' if use_word_sync else 'scrolling'} "
                f"({len(tts_result.word_timings)} words, {tts_result.duration_seconds:.1f}s)"
            )

            if use_word_sync:
                # Word-by-word animation (karaoke style)
                frames_result = await asyncio.to_thread(
                    self.frame_generator.generate_content_frames_word_sync,
                    content=excerpt_content,
                    word_timings=tts_result.word_timings,
                    start_time=0.0,
                    end_time=tts_result.duration_seconds,
                    output_dir=str(frames_dir),
                )
            else:
                # Scrolling text animation
                full_content = "\n\n".join(sections)
                frames_result = await asyncio.to_thread(
                    self.frame_generator.generate_content_frames_scrolling,
                    content=full_content,
                    start_time=0.0,
                    end_time=tts_result.duration_seconds,
                    output_dir=str(frames_dir),
                )

            # Add title frames
            await asyncio.to_thread(
                self.frame_generator.generate_title_frames,
                title=chapter_title,
                output_dir=str(frames_dir / "title"),
            )

            # Add outro frames
            await asyncio.to_thread(
                self.frame_generator.generate_outro_frames,
                cta_text="Learn more at agentfactory.dev",
                output_dir=str(frames_dir / "outro"),
            )

            frame_count = len(frames_result)
            logger.info(f"Generated {frame_count} content frames")

            await self._report_progress(
                progress_callback,
                "generate_frames",
                70,
                f"Generated {frame_count} frames",
            )

            # Step 4: Compose video
            await self._report_progress(
                progress_callback, "compose_video", 80, "Composing final video"
            )

            video_path = temp_dir / "video.mp4"
            thumbnail_path = temp_dir / "thumbnail.jpg"

            compose_result = await self.video_composer.compose(
                frames_dir=str(frames_dir),
                audio_path=str(audio_path),
                output_path=str(video_path),
                fps=settings.video_fps,
                progress_callback=lambda p: self._report_progress(
                    progress_callback,
                    "compose_video",
                    80 + int(p * 10),
                    f"Composing video: {p * 100:.0f}%",
                ),
            )

            # Generate thumbnail at 25% of video duration
            thumbnail_timestamp = compose_result.duration_seconds * 0.25
            await self.video_composer.generate_thumbnail(
                video_path=str(video_path),
                output_path=str(thumbnail_path),
                timestamp=thumbnail_timestamp,
            )

            logger.info(f"Composed video: {compose_result.duration_seconds:.2f}s")

            # Step 5: Upload to R2
            await self._report_progress(
                progress_callback, "upload_video", 90, "Uploading to R2 storage"
            )

            # Upload video (sync method wrapped in async)
            video_upload = await asyncio.to_thread(
                self.r2_uploader.upload_video,
                video_path=str(video_path),
                chapter_id=chapter_id,
            )

            # Upload thumbnail (sync method wrapped in async)
            thumbnail_upload = await asyncio.to_thread(
                self.r2_uploader.upload_file,
                file_path=str(thumbnail_path),
                key=f"thumbnails/{chapter_id}/thumbnail.jpg",
            )

            logger.info(f"Uploaded video: {video_upload.url}")

            # Step 6: Save to database
            await self._report_progress(
                progress_callback, "save_database", 95, "Saving to database"
            )

            video_data = VideoCreate(
                chapter_id=chapter_id,
                chapter_title=chapter_title,
                chapter_number=chapter_number,
                content_snippet=f"🤖 AI Summary ({generated_script.total_duration}s): {excerpt_content[:180]}...",
                video_url=video_upload.url,
                thumbnail_url=thumbnail_upload.url,
                duration_seconds=compose_result.duration_seconds,
                word_count=excerpt_word_count,
                scene_count=len(sections),
                generation_method="google_tts",
                voice_used=voice,
                file_size_mb=video_upload.file_size_mb,
            )

            video = await database_manager.create_video(video_data)

            logger.info(f"Saved video to database: {video.id}")

            await self._report_progress(
                progress_callback, "complete", 100, "Video generation complete"
            )

            return GenerationResult(
                success=True,
                video_id=video.id,
                chapter_id=chapter_id,
                video_url=video_upload.url,
                thumbnail_url=thumbnail_upload.url,
                duration_seconds=compose_result.duration_seconds,
                file_size_mb=video_upload.file_size_mb,
                metadata={
                    "word_count": parsed.word_count,
                    "scene_count": len(sections),
                    "voice_used": voice,
                    "frame_count": frame_count,
                },
            )

        except Exception as e:
            logger.error(f"Video generation failed: {e}", exc_info=True)
            return GenerationResult(
                success=False,
                error_message=str(e),
            )

        finally:
            # Cleanup temporary files
            if temp_dir and temp_dir.exists():
                try:
                    # Clean up large files but keep directory for debugging
                    for file in temp_dir.glob("*.mp4"):
                        file.unlink()
                    for file in temp_dir.glob("*.mp3"):
                        file.unlink(missing_ok=True)
                    # Note: We keep frames and timing for debugging
                except Exception as e:
                    logger.warning(f"Failed to cleanup temp files: {e}")

    async def generate_from_file(
        self,
        markdown_file: str,
        chapter_id: str,
        chapter_title: str,
        chapter_number: int | None = None,
        voice_preset: str | None = None,
        progress_callback: Callable[[GenerationProgress], None] | None = None,
    ) -> GenerationResult:
        """Generate a short video from a markdown file.

        Args:
            markdown_file: Path to markdown file
            chapter_id: Unique chapter identifier
            chapter_title: Title of the chapter
            chapter_number: Chapter number in sequence
            voice_preset: TTS voice preset (default: from settings)
            progress_callback: Optional callback for progress updates

        Returns:
            GenerationResult with video metadata or error
        """
        # Read markdown file
        with open(markdown_file, encoding="utf-8") as f:
            markdown_content = f.read()

        return await self.generate_from_markdown(
            markdown_content=markdown_content,
            chapter_id=chapter_id,
            chapter_title=chapter_title,
            chapter_number=chapter_number,
            voice_preset=voice_preset,
            progress_callback=progress_callback,
        )

    async def _report_progress(
        self,
        callback: Callable[[GenerationProgress], None] | None,
        step: str,
        progress_percent: int,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Report progress to callback if provided.

        Args:
            callback: Progress callback function
            step: Current step name
            progress_percent: Progress percentage (0-100)
            message: Human-readable message
            details: Optional additional details
        """
        if callback:
            progress = GenerationProgress(
                step=step,
                progress_percent=progress_percent,
                message=message,
                details=details or {},
            )
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(progress)
                else:
                    callback(progress)
            except Exception as e:
                logger.warning(f"Progress callback failed: {e}")


# Singleton instance (lazy initialization)
video_generation_service: VideoGenerationService | None = None


def get_video_generation_service() -> VideoGenerationService:
    """Get or create the video generation service singleton (lazy initialization)."""
    global video_generation_service
    if video_generation_service is None:
        logger.info("Creating video generation service singleton")
        video_generation_service = VideoGenerationService()
        logger.info("Video generation service singleton created")
    return video_generation_service
