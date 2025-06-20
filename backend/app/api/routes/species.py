"""
🌱 Species Routes - API Layer
============================

HTTP endpoints for species data management.
Thin controllers that delegate to service layer.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
import logging

# Import service layer (will be created)
try:
    from app.services.biological.species_service import SpeciesService
    from app.api.dependencies import get_species_service
    from app.main import load_mock_data
except ImportError:
    # Temporary fallback for development
    SpeciesService = None
    def get_species_service():
        return None
    def load_mock_data(filename):
        return {}

# Import models
try:
    from app.models.domain.species import Species, SpeciesStats
    from app.models.dto.species import SpeciesResponse, SpeciesListResponse
except ImportError:
    # Temporary fallback
    Species = Dict[str, Any]
    SpeciesStats = Dict[str, Any]
    SpeciesResponse = Dict[str, Any]
    SpeciesListResponse = Dict[str, Any]

router = APIRouter(prefix="/api/species", tags=["species"])
logger = logging.getLogger(__name__)

@router.get("/", response_model=Dict[str, Any])
async def get_all_species(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None, description="Search species by name"),
    service: SpeciesService = Depends(get_species_service)
) -> Dict[str, Any]:
    """
    🌍 Get all species with pagination and search
    
    Performance target: < 10ms for cached results
    """
    try:
        # Try to load mock data
        species_data = load_mock_data("species.json")
        
        if species_data and "species" in species_data:
            species = species_data["species"]
            
            # Apply search filter if specified
            if search:
                species = [s for s in species if search.lower() in s.get("name", "").lower()]
            
            # Apply pagination
            total = len(species)
            species = species[offset:offset + limit]
            
            return {
                "success": True,
                "data": species,
                "total": total,
                "limit": limit,
                "offset": offset
            }
        else:
            return {
                "success": False,
                "data": [],
                "message": "Failed to load species data",
                "total": 0,
                "limit": limit,
                "offset": offset
            }
        
    except Exception as e:
        logger.error(f"Error getting species list: {e}")
        return {
            "success": False,
            "data": [],
            "message": "Failed to load species data",
            "total": 0,
            "limit": limit,
            "offset": offset
        }

@router.get("/{species_id}", response_model=Dict[str, Any])
async def get_species_by_id(
    species_id: str,
    include_stats: bool = Query(False, description="Include statistical data"),
    service: SpeciesService = Depends(get_species_service)
) -> Dict[str, Any]:
    """
    Get specific species by ID
    
    Performance target: < 25ms
    """
    try:
        # Try to load mock data
        species_data = load_mock_data("species.json")
        
        if species_data and "species" in species_data:
            # Find the species
            found_species = [s for s in species_data["species"] if s.get("id") == species_id]
            
            if found_species:
                return {
                    "success": True,
                    "data": found_species
                }
            else:
                return {
                    "success": False,
                    "data": [],
                    "message": f"Species {species_id} not found"
                }
        else:
            return {
                "success": False,
                "data": [],
                "message": "Failed to load species data"
            }
        
    except Exception as e:
        logger.error(f"Error getting species {species_id}: {e}")
        return {
            "success": False,
            "data": [],
            "message": f"Failed to retrieve species: {str(e)}"
        }

@router.get("/{species_id}/stats", response_model=SpeciesStats)
async def get_species_statistics(
    species_id: str,
    service: SpeciesService = Depends(get_species_service)
) -> SpeciesStats:
    """
    Get detailed statistics for a species
    
    Performance target: < 50ms
    """
    try:
        if service is None:
            # Temporary mock data
            return {
                "species_id": species_id,
                "gene_count": 27416,
                "orthogroup_count": 18780,
                "unique_genes": 8636,
                "avg_gene_length": 1245,
                "gc_content": 36.5
            }
        
        stats = await service.get_species_statistics(species_id)
        if not stats:
            raise HTTPException(status_code=404, detail="Species not found")
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting species stats {species_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve species statistics")

@router.get("/{species_id}/genes", response_model=List[Dict[str, Any]])
async def get_species_genes(
    species_id: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None, description="Search genes by name"),
    service: SpeciesService = Depends(get_species_service)
) -> List[Dict[str, Any]]:
    """
    Get genes for a specific species
    
    Performance target: < 50ms
    """
    try:
        if service is None:
            # Temporary mock data
            return [
                {"gene_id": "AT1G01010", "name": "NAC001", "length": 1688},
                {"gene_id": "AT1G01020", "name": "ARV1", "length": 1276}
            ]
        
        genes = await service.get_species_genes(
            species_id=species_id,
            limit=limit,
            offset=offset,
            search=search
        )
        return genes
        
    except Exception as e:
        logger.error(f"Error getting genes for species {species_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve species genes")

@router.get("/{species_id}/orthogroups", response_model=Dict[str, Any])
async def get_species_orthogroups(
    species_id: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    service: SpeciesService = Depends(get_species_service)
) -> Dict[str, Any]:
    """
    Get orthogroups for a specific species
    
    Performance target: < 100ms
    """
    try:
        # Try to load mock data
        orthogroup_data = load_mock_data("orthogroups.json")
        
        if orthogroup_data and "orthogroups" in orthogroup_data:
            # Filter orthogroups that include the specified species
            orthogroups = [og for og in orthogroup_data["orthogroups"] 
                          if species_id in og.get("species", [])]
            
            # Apply pagination
            total = len(orthogroups)
            orthogroups = orthogroups[offset:offset + limit]
            
            return {
                "success": True,
                "data": orthogroups,
                "species_id": species_id,
                "total": total,
                "limit": limit,
                "offset": offset
            }
        else:
            return {
                "success": False,
                "data": [],
                "species_id": species_id,
                "message": "Failed to load orthogroup data",
                "total": 0,
                "limit": limit,
                "offset": offset
            }
        
    except Exception as e:
        logger.error(f"Error getting orthogroups for species {species_id}: {e}")
        return {
            "success": False,
            "data": [],
            "species_id": species_id,
            "message": f"Failed to retrieve species orthogroups: {str(e)}",
            "total": 0,
            "limit": limit,
            "offset": offset
        }