"""Analytics endpoints for shorts."""

import logging
from collections import defaultdict
from typing import Literal, Union

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from shorts_generator.database.connection import get_session
from shorts_generator.models import (
    ShortVideo,
    ShortLike,
    ShortComment,
    ShortView,
    ShortAnalytics,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])


@router.get("/aggregate")
async def get_aggregate_analytics(
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Get aggregate analytics across all shorts.

    Returns:
        dict with total generated, total cost, top performing shorts

    Raises:
        HTTPException: If database query fails
    """
    # Total shorts generated
    total_result = await session.execute(
        select(func.count(ShortVideo.id))
    )
    total_generated = total_result.scalar() or 0

    # Total cost
    cost_result = await session.execute(
        select(func.sum(ShortVideo.generation_cost))
    )
    total_cost = cost_result.scalar() or 0

    # Average cost per video
    avg_cost = total_cost / total_generated if total_generated > 0 else 0

    # Total engagement (likes + comments + views)
    likes_result = await session.execute(
        select(func.count(ShortLike.id))
    )
    total_likes = likes_result.scalar() or 0

    comments_result = await session.execute(
        select(func.count(ShortComment.id))
    )
    total_comments = comments_result.scalar() or 0

    views_result = await session.execute(
        select(func.count(ShortView.id))
    )
    total_views = views_result.scalar() or 0

    return {
        "total_generated": total_generated,
        "total_cost_usd": round(total_cost, 4),
        "avg_cost_per_video_usd": round(avg_cost, 4),
        "total_likes": total_likes,
        "total_comments": total_comments,
        "total_views": total_views,
        "total_engagement": total_likes + total_comments + total_views,
    }


@router.get("/videos/{video_id}")
async def get_video_analytics(
    video_id: str,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Get detailed analytics for a specific video.

    Args:
        video_id: Video ID to get analytics for
        session: Database session

    Returns:
        dict with view count, unique viewers, engagement metrics

    Raises:
        HTTPException: If video not found
    """
    # Check if video exists
    video_result = await session.execute(
        select(ShortVideo).where(ShortVideo.id == video_id)
    )
    video = video_result.scalar_one_or_none()

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )

    # Count likes
    likes_result = await session.execute(
        select(func.count(ShortLike.id)).where(ShortLike.video_id == video_id)
    )
    like_count = likes_result.scalar() or 0

    # Count comments
    comments_result = await session.execute(
        select(func.count(ShortComment.id)).where(ShortComment.video_id == video_id)
    )
    comment_count = comments_result.scalar() or 0

    # Get all views
    views_result = await session.execute(
        select(ShortView).where(ShortView.video_id == video_id)
    )
    views = views_result.scalars().all()

    # Calculate metrics
    view_count = len(views)
    unique_viewers = len(set(v.user_id for v in views if v.user_id != "anonymous"))

    # Calculate completion rate
    completed_views = [v for v in views if v.completed]
    completion_rate = (
        len(completed_view) / len(views) * 100 if views else 0
    )

    # Average watch duration
    avg_watch_duration = (
        sum(v.watch_duration_seconds for v in views) / len(views) if views else 0
    )

    # Engagement score (likes + comments) / views * 100
    engagement_score = (
        ((like_count + comment_count) / view_count * 100) if view_count > 0 else 0
    )

    return {
        "video_id": video_id,
        "lesson_path": video.chapter_id,
        "title": video.chapter_title,
        "duration_seconds": video.duration_seconds,
        "view_count": view_count,
        "unique_viewers": unique_viewers,
        "like_count": like_count,
        "comment_count": comment_count,
        "avg_watch_duration_seconds": round(avg_watch_duration, 2),
        "completion_rate": round(completion_rate, 2),
        "engagement_score": round(engagement_score, 2),
        "generation_cost_usd": round(video.generation_cost, 4) if video.generation_cost else 0,
    }


@router.get("/top-performing")
async def get_top_performing(
    limit: int = 10,
    sort_by: Literal["views", "likes", "engagement"] = "engagement",
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Get top performing shorts.

    Args:
        limit: Maximum number of results
        sort_by: Metric to sort by (views, likes, or engagement)
        session: Database session

    Returns:
        dict with list of top performing videos
    """
    # Build query based on sort metric
    if sort_by == "views":
        # Count views per video
        query = (
            select(
                ShortVideo.id,
                ShortVideo.chapter_title,
                ShortVideo.chapter_id,
                func.count(ShortView.id).label("metric_count"),
            )
            .join(ShortView, ShortView.video_id == ShortVideo.id)
            .group_by(ShortVideo.id)
            .order_by(func.count(ShortView.id).desc())
            .limit(limit)
        )
    elif sort_by == "likes":
        # Count likes per video
        query = (
            select(
                ShortVideo.id,
                ShortVideo.chapter_title,
                ShortVideo.chapter_id,
                func.count(ShortLike.id).label("metric_count"),
            )
            .join(ShortLike, ShortLike.video_id == ShortVideo.id)
            .group_by(ShortVideo.id)
            .order_by(func.count(ShortLike.id).desc())
            .limit(limit)
        )
    else:  # engagement
        # Calculate engagement as likes + comments
        query = (
            select(
                ShortVideo.id,
                ShortVideo.chapter_title,
                ShortVideo.chapter_id,
                (
                    func.count(ShortLike.id) + func.count(ShortComment.id)
                ).label("metric_count"),
            )
            .outerjoin(ShortLike, ShortLike.video_id == ShortVideo.id)
            .outerjoin(ShortComment, ShortComment.video_id == ShortVideo.id)
            .group_by(ShortVideo.id)
            .order_by((func.count(ShortLike.id) + func.count(ShortComment.id)).desc())
            .limit(limit)
        )

    result = await session.execute(query)
    rows = result.all()

    videos = []
    for row in rows:
        # Get detailed metrics for each video
        video_id = row.id
        likes_result = await session.execute(
            select(func.count(ShortLike.id)).where(ShortLike.video_id == video_id)
        )
        comments_result = await session.execute(
            select(func.count(ShortComment.id)).where(
                ShortComment.video_id == video_id
            )
        )
        views_result = await session.execute(
            select(func.count(ShortView.id)).where(ShortView.video_id == video_id)
        )

        videos.append({
            "video_id": str(row.id),
            "title": row.title,
            "lesson_path": row.lesson_path,
            "metric_count": row.metric_count,
            "like_count": likes_result.scalar() or 0,
            "comment_count": comments_result.scalar() or 0,
            "view_count": views_result.scalar() or 0,
        })

    return {
        "sort_by": sort_by,
        "videos": videos,
    }


@router.get("/ctr-to-lesson")
async def get_ctr_to_lesson(
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Get click-through rate from shorts to full lessons.

    This tracks how many users watched a short then went to the full lesson.

    Returns:
        dict with CTR metrics
    """
    # This would require tracking views/clicks on the "View Lesson" button
    # For now, return a placeholder that can be implemented later

    return {
        "message": "CTR tracking requires lesson page integration",
        "implementation_notes": "Track clicks on 'View Lesson' button and correlate with video views",
        "placeholder_ctr": 0.20,  # 20% placeholder
    }
