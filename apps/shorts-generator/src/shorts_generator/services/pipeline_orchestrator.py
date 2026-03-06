"""Pipeline Orchestrator for Complete Video Generation Pipeline.

This module provides high-level orchestration of the entire video generation
pipeline with support for:
- Batch processing of multiple chapters
- Error handling with retry logic
- Progress tracking
- Concurrent processing with configurable limits
- Job queue management
- Resource cleanup

Usage:
    orchestrator = PipelineOrchestrator()
    result = await orchestrator.generate_single(chapter_id, markdown_content)
    # Or for batch:
    batch_result = await orchestrator.generate_batch(chapters_list)
"""

import asyncio
import logging
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from shorts_generator.database import database_manager
from shorts_generator.services.video_generation_service import (
    GenerationProgress,
    GenerationResult,
    VideoGenerationService,
)

logger = logging.getLogger(__name__)


class PipelineStatus(Enum):
    """Status of a pipeline job."""

    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


@dataclass
class ChapterInput:
    """Input data for a single chapter generation."""

    chapter_id: str
    chapter_title: str
    markdown_content: str | None = None
    markdown_file: str | None = None
    chapter_number: int | None = None
    voice_preset: str | None = None

    def __post_init__(self):
        """Validate that either markdown_content or markdown_file is provided."""
        if not self.markdown_content and not self.markdown_file:
            raise ValueError("Either markdown_content or markdown_file must be provided")


@dataclass
class ChapterResult:
    """Result of a single chapter generation."""

    chapter_id: str
    success: bool
    video_id: int | None = None
    video_url: str | None = None
    duration_seconds: float | None = None
    error_message: str | None = None
    retry_count: int = 0
    started_at: datetime | None = None
    completed_at: datetime | None = None


@dataclass
class BatchResult:
    """Result of a batch generation job."""

    batch_id: str
    status: PipelineStatus
    total_chapters: int
    completed: int = 0
    failed: int = 0
    skipped: int = 0
    results: list[ChapterResult] = field(default_factory=list)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error_message: str | None = None

    @property
    def progress_percent(self) -> int:
        """Calculate progress percentage."""
        if self.total_chapters == 0:
            return 0
        return int((self.completed + self.failed) / self.total_chapters * 100)


@dataclass
class PipelineConfig:
    """Configuration for pipeline execution."""

    max_concurrent_jobs: int = 3
    max_retries: int = 2
    retry_delay_seconds: int = 30
    timeout_seconds: int = 600  # 10 minutes per video
    enable_progress_callbacks: bool = True
    cleanup_temp_files: bool = True
    fail_fast: bool = False  # Stop batch on first failure


