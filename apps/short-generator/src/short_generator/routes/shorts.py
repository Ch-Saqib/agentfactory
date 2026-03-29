"""Shorts Generation API Routes.

This module provides REST API endpoints for generating short videos
from markdown content using the complete pipeline (TTS, frames, composition, R2).

Endpoints:
- POST /api/v1/shorts/generate - Generate a short video
- GET /api/v1/shorts/jobs/{job_id} - Get job status
- GET /api/v1/shorts/videos - List videos
- GET /api/v1/shorts/videos/{video_id} - Get video details
- GET /api/v1/shorts/videos/by-chapter/{chapter_id} - Get video by chapter ID
"""

import logging
import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Request, status
from pydantic import BaseModel, Field

from short_generator.database import (
    VideoResponse,
    database_manager,
)
from short_generator.services.video_generation_service import (
    GenerationProgress,
    GenerationResult,
    video_generation_service,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/shorts", tags=["Shorts Generation"])

# In-memory unique view guard keyed by (video_id, viewer_key).
# This prevents repeat view increments from the same user in the running process.
_view_registry: dict[tuple[int, str], datetime] = {}


# Request/Response Models


class GenerateFromMarkdownRequest(BaseModel):
    """Request to generate a short video from markdown content."""

    markdown_content: str = Field(
        ..., description="Markdown content from Docusaurus lesson", min_length=10
    )
    chapter_id: str = Field(
        ...,
        description=(
            "Unique chapter identifier "
            "(e.g., '01-general-agents-foundations/01-agent-factory-paradigm')"
        ),
    )
    chapter_title: str = Field(..., description="Title of the chapter", min_length=1)
    chapter_number: int | None = Field(
        None, description="Chapter number in sequence (optional)"
    )
    voice_preset: str | None = Field(
        None,
        description='TTS voice preset (e.g., "narration_male", "narration_female")',
    )


class GenerateFromFileRequest(BaseModel):
    """Request to generate a short video from a markdown file."""

    markdown_file: str = Field(..., description="Path to markdown file")
    chapter_id: str = Field(
        ..., description="Unique chapter identifier (e.g., 'chapter-1')"
    )
    chapter_title: str = Field(..., description="Title of the chapter", min_length=1)
    chapter_number: int | None = Field(None, description="Chapter number in sequence")
    voice_preset: str | None = Field(None, description="TTS voice preset")


class GenerateResponse(BaseModel):
    """Response from video generation request."""

    job_id: str = Field(..., description="Unique job identifier for tracking")
    status: str = Field(..., description="Initial job status")
    message: str = Field(..., description="Human-readable message")


class JobStatusResponse(BaseModel):
    """Response for job status query."""

    job_id: str
    status: str
    progress: int
    error_message: str | None = None
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    result: dict[str, Any] | None = None


class VideoListResponse(BaseModel):
    """Response for video list."""

    total_count: int
    videos: list[VideoResponse]
    page: int | None = None
    limit: int | None = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    service: str
    components: dict[str, str]


class AddCommentRequest(BaseModel):
    """Request payload for adding a comment."""

    text: str = Field(..., min_length=1, max_length=2000)
    parent_id: int | None = Field(None)
    user_id: str | None = Field(None, max_length=100)


class RecordViewRequest(BaseModel):
    """Request payload for recording a view event."""

    watch_duration_seconds: int = Field(..., ge=0)
    completed: bool = Field(False)
    viewer_id: str | None = Field(None, max_length=200)


class CommentResponse(BaseModel):
    """Comment response model."""

    id: str
    userId: str
    videoId: str
    text: str
    parentId: str | None = None
    createdAt: str


# Background Tasks


async def _run_generation_task(
    job_id: str,
    request: GenerateFromMarkdownRequest | GenerateFromFileRequest,
):
    """Background task for video generation.

    Args:
        job_id: Unique job identifier
        request: Generation request
    """

    logger.info(f"Starting background generation task: {job_id}")

    # Update job status to running
    await database_manager.update_job_status(job_id, status="running", progress=0)

    # Progress callback to update job status
    async def progress_callback(progress: GenerationProgress):
        await database_manager.update_job_status(
            job_id,
            progress=progress.progress_percent,
        )
        logger.info(f"Job {job_id}: {progress.step} - {progress.message}")

    try:
        # Generate video
        result: GenerationResult

        if isinstance(request, GenerateFromFileRequest):
            result = await video_generation_service.generate_from_file(
                markdown_file=request.markdown_file,
                chapter_id=request.chapter_id,
                chapter_title=request.chapter_title,
                chapter_number=request.chapter_number,
                voice_preset=request.voice_preset,
                progress_callback=progress_callback,
            )
        else:
            result = await video_generation_service.generate_from_markdown(
                markdown_content=request.markdown_content,
                chapter_id=request.chapter_id,
                chapter_title=request.chapter_title,
                chapter_number=request.chapter_number,
                voice_preset=request.voice_preset,
                progress_callback=progress_callback,
            )

        if result.success:
            # Mark job as completed
            await database_manager.update_job_status(
                job_id,
                status="completed",
                progress=100,
                result_data={
                    "video_id": result.video_id,
                    "video_url": result.video_url,
                    "thumbnail_url": result.thumbnail_url,
                    "duration_seconds": result.duration_seconds,
                    "file_size_mb": result.file_size_mb,
                    **result.metadata,
                },
            )
            logger.info(f"Generation completed successfully: {job_id}")
        else:
            # Mark job as failed
            await database_manager.update_job_status(
                job_id,
                status="failed",
                error_message=result.error_message,
            )
            logger.error(f"Generation failed: {job_id} - {result.error_message}")

    except Exception as e:
        logger.error(f"Generation task error: {job_id} - {e}", exc_info=True)
        await database_manager.update_job_status(
            job_id,
            status="failed",
            error_message=str(e),
        )


# Endpoints

@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str) -> JobStatusResponse:
    """Get the status of a generation job.

    Args:
        job_id: Job identifier

    Returns:
        JobStatusResponse with current job status

    Raises:
        HTTPException: If job_id not found
    """
    job = await database_manager.get_job(job_id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job not found: {job_id}",
        )

    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        progress=job.progress,
        error_message=job.error_message,
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        result=job.result_data,
    )


