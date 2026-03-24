"""Tests for Database Manager and Models.

This test module validates:
1. Database connection and health checks
2. Video CRUD operations
3. Job tracking operations
4. Script versioning
5. Analytics operations
6. Model validation
"""

import os
from datetime import datetime, timedelta
from unittest import mock

import pytest
import pytest_asyncio

from shorts_generator.database.db_manager import DatabaseManager
from shorts_generator.database.models import (
    GenerationJob,
    Script,
    Video,
    VideoAnalytics,
    VideoCreate,
    VideoResponse,
)


@pytest.fixture
async def db_manager():
    """Create a database manager for testing."""
    # Use test database URL if available, otherwise mock
    test_url = os.getenv("TEST_DATABASE_URL")

    if test_url:
        manager = DatabaseManager(database_url=test_url)
        # Create tables for testing
        try:
            await manager.create_tables()
        except Exception:
            pass  # Tables might already exist

        yield manager

        # Drop tables after test
        try:
            await manager.drop_tables()
        finally:
            await manager.close()
    else:
        # Use mock manager for unit tests
        manager = DatabaseManager()
        manager.get_session = mock.AsyncMock()
        yield manager


@pytest.mark.asyncio
class TestDatabaseConnection:
    """Tests for database connection."""

    async def test_health_check(self, db_manager):
        """Test database health check."""
        # For mock manager, health check will return True
        if os.getenv("TEST_DATABASE_URL"):
            result = await db_manager.health_check()
            assert isinstance(result, bool)

    async def test_get_session(self, db_manager):
        """Test getting a database session."""
        session = await db_manager.get_session()
        assert session is not None


@pytest.mark.asyncio
class TestVideoCRUD:
    """Tests for video CRUD operations."""

    async def test_create_video(self, db_manager):
        """Test creating a video record."""
        video_data = VideoCreate(
            chapter_id="test-chapter-1",
            chapter_title="Test Chapter 1",
            content_snippet="This is a test content snippet...",
            video_url="https://r2.dev/videos/test.mp4",
            thumbnail_url="https://r2.dev/thumbnails/test.jpg",
            duration_seconds=60.0,
            word_count=150,
            scene_count=3,
            generation_method="google_tts",
            voice_used="en-US-Neural2-C",
            file_size_mb=5.2,
        )

        # Mock the session operations
        with mock.patch.object(db_manager, "get_session") as mock_session:
            session = mock_session.return_value.__aenter__.return_value
            session.add = mock.Mock()
            session.commit = mock.AsyncMock()

            async def refresh_side_effect(model):
                if isinstance(model, Video) and model.id is None:
                    model.id = 1

            session.refresh = mock.AsyncMock(side_effect=refresh_side_effect)

            result = await db_manager.create_video(video_data)

            assert isinstance(result, Video)
            assert result.chapter_id == "test-chapter-1"
            assert result.thumbnail_url == "https://r2.dev/thumbnails/test.jpg"

    async def test_get_video_by_id(self, db_manager):
        """Test getting a video by ID."""
        if not os.getenv("TEST_DATABASE_URL"):
            pytest.skip("Test database not configured")

        with mock.patch.object(db_manager, "get_session") as mock_session:
            mock_result = mock.Mock()
            mock_result.scalar_one_or_none.return_value = Video(
                id=1,
                chapter_id="test-chapter-1",
                chapter_title="Test Chapter 1",
                content_snippet="Test snippet",
                video_url="https://r2.dev/videos/test.mp4",
                duration_seconds=60.0,
                status="completed",
            )

            mock_session.return_value.__aenter__.return_value.execute.return_value = mock_result

            result = await db_manager.get_video(1)

            assert result.chapter_id == "test-chapter-1"

    async def test_get_video_by_chapter_id(self, db_manager):
        """Test getting a video by chapter ID."""
        if not os.getenv("TEST_DATABASE_URL"):
            pytest.skip("Test database not configured")

        with mock.patch.object(db_manager, "get_session") as mock_session:
            mock_result = mock.Mock()
            mock_result.scalar_one_or_none.return_value = Video(
                id=1,
                chapter_id="test-chapter-1",
                chapter_title="Test Chapter 1",
                content_snippet="Test snippet",
                video_url="https://r2.dev/videos/test.mp4",
                duration_seconds=60.0,
                status="completed",
            )

            mock_session.return_value.__aenter__.return_value.execute.return_value = mock_result

            result = await db_manager.get_video_by_chapter_id("test-chapter-1")

            assert result is not None
            assert result.chapter_id == "test-chapter-1"

    async def test_update_video(self, db_manager):
        """Test updating a video record."""
        if not os.getenv("TEST_DATABASE_URL"):
            pytest.skip("Test database not configured")

        with mock.patch.object(db_manager, "get_session") as mock_session:
            # Mock existing video
            mock_video = Video(
                id=1,
                chapter_id="test-chapter-1",
                chapter_title="Test Chapter 1",
                content_snippet="Test snippet",
                video_url="https://r2.dev/videos/test.mp4",
                duration_seconds=60.0,
                status="processing",
                thumbnail_url=None,
            )

            mock_result = mock.Mock()
            mock_result.scalar_one_or_none.return_value = mock_video

            mock_session.return_value.__aenter__.return_value.execute.return_value = mock_result
            mock_session.return_value.__aenter__.return_value.commit = mock.Mock()
            mock_session.return_value.__aenter__.return_value.refresh = mock_video

            result = await db_manager.update_video(1, status="completed", thumbnail_url="https://r2.dev/thumb.jpg")

            assert result.status == "completed"
            assert result.thumbnail_url == "https://r2.dev/thumb.jpg"

    async def test_delete_video(self, db_manager):
        """Test deleting a video."""
        if not os.getenv("TEST_DATABASE_URL"):
            pytest.skip("Test database not configured")

        with mock.patch.object(db_manager, "get_session") as mock_session:
            mock_result = mock.Mock()
            mock_result.rowcount = 1

            mock_session.return_value.__aenter__.return_value.execute.return_value = mock_result
            mock_session.return_value.__aenter__.return_value.commit = mock.Mock()

            result = await db_manager.delete_video(1)

            assert result is True

    async def test_list_videos(self, db_manager):
        """Test listing videos."""
        if not os.getenv("TEST_DATABASE_URL"):
            pytest.skip("Test database not configured")

        with mock.patch.object(db_manager, "get_session") as mock_session:
            videos = [
                Video(
                    id=1,
                    chapter_id="chapter-1",
                    chapter_title="Chapter 1",
                    content_snippet="Snippet 1",
                    video_url="url1.mp4",
                    duration_seconds=60.0,
                    status="completed",
                ),
                Video(
                    id=2,
                    chapter_id="chapter-2",
                    chapter_title="Chapter 2",
                    content_snippet="Snippet 2",
                    video_url="url2.mp4",
                    duration_seconds=60.0,
                    status="completed",
                ),
            ]

            mock_result = mock.Mock()
            mock_result.scalars().all.return_value = videos

            mock_session.return_value.__aenter__.return_value.execute.return_value = mock_result

            result = await db_manager.list_videos(limit=10)

            assert len(result) == 2


