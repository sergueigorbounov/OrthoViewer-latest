"""
This file contains a patched version of the search_orthologues function
that properly resolves species names and counts.
"""
import logging
from ..models.phylo import OrthologueSearchResponse, OrthologueData, OrthoSpeciesCount
from ..utils.species_utils import get_species_full_name

logger = logging.getLogger(__name__)

async def search_orthologues_patched(
    gene_id, 
    orthogroup_id, 
    genes_by_species, 
    species_mapping, 
    species_tree, 
    load_orthogroups_data
):
    """Patched version of search_orthologues that properly handles species names"""
    try:
        df = load_orthogroups_data()
        logger.info(f"Loaded orthogroups data with shape: {df.shape}")
        
        # Préparer la réponse
        orthologues = []
        counts_by_species = []
        
        # First, create counts for all species (even those with zero orthologues)
        # We'll use the species from the orthogroup data as the source of truth
        species_columns = [col for col in df.columns if col != df.columns[0]]  # Skip the first column (orthogroup ID)
        logger.info(f"Found {len(species_columns)} species columns in the data")
        
        # Create a set of all species from the orthogroup data
        all_species_ids = set(species_columns)
        
        # Add species counts for all species
        for species_id in all_species_ids:
            # Get the full name using our utility function
            species_full_name = get_species_full_name(species_id, species_mapping)
            
            # Count genes for this species (0 if species not in the orthogroup)
            gene_count = len(genes_by_species.get(species_id, []))
            
            # Add to counts (include all species, even those with 0 count)
            counts_by_species.append(
                OrthoSpeciesCount(
                    species_id=species_id,
                    species_name=species_full_name,
                    count=gene_count
                )
            )
        
        logger.info(f"Total species in counts: {len(counts_by_species)}")
        
        # Now add the actual orthologues
        for species_id, genes in genes_by_species.items():
            # Get the full name using our utility function
            species_full_name = get_species_full_name(species_id, species_mapping)
            
            # Add the orthologues for this species
            for gene in genes:
                # Ne pas ajouter le gène de requête lui-même
                if gene != gene_id:
                    orthologues.append(
                        OrthologueData(
                            gene_id=gene,
                            species_id=species_id,
                            species_name=species_full_name,
                            orthogroup_id=orthogroup_id
                        )
                    )
        
        logger.info(f"Returning {len(orthologues)} orthologues for gene {gene_id}")
        
        return OrthologueSearchResponse(
            success=True,
            gene_id=gene_id,
            orthogroup_id=orthogroup_id,
            orthologues=orthologues,
            counts_by_species=counts_by_species,
            newick_tree=species_tree
        )
    except Exception as e:
        logger.error(f"Error in patched search: {str(e)}", exc_info=True)
        return OrthologueSearchResponse(
            success=False,
            gene_id=gene_id,
            message=f"Error searching for orthologues: {str(e)}"
        )