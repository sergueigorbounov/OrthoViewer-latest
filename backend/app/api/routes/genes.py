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
except ImportError:
    # Temporary fallback for development
    GeneService = None
    def get_gene_service():
        return None

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
                    "gene_id": "AT1G01010",
                    "name": "NAC001",
                    "species": "arabidopsis",
                    "length": 1688,
                    "description": "NAC domain containing protein"
                },
                {
                    "gene_id": "Os01g01010", 
                    "name": "TBC1",
                    "species": "rice",
                    "length": 2345,
                    "description": "TBC domain containing protein"
                }
            ]
            
            # Filter by query
            if exact_match:
                results = [g for g in mock_results if query.lower() == g["gene_id"].lower() or query.lower() == g["name"].lower()]
            else:
                results = [g for g in mock_results if query.lower() in g["gene_id"].lower() or query.lower() in g["name"].lower()]
            
            # Filter by species
            if species:
                results = [g for g in results if g["species"] == species]
            
            execution_time = (time.time() - start_time) * 1000
            
            return {
                "genes": results[:limit],
                "total": len(results),
                "query": query,
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
        results["execution_time_ms"] = round(execution_time, 2)
        results["performance_target_met"] = execution_time < 50
        
        if execution_time > 50:
            logger.warning(f"Gene search performance target missed: {execution_time}ms for query '{query}'")
        
        return results
        
    except Exception as e:
        logger.error(f"Error searching genes: {e}")
        raise HTTPException(status_code=500, detail="Failed to search genes")

@router.get("/{gene_id}", response_model=GeneResponse)
async def get_gene_by_id(
    gene_id: str,
    include_orthologs: bool = Query(False, description="Include ortholog information"),
    service: GeneService = Depends(get_gene_service)
) -> GeneResponse:
    """
    🔬 Get detailed gene information
    
    Performance target: < 25ms
    """
    try:
        if service is None:
            # Temporary mock data
            if gene_id == "AT1G01010":
                return {
                    "gene_id": "AT1G01010",
                    "name": "NAC001", 
                    "species": "arabidopsis",
                    "length": 1688,
                    "chromosome": "1",
                    "start": 3631,
                    "end": 5899,
                    "strand": "+",
                    "description": "NAC domain containing protein 1",
                    "orthologs": ["Os01g01010", "Zm00001d002086"] if include_orthologs else []
                }
            raise HTTPException(status_code=404, detail="Gene not found")
        
        gene = await service.get_gene_by_id(gene_id, include_orthologs=include_orthologs)
        if not gene:
            raise HTTPException(status_code=404, detail="Gene not found")
        
        return gene
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting gene {gene_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve gene")

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