"""Daily Challenges models."""

import datetime as dt
from typing import Any

import sqlalchemy as sa
from sqlmodel import Column, DateTime, Field, Relationship, SQLModel, Text


class ChallengeTemplate(SQLModel, table=True):
    """Reusable challenge template definition."""

    __tablename__ = "challenge_templates"

    id: str = Field(primary_key=True)
    name: str = Field(max_length=100)
    description: str = Field(sa_column=Column(Text))
    config_schema: dict[str, Any] = Field(sa_column=sa.Column(sa.JSON), default={})
    xp_bonus: int = Field(default=50)
    is_active: bool = Field(default=True)
    created_at: dt.datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=sa.text("NOW()"))
    )


class DailyChallenge(SQLModel, table=True):
    """Pre-generated daily challenge."""

    __tablename__ = "daily_challenges"

    id: int | None = Field(default=None, primary_key=True)
    challenge_date: dt.date = Field(unique=True, index=True)
    challenge_type: str = Field(max_length=50)
    title: str = Field(max_length=200)
    description: str = Field(sa_column=Column(Text))
    config: dict[str, Any] = Field(sa_column=sa.Column(sa.JSON), default={})
    xp_bonus: int = Field(default=50)
    created_at: dt.datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=sa.text("NOW()"))
    )

    # Relationship
    user_progress: list["UserChallengeProgress"] = Relationship(back_populates="challenge")  # noqa: F821


class UserChallengeProgress(SQLModel, table=True):
    """User's progress on a specific daily challenge."""

    __tablename__ = "user_challenge_progress"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    challenge_id: int = Field(foreign_key="daily_challenges.id")
    progress: dict[str, Any] = Field(sa_column=sa.Column(sa.JSON), default={})
    completed: bool = Field(default=False, index=True)
    xp_awarded: int = Field(default=0)
    started_at: dt.datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=sa.text("NOW()"))
    )
    completed_at: dt.datetime | None = None

    # Relationships
    challenge: DailyChallenge = Relationship(back_populates="user_progress")
