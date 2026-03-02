"""Smart Review service — personalized review recommendations.

This service handles:
- Review queue generation based on:
  - Spaced repetition (FSRS-style intervals)
  - Weak areas (<70% quiz scores)
  - Prerequisites for next lesson
- Review completion tracking
- Interval calculation for next review
"""

import logging
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.chapter import Chapter, ChapterAlias
from ...models.quiz import QuizAttempt
from ...models.review import ReviewReminder
from ...schemas.review import (
    ReviewCompleteRequest,
    ReviewCompleteResponse,
    ReviewItem,
    ReviewQueueResponse,
)

logger = logging.getLogger(__name__)


async def generate_review_queue(user_id: str, session: AsyncSession) -> ReviewQueueResponse:
    """Generate personalized review queue for a user.

    Includes:
    1. Weak areas (chapters with <70% average score)
    2. Spaced repetition items (due today)
    3. Prerequisites for chapters in progress
    """
    today = date.today()

    # Get all existing uncompleted reviews
    # Generate weak area recommendations
    await _generate_weak_area_reviews(session, user_id, today)

    # Get updated queue
    result = await session.execute(
        select(ReviewReminder)
        .where(
            ReviewReminder.user_id == user_id,
            not ReviewReminder.completed,
        )
        .order_by(
            text("CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END"),
            ReviewReminder.due_date,
        )
        .limit(20)
    )
    items = result.scalars().all()

    # Count high priority
    high_priority_count = sum(1 for item in items if item.priority == "high")

    return ReviewQueueResponse(
        items=[
            ReviewItem(
                id=item.id,
                chapter_slug=item.chapter_slug,
                priority=item.priority,
                reason=item.reason,
                due_date=item.due_date,
                interval_days=item.interval_days,
            )
            for item in items
        ],
        total_count=len(items),
        high_priority_count=high_priority_count,
    )


async def _generate_weak_area_reviews(
    session: AsyncSession,
    user_id: str,
    today: date,
) -> None:
    """Identify weak areas (chapters with <70% average score)."""
    # Get chapters with average score < 70%
    result = await session.execute(
        select(
            QuizAttempt.chapter_id,
            text("AVG(score_pct) as avg_score"),
            text("MAX(score_pct) as max_score"),
        )
        .join(Chapter, QuizAttempt.chapter_id == Chapter.id)
        .where(QuizAttempt.user_id == user_id)
        .group_by(QuizAttempt.chapter_id)
        .having(text("AVG(score_pct) < 70"))
    )
    weak_chapters = result.all()

    for chapter_id, avg_score, max_score in weak_chapters:
        # Check if review already exists
        result = await session.execute(
            select(ReviewReminder).where(
                ReviewReminder.user_id == user_id,
                ReviewReminder.chapter_slug == str(chapter_id),
                not ReviewReminder.completed,
            )
        )
        existing = result.scalar_one_or_none()

        if not existing:
            # Get chapter slug
            result = await session.execute(
                select(ChapterAlias.slug).where(ChapterAlias.chapter_id == chapter_id).limit(1)
            )
            slug_row = result.one_or_none()
            if not slug_row:
                continue

            review = ReviewReminder(
                user_id=user_id,
                chapter_slug=slug_row[0],
                priority="high",
                reason="weak_area",
                interval_days=1,
                due_date=today,
            )
            session.add(review)

    await session.commit()


async def mark_review_complete(
    session: AsyncSession,
    user_id: str,
    review_id: int,
    request: ReviewCompleteRequest,
) -> ReviewCompleteResponse:
    """Mark a review item as complete and schedule next review.

    Uses FSRS-style interval calculation:
    - Score >= 80%: Double interval (max 90 days)
    - Score < 80%: Reset to 1 day
    """
    # Get review item
    result = await session.execute(
        select(ReviewReminder).where(
            ReviewReminder.id == review_id,
            ReviewReminder.user_id == user_id,
            not ReviewReminder.completed,
        )
    )
    review = result.scalar_one_or_none()

    if not review:
        raise ValueError("Review not found")

    # Calculate next interval
    if request.score_pct >= 80:
        new_interval = min(review.interval_days * 2, 90)
    else:
        new_interval = 1

    # Mark as completed
    review.completed = True
    review.completed_at = datetime.now(UTC)

    # Create next review
    next_due_date = date.today() + timedelta(days=new_interval)
    next_review = ReviewReminder(
        user_id=user_id,
        chapter_slug=review.chapter_slug,
        priority="medium" if new_interval > 7 else "high",
        reason="spaced_repetition",
        interval_days=new_interval,
        due_date=next_due_date,
    )
    session.add(next_review)

    await session.commit()

    message = ""
    if request.score_pct >= 80:
        message = f"Great job! Your next review is in {new_interval} days."
    else:
        message = "Keep practicing! We'll review this again soon."

    return ReviewCompleteResponse(
        interval_days=new_interval,
        next_due_date=next_due_date,
        message=message,
    )


async def calculate_next_review(
    current_interval: int,
    score_pct: int,
) -> int:
    """Calculate the next review interval using FSRS-style logic.

    Args:
        current_interval: Current interval in days
        score_pct: Quiz score percentage (0-100)

    Returns:
        New interval in days
    """
    if score_pct >= 80:
        # Double interval, max 90 days
        return min(current_interval * 2, 90)
    else:
        # Reset to 1 day for poor performance
        return 1
