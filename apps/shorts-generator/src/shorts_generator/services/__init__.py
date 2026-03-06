"""Generation services for Lesson Shorts Generator."""

from shorts_generator.services.audio_generator import (
    AudioGenerator,
    GeneratedAudio,
    audio_generator,
)
from shorts_generator.services.frame_generator import (
    FrameGenerationResult,
    FrameGenerator,
    FrameSpec,
    TextAnimationConfig,
    frame_generator,
)
from shorts_generator.services.google_tts_audio import (
    AudioEncoding,
    GoogleCloudTTSGenerator,
    GoogleTTSResult,
    WordTiming,
    google_tts_generator,
)
from shorts_generator.services.markdown_parser import (
    MarkdownParser,
    ParsedChapter,
    get_lesson_excerpt,
    markdown_parser,
    parse_lesson_file,
)
from shorts_generator.services.r2_uploader import (
    PresignedURLResult,
    R2Uploader,
    UploadResult,
    r2_uploader,
)
from shorts_generator.services.video_composer import (
    VideoCodec,
    VideoComposer,
    VideoCompositionConfig,
    VideoCompositionResult,
    VideoPreset,
    VideoQuality,
    video_composer,
)
from shorts_generator.services.video_generation_service import (
    GenerationProgress,
    GenerationResult,
    VideoGenerationService,
    video_generation_service,
)
from shorts_generator.services.pipeline_orchestrator import (
    BatchResult,
    ChapterInput,
    ChapterResult,
    PipelineConfig,
    PipelineOrchestrator,
    PipelineStatus,
    pipeline_orchestrator,
)
from shorts_generator.services.batch_processor import (
    BatchProcessor,
    BatchReport,
    ChapterMetadata,
    batch_processor,
)
from shorts_generator.services.progress_service import (
    BatchProgress,
    ProgressService,
    ProgressStep,
    ProgressUpdate,
    progress_service,
)

__all__ = [
    # Audio Generator (Edge-TTS)
    "AudioGenerator",
    "GeneratedAudio",
    "audio_generator",
    # Frame Generator
    "FrameGenerator",
    "FrameSpec",
    "FrameGenerationResult",
    "TextAnimationConfig",
    "frame_generator",
    # Google Cloud TTS
    "AudioEncoding",
    "GoogleCloudTTSGenerator",
    "GoogleTTSResult",
    "WordTiming",
    "google_tts_generator",
    # Markdown Parser
    "MarkdownParser",
    "ParsedChapter",
    "markdown_parser",
    "parse_lesson_file",
    "get_lesson_excerpt",
    # R2 Uploader
    "R2Uploader",
    "UploadResult",
    "PresignedURLResult",
    "r2_uploader",
    # Video Composer
    "VideoCodec",
    "VideoComposer",
    "VideoCompositionConfig",
    "VideoCompositionResult",
    "VideoPreset",
    "VideoQuality",
    "video_composer",
    # Video Generation Service
    "VideoGenerationService",
    "GenerationProgress",
    "GenerationResult",
    "video_generation_service",
    # Pipeline Orchestrator
    "PipelineOrchestrator",
    "PipelineConfig",
    "PipelineStatus",
    "ChapterInput",
    "ChapterResult",
    "BatchResult",
    "pipeline_orchestrator",
    # Batch Processor
    "BatchProcessor",
    "BatchReport",
    "ChapterMetadata",
    "batch_processor",
    # Progress Service
    "ProgressService",
    "ProgressUpdate",
    "ProgressStep",
    "BatchProgress",
    "progress_service",
]
