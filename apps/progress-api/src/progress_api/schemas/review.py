"""Smart Review request/response schemas."""

from datetime import date

from pydantic import BaseModel, Field


class ReviewItem(BaseModel):
    """A single item in the review queue."""

    id: int
    chapter_slug: str
    priority: str  # 'high', 'medium', 'low'
    reason: str  # 'weak_area', 'spaced_repetition', 'prerequisite'
    due_date: date
    interval_days: int


class ReviewQueueResponse(BaseModel):
    """Response for GET /review/queue."""

    items: list[ReviewItem]
    total_count: int
    high_priority_count: int


class ReviewCompleteRequest(BaseModel):
    """Mark a review item as complete."""

    score_pct: int = Field(description="Quiz score for this review (0-100)")


class ReviewCompleteResponse(BaseModel):
    """Response after completing a review."""

    interval_days: int  # New interval for next review
    next_due_date: date
    message: str
