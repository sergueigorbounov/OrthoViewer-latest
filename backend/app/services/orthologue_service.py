import logging
from typing import Dict, List, Optional, Any, Set

from app.data_access.orthogroups_repository import OrthogroupsRepository
from app.data_access.species_repository import SpeciesRepository
from app.models.phylo import (
    OrthologueSearchRequest, OrthologueSearchResponse, OrthologueData, OrthoSpeciesCount
)

# Configure logging
logger = logging.getLogger(__name__)

class OrthologueService:
    """Service for orthologue-related operations."""
    
    def __init__(self):
        """Initialize the service with repositories."""
        self.orthogroups_repo = OrthogroupsRepository()
        self.species_repo = SpeciesRepository()
    
    async def search_orthologues(self, request: OrthologueSearchRequest) -> OrthologueSearchResponse:
        """Search for orthologues of a given gene."""
        gene_id = request.gene_id.strip()
        logger.info(f"Searching for orthologues of gene: {gene_id}")
        
        try:
            # Start timing the search
            import time
            start_time = time.time()
            
            # Find the orthogroup for the gene
            orthogroup_id = self.orthogroups_repo.find_gene_orthogroup(gene_id)
            
            # Log time taken to find orthogroup
            find_time = time.time() - start_time
            logger.info(f"Time to find orthogroup: {find_time:.2f} seconds")
            
            if not orthogroup_id:
                logger.warning(f"Gene {gene_id} not found in any orthogroup")
                return OrthologueSearchResponse(
                    success=False,
                    gene_id=gene_id,
                    message=f"Gene {gene_id} not found in any orthogroup"
                )
            
            logger.info(f"Gene {gene_id} found in orthogroup {orthogroup_id}")
            
            # Get all genes in the orthogroup
            start_time = time.time()
            genes_by_species = self.orthogroups_repo.get_orthogroup_genes(orthogroup_id)
            get_genes_time = time.time() - start_time
            logger.info(f"Time to get genes: {get_genes_time:.2f} seconds")
            logger.info(f"Found {sum(len(genes) for genes in genes_by_species.values())} genes in {len(genes_by_species)} species")
            
            # Load species mapping
            species_mapping = self.species_repo.load_species_mapping()
            
            # Enhance species mapping with the species from orthogroups
            ortho_species = set(genes_by_species.keys())
            enhanced_mapping = self.species_repo.enhance_species_mapping(ortho_species)
            
            # Get species tree
            species_tree = self.species_repo.load_species_tree()
            
            # Process results into response format
            start_time = time.time()
            orthologue_data = []
            
            # Get total gene count
            total_genes = sum(len(genes) for genes in genes_by_species.values())
            
            for species_code, genes in genes_by_species.items():
                # Get full species name
                species_name = self.species_repo.get_species_full_name(species_code)
                
                # Add to orthologue data
                orthologue_data.append(
                    OrthologueData(
                        species_id=species_code,
                        species_name=species_name,
                        genes=genes
                    )
                )
            
            # Sort by species name
            orthologue_data.sort(key=lambda x: x.species_name)
            
            # Count species per genes
            species_count = [
                OrthoSpeciesCount(
                    gene_count=len(genes),
                    species_count=1
                ) for _, genes in genes_by_species.items()
            ]
            
            # Create response
            response = OrthologueSearchResponse(
                success=True,
                gene_id=gene_id,
                orthogroup_id=orthogroup_id,
                total_genes=total_genes,
                total_species=len(genes_by_species),
                species_tree=species_tree,
                orthologues=orthologue_data,
                species_count=species_count
            )
            
            # Log processing time
            process_time = time.time() - start_time
            logger.info(f"Time to process results: {process_time:.2f} seconds")
            
            # Log total time
            total_time = find_time + get_genes_time + process_time
            logger.info(f"Total search time: {total_time:.2f} seconds")
            
            return response
            
        except Exception as e:
            logger.error(f"Error searching for orthologues: {str(e)}", exc_info=True)
            return OrthologueSearchResponse(
                success=False,
                gene_id=gene_id,
                message=f"Error searching for orthologues: {str(e)}"
            )