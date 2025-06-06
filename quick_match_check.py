#!/usr/bin/env python3

import pandas as pd

def quick_check():
    print("🔍 Quick species matching check...")
    
    # Load orthogroups data to get species codes
    ortho_file = "data/orthofinder/Orthogroups_clean_121124.txt"
    df = pd.read_csv(ortho_file, sep='\t', dtype=str, keep_default_na=False, na_filter=False)
    
    # Get species columns (all except Orthogroup)
    species_codes = [col for col in df.columns if col != 'Orthogroup']
    print(f"Species codes from orthogroups ({len(species_codes)}):")
    print(sorted(species_codes))
    
    # Load species mapping
    mapping_file = "data/orthofinder/Table_S1_Metadata_angiosperm_species.csv"
    mapping_df = pd.read_csv(mapping_file)
    print(f"\nMapping file columns: {list(mapping_df.columns)}")
    
    # Get the species code column (need to check what it's called)
    if 'species_code' in mapping_df.columns:
        mapping_codes = set(mapping_df['species_code'].tolist())
    elif 'Species_code' in mapping_df.columns:
        mapping_codes = set(mapping_df['Species_code'].tolist())
    else:
        print("Available columns in mapping file:")
        print(mapping_df.columns.tolist())
        print("\nFirst few rows:")
        print(mapping_df.head())
        return
        
    print(f"\nSpecies codes from mapping ({len(mapping_codes)}):")
    print(sorted(mapping_codes))
    
    # Compare
    in_ortho_not_mapping = set(species_codes) - mapping_codes
    in_mapping_not_ortho = mapping_codes - set(species_codes)
    
    print(f"\nIn orthogroups but NOT in mapping ({len(in_ortho_not_mapping)}):")
    print(sorted(in_ortho_not_mapping))
    
    print(f"\nIn mapping but NOT in orthogroups ({len(in_mapping_not_ortho)}):")
    print(sorted(in_mapping_not_ortho))
    
    # Check what Ac maps to
    ac_mapping = mapping_df[mapping_df['species_code'] == 'Ac']
    if not ac_mapping.empty:
        print(f"\nAc maps to: {ac_mapping['species_name'].iloc[0]}")
    else:
        print(f"\nAc NOT found in mapping")

if __name__ == "__main__":
    quick_check() 