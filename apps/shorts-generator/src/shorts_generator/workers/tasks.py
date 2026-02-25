"""Celery task definitions for video generation.

This module defines all async tasks that can be executed by Celery workers:
- Single video generation
- Batch video generation
- Job cleanup and maintenance
"""

import logging
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shorts_generator.database.connection import get_session
from shorts_generator.models import GenerationJob, ShortVideo
from shorts_generator.services.audio_generator import audio_generator
from shorts_generator.services.content_extractor import ContentExtractor
from shorts_generator.services.script_generator import ScriptGenerator
from shorts_generator.services.video_assembler import VideoAssembler
from shorts_generator.services.visual_generator import VisualGenerator

logger = logging.getLogger(__name__)

# Service singletons
content_extractor = ContentExtractor()
script_generator = ScriptGenerator()
visual_generator = VisualGenerator()
video_assembler = VideoAssembler()


def _update_job_progress(job_id: str, progress: int, status: str = None):
    """Update job progress in database.

    Args:
        job_id: Generation job ID
        progress: Progress percentage (0-100)
        status: Optional status update
    """
    import asyncio

    async def _do_update():
        async with get_session() as session:
            result = await session.execute(select(GenerationJob).where(GenerationJob.id == job_id))
            job = await result.scalar_one_or_none()

            if job:
                job.progress = progress
                if status:
                    job.status = status
                job.updated_at = datetime.utcnow()
                await session.commit()

    # Run async function in sync context
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.run_until_complete(_do_update())


def _set_job_error(job_id: str, error_message: str):
    """Mark job as failed with error message.

    Args:
        job_id: Generation job ID
        error_message: Error message to store
    """
    import asyncio

    async def _do_set_error():
        async with get_session() as session:
            result = await session.execute(select(GenerationJob).where(GenerationJob.id == job_id))
            job = await result.scalar_one_or_none()

            if job:
                job.status = "failed"
                job.error_message = error_message
                job.updated_at = datetime.utcnow()
                job.completed_at = datetime.utcnow()
                await session.commit()

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.run_until_complete(_do_set_error())


