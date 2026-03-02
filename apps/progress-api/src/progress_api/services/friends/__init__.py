"""Friends service package."""

from .bonus import (
    accept_friend_request,
    check_buddy_xp_eligibility,
    get_friends_leaderboard,
    get_friends_list,
    send_friend_request,
)

__all__ = [
    "accept_friend_request",
    "check_buddy_xp_eligibility",
    "get_friends_leaderboard",
    "get_friends_list",
    "send_friend_request",
]
