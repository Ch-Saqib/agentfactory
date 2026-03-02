"""Models package — re-exports all models + SQLModel."""

from sqlmodel import SQLModel

from .activity import ActivityDay
from .badge import UserBadge
from .challenge import ChallengeTemplate, DailyChallenge, UserChallengeProgress
from .chapter import Chapter, ChapterAlias
from .checkpoint import CheckpointAttempt, KnowledgeCheckpoint
from .flashcard import FlashcardCompletion
from .friendship import Friendship, SharedActivity
from .lesson import LessonCompletion
from .progress import UserProgress
from .quiz import QuizAttempt
from .review import ReviewReminder
from .roadmap import RoadmapNode, UserAchievementProgress
from .user import User

__all__ = [
    "SQLModel",
    "ActivityDay",
    "Chapter",
    "ChapterAlias",
    "ChallengeTemplate",
    "CheckpointAttempt",
    "DailyChallenge",
    "FlashcardCompletion",
    "Friendship",
    "KnowledgeCheckpoint",
    "LessonCompletion",
    "QuizAttempt",
    "ReviewReminder",
    "RoadmapNode",
    "SharedActivity",
    "User",
    "UserAchievementProgress",
    "UserBadge",
    "UserChallengeProgress",
    "UserProgress",
]
