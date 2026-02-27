"""Automation settings and scheduling endpoints."""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shorts_generator.database.connection import get_session
from shorts_generator.models import AutomationSettings as AutomationSettingsModel, utcnow

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/automation", tags=["Automation"])


class AutomationSettings(BaseModel):
    """Automation settings model."""

    enabled: bool = False
    schedule_time: str = "02:00"  # HH:MM format
    timezone: str = "UTC"
    batch_limit: int = 10
    target_duration: int = 60
    auto_retry: bool = True
    retry_attempts: int = 3
    notify_on_complete: bool = True
    selected_parts: list[str] = []


class AutomationSettingsResponse(BaseModel):
    """Response with automation settings."""

    enabled: bool
    schedule_time: str
    timezone: str
    batch_limit: int
    target_duration: int
    auto_retry: bool
    retry_attempts: int
    notify_on_complete: bool
    selected_parts: list[str]
    last_run: Optional[str] = None
    next_run: Optional[str] = None


async def get_automation_settings_from_db(session: AsyncSession) -> AutomationSettingsModel:
    """Get automation settings from database.

    Creates default settings if none exist.

    Args:
        session: Database session

    Returns:
        AutomationSettingsModel: Database model instance
    """
    result = await session.execute(
        select(AutomationSettingsModel).order_by(AutomationSettingsModel.created_at.desc())
    )
    settings = result.scalar_one_or_none()

    if not settings:
        # Create default settings
        settings = AutomationSettingsModel(
            enabled=False,
            schedule_time="02:00",
            timezone="UTC",
            batch_limit=10,
            target_duration=60,
            auto_retry=True,
            retry_attempts=3,
            notify_on_complete=True,
            selected_parts={},
        )
        session.add(settings)
        await session.commit()
        await session.refresh(settings)

    return settings


def calculate_next_run(schedule_time: str, timezone_str: str = "UTC") -> Optional[datetime]:
    """Calculate the next run time based on schedule.

    Args:
        schedule_time: Time in HH:MM format (in the user's timezone)
        timezone_str: Timezone string (default: UTC)

    Returns:
        Next run datetime in UTC or None if invalid schedule
    """
    try:
        hour, minute = map(int, schedule_time.split(":"))

        # Get current time in the user's timezone
        try:
            user_tz = ZoneInfo(timezone_str)
        except Exception:
            logger.warning(f"Invalid timezone '{timezone_str}', falling back to UTC")
            user_tz = ZoneInfo("UTC")

        now_utc = utcnow()
        now_user_tz = now_utc.astimezone(user_tz)

        # Create next run time in user's timezone
        next_run_user_tz = now_user_tz.replace(hour=hour, minute=minute, second=0, microsecond=0)

        # If the time has passed today, schedule for tomorrow
        if next_run_user_tz <= now_user_tz:
            next_run_user_tz += timedelta(days=1)

        # Convert back to UTC for storage
        next_run_utc = next_run_user_tz.astimezone(ZoneInfo("UTC"))

        return next_run_utc
    except Exception as e:
        logger.error(f"Error calculating next run: {e}")
        return None


@router.get("/settings", response_model=AutomationSettingsResponse)
async def get_automation_settings(
    session: AsyncSession = Depends(get_session),
) -> AutomationSettingsResponse:
    """Get current automation settings."""
    settings = await get_automation_settings_from_db(session)

    # Convert selected_parts dict to list
    selected_parts_list = list(settings.selected_parts.values()) if settings.selected_parts else []

    # Calculate next run time if enabled
    next_run = None
    if settings.enabled:
        next_run_dt = calculate_next_run(settings.schedule_time, settings.timezone)
        if next_run_dt:
            next_run = next_run_dt.isoformat()

    return AutomationSettingsResponse(
        enabled=settings.enabled,
        schedule_time=settings.schedule_time,
        timezone=settings.timezone,
        batch_limit=settings.batch_limit,
        target_duration=settings.target_duration,
        auto_retry=settings.auto_retry,
        retry_attempts=settings.retry_attempts,
        notify_on_complete=settings.notify_on_complete,
        selected_parts=selected_parts_list,
        last_run=settings.last_run.isoformat() if settings.last_run else None,
        next_run=next_run,
    )


