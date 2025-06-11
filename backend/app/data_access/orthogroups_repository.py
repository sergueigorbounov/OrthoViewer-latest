"""
Orthogroups Repository - Data Access Layer
==========================================

Repository for accessing orthogroup data.
"""

import logging
import pandas as pd
import os
from typing import Dict, List, Optional, Any, Tuple
from ..core.config import get_settings

logger = logging.getLogger(__name__)

class OrthogroupsRepository:
    """Repository for orthogroup data access"""
    
    def __init__(self):
        """Initialize the repository"""
        self._data = None
        self._gene_map = {}
        
        # Use centralized configuration for consistent path handling
        settings = get_settings()
        data_dir = settings.DATA_DIR
        
        # Try files in order of preference, including paths from configuration
        potential_files = [
            settings.ORTHOGROUPS_FILE,  # Primary file from config
            os.path.join(data_dir, "Orthogroups_clean_121124_sample.csv"),  # Sample file
            os.path.join(data_dir, "Orthogroups.tsv")  # Fallback
        ]
        
        self.orthogroups_file = None
        for file_path in potential_files:
            if os.path.exists(file_path):
                self.orthogroups_file = file_path
                logger.info(f"Using orthogroups file: {file_path}")
                break
        
        if not self.orthogroups_file:
            logger.warning(f"No orthogroups file found. Tried: {potential_files}")
    
    def load_orthogroups_data(self, page: int = 1, per_page: int = 100) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Load orthogroups data with pagination"""
        try:
            if not self.orthogroups_file or not os.path.exists(self.orthogroups_file):
                logger.warning("No valid orthogroups file available")
                return pd.DataFrame(), {"page": page, "per_page": per_page, "total": 0, "pages": 0}
            
            # Load data if not already cached
            if self._data is None:
                logger.info(f"Loading orthogroups data from {self.orthogroups_file}")
                
                # All orthogroups files are tab-separated, regardless of extension
                # This is because orthofinder output is consistently tab-delimited
                sep = '\t'
                
                # Load the data
                self._data = pd.read_csv(
                    self.orthogroups_file,
                    sep=sep,
                    low_memory=False,
                    dtype=str,  # Treat all columns as strings
                    na_filter=False,  # Don't convert empty strings to NaN
                    keep_default_na=False  # Keep empty strings as empty strings
                )
                
                logger.info(f"Orthogroups data loaded successfully: {self._data.shape}")
                logger.info(f"Columns: {self._data.columns.tolist()}")
                
                # Build gene mapping for faster lookups
                self._build_gene_map()
            
            # Handle pagination
            total_rows = len(self._data)
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            
            paginated_data = self._data.iloc[start_idx:end_idx]
            
            pagination = {
                "page": page,
                "per_page": per_page,
                "total": total_rows,
                "pages": (total_rows + per_page - 1) // per_page
            }
            
            return paginated_data, pagination
            
        except Exception as e:
            logger.error(f"Error loading orthogroups data: {e}")
            raise
    
    def _build_gene_map(self):
        """Build gene-to-orthogroup mapping for faster lookups"""
        if self._data is None or self._data.empty:
            return
        
        try:
            logger.info("Building gene-to-orthogroup mapping...")
            self._gene_map = {}
            orthogroup_col = self._data.columns[0]  # First column is orthogroup ID
            
            for _, row in self._data.iterrows():
                orthogroup_id = row[orthogroup_col]
                
                # Process each species column
                for col in self._data.columns[1:]:
                    cell_value = row[col]
                    if isinstance(cell_value, str) and cell_value.strip():
                        # Split genes by comma and clean them
                        genes = [gene.strip() for gene in cell_value.split(',') if gene.strip()]
                        for gene in genes:
                            self._gene_map[gene] = orthogroup_id
            
            logger.info(f"Gene mapping built with {len(self._gene_map)} entries")
            
        except Exception as e:
            logger.error(f"Error building gene mapping: {e}")
    
    def find_gene_orthogroup(self, gene_id: str) -> Optional[str]:
        """Find which orthogroup a gene belongs to"""
        if not self._gene_map:
            # Try to load data if not already loaded
            self.load_orthogroups_data()
        
        return self._gene_map.get(gene_id)
    
    def get_orthogroup_genes(self, orthogroup_id: str) -> Dict[str, List[str]]:
        """Get all genes in an orthogroup organized by species"""
        if self._data is None:
            self.load_orthogroups_data()
        
        if self._data is None or self._data.empty:
            return {}
        
        # Find the row with this orthogroup
        orthogroup_row = self._data[self._data[self._data.columns[0]] == orthogroup_id]
        
        if orthogroup_row.empty:
            return {}
        
        # Extract genes by species
        genes_by_species = {}
        for col in self._data.columns[1:]:  # Skip orthogroup ID column
            cell_value = orthogroup_row[col].iloc[0]
            if isinstance(cell_value, str) and cell_value.strip():
                genes = [gene.strip() for gene in cell_value.split(',') if gene.strip()]
                if genes:
                    genes_by_species[col] = genes
        
        return genes_by_species
    
    def get_species_columns(self) -> List[str]:
        """Get list of species column names"""
        if self._data is None:
            self.load_orthogroups_data()
        
        if self._data is None or self._data.empty:
            return []
        
        # Return all columns except the first one (orthogroup ID)
        return self._data.columns[1:].tolist()
    
    async def get_gene_info(self, gene_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific gene"""
        orthogroup_id = self.find_gene_orthogroup(gene_id)
        if orthogroup_id:
            return {
                "gene_id": gene_id,
                "orthogroup_id": orthogroup_id
            }
        return None
    
    async def get_orthogroup_info(self, orthogroup_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific orthogroup"""
        genes_by_species = self.get_orthogroup_genes(orthogroup_id)
        if genes_by_species:
            total_genes = sum(len(genes) for genes in genes_by_species.values())
            return {
                "orthogroup_id": orthogroup_id,
                "species_count": len(genes_by_species),
                "total_genes": total_genes,
                "genes_by_species": genes_by_species
            }
        return None
    
    async def search_genes(self, query: str, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """Search for genes by name or ID"""
        if not self._gene_map:
            self.load_orthogroups_data()
        
        # Search through gene IDs that contain the query
        matching_genes = []
        query_lower = query.lower()
        
        for gene_id, orthogroup_id in self._gene_map.items():
            if query_lower in gene_id.lower():
                matching_genes.append({
                    "gene_id": gene_id,
                    "orthogroup_id": orthogroup_id
                })
                
                if len(matching_genes) >= offset + limit:
                    break
        
        # Apply pagination
        return matching_genes[offset:offset + limit]
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "data_loaded": self._data is not None,
            "data_shape": self._data.shape if self._data is not None else None,
            "gene_map_size": len(self._gene_map),
            "file_path": self.orthogroups_file
        }
