from fastapi import APIRouter, Query, HTTPException, status
from typing import Optional

from app.models.biological_models import GeneResponse, GeneDetailResponse
from app.services.gene_search_service import GeneSearchService

router = APIRouter(prefix="/api", tags=["genes"])
service = GeneSearchService()

@router.get("/gene/{gene_id}", response_model=GeneDetailResponse)
async def get_gene_by_id(gene_id: str):
    """Get gene details by ID.
    
    Args:
        gene_id: ID of the gene to retrieve
        
    Returns:
        Gene details if found
    """
    return service.get_gene_by_id(gene_id)

@router.get("/orthogroup/{og_id}/genes", response_model=GeneResponse)
async def get_orthogroup_genes(og_id: str):
    """Get genes for a specific orthogroup.
    
    Args:
        og_id: ID of the orthogroup
        
    Returns:
        List of genes belonging to the specified orthogroup
    """
    return service.get_genes_by_orthogroup(og_id)

@router.get("/species/{species_id}/genes", response_model=GeneResponse)
async def get_species_genes(species_id: str):
    """Get genes for a specific species.
    
    Args:
        species_id: ID of the species
        
    Returns:
        List of genes belonging to the specified species
    """
    return service.get_genes_by_species(species_id)

@router.get("/genes/search")
async def search_genes(
    query: str = Query(..., description="Search query for gene name or ID"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results to return")
):
    """Search for genes by name or ID.
    
    Args:
        query: Search query string
        limit: Maximum number of results to return (default: 10, max: 100)
        
    Returns:
        List of genes matching the search query
    """
    return service.search_genes(query, limit)

@router.get("/gene/{gene_id}/go_terms")
async def get_gene_go_terms(gene_id: str):
    """Get GO terms for a specific gene.
    
    Args:
        gene_id: ID of the gene
        
    Returns:
        GO terms associated with the gene
    """
    gene_result = service.get_gene_by_id(gene_id)
    
    if not gene_result["success"]:
        return {
            "success": False,
            "message": f"GO terms for gene {gene_id} not found",
            "terms": [],
            "gene_id": gene_id
        }
    
    gene = gene_result["data"]
    go_terms = gene.get("go_terms", [])
    
    if not go_terms:
        return {
            "success": False,
            "message": f"GO terms for gene {gene_id} not found",
            "terms": [],
            "gene_id": gene_id
        }
    
    return {
        "success": True,
        "terms": go_terms,
        "gene_id": gene_id
    }