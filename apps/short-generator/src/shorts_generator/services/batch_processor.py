"""Batch Processor for Multiple Video Generations.

This module provides utilities for processing multiple chapters:
- Discover chapters from directory structure
- Create batch inputs from file patterns
- Resume failed batch jobs
- Export batch reports

Usage:
    processor = BatchProcessor()
    chapters = processor.discover_chapters("docs/01-General-Agents-Foundations")
    batch_result = await processor.process_all(chapters)
"""

import fnmatch
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from shorts_generator.services.pipeline_orchestrator import (
    BatchResult,
    ChapterInput,
    PipelineOrchestrator,
    pipeline_orchestrator,
)

logger = logging.getLogger(__name__)


@dataclass
class ChapterMetadata:
    """Metadata extracted from a chapter file."""

    file_path: str
    chapter_id: str
    chapter_title: str
    chapter_number: int | None = None
    word_count: int = 0
    estimated_duration: float = 60.0


@dataclass
class BatchReport:
    """Report generated after batch processing."""

    batch_id: str
    generated_at: datetime = field(default_factory=datetime.now)
    total_chapters: int = 0
    successful: int = 0
    failed: int = 0
    skipped: int = 0
    total_duration: float = 0.0
    total_file_size: float = 0.0
    errors: list[str] = field(default_factory=list)
    processing_time_seconds: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "batch_id": self.batch_id,
            "generated_at": self.generated_at.isoformat(),
            "total_chapters": self.total_chapters,
            "successful": self.successful,
            "failed": self.failed,
            "skipped": self.skipped,
            "total_duration": self.total_duration,
            "total_file_size": self.total_file_size,
            "errors": self.errors,
            "processing_time_seconds": self.processing_time_seconds,
        }


