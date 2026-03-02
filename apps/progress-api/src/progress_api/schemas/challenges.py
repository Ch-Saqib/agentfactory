"""Daily Challenges request/response schemas."""

from datetime import date, datetime

from pydantic import BaseModel, Field


class ChallengeProgress(BaseModel):
    """Progress tracking for a challenge."""

    current: int = Field(description="Current progress value")
    target: int = Field(description="Target value to complete")
    unit: str = Field(default="items", description="Unit label (e.g., 'quizzes', 'lessons')")


class ChallengeResponse(BaseModel):
    """Today's challenge response."""

    id: int
    challenge_date: date
    challenge_type: str
    title: str
    description: str
    config: dict
    xp_bonus: int
    progress: ChallengeProgress
    completed: bool
    started_at: datetime | None = None


class ChallengeHistoryItem(BaseModel):
    """Single challenge in history."""

    id: int
    challenge_date: date
    title: str
    completed: bool
    xp_awarded: int
    completed_at: datetime | None = None


class ChallengeHistoryResponse(BaseModel):
    """Past 7 days of challenges."""

    challenges: list[ChallengeHistoryItem]


class ChallengeProgressUpdate(BaseModel):
    """Update challenge progress request."""

    progress_delta: int = Field(
        description="Amount to add to current progress (e.g., completed 1 more quiz)"
    )


class ChallengeCompleteResponse(BaseModel):
    """Response when challenge is completed."""

    xp_earned: int
    total_xp: int
    new_badges: list[dict] = Field(default_factory=list)
    streak: dict[str, int]
