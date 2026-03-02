"""Study Buddies (Friends) endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.auth import CurrentUser, get_current_user
from ..core.database import get_session
from ..schemas.friends import (
    FriendAcceptRequest,
    FriendListResponse,
    FriendRequest,
    FriendsLeaderboardResponse,
)
from ..services.friends import (
    accept_friend_request,
    check_buddy_xp_eligibility,
    get_friends_leaderboard,
    get_friends_list,
)
from ..services.friends import (
    send_friend_request as send_friend_request_svc,
)

router = APIRouter()


@router.post("/friends/request")
async def send_friend_request_endpoint(
    request: FriendRequest,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Send a friend request to another user.

    Rate limited to 10 requests per hour.
    """
    await send_friend_request_svc(session, user.id, request.username)
    return {"message": "Friend request sent"}


@router.post("/friends/accept")
async def accept_friend_request_endpoint(
    request: FriendAcceptRequest,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Accept a pending friend request."""
    await accept_friend_request(session, user.id, request.requester_id)
    return {"message": "Friend request accepted"}


@router.get("/friends", response_model=FriendListResponse)
async def get_friends_endpoint(
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> FriendListResponse:
    """Get user's friends list.

    Returns:
        - friends: Accepted friendships
        - pending_requests: Requests received from others
        - sent_requests: Requests sent by user
    """
    return await get_friends_list(session, user.id)


@router.get("/friends/leaderboard", response_model=FriendsLeaderboardResponse)
async def get_friends_leaderboard_endpoint(
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> FriendsLeaderboardResponse:
    """Get friends-only leaderboard.

    Shows ranking among friends only, not global leaderboard.
    """
    return await get_friends_leaderboard(session, user.id)


@router.post("/friends/buddy-xp-check")
async def check_buddy_xp_endpoint(
    activity_type: str,
    activity_ref: str,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Check buddy XP eligibility for an activity.

    Called when completing quizzes, lessons, etc.
    Returns +10 XP if a friend completed the same activity today.
    """
    return await check_buddy_xp_eligibility(session, user.id, activity_type, activity_ref)
