"""Knowledge Checkpoints request/response schemas."""


from pydantic import BaseModel


class CheckpointQuestion(BaseModel):
    """A checkpoint question."""

    question: str
    options: list[str]
    correct_answer: int  # Index of correct option
    explanation: str


class CheckpointResponse(BaseModel):
    """Response for GET /checkpoint (question data)."""

    id: int
    lesson_slug: str
    position_pct: int
    question: CheckpointQuestion
    xp_bonus: int


class CheckpointAnswerRequest(BaseModel):
    """Submit an answer to a checkpoint."""

    checkpoint_id: int
    answer: int  # Index of selected option


class CheckpointAnswerResponse(BaseModel):
    """Response after submitting an answer."""

    correct: bool
    explanation: str
    correct_answer: int
    xp_awarded: int
    total_xp: int
