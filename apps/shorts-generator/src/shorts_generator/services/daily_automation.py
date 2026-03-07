"""Daily Automation Service for Shorts Generation.

This service automatically:
- Discovers new chapters from the docs directory
- Generates one video per day
- Tracks which chapters have been processed
- Provides simple trigger/stop controls

Usage:
    # Start automation (generates one video immediately, then schedules daily)
    await start_daily_automation()

    # Trigger manually
    await trigger_daily_generation()

    # Stop automation
    await stop_daily_automation()
"""

import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from shorts_generator.core.config import settings
from shorts_generator.database import database_manager
from shorts_generator.services.pipeline_orchestrator import ChapterInput, get_pipeline_orchestrator

logger = logging.getLogger(__name__)

# Scheduler instance
scheduler: AsyncIOScheduler | None = None

# Docs path
DOCS_PATH = Path("/home/saqib-squad/agentfactory/apps/learn-app/docs")


async def get_unchapters_lessons(limit: int = 1) -> list[ChapterInput]:
    """Find lessons that don't have videos yet.

    Args:
        limit: Maximum number of lessons to return

    Returns:
        List of ChapterInput objects for unprocessed lessons
    """
    logger.info(f"=== get_unchapters_lessons called with limit={limit} ===")

    # Get all existing chapter_ids from database
    logger.info("get_unchapters_lessons: Calling database_manager.list_videos...")
    existing_videos = await database_manager.list_videos(status="completed")
    logger.info(f"get_unchapters_lessons: Got {len(existing_videos)} existing videos")
    existing_chapter_ids = {v.chapter_id for v in existing_videos}

    # Find all markdown files in docs directory
    unprocessed = []

    if not DOCS_PATH.exists():
        logger.warning(f"Docs path not found: {DOCS_PATH}")
        return unprocessed

    # Iterate through parts (NN-Part-Name directories)
    for part_dir in sorted(DOCS_PATH.iterdir()):
        if not part_dir.is_dir() or not part_dir.name[:2].isdigit():
            continue

        # Iterate through chapters (NN-Chapter-Name directories)
        for chapter_dir in sorted(part_dir.iterdir()):
            if not chapter_dir.is_dir() or not chapter_dir.name[:2].isdigit():
                continue

            # Find lesson files (numbered .md files, skip README/index)
            for lesson_file in sorted(chapter_dir.glob("*.md")):
                # Skip non-lesson files
                skip_patterns = ["README", "index", "quiz", "SUMMARY", "INTRODUCTION", "chapter-"]
                if any(pattern.lower() in lesson_file.name.lower() for pattern in skip_patterns):
                    continue

                # Only process numbered lesson files (01-*.md, 02-*.md, etc.)
                if not lesson_file.name[0].isdigit():
                    continue

                # Create chapter_id from path
                relative_path = lesson_file.relative_to(DOCS_PATH)
                chapter_id = str(relative_path.with_suffix(""))

                # Skip if already processed
                if chapter_id in existing_chapter_ids:
                    continue

                # Read markdown content
                try:
                    with open(lesson_file, encoding="utf-8") as f:
                        markdown_content = f.read()

                    # Extract title - check YAML frontmatter first, then headings
                    title = lesson_file.stem  # Default fallback
                    lines = markdown_content.split("\n")

                    # Check YAML frontmatter for title
                    in_yaml = False
                    for i, line in enumerate(lines[:30]):  # Check first 30 lines
                        line_stripped = line.strip()
                        if line_stripped == "---":
                            if i == 0:
                                in_yaml = True
                            else:
                                break  # End of YAML
                        elif in_yaml and line_stripped.startswith("title:"):
                            # Extract title from YAML (handle quoted and unquoted)
                            title_value = line_stripped[6:].strip()
                            # Remove quotes if present
                            if title_value.startswith('"') and title_value.endswith('"'):
                                title = title_value[1:-1]
                            elif title_value.startswith("'") and title_value.endswith("'"):
                                title = title_value[1:-1]
                            else:
                                title = title_value
                            break

                    # If no title in YAML, check for first heading
                    if title == lesson_file.stem:
                        for line in lines[:30]:
                            line_stripped = line.strip()
                            if line_stripped.startswith("# "):
                                title = line_stripped[2:].strip()
                                break
                            elif line_stripped.startswith("## "):
                                title = line_stripped[3:].strip()
                                break

                    # Extract chapter number
                    try:
                        chapter_number = int(chapter_dir.name[:2])
                    except (ValueError, IndexError):
                        chapter_number = None

                    unprocessed.append(
                        ChapterInput(
                            chapter_id=chapter_id,
                            chapter_title=title,
                            chapter_number=chapter_number,
                            markdown_content=markdown_content,
                            voice_preset="narration_male",
                        )
                    )

                    if len(unprocessed) >= limit:
                        return unprocessed

                except Exception as e:
                    logger.warning(f"Failed to read {lesson_file}: {e}")
                    continue

    return unprocessed


