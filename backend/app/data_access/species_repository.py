import os
import pandas as pd
import logging
from typing import Dict, Set, Optional
from fastapi import HTTPException
from app.models.biological_models import Species
from .mock_repository import MockRepository

logger = logging.getLogger(__name__)

class SpeciesRepository(MockRepository[Species]):
    """Repository for accessing species data."""
    
    def __init__(self):
        """Initialize the species repository."""
        super().__init__(
            model_class=Species,
            data_filename="species.json",
            id_field="id"
        )
        self.data_key = "species"
        
        # Initialize repository with data paths
        self.BASE_DIR = "/home/sgorbounov/Documents/orthoviewer2-clean"
        self.DATA_DIR = os.path.join(self.BASE_DIR, "data/orthofinder")
        self.SPECIES_MAPPING_FILE = os.path.join(self.DATA_DIR, "Table_S1_Metadata_angiosperm_species.csv")
        self.TREE_FILE = os.path.join(self.DATA_DIR, "SpeciesTree_nameSp_completeGenome110124.tree")
        
        # Cache
        self._species_mapping = None
        self._species_tree = None

    def load_species_mapping(self) -> Dict:
        """Load species mapping with correct file format handling"""
        if self._species_mapping is None:
            try:
                logger.info(f"Loading species mapping from {self.SPECIES_MAPPING_FILE}")
                
                # Load mapping file: skip header (first 2 lines), use tab separator
                mapping_df = pd.read_csv(self.SPECIES_MAPPING_FILE, sep='\t', skiprows=2)
                logger.info(f"Species mapping loaded successfully: {mapping_df.shape}")
                
                # Get column names for species full name and ID
                species_full_col = mapping_df.columns[0]  # Full species name
                species_id_col = mapping_df.columns[1]    # Species ID
                
                # Create mappings
                id_to_full = dict(zip(mapping_df[species_id_col], mapping_df[species_full_col]))
                full_to_id = dict(zip(mapping_df[species_full_col], mapping_df[species_id_col]))
                
                self._species_mapping = {
                    'id_to_full': id_to_full,
                    'full_to_id': full_to_id,
                    'newick_to_full': id_to_full.copy(),
                    'prefix_to_full': id_to_full.copy()
                }
                
            except Exception as e:
                logger.error(f"Failed to load species mapping: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Failed to load species mapping: {str(e)}")
        
        return self._species_mapping

    def load_species_tree(self) -> str:
        """Load species tree from Newick file"""
        if self._species_tree is None:
            try:
                logger.info(f"Loading species tree from {self.TREE_FILE}")
                with open(self.TREE_FILE, 'r') as f:
                    self._species_tree = f.read().strip()
                logger.info(f"Species tree loaded successfully: {len(self._species_tree)} characters")
            except Exception as e:
                logger.error(f"Failed to load species tree: {str(e)}")
                self._species_tree = "(A:0.1,B:0.2);"  # Minimal fallback tree
        
        return self._species_tree

    def get_species_full_name(self, species_code: str) -> str:
        """Get full species name from code with fallback to generated name"""
        mapping = self.load_species_mapping()
        
        # Try different mapping strategies
        for mapping_key in ['id_to_full', 'prefix_to_full', 'newick_to_full']:
            if species_code in mapping.get(mapping_key, {}):
                return mapping[mapping_key][species_code]
        
        # Generate fallback name if not found
        return self.generate_fallback_name(species_code)

    def generate_fallback_name(self, species_code: str) -> str:
        """Generate a reasonable fallback name for unmapped species codes"""
        genus_hints = {
            'A': ['Arabidopsis', 'Aegilops', 'Actinidia', 'Amaranthus', 'Acorus'],
            'B': ['Brassica', 'Beta', 'Bambusa'],
            'C': ['Citrus', 'Cannabis', 'Cucumis', 'Coffea', 'Camelina', 'Capsella'],
            'D': ['Daucus'],
            'E': ['Eucalyptus'],
            'F': ['Fragaria'],
            'G': ['Glycine', 'Gossypium'],
            'H': ['Helianthus', 'Hordeum'],
            'L': ['Lotus', 'Lupinus', 'Lactuca', 'Linum'],
            'M': ['Medicago', 'Malus', 'Musa', 'Manihot'],
            'N': ['Nicotiana', 'Nelumbo'],
            'O': ['Oryza', 'Olea'],
            'P': ['Populus', 'Pisum', 'Prunus', 'Panicum', 'Phaseolus'],
            'Q': ['Quercus'],
            'R': ['Ricinus'],
            'S': ['Solanum', 'Sorghum', 'Setaria', 'Sesamum'],
            'T': ['Triticum', 'Theobroma', 'Trifolium'],
            'V': ['Vigna', 'Vitis'],
            'W': ['Wheat line'],
            'Z': ['Zea']
        }
        
        if len(species_code) >= 1:
            first_letter = species_code[0].upper()
            if first_letter in genus_hints:
                possible_genera = genus_hints[first_letter]
                return f"{possible_genera[0]} sp. ({species_code})"
        
        return f"Species {species_code}"

    def enhance_species_mapping(self, ortho_species: Set[str]) -> Dict:
        """Enhance species mapping with fallback names for missing species"""
        mapping = self.load_species_mapping()
        enhanced = mapping['id_to_full'].copy()
        
        # Find missing species and create fallback mappings
        missing_species = ortho_species - set(enhanced.keys())
        logger.info(f"Found {len(missing_species)} species needing fallback mapping")
        
        for species_code in missing_species:
            enhanced[species_code] = self.generate_fallback_name(species_code)
        
        return enhanced

    def get_species_by_name(self, name: str) -> Optional[Species]:
        """Get a species by name.
        
        Args:
            name: Name of the species
            
        Returns:
            Species if found, None otherwise
        """
        all_species = self.get_all()
        for species in all_species:
            if species.name.lower() == name.lower():
                return species
        return None