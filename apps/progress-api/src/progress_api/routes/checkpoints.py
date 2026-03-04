"""Knowledge Checkpoints endpoints."""

import json
import os
import random
from pathlib import Path
from typing import Any

import httpx
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
from dotenv import load_dotenv,find_dotenv

load_dotenv(find_dotenv())

router = APIRouter()

# Path to lesson docs - calculate from the progress-api directory
# checkpoints.py is at: progress-api/src/progress_api/routes/checkpoints.py
# We need to go to: agentfactory/apps/learn-app/docs
_file_path = Path(__file__).resolve()
_progress_api_path = _file_path.parent
for _ in range(5):  # Go up 5 levels to reach agentfactory root
    _progress_api_path = _progress_api_path.parent
DOCS_PATH = _progress_api_path / "apps" / "learn-app" / "docs"
print(f"[Checkpoint] DOCS_PATH: {DOCS_PATH}, exists: {DOCS_PATH.exists()}")

# Optional: Google Gemini API key for LLM fallback question generation
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


async def extract_questions_from_lesson(lesson_slug: str) -> list[dict] | None:
    """Extract checkpoint questions from lesson frontmatter.

    Looks for a 'checkpoint_questions' field in the lesson's YAML frontmatter.
    Format:
      checkpoint_questions:
        - question: "..."
          options: ["A", "B", "C", "D"]
          correct_answer: 0
          explanation: "..."

    Note: lesson_slug from URL doesn't include numeric prefixes (e.g., "General-Agents-Foundations/agent-factory-paradigm/the-2025-inflection-point")
    but filesystem does (e.g., "01-General-Agents-Foundations/01-agent-factory-paradigm/01-the-2025-inflection-point.md")
    """
    import yaml
    import re

    try:
        # First, try direct path with lesson_slug
        lesson_path = DOCS_PATH / f"{lesson_slug}.md"

        if not lesson_path.exists():
            # Try to find by searching - match by stripping numeric prefixes
            # URL: General-Agents-Foundations/agent-factory-paradigm/the-2025-inflection-point
            # File: 01-General-Agents-Foundations/01-agent-factory-paradigm/01-the-2025-inflection-point.md
            lesson_name = lesson_slug.split("/")[-1]

            for md_file in DOCS_PATH.rglob("*.md"):
                # Strip numeric prefix from filename (e.g., "01-the-2025-inflection-point" -> "the-2025-inflection-point")
                file_stem = md_file.stem
                # Remove leading digits and dash
                clean_stem = re.sub(r'^\d+-', '', file_stem)

                if clean_stem == lesson_name:
                    lesson_path = md_file
                    break

        if not lesson_path.exists():
            print(f"[Checkpoint] Lesson file not found: {lesson_slug}")
            return None

        content = lesson_path.read_text()

        # Parse YAML frontmatter (between --- markers)
        if not content.startswith("---"):
            print(f"[Checkpoint] No YAML frontmatter found in: {lesson_slug}")
            return None

        # Find the end of frontmatter
        end_idx = content.find("\n---", 4)
        if end_idx == -1:
            print(f"[Checkpoint] Invalid YAML frontmatter in: {lesson_slug}")
            return None

        frontmatter = content[4:end_idx]

        # Parse the entire frontmatter as YAML
        try:
            data = yaml.safe_load(frontmatter)
        except yaml.YAMLError as e:
            print(f"[Checkpoint] YAML parse error in {lesson_slug}: {e}")
            return None

        # Extract checkpoint_questions
        questions = data.get("checkpoint_questions")
        if not questions:
            print(f"[Checkpoint] No checkpoint_questions found in: {lesson_slug}")
            return None

        print(f"[Checkpoint] Found {len(questions)} questions in: {lesson_slug}")
        return questions

    except Exception as e:
        print(f"[Checkpoint] Error extracting questions from lesson {lesson_slug}: {e}")
        return None


