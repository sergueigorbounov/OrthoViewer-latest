import logging
import time
from typing import Dict, List, Optional

from app.models.phylo import (
    OrthologueSearchRequest, OrthologueSearchResponse,
    OrthologueData, OrthoSpeciesCount
)
from app.data_access.orthogroups_repository import OrthogroupsRepository
from app.data_access.species_repository import SpeciesRepository

logger = logging.getLogger(__name__)

class OrthologueService:
    """Service for orthologue-related operations"""
    
    def __init__(self):
        """Initialize the service with repositories"""
        self.orthogroups_repo = OrthogroupsRepository()
        self.species_repo = SpeciesRepository()

    async def search_orthologues(self, request: OrthologueSearchRequest) -> OrthologueSearchResponse:
        """Search for orthologues of a given gene"""
        gene_id = request.gene_id.strip()
        logger.info(f"Searching for orthologues of gene: {gene_id}")
        
        try:
            # Start timing the search
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
            
            # Process results
            start_time = time.time()
            
            # Prepare response data
            orthologues = []
            counts_by_species = []
            
            # Get all species from orthogroups data
            all_species = set(self.orthogroups_repo.get_species_columns())
            
            # Process each species
            for species_code in all_species:
                # Get full species name
                species_name = self.species_repo.get_species_full_name(species_code)
                
                # Get genes for this species
                species_genes = genes_by_species.get(species_code, [])
                
                # Add count for this species
                counts_by_species.append(
                    OrthoSpeciesCount(
                        species_id=species_code,
                        species_name=species_name,
                        count=len(species_genes)
                    )
                )
                
                # Add orthologue data for each gene
                for gene in species_genes:
                    if gene != gene_id:  # Don't include the query gene itself
                        orthologues.append(
                            OrthologueData(
                                gene_id=gene,
                                species_id=species_code,
                                species_name=species_name,
                                orthogroup_id=orthogroup_id
                            )
                        )
            
            # Sort orthologues by species name
            orthologues.sort(key=lambda x: x.species_name)
            
            # Get species tree
            species_tree = self.species_repo.load_species_tree()
            
            # Create response
            response = OrthologueSearchResponse(
                success=True,
                gene_id=gene_id,
                orthogroup_id=orthogroup_id,
                orthologues=orthologues,
                counts_by_species=counts_by_species,
                newick_tree=species_tree
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