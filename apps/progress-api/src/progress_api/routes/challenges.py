"""Daily Challenges endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.auth import CurrentUser, get_current_user
from ..core.database import get_session
from ..schemas.challenges import (
    ChallengeCompleteResponse,
    ChallengeHistoryResponse,
    ChallengeProgressUpdate,
    ChallengeResponse,
)
from ..services.challenges.engine import (
    get_challenge_history,
    get_today_challenge,
    update_challenge_progress,
)

router = APIRouter()


@router.get("/challenges/today", response_model=ChallengeResponse)
async def get_today_challenge_endpoint(
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ChallengeResponse:
    """Get today's daily challenge.

    Returns the active challenge for today with the user's current progress.
    Automatically initializes progress tracking if not started.
    """
    return await get_today_challenge(session, user)


@router.post(
    "/challenges/{challenge_id}/progress",
    response_model=ChallengeResponse | ChallengeCompleteResponse,
)
async def update_challenge_progress_endpoint(
    challenge_id: int,
    request: ChallengeProgressUpdate,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ChallengeResponse | ChallengeCompleteResponse:
    """Update progress on a challenge.

    Increments the challenge progress by the specified delta.
    If the challenge is completed, awards bonus XP and returns celebration data.

    Args:
        challenge_id: The ID of the challenge
        request: Contains progress_delta (amount to add)
    """
    return await update_challenge_progress(
        session,
        user,
        challenge_id,
        request.progress_delta,
    )


@router.get("/challenges/history", response_model=ChallengeHistoryResponse)
async def get_challenge_history_endpoint(
    days: int = Query(default=7, ge=1, le=30, description="Number of days to look back"),
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ChallengeHistoryResponse:
    """Get challenge completion history.

    Returns past challenges and their completion status for the specified number of days.
    """
    return await get_challenge_history(session, user, days)
