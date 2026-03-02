"""Achievement Roadmap endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.auth import CurrentUser, get_current_user
from ..core.database import get_session
from ..schemas.roadmap import RoadmapResponse, RoadmapSyncResponse
from ..services.roadmap import get_roadmap_for_user, sync_roadmap_progress

router = APIRouter()


@router.get("/roadmap", response_model=RoadmapResponse)
async def get_roadmap_endpoint(
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> RoadmapResponse:
    """Get the user's achievement roadmap.

    Returns all nodes and edges for visual rendering in ReactFlow.
    Nodes are marked with their unlock status based on user's progress.
    """
    return await get_roadmap_for_user(session, user.id)


@router.post("/roadmap/sync", response_model=RoadmapSyncResponse)
async def sync_roadmap_endpoint(
    user: CurrentUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> RoadmapSyncResponse:
    """Sync roadmap progress and auto-unlock qualified nodes.

    Automatically unlocks nodes based on:
    - User's current XP (for XP-gated content)
    - Completed activities (quizzes, lessons)
    - Parent node unlock status

    Returns list of newly unlocked node IDs for UI updates.
    """
    return await sync_roadmap_progress(session, user.id)