@router.get("/videos", response_model=VideoListResponse)
async def list_videos(
    status_filter: str | None = Query(None, description="Filter by status"),
    limit: int = Query(20, ge=1, le=100, description="Max videos to return"),
    offset: int = Query(0, ge=0, description="Number of videos to skip"),
) -> VideoListResponse:
    """List generated videos.

    Args:
        status_filter: Optional status filter (pending, processing, completed, failed)
        limit: Maximum number of videos to return (1-100)
        offset: Number of videos to skip

    Returns:
        VideoListResponse with list of videos
    """
    videos = await database_manager.list_videos(
        status=status_filter,
        limit=limit,
        offset=offset,
        include_analytics=True,
    )

    # Convert to response format without triggering lazy-loading on detached ORM
    # relationships (notably `Video.comments`).
    video_responses = []
    for video in videos:
        video_dict: dict[str, Any] = {
            "id": video.id,
            "chapter_id": video.chapter_id,
            "chapter_title": video.chapter_title,
            "chapter_number": video.chapter_number,
            "content_snippet": video.content_snippet,
            "video_url": video.video_url,
            "thumbnail_url": video.thumbnail_url,
            "duration_seconds": video.duration_seconds,
            "file_size_mb": video.file_size_mb,
            "status": video.status,
            "word_count": video.word_count,
            "scene_count": video.scene_count,
            "generation_method": video.generation_method,
            "voice_used": video.voice_used,
            "created_at": video.created_at,
            "updated_at": video.updated_at,
        }
        # Add analytics if available (relationship is one-to-many in current model)
        analytics = None
        if video.analytics:
            if isinstance(video.analytics, list):
                analytics = video.analytics[0] if len(video.analytics) > 0 else None
            else:
                analytics = video.analytics

        video_dict["views"] = analytics.views if analytics else 0
        video_dict["likes"] = analytics.likes if analytics else 0
        video_dict["comments"] = analytics.comments if analytics else 0
        video_responses.append(VideoResponse(**video_dict))

    return VideoListResponse(
        total_count=len(video_responses),
        videos=video_responses,
        page=None,
        limit=limit,
    )


@router.post("/videos/{video_id}/like")
async def like_video(video_id: int) -> dict[str, Any]:
    """Increment like count for a video."""
    video = await database_manager.get_video(video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video not found: {video_id}",
        )

    updated = await database_manager.increment_likes(video_id)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update like count",
        )

    analytics = await database_manager.get_analytics(video_id)
    return {
        "video_id": str(video_id),
        "likes": analytics.likes if analytics else None,
    }


