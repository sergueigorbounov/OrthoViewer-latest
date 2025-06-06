import logging
import os
import tempfile
import base64
import asyncio
from typing import List, Dict, Any, Optional
from fastapi import HTTPException

from app.core.config import get_settings
from app.data_access.orthogroups_repository import OrthogroupsRepository
from app.data_access.species_repository import SpeciesRepository
from app.models.phylo import (
    ETESearchRequest, ETESearchResponse, ETESearchResult
)

# Configure logging
logger = logging.getLogger(__name__)
settings = get_settings()

# ETE3 imports - conditional import
try:
    from ete3 import Tree, TreeStyle, NodeStyle
    ETE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"ETE3 not available: {e}")
    ETE_AVAILABLE = False
    # Create dummy classes to prevent NameError
    class Tree:
        def __init__(self, *args, **kwargs):
            pass
        
        def get_leaves(self):
            return []
        
        def traverse(self):
            return []
        
        def get_distance(self, other):
            return 0
        
        def get_common_ancestor(self, nodes):
            return self
        
        def is_leaf(self):
            return True
        
        def render(self, *args, **kwargs):
            pass
        
        def write(self, *args, **kwargs):
            return ""
        
        def get_tree_root(self):
            return self
        
        def get_farthest_leaf(self):
            return (self, 0)
        
        def is_binary(self):
            return True
        
        def get_descendants(self):
            return []
        
        @property
        def name(self):
            return "dummy"
        
        def set_style(self, style):
            pass
    
    class TreeStyle:
        def __init__(self):
            self.show_leaf_name = True
            self.show_branch_length = True
            self.show_branch_support = True
            self.scale = 120
            self.branch_vertical_margin = 10
            self.mode = "c"
            self.arc_start = 0
            self.arc_span = 360
    
    class NodeStyle:
        def __init__(self):
            self._attrs = {}
        
        def __setitem__(self, key, value):
            self._attrs[key] = value
        
        def __getitem__(self, key):
            return self._attrs.get(key)

# Global service instance to prevent race conditions
_ete_service_instance = None