def _complete_job(job_id: str, video_id: str):
    """Mark job as completed successfully.

    Args:
        job_id: Generation job ID
        video_id: Generated video ID
    """
    import asyncio

    async def _do_complete():
        async with get_session() as session:
            result = await session.execute(select(GenerationJob).where(GenerationJob.id == job_id))
            job = await result.scalar_one_or_none()

            if job:
                job.status = "completed"
                job.progress = 100
                job.video_id = UUID(video_id)
                job.updated_at = datetime.utcnow()
                job.completed_at = datetime.utcnow()
                await session.commit()

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.run_until_complete(_do_complete())


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    soft_time_limit=3300,  # 55 minutes
    time_limit=3600,  # 1 hour
)
def generate_short_task(
    self,
    job_id: str,
    lesson_path: str,
    target_duration: int = 60,
    voice: str = "en-US-AriaNeural",
) -> dict:
    """Generate a single short video from a lesson.

    This task:
    1. Extracts content from the lesson
    2. Generates a script using Gemini
    3. Creates visuals using Flux.1
    4. Generates narration using Edge-TTS
    5. Assembles the final video using FFmpeg
    6. Saves video metadata to database

    Args:
        self: Celery task instance (for retries)
        job_id: Generation job ID
        lesson_path: Path to lesson markdown file
        target_duration: Target video duration in seconds
        voice: TTS voice to use

    Returns:
        dict with video_id and metadata

    Raises:
        Exception: If generation fails (will trigger retry)
    """
    logger.info(f"Starting generation task for job: {job_id}")

    try:
        # Update job status
        _update_job_progress(job_id, 0, "processing")

        # Step 1: Extract content (10%)
        logger.info(f"Step 1: Extracting content from {lesson_path}")
        lesson_content = asyncio.run(content_extractor.extract_content(lesson_path))

        if not lesson_content:
            raise Exception(f"Could not extract content from lesson: {lesson_path}")

        _update_job_progress(job_id, 10)

        # Step 2: Generate script (30%)
        logger.info("Step 2: Generating script with Gemini")
        script = asyncio.run(
            script_generator.generate_script(
                lesson_content,
                target_duration=target_duration,
            )
        )

        _update_job_progress(job_id, 30)

        # Step 3: Generate visuals (60%)
        logger.info(f"Step 3: Generating {len(script.concepts)} scene visuals")
        scene_images = []

        # Hook visual
        hook_image = asyncio.run(
            visual_generator.generate_scene_image(script.hook.visual_description)
        )
        scene_images.append(hook_image.url)

        # Concept visuals
        for i, concept in enumerate(script.concepts):
            concept_image = asyncio.run(
                visual_generator.generate_scene_image(concept.visual_description)
            )
            scene_images.append(concept_image.url)
            # Update progress incrementally
            _update_job_progress(job_id, 30 + (i + 1) * 10)

        # Example visual
        if "code" in script.example.visual_description.lower():
            example_image = asyncio.run(
                visual_generator.generate_code_screenshot(script.example.text, "python")
            )
        else:
            example_image = asyncio.run(
                visual_generator.generate_scene_image(script.example.visual_description)
            )
        scene_images.append(example_image.url)

        # CTA visual
        cta_image = asyncio.run(
            visual_generator.generate_scene_image(script.cta.visual_description)
        )
        scene_images.append(cta_image.url)

        _update_job_progress(job_id, 60)

        # Step 4: Generate audio (80%)
        logger.info("Step 4: Generating narration with Edge-TTS")
        full_script = script_generator.format_for_tts(script)
        audio, captions = asyncio.run(
            audio_generator.generate_audio_for_script(
                full_script,
                voice=voice,
                add_music=False,
            )
        )

        _update_job_progress(job_id, 80)

        # Step 5: Assemble video (95%)
        logger.info("Step 5: Assembling final video with FFmpeg")
        video = asyncio.run(
            video_assembler.assemble_video(
                scene_images=scene_images,
                audio=audio,
                script=script,
                captions=captions,
            )
        )

        _update_job_progress(job_id, 95)

        # Step 6: Save to database (100%)
        logger.info("Step 6: Saving video metadata to database")

        async def _save_video():
            from shorts_generator.services.storage import storage_service

            async with get_session() as session:
                video_id = str(uuid4())

                # Upload captions to R2
                captions_upload = await storage_service.upload_captions(
                    captions_content=captions,
                    video_id=video_id,
                )

                short_video = ShortVideo(
                    id=video_id,
                    lesson_path=lesson_path,
                    title=lesson_content.title,
                    script=full_script,
                    duration_seconds=script.total_duration,
                    video_url=video.url,
                    thumbnail_url=video.thumbnail_url,
                    captions_url=captions_upload["cdn_url"],
                    generation_cost=0.006,  # TODO: Calculate actual cost
                )

                session.add(short_video)
                await session.commit()

                return video_id

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        video_id = loop.run_until_complete(_save_video())

        # Mark job as completed
        _complete_job(job_id, video_id)

        logger.info(f"Video generation complete: {video_id}")

        return {
            "job_id": job_id,
            "video_id": video_id,
            "lesson_path": lesson_path,
            "duration_seconds": script.total_duration,
            "file_size_mb": video.file_size_mb,
        }

    except SoftTimeLimitExceeded:
        logger.error(f"Task timed out for job: {job_id}")
        _set_job_error(job_id, "Task timed out after 55 minutes")
        raise

    except Exception as e:
        logger.error(f"Video generation failed for job {job_id}: {e}", exc_info=True)

        # Check if we should retry
        if self.request.retries < self.max_retries:
            _update_job_progress(job_id, 0, "queued")
            logger.info(f"Retrying job {job_id} (attempt {self.request.retries + 1}/{self.max_retries})")
            raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))

        # Max retries exceeded
        _set_job_error(job_id, str(e))
        raise


@shared_task
def cleanup_old_jobs():
    """Clean up old generation jobs from database.

    Runs daily at 2 AM via Celery Beat.
    Removes jobs older than 30 days.
    """
    logger.info("Starting cleanup of old jobs")

    cutoff_date = datetime.utcnow() - timedelta(days=30)

    async def _do_cleanup():
        async with get_session() as session:
            # Delete completed jobs older than 30 days
            result = await session.execute(
                select(GenerationJob).where(
                    GenerationJob.status == "completed",
                    GenerationJob.completed_at < cutoff_date,
                )
            )
            jobs_to_delete = result.scalars().all()

            count = len(jobs_to_delete)
            for job in jobs_to_delete:
                await session.delete(job)

            await session.commit()
            return count

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    deleted_count = loop.run_until_complete(_do_cleanup())

    logger.info(f"Cleaned up {deleted_count} old jobs")
    return {"deleted_jobs": deleted_count}


