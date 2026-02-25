"""Cost monitoring and control service for shorts generation.

Tracks daily/monthly costs, alerts on budget exceedance,
provides per-job cost breakdown, monitors cache hit rates,
and tracks API usage by service.
"""

import logging
from datetime import datetime, timedelta, UTC
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from shorts_generator.core.config import settings
from shorts_generator.models import GenerationJob, ShortVideo

logger = logging.getLogger(__name__)


class CostMonitor:
    """Monitor and control costs for shorts generation."""

    # Service costs per operation
    SERVICE_COSTS = {
        "gemini_script": 0.002,  # $0.002 per script
        "pollinations_image": 0.0,  # FREE via Pollinations.ai
        "edge_tts": 0.0,  # Free
        "ffmpeg": 0.0,  # Free (local)
        "r2_storage": 0.015,  # $0.015 per GB per month
    }

    # Budget thresholds
    DAILY_BONUS_THRESHOLD = 10.0  # Alert at $10/day
    MONTHLY_BUDGET_THRESHOLD = 100.0  # Alert at $100/month

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_daily_cost(self, date: Optional[datetime] = None) -> dict:
        """Get cost breakdown for a specific day.

        Args:
            date: Date to get cost for (default: today)

        Returns:
            dict with daily cost breakdown
        """
        if date is None:
            date = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)

        next_day = date + timedelta(days=1)

        # Get completed jobs for the day
        result = await self.session.execute(
            select(GenerationJob)
            .where(GenerationJob.status == "completed")
            .where(GenerationJob.created_at >= date)
            .where(GenerationJob.created_at < next_day)
        )
        jobs = result.scalars().all()

        # Get videos for these jobs
        video_ids = [j.video_id for j in jobs if j.video_id]
        if not video_ids:
            return self._empty_cost_breakdown(date, "daily")

        videos_result = await self.session.execute(
            select(ShortVideo).where(ShortVideo.id.in_(video_ids))
        )
        videos = videos_result.scalars().all()

        total_cost = sum(v.generation_cost or 0 for v in videos)

        return {
            "date": date.strftime("%Y-%m-%d"),
            "total_cost_usd": round(total_cost, 4),
            "job_count": len(jobs),
            "video_count": len(videos),
            "avg_cost_per_video": round(total_cost / len(videos), 4) if videos else 0,
            "breakdown": {
                "script_generation": round(len(videos) * self.SERVICE_COSTS["gemini_script"], 4),
                "visual_generation": round(len(videos) * 3 * self.SERVICE_COSTS["flux_image"], 4),  # ~3 images per video
                "audio_generation": 0.0,
                "video_assembly": 0.0,
            },
            "alert_threshold": self.DAILY_BONUS_THRESHOLD,
            "alert_exceeded": total_cost > self.DAILY_BONUS_THRESHOLD,
        }

    async def get_monthly_cost(self, year: Optional[int] = None, month: Optional[int] = None) -> dict:
        """Get cost breakdown for a specific month.

        Args:
            year: Year to get cost for (default: current year)
            month: Month to get cost for (default: current month)

        Returns:
            dict with monthly cost breakdown
        """
        now = datetime.now(UTC)
        year = year or now.year
        month = month or now.month

        # Start and end of month
        start_date = datetime(year, month, 1, tzinfo=UTC)
        if month == 12:
            end_date = datetime(year + 1, 1, 1, tzinfo=UTC)
        else:
            end_date = datetime(year, month + 1, 1, tzinfo=UTC)

        # Get completed jobs for the month
        result = await self.session.execute(
            select(GenerationJob)
            .where(GenerationJob.status == "completed")
            .where(GenerationJob.created_at >= start_date)
            .where(GenerationJob.created_at < end_date)
        )
        jobs = result.scalars().all()

        # Get videos for these jobs
        video_ids = [j.video_id for j in jobs if j.video_id]
        if not video_ids:
            return self._empty_cost_breakdown(start_date, "monthly")

        videos_result = await self.session.execute(
            select(ShortVideo).where(ShortVideo.id.in_(video_ids))
        )
        videos = videos_result.scalars().all()

        total_cost = sum(v.generation_cost or 0 for v in videos)

        return {
            "year": year,
            "month": month,
            "total_cost_usd": round(total_cost, 4),
            "job_count": len(jobs),
            "video_count": len(videos),
            "avg_cost_per_video": round(total_cost / len(videos), 4) if videos else 0,
            "breakdown": {
                "script_generation": round(len(videos) * self.SERVICE_COSTS["gemini_script"], 4),
                "visual_generation": round(len(videos) * 3 * self.SERVICE_COSTS["flux_image"], 4),
                "audio_generation": 0.0,
                "video_assembly": 0.0,
            },
            "alert_threshold": self.MONTHLY_BUDGET_THRESHOLD,
            "alert_exceeded": total_cost > self.MONTHLY_BUDGET_THRESHOLD,
            "projected_monthly": self._project_monthly_cost(total_cost, now, start_date, end_date),
        }

    def _project_monthly_cost(
        self, current_cost: float, now: datetime, start_date: datetime, end_date: datetime
    ) -> dict:
        """Project total monthly cost based on current spending."""
        month_days = (end_date - start_date).days
        days_passed = (now - start_date).days + 1

        if days_passed <= 0:
            return {"projected_usd": 0.0, "method": "start_of_month"}

        # Linear projection
        daily_avg = current_cost / days_passed
        projected = daily_avg * month_days

        return {
            "projected_usd": round(projected, 2),
            "method": "linear_projection",
            "days_so_far": days_passed,
            "days_remaining": month_days - days_passed,
            "daily_average": round(daily_avg, 4),
        }

    async def get_job_cost_breakdown(self, job_id: str) -> dict:
        """Get detailed cost breakdown for a specific job.

        Args:
            job_id: Job ID to get cost breakdown for

        Returns:
            dict with job cost breakdown

        Raises:
            ValueError: If job not found
        """
        result = await self.session.execute(
            select(GenerationJob).where(GenerationJob.id == job_id)
        )
        job = result.scalar_one_or_none()

        if not job:
            raise ValueError(f"Job {job_id} not found")

        # Get video if exists
        video = None
        if job.video_id:
            video_result = await self.session.execute(
                select(ShortVideo).where(ShortVideo.id == job.video_id)
            )
            video = video_result.scalar_one_or_none()

        return {
            "job_id": job_id,
            "lesson_path": job.lesson_path,
            "status": job.status,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "total_cost_usd": round(video.generation_cost, 4) if video and video.generation_cost else 0,
            "breakdown": {
                "script_generation": self.SERVICE_COSTS["gemini_script"],
                "visual_generation": 3 * self.SERVICE_COSTS["flux_image"],  # ~3 images
                "audio_generation": self.SERVICE_COSTS["edge_tts"],
                "video_assembly": self.SERVICE_COSTS["ffmpeg"],
            },
            "retry_count": job.retry_count,
        }

    async def get_cache_hit_rate(self, days: int = 7) -> dict:
        """Get cache hit rate for visual generation.

        Args:
            days: Number of days to look back

        Returns:
            dict with cache statistics
        """
        # This would require tracking cache hits in Redis
        # For now, return placeholder data

        return {
            "message": "Cache tracking requires Redis instrumentation",
            "implementation_notes": "Track visual hash lookups in Redis to measure cache hit rate",
            "placeholder_data": {
                "lookups": 1000,
                "hits": 750,
                "misses": 250,
                "hit_rate_percent": 75.0,
                "days_analyzed": days,
            },
        }

    async def get_api_usage_by_service(self, days: int = 7) -> dict:
        """Get API usage breakdown by service.

        Args:
            days: Number of days to look back

        Returns:
            dict with API usage per service
        """
        since = datetime.now(UTC) - timedelta(days=days)

        # Get completed jobs in the period
        result = await self.session.execute(
            select(GenerationJob)
            .where(GenerationJob.status == "completed")
            .where(GenerationJob.created_at >= since)
        )
        jobs = result.scalars().all()

        video_ids = [j.video_id for j in jobs if j.video_id]
        video_count = len(video_ids) if video_ids else 0

        return {
            "period_days": days,
            "since": since.isoformat(),
            "services": {
                "gemini_script": {
                    "calls": video_count,
                    "cost_per_call_usd": self.SERVICE_COSTS["gemini_script"],
                    "total_cost_usd": round(video_count * self.SERVICE_COSTS["gemini_script"], 4),
                },
                "flux_images": {
                    "calls": video_count * 3,  # ~3 images per video
                    "cost_per_call_usd": self.SERVICE_COSTS["flux_image"],
                    "total_cost_usd": round(video_count * 3 * self.SERVICE_COSTS["flux_image"], 4),
                },
                "edge_tts": {
                    "calls": video_count,
                    "cost_per_call_usd": self.SERVICE_COSTS["edge_tts"],
                    "total_cost_usd": 0.0,
                },
            },
        }

    async def check_budget_alerts(self) -> list[dict]:
        """Check if budget thresholds are exceeded.

        Returns:
            list of alert dicts
        """
        alerts = []

        # Check daily budget
        daily_cost = await self.get_daily_cost()
        if daily_cost["alert_exceeded"]:
            alerts.append({
                "severity": "warning",
                "type": "daily_budget_exceeded",
                "threshold": self.DAILY_BONUS_THRESHOLD,
                "actual": daily_cost["total_cost_usd"],
                "message": f"Daily cost ${daily_cost['total_cost_usd']:.2f} exceeds threshold ${self.DAILY_BONUS_THRESHOLD:.2f}",
                "date": daily_cost["date"],
            })

        # Check monthly budget
        monthly_cost = await self.get_monthly_cost()
        if monthly_cost["alert_exceeded"]:
            alerts.append({
                "severity": "critical",
                "type": "monthly_budget_exceeded",
                "threshold": self.MONTHLY_BUDGET_THRESHOLD,
                "actual": monthly_cost["total_cost_usd"],
                "message": f"Monthly cost ${monthly_cost['total_cost_usd']:.2f} exceeds threshold ${self.MONTHLY_BUDGET_THRESHOLD:.2f}",
                "year": monthly_cost["year"],
                "month": monthly_cost["month"],
            })

        # Check projected monthly
        projected = monthly_cost.get("projected_monthly", {}).get("projected_usd", 0)
        if projected > self.MONTHLY_BUDGET_THRESHOLD:
            alerts.append({
                "severity": "warning",
                "type": "projected_monthly_exceeded",
                "threshold": self.MONTHLY_BUDGET_THRESHOLD,
                "actual": projected,
                "message": f"Projected monthly cost ${projected:.2f} exceeds threshold ${self.MONTHLY_BUDGET_THRESHOLD:.2f}",
                "year": monthly_cost["year"],
                "month": monthly_cost["month"],
            })

        return alerts

    def _empty_cost_breakdown(self, date: datetime, period_type: str) -> dict:
        """Return empty cost breakdown when no data exists."""
        return {
            "period": period_type,
            "date": date.strftime("%Y-%m-%d") if period_type == "daily" else date.strftime("%Y-%m"),
            "total_cost_usd": 0.0,
            "job_count": 0,
            "video_count": 0,
            "avg_cost_per_video": 0.0,
            "breakdown": {
                "script_generation": 0.0,
                "visual_generation": 0.0,
                "audio_generation": 0.0,
                "video_assembly": 0.0,
            },
            "alert_threshold": self.DAILY_BONUS_THRESHOLD if period_type == "daily" else self.MONTHLY_BUDGET_THRESHOLD,
            "alert_exceeded": False,
        }


async def send_budget_alert(alert: dict, webhook_url: Optional[str] = None) -> bool:
    """Send budget alert notification.

    Args:
        alert: Alert dict from check_budget_alerts
        webhook_url: Optional webhook URL to send alert to

    Returns:
        True if alert was sent successfully
    """
    logger.warning(f"Budget alert: {alert['message']}")

    # TODO: Implement actual alert delivery
    # - Email notification
    # - Slack webhook
    # - Discord webhook
    # - Custom webhook

    if webhook_url:
        # TODO: Send webhook POST request
        pass

    return True
