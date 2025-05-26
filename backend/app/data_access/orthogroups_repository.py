import os
import pandas as pd
import logging
from typing import Dict, List, Optional
from fastapi import HTTPException

from app.core.config import get_settings

# Configure logging
logger = logging.getLogger(__name__)
settings = get_settings()

class OrthogroupsRepository:
    """Repository for handling orthogroups data access"""
    
    def __init__(self):
        """Initialize the repository with data paths"""
        self.BASE_DIR = "/home/sgorbounov/Documents/orthoviewer2-clean"
        self.DATA_DIR = os.path.join(self.BASE_DIR, "data/orthofinder")
        self.ORTHOGROUPS_FILE = os.path.join(self.DATA_DIR, "Orthogroups_clean_121124.txt")
        
        # Cache
        self._orthogroups_data = None
        self._gene_map = {}

    def load_orthogroups_data(self) -> pd.DataFrame:
        """Load orthogroups data from CSV file"""
        if self._orthogroups_data is None:
            try:
                logger.info(f"Loading orthogroups data from {self.ORTHOGROUPS_FILE}")
                sep = '\t' if self.ORTHOGROUPS_FILE.endswith(('.tsv', '.txt')) else ','
                self._orthogroups_data = pd.read_csv(self.ORTHOGROUPS_FILE, sep=sep, low_memory=False)
                logger.info(f"Orthogroups data loaded successfully: {self._orthogroups_data.shape}")
                
                # Build gene mapping
                self._gene_map = self._build_gene_to_orthogroup_map()
                logger.info(f"Gene mapping built with {len(self._gene_map)} entries")
                
            except Exception as e:
                logger.error(f"Failed to load orthogroups data: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Failed to load orthogroups data: {str(e)}")
        
        return self._orthogroups_data

    def _build_gene_to_orthogroup_map(self) -> Dict[str, str]:
        """Build mapping from gene IDs to orthogroup IDs"""
        gene_map = {}
        df = self._orthogroups_data
        
        for _, row in df.iterrows():
            orthogroup_id = row[df.columns[0]]
            for col in df.columns[1:]:
                cell_value = row[col]
                if isinstance(cell_value, str) and cell_value.strip():
                    genes = [g.strip() for g in cell_value.split(',')]
                    for gene in genes:
                        gene_map[gene] = orthogroup_id
        
        return gene_map

    def get_orthogroup_genes(self, orthogroup_id: str) -> Dict[str, List[str]]:
        """Get all genes in an orthogroup, organized by species"""
        df = self.load_orthogroups_data()
        
        # Find row with this orthogroup ID
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

    def find_gene_orthogroup(self, gene_id: str) -> Optional[str]:
        """Find orthogroup ID for a given gene"""
        self.load_orthogroups_data()  # Ensure data is loaded
        return self._gene_map.get(gene_id)

    def get_species_columns(self) -> List[str]:
        """Get list of all species columns from orthogroups data"""
        df = self.load_orthogroups_data()
        return df.columns[1:].tolist()  # Skip first column (orthogroup ID)

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