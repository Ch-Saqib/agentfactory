"""Friendship and social learning models."""

import datetime as dt
from enum import Enum

from sqlalchemy import Column, DateTime, text
from sqlmodel import Field, SQLModel


class FriendshipStatus(str, Enum):
    """Status of a friendship relationship."""

    PENDING = "pending"
    ACCEPTED = "accepted"
    REMOVED = "removed"


class Friendship(SQLModel, table=True):
    """Friend relationship between two users."""

    __tablename__ = "friendships"

    id: int | None = Field(default=None, primary_key=True)
    requester_id: str = Field(foreign_key="users.id")
    accepter_id: str = Field(foreign_key="users.id")
    status: FriendshipStatus = Field(default=FriendshipStatus.PENDING)
    created_at: dt.datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=text("NOW()"))
    )
    updated_at: dt.datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=text("NOW()"))
    )


class SharedActivity(SQLModel, table=True):
    """Activity shared between friends for buddy XP tracking."""

    __tablename__ = "shared_activities"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id")
    friend_id: str = Field(foreign_key="users.id")
    activity_type: str = Field(max_length=50)  # 'quiz', 'lesson', 'flashcard', 'challenge'
    activity_ref: str = Field(max_length=200)  # chapter_slug, lesson_id, etc.
    xp_earned: int = Field(default=0)
    shared_at: dt.datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=text("NOW()"))
    )
    buddy_xp_awarded: bool = Field(default=False)
