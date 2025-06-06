from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List

from app.models.phylo import (
    OrthologueSearchRequest, OrthologueSearchResponse,
    ETESearchRequest, ETESearchResponse
)
from app.services.orthologue_service import OrthologueService
from app.services.ete_tree_service import get_ete_tree_service
from app.core.monitoring import monitor_performance, track_memory_usage

# Create router
router = APIRouter(
    prefix="/api/orthologue",
    tags=["orthologue"],
    responses={404: {"description": "Not found"}}
)

# Global service instances to prevent race conditions
orthologue_service = OrthologueService()
ete_tree_service = get_ete_tree_service()  # Use global singleton

@router.post("/search", response_model=OrthologueSearchResponse)
@monitor_performance(threshold_ms=500.0)  # Increased threshold for gene searches
@track_memory_usage
async def search_orthologues(request: OrthologueSearchRequest):
    """Search for orthologues of a given gene"""
    try:
        return await orthologue_service.search_orthologues(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching orthologues: {str(e)}")

@router.post("/ete/search", response_model=ETESearchResponse)
@monitor_performance(threshold_ms=200.0)  # Optimized threshold for fast searches
@track_memory_usage
async def search_orthologues_ete(request: ETESearchRequest):
    """Search for orthologues using optimized ETE toolkit"""
    try:
        # Call the new unified search method
        return await ete_tree_service.search(
            query=request.query,
            search_type=request.search_type, 
            max_results=request.max_results,
            include_tree_image=request.include_tree_image
        )
    except Exception as e:
        return ETESearchResponse(
            success=False,
            query=request.query,
            search_type=request.search_type,
            results=[],
            total_results=0,
            error=f"Error in ETE search: {str(e)}",
            has_more=False,
            tree_image_url=None
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
@monitor_performance(threshold_ms=50.0)
@track_memory_usage
async def get_ete_status():
    """Get ETE toolkit availability status and performance metrics"""
    try:
        status = ete_tree_service.get_ete_status()
        return status
    except Exception as e:
        return {"error": f"Error getting ETE status: {str(e)}"}

@router.get("/ete-status")
@monitor_performance(threshold_ms=50.0)
@track_memory_usage
async def get_ete_status_legacy():
    """Legacy ETE status endpoint for frontend compatibility"""
    try:
        status = ete_tree_service.get_ete_status()
        return status
    except Exception as e:
        return {"error": f"Error getting ETE status: {str(e)}"}

@router.get("/cache/stats")
@monitor_performance(threshold_ms=10.0)
@track_memory_usage
async def get_cache_stats():
    """Get cache performance statistics"""
    try:
        # Get stats from both services
        ete_stats = {
            "ete_available": ete_tree_service.is_ete_available(),
            "tree_loaded": ete_tree_service._tree is not None,
            "indices_built": ete_tree_service._indices_built,
            "total_genes": len(ete_tree_service._gene_to_species_index),
            "total_species": len(ete_tree_service._species_to_genes_index)
        }
        
        ortho_stats = ete_tree_service.orthogroups_repo.get_cache_stats()
        
        return {
            "ete_service": ete_stats,
            "orthogroups_repository": ortho_stats,
            "performance_optimizations": {
                "gene_index_enabled": True,
                "species_cache_enabled": True,
                "tree_cache_enabled": True,
                "lru_cache_enabled": True
            }
        }
    except Exception as e:
        return {"error": f"Error getting cache stats: {str(e)}"}

@router.post("/cache/warm")
@monitor_performance(threshold_ms=5000.0)  # Cache warming can take time
@track_memory_usage
async def warm_cache():
    """Warm up caches for better performance"""
    try:
        # Only warm up the gene indices, skip tree loading for now
        await ete_tree_service._build_gene_indices()
        
        # Get orthogroups repository stats (which builds indices)
        cache_stats = ete_tree_service.orthogroups_repo.get_cache_stats()
        
        return {
            "success": True,
            "message": "Cache warmed successfully (gene indices only)",
            "cache_stats": cache_stats
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error warming cache: {str(e)}"
        }

# Debug endpoint to check species mapping (remove after testing)
@router.get("/debug/species-mapping")
async def debug_species_mapping_endpoint():
    """Debug endpoint to check species mapping issues."""
    try:
        from app.data_access.orthogroups_repository import OrthogroupsRepository
        from app.data_access.species_repository import SpeciesRepository
        import pandas as pd
        
        # Create repositories
        orthogroups_repo = OrthogroupsRepository()
        species_repository = SpeciesRepository()
        
        # Load orthogroups data (returns tuple: df, pagination)
        ortho_df, _ = await orthogroups_repo.load_orthogroups_data()
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