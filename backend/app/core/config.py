"""
Configuration settings for the application
"""

import os
from typing import Dict, Any

class Settings:
    """Application settings"""
    
    def __init__(self):
        # Data paths
        self.BASE_DIR = "/home/sgorbounov/Documents/orthoviewer2-clean_backup_20250528_134020"
        self.DATA_DIR = os.path.join(self.BASE_DIR, "data/orthofinder")
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