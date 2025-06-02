"""
🌐 Orthogroup Routes - API Layer
===============================

HTTP endpoints for orthogroup data management.
Efficient retrieval of orthologous gene groups.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
import logging

# Import service layer (will be created)
try:
    from app.services.biological.orthogroup_service import OrthogroupService
    from app.api.dependencies import get_orthogroup_service
except ImportError:
    # Temporary fallback for development
    OrthogroupService = None
    def get_orthogroup_service():
        return None

# Import models
try:
    from app.models.domain.orthogroup import Orthogroup, OrthogroupStats
    from app.models.dto.orthogroup import OrthogroupResponse, OrthogroupListResponse
except ImportError:
    # Temporary fallback
    Orthogroup = Dict[str, Any]
    OrthogroupStats = Dict[str, Any]
    OrthogroupResponse = Dict[str, Any]
    OrthogroupListResponse = Dict[str, Any]

router = APIRouter(prefix="/api/orthogroups", tags=["orthogroups"])
logger = logging.getLogger(__name__)

@router.get("/", response_model=OrthogroupListResponse)
async def get_all_orthogroups(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    min_species: Optional[int] = Query(None, ge=2, description="Minimum number of species"),
    service: OrthogroupService = Depends(get_orthogroup_service)
) -> OrthogroupListResponse:
    """
    🌍 Get all orthogroups with filtering
    
    Performance target: < 100ms
    """
    try:
        if service is None:
            # Temporary mock data
            return {
                "orthogroups": [
                    {
                        "id": "OG0000001",
                        "species_count": 3,
                        "gene_count": 5,
                        "description": "NAC domain containing proteins"
                    },
                    {
                        "id": "OG0000002", 
                        "species_count": 2,
                        "gene_count": 3,
                        "description": "Cytochrome P450 family"
                    }
                ],
                "total": 2,
                "limit": limit,
                "offset": offset
            }
        
        orthogroups = await service.get_orthogroups_list(
            limit=limit,
            offset=offset,
            min_species=min_species
        )
        return orthogroups
        
    except Exception as e:
        logger.error(f"Error getting orthogroups: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve orthogroups")

@router.get("/{orthogroup_id}", response_model=OrthogroupResponse)
async def get_orthogroup_by_id(
    orthogroup_id: str,
    include_genes: bool = Query(True, description="Include gene details"),
    service: OrthogroupService = Depends(get_orthogroup_service)
) -> OrthogroupResponse:
    """
    🔍 Get specific orthogroup by ID
    
    Performance target: < 100ms
    """
    try:
        if service is None:
            # Temporary mock data
            if orthogroup_id == "OG0000001":
                return {
                    "id": "OG0000001",
                    "species_count": 3,
                    "gene_count": 5,
                    "description": "NAC domain containing proteins",
                    "genes": [
                        {"gene_id": "AT1G01010", "species": "arabidopsis", "name": "NAC001"},
                        {"gene_id": "Os01g01010", "species": "rice", "name": "TBC1"},
                        {"gene_id": "Zm00001d002086", "species": "maize", "name": "TBC1"}
                    ] if include_genes else []
                }
            raise HTTPException(status_code=404, detail="Orthogroup not found")
        
        orthogroup = await service.get_orthogroup_by_id(orthogroup_id, include_genes=include_genes)
        if not orthogroup:
            raise HTTPException(status_code=404, detail="Orthogroup not found")
        
        return orthogroup
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting orthogroup {orthogroup_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve orthogroup")

@router.get("/{orthogroup_id}/genes", response_model=List[Dict[str, Any]])
async def get_orthogroup_genes(
    orthogroup_id: str,
    species_filter: Optional[str] = Query(None, description="Filter by species"),
    service: OrthogroupService = Depends(get_orthogroup_service)
) -> List[Dict[str, Any]]:
    """
    🧬 Get all genes in an orthogroup
    
    Performance target: < 50ms
    """
    try:
        if service is None:
            # Temporary mock data
            genes = [
                {
                    "gene_id": "AT1G01010",
                    "species": "arabidopsis", 
                    "name": "NAC001",
                    "length": 1688,
                    "similarity_score": 1.0
                },
                {
                    "gene_id": "Os01g01010",
                    "species": "rice",
                    "name": "TBC1", 
                    "length": 2345,
                    "similarity_score": 0.85
                },
                {
                    "gene_id": "Zm00001d002086",
                    "species": "maize",
                    "name": "TBC1",
                    "length": 1987,
                    "similarity_score": 0.78
                }
            ]
            
            if species_filter:
                genes = [g for g in genes if g["species"] == species_filter]
            
            return genes
        
        genes = await service.get_orthogroup_genes(orthogroup_id, species_filter=species_filter)
        return genes
        
    except Exception as e:
        logger.error(f"Error getting genes for orthogroup {orthogroup_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve orthogroup genes")

@router.get("/{orthogroup_id}/stats", response_model=OrthogroupStats)
async def get_orthogroup_statistics(
    orthogroup_id: str,
    service: OrthogroupService = Depends(get_orthogroup_service)
) -> OrthogroupStats:
    """
    📊 Get detailed statistics for an orthogroup
    
    Performance target: < 150ms
    """
    try:
        if service is None:
            # Temporary mock data
            return {
                "orthogroup_id": orthogroup_id,
                "total_genes": 5,
                "species_count": 3,
                "avg_gene_length": 1940,
                "length_variance": 278.5,
                "conservation_score": 0.85,
                "species_distribution": {
                    "arabidopsis": 2,
                    "rice": 2, 
                    "maize": 1
                }
            }
        
        stats = await service.get_orthogroup_statistics(orthogroup_id)
        if not stats:
            raise HTTPException(status_code=404, detail="Orthogroup not found")
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting orthogroup stats {orthogroup_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve orthogroup statistics")

@router.get("/{orthogroup_id}/tree", response_model=Dict[str, Any])
async def get_orthogroup_phylogenetic_tree(
    orthogroup_id: str,
    format: str = Query("newick", regex="^(newick|json)$"),
    service: OrthogroupService = Depends(get_orthogroup_service)
) -> Dict[str, Any]:
    """
    🌳 Get phylogenetic tree for orthogroup
    
    Performance target: < 200ms
    """
    try:
        if service is None:
            # Temporary mock data
            if format == "newick":
                tree_data = "((AT1G01010:0.1,Os01g01010:0.15):0.05,Zm00001d002086:0.2);"
            else:
                tree_data = {
                    "name": "root",
                    "children": [
                        {
                            "name": "clade1",
                            "children": [
                                {"name": "AT1G01010", "length": 0.1},
                                {"name": "Os01g01010", "length": 0.15}
                            ],
                            "length": 0.05
                        },
                        {"name": "Zm00001d002086", "length": 0.2}
                    ]
                }
            
            return {
                "orthogroup_id": orthogroup_id,
                "format": format,
                "tree": tree_data,
                "gene_count": 3,
                "method": "neighbor_joining"
            }
        
        tree = await service.get_orthogroup_tree(orthogroup_id, format=format)
        if not tree:
            raise HTTPException(status_code=404, detail="Orthogroup tree not found")
        
        return tree
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting orthogroup tree {orthogroup_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve orthogroup tree")