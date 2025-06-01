from functools import wraps
import time
import logging
from prometheus_client import Counter, Histogram, start_http_server
from typing import Callable, Any

# Configure logging
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('request_count', 'Total request count', ['endpoint'])
REQUEST_LATENCY = Histogram('request_latency_seconds', 'Request latency', ['endpoint'])
ERROR_COUNT = Counter('error_count', 'Total error count', ['endpoint', 'error_type'])

def start_metrics_server(port: int = 9090):
    """Start Prometheus metrics server"""
    try:
        start_http_server(port)
        logger.info(f"Metrics server started on port {port}")
    except Exception as e:
        logger.error(f"Failed to start metrics server: {e}")

def monitor_performance(threshold_ms: float = 50.0):
    """Decorator to monitor endpoint performance"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            endpoint = func.__name__
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                
                # Record metrics
                duration = time.time() - start_time
                REQUEST_COUNT.labels(endpoint=endpoint).inc()
                REQUEST_LATENCY.labels(endpoint=endpoint).observe(duration)
                
                # Log slow requests
                duration_ms = duration * 1000
                if duration_ms > threshold_ms:
                    logger.warning(
                        f"Slow request detected: {endpoint} took {duration_ms:.2f}ms "
                        f"(threshold: {threshold_ms}ms)"
                    )
                
                return result
                
            except Exception as e:
                # Record error metrics
                ERROR_COUNT.labels(
                    endpoint=endpoint,
                    error_type=type(e).__name__
                ).inc()
                raise
                
        return wrapper
    return decorator

class PerformanceMonitor:
    """Performance monitoring context manager"""
    
    def __init__(self, operation_name: str, threshold_ms: float = 50.0):
        self.operation_name = operation_name
        self.threshold_ms = threshold_ms
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        duration_ms = duration * 1000
        
        # Record metrics
        REQUEST_COUNT.labels(endpoint=self.operation_name).inc()
        REQUEST_LATENCY.labels(endpoint=self.operation_name).observe(duration)
        
        # Log performance data
        if duration_ms > self.threshold_ms:
            logger.warning(
                f"Slow operation detected: {self.operation_name} took {duration_ms:.2f}ms "
                f"(threshold: {self.threshold_ms}ms)"
            )
        else:
            logger.debug(
                f"Operation completed: {self.operation_name} took {duration_ms:.2f}ms"
            )
            
        if exc_type:
            ERROR_COUNT.labels(
                endpoint=self.operation_name,
                error_type=exc_type.__name__
            ).inc()

def track_memory_usage(func: Callable) -> Callable:
    """Decorator to track memory usage"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        import psutil
        process = psutil.Process()
        
        # Memory usage before
        mem_before = process.memory_info().rss / 1024 / 1024  # MB
        
        try:
            result = func(*args, **kwargs)
            
            # Memory usage after
            mem_after = process.memory_info().rss / 1024 / 1024  # MB
            mem_diff = mem_after - mem_before
            
            logger.info(
                f"Memory usage for {func.__name__}: "
                f"Before={mem_before:.1f}MB, "
                f"After={mem_after:.1f}MB, "
                f"Diff={mem_diff:+.1f}MB"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            raise
            
    return wrapper 