async def generate_llm_question(lesson_slug: str, lesson_content: str | None = None) -> dict | None:
    """Generate a knowledge checkpoint question using Google Gemini API.

    Falls back to this if no questions found in frontmatter.
    """
    if not GEMINI_API_KEY:
        return None

    try:
        # Try to read lesson content for context
        import re
        lesson_path = DOCS_PATH / f"{lesson_slug}.md"
        context = ""

        # If direct path doesn't exist, search with numeric prefix stripping
        if not lesson_path.exists():
            lesson_name = lesson_slug.split("/")[-1]
            for md_file in DOCS_PATH.rglob("*.md"):
                file_stem = md_file.stem
                clean_stem = re.sub(r'^\d+-', '', file_stem)
                if clean_stem == lesson_name:
                    lesson_path = md_file
                    break

        if lesson_path.exists():
            content = lesson_path.read_text()
            # Extract frontmatter and first paragraph for context
            end_idx = content.find("\n---", 4)
            if end_idx != -1:
                frontmatter = content[4:end_idx]
                # Get content after frontmatter
                lesson_body = content[end_idx + 5 :][:1500]
                context = f"Frontmatter:\n{frontmatter}\n\nLesson start:\n{lesson_body}"

        # Generate a knowledge question using Gemini
        prompt = f"""Based on the following lesson context, generate ONE knowledge checkpoint question to test the reader's understanding.

Lesson: {lesson_slug}
{context}

Generate a JSON object with this exact format:
{{
    "question": "Specific knowledge question about the lesson content",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": 0,
    "explanation": "Brief explanation of why this is the correct answer"
}}

Requirements:
- Question must test factual knowledge from the lesson
- All options should be plausible
- Only return the JSON, no other text

Response:"""

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={GEMINI_API_KEY}",
                headers={"content-type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.7,
                        "maxOutputTokens": 500,
                    },
                },
            )

            if response.status_code == 200:
                data = response.json()
                content = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                # Extract JSON from response - handle markdown code blocks
                import re
                # Try to find JSON in code blocks first
                json_match = re.search(r'```(?:json)?\s*(\{{[^}]*"question"[^}]*\}})\s*```', content, re.DOTALL)
                if not json_match:
                    # Try to find JSON without code blocks
                    json_match = re.search(r'\{[^{}]*"question"[^{}]*\}', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1) if '```' in json_match.group() else json_match.group()
                    return json.loads(json_str)

    except Exception as e:
        print(f"Error generating LLM question: {e}")

    return None


# Fallback knowledge-based templates (used only if frontmatter and LLM fail)
FALLBACK_KNOWLEDGE_TEMPLATES = {
    50: [
        {
            "question": "What is the core concept being explained in this lesson so far?",
            "options": [
                "The main technical principle or framework",
                "A supporting example or use case",
                "Background context or history",
            ],
            "correct_answer": 0,
            "explanation": "Identifying the core concept helps you build a strong mental model of the topic.",
        },
        {
            "question": "Which term or concept from this lesson was newly introduced?",
            "options": [
                "Can identify the key terminology",
                "Recognize some but not all terms",
                "Need to review the key terms",
            ],
            "correct_answer": 0,
            "explanation": "New terminology is the foundation of technical learning. Make sure you understand these terms!",
        },
    ],
    75: [
        {
            "question": "What practical application did this lesson demonstrate?",
            "options": [
                "Can describe the practical use case",
                "Understand the theory but not the application",
                "Need to review the examples",
            ],
            "correct_answer": 0,
            "explanation": "Connecting theory to practice is essential for real-world skill development.",
        },
        {
            "question": "How would you explain the main concept from this lesson to a beginner?",
            "options": [
                "Can explain it in simple terms",
                "Can explain with some technical details",
                "Would need notes to explain it",
            ],
            "correct_answer": 0,
            "explanation": "The Feynman Technique: if you can't explain it simply, you don't understand it well enough.",
        },
    ],
}


async def generate_checkpoint_question(lesson_slug: str, position_pct: int) -> dict:
    """Generate a knowledge checkpoint question for a lesson using hybrid approach.

    Priority:
    1. Extract from lesson frontmatter (checkpoint_questions field)
    2. Generate using LLM (Gemini) based on lesson content
    3. Fallback to knowledge-based templates
    """

    # Try to extract from lesson frontmatter first
    frontmatter_questions = await extract_questions_from_lesson(lesson_slug)
    if frontmatter_questions:
        # Filter questions by position if specified, or use random
        position_questions = [q for q in frontmatter_questions if q.get("position_pct") == position_pct]
        if position_questions:
            return random.choice(position_questions)
        # Use any question if no position-specific ones
        if frontmatter_questions:
            return random.choice(frontmatter_questions)

    # Try LLM generation
    llm_question = await generate_llm_question(lesson_slug)
    if llm_question:
        return llm_question

    # Fallback to knowledge-based templates
    templates = FALLBACK_KNOWLEDGE_TEMPLATES.get(position_pct, FALLBACK_KNOWLEDGE_TEMPLATES[50])
    return random.choice(templates)


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
        # Generate a contextual checkpoint question using hybrid approach
        question_data = await generate_checkpoint_question(lesson_slug, position_pct)
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
