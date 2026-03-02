"""Smart Review endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.auth import CurrentUser, get_current_user
from ..core.database import get_session
from ..schemas.review import ReviewCompleteRequest, ReviewCompleteResponse, ReviewQueueResponse
from ..services.review import generate_review_queue, mark_review_complete

router = APIRouter()


@router.get("/review/queue", response_model=ReviewQueueResponse)
async def get_review_queue(
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ReviewQueueResponse:
    """Get personalized review queue.

    Returns items recommended for review based on:
    - Weak areas (chapters with <70% average score)
    - Spaced repetition (items due today)
    - Prerequisites for upcoming lessons
    """
    return await generate_review_queue(user.id, session)


@router.post("/review/{review_id}/complete", response_model=ReviewCompleteResponse)
async def complete_review(
    review_id: int,
    request: ReviewCompleteRequest,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ReviewCompleteResponse:
    """Mark a review item as complete.

    Schedules the next review based on performance using FSRS-style intervals:
    - Score >= 80%: Double the interval (up to 90 days)
    - Score < 80%: Reset to 1 day
    """
    return await mark_review_complete(session, user.id, review_id, request)
