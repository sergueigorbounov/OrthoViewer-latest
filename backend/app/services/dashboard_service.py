from typing import Dict, Any, List
from collections import defaultdict

from app.models.biological_models import DashboardResponse, DashboardData
from app.data_access.species_repository import SpeciesRepository
from app.data_access.orthogroup_repository import OrthoGroupRepository
from app.data_access.gene_repository import GeneRepository


class DashboardService:
    """Service for generating dashboard data."""
    
    def __init__(self):
        """Initialize the dashboard service."""
        self.species_repository = SpeciesRepository()
        self.orthogroup_repository = OrthoGroupRepository()
        self.gene_repository = GeneRepository()
    
    def get_dashboard_stats(self) -> DashboardResponse:
        """Get dashboard statistics.
        
        Returns:
            Response containing dashboard statistics
        """
        try:
            # Get data from repositories
            species_list = self.species_repository.get_all()
            orthogroups_list = self.orthogroup_repository.get_all()
            genes_list = self.gene_repository.get_all()
            
            # Calculate basic counts
            species_count = len(species_list)
            orthogroup_count = len(orthogroups_list)
            gene_count = len(genes_list)
            
            # Calculate species with most genes
            species_gene_counts = defaultdict(int)
            species_names = {s.id: s.name for s in species_list}
            
            for gene in genes_list:
                if gene.species_id:
                    species_gene_counts[gene.species_id] += 1
            
            species_distribution = [
                {"name": species_names.get(sp_id, sp_id), "value": count}
                for sp_id, count in sorted(species_gene_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            ]
            
            # Calculate genes by orthogroup
            orthogroup_gene_counts = defaultdict(int)
            orthogroup_names = {og.id: og.name for og in orthogroups_list}
            
            for gene in genes_list:
                orthogroup_id = gene.orthogroup_id
                if orthogroup_id:
                    orthogroup_gene_counts[orthogroup_id] += 1
            
            genes_by_orthogroup = [
                {"name": orthogroup_names.get(og_id, og_id), "genes": count}
                for og_id, count in sorted(orthogroup_gene_counts.items(), key=lambda x: x[1], reverse=True)[:8]
            ]
            
            # Calculate orthogroup connectivity (how many species an orthogroup spans)
            orthogroup_species = defaultdict(set)
            for gene in genes_list:
                species_id = gene.species_id
                orthogroup_id = gene.orthogroup_id
                if species_id and orthogroup_id:
                    orthogroup_species[orthogroup_id].add(species_id)
            
            orthogroup_connectivity = [
                {"name": orthogroup_names.get(og_id, og_id), "value": len(species)}
                for og_id, species in sorted(orthogroup_species.items(), key=lambda x: len(x[1]), reverse=True)[:5]
            ]
            
            # Count GO terms by category
            go_term_counts = {"Molecular Function": 0, "Biological Process": 0, "Cellular Component": 0}
            for gene in genes_list:
                if gene.go_terms:
                    for go_term in gene.go_terms:
                        category = go_term.category
                        if category in go_term_counts:
                            go_term_counts[category] += 1
            
            # Create dashboard data
            dashboard_data = DashboardData(
                speciesCount=species_count,
                orthogroupCount=orthogroup_count,
                geneCount=gene_count,
                annotationCount=sum(go_term_counts.values()),
                speciesDistribution=species_distribution,
                genesByOrthogroup=genes_by_orthogroup,
                orthogroupConnectivity=orthogroup_connectivity,
                taxonomyDistribution=[
                    {"name": "Plant", "value": 35},
                    {"name": "Fungi", "value": 25},
                    {"name": "Bacteria", "value": 20},
                    {"name": "Animal", "value": 15},
                    {"name": "Other", "value": 5}
                ],
                goTermDistribution=go_term_counts
            )
            
            return DashboardResponse(
                success=True,
                data=dashboard_data
            )
        
        except Exception as e:
            return DashboardResponse(
                success=False,
                message=f"Failed to generate dashboard stats: {str(e)}",
                data=DashboardData()
            )