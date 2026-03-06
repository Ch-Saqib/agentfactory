"""Database models and repositories."""

from shorts_generator.database.db_manager import DatabaseManager, database_manager
from shorts_generator.database.models import (
    GenerationJob,
    GenerationJobCreate,
    GenerationJobResponse,
    Script,
    Video,
    VideoAnalytics,
    VideoCreate,
    VideoResponse,
    TimestampMixin,
)

__all__ = [
    # Models
    "Video",
    "GenerationJob",
    "Script",
    "VideoAnalytics",
    "TimestampMixin",
    # Pydantic Schemas
    "VideoCreate",
    "VideoUpdate",
    "VideoResponse",
    "GenerationJobCreate",
    "GenerationJobResponse",
    # Database Manager
    "DatabaseManager",
    "database_manager",
]
