from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List

# Create router
router = APIRouter(
    prefix="/api/phylo",
    tags=["phylo"],
    responses={404: {"description": "Not found"}}
)

@router.get("/status")
async def get_phylo_status() -> Dict[str, Any]:
    """Check phylogenetic analysis status"""
    return {
        "success": True,
        "status": "available",
        "message": "Phylogenetic analysis service is running"
    } 