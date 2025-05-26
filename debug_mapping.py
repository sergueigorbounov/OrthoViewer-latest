# Fixed debug script for your specific file format
import pandas as pd
import os

# Your file paths
BASE_DIR = "/home/sgorbounov/Documents/orthoviewer2-clean"
DATA_DIR = os.path.join(BASE_DIR, "data/orthofinder")
ORTHOGROUPS_FILE = os.path.join(DATA_DIR, "Orthogroups_clean_121124.txt")
SPECIES_MAPPING_FILE = os.path.join(DATA_DIR, "Table_S1_Metadata_angiosperm_species.csv")

def debug_species_mapping_fixed():
    print("=== FIXED DEBUGGING SPECIES MAPPING ===\n")
    
    # 1. Load orthogroups file
    print("1. Loading orthogroups file...")
    try:
        ortho_df = pd.read_csv(ORTHOGROUPS_FILE, sep='\t', low_memory=False)
        species_columns = ortho_df.columns[1:].tolist()
        print(f"✅ Found {len(species_columns)} species columns in orthogroups file:")
        for i, col in enumerate(species_columns[:20]):
            print(f"  {i+1:2d}. '{col}'")
        if len(species_columns) > 20:
            print(f"  ... and {len(species_columns) - 20} more")
        print()
        ortho_codes = set(species_columns)
    except Exception as e:
        print(f"❌ Error loading orthogroups file: {e}")
        return
    
    # 2. Load species mapping file with correct format
    print("2. Loading species mapping file (skipping header, using tabs)...")
    try:
        # Skip the first 2 lines (header description), use tab separator
        mapping_df = pd.read_csv(SPECIES_MAPPING_FILE, sep='\t', skiprows=2)
        print(f"✅ Mapping file loaded successfully!")
        print(f"   Shape: {mapping_df.shape}")
        print(f"   Columns: {mapping_df.columns.tolist()}")
        print(f"\nFirst 5 rows:")
        print(mapping_df.head())
        
        # The columns are: [Species_Full_Name, Species_ID, Annotation, etc...]
        # We want: Species_ID -> Species_Full_Name mapping
        species_full_col = mapping_df.columns[0]  # Full species name
        species_id_col = mapping_df.columns[1]    # Species ID (short code)
        
        print(f"\nUsing columns for mapping:")
        print(f"  Species ID (short): '{species_id_col}'")
        print(f"  Full name: '{species_full_col}'")
        
    except Exception as e:
        print(f"❌ Error loading mapping file: {e}")
        return
    
    # 3. Create the mapping dictionary (ID -> Full Name)
    print(f"\n3. Creating species mapping...")
    try:
        # Create mapping: short code -> full name
        id_to_full = dict(zip(mapping_df[species_id_col], mapping_df[species_full_col]))
        
        print(f"✅ Created mapping with {len(id_to_full)} entries")
        print(f"Sample mappings:")
        for i, (short, full) in enumerate(id_to_full.items()):
            if i >= 10:
                break
            print(f"  '{short}' -> '{full}'")
            
    except Exception as e:
        print(f"❌ Error creating mapping: {e}")
        return
    
    # 4. Compare with orthogroups species
    print(f"\n4. Comparing with orthogroups species...")
    
    mapping_codes = set(id_to_full.keys())
    missing_in_mapping = ortho_codes - mapping_codes
    found_in_both = ortho_codes & mapping_codes
    
    print(f"\n📊 RESULTS:")
    print(f"   Species in orthogroups: {len(ortho_codes)}")
    print(f"   Species in mapping: {len(mapping_codes)}")
    print(f"   ✅ Successfully mapped: {len(found_in_both)} ({len(found_in_both)/len(ortho_codes)*100:.1f}%)")
    print(f"   ❌ Missing mappings: {len(missing_in_mapping)}")
    
    if found_in_both:
        print(f"\n✅ SUCCESSFUL MAPPINGS (sample):")
        for code in sorted(list(found_in_both))[:15]:
            full_name = id_to_full[code]
            print(f"   '{code}' -> '{full_name}'")
    
    if missing_in_mapping:
        print(f"\n🔴 MISSING MAPPINGS ({len(missing_in_mapping)} species):")
        missing_sorted = sorted(list(missing_in_mapping))
        for i, code in enumerate(missing_sorted):
            if i >= 20:
                print(f"   ... and {len(missing_in_mapping) - 20} more")
                break
            print(f"   '{code}' (needs mapping)")
            
        # Look for potential partial matches
        print(f"\n🔍 Looking for potential partial matches...")
        potential_matches = {}
        for missing_code in missing_sorted[:10]:  # Check first 10 missing codes
            for mapping_code in mapping_codes:
                if (missing_code.lower() in mapping_code.lower() or 
                    mapping_code.lower() in missing_code.lower() or
                    missing_code[:2].lower() == mapping_code[:2].lower()):
                    if missing_code not in potential_matches:
                        potential_matches[missing_code] = []
                    potential_matches[missing_code].append(mapping_code)
        
        if potential_matches:
            print("Potential matches found:")
            for missing, candidates in potential_matches.items():
                print(f"   '{missing}' might match: {candidates}")
        else:
            print("No obvious partial matches found")
    
    print(f"\n🎯 SUMMARY:")
    if len(found_in_both) > len(missing_in_mapping):
        print(f"✅ Good news! {len(found_in_both)}/{len(ortho_codes)} species are already mapped")
        print(f"   Only {len(missing_in_mapping)} species need additional mapping")
    else:
        print(f"⚠️  {len(missing_in_mapping)} species still need mapping")
    
    return {
        'mapping': id_to_full,
        'found': found_in_both,
        'missing': missing_in_mapping
    }

# Run the fixed debug function
if __name__ == "__main__":
    result = debug_species_mapping_fixed()