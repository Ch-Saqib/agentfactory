"""Smart Review models."""

import datetime as dt

from sqlalchemy import Column, DateTime, text
from sqlmodel import Field, SQLModel


class ReviewPriority(str):
    """Review priority levels."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ReviewReason(str):
    """Reasons for review recommendation."""

    WEAK_AREA = "weak_area"
    SPACED_REPETITION = "spaced_repetition"
    PREREQUISITE = "prerequisite"


class ReviewReminder(SQLModel, table=True):
    """An item in the user's review queue."""

    __tablename__ = "review_reminders"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id")
    chapter_slug: str = Field(max_length=200)
    priority: str = Field(default="medium")  # 'high', 'medium', 'low'
    reason: str = Field(default="spaced_repetition")  # Options: 'weak_area', 'spaced_repetition', 'prerequisite'  # noqa: E501
    interval_days: int = Field(default=1)
    due_date: dt.date
    completed: bool = Field(default=False)
    completed_at: dt.datetime | None = None
    created_at: dt.datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=text("NOW()"))
    )
