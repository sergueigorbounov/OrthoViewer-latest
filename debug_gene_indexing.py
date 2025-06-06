#!/usr/bin/env python3

import sys
import os
sys.path.append('backend')

from backend.app.data_access.orthogroups_repository import OrthogroupsRepository
from backend.app.services.ete_tree_service import ETETreeService
import pandas as pd

def debug_gene_indexing():
    print("=== Debugging Gene Indexing ===\n")
    
    # Test OrthogroupsRepository
    print("1. Testing OrthogroupsRepository...")
    ortho_repo = OrthogroupsRepository()
    
    try:
        # Load data without pagination limits to get all data
        ortho_data, pagination = ortho_repo.load_orthogroups_data(page=1, per_page=1000)
        print(f"   Data shape: {ortho_data.shape}")
        print(f"   Pagination: {pagination}")
        print(f"   Columns: {list(ortho_data.columns)}")
        
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
    
    print("\n2. Testing ETETreeService gene indexing...")
    ete_service = ETETreeService()
    
    try:
        # Get data using the same method ETE service uses
        ortho_data, pagination = ete_service.orthogroups_repo.load_orthogroups_data()
        print(f"   ETE service sees data shape: {ortho_data.shape}")
        
        if not ortho_data.empty:
            print("   Processing columns manually...")
            total_genes_found = 0
            
            for col_idx, col in enumerate(ortho_data.columns[1:]):  # Skip first column
                print(f"     Column {col_idx + 1}: {col}")
                species_genes = []
                
                for row_idx, (_, row) in enumerate(ortho_data.iterrows()):
                    cell_value = row[col]
                    print(f"       Row {row_idx}: {type(cell_value)} = {str(cell_value)[:100]}")
                    
                    if isinstance(cell_value, str) and cell_value.strip():
                        genes = [gene.strip() for gene in cell_value.split(',') if gene.strip()]
                        species_genes.extend(genes)
                        print(f"         Found {len(genes)} genes in this cell")
                    else:
                        print(f"         Skipped (not a non-empty string)")
                    
                    if row_idx >= 2:  # Only check first few rows
                        break
                
                total_genes_found += len(species_genes)
                print(f"     Total genes in {col}: {len(species_genes)}")
                
                if col_idx >= 2:  # Only check first few columns
                    break
            
            print(f"   Manual count found {total_genes_found} genes")
        
    except Exception as e:
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n3. Testing direct file reading...")
    try:
        file_path = "data/orthofinder/Orthogroups_clean_121124_sample.csv"
        df = pd.read_csv(file_path)
        print(f"   Direct file read shape: {df.shape}")
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
            
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    debug_gene_indexing() 