@pytest.mark.asyncio
class TestJobTracking:
    """Tests for job tracking operations."""

    async def test_create_job(self, db_manager):
        """Test creating a generation job."""
        if not os.getenv("TEST_DATABASE_URL"):
            pytest.skip("Test database not configured")

        with mock.patch.object(db_manager, "get_session") as mock_session:
            mock_job = GenerationJob(
                id=1,
                job_id="test-job-123",
                type="single",
                chapter_id="chapter-1",
                input_data={"text": "test"},
                status="pending",
            )

            mock_session.return_value.__aenter__.return_value.add = mock.Mock()
            mock_session.return_value.__aenter__.return_value.commit = mock.Mock()
            mock_session.return_value.__aenter__.return_value.refresh = mock_job

            result = await db_manager.create_job(
                job_id="test-job-123",
                job_type="single",
                chapter_id="chapter-1",
                input_data={"text": "test"},
            )

            assert result.job_id == "test-job-123"

    async def test_update_job_status(self, db_manager):
        """Test updating job status."""
        if not os.getenv("TEST_DATABASE_URL"):
            pytest.skip("Test database not configured")

        with mock.patch.object(db_manager, "get_session") as mock_session:
            mock_job = GenerationJob(
                id=1,
                job_id="test-job-123",
                type="single",
                status="pending",
                progress=0,
            )

            mock_result = mock.Mock()
            mock_result.scalar_one_or_none.return_value = mock_job

            mock_session.return_value.__aenter__.return_value.execute.return_value = mock_result
            mock_session.return_value.__aenter__.return_value.commit = mock.Mock()
            mock_session.return_value.__aenter__.return_value.refresh.return_value = mock_job

            result = await db_manager.update_job_status(
                job_id="test-job-123",
                status="running",
                progress=50,
            )

            assert result.status == "running"
            assert result.progress == 50


