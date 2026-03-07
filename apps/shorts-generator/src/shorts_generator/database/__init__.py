"""Database models, schemas, and repository."""

from shorts_generator.database.db_manager import DatabaseManager, database_manager

# Import models and schemas from database/models.py
from shorts_generator.database.models import (
    Base,
    GenerationJob,
    Script,
    Video,
    VideoAnalytics,
    VideoCreate,
    VideoResponse,
    TimestampMixin,
)

__all__ = [
    # SQLAlchemy Models
    "Base",
    "GenerationJob",
    "Script",    "Video",
    "VideoAnalytics",
    "TimestampMixin",
    # Pydantic Schemas
    "VideoCreate",
    "VideoResponse",
    # Database Manager
    "DatabaseManager",
    "database_manager",
]

# Note: ShortVideo is an alias for Video in database/models.py for backward compatibility