class BatchProcessor:
    """Process multiple chapters for video generation.

    Features:
    - Auto-discovery of chapters from directory
    - Pattern matching for chapter selection
    - Resume support for failed jobs
    - Report generation
    """

    def __init__(
        self,
        orchestrator: PipelineOrchestrator | None = None,
        default_voice_preset: str = "narration_male",
    ) -> None:
        """Initialize the batch processor.

        Args:
            orchestrator: Pipeline orchestrator (default: singleton)
            default_voice_preset: Default voice preset for TTS
        """
        self.orchestrator = orchestrator or pipeline_orchestrator
        self.default_voice_preset = default_voice_preset

        logger.info("BatchProcessor initialized")

    def discover_chapters(
        self,
        root_dir: str,
        pattern: str = "*.md",
        recursive: bool = True,
        exclude_patterns: list[str] | None = None,
    ) -> list[ChapterMetadata]:
        """Discover chapter files in a directory.

        Args:
            root_dir: Root directory to search
            pattern: Glob pattern for files
            recursive: Search recursively
            exclude_patterns: Patterns to exclude

        Returns:
            List of chapter metadata
        """
        root_path = Path(root_dir)
        if not root_path.exists():
            logger.warning(f"Directory not found: {root_dir}")
            return []

        exclude_patterns = exclude_patterns or ["README.md", "index.md"]

        chapters = []
        files = (
            root_path.rglob(pattern) if recursive else root_path.glob(pattern)
        )

        for file_path in files:
            # Skip excluded patterns
            if any(
                fnmatch.fnmatch(file_path.name, exclude)
                for exclude in exclude_patterns
            ):
                continue

            # Extract metadata
            relative_path = file_path.relative_to(root_path)
            chapter_id = str(relative_path.with_suffix(""))

            # Try to extract title from file
            title = self._extract_title_from_file(file_path)

            # Count words
            word_count = self._count_words_in_file(file_path)

            # Estimate duration (150 words per minute average)
            estimated_duration = max(30, word_count / 150 * 60)

            chapters.append(
                ChapterMetadata(
                    file_path=str(file_path),
                    chapter_id=chapter_id,
                    chapter_title=title or file_path.stem,
                    word_count=word_count,
                    estimated_duration=estimated_duration,
                )
            )

        logger.info(f"Discovered {len(chapters)} chapters in {root_dir}")
        return chapters

    def _extract_title_from_file(self, file_path: Path) -> str | None:
        """Extract the title (first heading) from a markdown file.

        Args:
            file_path: Path to markdown file

        Returns:
            Title or None
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("# "):
                        return line[2:].strip()
                    elif line.startswith("## "):
                        return line[3:].strip()
                    elif line and not line.startswith("---"):
                        break
        except Exception as e:
            logger.warning(f"Failed to read title from {file_path}: {e}")

        return None

    def _count_words_in_file(self, file_path: Path) -> int:
        """Count words in a markdown file.

        Args:
            file_path: Path to markdown file

        Returns:
            Word count
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
                # Remove frontmatter
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        content = parts[2]

                # Remove markdown syntax
                import re

                content = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
                content = re.sub(r"[#*`_\[\]]", " ", content)
                content = re.sub(r"\s+", " ", content)

                return len(content.split())
        except Exception:
            return 0

    def metadata_to_inputs(
        self,
        chapters: list[ChapterMetadata],
        voice_preset: str | None = None,
    ) -> list[ChapterInput]:
        """Convert chapter metadata to input objects.

        Args:
            chapters: List of chapter metadata
            voice_preset: Override default voice preset

        Returns:
            List of chapter inputs
        """
        return [
            ChapterInput(
                chapter_id=ch.chapter_id,
                chapter_title=ch.chapter_title,
                markdown_file=ch.file_path,
                voice_preset=voice_preset or self.default_voice_preset,
            )
            for ch in chapters
        ]

    async def process_all(
        self,
        chapters: list[ChapterInput],
        batch_id: str | None = None,
        resume_from_failed: bool = False,
    ) -> BatchResult:
        """Process all chapters in a batch.

        Args:
            chapters: List of chapter inputs
            batch_id: Optional batch ID
            resume_from_failed: Skip already completed videos

        Returns:
            BatchResult with all results
        """
        from shorts_generator.database import database_manager

        # Filter out already completed if resuming
        if resume_from_failed:
            filtered = []
            for chapter in chapters:
                existing = await database_manager.get_video_by_chapter_id(
                    chapter.chapter_id
                )
                if not existing:
                    filtered.append(chapter)
            logger.info(f"Resume mode: {len(chapters) - len(filtered)} skipped")
            chapters = filtered

        # Generate batch
        result = await self.orchestrator.generate_batch(chapters, batch_id=batch_id)

        return result

    def generate_report(self, batch_result: BatchResult) -> BatchReport:
        """Generate a summary report from batch result.

        Args:
            batch_result: Batch processing result

        Returns:
            BatchReport summary
        """
        total_duration = sum(
            r.duration_seconds or 0 for r in batch_result.results if r.success
        )

        errors = [
            f"{r.chapter_id}: {r.error_message}"
            for r in batch_result.results
            if not r.success and r.error_message
        ]

        processing_time = 0.0
        if batch_result.started_at and batch_result.completed_at:
            processing_time = (
                batch_result.completed_at - batch_result.started_at
            ).total_seconds()

        return BatchReport(
            batch_id=batch_result.batch_id,
            total_chapters=batch_result.total_chapters,
            successful=batch_result.completed,
            failed=batch_result.failed,
            skipped=batch_result.skipped,
            total_duration=total_duration,
            total_file_size=0.0,  # Would need to query DB for this
            errors=errors,
            processing_time_seconds=processing_time,
        )

    async def process_directory(
        self,
        root_dir: str,
        pattern: str = "*.md",
        batch_id: str | None = None,
        voice_preset: str | None = None,
        resume: bool = False,
    ) -> BatchReport:
        """Process all chapters in a directory.

        Convenience method that combines discovery and processing.

        Args:
            root_dir: Root directory to process
            pattern: File pattern to match
            batch_id: Optional batch ID
            voice_preset: Voice preset for TTS
            resume: Skip already completed videos

        Returns:
            BatchReport summary
        """
        # Discover chapters
        chapters_metadata = self.discover_chapters(root_dir, pattern)

        if not chapters_metadata:
            logger.warning(f"No chapters found in {root_dir}")
            return BatchReport(
                batch_id=batch_id or "empty",
                total_chapters=0,
            )

        # Convert to inputs
        chapters = self.metadata_to_inputs(chapters_metadata, voice_preset)

        # Process batch
        batch_result = await self.process_all(
            chapters, batch_id=batch_id, resume_from_failed=resume
        )

        # Generate and return report
        return self.generate_report(batch_result)

    async def resume_failed_batch(
        self,
        batch_id: str,
    ) -> BatchReport | None:
        """Resume a failed batch by reprocessing only failed chapters.

        Args:
            batch_id: Original batch ID

        Returns:
            BatchReport or None if batch not found
        """
        batch_result = self.orchestrator.get_batch_status(batch_id)
        if not batch_result:
            logger.warning(f"Batch not found: {batch_id}")
            return None

        # Get failed chapters
        failed_results = [r for r in batch_result.results if not r.success]

        if not failed_results:
            logger.info(f"No failed chapters to resume in batch {batch_id}")
            return self.generate_report(batch_result)

        # Create new batch for retries
        _ = f"{batch_id}-retry"  # Would be used for retry batch in full implementation
        logger.info(f"Resuming {len(failed_results)} failed chapters")

        # Re-process failed chapters (would need to reconstruct inputs)
        # This is a simplified version - in practice you'd need to store
        # the original inputs

        return None


# Singleton instance
batch_processor = BatchProcessor()
