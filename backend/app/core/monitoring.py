"""
Monitoring utilities for performance tracking
"""

import time
import functools
import logging
import asyncio
from typing import Any, Callable

logger = logging.getLogger(__name__)

def monitor_performance(threshold_ms: float = 100.0):
    """Decorator to monitor function performance"""
    def decorator(func: Callable) -> Callable:
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs) -> Any:
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    execution_time = (time.time() - start_time) * 1000
                    if execution_time > threshold_ms:
                        logger.warning(f"{func.__name__} took {execution_time:.2f}ms (threshold: {threshold_ms}ms)")
                    return result
                except Exception as e:
                    execution_time = (time.time() - start_time) * 1000
                    logger.error(f"{func.__name__} failed after {execution_time:.2f}ms: {e}")
                    raise
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs) -> Any:
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    execution_time = (time.time() - start_time) * 1000
                    if execution_time > threshold_ms:
                        logger.warning(f"{func.__name__} took {execution_time:.2f}ms (threshold: {threshold_ms}ms)")
                    return result
                except Exception as e:
                    execution_time = (time.time() - start_time) * 1000
                    logger.error(f"{func.__name__} failed after {execution_time:.2f}ms: {e}")
                    raise
            return sync_wrapper
    return decorator

def track_memory_usage(func: Callable) -> Callable:
    """Decorator to track memory usage (basic implementation)"""
    if asyncio.iscoroutinefunction(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            # Basic implementation - could be enhanced with psutil for actual memory tracking
            return await func(*args, **kwargs)
        return async_wrapper
    else:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            # Basic implementation - could be enhanced with psutil for actual memory tracking
            return func(*args, **kwargs)
        return sync_wrapper 