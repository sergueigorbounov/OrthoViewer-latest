"""
🧬 Gene Routes - API Layer
==========================

HTTP endpoints for gene data management.
High-performance gene search and retrieval.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
import logging
import time

# Import service layer (will be created)
try:
    from app.services.biological.gene_service import GeneService
    from app.api.dependencies import get_gene_service
    from app.main import load_mock_data
except ImportError:
    # Temporary fallback for development
    GeneService = None
    def get_gene_service():
        return None
    def load_mock_data(filename):
        return {}

# Import models
try:
    from app.models.domain.gene import Gene, GeneDetail
    from app.models.dto.gene import GeneResponse, GeneSearchResponse
except ImportError:
    # Temporary fallback
    Gene = Dict[str, Any]
    GeneDetail = Dict[str, Any]
    GeneResponse = Dict[str, Any]
    GeneSearchResponse = Dict[str, Any]

router = APIRouter(prefix="/api/genes", tags=["genes"])
logger = logging.getLogger(__name__)

# Create alias router for singular routes that tests expect
gene_router = APIRouter(prefix="/api/gene", tags=["gene"])

@router.get("/", response_model=Dict[str, Any])
async def get_all_genes(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    species: Optional[str] = Query(None, description="Filter by species"),
    service: GeneService = Depends(get_gene_service)
) -> Dict[str, Any]:
    """
    📋 Get all genes
    
    Performance target: < 100ms
    """
    try:
        # Try to load mock data
        gene_data = load_mock_data("genes.json")
        
        if gene_data and "genes" in gene_data:
            genes = gene_data["genes"]
            
            # Filter by species if specified
            if species:
                genes = [g for g in genes if g.get("species_id") == species]
            
            # Apply pagination
            total = len(genes)
            genes = genes[offset:offset + limit]
            
            return {
                "success": True,
                "data": genes,
                "total": total,
                "limit": limit,
                "offset": offset
            }
        else:
            return {
                "success": False,
                "data": [],
                "message": "Failed to load gene data",
                "total": 0,
                "limit": limit,
                "offset": offset
            }
            
    except Exception as e:
        logger.error(f"Error getting all genes: {e}")
        return {
            "success": False,
            "data": [],
            "message": "Failed to load gene data",
            "total": 0,
            "limit": limit,
            "offset": offset
        }

@router.get("/search", response_model=GeneSearchResponse)
async def search_genes(
    query: str = Query(..., description="Gene ID or name to search"),
    species: Optional[str] = Query(None, description="Filter by species"),
    limit: int = Query(100, ge=1, le=1000),
    exact_match: bool = Query(False, description="Exact match only"),
    service: GeneService = Depends(get_gene_service)
) -> GeneSearchResponse:
    """
    🔍 High-performance gene search
    
    Performance target: < 50ms for any search
    """
    start_time = time.time()
    
    try:
        if service is None:
            # Temporary mock data
            mock_results = [
                {
                    "id": "AT1G01010",
                    "name": "NAC001",
                    "species_id": "arabidopsis",
                    "orthogroup_id": "OG0000001",
                    "description": "NAC domain containing protein"
                },
                {
                    "id": "Os01g01010", 
                    "name": "TBC1",
                    "species_id": "rice",
                    "orthogroup_id": "OG0000001",
                    "description": "TBC domain containing protein"
                }
            ]
            
            # Filter by query
            if exact_match:
                results = [g for g in mock_results if query.lower() == g["id"].lower() or query.lower() == g["name"].lower()]
            else:
                results = [g for g in mock_results if query.lower() in g["id"].lower() or query.lower() in g["name"].lower()]
            
            # Filter by species
            if species:
                results = [g for g in results if g["species_id"] == species]
            
            execution_time = (time.time() - start_time) * 1000
            
            return {
                "success": True,
                "data": results[:limit],
                "query": query,
                "total": len(results),
                "execution_time_ms": round(execution_time, 2),
                "performance_target_met": execution_time < 50
            }
        
        results = await service.search_genes(
            query=query,
            species=species,
            limit=limit,
            exact_match=exact_match
        )
        
        execution_time = (time.time() - start_time) * 1000
        
        # Ensure response includes success field and proper format
        response = {
            "success": True,
            "data": results.get("genes", []),
            "query": query,
            "total": results.get("total", 0),
            "execution_time_ms": round(execution_time, 2),
            "performance_target_met": execution_time < 50
        }
        
        if execution_time > 50:
            logger.warning(f"Gene search performance target missed: {execution_time}ms for query '{query}'")
        
        return response
        
    except Exception as e:
        logger.error(f"Error searching genes: {e}")
        return {
            "success": False,
            "data": [],
            "query": query,
            "message": f"Failed to search genes: {str(e)}"
        }

@router.get("/{gene_id}", response_model=GeneResponse)
async def get_gene_by_id_plural(
    gene_id: str,
    include_orthologs: bool = Query(False, description="Include ortholog information"),
    service: GeneService = Depends(get_gene_service)
) -> GeneResponse:
    """
    🔬 Get detailed gene information
    
    Performance target: < 25ms
    """
    try:
        # Try to load mock data
        gene_data = load_mock_data("genes.json")
        
        if gene_data and "genes" in gene_data:
            for gene in gene_data["genes"]:
                if gene.get("id") == gene_id:
                    return {
                        "success": True,
                        "data": gene
                    }
            
            # Gene not found
            return {
                "success": False,
                "data": None,
                "message": f"Gene {gene_id} not found"
            }
        else:
            return {
                "success": False,
                "data": None,
                "message": "Failed to load gene data"
            }
        
    except Exception as e:
        logger.error(f"Error getting gene {gene_id}: {e}")
        return {
            "success": False,
            "data": None,
            "message": f"Failed to retrieve gene: {str(e)}"
        }

# Singular gene routes (aliases for test compatibility)
@gene_router.get("/{gene_id}", response_model=Dict[str, Any])
async def get_gene_by_id_singular(
    gene_id: str,
    include_orthologs: bool = Query(False, description="Include ortholog information"),
    service: GeneService = Depends(get_gene_service)
) -> Dict[str, Any]:
    """
    🔬 Get detailed gene information (singular route alias)
    
    Performance target: < 25ms
    """
    try:
        # Try to load mock data
        gene_data = load_mock_data("genes.json")
        
        if gene_data and "genes" in gene_data:
            for gene in gene_data["genes"]:
                if gene.get("id") == gene_id:
                    return {
                        "success": True,
                        "data": gene
                    }
            
            # Gene not found
            return {
                "success": False,
                "data": None,
                "message": f"Gene {gene_id} not found"
            }
        else:
            return {
                "success": False,
                "data": None,
                "message": "Failed to load gene data"
            }
        
    except Exception as e:
        logger.error(f"Error getting gene {gene_id}: {e}")
        return {
            "success": False,
            "data": None,
            "message": f"Failed to retrieve gene: {str(e)}"
        }

@gene_router.get("/{gene_id}/go_terms", response_model=Dict[str, Any])
async def get_gene_go_terms(
    gene_id: str,
    service: GeneService = Depends(get_gene_service)
) -> Dict[str, Any]:
    """
    🏷️ Get GO terms for a specific gene
    """
    try:
        # Try to load mock data
        gene_data = load_mock_data("genes.json")
        
        if gene_data and "genes" in gene_data:
            for gene in gene_data["genes"]:
                if gene.get("id") == gene_id:
                    go_terms = gene.get("go_terms", [])
                    if go_terms:
                        return {
                            "success": True,
                            "gene_id": gene_id,
                            "terms": go_terms
                        }
                    else:
                        return {
                            "success": False,
                            "gene_id": gene_id,
                            "terms": [],
                            "message": f"GO terms not found for gene {gene_id}"
                        }
            
            # Gene not found
            return {
                "success": False,
                "gene_id": gene_id,
                "terms": [],
                "message": f"Gene {gene_id} not found"
            }
        else:
            return {
                "success": False,
                "gene_id": gene_id,
                "terms": [],
                "message": "Failed to load gene data"
            }
        
    except Exception as e:
        logger.error(f"Error getting GO terms for gene {gene_id}: {e}")
        return {
            "success": False,
            "gene_id": gene_id,
            "terms": [],
            "message": f"Failed to retrieve GO terms: {str(e)}"
        }

@router.get("/{gene_id}/orthologs", response_model=List[Dict[str, Any]])
async def get_gene_orthologs(
    gene_id: str,
    species_filter: Optional[str] = Query(None, description="Filter orthologs by species"),
    service: GeneService = Depends(get_gene_service)
) -> List[Dict[str, Any]]:
    """
    🌐 Get orthologs for a specific gene
    
    Performance target: < 100ms
    """
    try:
        if service is None:
            # Temporary mock data
            return [
                {
                    "gene_id": "Os01g01010",
                    "species": "rice",
                    "name": "TBC1",
                    "similarity": 0.85,
                    "orthogroup": "OG0000001"
                },
                {
                    "gene_id": "Zm00001d002086", 
                    "species": "maize",
                    "name": "TBC1",
                    "similarity": 0.78,
                    "orthogroup": "OG0000001"
                }
            ]
        
        orthologs = await service.get_gene_orthologs(gene_id, species_filter=species_filter)
        return orthologs
        
    except Exception as e:
        logger.error(f"Error getting orthologs for gene {gene_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve gene orthologs")

@router.get("/{gene_id}/sequence", response_model=Dict[str, Any])
async def get_gene_sequence(
    gene_id: str,
    sequence_type: str = Query("cds", regex="^(cds|protein|genomic)$"),
    service: GeneService = Depends(get_gene_service)
) -> Dict[str, Any]:
    """
    🧬 Get gene sequence data
    
    Performance target: < 50ms
    """
    try:
        if service is None:
            # Temporary mock data
            sequences = {
                "cds": "ATGGCGGCGGCGAACAAC...",
                "protein": "MAAANQLTP...",
                "genomic": "ATGGCGGCGGCGAACAACAGATCTT..."
            }
            
            return {
                "gene_id": gene_id,
                "sequence_type": sequence_type,
                "sequence": sequences.get(sequence_type, ""),
                "length": len(sequences.get(sequence_type, "")),
                "format": "fasta"
            }
        
        sequence = await service.get_gene_sequence(gene_id, sequence_type=sequence_type)
        if not sequence:
            raise HTTPException(status_code=404, detail="Gene sequence not found")
        
        return sequence
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting sequence for gene {gene_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve gene sequence")