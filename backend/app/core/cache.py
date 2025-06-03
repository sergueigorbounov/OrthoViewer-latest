"""
Basic caching utilities
"""

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Simple in-memory cache for development
_cache = {}

async def get_cache(key: str) -> Optional[Any]:
    """Get value from cache"""
    try:
        return _cache.get(key)
    except Exception as e:
        logger.error(f"Error getting from cache: {e}")
        return None

async def set_cache(key: str, value: Any, expire: int = 300) -> bool:
    """Set value in cache with expiration"""
    try:
        # Basic implementation - doesn't handle expiration for now
        _cache[key] = value
        return True
    except Exception as e:
        logger.error(f"Error setting cache: {e}")
        return False

def clear_cache():
    """Clear all cached data"""
    global _cache
    _cache = {} 