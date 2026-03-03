"""Knowledge Checkpoints endpoints."""

import random
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


# Checkpoint question templates for different positions and contexts
CHECKPOINT_TEMPLATES = {
    50: [  # Mid-lesson checkpoints
        {
            "question": "Let's check your understanding so far. Which concept from this section resonates most with you?",
            "options": [
                "I understand the core concepts well",
                "I need to review some key ideas",
                "I'm confused and need clarification",
            ],
            "correct_answer": 0,
            "explanation": "Great that you're engaging with the material! Keeping track of your understanding helps you learn more effectively.",
        },
        {
            "question": "Quick knowledge check: What's the main takeaway from what you've read so far?",
            "options": [
                "I can explain it clearly",
                "I understand the basics",
                "I'm still processing the information",
            ],
            "correct_answer": 0,
            "explanation": "Being able to articulate key concepts shows strong learning. Keep up the good work!",
        },
        {
            "question": "How confident are you with the material covered up to this point?",
            "options": [
                "Very confident - ready to move on",
                "Somewhat confident - but slowing down",
                "Not confident - need to re-read",
            ],
            "correct_answer": 0,
            "explanation": "Confidence monitoring is an important part of learning. Adjust your pace based on how you're feeling!",
        },
    ],
    75: [  # Near-end checkpoints
        {
            "question": "You're almost done! What's one thing you'll apply from this lesson?",
            "options": [
                "I have several ideas in mind",
                "I'm thinking about how to use this",
                "Not sure yet, need to finish first",
            ],
            "correct_answer": 0,
            "explanation": "Applying what you learn is key to retention! Great job thinking about practical applications.",
        },
        {
            "question": "Final check: Would you be able to explain this lesson's content to someone else?",
            "options": [
                "Yes, I could teach this now",
                "Mostly, with some notes",
                "I'd need more practice first",
            ],
            "correct_answer": 0,
            "explanation": "The Feynman Technique says if you can't explain it simply, you don't understand it well enough yet.",
        },
        {
            "question": "How would you rate your comprehension of this lesson overall?",
            "options": [
                "Excellent - I've learned a lot",
                "Good - with some areas to review",
                "Challenging - but I'm making progress",
            ],
            "correct_answer": 0,
            "explanation": "Self-assessment helps you identify areas where you need more practice. Great job being honest with yourself!",
        },
    ],
}


def generate_checkpoint_question(lesson_slug: str, position_pct: int) -> dict:
    """Generate a contextual checkpoint question for a lesson."""
    templates = CHECKPOINT_TEMPLATES.get(position_pct, CHECKPOINT_TEMPLATES[50])
    template = random.choice(templates)

    # Add lesson context to make it feel more personalized
    lesson_name = lesson_slug.replace("-", " ").replace("_", " ").title()

    return {
        "question": f"[{lesson_name}] {template['question']}",
        "options": template["options"],
        "correct_answer": template["correct_answer"],
        "explanation": template["explanation"],
    }


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
        # Generate a contextual checkpoint question
        question_data = generate_checkpoint_question(lesson_slug, position_pct)
        checkpoint = KnowledgeCheckpoint(
            lesson_slug=lesson_slug,
            position_pct=position_pct,
            question_data=question_data,
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
