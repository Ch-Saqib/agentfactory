"""Manual Test Script for Database Manager.

This script tests the DatabaseManager with a real NeonDB connection.
Run this to verify database operations are working correctly.

Usage:
    python scripts/test_db_manager.py

Requirements:
    - NeonDB database running
    - DATABASE_URL environment variable set
    - All database models created
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from shorts_generator.core.config import settings
from shorts_generator.database.db_manager import DatabaseManager
from shorts_generator.database.models import (
    VideoCreate,
)


class Colors:
    """ANSI color codes for terminal output."""

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def print_header(text: str) -> None:
    """Print a formatted header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}\n")


def print_success(text: str) -> None:
    """Print success message."""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text: str) -> None:
    """Print error message."""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_warning(text: str) -> None:
    """Print warning message."""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def print_info(text: str) -> None:
    """Print info message."""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def print_test(name: str) -> None:
    """Print test name."""
    print(f"\n{Colors.BOLD}Testing: {name}{Colors.ENDC}")


async def test_database_connection(db: DatabaseManager) -> bool:
    """Test database connection."""
    print_test("Database Connection")

    try:
        is_healthy = await db.health_check()
        if is_healthy:
            print_success("Database connection successful")
            return True
        else:
            print_error("Database health check failed")
            return False
    except Exception as e:
        print_error(f"Connection failed: {e}")
        return False


async def test_video_crud(db: DatabaseManager) -> bool:
    """Test video CRUD operations."""
    print_test("Video CRUD Operations")

    try:
        # Create a test video
        video_data = VideoCreate(
            chapter_id="test-chapter-db-001",
            chapter_title="Database Test Chapter",
            chapter_number=1,
            content_snippet="This is a test video for database operations...",
            video_url="https://test-bucket.r2.dev/videos/test.mp4",
            duration_seconds=60.5,
            word_count=150,
            scene_count=3,
            generation_method="google_tts",
            voice_used="en-US-Neural2-C",
            file_size_mb=5.2,
        )

        print_info("Creating test video...")
        created_video = await db.create_video(video_data)
        print_success(f"Created video: {created_video.chapter_id} (ID: {created_video.id})")

        # Get video by ID
        print_info("Retrieving video by ID...")
        retrieved_video = await db.get_video(created_video.id)
        if retrieved_video and retrieved_video.chapter_id == "test-chapter-db-001":
            print_success(f"Retrieved video by ID: {retrieved_video.chapter_id}")
        else:
            print_error("Failed to retrieve video by ID")
            return False

        # Get video by chapter ID
        print_info("Retrieving video by chapter ID...")
        chapter_video = await db.get_video_by_chapter_id("test-chapter-db-001")
        if chapter_video:
            print_success(f"Retrieved video by chapter_id: {chapter_video.chapter_id}")
        else:
            print_error("Failed to retrieve video by chapter_id")
            return False

        # Update video
        print_info("Updating video...")
        updated_video = await db.update_video(
            created_video.id,
            status="completed",
            thumbnail_url="https://test-bucket.r2.dev/thumbnails/test.jpg",
        )
        if updated_video and updated_video.thumbnail_url:
            print_success("Updated video with thumbnail")
        else:
            print_error("Failed to update video")
            return False

        # List videos
        print_info("Listing videos...")
        videos = await db.list_videos(limit=10)
        print_success(f"Found {len(videos)} videos")

        # Clean up - delete test video
        print_info("Cleaning up test video...")
        deleted = await db.delete_video(created_video.id)
        if deleted:
            print_success("Deleted test video")
        else:
            print_warning("Failed to delete test video (may need manual cleanup)")

        return True

    except Exception as e:
        print_error(f"Video CRUD test failed: {e}")
        return False


