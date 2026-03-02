"""Knowledge Checkpoints models."""

import datetime as dt
from typing import Any

import sqlalchemy as sa
from sqlmodel import Column, DateTime, Field, Relationship, SQLModel, Text


class KnowledgeCheckpoint(SQLModel, table=True):
    """A checkpoint question at a specific scroll position in a lesson."""

    __tablename__ = "knowledge_checkpoints"

    id: int | None = Field(default=None, primary_key=True)
    lesson_slug: str = Field(max_length=200)
    position_pct: int = Field(default=50)  # Scroll position (50%, 75%, etc.)
    question_data: dict[str, Any] = Field(sa_column=sa.Column(sa.JSON), default={})
    xp_bonus: int = Field(default=10)
    created_at: dt.datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=sa.text("NOW()"))
    )

    # Relationships
    attempts: list["CheckpointAttempt"] = Relationship(back_populates="checkpoint")  # noqa: F821


class CheckpointAttempt(SQLModel, table=True):
    """User's answer to a checkpoint question."""

    __tablename__ = "checkpoint_attempts"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id")
    checkpoint_id: int = Field(foreign_key="knowledge_checkpoints.id")
    answer: str = Field(sa_column=Column(Text))
    correct: bool = Field(default=False)
    xp_awarded: int = Field(default=0)
    created_at: dt.datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=sa.text("NOW()"))
    )

    # Relationships
    checkpoint: KnowledgeCheckpoint = Relationship(back_populates="attempts")
