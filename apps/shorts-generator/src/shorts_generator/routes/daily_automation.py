"""Daily Automation API Routes for Shorts Generation.

Simple API endpoints for daily video automation:
- POST /api/v1/daily/start - Start daily automation (generates one now, then daily)
- POST /api/v1/daily/stop - Stop daily automation
- POST /api/v1/daily/trigger - Manually trigger one video generation
- GET /api/v1/daily/status - Get automation status
- GET /api/v1/daily/lessons - List pending lessons
"""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, status

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
    hour: int = 9,
    minute: int = 0,
) -> dict[str, Any]:
    """Start daily automation for video generation.

    Generates one video immediately, then schedules daily generation.

    Query Parameters:
        hour: Hour to run daily (0-23, default 9 AM)
        minute: Minute to run daily (0-59, default 0)

    Returns:
        dict with scheduler status and immediate generation result
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


@router.post("/trigger")
async def trigger_generation() -> dict[str, Any]:
    """Manually trigger one video generation.

    Generates one video immediately regardless of schedule.

    Returns:
        dict with generation result
    """
    try:
        result = await trigger_daily_generation()
        return result
    except Exception as e:
        logger.error(f"Failed to trigger generation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger generation: {str(e)}",
        )


@router.get("/status")
async def automation_status() -> dict[str, Any]:
    """Get current automation status.

    Returns:
        dict with status information including total lessons, processed count
    """
    try:
        status_info = get_automation_status()

        # Add video count
        from shorts_generator.database import database_manager

        completed_videos = await database_manager.list_videos(status="completed", limit=1000)
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
