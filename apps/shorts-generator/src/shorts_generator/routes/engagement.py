"""Engagement endpoints for shorts."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shorts_generator.database.connection import get_session
from shorts_generator.models import ShortLike, ShortComment, ShortView

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/videos", tags=["Engagement"])


class LikeRequest(BaseModel):
    """Request to like/unlike a video."""

    user_id: str


class CommentRequest(BaseModel):
    """Request to comment on a video."""

    user_id: str
    text: str
    parent_id: str | None = None


class ViewTrackingRequest(BaseModel):
    """Request to track video view progress."""

    user_id: str | None = None  # Allow anonymous views
    watch_duration_seconds: int
    completed: bool = False


@router.post("/{video_id}/like", status_code=status.HTTP_201_CREATED)
async def like_video(
    video_id: str,
    request: LikeRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Like a video.

    Args:
        video_id: Video ID to like
        request: Like request with user_id
        session: Database session

    Returns:
        dict with updated like count

    Raises:
        HTTPException: If video not found or already liked
    """
    # Check if video exists
    result = await session.execute(
        select(ShortLike).where(
            ShortLike.video_id == video_id,
            ShortLike.user_id == request.user_id,
        )
    )
    existing_like = result.scalar_one_or_none()

    if existing_like:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already liked",
        )

    # Create like
    like_record = ShortLike(
        user_id=request.user_id,
        video_id=UUID(video_id),
    )

    session.add(like_record)
    await session.commit()

    logger.info(f"User {request.user_id} liked video {video_id}")

    return {"status": "liked", "video_id": video_id}


@router.post("/{video_id}/unlike", status_code=status.HTTP_200_OK)
async def unlike_video(
    video_id: str,
    request: LikeRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Unlike a video.

    Args:
        video_id: Video ID to unlike
        request: Like request with user_id
        session: Database session

    Returns:
        dict with status

    Raises:
        HTTPException: If like not found
    """
    result = await session.execute(
        select(ShortLike).where(
            ShortLike.video_id == video_id,
            ShortLike.user_id == request.user_id,
        )
    )
    existing_like = result.scalar_one_or_none()

    if not existing_like:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Like not found",
        )

    # Delete like
    await session.delete(existing_like)
    await session.commit()

    logger.info(f"User {request.user_id} unliked video {video_id}")

    return {"status": "unliked", "video_id": video_id}


@router.post("/{video_id}/comments", status_code=status.HTTP_201_CREATED)
async def add_comment(
    video_id: str,
    request: CommentRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Add a comment to a video.

    Args:
        video_id: Video ID to comment on
        request: Comment request with user_id, text, and optional parent_id
        session: Database session

    Returns:
        dict with comment ID and metadata

    Raises:
        HTTPException: If video not found or text is empty
    """
    if not request.text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment text cannot be empty",
        )

    # Create comment
    comment = ShortComment(
        user_id=request.user_id,
        video_id=UUID(video_id),
        text=request.text,
        parent_id=UUID(request.parent_id) if request.parent_id else None,
    )

    session.add(comment)
    await session.commit()
    await session.refresh(comment)

    logger.info(f"User {request.user_id} commented on video {video_id}")

    return {
        "comment_id": str(comment.id),
        "text": comment.text,
        "created_at": comment.created_at.isoformat() if comment.created_at else "",
    }


@router.get("/{video_id}/comments")
async def get_comments(
    video_id: str,
    limit: int = 50,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Get comments for a video.

    Args:
        video_id: Video ID
        limit: Maximum number of comments to return
        offset: Number of comments to skip
        session: Database session

    Returns:
        dict with comments list and total count

    Raises:
        HTTPException: If video not found
    """
    # Get top-level comments (no parent)
    query = select(ShortComment).where(
        ShortComment.video_id == video_id,
        ShortComment.parent_id == None,
    ).order_by(ShortComment.created_at.desc())

    result = await session.execute(query)
    comments = result.scalars().all()

    # Convert to response format
    comments_data = []
    for comment in comments:
        # Get replies for this comment
        replies_result = await session.execute(
            select(ShortComment)
            .where(ShortComment.parent_id == comment.id)
            .order_by(ShortComment.created_at.asc())
        )
        replies = replies_result.scalars().all()

        comments_data.append({
            "id": str(comment.id),
            "user_id": comment.user_id,
            "video_id": str(comment.video_id),
            "text": comment.text,
            "parent_id": str(comment.parent_id) if comment.parent_id else None,
            "created_at": comment.created_at.isoformat() if comment.created_at else "",
            "replies": [
                {
                    "id": str(reply),
                    "user_id": reply.user_id,
                    "video_id": str(reply.video_id),
                    "text": reply.text,
                    "parent_id": str(reply.parent_id) if reply.parent_id else None,
                    "created_at": reply.created_at.isoformat() if reply.created_at else "",
                }
                for reply in replies
            ],
        })

    return {
        "comments": comments_data,
        "total_count": len(comments_data),
    }


@router.post("/{video_id}/views")
async def record_view(
    video_id: str,
    request: ViewTrackingRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Record a video view for analytics.

    Args:
        video_id: Video ID
        request: View tracking data
        session: Database session

    Returns:
        dict with status

    Raises:
        HTTPException: If video not found
    """
    # Create view record
    view = ShortView(
        user_id=request.user_id or "anonymous",
        video_id=UUID(video_id),
        watch_duration_seconds=request.watch_duration_seconds,
        completed=request.completed,
    )

    session.add(view)
    await session.commit()

    logger.info(
        f"Recorded view for video {video_id}: {request.watch_duration_seconds}s, "
        f"completed={request.completed}"
    )

    return {
        "status": "recorded",
        "video_id": video_id,
    }


@router.get("/{video_id}/engagement")
async def get_video_engagement(
    video_id: str,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Get engagement stats for a video.

    Args:
        video_id: Video ID
        session: Database session

    Returns:
        dict with like count, comment count, and view count

    Raises:
        HTTPException: If video not found
    """
    # Count likes
    likes_result = await session.execute(
        select(ShortLike).where(ShortLike.video_id == video_id)
    )
    like_count = len(likes_result.scalars().all())

    # Count comments
    comments_result = await session.execute(
        select(ShortComment).where(ShortComment.video_id == video_id)
    )
    comment_count = len(comments_result.scalars().all())

    # Count unique views
    views_result = await session.execute(
        select(ShortView).where(ShortView.video_id == video_id)
    )
    views = views_result.scalars().all()

    unique_viewers = len(set(v.user_id for v in views if v.user_id != "anonymous"))

    # Calculate completion rate
    completed_views = [v for v in views if v.completed]
    completion_rate = (
        len(completed_views) / len(views) * 100 if views else 0
    )

    return {
        "video_id": video_id,
        "like_count": like_count,
        "comment_count": comment_count,
        "view_count": len(views),
        "unique_viewers": unique_viewers,
        "completion_rate": round(completion_rate, 2),
    }
