from uuid import UUID

import redis.asyncio as aioredis

from app.db.models import Users


async def clear_cache_for_get_messages(cache: aioredis.Redis, chat_guid: UUID):
    pattern_for_get_messages = f"messages*_{chat_guid}_*"
    keys_found = cache.scan_iter(match=pattern_for_get_messages)
    async for key in keys_found:
        await cache.delete(key)


async def clear_cache_for_get_direct_chats(cache: aioredis.Redis, user: Users):
    pattern_for_get_direct_chats = f"direct_chats_{user.guid}"
    keys_found = cache.scan_iter(match=pattern_for_get_direct_chats)
    async for key in keys_found:
        await cache.delete(key)


async def clear_cache_for_all_users(cache: aioredis.Redis):
    keys_found = cache.scan_iter(match="*all_users")
    async for key in keys_found:
        await cache.delete(key)
