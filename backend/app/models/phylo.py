from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from enum import Enum

# =============================================================================
# BASIC PHYLOGENETIC MODELS
# =============================================================================

class PhyloNodeData(BaseModel):
    """Base model for phylogenetic node data"""
    id: Optional[str] = None
    name: Optional[str] = None
    branch_length: Optional[float] = Field(None, alias="length")
    support: Optional[float] = None
    children: Optional[List['PhyloNodeData']] = None
    
    class Config:
        populate_by_name = True

class TreeData(BaseModel):
    """Model for tree data"""
    newick: str
    outgroup: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class NodeMutation(BaseModel):
    """Model for node mutations"""
    node_id: str
    mutation_type: str  # "SNP", "indel", "substitution"
    position: int
    ancestral: str
    derived: str
    annotation: Optional[str] = None

# =============================================================================
# ORTHOLOGUE SEARCH MODELS
# =============================================================================

class OrthologueSearchRequest(BaseModel):
    """Request model for orthologue search"""
    gene_id: str

class OrthologueData(BaseModel):
    """Model for orthologue data"""
    gene_id: str
    species_name: str
    species_id: str
    orthogroup_id: str
    sequence: Optional[str] = None

class OrthoSpeciesCount(BaseModel):
    """Model for species count in orthologue results"""
    species_name: str
    species_id: str
    count: int

class OrthologueSearchResponse(BaseModel):
    """Response model for orthologue search"""
    success: bool
    gene_id: str
    orthogroup_id: Optional[str] = None
    orthologues: List[OrthologueData] = []
    counts_by_species: List[OrthoSpeciesCount] = []
    newick_tree: Optional[str] = None
    message: Optional[str] = None

# =============================================================================
# ETE SEARCH MODELS
# =============================================================================

class ETESearchRequest(BaseModel):
    """Request model for ETE toolkit search"""
    search_type: str  # "gene", "species", "clade", "common_ancestor"
    query: str
    max_results: Optional[int] = 50
    include_tree_image: Optional[bool] = False

class ETESearchResult(BaseModel):
    """Result model for ETE toolkit search"""
    node_name: str
    node_type: str  # "leaf", "internal"
    distance_to_root: float
    support_value: Optional[float] = None
    species_count: Optional[int] = None
    gene_count: Optional[int] = None
    clade_members: List[str] = []
    
class ETESearchResponse(BaseModel):
    """Response model for ETE toolkit search"""
    success: bool
    query: str
    search_type: str
    results: List[ETESearchResult]
    total_results: int
    tree_image: Optional[str] = None  # Base64 encoded image
    message: Optional[str] = None

# =============================================================================
# VISUALIZATION MODELS
# =============================================================================

class VisualizationRequest(BaseModel):
    """Request model for tree visualization"""
    newick: str
    format: str = "png"  # "png", "svg", "pdf"
    width: int = 800
    height: int = 600
    dpi: int = 150
    highlight_nodes: List[str] = []
    color_by_support: bool = True

class VisualizationResponse(BaseModel):
    """Response model for tree visualization"""
    success: bool
    image_data: Optional[str] = None  # Base64 encoded
    format: str
    width: int
    height: int
    message: Optional[str] = None

# =============================================================================
# ANALYSIS MODELS
# =============================================================================

class TreeStatistics(BaseModel):
    """Model for tree statistics"""
    total_nodes: int
    leaf_nodes: int
    internal_nodes: int
    tree_height: float
    is_binary: bool
    min_branch_length: Optional[float] = None
    max_branch_length: Optional[float] = None
    mean_branch_length: Optional[float] = None
    total_tree_length: Optional[float] = None
    min_support: Optional[float] = None
    max_support: Optional[float] = None
    mean_support: Optional[float] = None
    well_supported_nodes: Optional[int] = None
    leaf_names: List[str] = []

class AnalysisRequest(BaseModel):
    """Request model for tree analysis"""
    newick: str
    include_statistics: bool = True
    include_distances: bool = False
    include_clades: bool = False

class AnalysisResponse(BaseModel):
    """Response model for tree analysis"""
    success: bool
    newick: str
    statistics: Optional[TreeStatistics] = None
    message: Optional[str] = None

# =============================================================================
# PATTERN SEARCH MODELS
# =============================================================================

class PatternSearchRequest(BaseModel):
    """Request model for pattern search in trees"""
    newick: str
    pattern_type: str  # "name", "clade", "distance"
    query: str
    max_results: int = 50

class PatternResult(BaseModel):
    """Result model for pattern search"""
    node_name: Optional[str] = None
    is_leaf: bool
    distance_to_root: float
    children_count: Optional[int] = None
    clade_size: Optional[int] = None
    descendants: Optional[List[str]] = None

class PatternSearchResponse(BaseModel):
    """Response model for pattern search"""
    success: bool
    pattern_type: str
    query: str
    results: List[PatternResult]
    total_results: int
    message: Optional[str] = None

# =============================================================================
# COMPARISON MODELS
# =============================================================================

class ComparisonRequest(BaseModel):
    """Request model for tree comparison"""
    tree1: str  # Newick format
    tree2: str  # Newick format
    comparison_type: str = "topology"  # "topology", "distances", "full"

class ComparisonResponse(BaseModel):
    """Response model for tree comparison"""
    success: bool
    unique_to_tree1: List[str]
    unique_to_tree2: List[str]
    common_leaves: List[str]
    tree1_leaf_count: int
    tree2_leaf_count: int
    similarity_ratio: float
    message: Optional[str] = None

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def newick_to_dict(newick_str: str) -> Dict[str, Any]:
    """Convert Newick string to dictionary representation"""
    # This is a placeholder - the actual implementation would be in the API layer
    return {
        "id": "root",
        "name": "root",
        "children": []
    }

# =============================================================================
# UPDATE FORWARD REFERENCES
# =============================================================================

# Update forward references for recursive models
PhyloNodeData.model_rebuild()
ETESearchResult.model_rebuild()
TreeStatistics.model_rebuild()
# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def newick_to_dict(newick_str: str) -> Dict[str, Any]:
    """Convert Newick string to dictionary representation"""
    # This is a placeholder - the actual implementation would be in the API layer
    return {
        "id": "root",
        "name": "root",
        "children": []
    }

# =============================================================================
# UPDATE FORWARD REFERENCES
# =============================================================================

# Update forward references for recursive models
PhyloNodeData.model_rebuild()
ETESearchResult.model_rebuild()
