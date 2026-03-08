"""Job status and tracking endpoints."""

import json
import logging
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from shorts_generator.core.config import settings
from shorts_generator.database.connection import _create_engine, get_session
from shorts_generator.database.models import GenerationJob, ShortVideo
from shorts_generator.services.storage import storage_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Status"])


def _parse_result_data(result_data: Any) -> dict[str, Any] | None:
    """Parse result_data from JSON string to dict if needed."""
    if not result_data:
        return None
    try:
        if isinstance(result_data, str):
            return json.loads(result_data)
        return result_data
    except (json.JSONDecodeError, TypeError):
        logger.warning(f"Could not parse result_data: {result_data}")
        return None


class JobStatusResponse(BaseModel):
    """Response model for job status."""

    id: int
    job_id: str
    type: str
    status: str
    chapter_id: str | None = None
    progress: int
    error_message: str | None = None
    created_at: str
    started_at: str | None = None
    completed_at: str | None = None
    result_data: dict[str, Any] | None = None


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
        job_id: Job ID to check (this is the job_id string, not the database id)
        session: Database session

    Returns:
        JobStatusResponse with current job status

    Raises:
        HTTPException: If job_id not found
    """
    logger.info(f"🔍 [STATUS] Fetching job status for job_id={job_id}")

    try:
        # Query by job_id field, not id field
        logger.debug(f"🔍 [STATUS] Executing database query...")
        result = await session.execute(
            select(GenerationJob).where(GenerationJob.job_id == job_id)
        )
        job = result.scalar_one_or_none()
        logger.debug(f"🔍 [STATUS] Query completed, job found: {job is not None}")

        if not job:
            logger.warning(f"❌ [STATUS] Job not found: {job_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job not found: {job_id}",
            )

        response = JobStatusResponse(
            id=job.id,
            job_id=job.job_id,
            type=job.type,
            status=job.status,
            chapter_id=job.chapter_id,
            progress=job.progress,
            error_message=job.error_message,
            created_at=job.created_at.isoformat() if job.created_at else "",
            started_at=job.started_at.isoformat() if job.started_at else None,
            completed_at=job.completed_at.isoformat() if job.completed_at else None,
            result_data=_parse_result_data(job.result_data),
        )

        logger.info(f"✅ [STATUS] Job {job_id} - status={job.status}, progress={job.progress}%")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [STATUS] Error fetching job {job_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching job status: {str(e)}",
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
        if status_filter not in ["queued", "processing", "completed", "failed", "pending", "running"]:
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
                id=job.id,
                job_id=job.job_id,
                type=job.type,
                status=job.status,
                chapter_id=job.chapter_id,
                progress=job.progress,
                error_message=job.error_message,
                created_at=job.created_at.isoformat() if job.created_at else "",
                started_at=job.started_at.isoformat() if job.started_at else None,
                completed_at=job.completed_at.isoformat() if job.completed_at else None,
                result_data=_parse_result_data(job.result_data),
            )
            for job in jobs
        ],
        page=page,
        page_size=page_size,
    )


@router.get("/videos/{video_id}", response_model=VideoMetadataResponse)
async def get_video_metadata(
    video_id: int,
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
        lesson_path=video.chapter_id,
        title=video.chapter_title,
        duration_seconds=int(video.duration_seconds),
        video_url=video.video_url,
        thumbnail_url=video.thumbnail_url or "",
        created_at=video.created_at.isoformat() if video.created_at else "",
        generation_cost=0.0,  # Not tracked in Video model
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
            lesson_path=video.chapter_id,
            title=video.chapter_title,
            duration_seconds=int(video.duration_seconds),
            video_url=video.video_url,
            thumbnail_url=video.thumbnail_url or "",
            created_at=video.created_at.isoformat() if video.created_at else "",
            generation_cost=0.0,  # Not tracked in Video model
        )
        for video in videos
    ]


@router.get("/videos/{video_id}/thumbnail")
async def stream_thumbnail(
    video_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Stream a thumbnail image from R2 storage.

    This endpoint proxies thumbnail images from R2 storage to the client,
    bypassing CORS and presigned URL expiry issues.

    Args:
        video_id: Video ID

    Returns:
        Response with thumbnail image content

    Raises:
        HTTPException: If video not found or thumbnail cannot be streamed
    """
    import asyncio
    from fastapi.responses import Response
    from botocore.exceptions import ClientError as BotoClientError
    from shorts_generator.services.r2_uploader import get_r2_uploader

    # Get video from database
    result = await session.execute(select(ShortVideo).where(ShortVideo.id == video_id))
    video = result.scalar_one_or_none()

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video not found: {video_id}",
        )

    # Extract the R2 storage key from the thumbnail_url
    thumbnail_key = None
    if video.thumbnail_url:
        url = video.thumbnail_url
        # Extract key from URL - look for "thumbnails/" prefix in URL
        for prefix in ["thumbnails/"]:
            idx = url.find(prefix)
            if idx != -1:
                # Extract from "thumbnails/" onwards, strip query params
                thumbnail_key = url[idx:].split("?")[0]
                break

    # If no thumbnail_url stored, try constructing a key from chapter_id
    if not thumbnail_key and video.chapter_id:
        thumbnail_key = f"thumbnails/{video.chapter_id}/thumbnail.jpg"

    if not thumbnail_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No thumbnail available for video: {video_id}",
        )

    try:
        r2_uploader = get_r2_uploader()

        def _fetch_thumbnail():
            return r2_uploader.client.get_object(
                Bucket=r2_uploader.bucket_name,
                Key=thumbnail_key,
            )

        response = await asyncio.to_thread(_fetch_thumbnail)
        content_type = response.get("ContentType", "image/jpeg")
        body = await asyncio.to_thread(response["Body"].read)

        return Response(
            content=body,
            media_type=content_type,
            headers={
                "Cache-Control": "public, max-age=86400",  # 1 day cache
                "Content-Disposition": f"inline; filename={video_id}-thumbnail.jpg",
            },
        )

    except BotoClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        if error_code == "NoSuchKey":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Thumbnail not found in storage for video: {video_id}",
            )
        logger.error(f"R2 error streaming thumbnail for video {video_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stream thumbnail from R2: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Error streaming thumbnail for video {video_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stream thumbnail: {str(e)}",
        )


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

    # Check Edge TTS connectivity
    try:
        from shorts_generator.services.edge_tts_audio import check_edge_tts_connectivity

        connectivity = await check_edge_tts_connectivity()
        if connectivity["reachable"]:
            dependencies["edge_tts"] = "connected"
        else:
            dependencies["edge_tts"] = f"unreachable: {connectivity.get('error', 'Unknown error')}"
            if health_status == "healthy":
                health_status = "degraded"
    except Exception as e:
        dependencies["edge_tts"] = f"error: {str(e)}"
        if health_status == "healthy":
            health_status = "degraded"

    # External APIs (assumed available unless pinged)
    dependencies.update({
        "gemini_api": "configured",
        "replicate_api": "configured",
        "pollinations_ai": "available (free)",
        "r2_storage": "configured",
        "tts_provider": settings.tts_provider,
    })

    return HealthResponse(
        status=health_status,
        service="lesson-shorts-generator",
        version="0.1.0",
        dependencies=dependencies,
    )


