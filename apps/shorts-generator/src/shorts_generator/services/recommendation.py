"""Recommendation service for shorts.

Implements collaborative filtering and content-based filtering
for personalized short video recommendations.
"""

import logging
from collections import defaultdict
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from shorts_generator.models import ShortVideo, ShortView, ShortLike

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """Engine for generating personalized short video recommendations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def recommend_for_user(
        self,
        user_id: Optional[str],
        options: dict = None,
    ) -> list[ShortVideo]:
        """Get personalized recommendations for a user.

        Args:
            user_id: User ID (None for anonymous)
            options: Recommendation options
                - limit: Number of recommendations (default 10)
                - current_lesson_path: User's current lesson
                - exclude_watched: Don't include watched videos
                - weaker_areas: List of parts/chapters to prioritize

        Returns:
            List of recommended ShortVideo objects

        Raises:
            ValueError: If options are invalid
        """
        if options is None:
            options = {}

        limit = options.get("limit", 10)
        current_lesson = options.get("current_lesson_path")
        exclude_watched = options.get("exclude_watched", True)
        weaker_areas = options.get("weaker_areas", [])

        # If anonymous, use trending/popular recommendations
        if user_id is None or user_id == "anonymous":
            return await self._get_trending_recommendations(limit)

        # Get user's viewing history
        viewed_video_ids = await self._get_viewed_video_ids(user_id)

        # Get liked video IDs
        liked_video_ids = await self._get_liked_video_ids(user_id)

        # Build recommendation scores
        scores = defaultdict(float)

        # Collaborative filtering: users who liked what you liked
        if liked_video_ids:
            collab_scores = await self._collaborative_filtering(
                user_id, liked_video_ids
            )
            for video_id, score in collab_scores.items():
                scores[video_id] += score * 0.4  # 40% weight

        # Content-based filtering: similar to what you watched
        if viewed_video_ids:
            content_scores = await self._content_based_filtering(
                user_id, viewed_video_ids
            )
            for video_id, score in content_scores.items():
                scores[video_id] += score * 0.3  # 30% weight

        # Current lesson context: suggest related content
        if current_lesson:
            context_scores = await self._contextual_recommendations(current_lesson)
            for video_id, score in context_scores.items():
                scores[video_id] += score * 0.2  # 20% weight

        # Weaker areas: prioritize content from struggling parts
        if weaker_areas:
            area_scores = await self._weaker_area_recommendations(weaker_areas)
            for video_id, score in area_scores.items():
                scores[video_id] += score * 0.1  # 10% weight

        # Filter out already watched videos if requested
        if exclude_watched:
            for video_id in viewed_video_ids:
                scores.pop(video_id, None)

        # Sort by score and return top N
        sorted_videos = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_video_ids = [vid for vid, _ in sorted_videos[:limit]]

        # Fetch full video objects
        if not top_video_ids:
            return await self._get_trending_recommendations(limit)

        result = await self.session.execute(
            select(ShortVideo).where(ShortVideo.id.in_(top_video_ids))
        )
        videos = result.scalars().all()

        # Sort by recommendation score
        video_dict = {v.id: v for v in videos}
        ordered_videos = []
        for vid in top_video_ids:
            if vid in video_dict:
                ordered_videos.append(video_dict[vid])

        return ordered_videos

    async def _get_viewed_video_ids(self, user_id: str) -> set[str]:
        """Get set of video IDs viewed by user."""
        result = await self.session.execute(
            select(ShortView.video_id).where(ShortView.user_id == user_id)
        )
        return {str(row[0]) for row in result.all()}

    async def _get_liked_video_ids(self, user_id: str) -> set[str]:
        """Get set of video IDs liked by user."""
        result = await self.session.execute(
            select(ShortLike.video_id).where(ShortLike.user_id == user_id)
        )
        return {str(row[0]) for row in result.all()}

    async def _collaborative_filtering(
        self, user_id: str, liked_video_ids: set[str]
    ) -> dict[str, float]:
        """Collaborative filtering: find videos liked by similar users.

        Users are similar if they liked the same videos.
        """
        # Find other users who liked the same videos
        result = await self.session.execute(
            select(ShortLike.user_id, ShortLike.video_id)
            .where(ShortLike.video_id.in_(liked_video_ids))
            .where(ShortLike.user_id != user_id)
        )

        # Group videos by similar users
        user_videos = defaultdict(set)
        for row in result.all():
            similar_user_id, video_id = str(row[0]), str(row[1])
            user_videos[similar_user_id].add(video_id)

        # Find videos liked by similar users
        similar_video_ids = set()
        for videos in user_videos.values():
            similar_video_ids.update(videos)

        # Score videos by number of similar users who liked them
        scores = defaultdict(int)
        for similar_user_id, their_videos in user_videos.items():
            for vid in their_videos:
                if vid not in liked_video_ids:
                    scores[vid] += 1

        return {vid: score / len(user_videos) for vid, score in scores.items()}

    async def _content_based_filtering(
        self, user_id: str, viewed_video_ids: set[str]
    ) -> dict[str, float]:
        """Content-based filtering: recommend similar videos.

        Similarity based on:
        - Same part (01-09)
        - Same chapter
        - Keywords in title
        """
        if not viewed_video_ids:
            return {}

        # Get the viewed videos to analyze
        result = await self.session.execute(
            select(ShortVideo).where(ShortVideo.id.in_(viewed_video_ids))
        )
        viewed_videos = result.scalars().all()

        # Extract parts and chapters from viewed videos
        parts_chapters = []
        for video in viewed_videos:
            path_parts = video.lesson_path.split("/")
            if len(path_parts) >= 2:
                parts_chapters.append((path_parts[0], path_parts[1]))

        # Find videos from same parts/chapters
        scores = defaultdict(float)
        for video in viewed_videos:
            path_parts = video.lesson_path.split("/")
            if len(path_parts) < 2:
                continue

            part, chapter = path_parts[0], path_parts[1]

            # Find videos from same part
            result = await self.session.execute(
                select(ShortVideo)
                .where(ShortVideo.lesson_path.like(f"{part}/%"))
                .where(ShortVideo.id.notin_(viewed_video_ids))
            )
            similar_videos = result.scalars().all()

            for sv in similar_videos:
                sv_part = sv.lesson_path.split("/")[0]
                sv_chapter = sv.lesson_path.split("/")[1] if len(sv.lesson_path.split("/")) > 1 else ""

                # Same part = base score
                score = 0.5

                # Same chapter = higher score
                if sv_chapter == chapter:
                    score += 0.3

                # Bonus for same lesson series
                if sv.lesson_path.split("/")[2:] == video.lesson_path.split("/")[2:]:
                    score += 0.2

                scores[str(sv.id)] += score

        return scores

    async def _contextual_recommendations(
        self, current_lesson_path: str
    ) -> dict[str, float]:
        """Recommend videos based on current lesson context.

        Suggests:
        - Previous lessons in same chapter (review)
        - Next lessons in same chapter (preview)
        - Related lessons in same part
        """
        scores = defaultdict(float)

        path_parts = current_lesson_path.split("/")
        if len(path_parts) < 2:
            return scores

        part, chapter = path_parts[0], path_parts[1]

        # Find videos from same chapter
        result = await self.session.execute(
            select(ShortVideo).where(
                ShortVideo.lesson_path.like(f"{part}/{chapter}/%")
            )
        )
        chapter_videos = result.scalars().all()

        for video in chapter_videos:
            # Same chapter gets base score
            scores[str(video.id)] += 0.5

            # Bonus for being nearby in sequence
            # (would require lesson ordering data)

        return scores

    async def _weaker_area_recommendations(
        self, weaker_areas: list[str]
    ) -> dict[str, float]:
        """Prioritize content from weaker areas.

        weaker_areas can contain:
        - Part numbers (e.g., "04-Coding-for-Problem-Solving")
        - Chapter paths (e.g., "04-Coding-for-Problem-Solving/01-skill-building")
        """
        scores = defaultdict(float)

        for area in weaker_areas:
            # Find videos from this area
            result = await self.session.execute(
                select(ShortVideo).where(ShortVideo.lesson_path.like(f"{area}%"))
            )
            area_videos = result.scalars().all()

            for video in area_videos:
                scores[str(video.id)] += 1.0

        return scores

    async def _get_trending_recommendations(self, limit: int) -> list[ShortVideo]:
        """Get trending videos for anonymous users.

        Trending = most viewed in last 7 days.
        """
        # This would require created_at timestamps on views
        # For now, return most viewed overall

        result = await self.session.execute(
            select(ShortVideo)
            .join(ShortView, ShortView.video_id == ShortVideo.id)
            .group_by(ShortVideo.id)
            .order_by(func.count(ShortView.id).desc())
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_continue_watching(
        self, user_id: str, limit: int = 5
    ) -> list[ShortVideo]:
        """Get videos user started but didn't complete.

        Args:
            user_id: User ID
            limit: Maximum number of results

        Returns:
            List of partially watched videos
        """
        # Get views with completion < 80%
        result = await self.session.execute(
            select(ShortView)
            .where(ShortView.user_id == user_id)
            .where(ShortView.completed == False)
            .order_by(ShortView.created_at.desc())
            .limit(limit * 2)  # Get more, we'll deduplicate
        )

        views = result.scalars().all()

        # Deduplicate by video (keep most recent)
        seen_videos = set()
        unique_views = []
        for view in views:
            if view.video_id not in seen_videos:
                seen_videos.add(view.video_id)
                unique_views.append(view)
                if len(unique_views) >= limit:
                    break

        # Fetch full video objects
        video_ids = [str(v.video_id) for v in unique_views]
        if not video_ids:
            return []

        result = await self.session.execute(
            select(ShortVideo).where(ShortVideo.id.in_(video_ids))
        )
        videos = result.scalars().all()

        # Order by most recently viewed
        video_dict = {str(v.id): v for v in videos}
        ordered_videos = []
        for vid in video_ids:
            if vid in video_dict:
                ordered_videos.append(video_dict[vid])

        return ordered_videos
