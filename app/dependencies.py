import redis.asyncio as aioredis
from starlette.requests import HTTPConnection

from app.config import CACHE_ENABLED
from app.db.session import get_redis_client
from app.services.assistant_service import get_current_user


async def get_cache(conn: HTTPConnection) -> aioredis.Redis:
    cache = getattr(conn.app.state, "redis", None)
    if cache is None:
        cache = get_redis_client()
        conn.app.state.redis = cache
    return cache


def get_cache_setting() -> bool:
    return CACHE_ENABLED


__all__ = ["get_cache", "get_cache_setting", "get_current_user"]