class ETETreeService:
    """Service for ETE toolkit operations"""
    
    def __init__(self):
        """Initialize the ETE tree service"""
        self.tree_file = settings.TREE_FILE
        self._tree = None
        self._indices_built = False
        self._gene_to_species_index = {}
        self._species_to_genes_index = {}
        self.orthogroups_repo = OrthogroupsRepository()
        self.species_repo = SpeciesRepository()
        self._build_lock = asyncio.Lock()  # Add async lock for thread safety

    def is_ete_available(self) -> bool:
        """Check if ETE toolkit is available."""
        return ETE_AVAILABLE

    def load_ete_tree(self) -> Optional[Tree]:
        """Load the ETE tree from file"""
        if not ETE_AVAILABLE:
            logger.warning("ETE toolkit not available, cannot load tree")
            return None
            
        if self._tree is None:
            try:
                logger.info(f"Loading ETE tree from {self.tree_file}")
                self._tree = Tree(self.tree_file, format=1)
                logger.info("ETE tree loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load ETE tree: {str(e)}")
                raise
        return self._tree
    
    def search_tree_by_gene(self, gene_id: str, max_results: Optional[int] = None) -> List[ETESearchResult]:
        """Search for species containing a specific gene."""
        if not ETE_AVAILABLE:
            return []
        
        results = []
        tree = self.load_ete_tree()
        ortho_data, pagination = self.orthogroups_repo.load_orthogroups_data()  # Properly unpack tuple
        
        # Check if we have data to work with
        if ortho_data.empty:
            logger.warning("No orthogroups data available for gene search")
            return []
        
        # Find which species have this gene
        species_with_gene = []
        for col in ortho_data.columns[1:]:
            for _, row in ortho_data.iterrows():
                cell_value = row[col]
                if isinstance(cell_value, str) and gene_id in cell_value:
                    species_with_gene.append(col)
                    break
        
        # Find corresponding tree nodes - process all if max_results is None
        species_to_process = species_with_gene if max_results is None else species_with_gene[:max_results]
        for species_code in species_to_process:
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
    
    def search_tree_by_species(self, species_query: str, max_results: Optional[int] = None) -> List[ETESearchResult]:
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
                
                # Only check limit if max_results is specified
                if max_results is not None and len(results) >= max_results:
                    break
        
        return results
    
    def search_tree_by_clade(self, clade_query: str, max_results: Optional[int] = None) -> List[ETESearchResult]:
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
                    
                    # Only check limit if max_results is specified
                    if max_results is not None and len(results) >= max_results:
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
    
    async def search(self, query: str, search_type: str, max_results: Optional[int] = None, include_tree_image: bool = False) -> ETESearchResponse:
        """
        Unified search method that can search by species, clade, or gene
        """
        try:
            if search_type == "species":
                results = await self.search_species(query, max_results)
            elif search_type == "clade":
                results = await self.search_clade(query, max_results)
            elif search_type == "gene":
                # For gene search, we need to return ALL orthologue information
                results = await self.search_gene_in_orthogroups(query, max_results)
                
                # Get detailed orthologue information
                ortho_data, pagination = self.orthogroups_repo.load_orthogroups_data()
                
                # Find the orthogroup containing this gene and get ALL orthologues
                total_orthologues = 0
                orthogroup_id = None
                all_orthologue_genes = []
                
                for _, row in ortho_data.iterrows():
                    current_orthogroup_id = row[ortho_data.columns[0]]
                    
                    # Check if this orthogroup contains our gene
                    found_gene = False
                    for col in ortho_data.columns[1:]:
                        cell_value = row[col]
                        if isinstance(cell_value, str) and query in cell_value:
                            found_gene = True
                            orthogroup_id = current_orthogroup_id
                            break
                    
                    if found_gene:
                        # Count ALL genes in this orthogroup
                        for col in ortho_data.columns[1:]:
                            cell_value = row[col]
                            if isinstance(cell_value, str) and cell_value.strip():
                                genes = [gene.strip() for gene in cell_value.split(',') if gene.strip()]
                                total_orthologues += len(genes)
                                all_orthologue_genes.extend(genes)
                        break
                
                # Create enhanced response with complete orthologue information
                return ETESearchResponse(
                    success=True,
                    query=query,
                    search_type=search_type,
                    results=results,
                    total_results=len(results),
                    has_more=False,
                    tree_image_url=None,
                    # Add orthologue-specific information
                    total_orthologues=total_orthologues,
                    orthogroup_id=orthogroup_id,
                    species_with_orthologues=len([r for r in results if r.gene_count > 0])
                )
            else:
                raise ValueError(f"Unknown search type: {search_type}")
            
            # For non-gene searches, return standard response
            tree_image_url = None
            if include_tree_image and results:
                try:
                    tree_image_url = await self.generate_tree_image(results)
                except Exception as e:
                    logger.warning(f"Failed to generate tree image: {e}")
            
            return ETESearchResponse(
                success=True,
                query=query,
                search_type=search_type,
                results=results,
                total_results=len(results),
                has_more=False,
                tree_image_url=tree_image_url
            )
        
        except Exception as e:
            logger.error(f"Search failed for query '{query}' with type '{search_type}': {e}")
            return ETESearchResponse(
                success=False,
                query=query,
                search_type=search_type,
                results=[],
                total_results=0,
                has_more=False,
                error=str(e),
                tree_image_url=None
            )
    
    async def search_gene_in_orthogroups(self, gene_id: str, max_results: Optional[int] = None) -> List[ETESearchResult]:
        """Search for ALL individual genes in the orthogroup containing the specified gene (like Explore menu)."""
        # Build indices if not already built
        await self._build_gene_indices()
        
        # Defensive check - ensure indices are actually built
        if not self._indices_built or not self._gene_to_species_index:
            logger.warning("Gene indices not properly built, rebuilding...")
            # Force rebuild by resetting flag
            self._indices_built = False
            await self._build_gene_indices()
        
        results = []
        
        # Step 1: Find the orthogroup containing this gene
        # Get ALL data (no pagination limit) to ensure we find the right orthogroup
        ortho_data, pagination = self.orthogroups_repo.load_orthogroups_data(page=1, per_page=999999)
        
        if ortho_data.empty:
            logger.warning("No orthogroups data available")
            return []
        
        # Find which orthogroup contains this gene
        orthogroup_id = None
        orthogroup_row = None
        for _, row in ortho_data.iterrows():
            current_orthogroup_id = row[ortho_data.columns[0]]  # First column is orthogroup ID
            
            # Check all species columns for this gene
            for col in ortho_data.columns[1:]:
                cell_value = row[col]
                if isinstance(cell_value, str) and gene_id in cell_value:
                    orthogroup_id = current_orthogroup_id
                    orthogroup_row = row
                    logger.info(f"Found gene {gene_id} in orthogroup {orthogroup_id}")
                    break
            
            if orthogroup_id:
                break  # Gene found, stop searching
        
        if not orthogroup_id or orthogroup_row is None:
            logger.info(f"Gene {gene_id} not found in any orthogroup")
            return []
        
        # Step 2: Extract ALL individual genes from this orthogroup (like Explore menu)
        gene_count = 0
        species_with_genes = 0
        
        logger.info(f"Starting to extract genes from orthogroup {orthogroup_id}")
        
        for col in ortho_data.columns[1:]:  # Skip orthogroup ID column
            cell_value = orthogroup_row[col]
            
            if isinstance(cell_value, str) and cell_value.strip():
                # Split genes by comma and clean them
                genes = [gene.strip() for gene in cell_value.split(',') if gene.strip()]
                
                if genes:  # Only count species that actually have genes
                    species_with_genes += 1
                    logger.info(f"Species {col}: found {len(genes)} genes")
            
                # Create a result for EACH individual gene (like Explore does)
                for gene in genes:
                    # Get full species name from repository
                    full_species_name = self.species_repo.get_species_full_name(col)
            
            result = ETESearchResult(
                        node_name=f"{gene} ({full_species_name})",  # Show both gene and species
                        node_type="gene",  # Mark as individual gene
                distance_to_root=0.0,  # Not available without tree
                        gene_count=1,  # Each result represents 1 gene
                species_count=1,
                        clade_members=[full_species_name]
            )
            results.append(result)
                    gene_count += 1
                    
                    # Remove max_results limitation for gene search to match Explore behavior
                    # if max_results is not None and gene_count >= max_results:
                    #     logger.info(f"Reached max_results limit of {max_results}")
                    #     break
            
            # Remove outer loop limitation too
            # if max_results is not None and gene_count >= max_results:
            #     break
        
        logger.info(f"Gene search completed: found {len(results)} individual orthologous genes across {species_with_genes} species for gene {gene_id} in orthogroup {orthogroup_id}")
        return results
    
    async def search_species_in_orthogroups(self, species_query: str, max_results: Optional[int] = None) -> List[ETESearchResult]:
        """Search for species by name using orthogroups data."""
        # Build indices if not already built
        await self._build_gene_indices()
        
        results = []
        species_columns = self.orthogroups_repo.get_species_columns()
        query_lower = species_query.lower()
        
        # Search through species columns
        for species_code in species_columns:
            full_name = self.species_repo.get_species_full_name(species_code)
            
            # Check if query matches species name
            if (query_lower in species_code.lower() or
                query_lower in full_name.lower() or
                any(query_lower in word.lower() for word in full_name.split())):
                
                # Count genes for this species
                gene_count = len(self._species_to_genes_index.get(species_code, []))
                
                result = ETESearchResult(
                    node_name=full_name,
                    node_type="leaf",
                    distance_to_root=0.0,  # Not available without tree
                    gene_count=gene_count,
                    species_count=1,
                    clade_members=[full_name]
                )
                results.append(result)
                
                # Only check limit if max_results is specified
                if max_results is not None and len(results) >= max_results:
                    break
        
        logger.info(f"Species search found {len(results)} matching species for '{species_query}'")
        return results
    
    def get_ete_status(self) -> Dict[str, Any]:
        """Check ETE toolkit status and availability"""
        if not ETE_AVAILABLE:
            return {
                "success": False,
                "available": False,
                "error": "ETE3 toolkit not available"
            }
            
        try:
            tree = self.load_ete_tree()
            if tree is None:
                return {
                    "success": False,
                    "available": False,
                    "error": "Could not load tree"
                }
                
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
        if not ETE_AVAILABLE:
            raise Exception("ETE3 toolkit not available for tree rendering")
            
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
        if not ETE_AVAILABLE:
            raise Exception("ETE3 toolkit not available for tree analysis")
            
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

    async def _build_gene_indices(self):
        """Build gene indices for faster lookups with thread safety"""
        async with self._build_lock:  # Use async lock to prevent race conditions
            if self._indices_built:
                return
            
            try:
                logger.info("Building gene indices...")
                ortho_data, pagination = self.orthogroups_repo.load_orthogroups_data()
                
                # Check if we have data to work with
                if ortho_data.empty:
                    logger.warning("No orthogroups data available for building indices")
                    self._indices_built = False
                    return
                
                # Clear existing indices
                self._gene_to_species_index.clear()
                self._species_to_genes_index.clear()
                
                # Build gene-to-species mapping
                for col in ortho_data.columns[1:]:  # Skip first column (Orthogroup)
                    species_genes = []
                    for _, row in ortho_data.iterrows():
                        cell_value = row[col]
                        if isinstance(cell_value, str) and cell_value.strip():
                            genes = [gene.strip() for gene in cell_value.split(',') if gene.strip()]
                            species_genes.extend(genes)
                            # Add to gene-to-species index
                            for gene in genes:
                                if gene not in self._gene_to_species_index:
                                    self._gene_to_species_index[gene] = []
                                self._gene_to_species_index[gene].append(col)
                    
                    # Add to species-to-genes index
                    self._species_to_genes_index[col] = species_genes
                
                self._indices_built = True
                logger.info(f"Gene indices built: {len(self._gene_to_species_index)} genes, {len(self._species_to_genes_index)} species")
                
            except Exception as e:
                logger.error(f"Failed to build gene indices: {str(e)}")
                self._indices_built = False

    async def search_species(self, species_query: str, max_results: Optional[int] = None) -> List[ETESearchResult]:
        """Async wrapper for species search."""
        return self.search_tree_by_species(species_query, max_results)
    
    async def search_clade(self, clade_query: str, max_results: Optional[int] = None) -> List[ETESearchResult]:
        """Async wrapper for clade search."""
        return self.search_tree_by_clade(clade_query, max_results)

def get_ete_tree_service():
    """Get the global ETE tree service instance"""
    global _ete_service_instance
    if _ete_service_instance is None:
        _ete_service_instance = ETETreeService()
    return _ete_service_instance