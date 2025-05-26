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

@router.post("/ete-search", response_model=ETESearchResponse)
async def ete_tree_search(request: ETESearchRequest):
    """Advanced tree-based search using ETE toolkit"""
    try:
        if request.search_type == "gene":
            results = ete_tree_service.search_tree_by_gene(request.query, request.max_results)
        elif request.search_type == "species":
            results = ete_tree_service.search_tree_by_species(request.query, request.max_results)
        elif request.search_type == "clade":
            results = ete_tree_service.search_tree_by_clade(request.query, request.max_results)
        elif request.search_type == "common_ancestor":
            # Parse comma-separated species list
            species_list = [s.strip() for s in request.query.split(",")]
            results = ete_tree_service.find_common_ancestor(species_list)
        else:
            return ETESearchResponse(
                success=False,
                query=request.query,
                search_type=request.search_type,
                results=[],
                total_results=0,
                message=f"Unknown search type: {request.search_type}"
            )
        
        # Generate tree image if requested
        tree_image = None
        if request.include_tree_image and results:
            highlighted_nodes = [r.node_name for r in results[:5]]  # Highlight first 5 results
            tree_image = ete_tree_service.generate_tree_image(highlighted_nodes)
        
        return ETESearchResponse(
            success=True,
            query=request.query,
            search_type=request.search_type,
            results=results,
            total_results=len(results),
            tree_image=tree_image,
            message=f"Found {len(results)} results"
        )
        
    except Exception as e:
        return ETESearchResponse(
            success=False,
            query=request.query,
            search_type=request.search_type,
            results=[],
            total_results=0,
            message=f"Search failed: {str(e)}"
        )

@router.get("/tree")
async def get_orthologue_tree() -> Dict[str, Any]:
    """Get the phylogenetic species tree in Newick format"""
    try:
        species_tree = ete_tree_service.load_ete_tree()
        return {
            "success": True,
            "newick": species_tree.write()
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to load species tree: {str(e)}"
        }

@router.get("/ete-status")
async def get_ete_status() -> Dict[str, Any]:
    """Check ETE3 toolkit availability and status"""
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