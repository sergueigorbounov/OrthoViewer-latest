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
except ImportError:
    # Temporary fallback for development
    SpeciesService = None
    def get_species_service():
        return None

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

@router.get("/", response_model=SpeciesListResponse)
async def get_all_species(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None, description="Search species by name"),
    service: SpeciesService = Depends(get_species_service)
) -> SpeciesListResponse:
    """
    🌍 Get all species with pagination and search
    
    Performance target: < 10ms for cached results
    """
    try:
        if service is None:
            # Temporary mock data
            return {
                "species": [
                    {"id": "arabidopsis", "name": "Arabidopsis thaliana", "type": "model_plant"},
                    {"id": "rice", "name": "Oryza sativa", "type": "crop_plant"}
                ],
                "total": 2,
                "limit": limit,
                "offset": offset
            }
        
        species_list = await service.get_species_list(
            limit=limit, 
            offset=offset, 
            search=search
        )
        return species_list
        
    except Exception as e:
        logger.error(f"Error getting species list: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve species")

@router.get("/{species_id}", response_model=SpeciesResponse)
async def get_species_by_id(
    species_id: str,
    include_stats: bool = Query(False, description="Include statistical data"),
    service: SpeciesService = Depends(get_species_service)
) -> SpeciesResponse:
    """
    🔍 Get specific species by ID
    
    Performance target: < 10ms
    """
    try:
        if service is None:
            # Temporary mock data
            if species_id == "arabidopsis":
                return {
                    "id": "arabidopsis",
                    "name": "Arabidopsis thaliana",
                    "type": "model_plant",
                    "gene_count": 27416,
                    "description": "Model organism for plant biology"
                }
            raise HTTPException(status_code=404, detail="Species not found")
        
        species = await service.get_species_by_id(species_id, include_stats=include_stats)
        if not species:
            raise HTTPException(status_code=404, detail="Species not found")
        
        return species
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting species {species_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve species")

@router.get("/{species_id}/stats", response_model=SpeciesStats)
async def get_species_statistics(
    species_id: str,
    service: SpeciesService = Depends(get_species_service)
) -> SpeciesStats:
    """
    📊 Get detailed statistics for a species
    
    Performance target: < 100ms
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
    🧬 Get genes for a specific species
    
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