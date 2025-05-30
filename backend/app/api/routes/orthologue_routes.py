from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List

from app.models.phylo import (
    OrthologueSearchRequest, OrthologueSearchResponse,
    ETESearchRequest, ETESearchResponse
)
from app.services.orthologue_service import OrthologueService
from app.services.ete_tree_service import ETETreeService

# Create router
router = APIRouter(
    prefix="/api/orthologue",
    tags=["orthologue"],
    responses={404: {"description": "Not found"}}
)

# Initialize services
orthologue_service = OrthologueService()
ete_tree_service = ETETreeService()

@router.post("/search", response_model=OrthologueSearchResponse)
async def search_orthologues(request: OrthologueSearchRequest):
    """Search for orthologues of a given gene"""
    return await orthologue_service.search_orthologues(request)

@router.post("/ete/search", response_model=ETESearchResponse)
async def search_orthologues_ete(request: ETESearchRequest):
    """Search for orthologues using ETE toolkit"""
    try:
        # Call the ETE tree service to perform the search
        return await ete_tree_service.ete_search(request)
    except Exception as e:
        return ETESearchResponse(
            success=False,
            query=request.query,
            search_type=request.search_type,
            results=[],
            total_results=0,
            message=f"Error in ETE search: {str(e)}"
        )

@router.get("/ete/tree/{orthogroup_id}")
async def get_orthologue_ete_tree(orthogroup_id: str) -> Dict[str, Any]:
    """Get the ETE-enhanced phylogenetic tree for an orthogroup"""
    try:
        # Get the basic tree data
        tree_data = await orthologue_service.get_orthogroup_tree(orthogroup_id)
        
        if not tree_data.get("success"):
            return tree_data
        
        # Enhance with ETE analysis
        newick_tree = tree_data.get("newick")
        if newick_tree:
            analysis = ete_tree_service.analyze_tree(newick_tree)
            tree_image = ete_tree_service.render_tree(newick_tree)
            
            return {
                "success": True,
                "orthogroup_id": orthogroup_id,
                "newick": newick_tree,
                "analysis": analysis,
                "tree_image": tree_image
            }
        
        return tree_data

    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to get ETE tree: {str(e)}"
        }

@router.get("/ete/status")
async def get_ete_status() -> Dict[str, Any]:
    """Check ETE toolkit availability and status"""
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