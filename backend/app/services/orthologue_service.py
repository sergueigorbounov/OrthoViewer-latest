import logging
import time
from typing import Dict, List, Optional, Any

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
            
            # Get species tree
            species_tree = self.species_repo.load_species_tree()
            
            # Prepare response data
            orthologues = []
            counts_by_species = []
            
            # Get all species from orthogroups data
            all_species = set(self.orthogroups_repo.get_species_columns())
            
            # Process each species
            for species_id in all_species:
                species_name = self.species_repo.get_species_full_name(species_id)
                genes = genes_by_species.get(species_id, [])
                
                # Add to counts
                counts_by_species.append(OrthoSpeciesCount(
                    species_name=species_name,
                    species_id=species_id,
                    count=len(genes)
                ))
                
                # Add each gene as an orthologue
                for gene in genes:
                    orthologues.append(OrthologueData(
                        gene_id=gene,
                        species_name=species_name,
                        species_id=species_id,
                        orthogroup_id=orthogroup_id
                    ))
            
            process_time = time.time() - start_time
            logger.info(f"Time to process results: {process_time:.2f} seconds")
            
            # Create response
            response = OrthologueSearchResponse(
                success=True,
                gene_id=gene_id,
                orthogroup_id=orthogroup_id,
                orthologues=orthologues,
                counts_by_species=counts_by_species,
                newick_tree=species_tree
            )
            
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

    async def get_orthogroup_tree(self, orthogroup_id: str) -> Dict[str, Any]:
        """Get the phylogenetic tree for a specific orthogroup"""
        try:
            # Get the species tree
            species_tree = self.species_repo.load_species_tree()
            
            # Get all genes in the orthogroup
            genes_by_species = self.orthogroups_repo.get_orthogroup_genes(orthogroup_id)
            
            if not genes_by_species:
                return {
                    "success": False,
                    "message": f"Orthogroup {orthogroup_id} not found"
                }
            
            # Get species with genes in this orthogroup
            species_with_genes = set(genes_by_species.keys())
            
            return {
                "success": True,
                "orthogroup_id": orthogroup_id,
                "newick": species_tree,
                "species_with_genes": list(species_with_genes),
                "total_species": len(species_with_genes)
            }
            
        except Exception as e:
            logger.error(f"Error getting orthogroup tree: {str(e)}", exc_info=True)
            return {
                "success": False,
                "message": f"Error getting orthogroup tree: {str(e)}"
            }