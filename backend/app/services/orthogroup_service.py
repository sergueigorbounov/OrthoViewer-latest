from typing import List, Optional, Dict
from fastapi import HTTPException, status

from app.models.biological_models import OrthoGroup, OrthoGroupResponse
from app.data_access.orthogroup_repository import OrthoGroupRepository


class OrthoGroupService:
    """Service for managing orthogroup data."""
    
    def __init__(self):
        """Initialize the orthogroup service."""
        self.repository = OrthoGroupRepository()
    
    def get_all_orthogroups(self) -> OrthoGroupResponse:
        """Get all orthogroups.
        
        Returns:
            Response containing all orthogroups
        """
        try:
            orthogroup_list = self.repository.get_all()
            return OrthoGroupResponse(
                success=True,
                data=orthogroup_list
            )
        except Exception as e:
            return OrthoGroupResponse(
                success=False,
                message=f"Failed to load orthogroup data: {str(e)}",
                data=[]
            )
    
    def get_orthogroup_by_id(self, og_id: str) -> OrthoGroupResponse:
        """Get an orthogroup by ID.
        
        Args:
            og_id: ID of the orthogroup
            
        Returns:
            Response containing the orthogroup if found
        """
        try:
            orthogroup = self.repository.get_by_id(og_id)
            
            if not orthogroup:
                return OrthoGroupResponse(
                    success=False,
                    message=f"Orthogroup with ID {og_id} not found",
                    data=[]
                )
            
            return OrthoGroupResponse(
                success=True,
                data=[orthogroup]
            )
        except Exception as e:
            return OrthoGroupResponse(
                success=False,
                message=f"Failed to load orthogroup data: {str(e)}",
                data=[]
            )
    
    def get_orthogroups_by_species(self, species_id: str) -> OrthoGroupResponse:
        """Get orthogroups for a specific species.
        
        Args:
            species_id: ID of the species
            
        Returns:
            Response containing orthogroups for the specified species
        """
        try:
            orthogroups = self.repository.get_orthogroups_by_species(species_id)
            
            return OrthoGroupResponse(
                success=True,
                data=orthogroups,
                species_id=species_id
            )
        except Exception as e:
            return OrthoGroupResponse(
                success=False,
                message=f"Failed to load orthogroup data: {str(e)}",
                data=[],
                species_id=species_id
            )