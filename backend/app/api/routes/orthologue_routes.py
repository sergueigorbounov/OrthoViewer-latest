from fastapi import APIRouter, HTTPException, Path, Query
from typing import Dict, Any

from app.models.phylo import (
    OrthologueSearchRequest, OrthologueSearchResponse,
    ETESearchRequest, ETESearchResponse
)
from app.services.orthologue_service import OrthologueService
from app.services.ete_tree_service import ETETreeService
from app.data_access.species_repository import SpeciesRepository

# Create router
router = APIRouter(
    prefix="/api/orthologue",
    tags=["orthologue"],
    responses={404: {"description": "Not found"}},
)

# Create services
orthologue_service = OrthologueService()
ete_tree_service = ETETreeService()
species_repository = SpeciesRepository()

@router.post("/search", response_model=OrthologueSearchResponse)
async def search_orthologues(request: OrthologueSearchRequest):
    """Search for orthologues of a given gene."""
    return await orthologue_service.search_orthologues(request)

@router.post("/ete-search", response_model=ETESearchResponse)
async def ete_tree_search(request: ETESearchRequest):
    """Advanced tree-based search using ETE toolkit."""
    return await ete_tree_service.ete_search(request)

@router.get("/tree", response_model=Dict[str, Any])
async def get_orthologue_tree():
    """Get the phylogenetic tree of species in Newick format."""
    try:
        species_tree = species_repository.load_species_tree()
        return {
            "success": True,
            "newick": species_tree
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to load species tree: {str(e)}"
        }

@router.get("/ete-status")
async def get_ete_status():
    """Check ETE3 toolkit availability and status."""
    return ete_tree_service.get_ete_status()

# Debug endpoint to check species mapping (remove after testing)
@router.get("/debug/species-mapping")
async def debug_species_mapping_endpoint():
    """Debug endpoint to check species mapping issues."""
    try:
        from app.data_access.orthogroups_repository import OrthogroupsRepository
        import pandas as pd
        
        # Create repositories
        orthogroups_repo = OrthogroupsRepository()
        
        # Load orthogroups data
        ortho_df = orthogroups_repo.load_orthogroups_data()
        species_columns = ortho_df.columns[1:].tolist()
        
        # Load mapping data from species repository
        species_mapping = species_repository.load_species_mapping()
        mapping_codes = set(species_mapping.get('id_to_full', {}).keys())
        
        ortho_codes = set(species_columns)
        missing_in_mapping = ortho_codes - mapping_codes
        found_in_both = ortho_codes & mapping_codes
        
        # Sample mappings for found codes
        sample_mappings = {}
        for code in list(found_in_both)[:10]:
            full_name = species_mapping['id_to_full'].get(code, "Unknown")
            sample_mappings[code] = full_name
        
        return {
            "success": True,
            "total_ortho_species": len(ortho_codes),
            "total_mapping_entries": len(mapping_codes),
            "missing_in_mapping": {
                "count": len(missing_in_mapping),
                "examples": list(missing_in_mapping)[:20]  # First 20 examples
            },
            "successfully_mapped": {
                "count": len(found_in_both),
                "examples": sample_mappings
            },
            "ortho_file_columns_sample": species_columns[:10],
            "ete_available": ete_tree_service.is_ete_available()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }