#!/usr/bin/env python3

import sys
import os
sys.path.append('backend')

from app.data_access.species_repository import SpeciesRepository

def test_species_mapping():
    print("Testing species mapping...")
    
    repo = SpeciesRepository()
    print(f"Data dir: {repo.data_dir}")
    print(f"Data dir exists: {os.path.exists(repo.data_dir)}")
    
    metadata_file = os.path.join(repo.data_dir, 'Table_S1_Metadata_angiosperm_species.csv')
    print(f"Metadata file: {metadata_file}")
    print(f"Metadata file exists: {os.path.exists(metadata_file)}")
    
    if os.path.exists(metadata_file):
        import pandas as pd
        try:
            print("Loading CSV...")
            df = pd.read_csv(metadata_file, skiprows=1)
            print(f"Loaded {len(df)} rows")
            print(f"Columns: {df.columns.tolist()}")
            if len(df) > 0:
                print(f"First few IDs: {df['ID'].head().tolist()}")
                print(f"First few Species: {df['Species'].head().tolist()}")
        except Exception as e:
            print(f"Error loading CSV: {e}")
    
    print("\nLoading through repository...")
    try:
        mapping = repo.load_species_mapping()
        print(f"Mapping keys: {list(mapping.keys())}")
        print(f"ID to full mapping size: {len(mapping.get('id_to_full', {}))}")
        if mapping.get('id_to_full'):
            sample_items = list(mapping['id_to_full'].items())[:5]
            print(f"Sample mappings: {sample_items}")
    except Exception as e:
        print(f"Error loading mapping: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_species_mapping() 