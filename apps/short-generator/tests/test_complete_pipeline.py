"""Tests for Complete Video Generation Pipeline.

This test module validates:
1. End-to-end single video generation
2. Batch video generation
3. Pipeline orchestration
4. Progress tracking
5. Error handling and retry logic
6. Batch processing
"""

import tempfile
from pathlib import Path
from unittest import mock

import pytest

from shorts_generator.services.batch_processor import (
    BatchProcessor,
    ChapterMetadata,
)
from shorts_generator.services.pipeline_orchestrator import (
    BatchResult,
    ChapterInput,
    ChapterResult,
    PipelineConfig,
    PipelineOrchestrator,
    PipelineStatus,
)
from shorts_generator.services.progress_service import (
    ProgressService,
    ProgressStep,
)


class TestPipelineOrchestrator:
    """Tests for PipelineOrchestrator."""

    @pytest.fixture
    def orchestrator(self):
        """Create an orchestrator for testing."""
        config = PipelineConfig(
            max_concurrent_jobs=2,
            max_retries=1,
            retry_delay_seconds=0,  # Instant retry for tests
            timeout_seconds=60,
        )
        return PipelineOrchestrator(config=config)

    @pytest.fixture
    def sample_chapter(self):
        """Create a sample chapter input."""
        return ChapterInput(
            chapter_id="test-chapter-001",
            chapter_title="Test Chapter",
            markdown_content="# Test\n\nThis is test content.",
        )

    @pytest.mark.asyncio
    async def test_generate_single_success(self, orchestrator, sample_chapter):
        """Test successful single video generation."""
        # Mock video service
        mock_result = mock.Mock()
        mock_result.success = True
        mock_result.video_id = 123
        mock_result.video_url = "https://r2.dev/video.mp4"
        mock_result.duration_seconds = 60.0
        mock_result.error_message = None

        with mock.patch.object(
            orchestrator.video_service, "generate_from_markdown", return_value=mock_result
        ):
            with mock.patch(
                "shorts_generator.services.pipeline_orchestrator.database_manager"
            ) as mock_db:
                mock_db.create_job.return_value = mock.Mock()
                mock_db.update_job_status.return_value = None

                result = await orchestrator.generate_single(sample_chapter)

                assert result.success is True
                assert result.chapter_id == "test-chapter-001"
                assert result.video_id == 123

    @pytest.mark.asyncio
    async def test_generate_single_with_retry(self, orchestrator, sample_chapter):
        """Test single generation with retry on failure."""
        # Mock first call fails, second succeeds
        mock_fail = mock.Mock()
        mock_fail.success = False
        mock_fail.error_message = "Temporary error"

        mock_success = mock.Mock()
        mock_success.success = True
        mock_success.video_id = 123
        mock_success.video_url = "https://r2.dev/video.mp4"
        mock_success.duration_seconds = 60.0

        with mock.patch.object(
            orchestrator.video_service,
            "generate_from_markdown",
            side_effect=[mock_fail, mock_success],
        ):
            with mock.patch(
                "shorts_generator.services.pipeline_orchestrator.database_manager"
            ) as mock_db:
                mock_db.create_job.return_value = mock.Mock()
                mock_db.update_job_status.return_value = None

                result = await orchestrator.generate_single(sample_chapter)

                assert result.success is True
                assert result.retry_count == 1

    @pytest.mark.asyncio
    async def test_generate_batch(self, orchestrator):
        """Test batch video generation."""
        chapters = [
            ChapterInput(
                chapter_id=f"chapter-{i}",
                chapter_title=f"Chapter {i}",
                markdown_content=f"# Chapter {i}\n\nContent.",
            )
            for i in range(3)
        ]

        # Mock successful generation
        mock_result = mock.Mock()
        mock_result.success = True
        mock_result.video_id = 100
        mock_result.video_url = "https://r2.dev/video.mp4"
        mock_result.duration_seconds = 60.0

        with mock.patch.object(
            orchestrator.video_service, "generate_from_markdown", return_value=mock_result
        ):
            with mock.patch(
                "shorts_generator.services.pipeline_orchestrator.database_manager"
            ) as mock_db:
                mock_db.create_job.return_value = mock.Mock()
                mock_db.update_job_status.return_value = mock.Mock()
                mock_db.get_video_by_chapter_id.return_value = None

                result = await orchestrator.generate_batch(chapters)

                assert result.status == PipelineStatus.COMPLETED
                assert result.completed == 3
                assert result.failed == 0

    @pytest.mark.asyncio
    async def test_batch_cancel(self, orchestrator):
        """Test cancelling a batch job."""
        batch_id = "test-batch-cancel"

        # Create a mock batch
        mock_batch = BatchResult(
            batch_id=batch_id,
            status=PipelineStatus.RUNNING,
            total_chapters=5,
        )

        orchestrator._active_batches[batch_id] = mock_batch
        orchestrator._cancel_flags[batch_id] = mock.Mock()

        with mock.patch(
            "shorts_generator.services.pipeline_orchestrator.database_manager"
        ) as mock_db:
            mock_db.update_job_status.return_value = None

            cancelled = await orchestrator.cancel_batch(batch_id)

            assert cancelled is True
            assert mock_batch.status == PipelineStatus.CANCELLED

    def test_get_batch_status(self, orchestrator):
        """Test getting batch status."""
        batch_id = "test-batch-status"

        mock_batch = BatchResult(
            batch_id=batch_id,
            status=PipelineStatus.RUNNING,
            total_chapters=10,
            completed=5,
        )

        orchestrator._active_batches[batch_id] = mock_batch

        result = orchestrator.get_batch_status(batch_id)

        assert result is not None
        assert result.batch_id == batch_id
        assert result.completed == 5


