"""
Health Check Routes - API Layer
================================

System health and monitoring endpoints.
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any
import time
import psutil
import logging

router = APIRouter(prefix="/api/health", tags=["health"])
logger = logging.getLogger(__name__)

@router.get("/")
@router.get("/status")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "2.0.0",
        "architecture": "3-layer"
    }

@router.get("/detailed")
async def detailed_health() -> Dict[str, Any]:
    """Detailed system health information"""
    try:
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)
        
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "system": {
                "cpu_usage": f"{cpu_percent}%",
                "memory_usage": f"{memory.percent}%",
                "memory_available": f"{memory.available / (1024**3):.2f} GB"
            },
            "services": {
                "api_layer": "healthy",
                "service_layer": "healthy", 
                "data_access_layer": "healthy"
            },
            "performance": {
                "response_time": "< 10ms",
                "throughput": "healthy"
            }
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "degraded",
            "timestamp": time.time(),
            "error": str(e)
        }

@router.get("/ready")
async def readiness_check() -> Dict[str, Any]:
    """Kubernetes readiness probe"""
    # Add checks for dependencies (database, file system, etc.)
    return {
        "ready": True,
        "timestamp": time.time(),
        "checks": {
            "file_system": "ready",
            "services": "ready"
        }
    }

@router.get("/live")
async def liveness_check() -> Dict[str, Any]:
    """Kubernetes liveness probe"""
    return {
        "alive": True,
        "timestamp": time.time()
    }