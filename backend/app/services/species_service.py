from typing import List, Optional, Dict
from fastapi import HTTPException, status

from app.models.biological_models import Species, SpeciesResponse
from app.data_access.species_repository import SpeciesRepository


class SpeciesService:
    """Service for managing species data."""
    
    def __init__(self):
        """Initialize the species service."""
        self.repository = SpeciesRepository()
    
    def get_all_species(self) -> SpeciesResponse:
        """Get all species.
        
        Returns:
            Response containing all species
        """
        try:
            species_list = self.repository.get_all()
            return SpeciesResponse(
                success=True,
                data=species_list
            )
        except Exception as e:
            return SpeciesResponse(
                success=False,
                message=f"Failed to load species data: {str(e)}",
                data=[]
            )
    
    def get_species_by_id(self, species_id: str) -> SpeciesResponse:
        """Get a species by ID.
        
        Args:
            species_id: ID of the species
            
        Returns:
            Response containing the species if found
        """
        try:
            species = self.repository.get_by_id(species_id)
            
            if not species:
                return SpeciesResponse(
                    success=False,
                    message=f"Species with ID {species_id} not found",
                    data=[]
                )
            
            return SpeciesResponse(
                success=True,
                data=[species]
            )
        except Exception as e:
            return SpeciesResponse(
                success=False,
                message=f"Failed to load species data: {str(e)}",
                data=[]
            )