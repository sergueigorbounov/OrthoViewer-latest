#!/usr/bin/env python3

import sys
import pandas as pd

# Simple check of orthogroup data without async
def check_orthogroup_species():
    print("🔍 Checking species in orthogroup OG0000003...")
    
    try:
        # Load the orthogroups data directly
        file_path = "data/orthofinder/Orthogroups_clean_121124.txt"
        print(f"Loading: {file_path}")
        
        df = pd.read_csv(file_path, sep='\t', dtype=str, keep_default_na=False, na_filter=False)
        print(f"Data shape: {df.shape}")
        print(f"Columns: {list(df.columns)[:10]}...")
        
        # Find the specific orthogroup
        og_row = df[df['Orthogroup'] == 'OG0000003']
        if og_row.empty:
            print("ERROR: OG0000003 not found")
            return
            
        print(f"Found orthogroup OG0000003")
        
        # Get all species columns (skip the Orthogroup column)
        species_cols = [col for col in df.columns if col != 'Orthogroup']
        print(f"Total species columns: {len(species_cols)}")
        
        # Check which species have genes in this orthogroup
        species_with_genes = []
        for col in species_cols:
            cell_value = og_row[col].iloc[0]
            if cell_value and cell_value.strip():
                genes = [g.strip() for g in cell_value.replace(',', ' ').split() if g.strip()]
                if genes:
                    species_with_genes.append((col, len(genes)))
        
        print(f"Species with genes in OG0000003: {len(species_with_genes)}")
        print("First 20 species:")
        for species, count in species_with_genes[:20]:
            print(f"  {species}: {count} genes")
            
        # Check if 'Ac' is in there (should contain Aco000536.1)
        for species, count in species_with_genes:
            if species == 'Ac':
                print(f"\n✅ Found Ac species with {count} genes")
                cell_value = og_row[species].iloc[0]
                genes = [g.strip() for g in cell_value.replace(',', ' ').split() if g.strip()]
                if 'Aco000536.1' in genes:
                    print(f"✅ Aco000536.1 is in the Ac column")
                else:
                    print(f"❌ Aco000536.1 NOT found in Ac column")
                    print(f"First 10 genes in Ac: {genes[:10]}")
                break
        else:
            print("\n❌ 'Ac' species not found in orthogroup")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_orthogroup_species() 