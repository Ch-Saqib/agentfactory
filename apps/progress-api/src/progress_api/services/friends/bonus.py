"""Study Buddies service — social learning with friends.

This service handles:
- Friend requests (send, accept, decline)
- Friend list with activity tracking
- Buddy XP eligibility checking
- Friends-only leaderboard
"""

import logging
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...config import settings
from ...core.exceptions import ProgressAPIException
from ...models.friendship import Friendship, FriendshipStatus, SharedActivity
from ...models.progress import UserProgress
from ...models.user import User
from ...schemas.friends import (
    BuddyXpCheckResponse,
    FriendActivity,
    FriendInfo,
    FriendListResponse,
    FriendsLeaderboardEntry,
    FriendsLeaderboardResponse,
)

logger = logging.getLogger(__name__)

# Rate limit: 10 friend requests per hour
MAX_FRIEND_REQUESTS_PER_HOUR = 10


async def send_friend_request(
    session: AsyncSession,
    user_id: str,
    target_username: str,
) -> None:
    """Send a friend request to another user.

    Raises:
        ProgressAPIException: If user not found, already friends, or rate limited
    """
    # Rate limiting check
    one_hour_ago = datetime.now(UTC) - timedelta(hours=1)
    result = await session.execute(
        select(Friendship).where(
            Friendship.requester_id == user_id,
            Friendship.status == FriendshipStatus.PENDING,
            Friendship.created_at >= one_hour_ago,
        )
    )
    recent_requests = len(result.scalars().all())

    if recent_requests >= MAX_FRIEND_REQUESTS_PER_HOUR:
        raise ProgressAPIException(
            error_code="RATE_LIMIT_EXCEEDED",
            message=f"Too many friend requests. Maximum {MAX_FRIEND_REQUESTS_PER_HOUR} per hour.",
            status_code=429,
        )

    # Find target user by username (or email)
    result = await session.execute(
        select(User).where(
            (User.id == target_username) | (User.email == target_username)
        )
    )
    target_user = result.scalar_one_or_none()

    if not target_user:
        raise ProgressAPIException(
            error_code="USER_NOT_FOUND",
            message="User not found. Check the username and try again.",
            status_code=404,
        )

    if target_user.id == user_id:
        raise ProgressAPIException(
            error_code="CANNOT_FRIEND_SELF",
            message="You cannot send a friend request to yourself.",
            status_code=400,
        )

    # Check if relationship already exists
    result = await session.execute(
        select(Friendship).where(
            ((Friendship.requester_id == user_id) & (Friendship.accepter_id == target_user.id))
            | ((Friendship.requester_id == target_user.id) & (Friendship.accepter_id == user_id))
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        if existing.status == FriendshipStatus.ACCEPTED:
            raise ProgressAPIException(
                error_code="ALREADY_FRIENDS",
                message="You are already friends with this user.",
                status_code=400,
            )
        elif existing.status == FriendshipStatus.PENDING:
            if existing.requester_id == user_id:
                raise ProgressAPIException(
                    error_code="REQUEST_ALREADY_SENT",
                    message="Friend request already sent.",
                    status_code=400,
                )
            else:
                raise ProgressAPIException(
                    error_code="REQUEST_PENDING",
                    message="This user already sent you a friend request.",
                    status_code=400,
                )

    # Create friend request
    # In dev mode, auto-accept friend requests
    status = FriendshipStatus.ACCEPTED if settings.dev_mode else FriendshipStatus.PENDING
    friendship = Friendship(
        requester_id=user_id,
        accepter_id=target_user.id,
        status=status,
    )
    session.add(friendship)
    await session.commit()


async def accept_friend_request(
    session: AsyncSession,
    user_id: str,
    requester_id: str,
) -> None:
    """Accept a pending friend request.

    Raises:
        ProgressAPIException: If request not found or already processed
    """
    result = await session.execute(
        select(Friendship).where(
            Friendship.requester_id == requester_id,
            Friendship.accepter_id == user_id,
            Friendship.status == FriendshipStatus.PENDING,
        )
    )
    friendship = result.scalar_one_or_none()

    if not friendship:
        raise ProgressAPIException(
            error_code="REQUEST_NOT_FOUND",
            message="Friend request not found or already processed.",
            status_code=404,
        )

    friendship.status = FriendshipStatus.ACCEPTED
    friendship.updated_at = datetime.now(UTC)
    await session.commit()


async def get_friends_list(
    session: AsyncSession,
    user_id: str,
) -> FriendListResponse:
    """Get user's friends list with activity information."""
    # Get accepted friendships (both requester and accepter sides)
    result = await session.execute(
        select(Friendship).where(
            Friendship.status == FriendshipStatus.ACCEPTED,
            ((Friendship.requester_id == user_id) | (Friendship.accepter_id == user_id)),
        )
    )
    friendships = result.scalars().all()

    friends = []
    for friendship in friendships:
        # Determine friend_id based on who sent the request
        if friendship.requester_id == user_id:
            friend_id = friendship.accepter_id
        else:
            friend_id = friendship.requester_id

        # Get friend info
        result = await session.execute(
            select(User, UserProgress)
            .join(UserProgress, User.id == UserProgress.user_id)
            .where(User.id == friend_id)
        )
        row = result.one_or_none()
        if not row:
            continue

        friend_user, friend_progress = row

        # Get recent activity
        result = await session.execute(
            select(SharedActivity)
            .where(SharedActivity.user_id == friend_id)
            .order_by(SharedActivity.shared_at.desc())
            .limit(1)
        )
        activity_row = result.scalar_one_or_none()

        last_activity = None
        if activity_row:
            last_activity = FriendActivity(
                activity_type=activity_row.activity_type,
                activity_ref=activity_row.activity_ref,
                completed_at=activity_row.shared_at,
            )

        friends.append(
            FriendInfo(
                user_id=friend_user.id,
                display_name=friend_user.display_name,
                avatar_url=friend_user.avatar_url,
                total_xp=friend_progress.total_xp,
                current_streak=friend_progress.current_streak,
                last_activity=last_activity,
                friendship_status="accepted",
            )
        )

    # Get pending requests (received)
    result = await session.execute(
        select(Friendship).where(
            Friendship.accepter_id == user_id,
            Friendship.status == FriendshipStatus.PENDING,
        )
    )
    pending_rows = result.scalars().all()
    pending_requests = []
    for f in pending_rows:
        result = await session.execute(
            select(User, UserProgress)
            .join(UserProgress, User.id == UserProgress.user_id)
            .where(User.id == f.requester_id)
        )
        row = result.one_or_none()
        if row:
            friend_user, friend_progress = row
            pending_requests.append(
                FriendInfo(
                    user_id=friend_user.id,
                    display_name=friend_user.display_name,
                    avatar_url=friend_user.avatar_url,
                    total_xp=friend_progress.total_xp,
                    current_streak=friend_progress.current_streak,
                    last_activity=None,
                    friendship_status="accepted",
                )
            )

    # Get sent requests
    result = await session.execute(
        select(Friendship).where(
            Friendship.requester_id == user_id,
            Friendship.status == FriendshipStatus.PENDING,
        )
    )
    sent_rows = result.scalars().all()
    sent_requests = []
    for f in sent_rows:
        result = await session.execute(
            select(User, UserProgress)
            .join(UserProgress, User.id == UserProgress.user_id)
            .where(User.id == f.accepter_id)
        )
        row = result.one_or_none()
        if row:
            friend_user, friend_progress = row
            sent_requests.append(
                FriendInfo(
                    user_id=friend_user.id,
                    display_name=friend_user.display_name,
                    avatar_url=friend_user.avatar_url,
                    total_xp=friend_progress.total_xp,
                    current_streak=friend_progress.current_streak,
                    last_activity=None,
                    friendship_status="accepted",
                )
            )

    return FriendListResponse(
        friends=friends,
        pending_requests=pending_requests,
        sent_requests=sent_requests,
    )


async def check_buddy_xp_eligibility(
    session: AsyncSession,
    user_id: str,
    activity_type: str,
    activity_ref: str,
) -> BuddyXpCheckResponse:
    """Check if any friends completed the same activity today.

    Returns +10 XP bonus if eligible.
    """
    # Get friend IDs
    result = await session.execute(
        select(Friendship).where(
            Friendship.status == FriendshipStatus.ACCEPTED,
            ((Friendship.requester_id == user_id) | (Friendship.accepter_id == user_id)),
        )
    )
    friendships = result.scalars().all()

    friend_ids = []
    for f in friendships:
        friend_ids.append(f.accepter_id if f.requester_id == user_id else f.requester_id)

    if not friend_ids:
        return BuddyXpCheckResponse(eligible=False, buddy_xp=0)

    # Check if any friend completed the same activity today
    today = date.today()
    result = await session.execute(
        select(SharedActivity, User)
        .join(User, SharedActivity.user_id == User.id)
        .where(
            SharedActivity.friend_id.in_(friend_ids),
            SharedActivity.activity_type == activity_type,
            SharedActivity.activity_ref == activity_ref,
            SharedActivity.shared_at >= today,
            not SharedActivity.buddy_xp_awarded,  # Not yet awarded
        )
    )
    matches = result.all()

    if not matches:
        return BuddyXpCheckResponse(eligible=False, buddy_xp=0)

    # Get friend names
    friend_names = [row[1].display_name for row in matches]
    buddy_xp = 10 * len(matches)

    return BuddyXpCheckResponse(
        eligible=True,
        buddy_xp=buddy_xp,
        friend_names=friend_names,
    )


async def get_friends_leaderboard(
    session: AsyncSession,
    user_id: str,
) -> FriendsLeaderboardResponse:
    """Get friends-only leaderboard."""
    # Get friend IDs
    result = await session.execute(
        select(Friendship).where(
            Friendship.status == FriendshipStatus.ACCEPTED,
            ((Friendship.requester_id == user_id) | (Friendship.accepter_id == user_id)),
        )
    )
    friendships = result.scalars().all()

    friend_ids = [user_id]  # Include self
    for f in friendships:
        friend_ids.append(f.accepter_id if f.requester_id == user_id else f.requester_id)

    if not friend_ids:
        return FriendsLeaderboardResponse(entries=[], your_rank=None)

    # Get leaderboard data
    result = await session.execute(
        select(User, UserProgress)
        .join(UserProgress, User.id == UserProgress.user_id)
        .where(User.id.in_(friend_ids))
        .order_by(UserProgress.total_xp.desc())
    )
    rows = result.all()

    entries = []
    user_rank = None

    for rank, (user, progress) in enumerate(rows, start=1):
        is_you = user.id == user_id
        if is_you:
            user_rank = rank

        entries.append(
            FriendsLeaderboardEntry(
                rank=rank,
                user_id=user.id,
                display_name=user.display_name,
                avatar_url=user.avatar_url,
                total_xp=progress.total_xp,
                badge_count=progress.badge_count,
                current_streak=progress.current_streak,
                is_you=is_you,
            )
        )

    return FriendsLeaderboardResponse(entries=entries, your_rank=user_rank)
