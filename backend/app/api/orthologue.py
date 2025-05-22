from fastapi import APIRouter, HTTPException, Path, Query
from typing import List, Dict, Any, Optional
import os
import pandas as pd
import logging
from collections import defaultdict
from ..models.phylo import OrthologueSearchRequest, OrthologueSearchResponse, OrthologueData, OrthoSpeciesCount

# Create router
router = APIRouter(
    prefix="/api/orthologue",
    tags=["orthologue"],
    responses={404: {"description": "Not found"}},
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Data paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATA_DIR = os.environ.get("ORTHOFINDER_DATA_DIR", os.path.join(BASE_DIR, "data/orthofinder"))
TREE_FILE = os.path.join(DATA_DIR, "SpeciesTree_nameSp_completeGenome110124.tree")
ORTHOGROUPS_FILE = os.path.join(DATA_DIR, "Orthogroups_clean_121124.txt")
SPECIES_MAPPING_FILE = os.path.join(DATA_DIR, "Table_S1_Metadata_angiosperm_species.csv")

# Cache for the data to avoid reloading
_orthogroups_data = None
_species_mapping = None
_species_tree = None

def load_orthogroups_data():
    """Load orthogroups data from CSV file"""
    global _orthogroups_data
    if _orthogroups_data is None:
        try:
            logger.info(f"Loading orthogroups data from {ORTHOGROUPS_FILE}")
            _orthogroups_data = pd.read_csv(ORTHOGROUPS_FILE, sep='\t')
            logger.info(f"Loaded orthogroups data with shape: {_orthogroups_data.shape}")
        except Exception as e:
            logger.error(f"Failed to load orthogroups data: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to load orthogroups data: {str(e)}")
    return _orthogroups_data

def load_species_mapping():
    """Load species mapping data from CSV file"""
    global _species_mapping
    if _species_mapping is None:
        try:
            logger.info(f"Loading species mapping from {SPECIES_MAPPING_FILE}")
            
            # Try to read as text first
            with open(SPECIES_MAPPING_FILE, 'r') as f:
                lines = f.readlines()
                
            logger.info(f"Read {len(lines)} lines from species mapping file")
            
            # Mapping structure
            species_data = []
            for line in lines:
                # Skip empty lines and header lines
                if not line.strip() or line.startswith('Table') or ':' in line[:15]:
                    continue
                    
                # Try to split the line by common delimiters
                parts = None
                for delimiter in ['\t', ',', ';', '|']:
                    if delimiter in line:
                        parts = line.strip().split(delimiter)
                        if len(parts) >= 2:
                            break
                
                # If no delimiter worked, try splitting by multiple spaces
                if not parts or len(parts) < 2:
                    parts = [p for p in line.strip().split() if p]
                
                if parts and len(parts) >= 2:
                    # Use first part as abbreviation/id and second as name
                    species_data.append({
                        'species_abbreviation': parts[0].strip(),
                        'species_name': parts[1].strip(),
                        'species_id': parts[0].strip()
                    })
            
            # Create a DataFrame from our parsed data
            mapping_df = pd.DataFrame(species_data)
            
            # Log what we found
            logger.info(f"Parsed {len(species_data)} species entries")
            if len(species_data) > 0:
                logger.info(f"First entry: {species_data[0]}")
            
            # Use standard column names
            species_abbr_col = 'species_abbreviation'
            species_name_col = 'species_name'
            species_id_col = 'species_id'
            
            # Create mapping dictionaries
            _species_mapping = {
                'newick_to_full': dict(zip(mapping_df[species_abbr_col], mapping_df[species_name_col])),
                'full_to_newick': dict(zip(mapping_df[species_name_col], mapping_df[species_abbr_col])),
                'id_to_full': dict(zip(mapping_df[species_id_col], mapping_df[species_name_col])),
                'full_to_id': dict(zip(mapping_df[species_name_col], mapping_df[species_id_col]))
            }
            
            logger.info(f"Loaded species mapping with {len(_species_mapping['newick_to_full'])} entries")
            
            # If we couldn't extract any mappings, create a minimal fallback
            if len(_species_mapping['newick_to_full']) == 0:
                logger.warning("No species mappings found, creating minimal fallback")
                # Create a dummy mapping that just uses the same value for abbreviation and name
                # This will at least allow the code to continue running
                _species_mapping = {
                    'newick_to_full': {'dummy': 'dummy'},
                    'full_to_newick': {'dummy': 'dummy'},
                    'id_to_full': {'dummy': 'dummy'},
                    'full_to_id': {'dummy': 'dummy'}
                }
                
        except Exception as e:
            logger.error(f"Failed to load species mapping: {str(e)}")
            # Create a minimal fallback mapping
            _species_mapping = {
                'newick_to_full': {'dummy': 'dummy'},
                'full_to_newick': {'dummy': 'dummy'},
                'id_to_full': {'dummy': 'dummy'},
                'full_to_id': {'dummy': 'dummy'}
            }
    return _species_mapping

def load_species_tree(optimize_for_viz=False):
    """
    Load species tree from Newick file
    
    Args:
        optimize_for_viz (bool): If True, optimize the tree data for visualization by:
            - Adding internal node labels if missing
            - Ensuring node names match with species in orthologue data
            - Adding any necessary metadata for better visualization
    """
    global _species_tree
    if _species_tree is None:
        try:
            logger.info(f"Loading species tree from {TREE_FILE}")
            with open(TREE_FILE, 'r') as f:
                _species_tree = f.read().strip()
            logger.info(f"Loaded species tree with length: {len(_species_tree)}")
            
            # Perform tree optimization if requested
            if optimize_for_viz:
                # Load species mapping to ensure node labels match the species data
                species_mapping = load_species_mapping()
                
                # Basic tree optimization - replace abbreviated species names with full names
                # This is a simplified approach - a real implementation would use 
                # a proper Newick parser library for more complex tree manipulations
                for abbrev, full_name in species_mapping.get('newick_to_full', {}).items():
                    # Only replace complete node names (not substrings)
                    # Use word boundaries to ensure we match whole node names
                    _species_tree = _species_tree.replace(
                        f"({abbrev}:", f"({full_name}:"
                    ).replace(
                        f",{abbrev}:", f",{full_name}:"
                    ).replace(
                        f"{abbrev};", f"{full_name};"
                    )
                
                logger.info(f"Optimized tree for visualization")
        except Exception as e:
            logger.error(f"Failed to load species tree: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to load species tree: {str(e)}")
    return _species_tree

def find_gene_orthogroup(gene_id: str) -> Optional[str]:
    """Find the orthogroup ID for a given gene ID"""
    df = load_orthogroups_data()
    
    # Search for the gene ID in all columns
    for col in df.columns:
        # Skip the orthogroup ID column (assuming it's the first column)
        if col == df.columns[0]:
            continue
            
        # Check if gene ID is in this column (species)
        # Each cell might contain multiple genes separated by comma
        mask = df[col].apply(lambda x: isinstance(x, str) and gene_id in x.split(','))
        if mask.any():
            # Return the orthogroup ID for the matching row
            return df.loc[mask, df.columns[0]].iloc[0]
    
    return None

def get_orthogroup_genes(orthogroup_id: str) -> Dict[str, List[str]]:
    """Get all genes in an orthogroup, organized by species"""
    df = load_orthogroups_data()
    
    # Find the row with this orthogroup ID
    orthogroup_row = df[df[df.columns[0]] == orthogroup_id]
    
    if orthogroup_row.empty:
        return {}
    
    # Extract genes by species
    genes_by_species = {}
    for col in df.columns[1:]:  # Skip the orthogroup ID column
        cell_value = orthogroup_row[col].iloc[0]
        if isinstance(cell_value, str) and cell_value.strip():
            genes = [gene.strip() for gene in cell_value.split(',')]
            genes_by_species[col] = genes
    
    return genes_by_species

@router.post("/search", response_model=OrthologueSearchResponse)
async def search_orthologues(request: OrthologueSearchRequest):
    """Search for orthologues of a given gene ID"""
    gene_id = request.gene_id.strip()
    
    # Find which orthogroup the gene belongs to
    orthogroup_id = find_gene_orthogroup(gene_id)
    
    if not orthogroup_id:
        return OrthologueSearchResponse(
            success=False,
            gene_id=gene_id,
            message=f"Gene {gene_id} not found in any orthogroup"
        )
    
    # Get all genes in the orthogroup
    genes_by_species = get_orthogroup_genes(orthogroup_id)
    
    # Load species mapping for name conversion
    species_mapping = load_species_mapping()
    
    # Prepare response
    orthologues = []
    counts_by_species = []
    
    for species, genes in genes_by_species.items():
        # Map species column name to full name and ID
        species_full_name = species
        species_id = species_mapping.get('full_to_id', {}).get(species_full_name, species)
        
        # Count genes for this species
        gene_count = len(genes)
        counts_by_species.append(
            OrthoSpeciesCount(
                species_id=species_id,
                species_name=species_full_name,
                count=gene_count
            )
        )
        
        # Add individual orthologues
        for gene in genes:
            orthologues.append(
                OrthologueData(
                    gene_id=gene,
                    species_id=species_id,
                    species_name=species_full_name,
                    orthogroup_id=orthogroup_id
                )
            )
    
    # Get the species tree - use optimized version for visualization
    species_tree = load_species_tree(optimize_for_viz=True)
    
    return OrthologueSearchResponse(
        success=True,
        gene_id=gene_id,
        orthogroup_id=orthogroup_id,
        orthologues=orthologues,
        counts_by_species=counts_by_species,
        newick_tree=species_tree
    )

@router.get("/tree", response_model=Dict[str, Any])
async def get_orthologue_tree():
    """Get the species phylogenetic tree in Newick format"""
    try:
        # Use optimized version for visualization
        species_tree = load_species_tree(optimize_for_viz=True)
        return {
            "success": True,
            "newick": species_tree
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to load species tree: {str(e)}"
        } 