"""Progress Tracking Service for Video Generation Pipeline.

This module provides real-time progress tracking with:
- In-memory progress state
- WebSocket support for live updates (optional)
- Progress persistence to database
- Progress aggregation for batch jobs

Usage:
    service = ProgressService()
    await service.update_progress("job-123", "generate_audio", 50, "Generating audio...")
    progress = await service.get_progress("job-123")
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from shorts_generator.database import database_manager

logger = logging.getLogger(__name__)


class ProgressStep(Enum):
    """Standard progress steps in video generation."""

    QUEUED = "queued"
    PARSING = "parsing"
    GENERATING_AUDIO = "generating_audio"
    GENERATING_FRAMES = "generating_frames"
    COMPOSING_VIDEO = "composing_video"
    UPLOADING = "uploading"
    SAVING_DATABASE = "saving_database"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ProgressUpdate:
    """Progress update for a job or batch."""

    job_id: str
    step: str
    progress_percent: int
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    details: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "job_id": self.job_id,
            "step": self.step,
            "progress_percent": self.progress_percent,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
            "error": self.error,
        }


@dataclass
class BatchProgress:
    """Progress tracking for batch jobs."""

    batch_id: str
    total_jobs: int
    completed: int = 0
    failed: int = 0
    running: int = 0
    job_progress: dict[str, int] = field(default_factory=dict)
    started_at: datetime | None = None
    updated_at: datetime | None = None

    @property
    def overall_progress(self) -> int:
        """Calculate overall batch progress percentage."""
        if self.total_jobs == 0:
            return 0
        completed_jobs = self.completed + self.failed
        return int(completed_jobs / self.total_jobs * 100)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "batch_id": self.batch_id,
            "total_jobs": self.total_jobs,
            "completed": self.completed,
            "failed": self.failed,
            "running": self.running,
            "job_progress": self.job_progress,
            "overall_progress": self.overall_progress,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ProgressService:
    """Service for tracking and broadcasting progress updates.

    Features:
    - In-memory progress state
    - Optional WebSocket broadcasting
    - Database persistence for jobs
    - Batch progress aggregation
    - Progress history tracking
    """

    def __init__(
        self,
        enable_websockets: bool = False,
        persist_to_db: bool = True,
        history_limit: int = 100,
    ) -> None:
        """Initialize the progress service.

        Args:
            enable_websockets: Enable WebSocket broadcasting
            persist_to_db: Persist updates to database
            history_limit: Max number of historical updates to keep
        """
        self.enable_websockets = enable_websockets
        self.persist_to_db = persist_to_db
        self.history_limit = history_limit

        # In-memory storage
        self._job_progress: dict[str, ProgressUpdate] = {}
        self._batch_progress: dict[str, BatchProgress] = {}
        self._progress_history: dict[str, list[ProgressUpdate]] = {}

        # WebSocket connections (if enabled)
        self._connections: dict[str, set[asyncio.Queue]] = {}

        logger.info(
            f"ProgressService initialized "
            f"(websockets={enable_websockets}, persist={persist_to_db})"
        )

    async def update_progress(
        self,
        job_id: str,
        step: str,
        progress_percent: int,
        message: str,
        details: dict[str, Any] | None = None,
        error: str | None = None,
    ) -> ProgressUpdate:
        """Update progress for a job.

        Args:
            job_id: Job identifier
            step: Current step name
            progress_percent: Progress percentage (0-100)
            message: Human-readable message
            details: Optional additional details
            error: Optional error message

        Returns:
            ProgressUpdate that was created
        """
        update = ProgressUpdate(
            job_id=job_id,
            step=step,
            progress_percent=max(0, min(100, progress_percent)),
            message=message,
            details=details or {},
            error=error,
        )

        # Store in memory
        self._job_progress[job_id] = update

        # Add to history
        if job_id not in self._progress_history:
            self._progress_history[job_id] = []
        self._progress_history[job_id].append(update)

        # Trim history
        if len(self._progress_history[job_id]) > self.history_limit:
            self._progress_history[job_id] = self._progress_history[job_id][
                -self.history_limit :
            ]

        # Persist to database
        if self.persist_to_db:
            try:
                await database_manager.update_job_status(
                    job_id,
                    status=step if step != "completed" else "completed",
                    progress=progress_percent,
                    error_message=error,
                )
            except Exception as e:
                logger.warning(f"Failed to persist progress to DB: {e}")

        # Broadcast via WebSocket
        if self.enable_websockets:
            await self._broadcast_update(job_id, update)

        logger.debug(f"[{job_id}] Progress: {progress_percent}% - {message}")

        return update

    async def get_progress(self, job_id: str) -> ProgressUpdate | None:
        """Get current progress for a job.

        Args:
            job_id: Job identifier

        Returns:
            ProgressUpdate or None if not found
        """
        return self._job_progress.get(job_id)

    async def get_progress_history(
        self, job_id: str, limit: int = 50
    ) -> list[ProgressUpdate]:
        """Get progress history for a job.

        Args:
            job_id: Job identifier
            limit: Max number of updates to return

        Returns:
            List of ProgressUpdate
        """
        history = self._progress_history.get(job_id, [])
        return history[-limit:] if history else []

    async def update_batch_progress(
        self,
        batch_id: str,
        job_id: str,
        job_progress: int,
        job_status: str,
    ) -> BatchProgress:
        """Update progress for a batch job.

        Args:
            batch_id: Batch identifier
            job_id: Job identifier within batch
            job_progress: Progress percentage for the job
            job_status: Status of the job (running, completed, failed)

        Returns:
            Updated BatchProgress
        """
        if batch_id not in self._batch_progress:
            self._batch_progress[batch_id] = BatchProgress(
                batch_id=batch_id,
                total_jobs=0,
            )

        batch = self._batch_progress[batch_id]
        batch.job_progress[job_id] = job_progress
        batch.updated_at = datetime.now()

        # Update counters based on status
        # (Simplified - in practice would need to track state transitions)
        if job_status == "completed":
            batch.completed += 1
            batch.running -= 1
        elif job_status == "failed":
            batch.failed += 1
            batch.running -= 1
        elif job_status == "running":
            if job_id not in batch.job_progress or batch.job_progress[job_id] == 0:
                batch.running += 1

        # Broadcast batch update
        if self.enable_websockets:
            await self._broadcast_batch_update(batch_id, batch)

        logger.debug(
            f"[{batch_id}] Batch progress: "
            f"{batch.completed}/{batch.total_jobs} completed"
        )

        return batch

    async def get_batch_progress(self, batch_id: str) -> BatchProgress | None:
        """Get progress for a batch job.

        Args:
            batch_id: Batch identifier

        Returns:
            BatchProgress or None if not found
        """
        return self._batch_progress.get(batch_id)

    async def initialize_batch(
        self, batch_id: str, total_jobs: int
    ) -> BatchProgress:
        """Initialize progress tracking for a new batch.

        Args:
            batch_id: Batch identifier
            total_jobs: Total number of jobs in batch

        Returns:
            New BatchProgress
        """
        batch = BatchProgress(
            batch_id=batch_id,
            total_jobs=total_jobs,
            started_at=datetime.now(),
            updated_at=datetime.now(),
        )

        self._batch_progress[batch_id] = batch

        logger.info(f"[{batch_id}] Initialized batch progress with {total_jobs} jobs")

        return batch

    async def complete_job(self, job_id: str, success: bool = True) -> None:
        """Mark a job as completed.

        Args:
            job_id: Job identifier
            success: Whether job completed successfully
        """
        progress = self._job_progress.get(job_id)
        if progress:
            progress.step = ProgressStep.COMPLETED.value if success else ProgressStep.FAILED.value
            progress.progress_percent = 100
            progress.timestamp = datetime.now()

        logger.info(f"[{job_id}] Job completed: {success}")

    async def cleanup(self, job_id: str | None = None) -> None:
        """Cleanup progress data.

        Args:
            job_id: Specific job to cleanup, or None to cleanup all old data
        """
        if job_id:
            self._job_progress.pop(job_id, None)
            self._progress_history.pop(job_id, None)
            logger.debug(f"Cleaned up progress for {job_id}")
        else:
            # Clean up old completed jobs (older than 1 hour)
            cutoff = datetime.now().timestamp() - 3600
            for jid, progress in list(self._job_progress.items()):
                if progress.timestamp.timestamp() < cutoff:
                    self._job_progress.pop(jid, None)
                    self._progress_history.pop(jid, None)

            logger.debug("Cleaned up old progress data")

    async def _broadcast_update(
        self, job_id: str, update: ProgressUpdate
    ) -> None:
        """Broadcast update via WebSocket.

        Args:
            job_id: Job identifier
            update: Progress update to broadcast
        """
        if job_id in self._connections:
            message = json.dumps({"type": "progress", "data": update.to_dict()})

            for queue in list(self._connections[job_id]):
                try:
                    await queue.put(message)
                except Exception:
                    self._connections[job_id].discard(queue)

    async def _broadcast_batch_update(
        self, batch_id: str, batch: BatchProgress
    ) -> None:
        """Broadcast batch update via WebSocket.

        Args:
            batch_id: Batch identifier
            batch: Batch progress to broadcast
        """
        if batch_id in self._connections:
            message = json.dumps(
                {"type": "batch_progress", "data": batch.to_dict()}
            )

            for queue in list(self._connections[batch_id]):
                try:
                    await queue.put(message)
                except Exception:
                    self._connections[batch_id].discard(queue)

    def register_connection(
        self, connection_id: str, queue: asyncio.Queue
    ) -> None:
        """Register a WebSocket connection for updates.

        Args:
            connection_id: Connection identifier (job_id or batch_id)
            queue: Queue for sending messages
        """
        if connection_id not in self._connections:
            self._connections[connection_id] = set()

        self._connections[connection_id].add(queue)
        logger.debug(f"Registered connection for {connection_id}")

    def unregister_connection(
        self, connection_id: str, queue: asyncio.Queue
    ) -> None:
        """Unregister a WebSocket connection.

        Args:
            connection_id: Connection identifier
            queue: Queue to remove
        """
        if connection_id in self._connections:
            self._connections[connection_id].discard(queue)

            if not self._connections[connection_id]:
                del self._connections[connection_id]

            logger.debug(f"Unregistered connection for {connection_id}")


# Singleton instance
progress_service = ProgressService()