@router.post("/videos/{video_id}/unlike")
async def unlike_video(video_id: int) -> dict[str, Any]:
    """Decrement like count for a video."""
    video = await database_manager.get_video(video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video not found: {video_id}",
        )

    updated = await database_manager.decrement_likes(video_id)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update like count",
        )

    analytics = await database_manager.get_analytics(video_id)
    return {
        "video_id": str(video_id),
        "likes": analytics.likes if analytics else None,
    }


@router.get("/videos/{video_id}/comments")
async def get_video_comments(
    video_id: int,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    """Get comments for a video."""
    video = await database_manager.get_video(video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video not found: {video_id}",
        )

    comments = await database_manager.list_comments(
        video_id=video_id,
        limit=limit,
        offset=offset,
    )

    payload = [
        CommentResponse(
            id=str(comment.id),
            userId=comment.user_id,
            videoId=str(comment.video_id),
            text=comment.text,
            parentId=str(comment.parent_id) if comment.parent_id is not None else None,
            createdAt=comment.created_at.isoformat(),
        ).model_dump()
        for comment in comments
    ]

    return {
        "comments": payload,
        "totalCount": len(payload),
    }


@router.post("/videos/{video_id}/comments")
async def add_video_comment(
    video_id: int,
    request: AddCommentRequest,
) -> dict[str, Any]:
    """Add a comment to a video."""
    created = await database_manager.create_comment(
        video_id=video_id,
        text=request.text.strip(),
        user_id=request.user_id or "anonymous",
        parent_id=request.parent_id,
    )
    if not created:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video not found: {video_id}",
        )

    return {
        "commentId": str(created.id),
        "text": created.text,
        "createdAt": created.created_at.isoformat(),
    }


@router.post("/videos/{video_id}/views")
async def record_video_view(
    video_id: int,
    payload: RecordViewRequest,
    request: Request,
) -> dict[str, Any]:
    """Record a video view."""
    video = await database_manager.get_video(video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video not found: {video_id}",
        )

    client_ip = request.client.host if request.client and request.client.host else "unknown"
    viewer_key = (payload.viewer_id or "").strip() or f"ip:{client_ip}"
    registry_key = (video_id, viewer_key)
    unique_view_applied = False

    # Periodically trim old entries to prevent unbounded growth.
    if len(_view_registry) > 100_000:
        cutoff = datetime.now().timestamp() - (7 * 24 * 60 * 60)
        stale_keys = [k for k, ts in _view_registry.items() if ts.timestamp() < cutoff]
        for stale_key in stale_keys:
            _view_registry.pop(stale_key, None)

    if registry_key not in _view_registry:
        updated = await database_manager.increment_views(video_id)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update view count",
            )
        _view_registry[registry_key] = datetime.now()
        unique_view_applied = True

    analytics = await database_manager.get_analytics(video_id)
    return {
        "video_id": str(video_id),
        "views": analytics.views if analytics else None,
        "watch_duration_seconds": payload.watch_duration_seconds,
        "completed": payload.completed,
        "unique_view_applied": unique_view_applied,
    }


