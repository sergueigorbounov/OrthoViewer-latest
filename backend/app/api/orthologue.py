from fastapi import APIRouter, HTTPException, Path, Query
from typing import List, Dict, Any, Optional
import os
import json
import pandas as pd
import logging
import tempfile
import base64
from ..models.phylo import (
    OrthologueSearchRequest, OrthologueSearchResponse, OrthologueData, OrthoSpeciesCount,
    ETESearchRequest, ETESearchResponse, ETESearchResult
)
from ..utils.species_utils import get_species_full_name
from .search_patch import search_orthologues_patched
from .gene_finder import build_gene_to_orthogroup_map, find_gene_orthogroup as find_gene_in_orthogroup_lookup

# ETE3 imports
try:
    from ete3 import Tree, TreeStyle, NodeStyle
    ETE_AVAILABLE = True
except ImportError as e:
    ETE_AVAILABLE = False

# Create router
router = APIRouter(
    prefix="/api/orthologue",
    tags=["orthologue"],
    responses={404: {"description": "Not found"}},
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Data paths - Utiliser le chemin absolu pour les fichiers de données
BASE_DIR = "/home/sgorbounov/Documents/orthoviewer2-clean"
DATA_DIR = os.path.join(BASE_DIR, "data/orthofinder")
TREE_FILE = os.path.join(DATA_DIR, "SpeciesTree_nameSp_completeGenome110124.tree")
ORTHOGROUPS_FILE = os.path.join(DATA_DIR, "Orthogroups_clean_121124.txt")  # Using the full dataset instead of sample
SPECIES_MAPPING_FILE = os.path.join(DATA_DIR, "Table_S1_Metadata_angiosperm_species.csv")

# Cache pour les données afin d'éviter de les recharger
_orthogroups_data = None
_species_mapping = None
_species_tree = None
_ete_tree = None  # ETE tree cache
_gene_map = {}  # Cache for gene-to-orthogroup mapping

def load_orthogroups_data():
    """Charger les données d'orthogroupes depuis le fichier CSV"""
    global _orthogroups_data
    global _gene_map

    if _orthogroups_data is None:
        try:
            logger.info(f"Chargement des données d'orthogroupes depuis {ORTHOGROUPS_FILE}")
            # Déterminer le séparateur en fonction de l'extension du fichier
            sep = '\t' if ORTHOGROUPS_FILE.endswith('.tsv') or ORTHOGROUPS_FILE.endswith('.txt') else ','
            _orthogroups_data = pd.read_csv(ORTHOGROUPS_FILE, sep=sep, low_memory=False)
            logger.info(f"Données d'orthogroupes chargées avec succès: {_orthogroups_data.shape}")
            
            # Afficher les premières lignes pour déboguer
            logger.info(f"Premières lignes des données d'orthogroupes:")
            logger.info(f"Colonnes: {_orthogroups_data.columns.tolist()}")
            logger.info(f"Échantillon: \n{_orthogroups_data.head(2)}")

            # Build the gene-to-orthogroup mapping for faster lookups
            _gene_map = build_gene_to_orthogroup_map(_orthogroups_data)
            logger.info(f"Gene mapping built with {len(_gene_map)} entries")

        except Exception as e:
            logger.error(f"Échec du chargement des données d'orthogroupes: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Échec du chargement des données d'orthogroupes: {str(e)}")
    return _orthogroups_data

def generate_fallback_name(species_code):
    """Generate a reasonable fallback name for unmapped species codes"""
    # Common genus mappings based on typical patterns
    genus_hints = {
        'A': ['Arabidopsis', 'Aegilops', 'Actinidia', 'Amaranthus', 'Acorus'],
        'B': ['Brassica', 'Beta', 'Bambusa'],
        'C': ['Citrus', 'Cannabis', 'Cucumis', 'Coffea', 'Camelina', 'Capsella'],
        'D': ['Daucus'],
        'E': ['Eucalyptus'],
        'F': ['Fragaria'],
        'G': ['Glycine', 'Gossypium'],
        'H': ['Helianthus', 'Hordeum'],
        'L': ['Lotus', 'Lupinus', 'Lactuca', 'Linum'],
        'M': ['Medicago', 'Malus', 'Musa', 'Manihot'],
        'N': ['Nicotiana', 'Nelumbo'],
        'O': ['Oryza', 'Olea'],
        'P': ['Populus', 'Pisum', 'Prunus', 'Panicum', 'Phaseolus'],
        'Q': ['Quercus'],
        'R': ['Ricinus'],
        'S': ['Solanum', 'Sorghum', 'Setaria', 'Sesamum'],
        'T': ['Triticum', 'Theobroma', 'Trifolium'],
        'V': ['Vigna', 'Vitis'],
        'W': ['Wheat line'],
        'Z': ['Zea']
    }
    
    if len(species_code) >= 1:
        first_letter = species_code[0].upper()
        if first_letter in genus_hints:
            possible_genera = genus_hints[first_letter]
            # Use the first genus as a reasonable guess
            return f"{possible_genera[0]} sp. ({species_code})"
    
    # Ultimate fallback
    return f"Species {species_code}"

def get_species_full_name_enhanced(species_code, species_mapping):
    """Get species full name with enhanced fallback strategies"""
    # Try different mapping strategies
    for mapping_key in ['id_to_full', 'prefix_to_full', 'newick_to_full']:
        if species_code in species_mapping.get(mapping_key, {}):
            return species_mapping[mapping_key][species_code]
    
    # Final fallback
    return generate_fallback_name(species_code)

def load_species_mapping():
    """Load species mapping with correct file format handling"""
    global _species_mapping
    if _species_mapping is None:
        try:
            logger.info(f"Loading species mapping from {SPECIES_MAPPING_FILE}")
            
            # Load mapping file: skip header (first 2 lines), use tab separator
            mapping_df = pd.read_csv(SPECIES_MAPPING_FILE, sep='\t', skiprows=2)
            logger.info(f"Species mapping loaded successfully: {mapping_df.shape}")
            logger.info(f"Mapping columns: {mapping_df.columns.tolist()}")
            
            # Column structure: [Full_Species_Name, Species_ID, Annotation, ...]
            # We want: Species_ID -> Full_Species_Name
            species_full_col = mapping_df.columns[0]  # Full species name (e.g., "Acorus tatarinowii")
            species_id_col = mapping_df.columns[1]    # Species ID (e.g., "Ata")
            
            logger.info(f"Using mapping: '{species_id_col}' -> '{species_full_col}'")
            
            # Create basic mapping: ID -> Full Name
            id_to_full = dict(zip(mapping_df[species_id_col], mapping_df[species_full_col]))
            full_to_id = dict(zip(mapping_df[species_full_col], mapping_df[species_id_col]))
            
            # Load orthogroups to see what species we actually need to map
            ortho_df = pd.read_csv(ORTHOGROUPS_FILE, sep='\t', low_memory=False)
            ortho_species = set(ortho_df.columns[1:])
            
            # Enhanced mapping with fallbacks for missing species
            enhanced_mapping = id_to_full.copy()
            
            # Find missing species and create fallback mappings
            missing_species = ortho_species - set(id_to_full.keys())
            logger.info(f"Found {len(missing_species)} species needing fallback mapping")
            
            for missing_code in missing_species:
                # Strategy 1: Look for partial matches in existing mappings
                found_match = False
                for mapped_id, full_name in id_to_full.items():
                    # Check if missing code is similar to mapped ID (first 2-3 letters match)
                    if (len(missing_code) >= 2 and len(mapped_id) >= 2 and
                        missing_code.lower()[:2] == mapped_id.lower()[:2] and 
                        abs(len(missing_code) - len(mapped_id)) <= 2):
                        enhanced_mapping[missing_code] = f"{full_name} (variant {missing_code})"
                        found_match = True
                        logger.info(f"Partial match found: '{missing_code}' -> '{enhanced_mapping[missing_code]}'")
                        break
                
                # Strategy 2: Generate reasonable fallback names
                if not found_match:
                    fallback_name = generate_fallback_name(missing_code)
                    enhanced_mapping[missing_code] = fallback_name
                    logger.info(f"Fallback mapping created: '{missing_code}' -> '{fallback_name}'")
            
            # Create all mapping dictionaries
            _species_mapping = {
                'newick_to_full': enhanced_mapping.copy(),
                'full_to_newick': full_to_id.copy(),
                'id_to_full': enhanced_mapping.copy(),
                'full_to_id': full_to_id.copy(),
                'prefix_to_full': enhanced_mapping.copy()
            }
            
            # Log mapping success
            mapped_count = len(set(enhanced_mapping.keys()) & ortho_species)
            logger.info(f"Species mapping complete: {mapped_count}/{len(ortho_species)} species mapped ({mapped_count/len(ortho_species)*100:.1f}%)")
            
            # Log some sample mappings
            sample_mappings = list(enhanced_mapping.items())[:5]
            for code, name in sample_mappings:
                logger.info(f"Sample mapping: '{code}' -> '{name}'")
                
        except Exception as e:
            logger.error(f"Failed to load species mapping: {str(e)}")
            # Create minimal fallback mapping
            _species_mapping = {
                'newick_to_full': {},
                'full_to_newick': {},
                'id_to_full': {},
                'full_to_id': {},
                'prefix_to_full': {}
            }
    return _species_mapping

def load_species_tree():
    """Charger l'arbre des espèces depuis le fichier Newick"""
    global _species_tree
    if _species_tree is None:
        try:
            logger.info(f"Chargement de l'arbre des espèces depuis {TREE_FILE}")
            with open(TREE_FILE, 'r') as f:
                _species_tree = f.read().strip()
            logger.info(f"Arbre des espèces chargé avec succès: {len(_species_tree)} caractères")
        except Exception as e:
            logger.error(f"Échec du chargement de l'arbre des espèces: {str(e)}")
            # Arbre minimal de secours
            _species_tree = "(A:0.1,B:0.2);"
    return _species_tree

# =============================================================================
# ETE3 TOOLKIT FUNCTIONS
# =============================================================================

def load_ete_tree():
    """Load phylogenetic tree using ETE toolkit"""
    global _ete_tree
    if not ETE_AVAILABLE:
        raise HTTPException(status_code=500, detail="ETE3 toolkit not available")
        
    if _ete_tree is None:
        try:
            logger.info("Loading tree with ETE toolkit")
            tree_content = load_species_tree()
            _ete_tree = Tree(tree_content, format=1)
            
            # Add species count information to tree nodes
            species_mapping = load_species_mapping()
            ortho_data = load_orthogroups_data()
            species_columns = ortho_data.columns[1:].tolist()
            
            # Map species to tree nodes
            for leaf in _ete_tree.get_leaves():
                leaf_name = leaf.name.strip().strip('"\'')
                
                # Try to find matching species in our data
                enhanced_mapping = species_mapping.get('id_to_full', {})
                
                if leaf_name in enhanced_mapping:
                    full_name = enhanced_mapping[leaf_name]
                    leaf.add_feature("full_species_name", full_name)
                    leaf.add_feature("species_code", leaf_name)
                    
                    # Count genes for this species
                    if leaf_name in species_columns:
                        gene_count = 0
                        for _, row in ortho_data.iterrows():
                            cell_value = row[leaf_name]
                            if isinstance(cell_value, str) and cell_value.strip():
                                genes = [g.strip() for g in cell_value.split(',') if g.strip()]
                                gene_count += len(genes)
                        leaf.add_feature("gene_count", gene_count)
                    
            logger.info(f"ETE tree loaded with {len(_ete_tree.get_leaves())} leaves")
            
        except Exception as e:
            logger.error(f"Failed to load ETE tree: {str(e)}")
            # Create a simple fallback tree
            _ete_tree = Tree("(A:1,B:1);")
    
    return _ete_tree

def search_tree_by_gene(gene_id: str, max_results: int = 50) -> List[ETESearchResult]:
    """Search for species containing a specific gene"""
    results = []
    tree = load_ete_tree()
    ortho_data = load_orthogroups_data()
    
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

def search_tree_by_species(species_query: str, max_results: int = 50) -> List[ETESearchResult]:
    """Search for species by name (fuzzy matching)"""
    results = []
    tree = load_ete_tree()
    species_mapping = load_species_mapping()
    
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

def search_tree_by_clade(clade_query: str, max_results: int = 50) -> List[ETESearchResult]:
    """Search for clades containing specific taxa"""
    results = []
    tree = load_ete_tree()
    
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

def find_common_ancestor_search(species_list: List[str]) -> List[ETESearchResult]:
    """Find common ancestor of specified species"""
    results = []
    tree = load_ete_tree()
    
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

def generate_tree_image(tree: Tree, highlighted_nodes: List[str] = None) -> str:
    """Generate tree visualization with ETE and return as base64 string"""
    try:
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

# =============================================================================
# ORIGINAL FUNCTIONS
# =============================================================================

def get_orthogroup_genes(orthogroup_id: str) -> Dict[str, List[str]]:
    """Obtenir tous les gènes d'un orthogroupe, organisés par espèce"""
    df = load_orthogroups_data()
    
    # Trouver la ligne avec cet ID d'orthogroupe
    orthogroup_row = df[df[df.columns[0]] == orthogroup_id]
    
    if orthogroup_row.empty:
        return {}
    
    # Extraire les gènes par espèce
    genes_by_species = {}
    for col in df.columns[1:]:  # Ignorer la colonne ID d'orthogroupe
        cell_value = orthogroup_row[col].iloc[0]
        if isinstance(cell_value, str) and cell_value.strip():
            genes = [gene.strip() for gene in cell_value.split(',')]
            genes_by_species[col] = genes
    
    return genes_by_species

def find_gene_orthogroup(gene_id: str) -> Optional[str]:
    """Trouver l'ID d'orthogroupe pour un gène donné"""
    global _gene_map
    df = load_orthogroups_data()

    # Use the optimized gene finder - FIXED: use the correct aliased function name
    return find_gene_in_orthogroup_lookup(gene_id, _gene_map, df)

# =============================================================================
# API ENDPOINTS
# =============================================================================

@router.post("/search", response_model=OrthologueSearchResponse)
async def search_orthologues(request: OrthologueSearchRequest):
    """Rechercher les orthologues d'un gène donné"""
    gene_id = request.gene_id.strip()
    logger.info(f"Recherche des orthologues du gène: {gene_id}")
    
    try:
        # Start timing the search
        import time
        start_time = time.time()

        # Trouver à quel orthogroupe appartient le gène
        orthogroup_id = find_gene_orthogroup(gene_id)

        # Log time taken to find orthogroup
        find_time = time.time() - start_time
        logger.info(f"Time to find orthogroup: {find_time:.2f} seconds")

        if not orthogroup_id:
            logger.warning(f"Gene {gene_id} not found in any orthogroup")
            return OrthologueSearchResponse(
                success=False,
                gene_id=gene_id,
                message=f"Gène {gene_id} non trouvé dans aucun orthogroupe"
            )

        logger.info(f"Gène {gene_id} trouvé dans l'orthogroupe {orthogroup_id}")

        # Obtenir tous les gènes de l'orthogroupe
        start_time = time.time()
        genes_by_species = get_orthogroup_genes(orthogroup_id)
        get_genes_time = time.time() - start_time
        logger.info(f"Time to get genes: {get_genes_time:.2f} seconds")

        logger.info(f"Found {sum(len(genes) for genes in genes_by_species.values())} genes in {len(genes_by_species)} species")

        # Charger le mapping d'espèces pour la conversion des noms
        species_mapping = load_species_mapping()

        # Obtenir l'arbre des espèces
        species_tree = load_species_tree()

        # Use our patched search function to correctly handle species names
        start_time = time.time()
        result = await search_orthologues_patched(
            gene_id=gene_id,
            orthogroup_id=orthogroup_id,
            genes_by_species=genes_by_species,
            species_mapping=species_mapping,
            species_tree=species_tree,
            load_orthogroups_data=load_orthogroups_data
        )
        search_time = time.time() - start_time
        logger.info(f"Time to process results: {search_time:.2f} seconds")

        # Log total time
        total_time = find_time + get_genes_time + search_time
        logger.info(f"Total search time: {total_time:.2f} seconds")

        return result
    except Exception as e:
        logger.error(f"Error searching for orthologues: {str(e)}", exc_info=True)
        return OrthologueSearchResponse(
            success=False,
            gene_id=gene_id,
            message=f"Error searching for orthologues: {str(e)}"
        )

@router.post("/ete-search", response_model=ETESearchResponse)
async def ete_tree_search(request: ETESearchRequest):
    """Advanced tree-based search using ETE toolkit"""
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
            results = search_tree_by_gene(request.query, request.max_results)
        elif request.search_type == "species":
            results = search_tree_by_species(request.query, request.max_results)
        elif request.search_type == "clade":
            results = search_tree_by_clade(request.query, request.max_results)
        elif request.search_type == "common_ancestor":
            # Parse comma-separated species list
            species_list = [s.strip() for s in request.query.split(",")]
            results = find_common_ancestor_search(species_list)
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
            tree = load_ete_tree()
            highlighted_nodes = [r.node_name for r in results[:5]]  # Highlight first 5 results
            tree_image = generate_tree_image(tree, highlighted_nodes)
        
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

@router.get("/tree", response_model=Dict[str, Any])
async def get_orthologue_tree():
    """Obtenir l'arbre phylogénétique des espèces au format Newick"""
    try:
        species_tree = load_species_tree()
        return {
            "success": True,
            "newick": species_tree
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Échec du chargement de l'arbre des espèces: {str(e)}"
        }

@router.get("/ete-status")
async def get_ete_status():
    """Check ETE3 toolkit availability and status"""
    try:
        if not ETE_AVAILABLE:
            return {
                "success": False,
                "ete_available": False,
                "message": "ETE3 toolkit not installed. Install with: conda install -c etetoolkit ete3"
            }
        
        # Test ETE functionality
        tree = load_ete_tree()
        leaf_count = len(tree.get_leaves())
        
        return {
            "success": True,
            "ete_available": True,
            "tree_loaded": True,
            "leaf_count": leaf_count,
            "message": f"ETE3 toolkit ready with {leaf_count} species"
        }
    except Exception as e:
        return {
            "success": False,
            "ete_available": ETE_AVAILABLE,
            "error": str(e),
            "message": f"ETE3 error: {str(e)}"
        }

# Debug endpoint to check species mapping (remove after testing)
@router.get("/debug/species-mapping")
async def debug_species_mapping_endpoint():
    """Debug endpoint to check species mapping issues"""
    try:
        # Load orthogroups data
        ortho_df = pd.read_csv(ORTHOGROUPS_FILE, sep='\t', low_memory=False)
        species_columns = ortho_df.columns[1:].tolist()
        
        # Load mapping data
        mapping_df = pd.read_csv(SPECIES_MAPPING_FILE, sep='\t', skiprows=2)
        species_full_col = mapping_df.columns[0]
        species_id_col = mapping_df.columns[1]
        
        mapping_codes = set(mapping_df[species_id_col].astype(str))
        ortho_codes = set(species_columns)
        
        missing_in_mapping = ortho_codes - mapping_codes
        found_in_both = ortho_codes & mapping_codes
        
        # Sample mappings for found codes
        sample_mappings = {}
        for code in list(found_in_both)[:10]:
            full_name = mapping_df[mapping_df[species_id_col] == code][species_full_col].iloc[0]
            sample_mappings[code] = full_name
        
        return {
            "success": True,
            "total_ortho_species": len(ortho_codes),
            "total_mapping_entries": len(mapping_codes),
            "missing_in_mapping": {
                "count": len(missing_in_mapping),
                "examples": list(missing_in_mapping)[:20]  # First 20 examples
            },
            "successfully_mapped": {
                "count": len(found_in_both),
                "examples": sample_mappings
            },
            "mapping_file_columns": mapping_df.columns.tolist(),
            "ortho_file_columns_sample": species_columns[:10],
            "ete_available": ETE_AVAILABLE
        }
        
    except Exception as e:
        logger.error(f"Debug error: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }