#!/usr/bin/env python3

import sys
import os
sys.path.append('backend')

import pandas as pd

def debug_gene_indexing():
    print("=== Debugging Gene Indexing (Simple) ===\n")
    
    print("1. Testing direct file reading...")
    try:
        file_path = "data/orthofinder/Orthogroups_clean_121124_sample.csv"
        df = pd.read_csv(file_path)
        print(f"   Direct file read shape: {df.shape}")
        print(f"   Columns: {list(df.columns)}")
        print(f"   First orthogroup: {df.iloc[0, 0]}")
        print(f"   First row, second column: {df.iloc[0, 1]}")
        print(f"   Type: {type(df.iloc[0, 1])}")
        
        # Test gene splitting on first cell
        cell_value = df.iloc[0, 1]
        if isinstance(cell_value, str):
            genes = [gene.strip() for gene in cell_value.split(',') if gene.strip()]
            print(f"   Split into {len(genes)} genes")
            print(f"   First 5 genes: {genes[:5]}")
        else:
            print(f"   Cell is not a string: {cell_value}")
            
        # Count total genes manually
        total_genes = 0
        for col in df.columns[1:]:  # Skip first column (Orthogroup)
            for _, row in df.iterrows():
                cell_value = row[col]
                if isinstance(cell_value, str) and cell_value.strip():
                    genes = [gene.strip() for gene in cell_value.split(',') if gene.strip()]
                    total_genes += len(genes)
        
        print(f"   Total genes across all data: {total_genes}")
        print(f"   Number of species columns: {len(df.columns) - 1}")
            
    except Exception as e:
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()

    print("\n2. Testing OrthogroupsRepository (without ETE)...")
    try:
        # Only import what we need
        from backend.app.data_access.orthogroups_repository import OrthogroupsRepository
        
        ortho_repo = OrthogroupsRepository()
        
        # Load data without pagination limits to get all data
        ortho_data, pagination = ortho_repo.load_orthogroups_data(page=1, per_page=1000)
        print(f"   Data shape: {ortho_data.shape}")
        print(f"   Pagination: {pagination}")
        
        if not ortho_data.empty:
            print(f"   First orthogroup: {ortho_data.iloc[0, 0]}")
            print(f"   Sample cell value: {ortho_data.iloc[0, 1]}")
            print(f"   Cell type: {type(ortho_data.iloc[0, 1])}")
            
            # Check for NaN values
            nan_count = ortho_data.isnull().sum().sum()
            print(f"   Total NaN values: {nan_count}")
            
        cache_stats = ortho_repo.get_cache_stats()
        print(f"   Cache stats: {cache_stats}")
        
    except Exception as e:
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_gene_indexing() 