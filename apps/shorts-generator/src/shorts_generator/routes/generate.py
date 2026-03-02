"""Single short video generation endpoint."""

import asyncio
import logging
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from shorts_generator.core.config import settings
from shorts_generator.database.connection import get_session
from shorts_generator.models import GenerationJob, ShortVideo
from shorts_generator.services.audio_generator import audio_generator
from shorts_generator.services.content_extractor import ContentExtractor
from shorts_generator.services.script_generator import ScriptGenerator
from shorts_generator.services.video_assembler import VideoAssembler
from shorts_generator.services.visual_generator import VisualGenerator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/generate", tags=["Generation"])

# Service singletons
content_extractor = ContentExtractor()
script_generator = ScriptGenerator()
visual_generator = VisualGenerator()
video_assembler = VideoAssembler()


class GenerateRequest(BaseModel):
    """Request to generate a single short video."""

    lesson_path: str
    target_duration: int = 60
    voice: str = "en-US-AriaNeural"


class GenerateResponse(BaseModel):
    """Response from short video generation."""

    job_id: str
    status: str
    message: str


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


@router.post("", response_model=GenerateResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_short(
    request: GenerateRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
) -> GenerateResponse:
    """Generate a single short video from a lesson.

    This endpoint:
    1. Extracts content from the lesson
    2. Generates a script using Gemini
    3. Creates visuals using Flux.1
    4. Generates narration using Edge-TTS
    5. Assembles the final video using FFmpeg
    6. Returns a job_id for tracking progress

    Args:
        request: Generation request with lesson_path and options
        background_tasks: FastAPI BackgroundTasks for async execution
        session: Database session

    Returns:
        GenerateResponse with job_id and initial status

    Raises:
        HTTPException: If generation request is invalid
    """
    logger.info(f"Received generation request for lesson: {request.lesson_path}")

    # Validate lesson path
    if not request.lesson_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="lesson_path is required",
        )

    # Validate target duration
    if not (30 <= request.target_duration <= 90):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="target_duration must be between 30 and 90 seconds",
        )

    # Create generation job
    job_id = str(uuid4())

    job = GenerationJob(
        id=job_id,
        lesson_path=request.lesson_path,
        status="queued",
        progress=0,
        retry_count=0,
    )

    session.add(job)
    await session.commit()

    logger.info(f"Created generation job: {job_id}")

    # Trigger background task for async generation
    background_tasks.add_task(
        _run_generation_task,
        job_id=job_id,
        lesson_path=request.lesson_path,
        target_duration=request.target_duration,
        voice=request.voice,
    )

    logger.info(f"Dispatched background task for job: {job_id}")

    return GenerateResponse(
        job_id=job_id,
        status="queued",
        message="Short video generation job created successfully",
    )


@router.post("/sync", response_model=dict, status_code=status.HTTP_200_OK)
async def generate_short_sync(
    request: GenerateRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Generate a single short video synchronously (blocking).

    This endpoint performs all generation steps synchronously and returns
    the completed video. Intended for testing and low-volume scenarios.

    WARNING: This endpoint may take 2-5 minutes to complete.

    Args:
        request: Generation request with lesson_path and options
        session: Database session

    Returns:
        dict with video metadata

    Raises:
        HTTPException: If generation fails
    """
    logger.info(f"Received sync generation request for lesson: {request.lesson_path}")

    try:
        # Step 1: Extract content
        logger.info("Step 1: Extracting content from lesson")
        lesson_content = await content_extractor.extract_content(request.lesson_path)

        if not lesson_content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Could not extract content from lesson: {request.lesson_path}",
            )

        # Step 2: Generate script
        logger.info("Step 2: Generating script with Gemini")
        script = await script_generator.generate_script(
            lesson_content,
            target_duration=request.target_duration,
        )

        # Step 3: Generate visuals
        logger.info(f"Step 3: Generating {len(script.concepts)} scene visuals")
        scene_images = []

        # Generate hook visual
        hook_image = await visual_generator.generate_scene_image(
            script.hook.visual_description,
        )
        scene_images.append(hook_image.url)

        # Generate concept visuals
        for concept in script.concepts:
            concept_image = await visual_generator.generate_scene_image(
                concept.visual_description,
            )
            scene_images.append(concept_image.url)

        # Generate example visual (if code screenshot)
        if "code" in script.example.visual_description.lower():
            example_image = await visual_generator.generate_code_screenshot(
                script.example.text,
                "python",  # TODO: Detect language
            )
        else:
            example_image = await visual_generator.generate_scene_image(
                script.example.visual_description,
            )
        scene_images.append(example_image.url)

        # Generate CTA visual
        cta_image = await visual_generator.generate_scene_image(
            script.cta.visual_description,
        )
        scene_images.append(cta_image.url)

        # Step 4: Generate audio
        logger.info("Step 4: Generating narration with Edge-TTS")
        full_script = script_generator.format_for_tts(script)
        audio, captions = await audio_generator.generate_audio_for_script(
            full_script,
            voice=request.voice,
            add_music=False,  # TODO: Make configurable
        )

        # Step 5: Assemble video
        logger.info("Step 5: Assembling final video with FFmpeg")
        video = await video_assembler.assemble_video(
            scene_images=scene_images,
            audio=audio,
            script=script,
            captions=captions,
            script_text=full_script,
        )

        # Step 6: Save to database
        logger.info("Step 6: Saving video metadata to database")

        short_video = ShortVideo(
            id=str(uuid4()),
            lesson_path=request.lesson_path,
            title=lesson_content.title,
            script=full_script,
            duration_seconds=script.total_duration,
            video_url=video.url,
            thumbnail_url=video.thumbnail_url,
            captions_url="",  # TODO: Upload captions to R2
            generation_cost=0.006,  # TODO: Calculate actual cost
        )

        session.add(short_video)
        await session.commit()

        logger.info(f"Video generation complete: {short_video.id}")

        return {
            "video_id": short_video.id,
            "lesson_path": request.lesson_path,
            "title": short_video.title,
            "duration_seconds": short_video.duration_seconds,
            "video_url": short_video.video_url,
            "thumbnail_url": short_video.thumbnail_url,
            "file_size_mb": video.file_size_mb,
            "generation_cost": short_video.generation_cost,
        }

    except Exception as e:
        logger.error(f"Video generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Video generation failed: {str(e)}",
        )
