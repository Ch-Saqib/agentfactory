"""Redis cache layer for profile and onboarding data.

Cache keys:
  lp:profile:{learner_id}     TTL 30min (1800s)
  lp:onboarding:{learner_id}  TTL 10min (600s)

Invalidated on any profile mutation (update, section update, onboarding, PHM sync, delete).
"""

import json
import logging

from api_infra.core.redis_cache import get_redis

from ..config import settings

logger = logging.getLogger(__name__)


def _profile_key(learner_id: str) -> str:
    return f"{settings.redis_namespace}profile:{learner_id}"


def _onboarding_key(learner_id: str) -> str:
    return f"{settings.redis_namespace}onboarding:{learner_id}"


async def get_cached_profile(learner_id: str) -> dict | None:
    """Get cached profile JSON or None if not cached."""
    redis = get_redis()
    if not redis:
        return None
    try:
        data = await redis.get(_profile_key(learner_id))
        if data:
            return json.loads(data)
    except Exception as e:
        logger.warning("[Cache] Failed to get profile: %s", e)
    return None


async def set_cached_profile(learner_id: str, profile_json: dict) -> None:
    """Cache profile JSON with configured TTL."""
    redis = get_redis()
    if not redis:
        return
    try:
        await redis.setex(
            _profile_key(learner_id),
            settings.cache_ttl_profile,
            json.dumps(profile_json, default=str),
        )
    except Exception as e:
        logger.warning("[Cache] Failed to set profile: %s", e)


async def get_cached_onboarding(learner_id: str) -> dict | None:
    """Get cached onboarding status or None."""
    redis = get_redis()
    if not redis:
        return None
    try:
        data = await redis.get(_onboarding_key(learner_id))
        if data:
            return json.loads(data)
    except Exception as e:
        logger.warning("[Cache] Failed to get onboarding: %s", e)
    return None


async def set_cached_onboarding(learner_id: str, status_json: dict) -> None:
    """Cache onboarding status with configured TTL."""
    redis = get_redis()
    if not redis:
        return
    try:
        await redis.setex(
            _onboarding_key(learner_id),
            settings.cache_ttl_onboarding,
            json.dumps(status_json, default=str),
        )
    except Exception as e:
        logger.warning("[Cache] Failed to set onboarding: %s", e)


async def invalidate_profile_cache(learner_id: str) -> None:
    """Delete all cache keys for a learner. Called on any profile mutation."""
    redis = get_redis()
    if not redis:
        return
    try:
        await redis.delete(_profile_key(learner_id))
        await redis.delete(_onboarding_key(learner_id))
    except Exception as e:
        logger.warning("[Cache] Failed to invalidate: %s", e)
