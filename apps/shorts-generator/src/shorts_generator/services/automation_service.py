"""Simplified automation service using APScheduler.

Replaces Celery with a simple in-memory scheduler for automated video generation.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from uuid import uuid4
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shorts_generator.database.connection import get_session
from shorts_generator.models import AutomationSettings, GenerationJob, ShortVideo, utcnow
from shorts_generator.services.content_extractor import ContentExtractor
from shorts_generator.services.script_generator import ScriptGenerator
from shorts_generator.services.visual_generator import VisualGenerator
from shorts_generator.services.audio_generator import audio_generator
from shorts_generator.services.video_assembler import VideoAssembler

logger = logging.getLogger(__name__)


async def run_automation_forced():
    """Wrapper function for forced automation runs (used by trigger endpoint)."""
    await run_automation(force=True)

# Global scheduler instance
scheduler: Optional[AsyncIOScheduler] = None

# Service singletons (reused for efficiency)
content_extractor = ContentExtractor()
script_generator = ScriptGenerator()
visual_generator = VisualGenerator()
video_assembler = VideoAssembler()


async def generate_single_short(
    job_id: str,
    lesson_path: str,
    target_duration: int = 60,
    voice: str = "en-US-AriaNeural",
) -> dict:
    """Generate a single short video from a lesson.

    Args:
        job_id: Generation job ID
        lesson_path: Path to lesson markdown file
        target_duration: Target video duration in seconds
        voice: TTS voice to use

    Returns:
        dict with video_id and metadata
    """
    logger.info(f"Starting generation for job: {job_id}")

    try:
        # Get database session
        async for session in get_session():
            # Update job status
            result = await session.execute(select(GenerationJob).where(GenerationJob.id == job_id))
            job = result.scalar_one_or_none()

            if job:
                job.progress = 0
                job.status = "processing"
                await session.commit()

            # Step 1: Extract content (10%)
            logger.info(f"Step 1: Extracting content from {lesson_path}")
            lesson_content = await content_extractor.extract_content(lesson_path)

            if not lesson_content:
                raise Exception(f"Could not extract content from lesson: {lesson_path}")

            job.progress = 10
            await session.commit()

            # Step 2: Generate script (30%)
            logger.info("Step 2: Generating script with Gemini")
            script = await script_generator.generate_script(
                lesson_content,
                target_duration=target_duration,
            )

            job.progress = 30
            await session.commit()

            # Step 3: Generate visuals (60%)
            logger.info(f"Step 3: Generating {len(script.concepts)} scene visuals")
            scene_images = []

            # Hook visual
            hook_image = await visual_generator.generate_scene_image(script.hook.visual_description)
            scene_images.append(hook_image.url)

            # Concept visuals
            for i, concept in enumerate(script.concepts):
                concept_image = await visual_generator.generate_scene_image(concept.visual_description)
                scene_images.append(concept_image.url)
                job.progress = 30 + (i + 1) * 10
                await session.commit()

            # Example visual
            if "code" in script.example.visual_description.lower():
                example_image = await visual_generator.generate_code_screenshot(script.example.text, "python")
            else:
                example_image = await visual_generator.generate_scene_image(script.example.visual_description)
            scene_images.append(example_image.url)

            # CTA visual
            cta_image = await visual_generator.generate_scene_image(script.cta.visual_description)
            scene_images.append(cta_image.url)

            job.progress = 60
            await session.commit()

            # Step 4: Generate audio (80%)
            logger.info("Step 4: Generating narration with Edge-TTS")
            full_script = script_generator.format_for_tts(script)
            audio, captions = await audio_generator.generate_audio_for_script(
                full_script,
                voice=voice,
                add_music=False,
            )

            job.progress = 80
            await session.commit()

            # Step 5: Assemble video (95%)
            logger.info("Step 5: Assembling final video with FFmpeg")
            video = await video_assembler.assemble_video(
                scene_images=scene_images,
                audio=audio,
                script=script,
                captions=captions,
                script_text=full_script,
            )

            job.progress = 95
            await session.commit()

            # Step 6: Save to database (100%)
            logger.info("Step 6: Saving video metadata to database")

            from shorts_generator.services.storage import storage_service

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

            # Mark job as completed
            job.status = "completed"
            job.progress = 100
            job.video_id = video_id
            job.completed_at = utcnow()
            await session.commit()

            logger.info(f"Video generation complete: {video_id}")

            return {
                "job_id": job_id,
                "video_id": video_id,
                "lesson_path": lesson_path,
                "duration_seconds": script.total_duration,
            }

    except Exception as e:
        logger.error(f"Video generation failed for job {job_id}: {e}", exc_info=True)

        # Mark job as failed
        async for session in get_session():
            result = await session.execute(select(GenerationJob).where(GenerationJob.id == job_id))
            job = result.scalar_one_or_none()
            if job:
                job.status = "failed"
                job.error_message = str(e)
                job.completed_at = utcnow()
                await session.commit()

        raise


async def find_lessons_without_shorts(
    docs_path: Path,
    batch_size: int,
    selected_parts: Optional[set[str]] = None,
) -> list[str]:
    """Find lessons that don't have shorts yet.

    Args:
        docs_path: Path to the docs directory
        batch_size: Maximum number of lessons to return
        selected_parts: Set of part IDs to filter by (empty = all parts)

    Returns:
        List of lesson paths
    """
    async for session in get_session():
        # Get existing lesson paths that already have shorts
        result = await session.execute(select(ShortVideo.lesson_path))
        existing_paths = set(row[0] for row in result.all())

    lessons = []
    selected_part_ids = selected_parts or set()

    if docs_path.exists():
        for part_dir in sorted(docs_path.iterdir()):
            if not part_dir.is_dir() or part_dir.name.startswith("."):
                continue

            # Parse part ID from folder name (NN-Part-Name)
            part_name_parts = part_dir.name.split("-", 1)
            if len(part_name_parts) != 2:
                continue

            part_id = part_name_parts[0]

            # Skip if not in selected parts (if filter is set)
            if selected_part_ids and part_id not in selected_part_ids:
                continue

            # Find all lesson files in this part
            for chapter_dir in sorted(part_dir.iterdir()):
                if not chapter_dir.is_dir() or chapter_dir.name.startswith("."):
                    continue

                # Look for lesson markdown files (skip README, index, quiz files)
                for lesson_file in chapter_dir.glob("*.md"):
                    if lesson_file.name.startswith("."):
                        continue

                    # Skip non-lesson files
                    skip_patterns = ["README", "index", "chapter-quiz", "quiz", "SUMMARY", "INTRODUCTION"]
                    if any(pattern.lower() in lesson_file.name.lower() for pattern in skip_patterns):
                        logger.debug(f"Skipping non-lesson file: {lesson_file.name}")
                        continue

                    # Only process numbered lesson files (01-*.md, 02-*.md, etc.)
                    if not lesson_file.name[0].isdigit():
                        logger.debug(f"Skipping non-numbered file: {lesson_file.name}")
                        continue

                    # Create relative lesson path
                    lesson_path = f"{part_dir.name}/{chapter_dir.name}/{lesson_file.name}"

                    # Skip if already has a short
                    if lesson_path in existing_paths:
                        continue

                    lessons.append(lesson_path)

                    if len(lessons) >= batch_size:
                        return lessons

    return lessons


async def run_automation(force: bool = False):
    """Main automation task - generates shorts based on database settings.

    This function is called by the APScheduler on a schedule.

    Args:
        force: If True, bypass the next_run check and run immediately
    """
    print(f"=== run_automation called with force={force} ===")  # Debug print
    if force:
        print("=== FORCE MODE ===")
    else:
        print("=== NORMAL MODE ===")

    print("Getting session...")
    async for session in get_session():
            print("Session obtained")
            # Get automation settings
            print("Executing query...")
            result = await session.execute(
                select(AutomationSettings).order_by(AutomationSettings.created_at.desc())
            )
            settings = result.scalar_one_or_none()

            print(f"Settings: {settings}")

            if not settings:
                print("No settings found, skipping")
                return

            if not settings.enabled:
                print(f"Automation disabled, skipping")
                return

            now = utcnow()
            print(f"Current time: {now.isoformat()}, next_run: {settings.next_run.isoformat() if settings.next_run else 'None'}, force={force}")

            # Check if we have a next_run time and if we're past it (unless force=True)
            if settings.next_run and (force or now >= settings.next_run):
                # Check if we already ran recently (to avoid duplicate runs) - skip this check for force mode
                if not force and settings.last_run:
                    if now - settings.last_run < timedelta(hours=1):
                        print(f"Already ran recently at {settings.last_run}, skipping")
                        return

                print(f"=== Automation triggered at {now.isoformat()} ===")

                # Find lessons without shorts
                print("Finding lessons without shorts...")
                docs_path = Path("/home/saqib-squad/agentfactory/apps/learn-app/docs")
                if not docs_path.exists():
                    docs_path = Path(__file__).parent.parent.parent.parent.parent / "learn-app" / "docs"

                selected_part_ids = set(settings.selected_parts.values()) if settings.selected_parts else set()
                print(f"Selected parts: {selected_part_ids}")
                lessons = await find_lessons_without_shorts(
                    docs_path=docs_path,
                    batch_size=settings.batch_limit,
                    selected_parts=selected_part_ids,
                )

                print(f"Found {len(lessons)} lessons: {lessons}")

                if not lessons:
                    print("No new lessons to generate shorts for")
                    # Still update last_run
                    settings.last_run = now
                    await session.commit()
                    return

                print(f"Found {len(lessons)} lessons to generate: {lessons}")

                # Create jobs for each lesson and collect tasks
                generation_tasks = []
                for lesson_path in lessons:
                    print(f"Creating job for: {lesson_path}")
                    job = GenerationJob(
                        lesson_path=lesson_path,
                        status="queued",
                        progress=0,
                    )
                    session.add(job)
                    await session.commit()
                    await session.refresh(job)
                    print(f"Job created: {job.id}")

                    # Create generation task (don't fire-and-forget)
                    task = asyncio.create_task(
                        generate_single_short(
                            job_id=str(job.id),
                            lesson_path=lesson_path,
                            target_duration=settings.target_duration,
                        )
                    )
                    generation_tasks.append(task)

                print(f"Created {len(generation_tasks)} generation tasks")

                # Wait for all tasks to complete (with timeout handling)
                if generation_tasks:
                    try:
                        await asyncio.gather(*generation_tasks, return_exceptions=True)
                        print(f"All {len(generation_tasks)} generation tasks completed")
                    except Exception as e:
                        print(f"Error in generation tasks: {e}")

                # Update last_run and calculate next_run
                settings.last_run = now

                # Calculate next run time with proper timezone conversion
                try:
                    user_tz = ZoneInfo(settings.timezone)
                except Exception:
                    user_tz = ZoneInfo("UTC")

                now_user_tz = now.astimezone(user_tz)
                hour, minute = map(int, settings.schedule_time.split(":"))
                next_run_user_tz = now_user_tz.replace(hour=hour, minute=minute, second=0, microsecond=0)

                # If the time has passed today, schedule for tomorrow
                if next_run_user_tz <= now_user_tz:
                    next_run_user_tz += timedelta(days=1)

                # Convert back to UTC for storage
                next_run = next_run_user_tz.astimezone(ZoneInfo("UTC"))
                settings.next_run = next_run

                await session.commit()

                print(f"=== Automation complete, next run scheduled for {next_run.isoformat()} ===")
            else:
                print(f"Automation not due yet. next_run={settings.next_run.isoformat() if settings.next_run else 'None'}, now={now.isoformat()}")


def get_scheduler() -> AsyncIOScheduler:
    """Get or create the global scheduler instance.

    Returns:
        AsyncIOScheduler: The scheduler instance
    """
    global scheduler

    if scheduler is None:
        scheduler = AsyncIOScheduler()
        logger.info("Created new APScheduler instance")

    return scheduler


async def start_scheduler():
    """Start the automation scheduler.

    This should be called during application startup.
    """
    sched = get_scheduler()

    if not sched.running:
        # Clean up any existing jobs with old IDs (migration cleanup)
        old_job_ids = ["run_automation", "automation_check"]
        for job_id in old_job_ids:
            try:
                if sched.get_job(job_id):
                    sched.remove_job(job_id)
                    logger.info(f"Removed old job: {job_id}")
            except Exception as e:
                logger.debug(f"No existing job {job_id} to remove: {e}")

        # Add the automation job with consistent ID
        sched.add_job(
            run_automation,
            "interval",
            minutes=5,
            id="automation_check",
            replace_existing=True,
            misfire_grace_time=300,  # Allow 5 minutes grace time for missed runs
        )
        sched.start()
        logger.info("Automation scheduler started with job 'automation_check'")

        # Log next scheduled run time
        job = sched.get_job("automation_check")
        if job:
            logger.info(f"Next automation check scheduled at: {job.next_run_time}")
    else:
        logger.info("Scheduler already running")


async def stop_scheduler():
    """Stop the automation scheduler.

    This should be called during application shutdown.
    """
    global scheduler

    if scheduler and scheduler.running:
        scheduler.shutdown()
        logger.info("Automation scheduler stopped")
