from fastapi import APIRouter, HTTPException, status
from typing import List

from app.models.biological_models import OrthoGroupResponse
from app.services.orthogroup_service import OrthoGroupService

router = APIRouter(prefix="/api/orthogroups", tags=["orthogroups"])
service = OrthoGroupService()


@router.get("/", response_model=OrthoGroupResponse)
async def get_orthogroups():
    """Get all orthogroups."""
    return service.get_all_orthogroups()


@router.get("/{og_id}", response_model=OrthoGroupResponse)
async def get_orthogroup_by_id(og_id: str):
    """Get orthogroup by ID."""
    return service.get_orthogroup_by_id(og_id)