"""
Helper module for efficiently finding genes in orthologues data
"""
import logging
import pandas as pd
from typing import Dict, Optional

# Configure logging
logger = logging.getLogger(__name__)

# Gene to orthogroup mapping
_gene_to_orthogroup_map = {}

def build_gene_to_orthogroup_map(df: pd.DataFrame) -> Dict[str, str]:
    """Build a mapping from gene IDs to orthogroup IDs for faster lookups"""
    gene_map = {}
    orthogroup_col = df.columns[0]
    
    try:
        logger.info("Building gene-to-orthogroup mapping cache...")
        # Process each row in the dataframe
        for idx, row in df.iterrows():
            if idx % 1000 == 0:
                logger.debug(f"Processing row {idx}/{len(df)}")
                
            orthogroup_id = str(row[orthogroup_col])
            
            # Process each species column
            for col in df.columns[1:]:
                cell_value = row[col]
                if not isinstance(cell_value, str) or not cell_value.strip():
                    continue
                    
                # Process each gene in the cell
                for gene in cell_value.split(','):
                    gene = gene.strip()
                    if gene:
                        gene_map[gene] = orthogroup_id
        
        logger.info(f"Successfully built gene-to-orthogroup map with {len(gene_map)} entries")
        return gene_map
    except Exception as e:
        logger.error(f"Error building gene-to-orthogroup map: {str(e)}")
        return {}

def find_gene_orthogroup(gene_id: str, gene_map: Dict[str, str], df: pd.DataFrame) -> Optional[str]:
    """Find orthogroup for a gene using the prebuilt mapping"""
    # First, try to find the gene in the prebuilt mapping (fast path)
    if gene_id in gene_map:
        logger.info(f"Found gene {gene_id} in orthogroup {gene_map[gene_id]} using cached mapping")
        return gene_map[gene_id]
    
    # If not found in the map, fall back to the slower method
    logger.info(f"Gene {gene_id} not found in cache, using fallback search")
    
    # Rechercher le gène dans toutes les colonnes
    for col in df.columns:
        # Ignorer la colonne ID d'orthogroupe (supposée être la première colonne)
        if col == df.columns[0]:
            continue
            
        # Vérifier si le gène est dans cette colonne (espèce)
        if df[col].dtype == 'object':  # Vérifier que la colonne contient des chaînes de caractères
            # Check for exact match by splitting on commas and comparing
            mask = df[col].apply(lambda x: isinstance(x, str) and gene_id in [g.strip() for g in str(x).split(',')])
            if mask.any():
                # Retourner l'ID d'orthogroupe pour la ligne correspondante
                result = str(df.loc[mask, df.columns[0]].iloc[0])
                logger.info(f"Found gene {gene_id} in orthogroup {result} using fallback search")
                
                # Add to cache for future lookups
                gene_map[gene_id] = result
                return result
    
    logger.info(f"Gene {gene_id} not found in any orthogroup")
    return None