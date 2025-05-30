import os
import pandas as pd
import logging
from typing import Dict, List, Optional, Tuple
from fastapi import HTTPException
from functools import lru_cache
from app.core.config import get_settings

# Configure logging
logger = logging.getLogger(__name__)
settings = get_settings()

class OrthogroupsRepository:
    """Repository for handling orthogroups data access with optimized loading"""
    
    def __init__(self):
        """Initialize the repository with data paths"""
        self.BASE_DIR = "/home/sgorbounov/Documents/orthoviewer2-clean"
        self.DATA_DIR = os.path.join(self.BASE_DIR, "data/orthofinder")
        self.ORTHOGROUPS_FILE = os.path.join(self.DATA_DIR, "Orthogroups_clean_121124.txt")
        
        # Chunk size for data loading (adjust based on your memory constraints)
        self.CHUNK_SIZE = 1000
        
        # Cache
        self._orthogroups_chunks = {}
        self._gene_map = {}
        self._total_chunks = None

    @lru_cache(maxsize=128)
    def get_chunk(self, chunk_index: int) -> pd.DataFrame:
        """Get a specific chunk of data with caching"""
        if chunk_index not in self._orthogroups_chunks:
            try:
                sep = '\t' if self.ORTHOGROUPS_FILE.endswith(('.tsv', '.txt')) else ','
                skip_rows = chunk_index * self.CHUNK_SIZE
                
                # Read only the chunk we need
                chunk = pd.read_csv(
                    self.ORTHOGROUPS_FILE,
                    sep=sep,
                    skiprows=skip_rows,
                    nrows=self.CHUNK_SIZE,
                    low_memory=False,
                    dtype=str,  # Optimize memory usage
                    na_filter=False  # Don't convert empty strings to NaN
                )
                
                self._orthogroups_chunks[chunk_index] = chunk
                logger.info(f"Loaded chunk {chunk_index} successfully")
                
            except Exception as e:
                logger.error(f"Failed to load chunk {chunk_index}: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Failed to load chunk {chunk_index}: {str(e)}")
                
        return self._orthogroups_chunks[chunk_index]

    def get_total_chunks(self) -> int:
        """Get total number of chunks in the dataset"""
        if self._total_chunks is None:
            try:
                # Count lines in file efficiently
                with open(self.ORTHOGROUPS_FILE) as f:
                    total_lines = sum(1 for _ in f) - 1  # Subtract header
                self._total_chunks = (total_lines + self.CHUNK_SIZE - 1) // self.CHUNK_SIZE
            except Exception as e:
                logger.error(f"Failed to count total chunks: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
        return self._total_chunks

    def load_orthogroups_data(self, page: int = 1, per_page: int = 100) -> Tuple[pd.DataFrame, dict]:
        """Load orthogroups data with pagination"""
        try:
            # Calculate which chunks we need for this page
            start_index = (page - 1) * per_page
            chunk_start = start_index // self.CHUNK_SIZE
            chunk_end = (start_index + per_page + self.CHUNK_SIZE - 1) // self.CHUNK_SIZE
            
            # Load required chunks
            chunks = []
            for i in range(chunk_start, chunk_end):
                if i >= self.get_total_chunks():
                    break
                chunks.append(self.get_chunk(i))
            
            if not chunks:
                return pd.DataFrame(), {"total": 0, "page": page, "per_page": per_page, "pages": 0}
            
            # Combine chunks and extract the requested page
            combined_df = pd.concat(chunks, ignore_index=True)
            start_offset = start_index % self.CHUNK_SIZE
            result_df = combined_df.iloc[start_offset:start_offset + per_page]
            
            # Build gene mapping for this chunk if needed
            if not self._gene_map:
                self._gene_map = self._build_gene_to_orthogroup_map(result_df)
            
            total_records = self.get_total_chunks() * self.CHUNK_SIZE
            total_pages = (total_records + per_page - 1) // per_page
            
            pagination = {
                "total": total_records,
                "page": page,
                "per_page": per_page,
                "pages": total_pages
            }
            
            return result_df, pagination
            
        except Exception as e:
            logger.error(f"Failed to load orthogroups data: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to load orthogroups data: {str(e)}")

    def _build_gene_to_orthogroup_map(self, df: pd.DataFrame) -> Dict[str, str]:
        """Build gene to orthogroup mapping for faster lookups"""
        gene_map = {}
        for idx, row in df.iterrows():
            orthogroup_id = row.get('Orthogroup')
            if orthogroup_id:
                for gene in row.dropna().values[1:]:  # Skip orthogroup column
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