class TestBatchProcessor:
    """Tests for BatchProcessor."""

    @pytest.fixture
    def processor(self):
        """Create a batch processor for testing."""
        return BatchProcessor()

    @pytest.fixture
    def temp_chapters_dir(self, tmp_path):
        """Create a temporary directory with test chapter files."""
        # Create test markdown files
        (tmp_path / "chapter1.md").write_text("# Chapter 1\n\nContent for chapter 1.")
        (tmp_path / "chapter2.md").write_text("## Chapter 2\n\nContent for chapter 2.")
        (tmp_path / "README.md").write_text("# README\n\nThis should be excluded.")
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "chapter3.md").write_text(
            "### Chapter 3\n\nContent for chapter 3."
        )

        return tmp_path

    def test_discover_chapters(self, processor, temp_chapters_dir):
        """Test discovering chapters in directory."""
        chapters = processor.discover_chapters(
            str(temp_chapters_dir), pattern="*.md", recursive=True
        )

        # Should find 3 chapters (README excluded)
        assert len(chapters) == 3

        # Check chapter IDs
        chapter_ids = [ch.chapter_id for ch in chapters]
        assert "chapter1.md" in chapter_ids
        assert "chapter2.md" in chapter_ids
        assert any("subdir" in id for id in chapter_ids)

    def test_discover_chapters_exclude_patterns(self, processor, temp_chapters_dir):
        """Test discovering chapters with exclusions."""
        chapters = processor.discover_chapters(
            str(temp_chapters_dir),
            pattern="*.md",
            exclude_patterns=["README.md", "chapter1.md"],
        )

        # Should exclude README and chapter1
        assert len(chapters) == 2

    def test_extract_title_from_file(self, processor):
        """Test extracting title from markdown file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as tmp:
            tmp.write("# Test Title\n\nSome content here.")
            tmp.flush()

            title = processor._extract_title_from_file(Path(tmp.name))

            Path(tmp.name).unlink()

            assert title == "Test Title"

    def test_count_words_in_file(self, processor):
        """Test counting words in markdown file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as tmp:
            tmp.write("# Title\n\nThis is a test with some words.")
            tmp.flush()

            count = processor._count_words_in_file(Path(tmp.name))

            Path(tmp.name).unlink()

            assert count > 0

    def test_metadata_to_inputs(self, processor):
        """Test converting metadata to inputs."""
        metadata = [
            ChapterMetadata(
                file_path="/path/to/chapter1.md",
                chapter_id="chapter1",
                chapter_title="Chapter 1",
                word_count=100,
            )
        ]

        inputs = processor.metadata_to_inputs(metadata, voice_preset="narration_male")

        assert len(inputs) == 1
        assert inputs[0].chapter_id == "chapter1"
        assert inputs[0].voice_preset == "narration_male"

    def test_generate_report(self, processor):
        """Test generating batch report."""
        from shorts_generator.services.pipeline_orchestrator import BatchResult, PipelineStatus

        mock_batch = BatchResult(
            batch_id="test-batch",
            status=PipelineStatus.COMPLETED,
            total_chapters=5,
            completed=4,
            failed=1,
            results=[
                ChapterResult(
                    chapter_id="ch-1",
                    success=True,
                    video_id=1,
                    video_url="url1",
                    duration_seconds=60.0,
                ),
                ChapterResult(
                    chapter_id="ch-2",
                    success=False,
                    error_message="Failed",
                ),
            ],
        )

        report = processor.generate_report(mock_batch)

        assert report.batch_id == "test-batch"
        assert report.total_chapters == 5
        assert report.successful == 4
        assert report.failed == 1
        assert len(report.errors) == 1


