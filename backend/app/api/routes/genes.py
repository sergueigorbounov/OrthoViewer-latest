from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any

from app.models.biological_models import GeneResponse, GeneDetailResponse
from app.services.gene_service import GeneService

router = APIRouter(prefix="/api/genes", tags=["genes"])
service = GeneService()


@router.get("/", response_model=GeneResponse)
async def get_genes():
    """Get all genes."""
    return service.get_all_genes()


@router.get("/{gene_id}", response_model=GeneDetailResponse)
async def get_gene_by_id(gene_id: str):
    """Get gene by ID."""
    return service.get_gene_by_id(gene_id)


@router.get("/{gene_id}/go_terms")
async def get_gene_go_terms(gene_id: str):
    """Get GO terms for a specific gene."""
    return service.get_gene_go_terms(gene_id)