class PipelineOrchestrator:
    """Orchestrates the complete video generation pipeline.

    Features:
    - Single and batch video generation
    - Retry logic with exponential backoff
    - Concurrent processing with limits
    - Progress tracking
    - Error recovery
    - Resource cleanup
    """

    def __init__(
        self,
        video_service: VideoGenerationService | None = None,
        config: PipelineConfig | None = None,
    ) -> None:
        """Initialize the pipeline orchestrator.

        Args:
            video_service: Video generation service (default: singleton)
            config: Pipeline configuration
        """
        from shorts_generator.services.video_generation_service import (
            video_generation_service,
        )

        self.video_service = video_service or video_generation_service
        self.config = config or PipelineConfig()
        self._active_batches: dict[str, BatchResult] = {}
        self._cancel_flags: dict[str, asyncio.Event] = {}

        logger.info(
            f"PipelineOrchestrator initialized with "
            f"max_concurrent_jobs={self.config.max_concurrent_jobs}"
        )

    async def generate_single(
        self,
        chapter: ChapterInput,
        progress_callback: Callable[[GenerationProgress], None] | None = None,
        job_id: str | None = None,
    ) -> ChapterResult:
        """Generate a single video.

        Args:
            chapter: Chapter input data
            progress_callback: Optional progress callback
            job_id: Optional job ID for tracking

        Returns:
            ChapterResult with generation outcome
        """
        job_id = job_id or f"job-{uuid.uuid4().hex[:8]}"
        started_at = datetime.now()

        logger.info(f"[{job_id}] Starting generation for {chapter.chapter_id}")

        # Create database job
        await database_manager.create_job(
            job_id=job_id,
            job_type="single",
            chapter_id=chapter.chapter_id,
            input_data={
                "chapter_title": chapter.chapter_title,
                "voice_preset": chapter.voice_preset,
            },
        )

        retry_count = 0
        last_error = None

        while retry_count <= self.config.max_retries:
            if retry_count > 0:
                logger.info(f"[{job_id}] Retry {retry_count}/{self.config.max_retries}")
                await database_manager.update_job_status(
                    job_id,
                    status="running",
                    progress=0,
                )
                await asyncio.sleep(self.config.retry_delay_seconds * retry_count)

            try:
                # Update job status to running
                await database_manager.update_job_status(
                    job_id,
                    status="running",
                    progress=0,
                )

                # Progress wrapper to update database
                async def db_progress_wrapper(progress: GenerationProgress):
                    if progress_callback:
                        if asyncio.iscoroutinefunction(progress_callback):
                            await progress_callback(progress)
                        else:
                            progress_callback(progress)

                    # Update database job progress
                    await database_manager.update_job_status(
                        job_id,
                        status="running",
                        progress=progress.progress_percent,
                    )

                # Generate video
                if chapter.markdown_content:
                    result: GenerationResult = (
                        await self.video_service.generate_from_markdown(
                            markdown_content=chapter.markdown_content,
                            chapter_id=chapter.chapter_id,
                            chapter_title=chapter.chapter_title,
                            chapter_number=chapter.chapter_number,
                            voice_preset=chapter.voice_preset,
                            progress_callback=db_progress_wrapper
                            if self.config.enable_progress_callbacks
                            else None,
                        )
                    )
                else:
                    result = await self.video_service.generate_from_file(
                        markdown_file=chapter.markdown_file,
                        chapter_id=chapter.chapter_id,
                        chapter_title=chapter.chapter_title,
                        chapter_number=chapter.chapter_number,
                        voice_preset=chapter.voice_preset,
                        progress_callback=db_progress_wrapper
                        if self.config.enable_progress_callbacks
                        else None,
                    )

                if result.success:
                    logger.info(f"[{job_id}] Generation successful")

                    await database_manager.update_job_status(
                        job_id,
                        status="completed",
                        progress=100,
                        result_data={
                            "video_id": result.video_id,
                            "video_url": result.video_url,
                            "thumbnail_url": result.thumbnail_url,
                            "duration_seconds": result.duration_seconds,
                            "file_size_mb": result.file_size_mb,
                        },
                    )

                    return ChapterResult(
                        chapter_id=chapter.chapter_id,
                        success=True,
                        video_id=result.video_id,
                        video_url=result.video_url,
                        duration_seconds=result.duration_seconds,
                        retry_count=retry_count,
                        started_at=started_at,
                        completed_at=datetime.now(),
                    )
                else:
                    last_error = result.error_message
                    logger.warning(f"[{job_id}] Generation failed: {last_error}")

            except TimeoutError:
                last_error = f"Timeout after {self.config.timeout_seconds} seconds"
                logger.error(f"[{job_id}] {last_error}")

            except asyncio.CancelledError:
                logger.info(f"[{job_id}] Generation cancelled")
                await database_manager.update_job_status(
                    job_id,
                    status="failed",
                    error_message="Cancelled by user",
                )
                return ChapterResult(
                    chapter_id=chapter.chapter_id,
                    success=False,
                    error_message="Cancelled by user",
                    retry_count=retry_count,
                    started_at=started_at,
                    completed_at=datetime.now(),
                )

            except Exception as e:
                last_error = str(e)
                logger.error(f"[{job_id}] Unexpected error: {e}", exc_info=True)

            retry_count += 1

        # All retries exhausted
        logger.error(f"[{job_id}] All retries exhausted")
        await database_manager.update_job_status(
            job_id,
            status="failed",
            error_message=last_error,
        )

        return ChapterResult(
            chapter_id=chapter.chapter_id,
            success=False,
            error_message=last_error,
            retry_count=retry_count - 1,
            started_at=started_at,
            completed_at=datetime.now(),
        )

    async def generate_batch(
        self,
        chapters: list[ChapterInput],
        batch_id: str | None = None,
        progress_callback: Callable[[BatchResult], None] | None = None,
    ) -> BatchResult:
        """Generate multiple videos in batch.

        Args:
            chapters: List of chapter inputs
            batch_id: Optional batch ID for tracking
            progress_callback: Optional progress callback

        Returns:
            BatchResult with all chapter results
        """
        batch_id = batch_id or f"batch-{uuid.uuid4().hex[:8]}"
        started_at = datetime.now()

        logger.info(
            f"[{batch_id}] Starting batch generation of {len(chapters)} chapters"
        )

        # Initialize batch result
        batch_result = BatchResult(
            batch_id=batch_id,
            status=PipelineStatus.RUNNING,
            total_chapters=len(chapters),
            started_at=started_at,
        )

        self._active_batches[batch_id] = batch_result
        self._cancel_flags[batch_id] = asyncio.Event()

        # Create batch job in database
        await database_manager.create_job(
            job_id=batch_id,
            job_type="batch",
            chapter_id="batch",
            input_data={"chapter_count": len(chapters)},
        )

        try:
            # Process chapters in concurrent batches
            semaphore = asyncio.Semaphore(self.config.max_concurrent_jobs)

            async def process_with_semaphore(
                chapter: ChapterInput,
            ) -> ChapterResult:
                """Process a chapter with semaphore control."""
                # Check for cancellation
                if self._cancel_flags[batch_id].is_set():
                    raise asyncio.CancelledError()

                async with semaphore:
                    # Check if video already exists
                    existing = await database_manager.get_video_by_chapter_id(
                        chapter.chapter_id
                    )
                    if existing:
                        logger.info(
                            f"[{batch_id}] Video already exists for {chapter.chapter_id}"
                        )
                        return ChapterResult(
                            chapter_id=chapter.chapter_id,
                            success=True,
                            video_id=existing.id,
                            video_url=existing.video_url,
                            duration_seconds=existing.duration_seconds,
                        )

                    result = await self.generate_single(
                        chapter=chapter,
                        job_id=f"{batch_id}-{chapter.chapter_id}",
                    )

                    # Update batch progress
                    if result.success:
                        batch_result.completed += 1
                    else:
                        batch_result.failed += 1
                        if self.config.fail_fast:
                            self._cancel_flags[batch_id].set()

                    # Report progress
                    if progress_callback:
                        if asyncio.iscoroutinefunction(progress_callback):
                            await progress_callback(batch_result)
                        else:
                            progress_callback(batch_result)

                    return result

            # Run all tasks concurrently
            tasks = [process_with_semaphore(chapter) for chapter in chapters]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            for item in results:
                if isinstance(item, asyncio.CancelledError):
                    batch_result.status = PipelineStatus.CANCELLED
                    break
                elif isinstance(item, Exception):
                    logger.error(f"Unexpected error in batch: {item}")
                    batch_result.failed += 1
                elif isinstance(item, ChapterResult):
                    batch_result.results.append(item)

            # Update final status
            batch_result.completed_at = datetime.now()
            if batch_result.status != PipelineStatus.CANCELLED:
                if batch_result.failed == 0:
                    batch_result.status = PipelineStatus.COMPLETED
                elif batch_result.completed > 0:
                    batch_result.status = PipelineStatus.COMPLETED
                else:
                    batch_result.status = PipelineStatus.FAILED

            # Update database
            await database_manager.update_job_status(
                batch_id,
                status=batch_result.status.value,
                progress=100,
                result_data={
                    "completed": batch_result.completed,
                    "failed": batch_result.failed,
                    "skipped": batch_result.skipped,
                },
            )

            logger.info(
                f"[{batch_id}] Batch complete: "
                f"{batch_result.completed} succeeded, {batch_result.failed} failed"
            )

            return batch_result

        finally:
            # Cleanup
            self._cancel_flags.pop(batch_id, None)

    async def cancel_batch(self, batch_id: str) -> bool:
        """Cancel a running batch job.

        Args:
            batch_id: Batch ID to cancel

        Returns:
            True if cancellation was requested
        """
        if batch_id in self._cancel_flags:
            self._cancel_flags[batch_id].set()

            if batch_id in self._active_batches:
                self._active_batches[batch_id].status = PipelineStatus.CANCELLED

            await database_manager.update_job_status(
                batch_id,
                status="cancelled",
            )

            logger.info(f"[{batch_id}] Batch cancellation requested")
            return True

        return False

    def get_batch_status(self, batch_id: str) -> BatchResult | None:
        """Get the status of a batch job.

        Args:
            batch_id: Batch ID

        Returns:
            BatchResult or None if not found
        """
        return self._active_batches.get(batch_id)

    async def get_estimated_time_remaining(
        self,
        batch_id: str,
        average_time_per_video: float = 120.0,  # 2 minutes default
    ) -> float | None:
        """Estimate time remaining for a batch job.

        Args:
            batch_id: Batch ID
            average_time_per_video: Average seconds per video

        Returns:
            Estimated seconds remaining or None
        """
        batch_result = self.get_batch_status(batch_id)
        if not batch_result:
            return None

        remaining = batch_result.total_chapters - batch_result.completed - batch_result.failed
        return remaining * average_time_per_video


# Singleton instance
pipeline_orchestrator = PipelineOrchestrator()