class TestProgressService:
    """Tests for ProgressService."""

    @pytest.fixture
    def progress_service(self):
        """Create a progress service for testing."""
        return ProgressService(enable_websockets=False, persist_to_db=False)

    @pytest.mark.asyncio
    async def test_update_and_get_progress(self, progress_service):
        """Test updating and retrieving progress."""
        job_id = "test-job-123"

        update = await progress_service.update_progress(
            job_id=job_id,
            step="generating_audio",
            progress_percent=50,
            message="Generating audio...",
        )

        assert update.job_id == job_id
        assert update.progress_percent == 50

        retrieved = await progress_service.get_progress(job_id)

        assert retrieved is not None
        assert retrieved.progress_percent == 50

    @pytest.mark.asyncio
    async def test_progress_history(self, progress_service):
        """Test progress history tracking."""
        job_id = "test-job-history"

        # Add multiple updates
        for i in range(5):
            await progress_service.update_progress(
                job_id=job_id,
                step="step",
                progress_percent=i * 20,
                message=f"Progress {i}",
            )

        history = await progress_service.get_progress_history(job_id)

        assert len(history) == 5

    @pytest.mark.asyncio
    async def test_batch_progress(self, progress_service):
        """Test batch progress tracking."""
        batch_id = "test-batch"

        batch = await progress_service.initialize_batch(batch_id, total_jobs=10)

        assert batch.batch_id == batch_id
        assert batch.total_jobs == 10

        # Update some job progress
        await progress_service.update_batch_progress(
            batch_id=batch_id,
            job_id="job-1",
            job_progress=100,
            job_status="completed",
        )

        updated_batch = await progress_service.get_batch_progress(batch_id)

        assert updated_batch is not None
        assert updated_batch.completed == 1

    @pytest.mark.asyncio
    async def test_complete_job(self, progress_service):
        """Test marking a job as complete."""
        job_id = "test-job-complete"

        await progress_service.update_progress(
            job_id=job_id,
            step="running",
            progress_percent=50,
            message="Running...",
        )

        await progress_service.complete_job(job_id, success=True)

        progress = await progress_service.get_progress(job_id)

        assert progress is not None
        assert progress.step == ProgressStep.COMPLETED.value
        assert progress.progress_percent == 100

    @pytest.mark.asyncio
    async def test_cleanup(self, progress_service):
        """Test cleanup of progress data."""
        job_id = "test-job-cleanup"

        await progress_service.update_progress(
            job_id=job_id,
            step="running",
            progress_percent=50,
            message="Running...",
        )

        assert await progress_service.get_progress(job_id) is not None

        await progress_service.cleanup(job_id)

        assert await progress_service.get_progress(job_id) is None


class TestIntegration:
    """Integration tests for the complete pipeline."""

    @pytest.mark.asyncio
    async def test_end_to_end_single_video(self):
        """Test complete single video generation flow."""
        # This is a simplified integration test
        # In a real scenario, this would require actual services

        orchestrator = PipelineOrchestrator()

        chapter = ChapterInput(
            chapter_id="integration-test-001",
            chapter_title="Integration Test",
            markdown_content="# Test\n\nIntegration test content.",
        )

        # Mock all dependencies
        mock_result = mock.Mock()
        mock_result.success = True
        mock_result.video_id = 999
        mock_result.video_url = "https://r2.dev/test.mp4"
        mock_result.duration_seconds = 45.0

        with mock.patch.object(
            orchestrator.video_service, "generate_from_markdown", return_value=mock_result
        ):
            with mock.patch(
                "shorts_generator.services.pipeline_orchestrator.database_manager"
            ) as mock_db:
                mock_db.create_job.return_value = mock.Mock()
                mock_db.update_job_status.return_value = None

                result = await orchestrator.generate_single(chapter)

                assert result.success is True
                assert result.video_id == 999
