"""Achievement Roadmap service — generates and syncs roadmap data.

This service handles:
- Roadmap structure definition
- User progress synchronization
- Node unlock logic based on XP and prerequisites
"""

import logging

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.progress import UserProgress
from ...models.roadmap import RoadmapNode, UserAchievementProgress
from ...schemas.roadmap import (
    RoadmapEdge,
    RoadmapNodeResponse,
    RoadmapResponse,
    RoadmapSyncResponse,
)

logger = logging.getLogger(__name__)


async def get_roadmap_for_user(
    session: AsyncSession,
    user_id: str,
) -> RoadmapResponse:
    """Get full roadmap with user's unlock status.

    Returns all nodes and edges for ReactFlow rendering,
    with unlock status for each node based on user's progress.
    """
    # Get user's total XP
    result = await session.execute(
        select(UserProgress).where(UserProgress.user_id == user_id)
    )
    user_progress = result.scalar_one_or_none()
    user_xp = user_progress.total_xp if user_progress else 0

    # Get all nodes
    result = await session.execute(select(RoadmapNode).order_by(RoadmapNode.position_y))
    all_nodes = result.scalars().all()

    # Get user's unlocked nodes
    result = await session.execute(
        select(UserAchievementProgress).where(UserAchievementProgress.user_id == user_id)
    )
    unlocked_node_ids = {row.node_id for row in result.all()}

    # Build node responses
    nodes = []
    for node in all_nodes:
        is_unlocked = node.id in unlocked_node_ids

        # Determine if locked (not yet unlockable)
        # A node is locked if its required_xp > user's current XP
        is_locked = node.required_xp > user_xp

        # Get unlock time
        unlocked_at = None
        if is_unlocked:
            result = await session.execute(
                select(UserAchievementProgress).where(
                    UserAchievementProgress.user_id == user_id,
                    UserAchievementProgress.node_id == node.id,
                )
            )
            progress_row = result.scalar_one_or_none()
            if progress_row:
                unlocked_at = progress_row.unlocked_at

        nodes.append(
            RoadmapNodeResponse(
                id=node.id,
                parent_id=node.parent_id,
                node_type=node.node_type,
                title=node.title,
                description=node.description,
                position_x=node.position_x,
                position_y=node.position_y,
                config=node.config,
                required_xp=node.required_xp,
                icon=node.icon,
                unlocked=is_unlocked,
                unlocked_at=unlocked_at,
                locked=is_locked,
            )
        )

    # Build edges from parent-child relationships
    edges = []
    edge_id = 0
    for node in all_nodes:
        if node.parent_id:
            edges.append(
                RoadmapEdge(
                    id=f"edge-{edge_id}",
                    source=node.parent_id,
                    target=node.id,
                    animated=False,
                )
            )
            edge_id += 1

    return RoadmapResponse(
        nodes=nodes,
        edges=edges,
        user_xp=user_xp,
        unlocked_count=len(unlocked_node_ids),
        total_count=len(all_nodes),
    )


async def sync_roadmap_progress(
    session: AsyncSession,
    user_id: str,
) -> RoadmapSyncResponse:
    """Auto-unlock nodes based on user's existing progress.

    Scans roadmap nodes and unlocks any that the user qualifies for:
    - Has sufficient XP for nodes with required_xp
    - Has completed activities related to the node

    Returns list of newly unlocked node IDs.
    """
    # Get user's XP
    result = await session.execute(
        select(UserProgress).where(UserProgress.user_id == user_id)
    )
    user_progress = result.scalar_one_or_none()
    user_xp = user_progress.total_xp if user_progress else 0

    # Get all nodes
    result = await session.execute(select(RoadmapNode))
    all_nodes = result.scalars().all()

    # Get already unlocked node IDs
    result = await session.execute(
        select(UserAchievementProgress.node_id).where(
            UserAchievementProgress.user_id == user_id
        )
    )
    unlocked_ids = {row[0] for row in result.all()}

    # Find nodes that should be unlocked
    new_unlocks = []
    for node in all_nodes:
        # Skip if already unlocked
        if node.id in unlocked_ids:
            continue

        # Check XP requirement
        should_unlock = False

        if user_xp >= node.required_xp:
            # Milestone nodes unlock automatically with XP
            if node.node_type == "milestone":
                should_unlock = True
            # Part nodes unlock if any child is unlocked
            elif node.node_type == "part":
                # Check if any chapter in this part is unlocked
                for child in node.children:
                    if child.id in unlocked_ids:
                        should_unlock = True
                        break
            # Chapter nodes unlock when XP threshold is met
            elif node.node_type == "chapter":
                should_unlock = True

        # Create unlock record
        if should_unlock:
            # Use raw SQL for idempotent insert (ON CONFLICT DO NOTHING)
            await session.execute(
                text("""
                    INSERT INTO user_achievement_progress (user_id, node_id)
                    VALUES (:user_id, :node_id)
                    ON CONFLICT (user_id, node_id) DO NOTHING
                """),
                {"user_id": user_id, "node_id": node.id},
            )
            new_unlocks.append(node.id)

    await session.commit()

    # Get updated counts
    result = await session.execute(
        select(UserAchievementProgress).where(UserAchievementProgress.user_id == user_id)
    )
    total_unlocked = len(result.all())

    return RoadmapSyncResponse(
        new_unlocks=new_unlocks,
        total_unlocked=total_unlocked,
        total_nodes=len(all_nodes),
    )
