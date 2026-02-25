"""Batch short video generation endpoint."""

import logging
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from shorts_generator.core.config import settings
from shorts_generator.database.connection import get_session
from shorts_generator.models import GenerationJob
from shorts_generator.workers.tasks import generate_short_task

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/batch", tags=["Batch Generation"])


class BatchGenerateRequest(BaseModel):
    """Request to generate multiple short videos."""

    lesson_paths: list[str]
    target_duration: int = 60
    voice: str = "en-US-AriaNeural"
    priority: str = "normal"  # normal, high, low


class BatchGenerateResponse(BaseModel):
    """Response from batch generation request."""

    batch_id: str
    job_count: int
    status: str
    message: str


class BatchJobSummary(BaseModel):
    """Summary of batch job status."""

    batch_id: str
    total_jobs: int
    completed_jobs: int
    failed_jobs: int
    in_progress_jobs: int
    queued_jobs: int


@router.post("", response_model=BatchGenerateResponse, status_code=status.HTTP_202_ACCEPTED)
async def batch_generate_shorts(
    request: BatchGenerateRequest,
    session: AsyncSession = Depends(get_session),
) -> BatchGenerateResponse:
    """Generate multiple short videos in batch.

    This endpoint creates generation jobs for multiple lessons.
    Jobs are processed asynchronously by the Celery worker.

    Args:
        request: Batch generation request with lesson_paths
        session: Database session

    Returns:
        BatchGenerateResponse with batch_id and job count

    Raises:
        HTTPException: If batch request is invalid
    """
    logger.info(f"Received batch generation request for {len(request.lesson_paths)} lessons")

    # Validate lesson paths
    if not request.lesson_paths:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="lesson_paths must contain at least one lesson",
        )

    if len(request.lesson_paths) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot generate more than 100 shorts in a single batch",
        )

    # Validate priority
    if request.priority not in ["normal", "high", "low"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="priority must be one of: normal, high, low",
        )

    # Create batch ID
    batch_id = str(uuid4())

    # Create generation jobs for each lesson
    jobs = []
    for lesson_path in request.lesson_paths:
        job_id = str(uuid4())

        job = GenerationJob(
            id=job_id,
            lesson_path=lesson_path,
            status="queued",
            progress=0,
            retry_count=0,
        )

        session.add(job)
        jobs.append(job)

    await session.commit()

    logger.info(f"Created batch {batch_id} with {len(jobs)} generation jobs")

    # Trigger Celery tasks for each job with priority queue
    priority_map = {"high": 5, "normal": 3, "low": 1}
    priority = priority_map.get(request.priority, 3)

    for job in jobs:
        task = generate_short_task.apply_async(
            args=[
                job.id,
                job.lesson_path,
                request.target_duration,
                request.voice,
            ],
            queue=request.priority,  # Route to priority queue
            priority=priority,  # Set task priority within queue
        )
        logger.info(f"Dispatched task {task.id} for job {job.id} with priority {request.priority}")

    return BatchGenerateResponse(
        batch_id=batch_id,
        job_count=len(jobs),
        status="queued",
        message=f"Batch generation job created with {len(jobs)} lessons",
    )


@router.get("/status/{batch_id}", response_model=BatchJobSummary)
async def get_batch_status(
    batch_id: str,
    session: AsyncSession = Depends(get_session),
) -> BatchJobSummary:
    """Get the status of a batch generation job.

    Args:
        batch_id: Batch ID to check
        session: Database session

    Returns:
        BatchJobSummary with job counts by status

    Raises:
        HTTPException: If batch_id not found
    """
    # TODO: Implement batch tracking in database
    # For now, return a placeholder response
    logger.warning(f"Batch status tracking not implemented for batch_id: {batch_id}")

    return BatchJobSummary(
        batch_id=batch_id,
        total_jobs=0,
        completed_jobs=0,
        failed_jobs=0,
        in_progress_jobs=0,
        queued_jobs=0,
    )


@router.get("/estimate-cost")
async def estimate_batch_cost(
    lesson_count: int,
    target_duration: int = 60,
) -> dict:
    """Estimate the cost for batch video generation.

    Args:
        lesson_count: Number of videos to generate
        target_duration: Target video duration in seconds

    Returns:
        dict with cost breakdown
    """
    # Cost per video (based on current service pricing)
    script_cost = 0.002  # Gemini 2.0 Flash
    visuals_cost = 0.002 * 5  # 5 scenes (hook + 3 concepts + example + cTA)
    audio_cost = 0.0  # Edge-TTS is free
    storage_cost = 0.0001  # Approximate R2 storage cost

    cost_per_video = script_cost + visuals_cost + audio_cost + storage_cost
    total_cost = cost_per_video * lesson_count

    return {
        "lesson_count": lesson_count,
        "cost_per_video_usd": round(cost_per_video, 4),
        "total_cost_usd": round(total_cost, 2),
        "breakdown": {
            "script_generation_usd": round(script_cost * lesson_count, 4),
            "visual_generation_usd": round(visuals_cost * lesson_count, 4),
            "audio_generation_usd": 0.0,
            "storage_usd": round(storage_cost * lesson_count, 4),
        },
    }