@router.post("/settings")
async def update_automation_settings(
    settings: AutomationSettings,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Update automation settings."""
    logger.info(f"Received automation settings update: enabled={settings.enabled}, schedule_time={settings.schedule_time}, timezone={settings.timezone}")

    # Get existing settings or create new
    result = await session.execute(
        select(AutomationSettingsModel).order_by(AutomationSettingsModel.created_at.desc())
    )
    db_settings = result.scalar_one_or_none()

    logger.info(f"Existing settings in DB: {db_settings.id if db_settings else None}")

    if db_settings:
        # Update existing
        db_settings.enabled = settings.enabled
        db_settings.schedule_time = settings.schedule_time
        db_settings.timezone = settings.timezone
        db_settings.batch_limit = settings.batch_limit
        db_settings.target_duration = settings.target_duration
        db_settings.auto_retry = settings.auto_retry
        db_settings.retry_attempts = settings.retry_attempts
        db_settings.notify_on_complete = settings.notify_on_complete
        # Convert list to dict with part_id as key
        db_settings.selected_parts = {
            str(i): part_id for i, part_id in enumerate(settings.selected_parts)
        }
        # Update next run time
        if settings.enabled:
            next_run_dt = calculate_next_run(settings.schedule_time, settings.timezone)
            if next_run_dt:
                db_settings.next_run = next_run_dt
        else:
            db_settings.next_run = None
    else:
        # Create new settings
        next_run_dt = calculate_next_run(settings.schedule_time, settings.timezone) if settings.enabled else None
        db_settings = AutomationSettingsModel(
            enabled=settings.enabled,
            schedule_time=settings.schedule_time,
            timezone=settings.timezone,
            batch_limit=settings.batch_limit,
            target_duration=settings.target_duration,
            auto_retry=settings.auto_retry,
            retry_attempts=settings.retry_attempts,
            notify_on_complete=settings.notify_on_complete,
            selected_parts={str(i): part_id for i, part_id in enumerate(settings.selected_parts)},
            next_run=next_run_dt,
        )
        session.add(db_settings)

    await session.commit()
    await session.refresh(db_settings)

    logger.info(f"Automation settings saved to DB: id={db_settings.id}, enabled={db_settings.enabled}, schedule_time={db_settings.schedule_time}, timezone={db_settings.timezone}, next_run={db_settings.next_run}")

    return {
        "success": True,
        "message": "Settings saved successfully",
        "settings": {
            "enabled": db_settings.enabled,
            "schedule_time": db_settings.schedule_time,
            "timezone": db_settings.timezone,
            "batch_limit": db_settings.batch_limit,
            "target_duration": db_settings.target_duration,
            "auto_retry": db_settings.auto_retry,
            "retry_attempts": db_settings.retry_attempts,
            "notify_on_complete": db_settings.notify_on_complete,
            "selected_parts": settings.selected_parts,
        },
    }


@router.post("/trigger")
async def trigger_automation_run(
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Manually trigger an automation run.

    This creates generation jobs for lessons that don't have shorts yet,
    based on the current automation settings.
    """
    settings = await get_automation_settings_from_db(session)

    if not settings.enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Automation is disabled. Enable it first.",
        )

    # Import the automation service
    from shorts_generator.services.automation_service import run_automation

    # Run automation synchronously (for debugging)
    logger.info("Manual automation trigger requested (force=True)")
    try:
        await run_automation(force=True)
    except Exception as e:
        logger.error(f"Automation failed: {e}", exc_info=True)
        return {
            "success": False,
            "message": f"Automation failed: {e}",
        }

    return {
        "success": True,
        "message": "Automation run triggered successfully",
    }


@router.get("/available-parts")
async def get_available_parts() -> dict:
    """Get available book parts and chapters from the docs directory.

    Returns a hierarchical structure of parts and chapters found in the
    learn-app/docs directory.
    """
    # Try multiple possible paths for the docs directory
    possible_paths = [
        # Absolute path (production)
        Path("/home/saqib-squad/agentfactory/apps/learn-app/docs"),
        # Relative path from shorts-generator (development)
        Path(__file__).parent.parent.parent.parent.parent / "learn-app" / "docs",
        # Fallback relative path
        Path("../../../learn-app/docs").resolve(),
    ]

    docs_path = None
    for path in possible_paths:
        if path.exists() and path.is_dir():
            docs_path = path
            logger.info(f"Found docs directory at: {docs_path}")
            break

    if not docs_path:
        logger.warning("Could not find docs directory, tried paths:")
        for path in possible_paths:
            logger.warning(f"  - {path}")
        return {"parts": [], "error": "docs_directory_not_found"}

    parts = []

    try:
        for part_dir in sorted(docs_path.iterdir()):
            if not part_dir.is_dir() or part_dir.name.startswith("."):
                continue

            # Extract part number and name (format: NN-Part-Name)
            name_parts = part_dir.name.split("-", 1)
            if len(name_parts) != 2:
                continue

            part_num = name_parts[0]
            part_name = name_parts[1].replace("-", " ")

            # Count chapters in this part
            chapters = []
            try:
                for chapter_dir in sorted(part_dir.iterdir()):
                    if not chapter_dir.is_dir() or chapter_dir.name.startswith("."):
                        continue

                    chapter_parts = chapter_dir.name.split("-", 1)
                    if len(chapter_parts) != 2:
                        continue

                    chapter_num = chapter_parts[0]
                    chapter_name = chapter_parts[1].replace("-", " ")

                    chapters.append({
                        "id": f"{part_num}-{chapter_num}",
                        "name": chapter_name,
                        "path": f"{part_dir.name}/{chapter_dir.name}",
                    })
            except Exception as e:
                logger.warning(f"Error reading chapters from {part_dir}: {e}")

            parts.append({
                "id": part_num,
                "name": part_name,
                "folder": part_dir.name,
                "chapters": chapters,
            })

        logger.info(f"Found {len(parts)} parts in docs directory")

    except Exception as e:
        logger.error(f"Error reading docs directory: {e}")
        return {"parts": [], "error": str(e)}

    return {"parts": parts}
