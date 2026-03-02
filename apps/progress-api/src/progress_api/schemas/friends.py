"""Friendship and social learning request/response schemas."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class FriendRequest(BaseModel):
    """Send a friend request."""

    username: str = Field(description="Username of the user to befriend")


class FriendAcceptRequest(BaseModel):
    """Accept a friend request."""

    requester_id: str = Field(description="User ID of the requester")


class FriendActivity(BaseModel):
    """Recent activity of a friend."""

    activity_type: str
    activity_ref: str
    completed_at: datetime


class FriendInfo(BaseModel):
    """Information about a friend."""

    user_id: str
    display_name: str
    avatar_url: str | None
    total_xp: int
    current_streak: int
    last_activity: FriendActivity | None = None
    friendship_status: Literal["accepted"]


class FriendListResponse(BaseModel):
    """List of user's friends."""

    friends: list[FriendInfo]
    pending_requests: list[FriendInfo]  # Requests received
    sent_requests: list[FriendInfo]  # Requests sent


class FriendsLeaderboardEntry(BaseModel):
    """Entry in friends leaderboard."""

    rank: int
    user_id: str
    display_name: str
    avatar_url: str | None
    total_xp: int
    badge_count: int
    current_streak: int
    is_you: bool = False


class FriendsLeaderboardResponse(BaseModel):
    """Friends-only leaderboard."""

    entries: list[FriendsLeaderboardEntry]
    your_rank: int | None = None


class BuddyXpCheckRequest(BaseModel):
    """Check buddy XP eligibility."""

    activity_type: str
    activity_ref: str


class BuddyXpCheckResponse(BaseModel):
    """Response for buddy XP check."""

    eligible: bool
    buddy_xp: int = 0
    friend_names: list[str] = []  # Names of friends who completed the same activity
