"""Knowledge Checkpoints endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.auth import CurrentUser, get_current_user
from ..core.database import get_session
from ..models.checkpoint import CheckpointAttempt, KnowledgeCheckpoint
from ..schemas.checkpoints import (
    CheckpointAnswerRequest,
    CheckpointAnswerResponse,
    CheckpointQuestion,
    CheckpointResponse,
)
from ..services.shared import (
    get_activity_dates,
    invalidate_user_cache,
    update_user_progress,
)

router = APIRouter()


@router.get("/checkpoints", response_model=CheckpointResponse)
async def get_checkpoint(
    lesson_slug: str = Query(..., description="Lesson slug"),
    position_pct: int = Query(..., ge=0, le=100, description="Scroll position percentage"),
    session: AsyncSession = Depends(get_session),
) -> CheckpointResponse:
    """Get a checkpoint question for a lesson at a specific scroll position.

    Returns the checkpoint question data for display in the modal.
    """
    result = await session.execute(
        select(KnowledgeCheckpoint).where(
            KnowledgeCheckpoint.lesson_slug == lesson_slug,
            KnowledgeCheckpoint.position_pct == position_pct,
        )
    )
    checkpoint = result.scalar_one_or_none()

    if not checkpoint:
        # Return a default checkpoint if none exists
        checkpoint = KnowledgeCheckpoint(
            lesson_slug=lesson_slug,
            position_pct=position_pct,
            question_data={
                "question": "Are you ready to test your understanding?",
                "options": ["Yes, let's continue!", "I need to review this section"],
                "correct_answer": 0,
                "explanation": "Great! Keep up the good work.",
            },
            xp_bonus=5,
        )
        session.add(checkpoint)
        await session.commit()
        await session.refresh(checkpoint)

    question = CheckpointQuestion(**checkpoint.question_data)

    return CheckpointResponse(
        id=checkpoint.id,
        lesson_slug=checkpoint.lesson_slug,
        position_pct=checkpoint.position_pct,
        question=question,
        xp_bonus=checkpoint.xp_bonus,
    )


@router.post("/checkpoints/answer", response_model=CheckpointAnswerResponse)
async def submit_checkpoint_answer(
    request: CheckpointAnswerRequest,
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> CheckpointAnswerResponse:
    """Submit an answer to a checkpoint question.

    Records the attempt and awards XP if correct.
    """
    # Get checkpoint
    result = await session.execute(
        select(KnowledgeCheckpoint).where(KnowledgeCheckpoint.id == request.checkpoint_id)
    )
    checkpoint = result.scalar_one_or_none()

    if not checkpoint:
        raise HTTPException(status_code=404, detail="Checkpoint not found")

    # Check if already attempted
    result = await session.execute(
        select(CheckpointAttempt).where(
            CheckpointAttempt.user_id == user.id,
            CheckpointAttempt.checkpoint_id == request.checkpoint_id,
        )
    )
    existing_attempt = result.scalar_one_or_none()

    if existing_attempt:
        question = CheckpointQuestion(**checkpoint.question_data)
        return CheckpointAnswerResponse(
            correct=existing_attempt.correct,
            explanation=checkpoint.question_data.get("explanation", ""),
            correct_answer=checkpoint.question_data.get("correct_answer", 0),
            xp_awarded=existing_attempt.xp_awarded,
            total_xp=0,
        )

    # Check answer
    question = CheckpointQuestion(**checkpoint.question_data)
    is_correct = request.answer == question.correct_answer

    # Record attempt
    attempt = CheckpointAttempt(
        user_id=user.id,
        checkpoint_id=checkpoint.id,
        answer=str(request.answer),
        correct=is_correct,
        xp_awarded=checkpoint.xp_bonus if is_correct else 0,
    )
    session.add(attempt)

    xp_awarded = 0
    total_xp = 0

    if is_correct:
        # Award XP
        activity_dates = await get_activity_dates(session, user.id)
        from datetime import date

        today = date.today()
        if today not in activity_dates:
            activity_dates.append(today)

        from ..services.engine.streaks import calculate_streak

        current_streak, longest_streak = calculate_streak(activity_dates, today=today)

        progress = await update_user_progress(
            session,
            user.id,
            xp_delta=checkpoint.xp_bonus,
            current_streak=current_streak,
            longest_streak=longest_streak,
            last_activity_date=today,
        )

        xp_awarded = checkpoint.xp_bonus
        total_xp = progress.total_xp if progress else checkpoint.xp_bonus

        await invalidate_user_cache(user.id)

    await session.commit()

    return CheckpointAnswerResponse(
        correct=is_correct,
        explanation=question.explanation,
        correct_answer=question.correct_answer,
        xp_awarded=xp_awarded,
        total_xp=total_xp,
    )
