"""Job status and tracking endpoints."""

import logging
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from shorts_generator.core.config import settings
from shorts_generator.database.connection import _create_engine, get_session
from shorts_generator.models import GenerationJob, ShortVideo
from shorts_generator.services.storage import storage_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Status"])


class JobStatusResponse(BaseModel):
    """Response model for job status."""

    job_id: str
    lesson_path: str
    status: str
    progress: int
    error_message: str | None = None
    retry_count: int
    created_at: str
    completed_at: str | None = None
    video_id: str | None = None


class JobsListResponse(BaseModel):
    """Response model for jobs list."""

    total_count: int
    jobs: list[JobStatusResponse]
    page: int
    page_size: int


class VideoMetadataResponse(BaseModel):
    """Response model for video metadata."""

    video_id: str
    lesson_path: str
    title: str
    duration_seconds: int
    video_url: str
    thumbnail_url: str
    created_at: str
    generation_cost: float


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str
    service: str
    version: str
    dependencies: dict[str, str]


@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
    session: AsyncSession = Depends(get_session),
) -> JobStatusResponse:
    """Get the status of a generation job.

    Args:
        job_id: Job ID to check
        session: Database session

    Returns:
        JobStatusResponse with current job status

    Raises:
        HTTPException: If job_id not found
    """
    result = await session.execute(select(GenerationJob).where(GenerationJob.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job not found: {job_id}",
        )

    return JobStatusResponse(
        job_id=job.id,
        lesson_path=job.lesson_path,
        status=job.status,
        progress=job.progress,
        error_message=job.error_message,
        retry_count=job.retry_count,
        created_at=job.created_at.isoformat() if job.created_at else "",
        completed_at=job.completed_at.isoformat() if job.completed_at else None,
        video_id=str(job.video_id) if job.video_id else None,
    )


@router.get("/jobs", response_model=JobsListResponse)
async def list_jobs(
    status_filter: str | None = None,
    page: int = 1,
    page_size: int = 50,
    session: AsyncSession = Depends(get_session),
) -> JobsListResponse:
    """List all generation jobs with optional filtering.

    Args:
        status_filter: Filter by status (queued, processing, completed, failed)
        page: Page number (1-indexed)
        page_size: Number of jobs per page (max 100)
        session: Database session

    Returns:
        JobsListResponse with paginated job list
    """
    # Validate page_size
    if page_size > 100:
        page_size = 100
    if page_size < 1:
        page_size = 50

    # Build query
    query = select(GenerationJob)

    if status_filter:
        if status_filter not in ["queued", "processing", "completed", "failed"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status filter: {status_filter}",
            )
        query = query.where(GenerationJob.status == status_filter)

    # Order by created_at descending
    query = query.order_by(GenerationJob.created_at.desc())

    # Get total count
    from sqlalchemy import func

    count_query = select(func.count()).select_from(query.subquery())
    total_count_result = await session.execute(count_query)
    total_count = total_count_result.scalar() or 0

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    # Execute query
    result = await session.execute(query)
    jobs = result.scalars().all()

    return JobsListResponse(
        total_count=total_count,
        jobs=[
            JobStatusResponse(
                job_id=job.id,
                lesson_path=job.lesson_path,
                status=job.status,
                progress=job.progress,
                error_message=job.error_message,
                retry_count=job.retry_count,
                created_at=job.created_at.isoformat() if job.created_at else "",
                completed_at=job.completed_at.isoformat() if job.completed_at else None,
                video_id=str(job.video_id) if job.video_id else None,
            )
            for job in jobs
        ],
        page=page,
        page_size=page_size,
    )


@router.get("/videos/{video_id}", response_model=VideoMetadataResponse)
async def get_video_metadata(
    video_id: str,
    session: AsyncSession = Depends(get_session),
) -> VideoMetadataResponse:
    """Get metadata for a generated video.

    Args:
        video_id: Video ID to fetch
        session: Database session

    Returns:
        VideoMetadataResponse with video metadata

    Raises:
        HTTPException: If video_id not found
    """
    result = await session.execute(select(ShortVideo).where(ShortVideo.id == video_id))
    video = result.scalar_one_or_none()

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video not found: {video_id}",
        )

    return VideoMetadataResponse(
        video_id=str(video.id),
        lesson_path=video.lesson_path,
        title=video.title,
        duration_seconds=video.duration_seconds,
        video_url=video.video_url,
        thumbnail_url=video.thumbnail_url,
        created_at=video.created_at.isoformat() if video.created_at else "",
        generation_cost=float(video.generation_cost) if video.generation_cost else 0.0,
    )


