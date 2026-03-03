"""Daily Challenges engine — generates and processes challenges.

This service handles:
- Challenge template definitions
- Daily challenge generation (7 days ahead)
- Progress tracking and completion checking
- XP bonus awards
"""

import json
import logging
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.auth import CurrentUser
from ...models.challenge import DailyChallenge, UserChallengeProgress
from ...schemas.challenges import (
    ChallengeCompleteResponse,
    ChallengeHistoryItem,
    ChallengeHistoryResponse,
    ChallengeProgress,
    ChallengeResponse,
)
from ..engine.streaks import calculate_streak
from ..shared import (
    get_activity_dates,
    invalidate_user_cache,
    update_user_progress,
)

logger = logging.getLogger(__name__)

# Challenge templates with default configuration
CHALLENGE_TEMPLATES = {
    "quiz_master": {
        "title": "Quiz Master",
        "description": "Complete {target_count} quizzes with {min_score}%+ score",
        "config": {"target_count": 3, "min_score": 80},
        "xp_bonus": 50,
    },
    "learning_spree": {
        "title": "Learning Spree",
        "description": "Complete {target_count} lessons today",
        "config": {"target_count": 5},
        "xp_bonus": 75,
    },
    "perfect_week": {
        "title": "Perfect Week",
        "description": "Maintain a {target_streak}-day streak",
        "config": {"target_streak": 7},
        "xp_bonus": 100,
    },
    "explorer": {
        "title": "Explorer",
        "description": "Complete activities from {target_parts} different parts",
        "config": {"target_parts": 3},
        "xp_bonus": 60,
    },
    "night_owl": {
        "title": "Night Owl",
        "description": "Complete a quiz after {after_hour}:00",
        "config": {"after_hour": 22},
        "xp_bonus": 30,
    },
    "early_bird": {
        "title": "Early Bird",
        "description": "Complete a quiz before {before_hour}:00",
        "config": {"before_hour": 8},
        "xp_bonus": 30,
    },
    "flashcard_fanatic": {
        "title": "Flashcard Fanatic",
        "description": "Complete {target_count} flashcard decks",
        "config": {"target_count": 3},
        "xp_bonus": 40,
    },
    "review_master": {
        "title": "Review Master",
        "description": "Complete {target_count} review items",
        "config": {"target_count": 5},
        "xp_bonus": 50,
    },
}


async def _ensure_templates_exist(session: AsyncSession) -> None:
    """Ensure challenge templates exist in the database.

    This is needed because daily_challenges has a foreign key to
    challenge_templates, but the templates might not be populated
    when using AUTO_CREATE_SCHEMA.
    """
    for template_id, template in CHALLENGE_TEMPLATES.items():
        await session.execute(
            text(
                """
                INSERT INTO challenge_templates
                (id, name, description, config_schema, xp_bonus, is_active)
                VALUES (:id, :name, :description, :config, :xp, true)
                ON CONFLICT (id) DO NOTHING
            """
            ),
            {
                "id": template_id,
                "name": template["title"],
                "description": template["description"],
                "config": json.dumps(template["config"]),
                "xp": template["xp_bonus"],
            },
        )
    await session.commit()


async def generate_daily_challenges(session: AsyncSession) -> None:
    """Generate challenges 7 days ahead using templates.

    Runs as a background task (typically via cron or on startup).
    Uses ON CONFLICT DO NOTHING to avoid duplicates.
    """
    # Ensure templates exist first
    await _ensure_templates_exist(session)

    today = date.today()
    template_types = list(CHALLENGE_TEMPLATES.keys())

    for days_ahead in range(7):
        target_date = today + timedelta(days=days_ahead + 1)

        # Pick a template (rotate through them)
        template_type = template_types[days_ahead % len(template_types)]
        template = CHALLENGE_TEMPLATES[template_type]

        # Format description with config values
        description = template["description"].format(**template["config"])

        # Use raw SQL for idempotent insert
        await session.execute(
            text(
                """
                INSERT INTO daily_challenges
                (challenge_date, challenge_type, title, description, config, xp_bonus)
                VALUES (:date, :type, :title, :description, :config, :xp)
                ON CONFLICT (challenge_date) DO NOTHING
            """
            ),
            {
                "date": target_date,
                "type": template_type,
                "title": template["title"],
                "description": description,
                "config": json.dumps(template["config"]),
                "xp": template["xp_bonus"],
            },
        )

    await session.commit()
    logger.info(f"Generated daily challenges through {today + timedelta(days=7)}")