async def test_job_tracking(db: DatabaseManager) -> bool:
    """Test job tracking operations."""
    print_test("Job Tracking Operations")

    try:
        # Create a test job
        import uuid

        job_id = f"test-job-{uuid.uuid4().hex[:8]}"

        print_info("Creating test job...")
        job = await db.create_job(
            job_id=job_id,
            job_type="single",
            chapter_id="test-chapter-job",
            input_data={"text": "test content", "voice": "en-US-Neural2-C"},
        )
        print_success(f"Created job: {job.job_id} (status: {job.status})")

        # Update job status to running
        print_info("Updating job to running...")
        job_running = await db.update_job_status(job_id, status="running", progress=50)
        if job_running and job_running.status == "running":
            print_success(f"Job status updated to: {job_running.status}")
        else:
            print_error("Failed to update job status")
            return False

        # Update job to completed
        print_info("Updating job to completed...")
        job_completed = await db.update_job_status(
            job_id,
            status="completed",
            progress=100,
            result_data={"video_url": "https://test.r2.dev/video.mp4"},
        )
        if job_completed and job_completed.status == "completed":
            print_success(f"Job completed: {job_completed.status}")
        else:
            print_error("Failed to complete job")
            return False

        # Get job
        print_info("Retrieving job...")
        retrieved_job = await db.get_job(job_id)
        if retrieved_job:
            print_success(f"Retrieved job: {retrieved_job.job_id}")
        else:
            print_error("Failed to retrieve job")
            return False

        # List jobs
        print_info("Listing jobs...")
        jobs = await db.list_jobs(limit=10)
        print_success(f"Found {len(jobs)} jobs")

        return True

    except Exception as e:
        print_error(f"Job tracking test failed: {e}")
        return False


async def test_script_management(db: DatabaseManager) -> bool:
    """Test script management operations."""
    print_test("Script Management Operations")

    try:
        # Save a script
        print_info("Saving script...")
        script = await db.save_script(
            chapter_id="test-chapter-script",
            script_text="This is a test script for the database.",
            word_count=10,
            estimated_duration=5.0,
            generation_method="gemini",
            model_used="gemini-2.0-flash",
        )
        print_success(f"Saved script: version {script.version}")

        # Get latest script
        print_info("Retrieving latest script...")
        latest = await db.get_latest_script("test-chapter-script")
        if latest and latest.version == 1:
            print_success(f"Retrieved script version {latest.version}")
        else:
            print_error("Failed to retrieve latest script")
            return False

        # Save another version (test versioning)
        print_info("Saving script version 2...")
        script_v2 = await db.save_script(
            chapter_id="test-chapter-script",
            script_text="This is the updated script version 2.",
            word_count=11,
            estimated_duration=5.5,
            generation_method="gemini",
            model_used="gemini-2.0-flash",
        )
        if script_v2.version == 2:
            print_success(f"Script version incremented to: {script_v2.version}")
        else:
            print_error("Version not incremented correctly")
            return False

        # Verify we get the latest version
        print_info("Verifying latest version retrieval...")
        latest_v2 = await db.get_latest_script("test-chapter-script")
        if latest_v2 and latest_v2.version == 2:
            print_success("Latest version correctly retrieved")
        else:
            print_error("Failed to retrieve latest version")
            return False

        return True

    except Exception as e:
        print_error(f"Script management test failed: {e}")
        return False


