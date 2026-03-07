"""Daily Automation API Routes for Shorts Generation.

Simple API endpoints for daily video automation:
- POST /api/v1/daily/start - Start daily automation (generates one now, then daily)
- POST /api/v1/daily/stop - Stop daily automation
- POST /api/v1/daily/trigger - Manually trigger one video generation
- GET /api/v1/daily/status - Get automation status
- GET /api/v1/daily/lessons - List pending lessons
"""

import asyncio
import logging
from datetime import datetime
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, HTTPException, status

from shorts_generator.services.daily_automation import (
    get_automation_status,
    start_daily_automation,
    stop_daily_automation,
    trigger_daily_generation,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/daily", tags=["daily-automation"])


@router.post("/start")
async def start_automation(
    background_tasks: BackgroundTasks,
    hour: int = 9,
    minute: int = 0,
) -> dict[str, Any]:
    """Start daily automation for video generation (runs in background).

    Generates one video in the background, then schedules daily generation.

    Query Parameters:
        hour: Hour to run daily (0-23, default 9 AM)
        minute: Minute to run daily (0-59, default 0)

    Returns:
        dict with scheduler status
    """
    if not 0 <= hour <= 23:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hour must be between 0 and 23",
        )

    if not 0 <= minute <= 59:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Minute must be between 0 and 59",
        )

    try:
        result = await start_daily_automation(hour=hour, minute=minute)

        # If the immediate generation is included in the result, run it in background
        if "immediate_result" in result:
            # The start_daily_automation function already handles scheduling
            # Just return the status immediately
            return {
                "success": True,
                "message": f"Daily automation started - scheduled for {hour:02d}:{minute:02d} daily",
                "status": "running",
                "schedule": f"{hour:02d}:{minute:02d} daily",
                "note": "Immediate generation runs in background, check /api/v1/status for progress",
            }

        return result
    except Exception as e:
        logger.error(f"Failed to start automation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start automation: {str(e)}",
        )


@router.post("/stop")
async def stop_automation() -> dict[str, Any]:
    """Stop daily automation.

    Returns:
        dict with scheduler status
    """
    try:
        result = await stop_daily_automation()
        return result
    except Exception as e:
        logger.error(f"Failed to stop automation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop automation: {str(e)}",
        )


@router.post("/test")
async def test_endpoint() -> dict[str, str]:
    """Simple test endpoint."""
    logger.info("=== /test endpoint called ===")
    return {"message": "Test successful"}


@router.post("/trigger")
async def trigger_generation(background_tasks: BackgroundTasks) -> dict[str, Any]:
    """Manually trigger one video generation (runs in background).

    Generates one video in the background and returns immediately.
    Use the returned job_id to check status via /api/v1/status/{job_id}.

    Returns:
        dict with job_id for tracking
    """
    # Generate a unique job ID for this trigger
    job_id = f"manual-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid4().hex[:6]}"

    logger.info(f"=== POST /api/v1/daily/trigger - Manual generation triggered | job_id={job_id} ===")

    # Define the background task
    async def run_generation():
        """Run generation in background and update job status."""
        logger.info(f"[{job_id}] Background task started")
        try:
            # Pass the job_id through to ensure consistency
            result = await trigger_daily_generation(job_id=job_id)

            if result.get("success"):
                logger.info(
                    f"[{job_id}] Generation succeeded | "
                    f"chapter_id={result.get('chapter_id')} "
                    f"video_id={result.get('video_id')}"
                )
            else:
                logger.warning(
                    f"[{job_id}] Generation failed | "
                    f"error={result.get('error', result.get('message', 'unknown'))}"
                )
        except Exception as e:
            logger.error(
                f"[{job_id}] Background task failed: {e}",
                exc_info=True,
            )

    # Add task to background
    background_tasks.add_task(run_generation)

    # Return immediately with job_id
    return {
        "success": True,
        "message": "Video generation started in background",
        "job_id": job_id,
        "status_endpoint": f"/api/v1/status/{job_id}",
        "info": "Use the status endpoint to check generation progress",
    }


@router.get("/status")
async def automation_status() -> dict[str, Any]:
    """Get current automation status.

    Returns:
        dict with status information including total lessons, processed count
    """
    logger.info("=== /status endpoint called ===")
    try:
        logger.info("Getting basic automation status...")
        status_info = get_automation_status()
        logger.info(f"Basic status: {status_info}")

        # Add video count
        logger.info("Importing database_manager...")
        from shorts_generator.database import database_manager
        logger.info("database_manager imported")

        logger.info("Calling list_videos...")
        completed_videos = await database_manager.list_videos(status="completed", limit=1000)
        logger.info(f"list_videos returned: {len(completed_videos)} videos")
        status_info["videos_generated"] = len(completed_videos)
        status_info["lessons_remaining"] = max(0, status_info["total_lessons"] - len(completed_videos))

        return status_info
    except Exception as e:
        logger.error(f"Failed to get status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get status: {str(e)}",
        )


@router.get("/lessons")
async def list_pending_lessons(limit: int = 10) -> dict[str, Any]:
    """List lessons that haven't been processed yet.

    Query Parameters:
        limit: Maximum number of lessons to return (default 10)

    Returns:
        dict with pending lessons
    """
    try:
        from shorts_generator.services.daily_automation import get_unchapters_lessons

        lessons = await get_unchapters_lessons(limit=limit)

        return {
            "count": len(lessons),
            "lessons": [
                {
                    "chapter_id": lesson.chapter_id,
                    "chapter_title": lesson.chapter_title,
                    "chapter_number": lesson.chapter_number,
                }
                for lesson in lessons
            ],
        }
    except Exception as e:
        logger.error(f"Failed to list pending lessons: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list pending lessons: {str(e)}",
        )
