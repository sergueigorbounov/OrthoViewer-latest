"""
Configuration settings for the application
"""

import os
from typing import Dict, Any

class Settings:
    """Application settings"""
    
    def __init__(self):
        # Data paths - dynamically determine based on current working directory
        # Get the actual project root (4 levels up from this config file)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        
        self.BASE_DIR = project_root
        self.DATA_DIR = os.path.join(self.BASE_DIR, "data", "orthofinder")
        self.TREE_FILE = os.path.join(self.DATA_DIR, "SpeciesTree_nameSp_completeGenome110124.tree")
        self.ORTHOGROUPS_FILE = os.path.join(self.DATA_DIR, "Orthogroups_clean_121124.txt")
        self.SPECIES_MAPPING_FILE = os.path.join(self.DATA_DIR, "Table_S1_Metadata_angiosperm_species.csv")
        
        # API settings
        self.API_HOST = "0.0.0.0"
        self.API_PORT = 8003
        
        # Performance settings
        self.DEFAULT_PAGE_SIZE = 100
        self.MAX_PAGE_SIZE = 1000

def get_settings() -> Settings:
    """Get application settings"""
    return Settings() 