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
    
    async def estimate_search_total(self, query: str) -> int:
        """Estimate total number of results for a search query (expensive operation)"""
        if not self._gene_map:
            self.load_orthogroups_data()
        
        query_lower = query.lower()
        count = 0
        
        for gene_id in self._gene_map.keys():
            if query_lower in gene_id.lower():
                count += 1
        
        return count
    
    async def search_genes_optimized(self, query: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Optimized search for genes with better performance for large datasets"""
        if not self._gene_map:
            self.load_orthogroups_data()
        
        # Use generator for memory efficiency
        def gene_generator():
            query_lower = query.lower()
            for gene_id, orthogroup_id in self._gene_map.items():
                if query_lower in gene_id.lower():
                    yield {
                        "gene_id": gene_id,
                        "orthogroup_id": orthogroup_id
                    }
        
        # Skip to offset and take limit
        results = []
        for i, gene_data in enumerate(gene_generator()):
            if i < offset:
                continue
            if len(results) >= limit:
                break
            results.append(gene_data)
        
        return results
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "data_loaded": self._data is not None,
            "data_shape": self._data.shape if self._data is not None else None,
            "gene_map_size": len(self._gene_map),
            "file_path": self.orthogroups_file
        }
    
    async def get_orthogroup_basic_info(self, orthogroup_id: str) -> Optional[Dict[str, Any]]:
        """Get basic orthogroup info quickly for preview (< 50ms target)"""
        try:
            # Ultra-fast path: use cached data if available
            if self._data is None:
                # Load minimal data for speed
                self.load_orthogroups_data(page=1, per_page=1000)
            
            if self._data is None or self._data.empty:
                return None
            
            # Find the orthogroup row using vectorized operations
            mask = self._data.iloc[:, 0] == orthogroup_id
            orthogroup_rows = self._data[mask]
            
            if orthogroup_rows.empty:
                return None
            
            # Get first row and count quickly
            row = orthogroup_rows.iloc[0]
            species_with_genes = []
            total_genes = 0
            
            # Fast counting - only process non-empty cells
            for col in self._data.columns[1:]:  # Skip orthogroup ID column
                cell_value = row[col]
                if isinstance(cell_value, str) and cell_value.strip():
                    species_with_genes.append(col)
                    # Quick gene count (don't split, just estimate)
                    gene_count = cell_value.count(',') + 1
                    total_genes += gene_count
            
            # Generate a simple tree string for instant display
            if len(species_with_genes) > 2:
                # Create a minimal balanced tree structure
                species_list = species_with_genes[:min(10, len(species_with_genes))]  # Limit for speed
                if len(species_list) == 3:
                    simple_newick = f"(({species_list[0]},{species_list[1]}),{species_list[2]});"
                elif len(species_list) >= 4:
                    # Simple binary tree structure
                    left_half = species_list[:len(species_list)//2]
                    right_half = species_list[len(species_list)//2:]
                    left_part = ",".join(left_half)
                    right_part = ",".join(right_half)
                    simple_newick = f"(({left_part}),({right_part}));"
                else:
                    simple_newick = f"({','.join(species_list)});"
            else:
                simple_newick = f"({','.join(species_with_genes)});" if species_with_genes else None
            
            return {
                "orthogroup_id": orthogroup_id,
                "species_count": len(species_with_genes),
                "gene_count": total_genes,
                "has_tree": len(species_with_genes) > 2,
                "simple_newick": simple_newick,  # Add instant tree
                "species_list": species_with_genes[:20]  # First 20 for quick display
            }
            
        except Exception as e:
            logger.error(f"Error getting basic info for orthogroup {orthogroup_id}: {e}")
            return None
