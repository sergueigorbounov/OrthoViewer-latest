from fastapi import APIRouter, HTTPException, status

from app.models.biological_models import DashboardResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])
service = DashboardService()


@router.get("/stats", response_model=DashboardResponse)
async def get_dashboard_stats():
    """Get dashboard statistics."""
    return service.get_dashboard_stats()