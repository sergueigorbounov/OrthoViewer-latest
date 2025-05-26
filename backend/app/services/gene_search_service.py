import pandas as pd
from typing import Dict, Any, List, Optional
import os
import json

from app.core.config import get_settings

settings = get_settings()

class GeneSearchService:
    """Service for efficient gene searching."""
    
    def __init__(self):
        """Initialize the gene search service with data."""
        self.genes_df = None
        self.orthogroups_df = None
        self.species_df = None
        self._load_data()
    
    def _load_data(self):
        """Load data into pandas DataFrames for efficient searching."""
        # Load genes
        genes_data = self._load_json_file("genes.json")
        if genes_data and "genes" in genes_data:
            self.genes_df = pd.DataFrame(genes_data["genes"])
            if not self.genes_df.empty and "id" in self.genes_df.columns:
                self.genes_df.set_index("id", inplace=True)
        
        # Load orthogroups
        orthogroups_data = self._load_json_file("orthogroups.json")
        if orthogroups_data and "orthogroups" in orthogroups_data:
            self.orthogroups_df = pd.DataFrame(orthogroups_data["orthogroups"])
            if not self.orthogroups_df.empty and "id" in self.orthogroups_df.columns:
                self.orthogroups_df.set_index("id", inplace=True)
        
        # Load species
        species_data = self._load_json_file("species.json")
        if species_data and "species" in species_data:
            self.species_df = pd.DataFrame(species_data["species"])
            if not self.species_df.empty and "id" in self.species_df.columns:
                self.species_df.set_index("id", inplace=True)
    
    def _load_json_file(self, filename: str) -> Dict[str, Any]:
        """Load a JSON file from the mock data directory."""
        try:
            file_path = os.path.join(settings.MOCK_DATA_DIR, filename)
            with open(file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
            print(f"Error loading {filename}: {str(e)}")
            return {}
    
    def get_gene_by_id(self, gene_id: str) -> Dict[str, Any]:
        """Get a gene by its ID."""
        try:
            if self.genes_df is None or self.genes_df.empty:
                return {
                    "success": False,
                    "message": "Gene data not loaded",
                    "data": None
                }
            
            if gene_id in self.genes_df.index:
                gene = self.genes_df.loc[gene_id].to_dict()
                
                # Convert any Series objects to lists
                for key, value in gene.items():
                    if isinstance(value, pd.Series):
                        gene[key] = value.tolist()
                
                return {
                    "success": True,
                    "data": gene
                }
            else:
                return {
                    "success": False,
                    "message": f"Gene with ID {gene_id} not found",
                    "data": None
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to retrieve gene: {str(e)}",
                "data": None
            }
    
    def get_genes_by_orthogroup(self, orthogroup_id: str) -> Dict[str, Any]:
        """Get all genes for a specific orthogroup."""
        try:
            if self.genes_df is None or self.genes_df.empty:
                return {
                    "success": False,
                    "message": "Gene data not loaded",
                    "data": [],
                    "orthogroup_id": orthogroup_id
                }
            
            # First check if the orthogroup exists
            if self.orthogroups_df is not None and not self.orthogroups_df.empty:
                if orthogroup_id not in self.orthogroups_df.index:
                    return {
                        "success": False,
                        "message": f"Orthogroup with ID {orthogroup_id} not found",
                        "data": [],
                        "orthogroup_id": orthogroup_id
                    }
            
            # Filter genes by orthogroup_id
            filtered_genes = self.genes_df[self.genes_df["orthogroup_id"] == orthogroup_id]
            
            if filtered_genes.empty:
                return {
                    "success": True,
                    "data": [],
                    "orthogroup_id": orthogroup_id
                }
            
            # Convert DataFrame to list of dicts
            genes_list = filtered_genes.reset_index().to_dict(orient="records")
            
            return {
                "success": True,
                "data": genes_list,
                "orthogroup_id": orthogroup_id
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to retrieve genes: {str(e)}",
                "data": [],
                "orthogroup_id": orthogroup_id
            }
    
    def get_genes_by_species(self, species_id: str) -> Dict[str, Any]:
        """Get all genes for a specific species."""
        try:
            if self.genes_df is None or self.genes_df.empty:
                return {
                    "success": False,
                    "message": "Gene data not loaded",
                    "data": [],
                    "species_id": species_id
                }
            
            # Filter genes by species_id
            filtered_genes = self.genes_df[self.genes_df["species_id"] == species_id]
            
            if filtered_genes.empty:
                return {
                    "success": True,
                    "data": [],
                    "species_id": species_id
                }
            
            # Convert DataFrame to list of dicts
            genes_list = filtered_genes.reset_index().to_dict(orient="records")
            
            return {
                "success": True,
                "data": genes_list,
                "species_id": species_id
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to retrieve genes: {str(e)}",
                "data": [],
                "species_id": species_id
            }
    
    def search_genes(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search for genes by name or ID."""
        try:
            if self.genes_df is None or self.genes_df.empty:
                return {
                    "success": False,
                    "message": "Gene data not loaded",
                    "data": []
                }
            
            # Search in ID and name
            mask_id = self.genes_df.index.str.contains(query, case=False)
            mask_name = self.genes_df["name"].str.contains(query, case=False)
            
            # Combine the masks with OR
            filtered_genes = self.genes_df[mask_id | mask_name]
            
            if filtered_genes.empty:
                return {
                    "success": True,
                    "data": [],
                    "query": query
                }
            
            # Limit results
            filtered_genes = filtered_genes.head(limit)
            
            # Convert DataFrame to list of dicts
            genes_list = filtered_genes.reset_index().to_dict(orient="records")
            
            return {
                "success": True,
                "data": genes_list,
                "query": query
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to search genes: {str(e)}",
                "data": [],
                "query": query
            }