from typing import List, Optional
from app.models.biological_models import Species
from .mock_repository import MockRepository


class SpeciesRepository(MockRepository[Species]):
    """Repository for accessing species data."""
    
    def __init__(self):
        """Initialize the species repository."""
        super().__init__(
            model_class=Species,
            data_filename="species.json",
            id_field="id"
        )
        self.data_key = "species"
    
    def get_species_by_name(self, name: str) -> Optional[Species]:
        """Get a species by name.
        
        Args:
            name: Name of the species
            
        Returns:
            Species if found, None otherwise
        """
        all_species = self.get_all()
        for species in all_species:
            if species.name.lower() == name.lower():
                return species
        return None