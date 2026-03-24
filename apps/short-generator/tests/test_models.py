"""Tests for database models."""

import pytest
from sqlalchemy import select

from shorts_generator.database.connection import get_session, init_db, reset_engine
from shorts_generator.models import (
    Base,
    GenerationJob,
    ShortVideo,
    Script,
    Scene,
    ShortLike,
    ShortComment,
    ShortView,
    ShortAnalytics,
)


@pytest.fixture(autouse=True)
async def setup_database():
    """Set up test database before each test."""
    await init_db()
    yield
    await reset_engine()


async def test_generation_job_creation():
    """Test creating a generation job."""
    async with get_session() as session:
        job = GenerationJob(
            lesson_path="01-Part/02-Chapter/03-Lesson.md",
            status="queued",
        )
        session.add(job)
        await session.commit()
        await session.refresh(job)

        assert job.id is not None
        assert job.lesson_path == "01-Part/02-Chapter/03-Lesson.md"
        assert job.status == "queued"
        assert job.progress == 0


async def test_short_video_creation():
    """Test creating a short video."""
    async with get_session() as session:
        video = ShortVideo(
            lesson_path="01-Part/02-Chapter/03-Lesson.md",
            title="Test Video",
            script="Hook\nConcept\nExample\nCTA",
            duration_seconds=60,
            video_url="https://cdn.example.com/video.mp4",
            thumbnail_url="https://cdn.example.com/thumb.jpg",
        )
        session.add(video)
        await session.commit()
        await session.refresh(video)

        assert video.id is not None
        assert video.title == "Test Video"
        assert video.duration_seconds == 60


async def test_script_relationship():
    """Test script to video relationship."""
    async with get_session() as session:
        video = ShortVideo(
            lesson_path="01-Part/02-Chapter/03-Lesson.md",
            title="Test Video",
            script="Full script text",
            duration_seconds=60,
            video_url="https://cdn.example.com/video.mp4",
            thumbnail_url="https://cdn.example.com/thumb.jpg",
        )
        session.add(video)
        await session.commit()

        script = Script(
            video_id=video.id,
            hook_text="Did you know...",
            concepts={"sections": [{"text": "Concept 1", "visual": "AI art"}]},
            example_text="Here's an example",
            cta_text="Read more at...",
            total_duration=60,
        )
        session.add(script)
        await session.commit()

        # Test relationship
        await session.refresh(video)
        assert len(video.scripts) == 1
        assert video.scripts[0].hook_text == "Did you know..."


async def test_scene_ordering():
    """Test scene sequence ordering."""
    async with get_session() as session:
        video = ShortVideo(
            lesson_path="01-Part/02-Chapter/03-Lesson.md",
            title="Test Video",
            script="Full script",
            duration_seconds=60,
            video_url="https://cdn.example.com/video.mp4",
            thumbnail_url="https://cdn.example.com/thumb.jpg",
        )
        session.add(video)
        await session.commit()

        # Create scenes in reverse order
        scene2 = Scene(video_id=video.id, sequence_number=2, duration_seconds=15)
        scene1 = Scene(video_id=video.id, sequence_number=1, duration_seconds=10)
        scene0 = Scene(video_id=video.id, sequence_number=0, duration_seconds=5)

        session.add_all([scene2, scene1, scene0])
        await session.commit()

        # Query and verify ordering
        result = await session.execute(
            select(Scene).where(Scene.video_id == video.id).order_by(Scene.sequence_number)
        )
        scenes = result.scalars().all()

        assert len(scenes) == 3
        assert scenes[0].sequence_number == 0
        assert scenes[1].sequence_number == 1
        assert scenes[2].sequence_number == 2


async def test_short_like_unique_constraint():
    """Test that a user can only like a video once."""
    async with get_session() as session:
        video = ShortVideo(
            lesson_path="01-Part/02-Chapter/03-Lesson.md",
            title="Test Video",
            script="Full script",
            duration_seconds=60,
            video_url="https://cdn.example.com/video.mp4",
            thumbnail_url="https://cdn.example.com/thumb.jpg",
        )
        session.add(video)
        await session.commit()

        like1 = ShortLike(user_id="user-123", video_id=video.id)
        session.add(like1)
        await session.commit()

        # Try to create duplicate like (should violate unique constraint)
        like2 = ShortLike(user_id="user-123", video_id=video.id)
        session.add(like2)

        with pytest.raises(Exception):  # IntegrityError
            await session.commit()


async def test_comment_threading():
    """Test threaded comment replies."""
    async with get_session() as session:
        video = ShortVideo(
            lesson_path="01-Part/02-Chapter/03-Lesson.md",
            title="Test Video",
            script="Full script",
            duration_seconds=60,
            video_url="https://cdn.example.com/video.mp4",
            thumbnail_url="https://cdn.example.com/thumb.jpg",
        )
        session.add(video)
        await session.commit()

        # Create parent comment
        parent = ShortComment(
            user_id="user-123",
            video_id=video.id,
            text="Great video!",
        )
        session.add(parent)
        await session.commit()

        # Create reply
        reply = ShortComment(
            user_id="user-456",
            video_id=video.id,
            parent_id=parent.id,
            text="I agree!",
        )
        session.add(reply)
        await session.commit()

        # Test relationship
        await session.refresh(parent)
        assert len(parent.replies) == 1
        assert parent.replies[0].text == "I agree!"


async def test_analytics_aggregation():
    """Test analytics model."""
    async with get_session() as session:
        video = ShortVideo(
            lesson_path="01-Part/02-Chapter/03-Lesson.md",
            title="Test Video",
            script="Full script",
            duration_seconds=60,
            video_url="https://cdn.example.com/video.mp4",
            thumbnail_url="https://cdn.example.com/thumb.jpg",
        )
        session.add(video)
        await session.commit()

        analytics = ShortAnalytics(
            video_id=video.id,
            view_count=1000,
            unique_viewers=850,
            avg_watch_duration=45.5,
            completion_rate=70.0,
            ctr_to_lesson=20.0,
        )
        session.add(analytics)
        await session.commit()

        # Test one-to-one relationship
        await session.refresh(video)
        assert video.analytics is not None
        assert video.analytics.view_count == 1000