async def get_today_challenge(
    session: AsyncSession,
    user: CurrentUser,
) -> ChallengeResponse:
    """Get today's challenge for a user, creating progress if needed."""
    today = date.today()

    # Get today's challenge
    result = await session.execute(
        select(DailyChallenge).where(DailyChallenge.challenge_date == today)
    )
    challenge = result.scalar_one_or_none()

    if challenge is None:
        # Generate today's challenge if missing
        await generate_daily_challenges(session)
        result = await session.execute(
            select(DailyChallenge).where(DailyChallenge.challenge_date == today)
        )
        challenge = result.scalar_one_or_none()

        if challenge is None:
            # Fallback: create a default challenge
            challenge = DailyChallenge(
                challenge_date=today,
                challenge_type="quiz_master",
                title="Daily Challenge",
                description="Complete activities to earn bonus XP",
                config={"target_count": 1},
                xp_bonus=25,
            )
            session.add(challenge)
            await session.commit()
            await session.refresh(challenge)

    # Get or create user progress
    result = await session.execute(
        select(UserChallengeProgress).where(
            UserChallengeProgress.user_id == user.id,
            UserChallengeProgress.challenge_id == challenge.id,
        )
    )
    progress_row = result.scalar_one_or_none()

    if progress_row is None:
        # Initialize progress
        target = challenge.config.get("target_count", 1)
        progress_row = UserChallengeProgress(
            user_id=user.id,
            challenge_id=challenge.id,
            progress={"current": 0, "target": target},
            completed=False,
        )
        session.add(progress_row)
        await session.commit()
        await session.refresh(progress_row)

    # Build response
    current = progress_row.progress.get("current", 0)
    target = challenge.config.get("target_count", 1)

    # Determine unit based on challenge type
    unit_map = {
        "quiz_master": "quizzes",
        "learning_spree": "lessons",
        "flashcard_fanatic": "decks",
        "review_master": "reviews",
        "explorer": "parts",
    }
    unit = unit_map.get(challenge.challenge_type, "items")

    return ChallengeResponse(
        id=challenge.id,
        challenge_date=challenge.challenge_date,
        challenge_type=challenge.challenge_type,
        title=challenge.title,
        description=challenge.description,
        config=challenge.config,
        xp_bonus=challenge.xp_bonus,
        progress=ChallengeProgress(current=current, target=target, unit=unit),
        completed=progress_row.completed,
        started_at=progress_row.started_at,
    )