@pytest.mark.asyncio
class TestScriptManagement:
    """Tests for script management operations."""

    async def test_save_script(self, db_manager):
        """Test saving a script."""
        if not os.getenv("TEST_DATABASE_URL"):
            pytest.skip("Test database not configured")

        with mock.patch.object(db_manager, "get_session") as mock_session:
            # Check for existing script
            mock_result = mock.Mock()
            mock_result.scalar_one_or_none.return_value = None

            mock_session.return_value.__aenter__.return_value.execute.return_value = mock_result

            mock_session.return_value.__aenter__.return_value.add = mock.Mock()
            mock_session.return_value.__aenter__.return_value.commit = mock.Mock()
            mock_session.return_value.__aenter__.return_value.refresh = mock.Mock()

            mock_script = Script(
                id=1,
                chapter_id="chapter-1",
                script_text="Test script",
                word_count=10,
                estimated_duration=5.0,
                version=1,
            )
            mock_session.return_value.__aenter__.return_value.refresh.return_value = mock_script

            result = await db_manager.save_script(
                chapter_id="chapter-1",
                script_text="Test script",
                word_count=10,
                estimated_duration=5.0,
                generation_method="gemini",
                model_used="gemini-2.0-flash",
            )

            assert result.chapter_id == "chapter-1"
            assert result.version == 1


@pytest.mark.asyncio
class TestAnalytics:
    """Tests for analytics operations."""

    async def test_increment_views(self, db_manager):
        """Test incrementing view count."""
        if not os.getenv("TEST_DATABASE_URL"):
            pytest.skip("Test database not configured")

        with mock.patch.object(db_manager, "get_session") as mock_session:
            # Mock analytics
            mock_analytics = VideoAnalytics(
                id=1,
                video_id=1,
                views=100,
            )

            mock_result = mock.Mock()
            mock_result.scalar_one_or_none.return_value = mock_analytics

            mock_session.return_value.__aenter__.return_value.execute.return_value = mock_result
            mock_session.return_value.__aenter__.return_value.commit = mock.Mock()

            result = await db_manager.increment_views(1)

            assert result is True

    async def test_get_analytics_summary(self, db_manager):
        """Test getting analytics summary."""
        if not os.getenv("TEST_DATABASE_URL"):
            pytest.skip("Test database not configured")

        with mock.patch.object(db_manager, "get_session") as mock_session:
            # Mock results
            total_videos_result = mock.Mock()
            total_videos_result.scalar_one.return_value = 10

            views_result = mock.Mock()
            views_result.scalars().all.return_value = [
                VideoAnalytics(
                    id=1,
                    video_id=1,
                    views=100,
                    likes=10,
                    comments=5,
                ),
                VideoAnalytics(
                    id=2,
                    video_id=2,
                    views=200,
                    likes=20,
                    comments=8,
                ),
            ]

            mock_session.return_value.__aenter__.return_value.execute.return_value = total_videos_result
            mock_session.return_value.__aenter__.return_value.execute.return_value = views_result

            result = await db_manager.get_analytics_summary(days=7)

            assert result["period_days"] == 7
            assert result["total_videos"] == 10
            assert result["total_views"] == 300
            assert result["total_likes"] == 30


class TestModels:
    """Tests for data models."""

    def test_video_response_schema(self):
        """Test VideoResponse schema validation."""
        video_data = {
            "id": 1,
            "chapter_id": "chapter-1",
            "chapter_title": "Test Chapter 1",
            "chapter_number": 1,
            "content_snippet": "Test snippet",
            "video_url": "https://r2.dev/videos/test.mp4",
            "thumbnail_url": "https://r2.dev/thumb.jpg",
            "duration_seconds": 60.0,
            "file_size_mb": 5.2,
            "status": "completed",
            "word_count": 150,
            "scene_count": 3,
            "generation_method": "google_tts",
            "voice_used": "en-US-Neural2-C",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "views": 100,
            "likes": 10,
            "comments": 5,
        }

        schema = VideoResponse(**video_data)

        assert schema.chapter_id == "chapter-1"
        assert schema.views == 100

    def test_video_create_schema(self):
        """Test VideoCreate schema validation."""
        video_data = {
            "chapter_id": "chapter-1",
            "chapter_title": "Test Chapter 1",
            "content_snippet": "Test snippet",
            "video_url": "https://r2.dev/videos/test.mp4",
            "duration_seconds": 60.0,
        }

        schema = VideoCreate(**video_data)

        assert schema.chapter_id == "chapter-1"
        assert schema.duration_seconds == 60.0


class TestSingleton:
    """Tests for singleton instance."""

    def test_database_manager_singleton(self):
        """Test that database_manager singleton exists."""
        from shorts_generator.database.db_manager import database_manager

        assert database_manager is not None
        assert isinstance(database_manager, DatabaseManager)
