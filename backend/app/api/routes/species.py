from fastapi import APIRouter, HTTPException, status
from typing import List

from app.models.biological_models import SpeciesResponse
from app.services.species_service import SpeciesService

router = APIRouter(prefix="/api/species", tags=["species"])
service = SpeciesService()


@router.get("/", response_model=SpeciesResponse)
async def get_species():
    """Get all species."""
    return service.get_all_species()


@router.get("/{species_id}", response_model=SpeciesResponse)
async def get_species_by_id(species_id: str):
    """Get species by ID."""
    return service.get_species_by_id(species_id)