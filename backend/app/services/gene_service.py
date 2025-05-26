from typing import List, Optional, Dict
from fastapi import HTTPException, status

from app.models.biological_models import Gene, GeneResponse, GeneDetailResponse
from app.data_access.gene_repository import GeneRepository
from app.data_access.orthogroup_repository import OrthoGroupRepository


class GeneService:
    """Service for managing gene data."""
    
    def __init__(self):
        """Initialize the gene service."""
        self.repository = GeneRepository()
        self.orthogroup_repository = OrthoGroupRepository()
    
    def get_all_genes(self) -> GeneResponse:
        """Get all genes.
        
        Returns:
            Response containing all genes
        """
        try:
            gene_list = self.repository.get_all()
            return GeneResponse(
                success=True,
                data=gene_list
            )
        except Exception as e:
            return GeneResponse(
                success=False,
                message=f"Failed to load gene data: {str(e)}",
                data=[]
            )
    
    def get_gene_by_id(self, gene_id: str) -> GeneDetailResponse:
        """Get a gene by ID.
        
        Args:
            gene_id: ID of the gene
            
        Returns:
            Response containing the gene if found
        """
        try:
            gene = self.repository.get_by_id(gene_id)
            
            if not gene:
                return GeneDetailResponse(
                    success=False,
                    message=f"Gene with ID {gene_id} not found",
                    data=None
                )
            
            return GeneDetailResponse(
                success=True,
                data=gene
            )
        except Exception as e:
            return GeneDetailResponse(
                success=False,
                message=f"Failed to load gene data: {str(e)}",
                data=None
            )
    
    def get_genes_by_orthogroup(self, og_id: str) -> GeneResponse:
        """Get genes for a specific orthogroup.
        
        Args:
            og_id: ID of the orthogroup
            
        Returns:
            Response containing genes for the specified orthogroup
        """
        try:
            # First check if the orthogroup exists
            orthogroup = self.orthogroup_repository.get_by_id(og_id)
            
            if not orthogroup:
                return GeneResponse(
                    success=False,
                    message=f"Orthogroup with ID {og_id} not found",
                    data=[],
                    orthogroup_id=og_id
                )
            
            # Get genes for the orthogroup
            genes = self.repository.get_genes_by_orthogroup(og_id)
            
            return GeneResponse(
                success=True,
                data=genes,
                orthogroup_id=og_id
            )
        except Exception as e:
            return GeneResponse(
                success=False,
                message=f"Failed to load gene data: {str(e)}",
                data=[],
                orthogroup_id=og_id
            )
    
    def get_gene_go_terms(self, gene_id: str) -> Dict:
        """Get GO terms for a specific gene.
        
        Args:
            gene_id: ID of the gene
            
        Returns:
            Response containing GO terms for the specified gene
        """
        try:
            gene = self.repository.get_by_id(gene_id)
            
            if not gene or not gene.go_terms:
                return {
                    "success": False,
                    "message": f"GO terms for gene {gene_id} not found",
                    "terms": [],
                    "gene_id": gene_id
                }
            
            return {
                "success": True,
                "terms": gene.go_terms,
                "gene_id": gene_id
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to load GO term data: {str(e)}",
                "terms": [],
                "gene_id": gene_id
            }