async def update_challenge_progress(
    session: AsyncSession,
    user: CurrentUser,
    challenge_id: int,
    progress_delta: int,
) -> ChallengeCompleteResponse | ChallengeResponse:
    """Update challenge progress and award XP if completed.

    Args:
        session: Database session
        user: Current user
        challenge_id: Challenge ID
        progress_delta: Amount to add to current progress

    Returns:
        ChallengeCompleteResponse if challenge completed, ChallengeResponse otherwise
    """
    # Get challenge
    result = await session.execute(
        select(DailyChallenge).where(DailyChallenge.id == challenge_id)
    )
    challenge = result.scalar_one_or_none()
    if challenge is None:
        raise ValueError(f"Challenge {challenge_id} not found")

    # Get or create user progress
    result = await session.execute(
        select(UserChallengeProgress).where(
            UserChallengeProgress.user_id == user.id,
            UserChallengeProgress.challenge_id == challenge_id,
        ).with_for_update()
    )
    progress_row = result.scalar_one_or_none()

    if progress_row is None:
        progress_row = UserChallengeProgress(
            user_id=user.id,
            challenge_id=challenge_id,
            progress={"current": 0, "target": challenge.config.get("target_count", 1)},
            completed=False,
        )
        session.add(progress_row)
        await session.flush()
        # Re-fetch with lock
        result = await session.execute(
            select(UserChallengeProgress).where(
                UserChallengeProgress.user_id == user.id,
                UserChallengeProgress.challenge_id == challenge_id,
            ).with_for_update()
        )
        progress_row = result.scalar_one()

    # Don't update if already completed
    if progress_row.completed:
        current = progress_row.progress.get("current", 0)
        target = challenge.config.get("target_count", 1)
        unit_map = {
            "quiz_master": "quizzes",
            "learning_spree": "lessons",
            "flashcard_fanatic": "decks",
            "review_master": "reviews",
        }
        unit = unit_map.get(challenge.challenge_type, "items")

        return ChallengeResponse(
            id=challenge.id,
            challenge_date=challenge.challenge_date,
            challenge_type=challenge.challenge_type,
            title=challenge.title,
            description=challenge.description,
            config=challenge.config,
            xp_bonus=challenge.xp_bonus,
            progress=ChallengeProgress(current=current, target=target, unit=unit),
            completed=True,
            started_at=progress_row.started_at,
        )

    # Update progress
    current = progress_row.progress.get("current", 0) + progress_delta
    target = challenge.config.get("target_count", 1)
    progress_row.progress = {"current": current, "target": target}

    # Check if completed
    just_completed = current >= target and not progress_row.completed

    if just_completed:
        progress_row.completed = True
        progress_row.completed_at = datetime.now(UTC)
        progress_row.xp_awarded = challenge.xp_bonus

        # Award XP
        activity_dates = await get_activity_dates(session, user.id)
        today = date.today()
        if today not in activity_dates:
            activity_dates.append(today)
        current_streak, longest_streak = calculate_streak(activity_dates, today=today)

        progress = await update_user_progress(
            session,
            user.id,
            xp_delta=challenge.xp_bonus,
            current_streak=current_streak,
            longest_streak=longest_streak,
            last_activity_date=today,
        )

        await session.commit()

        await invalidate_user_cache(user.id)

        return ChallengeCompleteResponse(
            xp_earned=challenge.xp_bonus,
            total_xp=progress.total_xp if progress else challenge.xp_bonus,
            new_badges=[],
            streak={"current": current_streak, "longest": longest_streak},
        )

    await session.commit()
    await invalidate_user_cache(user.id)

    # Return updated progress
    unit_map = {
        "quiz_master": "quizzes",
        "learning_spree": "lessons",
        "flashcard_fanatic": "decks",
        "review_master": "reviews",
    }
    unit = unit_map.get(challenge.challenge_type, "items")

    return ChallengeResponse(
        id=challenge.id,
        challenge_date=challenge.challenge_date,
        challenge_type=challenge.challenge_type,
        title=challenge.title,
        description=challenge.description,
        config=challenge.config,
        xp_bonus=challenge.xp_bonus,
        progress=ChallengeProgress(current=current, target=target, unit=unit),
        completed=False,
        started_at=progress_row.started_at,
    )


async def get_challenge_history(
    session: AsyncSession,
    user: CurrentUser,
    days: int = 7,
) -> ChallengeHistoryResponse:
    """Get challenge history for past N days."""
    result = await session.execute(
        select(UserChallengeProgress, DailyChallenge)
        .join(DailyChallenge, UserChallengeProgress.challenge_id == DailyChallenge.id)
        .where(UserChallengeProgress.user_id == user.id)
        .where(DailyChallenge.challenge_date >= date.today() - timedelta(days=days))
        .order_by(DailyChallenge.challenge_date.desc())
    )

    challenges = []
    for progress_row, challenge in result.all():
        challenges.append(
            ChallengeHistoryItem(
                id=challenge.id,
                challenge_date=challenge.challenge_date,
                title=challenge.title,
                completed=progress_row.completed,
                xp_awarded=progress_row.xp_awarded,
                completed_at=progress_row.completed_at,
            )
        )

    return ChallengeHistoryResponse(challenges=challenges)
