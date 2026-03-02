"""Achievement Roadmap models."""

import datetime as dt
from typing import Any, Optional

import sqlalchemy as sa
from sqlmodel import Column, DateTime, Field, Relationship, SQLModel, Text


class RoadmapNode(SQLModel, table=True):
    """A node in the achievement roadmap (part, chapter, or milestone)."""

    __tablename__ = "achievement_nodes"

    id: str = Field(primary_key=True)
    parent_id: str | None = Field(default=None, foreign_key="achievement_nodes.id")
    node_type: str = Field(max_length=20)  # 'part', 'chapter', 'milestone'
    title: str = Field(max_length=200)
    description: str | None = Field(sa_column=Column(Text), default=None)
    position_x: int = Field(default=0)
    position_y: int = Field(default=0)
    config: dict[str, Any] = Field(sa_column=sa.Column(sa.JSON), default={})
    required_xp: int = Field(default=0)
    icon: str | None = Field(default=None, max_length=50)
    created_at: dt.datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=sa.text("NOW()"))
    )

    # Relationships
    parent: Optional["RoadmapNode"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "RoadmapNode.id"},
    )
    children: list["RoadmapNode"] = Relationship(back_populates="parent")
    user_progress: list["UserAchievementProgress"] = Relationship(back_populates="node")  # noqa: F821


class UserAchievementProgress(SQLModel, table=True):
    """User's unlock status for a roadmap node."""

    __tablename__ = "user_achievement_progress"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id")
    node_id: str = Field(foreign_key="achievement_nodes.id")
    unlocked_at: dt.datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=sa.text("NOW()"))
    )

    # Relationships
    node: RoadmapNode = Relationship(back_populates="user_progress")
