from typing import Any, Optional
import aioredis
import json
from app.core.config import get_settings

settings = get_settings()

# Initialize Redis connection
redis = aioredis.from_url(
    settings.REDIS_URL or "redis://localhost",
    encoding="utf-8",
    decode_responses=True
)

async def get_cache(key: str) -> Optional[Any]:
    """Get data from cache"""
    try:
        data = await redis.get(key)
        return json.loads(data) if data else None
    except Exception as e:
        print(f"Cache get error: {str(e)}")
        return None

async def set_cache(key: str, value: Any, expire: int = 300) -> bool:
    """Set data in cache with expiration in seconds"""
    try:
        await redis.set(
            key,
            json.dumps(value),
            ex=expire
        )
        return True
    except Exception as e:
        print(f"Cache set error: {str(e)}")
        return False

async def delete_cache(key: str) -> bool:
    """Delete data from cache"""
    try:
        await redis.delete(key)
        return True
    except Exception as e:
        print(f"Cache delete error: {str(e)}")
        return False

async def clear_cache() -> bool:
    """Clear all cache"""
    try:
        await redis.flushall()
        return True
    except Exception as e:
        print(f"Cache clear error: {str(e)}")
        return False 