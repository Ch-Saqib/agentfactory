"""Tests for Shorts Generation API Routes.

This test module validates:
1. Video generation from markdown
2. Video generation from file
3. Job status tracking
4. Video listing and retrieval
5. Health check
6. Error handling
"""

from datetime import datetime
from unittest import mock

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from shorts_generator.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


class TestGenerateFromMarkdown:
    """Tests for POST /api/v1/shorts/generate/from-markdown."""

    def test_generate_from_markdown_success(self, client):
        """Test successful video generation request."""
        request_data = {
            "markdown_content": "# Test Chapter\n\nThis is test content for video generation.",
            "chapter_id": "test-chapter-001",
            "chapter_title": "Test Chapter 1",
            "chapter_number": 1,
            "voice_preset": "narration_male",
        }

        # Mock database manager
        with mock.patch(
            "shorts_generator.routes.shorts.database_manager"
        ) as mock_db:
            # Mock get_video_by_chapter_id (not found)
            mock_db.get_video_by_chapter_id.return_value = None
            # Mock create_job
            mock_db.create_job.return_value = mock.Mock(job_id="test-job-123")

            response = client.post("/api/v1/shorts/generate/from-markdown", json=request_data)

            assert response.status_code == status.HTTP_202_ACCEPTED
            data = response.json()
            assert "job_id" in data
            assert data["status"] == "queued"

    def test_generate_from_markdown_empty_chapter_id(self, client):
        """Test request with empty chapter_id."""
        request_data = {
            "markdown_content": "# Test\nContent",
            "chapter_id": "   ",  # Empty/whitespace
            "chapter_title": "Test",
        }

        response = client.post("/api/v1/shorts/generate/from-markdown", json=request_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_generate_from_markdown_short_content(self, client):
        """Test request with content shorter than min_length."""
        request_data = {
            "markdown_content": "Hi",  # Too short
            "chapter_id": "test-chapter",
            "chapter_title": "Test",
        }

        response = client.post("/api/v1/shorts/generate/from-markdown", json=request_data)

        # Validation error for min_length
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_generate_from_markdown_already_exists(self, client):
        """Test request when video already exists for chapter."""
        request_data = {
            "markdown_content": "# Test\n\nContent that exists",
            "chapter_id": "existing-chapter",
            "chapter_title": "Existing Chapter",
        }

        # Mock existing video
        mock_video = mock.Mock()
        mock_video.id = 123

        with mock.patch(
            "shorts_generator.routes.shorts.database_manager"
        ) as mock_db:
            mock_db.get_video_by_chapter_id.return_value = mock_video

            response = client.post("/api/v1/shorts/generate/from-markdown", json=request_data)

            assert response.status_code == status.HTTP_202_ACCEPTED
            data = response.json()
            assert data["status"] == "already_exists"
            assert "already_exists" in data["message"].lower()


class TestGenerateFromFile:
    """Tests for POST /api/v1/shorts/generate/from-file."""

    def test_generate_from_file_success(self, client):
        """Test successful file-based generation."""
        import tempfile
        from pathlib import Path

        # Create a temporary markdown file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as tmp:
            tmp.write("# Test Chapter\n\nTest content from file.")
            tmp.flush()

            request_data = {
                "markdown_file": tmp.name,
                "chapter_id": "test-chapter-file-001",
                "chapter_title": "Test Chapter from File",
                "chapter_number": 1,
            }

            with mock.patch(
                "shorts_generator.routes.shorts.database_manager"
            ) as mock_db:
                mock_db.get_video_by_chapter_id.return_value = None
                mock_db.create_job.return_value = mock.Mock(job_id="test-job-file")

                response = client.post("/api/v1/shorts/generate/from-file", json=request_data)

                # Clean up
                Path(tmp.name).unlink()

                assert response.status_code == status.HTTP_202_ACCEPTED
                data = response.json()
                assert "job_id" in data

    def test_generate_from_file_not_found(self, client):
        """Test request with non-existent file."""
        request_data = {
            "markdown_file": "/nonexistent/file.md",
            "chapter_id": "test-chapter",
            "chapter_title": "Test",
        }

        response = client.post("/api/v1/shorts/generate/from-file", json=request_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestJobStatus:
    """Tests for GET /api/v1/shorts/jobs/{job_id}."""

    def test_get_job_status_found(self, client):
        """Test getting job status when job exists."""
        job_id = "test-job-123"

        mock_job = mock.Mock()
        mock_job.job_id = job_id
        mock_job.status = "running"
        mock_job.progress = 50
        mock_job.error_message = None
        mock_job.created_at = datetime.now()
        mock_job.started_at = datetime.now()
        mock_job.completed_at = None
        mock_job.result_data = None

        with mock.patch(
            "shorts_generator.routes.shorts.database_manager"
        ) as mock_db:
            mock_db.get_job.return_value = mock_job

            response = client.get(f"/api/v1/shorts/jobs/{job_id}")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["job_id"] == job_id
            assert data["status"] == "running"
            assert data["progress"] == 50

    def test_get_job_status_not_found(self, client):
        """Test getting job status when job doesn't exist."""
        with mock.patch(
            "shorts_generator.routes.shorts.database_manager"
        ) as mock_db:
            mock_db.get_job.return_value = None

            response = client.get("/api/v1/shorts/jobs/nonexistent-job")

            assert response.status_code == status.HTTP_404_NOT_FOUND


class TestVideoList:
    """Tests for GET /api/v1/shorts/videos."""

    def test_list_videos_default(self, client):
        """Test listing videos with default parameters."""
        mock_videos = [
            mock.Mock(
                id=1,
                chapter_id="chapter-1",
                chapter_title="Chapter 1",
                chapter_number=1,
                content_snippet="Snippet 1",
                video_url="url1.mp4",
                thumbnail_url="thumb1.jpg",
                duration_seconds=60.0,
                file_size_mb=5.0,
                status="completed",
                word_count=150,
                scene_count=3,
                generation_method="google_tts",
                voice_used="en-US-Neural2-C",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                analytics=None,
            )
        ]

        with mock.patch(
            "shorts_generator.routes.shorts.database_manager"
        ) as mock_db:
            mock_db.list_videos.return_value = mock_videos

            response = client.get("/api/v1/shorts/videos")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "videos" in data
            assert data["total_count"] == 1

    def test_list_videos_with_status_filter(self, client):
        """Test listing videos with status filter."""
        with mock.patch(
            "shorts_generator.routes.shorts.database_manager"
        ) as mock_db:
            mock_db.list_videos.return_value = []

            response = client.get("/api/v1/shorts/videos?status_filter=completed")

            assert response.status_code == status.HTTP_200_OK
            mock_db.list_videos.assert_called_once_with(
                status="completed",
                limit=20,
                offset=0,
                include_analytics=True,
            )

    def test_list_videos_with_pagination(self, client):
        """Test listing videos with pagination."""
        with mock.patch(
            "shorts_generator.routes.shorts.database_manager"
        ) as mock_db:
            mock_db.list_videos.return_value = []

            response = client.get("/api/v1/shorts/videos?limit=10&offset=20")

            assert response.status_code == status.HTTP_200_OK
            mock_db.list_videos.assert_called_once_with(
                status=None,
                limit=10,
                offset=20,
                include_analytics=True,
            )

    def test_list_videos_invalid_limit(self, client):
        """Test listing videos with invalid limit (over max)."""
        response = client.get("/api/v1/shorts/videos?limit=200")

        # FastAPI validates query params, should clamp to max
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestGetVideoForPage:
    """Tests for GET /api/v1/shorts/videos/for-page."""

    def test_get_videos_for_page(self, client):
        """Test getting videos for shorts page."""
        mock_response = [
            {
                "id": 1,
                "chapter_id": "chapter-1",
                "chapter_title": "Chapter 1",
                "video_url": "url1.mp4",
                "duration_seconds": 60.0,
                "views": 100,
            }
        ]

        with mock.patch(
            "shorts_generator.routes.shorts.database_manager"
        ) as mock_db:
            mock_db.get_videos_for_shorts_page.return_value = mock_response

            response = client.get("/api/v1/shorts/videos/for-page")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 1


class TestGetVideoById:
    """Tests for GET /api/v1/shorts/videos/by-id/{video_id}."""

    def test_get_video_by_id_found(self, client):
        """Test getting video by ID when video exists."""
        mock_video = mock.Mock()
        mock_video.id = 1
        mock_video.chapter_id = "chapter-1"
        mock_video.chapter_title = "Chapter 1"
        mock_video.analytics = None

        with mock.patch(
            "shorts_generator.routes.shorts.database_manager"
        ) as mock_db:
            mock_db.get_video.return_value = mock_video

            response = client.get("/api/v1/shorts/videos/by-id/1")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["id"] == 1

    def test_get_video_by_id_not_found(self, client):
        """Test getting video by ID when video doesn't exist."""
        with mock.patch(
            "shorts_generator.routes.shorts.database_manager"
        ) as mock_db:
            mock_db.get_video.return_value = None

            response = client.get("/api/v1/shorts/videos/by-id/999")

            assert response.status_code == status.HTTP_404_NOT_FOUND


class TestGetVideoByChapter:
    """Tests for GET /api/v1/shorts/videos/by-chapter/{chapter_id}."""

    def test_get_video_by_chapter_found(self, client):
        """Test getting video by chapter when video exists."""
        mock_video = mock.Mock()
        mock_video.id = 1
        mock_video.chapter_id = "test-chapter"
        mock_video.analytics = None

        with mock.patch(
            "shorts_generator.routes.shorts.database_manager"
        ) as mock_db:
            mock_db.get_video_by_chapter_id.return_value = mock_video

            response = client.get("/api/v1/shorts/videos/by-chapter/test-chapter")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["chapter_id"] == "test-chapter"

    def test_get_video_by_chapter_not_found(self, client):
        """Test getting video by chapter when video doesn't exist."""
        with mock.patch(
            "shorts_generator.routes.shorts.database_manager"
        ) as mock_db:
            mock_db.get_video_by_chapter_id.return_value = None

            response = client.get("/api/v1/shorts/videos/by-chapter/nonexistent")

            assert response.status_code == status.HTTP_404_NOT_FOUND


class TestHealthCheck:
    """Tests for GET /api/v1/shorts/health."""

    def test_health_check_healthy(self, client):
        """Test health check when all components are healthy."""
        with mock.patch(
            "shorts_generator.routes.shorts.database_manager"
        ) as mock_db:
            mock_db.health_check.return_value = True

            # Mock subprocess for ffmpeg check
            with mock.patch("subprocess.run") as mock_run:
                mock_run.return_value = mock.Mock()

                response = client.get("/api/v1/shorts/health")

                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert "status" in data
                assert "components" in data

    def test_health_check_database_unhealthy(self, client):
        """Test health check when database is unhealthy."""
        with mock.patch(
            "shorts_generator.routes.shorts.database_manager"
        ) as mock_db:
            mock_db.health_check.return_value = False

            # Mock subprocess for ffmpeg check
            with mock.patch("subprocess.run") as mock_run:
                mock_run.return_value = mock.Mock()

                response = client.get("/api/v1/shorts/health")

                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert data["components"]["database"] == "unhealthy"


class TestDeleteVideo:
    """Tests for DELETE /api/v1/shorts/videos/{video_id}."""

    def test_delete_video_success(self, client):
        """Test successful video deletion."""
        mock_video = mock.Mock()
        mock_video.id = 1

        with mock.patch(
            "shorts_generator.routes.shorts.database_manager"
        ) as mock_db:
            mock_db.get_video.return_value = mock_video
            mock_db.delete_video.return_value = True

            response = client.delete("/api/v1/shorts/videos/1")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["video_id"] == 1
            assert data["deleted"] is True

    def test_delete_video_not_found(self, client):
        """Test deleting non-existent video."""
        with mock.patch(
            "shorts_generator.routes.shorts.database_manager"
        ) as mock_db:
            mock_db.get_video.return_value = None

            response = client.delete("/api/v1/shorts/videos/999")

            assert response.status_code == status.HTTP_404_NOT_FOUND