@router.get("/connectivity/tts")
async def check_tts_connectivity() -> dict:
    """Check TTS service connectivity.

    Returns:
        dict with connectivity status for TTS services
    """
    result = {
        "provider": settings.tts_provider,
        "services": {},
    }

    # Check Edge TTS connectivity
    try:
        from shorts_generator.services.edge_tts_audio import check_edge_tts_connectivity

        edge_status = await check_edge_tts_connectivity()
        result["services"]["edge_tts"] = edge_status
    except Exception as e:
        result["services"]["edge_tts"] = {
            "service": "Edge TTS",
            "reachable": False,
            "error": str(e),
        }

    return result


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
        job_id: Job ID to retry (this is the job_id string, not the database id)
        background_tasks: FastAPI BackgroundTasks
        session: Database session

    Returns:
        JobStatusResponse with updated job status

    Raises:
        HTTPException: If job_id not found or job cannot be retried
    """
    # Query by job_id field, not id field
    result = await session.execute(
        select(GenerationJob).where(GenerationJob.job_id == job_id)
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job not found: {job_id}",
        )

    if job.status not in ["failed", "completed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot retry job with status: {job.status}",
        )

    # Update job for retry
    job.status = "pending"
    job.progress = 0
    job.error_message = None
    job.result_data = None

    await session.commit()

    # Trigger background task for retry using the pipeline orchestrator
    async def retry_generation():
        """Retry generation in background."""
        from shorts_generator.services.pipeline_orchestrator import get_pipeline_orchestrator, ChapterInput

        try:
            orchestrator = get_pipeline_orchestrator()
            # Get chapter input from job's input_data
            input_data = job.input_data or {}
            chapter = ChapterInput(
                chapter_id=job.chapter_id or f"retry-{job.job_id}",
                chapter_title=input_data.get("chapter_title", "Retry Generation"),
                chapter_number=input_data.get("chapter_number"),
                voice_preset=input_data.get("voice_preset", "narration_male"),
            )
            # We would need to load markdown content here
            # For now, just mark as failed with message
            logger.warning(f"Retry for job {job_id} triggered - full retry logic needs implementation")
        except Exception as e:
            logger.error(f"Retry failed for job {job_id}: {e}")

    background_tasks.add_task(retry_generation)

    logger.info(f"Retrying job: {job_id}")

    return JobStatusResponse(
        id=job.id,
        job_id=job.job_id,
        type=job.type,
        status=job.status,
        chapter_id=job.chapter_id,
        progress=job.progress,
        error_message=job.error_message,
        created_at=job.created_at.isoformat() if job.created_at else "",
        started_at=job.started_at.isoformat() if job.started_at else None,
        completed_at=job.completed_at.isoformat() if job.completed_at else None,
        result_data=_parse_result_data(job.result_data),
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
