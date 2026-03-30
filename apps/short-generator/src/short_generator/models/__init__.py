"""SQLAlchemy models for Lesson Shorts Generator.

Tables:
- generation_jobs: Job queue and status tracking
- short_videos: Generated video metadata
- scripts: Versioned script storage
- scenes: Individual scene data
- short_likes: User likes
- short_comments: User comments
- short_views: View tracking
- short_analytics: Aggregated analytics
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import String, Text, Integer, TIMESTAMP, DECIMAL, Boolean, BigInteger, ForeignKey, Index, JSON, create_engine, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session


# Helper function for UTC timestamps (replaces deprecated utcnow)
def utcnow() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    @classmethod
    def create_tables(cls, database_url: str):
        """Create all tables in the database.

        This replaces Alembic migrations with automatic table creation.
        Tables are created only if they don't exist.

        Args:
            database_url: Database connection URL
        """
        engine = create_engine(database_url)
        cls.metadata.create_all(engine)
        engine.dispose()


def init_db(database_url: str) -> None:
    """Initialize database tables.

    This function creates all tables if they don't exist.
    Call this on application startup.

    Args:
        database_url: Database connection URL
    """
    Base.create_tables(database_url)


class GenerationJob(Base):
    """Represents a single short video generation job in the queue.

    Attributes:
        id: Unique job identifier (UUID)
        lesson_path: Path to the source lesson (e.g., 01-Part/02-Chapter/03-Lesson.md)
        status: Job status (queued, processing, completed, failed)
        progress: Progress percentage (0-100)
        error_message: Error details if failed
        retry_count: Number of retry attempts
        created_at: When the job was created
        updated_at: Last update timestamp
        completed_at: When the job completed (null if not completed)
        video_id: Reference to generated video (null if not completed)
    """
    __tablename__ = "generation_jobs"

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    lesson_path: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="queued", index=True)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=utcnow, onupdate=utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    video_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("short_videos.id"), nullable=True)

    # Relationship to generated video
    video: Mapped[Optional["ShortVideo"]] = relationship("ShortVideo", back_populates="generation_jobs")

    __table_args__ = (
        Index("ix_generation_jobs_status_created", "status", "created_at"),
    )


class ShortVideo(Base):
    """Represents a generated short video from a lesson.

    Attributes:
        id: Unique video identifier (UUID)
        lesson_path: Path to the source lesson (unique)
        title: Video title
        script: Generated script text
        duration_seconds: Video duration in seconds
        video_url: CDN URL for the video file
        thumbnail_url: CDN URL for the thumbnail image
        captions_url: CDN URL for the captions file (SRT)
        generation_cost: Cost in USD to generate this video
        created_at: When the video was created
    """
    __tablename__ = "short_videos"

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    lesson_path: Mapped[str] = mapped_column(String(500), nullable=False, unique=True, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    script: Mapped[str] = mapped_column(Text, nullable=False)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    video_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    thumbnail_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    captions_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    generation_cost: Mapped[Optional[DECIMAL]] = mapped_column(DECIMAL(10, 4), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=utcnow, index=True)

    # Relationships
    generation_jobs: Mapped[list["GenerationJob"]] = relationship("GenerationJob", back_populates="video")
    scripts: Mapped[list["Script"]] = relationship("Script", back_populates="video")
    scenes: Mapped[list["Scene"]] = relationship("Scene", back_populates="video")
    likes: Mapped[list["ShortLike"]] = relationship("ShortLike", back_populates="video")
    comments: Mapped[list["ShortComment"]] = relationship("ShortComment", back_populates="video")
    views: Mapped[list["ShortView"]] = relationship("ShortView", back_populates="video")
    analytics: Mapped[Optional["ShortAnalytics"]] = relationship("ShortAnalytics", back_populates="video", uselist=False)


class Script(Base):
    """Represents a generated script for a short video.

    Attributes:
        id: Unique script identifier (UUID)
        video_id: Reference to the short video
        hook_text: Opening hook text (5 seconds)
        concepts: JSON array of concept sections with text and visuals
        example_text: Example section text
        cta_text: Call-to-action text
        total_duration: Target duration in seconds
        visual_descriptions: JSON object with visual descriptions for each scene
    """
    __tablename__ = "scripts"

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    video_id: Mapped[UUID] = mapped_column(ForeignKey("short_videos.id"), nullable=False)
    hook_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    concepts: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    example_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cta_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    total_duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    visual_descriptions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Relationship to video
    video: Mapped["ShortVideo"] = relationship("ShortVideo", back_populates="scripts")


class Scene(Base):
    """Represents a single visual scene within a short video.

    Attributes:
        id: Unique scene identifier (UUID)
        video_id: Reference to the short video
        sequence_number: Order of this scene in the video (0-indexed)
        visual_description: Description used for image generation
        image_url: CDN URL for the generated scene image
        text_overlay: Text to overlay on this scene
        duration_seconds: How long this scene lasts
        transition_type: Transition to next scene (fade, slide, etc.)
    """
    __tablename__ = "scenes"

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    video_id: Mapped[UUID] = mapped_column(ForeignKey("short_videos.id"), nullable=False, index=True)
    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False)
    visual_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    text_overlay: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    transition_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Relationship to video
    video: Mapped["ShortVideo"] = relationship("ShortVideo", back_populates="scenes")

    __table_args__ = (
        Index("ix_scenes_video_sequence", "video_id", "sequence_number"),
    )


class ShortLike(Base):
    """Represents a user's like on a short video.

    Attributes:
        id: Unique like identifier (UUID)
        user_id: User who liked the video
        video_id: Video that was liked
        created_at: When the like was created
    """
    __tablename__ = "short_likes"

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    user_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    video_id: Mapped[UUID] = mapped_column(ForeignKey("short_videos.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=utcnow)

    # Relationship to video
    video: Mapped["ShortVideo"] = relationship("ShortVideo", back_populates="likes")

    __table_args__ = (
        Index("ix_short_likes_user_video", "user_id", "video_id", unique=True),
    )


class ShortComment(Base):
    """Represents a user's comment on a short video.

    Attributes:
        id: Unique comment identifier (UUID)
        user_id: User who posted the comment
        video_id: Video that was commented on
        parent_id: Parent comment ID (for threaded replies)
        text: Comment text content
        created_at: When the comment was created
    """
    __tablename__ = "short_comments"

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    user_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    video_id: Mapped[UUID] = mapped_column(ForeignKey("short_videos.id"), nullable=False, index=True)
    parent_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("short_comments.id"), nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=utcnow, index=True)

    # Relationship to video
    video: Mapped["ShortVideo"] = relationship("ShortVideo", back_populates="comments")

    # Self-referential relationship for threaded replies
    parent: Mapped[Optional["ShortComment"]] = relationship("ShortComment", remote_side=[id], back_populates="replies")
    replies: Mapped[list["ShortComment"]] = relationship("ShortComment", back_populates="parent")


class ShortView(Base):
    """Represents a view event on a short video.

    Attributes:
        id: Unique view identifier (UUID)
        user_id: User who viewed the video (null for anonymous)
        video_id: Video that was viewed
        watch_duration_seconds: How long the user watched
        completed: Whether the user watched to completion
        created_at: When the view occurred
    """
    __tablename__ = "short_views"

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    video_id: Mapped[UUID] = mapped_column(ForeignKey("short_videos.id"), nullable=False, index=True)
    watch_duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=utcnow, index=True)

    # Relationship to video
    video: Mapped["ShortVideo"] = relationship("ShortVideo", back_populates="views")

    __table_args__ = (
        Index("ix_short_views_video_created", "video_id", "created_at"),
    )


class ShortAnalytics(Base):
    """Aggregated analytics for a short video.

    This table stores pre-computed analytics for performance.
    Updated periodically by background jobs.

    Attributes:
        id: Unique analytics identifier (UUID)
        video_id: Reference to the short video (unique)
        view_count: Total number of views
        unique_viewers: Number of unique viewers
        avg_watch_duration: Average watch duration in seconds
        completion_rate: Percentage of viewers who completed (0-100)
        ctr_to_lesson: Click-through rate to full lesson (0-100)
        updated_at: Last update timestamp
    """
    __tablename__ = "short_analytics"

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    video_id: Mapped[UUID] = mapped_column(ForeignKey("short_videos.id"), nullable=False, unique=True, index=True)
    view_count: Mapped[int] = mapped_column(BigInteger, default=0)
    unique_viewers: Mapped[int] = mapped_column(Integer, default=0)
    avg_watch_duration: Mapped[Optional[DECIMAL]] = mapped_column(DECIMAL(10, 2), nullable=True)
    completion_rate: Mapped[Optional[DECIMAL]] = mapped_column(DECIMAL(5, 2), nullable=True)
    ctr_to_lesson: Mapped[Optional[DECIMAL]] = mapped_column(DECIMAL(5, 2), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=utcnow, onupdate=utcnow)

    # Relationship to video
    video: Mapped["ShortVideo"] = relationship("ShortVideo", back_populates="analytics")


class AutomationSettings(Base):
    """Automation settings for scheduled video generation.

    Stores configuration for automated short video generation from lessons.
    Settings are used by Celery Beat scheduler.

    Attributes:
        id: Unique settings identifier (UUID)
        enabled: Whether automation is enabled
        schedule_time: Daily schedule time in HH:MM format (UTC)
        timezone: Timezone for schedule (default: UTC)
        batch_limit: Maximum number of videos to generate per run
        target_duration: Target video duration in seconds
        auto_retry: Whether to automatically retry failed generations
        retry_attempts: Number of retry attempts for failed jobs
        notify_on_complete: Whether to send notifications on completion
        selected_parts: List of part IDs to generate from (empty = all)
        last_run: Timestamp of last automation run
        next_run: Timestamp of next scheduled run
        created_at: When settings were created
        updated_at: Last update timestamp
    """
    __tablename__ = "automation_settings"

    id: Mapped[UUID] = mapped_column(default=uuid4, primary_key=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    schedule_time: Mapped[str] = mapped_column(String(10), default="02:00")
    timezone: Mapped[str] = mapped_column(String(50), default="UTC")
    batch_limit: Mapped[int] = mapped_column(Integer, default=10)
    target_duration: Mapped[int] = mapped_column(Integer, default=60)
    auto_retry: Mapped[bool] = mapped_column(Boolean, default=True)
    retry_attempts: Mapped[int] = mapped_column(Integer, default=3)
    notify_on_complete: Mapped[bool] = mapped_column(Boolean, default=True)
    selected_parts: Mapped[dict] = mapped_column(JSON, default=lambda: {})
    last_run: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    next_run: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=utcnow, onupdate=utcnow)