@router.get("/videos", response_model=list[VideoMetadataResponse])
async def list_videos(
    limit: int = 50,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
) -> list[VideoMetadataResponse]:
    """List all generated videos.

    Args:
        limit: Maximum number of videos to return (max 100)
        offset: Number of videos to skip
        session: Database session

    Returns:
        List of VideoMetadataResponse
    """
    # Validate limit
    if limit > 100:
        limit = 100
    if limit < 1:
        limit = 50

    # Query videos
    query = (
        select(ShortVideo)
        .order_by(ShortVideo.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    result = await session.execute(query)
    videos = result.scalars().all()

    return [
        VideoMetadataResponse(
            video_id=str(video.id),
            lesson_path=video.lesson_path,
            title=video.title,
            duration_seconds=video.duration_seconds,
            video_url=video.video_url,
            thumbnail_url=video.thumbnail_url,
            created_at=video.created_at.isoformat() if video.created_at else "",
            generation_cost=float(video.generation_cost) if video.generation_cost else 0.0,
        )
        for video in videos
    ]


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint with detailed dependency checks.

    Returns:
        HealthResponse with service status and dependency health
    """
    health_status = "healthy"
    dependencies: dict[str, str] = {}

    # Check database connection
    try:
        engine = _create_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        dependencies["database"] = "connected"
        await engine.dispose()
    except Exception as e:
        health_status = "degraded"
        dependencies["database"] = f"error: {str(e)}"

    # Check scheduler
    try:
        from shorts_generator.services.automation_service import get_scheduler

        sched = get_scheduler()
        if sched.running:
            dependencies["automation_scheduler"] = "running"
        else:
            dependencies["automation_scheduler"] = "stopped"
    except Exception as e:
        dependencies["automation_scheduler"] = f"error: {str(e)}"

    # External APIs (assumed available unless pinged)
    dependencies.update({
        "gemini_api": "configured",
        "replicate_api": "configured",
        "edge_tts": "available",
        "pollinations_ai": "available (free)",
        "r2_storage": "configured",
    })

    return HealthResponse(
        status=health_status,
        service="lesson-shorts-generator",
        version="0.1.0",
        dependencies=dependencies,
    )


async def _run_generation_task(
    job_id: str,
    lesson_path: str,
    target_duration: int,
    voice: str,
):
    """Background task for video generation."""
    from shorts_generator.services.automation_service import generate_single_short
    await generate_single_short(
        job_id=job_id,
        lesson_path=lesson_path,
        target_duration=target_duration,
        voice=voice,
    )


@router.post("/jobs/{job_id}/retry", response_model=JobStatusResponse)
async def retry_job(
    job_id: str,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
) -> JobStatusResponse:
    """Retry a failed generation job.

    Args:
        job_id: Job ID to retry
        background_tasks: FastAPI BackgroundTasks
        session: Database session

    Returns:
        JobStatusResponse with updated job status

    Raises:
        HTTPException: If job_id not found or job cannot be retried
    """
    result = await session.execute(select(GenerationJob).where(GenerationJob.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job not found: {job_id}",
        )

    if job.status != "failed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot retry job with status: {job.status}",
        )

    # Update job for retry
    job.status = "queued"
    job.progress = 0
    job.error_message = None
    job.retry_count += 1

    await session.commit()

    # Trigger background task for retry
    background_tasks.add_task(
        _run_generation_task,
        job_id=str(job.id),
        lesson_path=job.lesson_path,
        target_duration=60,
        voice="en-US-AriaNeural",
    )

    logger.info(f"Retrying job: {job_id} (attempt {job.retry_count})")

    return JobStatusResponse(
        job_id=job.id,
        lesson_path=job.lesson_path,
        status=job.status,
        progress=job.progress,
        error_message=job.error_message,
        retry_count=job.retry_count,
        created_at=job.created_at.isoformat() if job.created_at else "",
        completed_at=job.completed_at.isoformat() if job.completed_at else None,
        video_id=str(job.video_id) if job.video_id else None,
    )


@router.get("/storage/stats")
async def get_storage_stats() -> dict:
    """Get R2 storage statistics.

    Returns:
        dict with file counts, total size, and estimated cost
    """
    stats = await storage_service.get_storage_stats()
    return stats


@router.delete("/storage/videos/{video_id}")
async def delete_video_files(video_id: str) -> dict:
    """Delete all files associated with a video from R2 storage.

    Args:
        video_id: Video ID to delete

    Returns:
        dict with deletion status

    Raises:
        HTTPException: If deletion fails
    """
    logger.info(f"Deleting R2 files for video: {video_id}")

    results = await storage_service.delete_video_files(video_id)

    deleted_count = sum(1 for v in results.values() if v)
    total_count = len(results)

    return {
        "video_id": video_id,
        "deleted_count": deleted_count,
        "total_count": total_count,
        "results": results,
    }
