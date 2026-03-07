"""Recommendation endpoints for shorts."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from shorts_generator.database.connection import get_session
from shorts_generator.services.recommendation import RecommendationEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/recommendations", tags=["Recommendations"])


class RecommendationsRequest(BaseModel):
    """Request for personalized recommendations."""

    user_id: str | None = None
    limit: int = 10
    current_lesson_path: str | None = None
    exclude_watched: bool = True
    weaker_areas: list[str] = []


class ContinueWatchingRequest(BaseModel):
    """Request for continue watching list."""

    user_id: str
    limit: int = 5


@router.post("/for-you")
async def get_for_you_recommendations(
    request: RecommendationsRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Get personalized "For You" recommendations.

    Args:
        request: Recommendation request with user context
        session: Database session

    Returns:
        dict with list of recommended videos

    Raises:
        HTTPException: If request is invalid
    """
    try:
        engine = RecommendationEngine(session)

        options = {
            "limit": request.limit,
            "current_lesson_path": request.current_lesson_path,
            "exclude_watched": request.exclude_watched,
            "weaker_areas": request.weaker_areas,
        }

        videos = await engine.recommend_for_user(request.user_id, options)

        return {
            "user_id": request.user_id or "anonymous",
            "videos": [
                {
                    "video_id": str(video.id),
                    "title": video.chapter_title,
                    "lesson_path": video.chapter_id,
                    "duration_seconds": video.duration_seconds,
                    "thumbnail_url": video.thumbnail_url,
                    "video_url": video.video_url,
                    "view_count": 0,  # Would need to join with views
                    "like_count": 0,  # Would need to join with likes
                }
                for video in videos
            ],
            "count": len(videos),
        }

    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}",
        )


@router.post("/continue-watching")
async def get_continue_watching(
    request: ContinueWatchingRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Get list of videos user started but didn't complete.

    Args:
        request: Continue watching request
        session: Database session

    Returns:
        dict with list of partially watched videos

    Raises:
        HTTPException: If user_id is not provided
    """
    if not request.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id is required",
        )

    try:
        engine = RecommendationEngine(session)
        videos = await engine.get_continue_watching(
            request.user_id, limit=request.limit
        )

        return {
            "user_id": request.user_id,
            "videos": [
                {
                    "video_id": str(video.id),
                    "title": video.chapter_title,
                    "lesson_path": video.chapter_id,
                    "duration_seconds": video.duration_seconds,
                    "thumbnail_url": video.thumbnail_url,
                    "video_url": video.video_url,
                }
                for video in videos
            ],
            "count": len(videos),
        }

    except Exception as e:
        logger.error(f"Error getting continue watching: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get continue watching: {str(e)}",
        )


@router.get("/trending")
async def get_trending(
    limit: int = 10,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Get trending shorts (most viewed).

    Args:
        limit: Maximum number of results
        session: Database session

    Returns:
        dict with list of trending videos
    """
    try:
        engine = RecommendationEngine(session)
        videos = await engine._get_trending_recommendations(limit)

        return {
            "videos": [
                {
                    "video_id": str(video.id),
                    "title": video.chapter_title,
                    "lesson_path": video.chapter_id,
                    "duration_seconds": video.duration_seconds,
                    "thumbnail_url": video.thumbnail_url,
                    "video_url": video.video_url,
                    "generation_cost_usd": 0.0,  # Not tracked in Video model
                }
                for video in videos
            ],
            "count": len(videos),
        }

    except Exception as e:
        logger.error(f"Error getting trending: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get trending: {str(e)}",
        )
