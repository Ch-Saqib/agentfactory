"""Database Manager for Lesson Shorts Generator.

This module provides async database operations for:
- Video metadata CRUD
- Job tracking and status updates
- Script versioning
- Analytics tracking
- Connection management

Uses SQLAlchemy async with asyncpg for NeonDB.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Optional

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import selectinload

from shorts_generator.core.config import settings
from shorts_generator.database.models import (
    GenerationJob,
    Script,
    Video,
    VideoAnalytics,
    VideoCreate,
    VideoResponse,
)

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Async database manager for NeonDB operations.

    Features:
    - Connection pooling
    - Async CRUD operations
    - Job tracking
    - Analytics aggregation
    - Automatic retries
    """

    def __init__(self, database_url: str | None = None):
        """Initialize the database manager.

        Args:
            database_url: PostgreSQL connection string (default: from settings)
        """
        # Get database URL from settings or parameter
        database_url = database_url or settings.shorts_database_url

        # Convert postgresql:// to postgresql+asyncpg:// for asyncpg driver
        if database_url.startswith("postgresql://"):
            database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")

        # Remove sslmode from URL if present (asyncpg doesn't support it in URL)
        # We'll pass SSL via connect_args instead
        database_url = database_url.split("?")[0].split("&")[0]

        self.database_url = database_url

        # Lazy initialization - engine is created on first use
        self._engine: Any = None
        self._session_factory: Any = None
        self._initialized = False

        logger.info("Database manager created (lazy initialization)")

    def _ensure_initialized(self) -> None:
        """Ensure database engine is created (lazy initialization)."""
        if not self._initialized:
            logger.info(f"_ensure_initialized: Creating engine for {self.database_url[:50]}...")
            # Create async engine with SSL support for Neon
            self._engine = create_async_engine(
                self.database_url,
                echo=False,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,  # Verify connections before using
                connect_args={
                    "server_settings": {"jit": "off"},  # Disable JIT for better performance on Neon
                    "ssl": True,  # Enable SSL for Neon (asyncpg uses this, not sslmode)
                    "timeout": 10,  # 10 second connection timeout
                },
            )
            logger.info("_ensure_initialized: Engine created")

            # Create session factory
            self._session_factory = async_sessionmaker(
                bind=self._engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )
            logger.info("_ensure_initialized: Session factory created")

            self._initialized = True
            logger.info("Database engine initialized")

    def get_session(self) -> AsyncSession:
        """Get a database session.

        Returns:
            AsyncSession instance
        """
        self._ensure_initialized()
        return self._session_factory()

    async def create_tables(self) -> None:
        """Create all database tables.

        This should be called once during setup.
        """
        self._ensure_initialized()
        from shorts_generator.database.models import Base

        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        logger.info("Database tables created")

    async def drop_tables(self) -> None:
        """Drop all database tables.

        WARNING: This will delete all data!
        """
        from shorts_generator.database.models import Base

        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

        logger.warning("Database tables dropped")

    # Video CRUD Operations

    async def create_video(
        self,
        video_data: VideoCreate,
    ) -> Video:
        """Create a new video record.

        Args:
            video_data: Video creation data

        Returns:
            Created Video object
        """
        async with self.get_session() as session:
            video = Video(
                chapter_id=video_data.chapter_id,
                chapter_title=video_data.chapter_title,
                chapter_number=video_data.chapter_number,
                content_snippet=video_data.content_snippet,
                video_url=video_data.video_url,
                thumbnail_url=video_data.thumbnail_url,
                duration_seconds=video_data.duration_seconds,
                word_count=video_data.word_count,
                scene_count=video_data.scene_count,
                generation_method=video_data.generation_method,
                voice_used=video_data.voice_used,
                file_size_mb=video_data.file_size_mb,
                status="completed",
            )

            session.add(video)
            await session.commit()
            await session.refresh(video)

            # Create analytics record
            analytics = VideoAnalytics(video_id=video.id)
            session.add(analytics)
            await session.commit()

            logger.info(f"Created video record: {video.chapter_id}")

            return video

    async def get_video(self, video_id: int) -> Video | None:
        """Get a video by ID.

        Args:
            video_id: Video ID

        Returns:
            Video object or None
        """
        async with self.get_session() as session:
            result = await session.execute(
                select(Video).where(Video.id == video_id)
            )
            return result.scalar_one_or_none()

    async def get_video_by_chapter_id(self, chapter_id: str) -> Video | None:
        """Get a video by chapter ID.

        Args:
            chapter_id: Chapter identifier

        Returns:
            Video object or None
        """
        async with self.get_session() as session:
            result = await session.execute(
                select(Video).where(Video.chapter_id == chapter_id)
            )
            return result.scalar_one_or_none()

    async def update_video(
        self,
        video_id: int,
        **updates: Any,
    ) -> Video | None:
        """Update a video record.

        Args:
            video_id: Video ID
            **updates: Fields to update

        Returns:
            Updated Video object or None
        """
        async with self.get_session() as session:
            result = await session.execute(
                select(Video).where(Video.id == video_id)
            )
            video = result.scalar_one_or_none()

            if video:
                for key, value in updates.items():
                    if hasattr(video, key):
                        setattr(video, key, value)

                await session.commit()
                await session.refresh(video)

                logger.info(f"Updated video {video_id}")

            return video

    async def delete_video(self, video_id: int) -> bool:
        """Delete a video record.

        Args:
            video_id: Video ID

        Returns:
            True if deleted, False if not found
        """
        async with self.get_session() as session:
            result = await session.execute(
                delete(Video).where(Video.id == video_id)
            )

            if result.rowcount > 0:
                await session.commit()
                logger.info(f"Deleted video {video_id}")
                return True

            return False

    async def list_videos(
        self,
        status: str | None = None,
        limit: int = 20,
        offset: int = 0,
        include_analytics: bool = False,
    ) -> list[Video]:
        """List videos with optional filtering.

        Args:
            status: Filter by status
            limit: Max records to return
            offset: Records to skip
            include_analytics: Include analytics data

        Returns:
            List of Video objects
        """
        logger.info(f"list_videos called: status={status}, limit={limit}")
        logger.info("Calling get_session()...")
        async with self.get_session() as session:
            query = select(Video)

            if status:
                query = query.where(Video.status == status)

            query = query.order_by(Video.created_at.desc()).limit(limit).offset(offset)

            if include_analytics:
                query = query.options(selectinload(Video.analytics))

            result = await session.execute(query)
            return list(result.scalars())

    async def get_videos_for_shorts_page(
        self,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Get videos for display on /shorts page.

        Args:
            limit: Max videos to return

        Returns:
            List of video dictionaries with analytics
        """
        async with self.get_session() as session:
            query = (
                select(Video)
                .where(Video.status == "completed")
                .options(selectinload(Video.analytics))
                .order_by(Video.created_at.desc())
                .limit(limit)
            )

            result = await session.execute(query)
            videos = result.scalars().all()

            # Convert to response format
            response_data = []
            for video in videos:
                video_dict = VideoResponse.model_validate(video).model_dump()
                # Add analytics if available (analytics is a one-to-many relationship)
                if video.analytics:
                    # Use the first/most recent analytics entry
                    analytics = video.analytics[0]
                    video_dict["views"] = analytics.views
                    video_dict["likes"] = analytics.likes
                    video_dict["comments"] = analytics.comments
                else:
                    # Set defaults if no analytics
                    video_dict["views"] = 0
                    video_dict["likes"] = 0
                    video_dict["comments"] = 0

                response_data.append(video_dict)

            return response_data

    # Job Tracking

    async def create_job(
        self,
        job_id: str,
        job_type: str,
        chapter_id: str,
        input_data: dict[str, Any],
    ) -> GenerationJob:
        """Create a generation job.

        Args:
            job_id: Unique job identifier
            job_type: Job type (single, batch, automation)
            chapter_id: Chapter ID
            input_data: Input parameters

        Returns:
            Created GenerationJob object
        """
        async with self.get_session() as session:
            job = GenerationJob(
                job_id=job_id,
                type=job_type,
                chapter_id=chapter_id,
                input_data=json.dumps(input_data) if input_data else None,
                status="pending",
            )

            session.add(job)
            await session.commit()
            await session.refresh(job)

            logger.info(f"Created job {job_id} for {chapter_id}")

            return job

    async def get_job(self, job_id: str) -> GenerationJob | None:
        """Get a job by ID.

        Args:
            job_id: Job ID

        Returns:
            GenerationJob object or None
        """
        async with self.get_session() as session:
            result = await session.execute(
                select(GenerationJob).where(GenerationJob.job_id == job_id)
            )
            return result.scalar_one_or_none()

    async def update_job_status(
        self,
        job_id: str,
        status: str,
        progress: int | None = None,
        error_message: str | None = None,
        result_data: dict[str, Any] | None = None,
    ) -> GenerationJob | None:
        """Update job status.

        Args:
            job_id: Job ID
            status: New status
            progress: Progress percentage
            error_message: Error message if failed
            result_data: Result data

        Returns:
            Updated GenerationJob or None
        """
        async with self.get_session() as session:
            result = await session.execute(
                select(GenerationJob).where(GenerationJob.job_id == job_id)
            )
            job = result.scalar_one_or_none()

            if job:
                job.status = status

                if progress is not None:
                    job.progress = progress

                if status == "running" and job.started_at is None:
                    job.started_at = datetime.now()

                if status in ("completed", "failed") and job.completed_at is None:
                    job.completed_at = datetime.now()

                if error_message:
                    job.error_message = error_message

                if result_data:
                    job.result_data = json.dumps(result_data) if isinstance(result_data, dict) else result_data

                await session.commit()
                await session.refresh(job)

                logger.info(f"Updated job {job_id} status to {status}")

            return job

    async def list_jobs(
        self,
        status: str | None = None,
        chapter_id: str | None = None,
        limit: int = 50,
    ) -> list[GenerationJob]:
        """List generation jobs.

        Args:
            status: Filter by status
            chapter_id: Filter by chapter
            limit: Max records to return

        Returns:
            List of GenerationJob objects
        """
        async with self.get_session() as session:
            query = select(GenerationJob)

            if status:
                query = query.where(GenerationJob.status == status)

            if chapter_id:
                query = query.where(GenerationJob.chapter_id == chapter_id)

            query = query.order_by(GenerationJob.created_at.desc()).limit(limit)

            result = await session.execute(query)
            return list(result.scalars())

    # Script Management

    async def save_script(
        self,
        chapter_id: str,
        script_text: str,
        word_count: int,
        estimated_duration: float,
        generation_method: str,
        model_used: str,
    ) -> Script:
        """Save a script to the database.

        Args:
            chapter_id: Chapter identifier
            script_text: Generated script content
            word_count: Number of words
            estimated_duration: Estimated duration in seconds
            generation_method: How script was generated
            model_used: AI model used

        Returns:
            Created Script object
        """
        async with self.get_session() as session:
            # Check if script exists and increment version
            existing = await session.execute(
                select(Script)
                .where(Script.chapter_id == chapter_id)
                .order_by(Script.version.desc())
                .limit(1)
            )
            existing_script = existing.scalar_one_or_none()

            version = 1 if not existing_script else existing_script.version + 1

            script = Script(
                chapter_id=chapter_id,
                script_text=script_text,
                word_count=word_count,
                estimated_duration=estimated_duration,
                version=version,
                generation_method=generation_method,
                model_used=model_used,
            )

            session.add(script)
            await session.commit()
            await session.refresh(script)

            logger.info(f"Saved script for {chapter_id} (version {version})")

            return script

    async def get_latest_script(self, chapter_id: str) -> Script | None:
        """Get the latest script for a chapter.

        Args:
            chapter_id: Chapter identifier

        Returns:
            Latest Script object or None
        """
        async with self.get_session() as session:
            result = await session.execute(
                select(Script)
                .where(Script.chapter_id == chapter_id)
                .order_by(Script.version.desc())
                .limit(1)
            )
            return result.scalar_one_or_none()

    # Analytics

    async def increment_views(self, video_id: int) -> bool:
        """Increment view count for a video.

        Args:
            video_id: Video ID

        Returns:
            True if successful
        """
        async with self.get_session() as session:
            result = await session.execute(
                select(VideoAnalytics).where(VideoAnalytics.video_id == video_id)
            )
            analytics = result.scalar_one_or_none()

            if analytics:
                analytics.views += 1
                await session.commit()
                logger.info(f"Incremented views for video {video_id}")
                return True

            return False

    async def increment_likes(self, video_id: int) -> bool:
        """Increment like count for a video.

        Args:
            video_id: Video ID

        Returns:
            True if successful
        """
        async with self.get_session() as session:
            result = await session.execute(
                select(VideoAnalytics).where(VideoAnalytics.video_id == video_id)
            )
            analytics = result.scalar_one_or_none()

            if analytics:
                analytics.likes += 1
                await session.commit()
                logger.info(f"Incremented likes for video {video_id}")
                return True

            return False

    async def get_analytics(self, video_id: int) -> VideoAnalytics | None:
        """Get analytics data for a video.

        Args:
            video_id: Video ID

        Returns:
            VideoAnalytics object or None
        """
        async with self.get_session() as session:
            result = await session.execute(
                select(VideoAnalytics).where(VideoAnalytics.video_id == video_id)
            )
            return result.scalar_one_or_none()

    async def get_analytics_summary(
        self,
        days: int = 7,
    ) -> dict[str, Any]:
        """Get analytics summary for recent videos.

        Args:
            days: Number of days to look back

        Returns:
            Summary statistics
        """
        async with self.get_session() as session:
            cutoff_date = datetime.now() - timedelta(days=days)

            # Total videos
            total_videos_result = await session.execute(
                select(Video)
                .where(Video.created_at >= cutoff_date)
                .where(Video.status == "completed")
            )
            total_videos = total_videos_result.scalar_one() or 0

            # Total views
            views_result = await session.execute(
                select(VideoAnalytics)
                .join(Video, VideoAnalytics.video_id == Video.id)
                .where(Video.created_at >= cutoff_date)
            )
            analytics_list = views_result.scalars().all()

            total_views = sum(a.views for a in analytics_list)
            total_likes = sum(a.likes for a in analytics_list)
            total_comments = sum(a.comments for a in analytics_list)

            return {
                "period_days": days,
                "total_videos": total_videos,
                "total_views": total_views,
                "total_likes": total_likes,
                "total_comments": total_comments,
                "average_views_per_video": total_views / total_videos if total_videos > 0 else 0,
                "average_likes_per_video": total_likes / total_videos if total_videos > 0 else 0,
            }

    # Utility Methods

    async def health_check(self) -> bool:
        """Check database connection health.

        Returns:
            True if database is accessible
        """
        try:
            self._ensure_initialized()
            async with self.get_session() as session:
                # Simple query to test connection
                await session.execute(select(1).limit(1))
                return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

    async def close(self) -> None:
        """Close all database connections."""
        if self._initialized and self._engine:
            await self._engine.dispose()
            logger.info("Database connections closed")


# Singleton instance
database_manager = DatabaseManager()
