import pandas as pd
import os
import logging
from typing import Dict, List, Optional, Any, Set

from app.core.config import get_settings

# Configure logging
logger = logging.getLogger(__name__)
settings = get_settings()

class OrthogroupsRepository:
    """Repository for accessing orthogroups data."""
    
    def __init__(self):
        """Initialize the repository."""
        self._orthogroups_data = None
        self._gene_map = {}
    
    def load_orthogroups_data(self) -> pd.DataFrame:
        """Load orthogroups data from file."""
        if self._orthogroups_data is None:
            try:
                filepath = settings.ORTHOGROUPS_FILE
                logger.info(f"Loading orthogroups data from {filepath}")
                
                # Determine separator based on file extension
                sep = '\t' if filepath.endswith('.tsv') or filepath.endswith('.txt') else ','
                self._orthogroups_data = pd.read_csv(filepath, sep=sep, low_memory=False)
                
                logger.info(f"Orthogroups data loaded successfully: {self._orthogroups_data.shape}")
                logger.info(f"Columns: {self._orthogroups_data.columns.tolist()}")
                logger.info(f"Sample: \n{self._orthogroups_data.head(2)}")
                
                # Build the gene-to-orthogroup mapping for faster lookups
                self._gene_map = self._build_gene_to_orthogroup_map(self._orthogroups_data)
                logger.info(f"Gene mapping built with {len(self._gene_map)} entries")
            except Exception as e:
                logger.error(f"Failed to load orthogroups data: {str(e)}")
                raise Exception(f"Failed to load orthogroups data: {str(e)}")
        
        return self._orthogroups_data
    
    def _build_gene_to_orthogroup_map(self, df: pd.DataFrame) -> Dict[str, str]:
        """Build a map of gene IDs to orthogroup IDs for fast lookups."""
        gene_map = {}
        orthogroup_col = df.columns[0]
        
        # Process each row (orthogroup)
        for _, row in df.iterrows():
            orthogroup_id = row[orthogroup_col]
            
            # Process each species column
            for col in df.columns[1:]:
                cell_value = row[col]
                if isinstance(cell_value, str) and cell_value.strip():
                    # Split comma-separated genes and map each to this orthogroup
                    genes = [gene.strip() for gene in cell_value.split(',')]
                    for gene in genes:
                        if gene:
                            gene_map[gene] = orthogroup_id
        
        return gene_map
    
    def find_gene_orthogroup(self, gene_id: str) -> Optional[str]:
        """Find orthogroup ID for a given gene."""
        # Make sure data is loaded
        self.load_orthogroups_data()
        
        # Direct lookup in the gene map
        return self._gene_map.get(gene_id)
    
    def get_orthogroup_genes(self, orthogroup_id: str) -> Dict[str, List[str]]:
        """Get all genes in an orthogroup, organized by species."""
        df = self.load_orthogroups_data()
        
        # Find the row with this orthogroup ID
        orthogroup_row = df[df[df.columns[0]] == orthogroup_id]
        if orthogroup_row.empty:
            return {}
        
        # Extract genes by species
        genes_by_species = {}
        for col in df.columns[1:]:  # Skip orthogroup ID column
            cell_value = orthogroup_row[col].iloc[0]
            if isinstance(cell_value, str) and cell_value.strip():
                genes = [gene.strip() for gene in cell_value.split(',')]
                genes_by_species[col] = genes
        
        return genes_by_species
    
    def get_all_species_codes(self) -> List[str]:
        """Get all species codes from the orthogroups data."""
        df = self.load_orthogroups_data()
        return df.columns[1:].tolist()  # Skip orthogroup ID column
    
    def get_orthogroup_count(self) -> int:
        """Get the total number of orthogroups."""
        df = self.load_orthogroups_data()
        return len(df)
    
    def get_gene_count_by_species(self) -> Dict[str, int]:
        """Get the count of genes for each species."""
        df = self.load_orthogroups_data()
        gene_counts = {}
        
        for col in df.columns[1:]:  # Skip orthogroup ID column
            gene_counts[col] = 0
            for _, row in df.iterrows():
                cell_value = row[col]
                if isinstance(cell_value, str) and cell_value.strip():
                    genes = [gene.strip() for gene in cell_value.split(',') if gene.strip()]
                    gene_counts[col] += len(genes)
        
        return gene_counts