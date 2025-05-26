from typing import List, Optional
from app.models.biological_models import OrthoGroup
from .mock_repository import MockRepository


class OrthoGroupRepository(MockRepository[OrthoGroup]):
    """Repository for accessing orthogroup data."""
    
    def __init__(self):
        """Initialize the orthogroup repository."""
        super().__init__(
            model_class=OrthoGroup,
            data_filename="orthogroups.json",
            id_field="id"
        )
        self.data_key = "orthogroups"
    
    def get_orthogroups_by_species(self, species_id: str) -> List[OrthoGroup]:
        """Get orthogroups for a specific species.
        
        Args:
            species_id: ID of the species
            
        Returns:
            List of orthogroups containing the specified species
        """
        all_orthogroups = self.get_all()
        return [og for og in all_orthogroups if species_id in og.species]