"""Database Models for Lesson Shorts Generator.

This module defines SQLAlchemy models for:
- Videos (generated short videos)
- Generation Jobs (async job tracking)
- Scripts (versioned script storage)
- Analytics (views, likes, comments)

Uses async SQLAlchemy for NeonDB integration.
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# Base class for all models with AsyncAttrs support
class Base(DeclarativeBase, AsyncAttrs):
    """Base class for all models with async support."""


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(),
        onupdate=lambda: datetime.now(),
        nullable=False,
    )


class Video(Base, TimestampMixin):
    """Generated short video metadata.

    Attributes:
        id: Primary key
        chapter_id: Chapter/lesson identifier
        chapter_title: Title of the chapter
        chapter_number: Chapter number in sequence
        content_snippet: Preview of content text
        video_url: Public URL of the video
        thumbnail_url: URL to thumbnail image
        duration_seconds: Video duration in seconds
        status: Generation status (pending, processing, completed, failed)
        error_message: Error message if failed
        word_count: Number of words in content
        scene_count: Number of scenes in video
        generation_method: How video was generated (google_tts, edge_tts, etc.)
        voice_used: TTS voice used
        file_size_mb: File size in megabytes
        metadata: Additional metadata as JSON
    """

    __tablename__ = "videos"

    id: Mapped[int] = mapped_column(primary_key=True)
    chapter_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    chapter_title: Mapped[str] = mapped_column(String(255), nullable=False)
    chapter_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    content_snippet: Mapped[str] = mapped_column(Text, nullable=True)

    # Video Details
    video_url: Mapped[str] = mapped_column(String(500), nullable=False)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    duration_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    file_size_mb: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Status & Metadata
    status: Mapped[str] = mapped_column(
        String(50), default="pending", nullable=False, index=True
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Content Stats
    word_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    scene_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Generation Metadata
    generation_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    voice_used: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Relationships
    analytics: Mapped[list["VideoAnalytics"]] = relationship(
        "VideoAnalytics", back_populates="video", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Video(id={self.id}, chapter_id={self.chapter_id}, status={self.status})>"


# Alias for backward compatibility
ShortVideo = Video


class GenerationJob(Base, TimestampMixin):
    """Async job tracking for video generation.

    Attributes:
        id: Primary key
        job_id: Unique job identifier (UUID)
        type: Job type (single, batch, automation)
        status: Job status (pending, running, completed, failed)
        chapter_id: Target chapter ID
        input_data: Input parameters as JSON
        result_data: Result data as JSON
        error_message: Error message if failed
        started_at: Job start time
        completed_at: Job completion time
        progress: Progress percentage (0-100)
    """

    __tablename__ = "generation_jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False, index=True)

    chapter_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    input_data: Mapped[Optional[dict[str, Any]]] = mapped_column(Text, nullable=True)
    result_data: Mapped[Optional[dict[str, Any]]] = mapped_column(Text, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    def __repr__(self) -> str:
        return f"<GenerationJob(id={self.id}, job_id={self.job_id}, status={self.status})>"


class Script(Base, TimestampMixin):
    """Versioned script storage.

    Attributes:
        id: Primary key
        chapter_id: Chapter identifier
        script_text: Generated script content
        word_count: Number of words
        estimated_duration: Estimated duration in seconds
        version: Script version
        generation_method: How script was generated
        model_used: AI model used for generation
    """

    __tablename__ = "scripts"

    id: Mapped[int] = mapped_column(primary_key=True)
    chapter_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    script_text: Mapped[str] = mapped_column(Text, nullable=False)
    word_count: Mapped[int] = mapped_column(Integer, nullable=False)
    estimated_duration: Mapped[float] = mapped_column(Float, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    generation_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    model_used: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    def __repr__(self) -> str:
        return f"<Script(id={self.id}, chapter_id={self.chapter_id}, version={self.version})>"


class VideoAnalytics(Base, TimestampMixin):
    """Analytics data for videos.

    Attributes:
        id: Primary key
        video_id: Foreign key to videos table
        views: View count
        likes: Like count
        comments: Comment count
        shares: Share count
        watch_time: Total watch time in seconds
        completion_rate: Average completion rate (0-1)
    """

    __tablename__ = "video_analytics"

    id: Mapped[int] = mapped_column(primary_key=True)
    video_id: Mapped[int] = mapped_column(ForeignKey("videos.id"), nullable=False, unique=True)

    views: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    likes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    comments: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    shares: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    watch_time: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    completion_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Relationship
    video: Mapped["Video"] = relationship("Video", back_populates="analytics")

    def __repr__(self) -> str:
        return f"<VideoAnalytics(id={self.id}, views={self.views}, likes={self.likes})>"


# Pydantic schemas for API input/output
class VideoCreate(BaseModel):
    """Schema for creating a video record."""

    chapter_id: str
    chapter_title: str
    chapter_number: int | None = None
    content_snippet: str
    video_url: str
    thumbnail_url: str | None = None
    duration_seconds: float
    word_count: int | None = None
    scene_count: int | None = None
    generation_method: str | None = None
    voice_used: str | None = None
    file_size_mb: float | None = None

    model_config = ConfigDict(from_attributes=True)


class VideoUpdate(BaseModel):
    """Schema for updating a video record."""

    status: str | None = None
    thumbnail_url: str | None = None
    error_message: str | None = None
    progress: int | None = None


class VideoResponse(BaseModel):
    """Schema for video response."""

    id: int
    chapter_id: str
    chapter_title: str
    chapter_number: int | None
    content_snippet: str
    video_url: str
    thumbnail_url: str | None
    duration_seconds: float
    file_size_mb: float | None
    status: str
    word_count: int | None
    scene_count: int | None
    generation_method: str | None
    voice_used: str | None
    created_at: datetime
    updated_at: datetime

    # Analytics (if included)
    views: int | None = None
    likes: int | None = None
    comments: int | None = None

    model_config = ConfigDict(from_attributes=True)


class GenerationJobCreate(BaseModel):
    """Schema for creating a generation job."""

    chapter_id: str
    type: str  # single, batch, automation
    input_data: dict[str, Any]


class GenerationJobResponse(BaseModel):
    """Schema for generation job response."""

    id: int
    job_id: str
    type: str
    status: str
    chapter_id: str | None
    progress: int
    input_data: dict[str, Any] | None
    result_data: dict[str, Any] | None
    error_message: str | None
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