@router.get("/videos/stream/{video_id}")
async def stream_video(video_id: int):
    """Stream a video file from R2 storage.

    This endpoint proxies video files from R2 storage to the client,
    bypassing CORS and public access restrictions.

    Args:
        video_id: Video ID

    Returns:
        StreamingResponse with video content

    Raises:
        HTTPException: If video not found or cannot be streamed
    """
    from fastapi.responses import StreamingResponse
    from short_generator.services.r2_uploader import get_r2_uploader
    import boto3
    from botocore.exceptions import ClientError

    # Get video from database
    video = await database_manager.get_video(video_id)

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video not found: {video_id}",
        )

    # Extract R2 key from video URL
    # URL format: https://account.r2.cloudflarestorage.com/bucket/key
    url = video.video_url
    r2_uploader = get_r2_uploader()

    # Extract key from URL
    # Remove the base URL to get the key
    if url.startswith(r2_uploader.public_url):
        key = url[len(r2_uploader.public_url):].lstrip("/")
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid video URL format",
        )

    try:
        # Stream the video from R2
        response = r2_uploader.client.get_object(
            Bucket=r2_uploader.bucket_name,
            Key=key,
        )

        # Get content type
        content_type = response.get("ContentType", "video/mp4")

        # Generate streaming response
        def iterfile():
            """Iterate over the S3 object."""
            for chunk in response["Body"].iter_chunks():
                yield chunk

        return StreamingResponse(
            iterfile(),
            media_type=content_type,
            headers={
                "Content-Disposition": f"inline; filename={video.chapter_id}.mp4",
                "Accept-Ranges": "bytes",
            }
        )

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        if error_code == "NoSuchKey":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video file not found in storage: {key}",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stream video from R2: {str(e)}",
        )


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check for the shorts generation service.

    Returns:
        HealthResponse with service status and component health
    """
    components = {}

    # Check database
    db_healthy = await database_manager.health_check()
    components["database"] = "healthy" if db_healthy else "unhealthy"

    # Check R2 (assume configured if settings exist)
    components["r2_storage"] = "configured"

    # Check TTS (assume configured if credentials exist)
    from short_generator.core.config import settings

    if settings.google_cloud_credentials_path:
        components["tts_service"] = "configured"
    else:
        components["tts_service"] = "not_configured"

    # Check FFmpeg
    import subprocess
    from short_generator.services.ffmpeg_utils import get_ffmpeg_path

    try:
        subprocess.run(
            [get_ffmpeg_path(), "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
        )
        components["ffmpeg"] = "available"
    except Exception:
        components["ffmpeg"] = "not_available"

    overall_status = "healthy" if all(
        v in ("healthy", "configured", "available") for v in components.values()
    ) else "degraded"

    return HealthResponse(
        status=overall_status,
        service="shorts-generation",
        components=components,
    )


@router.delete("/videos/{video_id}")
async def delete_video(video_id: int) -> dict[str, Any]:
    """Delete a video.

    Args:
        video_id: Video ID

    Returns:
        dict with deletion status

    Raises:
        HTTPException: If video not found
    """
    video = await database_manager.get_video(video_id)

    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video not found: {video_id}",
        )

    # Delete from database
    deleted = await database_manager.delete_video(video_id)

    # TODO: Delete from R2 storage

    return {
        "video_id": video_id,
        "deleted": deleted,
        "message": "Video deleted successfully" if deleted else "Failed to delete video",
    }


# Batch Processing Endpoints


class BatchChapterInput(BaseModel):
    """Input for a single chapter in a batch."""

    chapter_id: str = Field(..., description="Unique chapter identifier")
    chapter_title: str = Field(..., description="Title of the chapter")
    chapter_number: int | None = Field(None, description="Chapter number")
    markdown_content: str | None = Field(None, description="Markdown content")
    markdown_file: str | None = Field(None, description="Path to markdown file")
    voice_preset: str | None = Field(None, description="TTS voice preset")


class BatchGenerateRequest(BaseModel):
    """Request for batch video generation."""

    batch_id: str | None = Field(None, description="Optional custom batch ID")
    chapters: list[BatchChapterInput] = Field(
        ..., description="List of chapters to process", min_length=1
    )
    max_concurrent: int = Field(3, ge=1, le=10, description="Max concurrent jobs")
    fail_fast: bool = Field(False, description="Stop on first failure")
    resume: bool = Field(False, description="Skip already completed videos")


class BatchGenerateResponse(BaseModel):
    """Response for batch generation request."""

    batch_id: str
    status: str
    total_chapters: int
    message: str


class BatchStatusResponse(BaseModel):
    """Response for batch status query."""

    batch_id: str
    status: str
    total_chapters: int
    completed: int
    failed: int
    skipped: int
    progress_percent: int
    started_at: datetime | None = None
    completed_at: datetime | None = None
    results: list[dict[str, Any]] = []


@router.post("/batch/generate", response_model=BatchGenerateResponse)
async def batch_generate(
    request: BatchGenerateRequest,
    background_tasks: BackgroundTasks,
) -> BatchGenerateResponse:
    """Generate multiple short videos in batch.

    Processes multiple chapters concurrently with configurable limits.
    Each chapter is processed independently with its own retry logic.

    Args:
        request: Batch generation request
        background_tasks: FastAPI background tasks

    Returns:
        BatchGenerateResponse with batch_id for tracking
    """
    from short_generator.services.pipeline_orchestrator import (
        ChapterInput,
        pipeline_orchestrator,
    )

    logger.info(
        f"Received batch generation request for {len(request.chapters)} chapters"
    )

    # Convert request inputs
    chapters = [
        ChapterInput(
            chapter_id=ch.chapter_id,
            chapter_title=ch.chapter_title,
            chapter_number=ch.chapter_number,
            markdown_content=ch.markdown_content,
            markdown_file=ch.markdown_file,
            voice_preset=ch.voice_preset,
        )
        for ch in request.chapters
    ]

    # Create batch ID
    batch_id = request.batch_id or f"batch-{uuid.uuid4().hex[:8]}"

    # Update orchestrator config

    orchestrator = pipeline_orchestrator
    orchestrator.config.max_concurrent_jobs = request.max_concurrent
    orchestrator.config.fail_fast = request.fail_fast

    # Trigger background task
    async def run_batch():
        result = await orchestrator.generate_batch(
            chapters=chapters,
            batch_id=batch_id,
        )
        logger.info(
            f"Batch {batch_id} complete: "
            f"{result.completed} succeeded, {result.failed} failed"
        )

    background_tasks.add_task(run_batch)

    return BatchGenerateResponse(
        batch_id=batch_id,
        status="queued",
        total_chapters=len(chapters),
        message=f"Batch generation job created with {len(chapters)} chapters",
    )


@router.get("/batch/{batch_id}/status", response_model=BatchStatusResponse)
async def get_batch_status(batch_id: str) -> BatchStatusResponse:
    """Get the status of a batch generation job.

    Args:
        batch_id: Batch ID

    Returns:
        BatchStatusResponse with current batch status

    Raises:
        HTTPException: If batch_id not found
    """
    from short_generator.services.pipeline_orchestrator import pipeline_orchestrator

    batch_result = pipeline_orchestrator.get_batch_status(batch_id)

    if not batch_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch not found: {batch_id}",
        )

    # Convert results to dicts
    results = [
        {
            "chapter_id": r.chapter_id,
            "success": r.success,
            "video_id": r.video_id,
            "video_url": r.video_url,
            "duration_seconds": r.duration_seconds,
            "error_message": r.error_message,
            "retry_count": r.retry_count,
        }
        for r in batch_result.results
    ]

    return BatchStatusResponse(
        batch_id=batch_result.batch_id,
        status=batch_result.status.value,
        total_chapters=batch_result.total_chapters,
        completed=batch_result.completed,
        failed=batch_result.failed,
        skipped=batch_result.skipped,
        progress_percent=batch_result.progress_percent,
        started_at=batch_result.started_at,
        completed_at=batch_result.completed_at,
        results=results,
    )


@router.post("/batch/{batch_id}/cancel")
async def cancel_batch(batch_id: str) -> dict[str, Any]:
    """Cancel a running batch generation job.

    Args:
        batch_id: Batch ID to cancel

    Returns:
        dict with cancellation status

    Raises:
        HTTPException: If batch_id not found
    """
    from short_generator.services.pipeline_orchestrator import pipeline_orchestrator

    cancelled = await pipeline_orchestrator.cancel_batch(batch_id)

    if not cancelled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch not found or already completed: {batch_id}",
        )

    return {
        "batch_id": batch_id,
        "cancelled": True,
        "message": "Batch cancellation requested",
    }


@router.post("/batch/directory")
async def batch_generate_from_directory(
    background_tasks: BackgroundTasks,
    root_dir: str = Query(..., description="Root directory containing chapters"),
    pattern: str = Query("*.md", description="File pattern to match"),
    batch_id: str | None = None,
    voice_preset: str | None = None,
    resume: bool = False,
    max_concurrent: int = Query(3, ge=1, le=10),
) -> BatchGenerateResponse:
    """Generate videos for all chapters in a directory.

    Convenience endpoint that auto-discovers and processes all
    markdown files in a directory.

    Args:
        root_dir: Root directory containing chapter files
        pattern: Glob pattern for file matching
        batch_id: Optional custom batch ID
        voice_preset: TTS voice preset
        resume: Skip already completed videos
        max_concurrent: Max concurrent processing jobs
        background_tasks: FastAPI background tasks

    Returns:
        BatchGenerateResponse with batch_id for tracking

    Raises:
        HTTPException: If directory not found or no chapters found
    """
    from pathlib import Path

    # Validate directory
    dir_path = Path(root_dir)
    if not dir_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Directory not found: {root_dir}",
        )

    from short_generator.services.batch_processor import batch_processor

    # Generate batch ID
    batch_id = batch_id or f"batch-dir-{uuid.uuid4().hex[:8]}"

    # Trigger background task
    async def run_directory_batch():
        report = await batch_processor.process_directory(
            root_dir=root_dir,
            pattern=pattern,
            batch_id=batch_id,
            voice_preset=voice_preset,
            resume=resume,
        )
        logger.info(
            f"Directory batch {batch_id} complete: "
            f"{report.successful} succeeded, {report.failed} failed"
        )

    background_tasks.add_task(run_directory_batch)

    return BatchGenerateResponse(
        batch_id=batch_id,
        status="queued",
        total_chapters=0,  # Unknown until discovery runs
        message=f"Directory batch generation job created for {root_dir}",
    )
