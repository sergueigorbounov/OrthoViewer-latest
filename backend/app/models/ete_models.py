from typing import List, Optional
from pydantic import BaseModel

class ETESearchResponse(BaseModel):
    success: bool
    query: str
    search_type: str
    results: List[ETESearchResult]
    total_results: int
    has_more: bool = False
    tree_image_url: Optional[str] = None
    error: Optional[str] = None
    message: Optional[str] = None
    
    # Orthologue-specific fields
    total_orthologues: Optional[int] = None
    orthogroup_id: Optional[str] = None
    species_with_orthologues: Optional[int] = None 