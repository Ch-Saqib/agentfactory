"""Cost monitoring endpoints for shorts generation."""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from shorts_generator.database.connection import get_session
from shorts_generator.services.cost_monitor import CostMonitor, send_budget_alert

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/cost", tags=["Cost Monitoring"])


@router.get("/daily")
async def get_daily_cost(
    date: str | None = Query(
        None, description="Date in YYYY-MM-DD format (default: today)"
    ),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Get daily cost breakdown.

    Args:
        date: Optional date string (YYYY-MM-DD), defaults to today
        session: Database session

    Returns:
        dict with daily cost breakdown

    Raises:
        HTTPException: If date format is invalid
    """
    try:
        parsed_date = None
        if date:
            parsed_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD.",
        )

    monitor = CostMonitor(session)
    return await monitor.get_daily_cost(parsed_date)


@router.get("/monthly")
async def get_monthly_cost(
    year: int | None = Query(None, description="Year (default: current year)"),
    month: int | None = Query(
        None, description="Month 1-12 (default: current month)"
    ),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Get monthly cost breakdown.

    Args:
        year: Optional year, defaults to current year
        month: Optional month, defaults to current month
        session: Database session

    Returns:
        dict with monthly cost breakdown
    """
    monitor = CostMonitor(session)
    return await monitor.get_monthly_cost(year, month)


@router.get("/job/{job_id}")
async def get_job_cost_breakdown(
    job_id: str,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Get detailed cost breakdown for a specific job.

    Args:
        job_id: Job ID to get cost breakdown for
        session: Database session

    Returns:
        dict with job cost breakdown

    Raises:
        HTTPException: If job not found
    """
    try:
        monitor = CostMonitor(session)
        return await monitor.get_job_cost_breakdown(job_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/cache-stats")
async def get_cache_hit_rate(
    days: int = Query(7, description="Number of days to analyze", ge=1, le=90),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Get cache hit rate statistics.

    Args:
        days: Number of days to look back (1-90, default 7)
        session: Database session

    Returns:
        dict with cache statistics
    """
    monitor = CostMonitor(session)
    return await monitor.get_cache_hit_rate(days)


@router.get("/api-usage")
async def get_api_usage_by_service(
    days: int = Query(7, description="Number of days to analyze", ge=1, le=90),
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Get API usage breakdown by service.

    Args:
        days: Number of days to look back (1-90, default 7)
        session: Database session

    Returns:
        dict with API usage per service
    """
    monitor = CostMonitor(session)
    return await monitor.get_api_usage_by_service(days)


@router.get("/alerts")
async def check_budget_alerts(
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Check if budget thresholds are exceeded.

    Returns:
        dict with list of alerts
    """
    monitor = CostMonitor(session)
    alerts = await monitor.check_budget_alerts()

    # Send alerts (non-blocking)
    for alert in alerts:
        # TODO: Get webhook URL from config
        await send_budget_alert(alert)

    return {
        "alerts": alerts,
        "alert_count": len(alerts),
        "has_critical": any(a["severity"] == "critical" for a in alerts),
        "has_warning": any(a["severity"] == "warning" for a in alerts),
    }


@router.get("/summary")
async def get_cost_summary(
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Get overall cost summary.

    Returns:
        dict with cost summary for today, this month, and all time
    """
    monitor = CostMonitor(session)

    daily = await monitor.get_daily_cost()
    monthly = await monitor.get_monthly_cost()

    # All-time stats
    from sqlalchemy import select, func

    from shorts_generator.models import ShortVideo

    result = await session.execute(select(func.count(ShortVideo.id)))
    total_videos = result.scalar() or 0

    cost_result = await session.execute(select(func.sum(ShortVideo.generation_cost)))
    total_cost = float(cost_result.scalar() or 0)

    return {
        "today": {
            "cost_usd": float(daily["total_cost_usd"]),
            "video_count": daily["video_count"],
            "alert_exceeded": daily["alert_exceeded"],
        },
        "this_month": {
            "cost_usd": float(monthly["total_cost_usd"]),
            "video_count": monthly["video_count"],
            "alert_exceeded": monthly["alert_exceeded"],
            "projected_usd": float(monthly.get("projected_monthly", {}).get("projected_usd", 0)),
        },
        "all_time": {
            "total_videos": total_videos,
            "total_cost_usd": round(total_cost, 2),
            "avg_cost_per_video": round(total_cost / total_videos, 4) if total_videos > 0 else 0.0,
        },
    }
