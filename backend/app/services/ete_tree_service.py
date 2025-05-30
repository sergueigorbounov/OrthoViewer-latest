import logging
import os
import tempfile
import base64
from typing import List, Dict, Any, Optional
from fastapi import HTTPException
from ete3 import Tree, TreeStyle, NodeStyle

from app.core.config import get_settings
from app.data_access.orthogroups_repository import OrthogroupsRepository
from app.data_access.species_repository import SpeciesRepository
from app.models.phylo import (
    ETESearchRequest, ETESearchResponse, ETESearchResult
)

# Configure logging
logger = logging.getLogger(__name__)
settings = get_settings()

# ETE3 imports
try:
    from ete3 import Tree, TreeStyle, NodeStyle
    ETE_AVAILABLE = True
except ImportError as e:
    ETE_AVAILABLE = False

class ETETreeService:
    """Service for ETE toolkit operations"""

    def __init__(self):
        """Initialize the ETE tree service"""
        self.tree_file = settings.TREE_FILE
        self._tree = None
        self.orthogroups_repo = OrthogroupsRepository()
        self.species_repo = SpeciesRepository()
    
    def is_ete_available(self) -> bool:
        """Check if ETE toolkit is available."""
        return ETE_AVAILABLE
    
    def load_ete_tree(self) -> Tree:
        """Load the ETE tree from file"""
        if self._tree is None:
            try:
                logger.info(f"Loading ETE tree from {self.tree_file}")
                self._tree = Tree(self.tree_file, format=1)
                logger.info("ETE tree loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load ETE tree: {str(e)}")
                raise
        return self._tree
    
    def search_tree_by_gene(self, gene_id: str, max_results: int = 50) -> List[ETESearchResult]:
        """Search for species containing a specific gene."""
        if not ETE_AVAILABLE:
            return []
        
        results = []
        tree = self.load_ete_tree()
        ortho_data = self.orthogroups_repo.load_orthogroups_data()
        
        # Find which species have this gene
        species_with_gene = []
        for col in ortho_data.columns[1:]:
            for _, row in ortho_data.iterrows():
                cell_value = row[col]
                if isinstance(cell_value, str) and gene_id in cell_value:
                    species_with_gene.append(col)
                    break
        
        # Find corresponding tree nodes
        for species_code in species_with_gene[:max_results]:
            for leaf in tree.get_leaves():
                if leaf.name.strip().strip('"\'') == species_code:
                    result = ETESearchResult(
                        node_name=getattr(leaf, "full_species_name", leaf.name),
                        node_type="leaf",
                        distance_to_root=leaf.get_distance(tree),
                        gene_count=getattr(leaf, "gene_count", 0),
                        species_count=1,
                        clade_members=[getattr(leaf, "full_species_name", leaf.name)]
                    )
                    results.append(result)
                    break
        
        return results
    
    def search_tree_by_species(self, species_query: str, max_results: int = 50) -> List[ETESearchResult]:
        """Search for species by name (fuzzy matching)."""
        if not ETE_AVAILABLE:
            return []
        
        results = []
        tree = self.load_ete_tree()
        query_lower = species_query.lower()
        
        for leaf in tree.get_leaves():
            leaf_name = leaf.name.strip().strip('"\'')
            full_name = getattr(leaf, "full_species_name", leaf_name)
            
            # Check if query matches species name
            if (query_lower in leaf_name.lower() or
                query_lower in full_name.lower() or
                any(query_lower in word.lower() for word in full_name.split())):
                
                result = ETESearchResult(
                    node_name=full_name,
                    node_type="leaf",
                    distance_to_root=leaf.get_distance(tree),
                    gene_count=getattr(leaf, "gene_count", 0),
                    species_count=1,
                    clade_members=[full_name]
                )
                results.append(result)
                
                if len(results) >= max_results:
                    break
        
        return results
    
    def search_tree_by_clade(self, clade_query: str, max_results: int = 50) -> List[ETESearchResult]:
        """Search for clades containing specific taxa."""
        if not ETE_AVAILABLE:
            return []
        
        results = []
        tree = self.load_ete_tree()
        query_lower = clade_query.lower()
        
        # Search internal nodes for clades
        for node in tree.traverse():
            if not node.is_leaf():
                # Get all species in this clade
                clade_species = []
                total_genes = 0
                
                for leaf in node.get_leaves():
                    full_name = getattr(leaf, "full_species_name", leaf.name)
                    clade_species.append(full_name)
                    total_genes += getattr(leaf, "gene_count", 0)
                
                # Check if this clade matches the query
                clade_string = " ".join(clade_species).lower()
                if query_lower in clade_string:
                    result = ETESearchResult(
                        node_name=f"Clade with {len(clade_species)} species",
                        node_type="internal",
                        distance_to_root=node.get_distance(tree),
                        support_value=getattr(node, "support", None),
                        species_count=len(clade_species),
                        gene_count=total_genes,
                        clade_members=clade_species[:10]  # Limit to first 10 for display
                    )
                    results.append(result)
                    
                    if len(results) >= max_results:
                        break
        
        return results
    
    def find_common_ancestor(self, species_list: List[str]) -> List[ETESearchResult]:
        """Find common ancestor of specified species."""
        if not ETE_AVAILABLE:
            return []
        
        results = []
        tree = self.load_ete_tree()
        
        # Find tree nodes for each species
        target_nodes = []
        for species in species_list:
            for leaf in tree.get_leaves():
                full_name = getattr(leaf, "full_species_name", leaf.name)
                if species.lower() in full_name.lower():
                    target_nodes.append(leaf)
                    break
        
        if len(target_nodes) >= 2:
            # Find common ancestor
            ancestor = tree.get_common_ancestor(target_nodes)
            
            # Get all species under this ancestor
            descendant_species = []
            total_genes = 0
            
            for leaf in ancestor.get_leaves():
                full_name = getattr(leaf, "full_species_name", leaf.name)
                descendant_species.append(full_name)
                total_genes += getattr(leaf, "gene_count", 0)
            
            result = ETESearchResult(
                node_name=f"Common ancestor of {', '.join(species_list)}",
                node_type="internal",
                distance_to_root=ancestor.get_distance(tree),
                support_value=getattr(ancestor, "support", None),
                species_count=len(descendant_species),
                gene_count=total_genes,
                clade_members=descendant_species
            )
            results.append(result)
        
        return results
    
    def generate_tree_image(self, highlighted_nodes: Optional[List[str]] = None) -> Optional[str]:
        """Generate tree visualization with ETE and return as base64 string."""
        if not ETE_AVAILABLE:
            return None
        
        try:
            tree = self.load_ete_tree()
            
            # Create tree style
            ts = TreeStyle()
            ts.show_leaf_name = True
            ts.mode = "c"  # Circular mode
            ts.arc_start = 0
            ts.arc_span = 360
            
            # Style nodes
            for node in tree.traverse():
                nstyle = NodeStyle()
                
                if highlighted_nodes and node.name in highlighted_nodes:
                    nstyle["bgcolor"] = "#ffcccc"
                    nstyle["size"] = 15
                elif node.is_leaf():
                    if hasattr(node, "gene_count") and node.gene_count > 0:
                        nstyle["fgcolor"] = "#4caf50"
                        nstyle["size"] = max(5, min(15, node.gene_count // 100))
                    else:
                        nstyle["fgcolor"] = "#9e9e9e"
                        nstyle["size"] = 5
                else:
                    nstyle["size"] = 3
                    
                node.set_style(nstyle)
            
            # Render to image
            with tempfile.NamedTemporaryFile(suffix=".png", delete=True) as tmp:
                tree.render(tmp.name, tree_style=ts, w=800, h=600, dpi=150)
                
                # Read image and convert to base64
                with open(tmp.name, "rb") as img_file:
                    img_data = img_file.read()
                    base64_string = base64.b64encode(img_data).decode('utf-8')
                
                return f"data:image/png;base64,{base64_string}"
        
        except Exception as e:
            logger.error(f"Failed to generate tree image: {str(e)}")
            return None
    
    async def ete_search(self, request: ETESearchRequest) -> ETESearchResponse:
        """Perform tree-based search using ETE toolkit."""
        if not ETE_AVAILABLE:
            return ETESearchResponse(
                success=False,
                query=request.query,
                search_type=request.search_type,
                results=[],
                total_results=0,
                message="ETE3 toolkit not available. Please install: conda install -c etetoolkit ete3"
            )
        
        try:
            logger.info(f"ETE search: {request.search_type} for '{request.query}'")
            results = []
            
            if request.search_type == "gene":
                results = self.search_tree_by_gene(request.query, request.max_results)
            elif request.search_type == "species":
                results = self.search_tree_by_species(request.query, request.max_results)
            elif request.search_type == "clade":
                results = self.search_tree_by_clade(request.query, request.max_results)
            elif request.search_type == "common_ancestor":
                # Parse comma-separated species list
                species_list = [s.strip() for s in request.query.split(",")]
                results = self.find_common_ancestor(species_list)
            else:
                return ETESearchResponse(
                    success=False,
                    query=request.query,
                    search_type=request.search_type,
                    results=[],
                    total_results=0,
                    message=f"Unknown search type: {request.search_type}"
                )
            
            # Generate tree image if requested
            tree_image = None
            if request.include_tree_image and results:
                highlighted_nodes = [r.node_name for r in results[:5]]  # Highlight first 5 results
                tree_image = self.generate_tree_image(highlighted_nodes)
            
            return ETESearchResponse(
                success=True,
                query=request.query,
                search_type=request.search_type,
                results=results,
                total_results=len(results),
                tree_image=tree_image,
                message=f"Found {len(results)} results"
            )
        
        except Exception as e:
            logger.error(f"ETE search error: {str(e)}", exc_info=True)
            return ETESearchResponse(
                success=False,
                query=request.query,
                search_type=request.search_type,
                results=[],
                total_results=0,
                message=f"Search failed: {str(e)}"
            )
    
    def get_ete_status(self) -> Dict[str, Any]:
        """Check ETE toolkit status and availability"""
        try:
            tree = self.load_ete_tree()
            return {
                "success": True,
                "available": True,
                "tree_loaded": True,
                "num_leaves": len(tree.get_leaves()),
                "tree_format": tree.get_tree_root().get_tree_root().write(format=1)[:100] + "..."
            }
        except Exception as e:
            return {
                "success": False,
                "available": False,
                "error": str(e)
            }

    def render_tree(self, tree_data: str, selected_species: Optional[str] = None) -> str:
        """Render a tree with ETE toolkit"""
        try:
            # Create a tree from the Newick data
            tree = Tree(tree_data, format=1)

            # Create a TreeStyle
            ts = TreeStyle()
            ts.show_leaf_name = True
            ts.show_branch_length = True
            ts.show_branch_support = True
            ts.scale = 120  # pixels per branch length unit
            ts.branch_vertical_margin = 10  # pixels between adjacent branches

            # Create styles for different node types
            default_style = NodeStyle()
            default_style["size"] = 5
            default_style["fgcolor"] = "#000000"
            default_style["shape"] = "circle"

            selected_style = NodeStyle()
            selected_style["size"] = 8
            selected_style["fgcolor"] = "#1976d2"
            selected_style["shape"] = "circle"

            # Apply styles to nodes
            for node in tree.traverse():
                if selected_species and node.name == selected_species:
                    node.set_style(selected_style)
                else:
                    node.set_style(default_style)

            # Render the tree to a temporary PNG file
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tree.render(tmp.name, tree_style=ts)
                # Read the file and convert to base64
                with open(tmp.name, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode()
                os.unlink(tmp.name)
                return encoded_string

        except Exception as e:
            logger.error(f"Error rendering tree: {str(e)}")
            raise

    def analyze_tree(self, tree_data: str) -> Dict[str, Any]:
        """Analyze a tree using ETE toolkit"""
        try:
            tree = Tree(tree_data, format=1)
            return {
                "num_leaves": len(tree.get_leaves()),
                "total_nodes": len(tree.get_descendants()) + 1,
                "tree_height": tree.get_farthest_leaf()[1],
                "is_binary": tree.is_binary(),
                "leaf_names": [leaf.name for leaf in tree.get_leaves()][:10]  # First 10 leaves
            }
        except Exception as e:
            logger.error(f"Error analyzing tree: {str(e)}")
            raise