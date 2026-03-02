"""Achievement Roadmap request/response schemas."""

from datetime import datetime

from pydantic import BaseModel


class RoadmapNodeData(BaseModel):
    """Additional data for a roadmap node."""

    chapter_slug: str | None = None
    lesson_count: int | None = None
    quiz_count: int | None = None
    completion_pct: int | None = None


class RoadmapNodeResponse(BaseModel):
    """A single node in the roadmap."""

    id: str
    parent_id: str | None = None
    node_type: str  # 'part', 'chapter', 'milestone'
    title: str
    description: str | None = None
    position_x: int
    position_y: int
    config: dict
    required_xp: int
    icon: str | None = None
    unlocked: bool = False
    unlocked_at: datetime | None = None
    locked: bool = False  # Whether this node is locked (not yet unlockable)


class RoadmapEdge(BaseModel):
    """A connection between two roadmap nodes."""

    id: str
    source: str  # Source node ID
    target: str  # Target node ID
    animated: bool = False


class RoadmapResponse(BaseModel):
    """Full roadmap with nodes and edges."""

    nodes: list[RoadmapNodeResponse]
    edges: list[RoadmapEdge]
    user_xp: int
    unlocked_count: int
    total_count: int


class RoadmapSyncResponse(BaseModel):
    """Response after syncing roadmap progress."""

    new_unlocks: list[str]  # Node IDs that were newly unlocked
    total_unlocked: int
    total_nodes: int
