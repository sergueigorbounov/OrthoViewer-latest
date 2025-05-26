from typing import List, Optional
from app.models.biological_models import Gene
from .mock_repository import MockRepository


class GeneRepository(MockRepository[Gene]):
    """Repository for accessing gene data."""
    
    def __init__(self):
        """Initialize the gene repository."""
        super().__init__(
            model_class=Gene,
            data_filename="genes.json",
            id_field="id"
        )
        self.data_key = "genes"
    
    def get_genes_by_orthogroup(self, orthogroup_id: str) -> List[Gene]:
        """Get genes for a specific orthogroup.
        
        Args:
            orthogroup_id: ID of the orthogroup
            
        Returns:
            List of genes belonging to the specified orthogroup
        """
        all_genes = self.get_all()
        return [gene for gene in all_genes if gene.orthogroup_id == orthogroup_id]
    
    def get_genes_by_species(self, species_id: str) -> List[Gene]:
        """Get genes for a specific species.
        
        Args:
            species_id: ID of the species
            
        Returns:
            List of genes belonging to the specified species
        """
        all_genes = self.get_all()
        return [gene for gene in all_genes if gene.species_id == species_id]