@shared_task
def purge_old_videos():
    """Purge old video files from storage.

    Runs daily at 3 AM via Celery Beat.
    Removes videos with no views in 90 days.

    TODO: Implement R2 storage purging
    """
    logger.info("Starting purge of old videos")

    cutoff_date = datetime.utcnow() - timedelta(days=90)

    async def _get_old_videos():
        async with get_session() as session:
            # Get videos with no views in 90 days
            result = await session.execute(
                select(ShortVideo).where(
                    ShortVideo.created_at < cutoff_date,
                )
            )
            return result.scalars().all()

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    old_videos = loop.run_until_complete(_get_old_videos())

    # TODO: Delete from R2 storage
    # For now, just log
    logger.info(f"Found {len(old_videos)} videos older than 90 days")

    return {
        "eligible_for_purge": len(old_videos),
        "purged": 0,  # Will implement when R2 integration is complete
    }


@shared_task(bind=True)
def batch_generate_shorts_task(
    self,
    batch_id: str,
    job_ids: list[str],
    lesson_paths: list[str],
    target_duration: int,
    voice: str,
) -> dict:
    """Generate multiple shorts in batch.

    Dispatches individual generation tasks and tracks completion.

    Args:
        self: Celery task instance
        batch_id: Batch identifier
        job_ids: List of job IDs
        lesson_paths: List of lesson paths
        target_duration: Target duration for each video
        voice: TTS voice to use

    Returns:
        dict with batch summary
    """
    logger.info(f"Starting batch {batch_id} with {len(lesson_paths)} jobs")

    # Dispatch individual tasks
    task_results = []
    for job_id, lesson_path in zip(job_ids, lesson_paths):
        task = generate_short_task.delay(job_id, lesson_path, target_duration, voice)
        task_results.append({"job_id": job_id, "task_id": task.id})

    return {
        "batch_id": batch_id,
        "total_jobs": len(lesson_paths),
        "tasks": task_results,
    }


@shared_task
def auto_generate_shorts():
    """Automatically generate shorts from lessons.

    Runs daily at 10 AM UTC via Celery Beat.
    Finds lessons that don't have shorts yet and generates them.

    Configuration via environment variables:
    - AUTO_GENERATE_ENABLED: Enable/disable auto-generation (default: true)
    - AUTO_GENERATE_BATCH_SIZE: Number of shorts to generate per run (default: 5)
    - AUTO_GENERATE_PARTS: Parts to generate from (default: all)

    Returns:
        dict with generation summary
    """
    import os

    # Check if auto-generation is enabled
    if os.getenv("AUTO_GENERATE_ENABLED", "true").lower() != "true":
        logger.info("Auto-generation is disabled")
        return {"enabled": False, "reason": "disabled_by_config"}

    batch_size = int(os.getenv("AUTO_GENERATE_BATCH_SIZE", "5"))
    logger.info(f"Starting auto-generation of shorts (batch_size={batch_size})")

    async def _get_lessons_without_shorts():
        async with get_session() as session:
            # Get existing lesson paths that already have shorts
            result = await session.execute(
                select(ShortVideo.lesson_path)
            )
            existing_paths = set(row[0] for row in result.all())

            # For now, return a sample list of lessons
            # In production, this would query your content API
            sample_lessons = [
                "01-General-Agents-Foundations/01-agent-factory-paradigm/README.md",
                "01-General-Agents-Foundations/02-general-agents/README.md",
                "01-General-Agents-Foundations/03-seven-principles/README.md",
                "02-Applied-General-Agent-Workflows/06-build-your-first-personal-ai-employee/README.md",
                "03-SDD-RI-Fundamentals/11-ai-native-ides/README.md",
            ]

            # Filter out lessons that already have shorts
            new_lessons = [l for l in sample_lessons if l not in existing_paths]
            return new_lessons[:batch_size]

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    lessons_to_generate = loop.run_until_complete(_get_lessons_without_shorts())

    if not lessons_to_generate:
        logger.info("No new lessons to generate shorts for")
        return {
            "enabled": True,
            "generated": 0,
            "reason": "all_lessons_have_shorts",
        }

    # Create jobs for each lesson
    job_ids = []
    for lesson_path in lessons_to_generate:
        async def _create_job():
            async with get_session() as session:
                job = GenerationJob(
                    lesson_path=lesson_path,
                    status="queued",
                    progress=0,
                )
                session.add(job)
                await session.commit()
                await session.refresh(job)
                return str(job.id)

        job_id = loop.run_until_complete(_create_job())
        job_ids.append(job_id)

        # Trigger generation task
        from uuid import uuid4

        generate_short_task.delay(job_id, lesson_path, 60, "en-US-AriaNeural")

    logger.info(f"Auto-generated {len(job_ids)} shorts for lessons: {lessons_to_generate}")

    return {
        "enabled": True,
        "generated": len(job_ids),
        "job_ids": job_ids,
        "lessons": lessons_to_generate,
    }