async def generate_daily_video(job_id: str | None = None) -> dict:
    """Generate one video for the daily automation.

    Args:
        job_id: Optional job ID for tracking. If not provided, generates a default one.

    Returns:
        dict with generation result
    """
    # Use provided job_id or generate a default one
    if not job_id:
        job_id = f"daily-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    print(f"\n{'='*60}")
    print(f"🎬 [SERVICE] generate_daily_video() called")
    print(f"🆔 [SERVICE] job_id={job_id}")
    print(f"{'='*60}")
    logger.info(f"=== generate_daily_video: Starting | job_id={job_id} ===")

    try:
        print(f"🔍 [{job_id}] Looking for unprocessed lessons...")
        logger.info("generate_daily_video: Calling get_unchapters_lessons...")
        # Get next unprocessed lesson
        lessons = await get_unchapters_lessons(limit=1)
        logger.info(f"generate_daily_video: Got {len(lessons)} lessons")
        print(f"📚 [{job_id}] Found {len(lessons)} unprocessed lesson(s)")

        if not lessons:
            print(f"⚠️  [{job_id}] No unprocessed lessons found!")
            logger.info("No unprocessed lessons found")
            return {
                "success": False,
                "message": "No unprocessed lessons found",
                "timestamp": datetime.now().isoformat(),
            }

        lesson = lessons[0]
        print(f"📖 [{job_id}] Processing: {lesson.chapter_id}")
        print(f"   └─ Title: {lesson.chapter_title}")
        logger.info(f"Generating video for: {lesson.chapter_id} - {lesson.chapter_title}")

        # Generate video using pipeline orchestrator
        print(f"🎬 [{job_id}] Starting video generation...")
        orchestrator = get_pipeline_orchestrator()
        result = await orchestrator.generate_single(lesson, job_id=job_id)
        print(f"📥 [{job_id}] Generation completed: success={result.success}")

        if result.success:
            logger.info(f"✅ Video generated successfully: {result.video_url}")
            return {
                "success": True,
                "job_id": job_id,
                "chapter_id": lesson.chapter_id,
                "chapter_title": lesson.chapter_title,
                "video_id": result.video_id,
                "video_url": result.video_url,
                "duration_seconds": result.duration_seconds,
                "timestamp": datetime.now().isoformat(),
            }
        else:
            logger.error(f"❌ Video generation failed: {result.error_message}")
            return {
                "success": False,
                "job_id": job_id,
                "chapter_id": lesson.chapter_id,
                "error": result.error_message,
                "timestamp": datetime.now().isoformat(),
            }

    except Exception as e:
        logger.error(f"Daily generation failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


async def trigger_daily_generation(job_id: str | None = None) -> dict:
    """Manually trigger daily video generation.

    Args:
        job_id: Optional job ID for tracking. If not provided, generates a default one.

    Returns:
        dict with generation result
    """
    return await generate_daily_video(job_id=job_id)


async def start_daily_automation(hour: int = 9, minute: int = 0) -> dict:
    """Start daily automation scheduler.

    Args:
        hour: Hour to run daily (0-23, default 9 AM)
        minute: Minute to run daily (0-59, default 0)

    Returns:
        dict with scheduler status
    """
    global scheduler

    if scheduler is None:
        scheduler = AsyncIOScheduler()

    if scheduler.running:
        return {
            "success": False,
            "message": "Automation already running",
            "status": "running",
        }

    # Generate one video immediately on start
    logger.info("Starting daily automation - generating first video now")
    immediate_result = await generate_daily_video()

    # Schedule daily job
    scheduler.add_job(
        generate_daily_video,
        "cron",
        hour=hour,
        minute=minute,
        id="daily_video_generation",
        replace_existing=True,
    )

    scheduler.start()
    logger.info(f"✅ Daily automation started - scheduled for {hour:02d}:{minute:02d} daily")

    return {
        "success": True,
        "message": f"Daily automation started - scheduled for {hour:02d}:{minute:02d} daily",
        "status": "running",
        "immediate_result": immediate_result,
        "schedule": f"{hour:02d}:{minute:02d} daily",
    }


async def stop_daily_automation() -> dict:
    """Stop daily automation scheduler.

    Returns:
        dict with scheduler status
    """
    global scheduler

    if scheduler is None or not scheduler.running:
        return {
            "success": False,
            "message": "Automation not running",
            "status": "stopped",
        }

    scheduler.shutdown()
    logger.info("Daily automation stopped")

    return {
        "success": True,
        "message": "Daily automation stopped",
        "status": "stopped",
    }


def get_automation_status() -> dict:
    """Get current automation status.

    Returns:
        dict with status information
    """
    global scheduler

    # Count total and processed lessons
    total_lessons = 0
    if DOCS_PATH.exists():
        for part_dir in DOCS_PATH.iterdir():
            if part_dir.is_dir() and part_dir.name[:2].isdigit():
                for chapter_dir in part_dir.iterdir():
                    if chapter_dir.is_dir() and chapter_dir.name[:2].isdigit():
                        for lesson_file in chapter_dir.glob("*.md"):
                            if lesson_file.name[0].isdigit() and not any(
                                p in lesson_file.name.lower()
                                for p in ["README", "index", "quiz", "SUMMARY"]
                            ):
                                total_lessons += 1

    return {
        "status": "running" if scheduler and scheduler.running else "stopped",
        "scheduler_configured": scheduler is not None,
        "total_lessons": total_lessons,
        "docs_path": str(DOCS_PATH),
    }


# Cleanup on shutdown
async def cleanup():
    """Cleanup scheduler on shutdown."""
    await stop_daily_automation()