async def test_analytics(db: DatabaseManager) -> bool:
    """Test analytics operations."""
    print_test("Analytics Operations")

    try:
        # First create a video to test analytics on
        video_data = VideoCreate(
            chapter_id="test-chapter-analytics-001",
            chapter_title="Analytics Test Chapter",
            chapter_number=1,
            content_snippet="Testing analytics...",
            video_url="https://test-bucket.r2.dev/videos/analytics.mp4",
            duration_seconds=30.0,
        )
        created_video = await db.create_video(video_data)
        print_info(f"Created video for analytics: ID {created_video.id}")

        # Increment views
        print_info("Incrementing views...")
        result = await db.increment_views(created_video.id)
        if result:
            print_success("Views incremented")
        else:
            print_error("Failed to increment views")
            return False

        # Increment likes
        print_info("Incrementing likes...")
        result = await db.increment_likes(created_video.id)
        if result:
            print_success("Likes incremented")
        else:
            print_error("Failed to increment likes")
            return False

        # Get analytics
        print_info("Retrieving analytics...")
        analytics = await db.get_analytics(created_video.id)
        if analytics and analytics.views > 0:
            print_success(f"Analytics: {analytics.views} views, {analytics.likes} likes")
        else:
            print_error("Failed to retrieve analytics")
            return False

        # Get analytics summary
        print_info("Getting analytics summary...")
        summary = await db.get_analytics_summary(days=7)
        print_success(f"Summary: {summary['total_videos']} videos, {summary['total_views']} views")

        # Clean up
        await db.delete_video(created_video.id)
        print_info("Cleaned up analytics test video")

        return True

    except Exception as e:
        print_error(f"Analytics test failed: {e}")
        return False


async def test_videos_for_shorts_page(db: DatabaseManager) -> bool:
    """Test getting videos for the shorts page."""
    print_test("Videos for Shorts Page")

    try:
        # Create a few completed videos
        for i in range(3):
            video_data = VideoCreate(
                chapter_id=f"test-chapter-page-{i}",
                chapter_title=f"Test Chapter {i}",
                chapter_number=i + 1,
                content_snippet=f"Test content {i}...",
                video_url=f"https://test.r2.dev/video{i}.mp4",
                duration_seconds=30.0 + i * 10,
            )
            await db.create_video(video_data)

        print_info("Created 3 test videos")

        # Get videos for shorts page
        videos = await db.get_videos_for_shorts_page(limit=10)
        print_success(f"Retrieved {len(videos)} videos for shorts page")

        # Verify structure
        if videos:
            first_video = videos[0]
            required_fields = [
                "id",
                "chapter_id",
                "chapter_title",
                "video_url",
                "duration_seconds",
            ]
            for field in required_fields:
                if field not in first_video:
                    print_error(f"Missing field: {field}")
                    return False

            print_success("Videos have correct structure")

        # Clean up
        for i in range(3):
            video = await db.get_video_by_chapter_id(f"test-chapter-page-{i}")
            if video:
                await db.delete_video(video.id)

        print_info("Cleaned up test videos")

        return True

    except Exception as e:
        print_error(f"Videos for shorts page test failed: {e}")
        return False


async def run_all_tests() -> None:
    """Run all database tests."""
    print_header("Database Manager Test Suite")

    # Check database URL
    if not settings.shorts_database_url:
        print_error("DATABASE_URL environment variable not set")
        print_warning("Set DATABASE_URL to run these tests")
        print_info("Example: postgresql+asyncpg://user:pass@host/db")
        return

    print_info(f"Database URL: {settings.shorts_database_url[:30]}...")

    # Create database manager
    db = DatabaseManager(database_url=settings.shorts_database_url)

    # Create tables (if needed)
    print_info("Creating database tables...")
    try:
        await db.create_tables()
        print_success("Database tables ready")
    except Exception as e:
        print_warning(f"Table creation noted: {e}")

    # Run tests
    results = []

    results.append(await test_database_connection(db))
    results.append(await test_video_crud(db))
    results.append(await test_job_tracking(db))
    results.append(await test_script_management(db))
    results.append(await test_analytics(db))
    results.append(await test_videos_for_shorts_page(db))

    # Print summary
    print_header("Test Summary")

    passed = sum(results)
    total = len(results)

    print(f"Total Tests: {total}")
    print(f"{Colors.OKGREEN}Passed: {passed}{Colors.ENDC}")
    if passed < total:
        print(f"{Colors.FAIL}Failed: {total - passed}{Colors.ENDC}")

    # Close connection
    await db.close()
    print_info("Database connection closed")

    # Exit with appropriate code
    sys.exit(0 if passed == total else 1)


def main() -> None:
    """Entry point for the test script."""
    asyncio.run(run_all_tests())


if __name__ == "__main__":
    main()
