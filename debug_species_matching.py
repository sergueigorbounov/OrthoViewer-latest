#!/usr/bin/env python3

import sys
sys.path.append('backend')

from app.services.ete_tree_service import ETETreeService

def debug_species_matching():
    """Debug species matching between orthogroups and tree"""
    print("🔍 Testing species matching...")
    
    try:
        ete_service = ETETreeService()
        
        if not ete_service.is_ete_available():
            print("ERROR: ETE3 not available")
            return
            
        # Load tree
        tree = ete_service.load_ete_tree()
        if not tree:
            print("ERROR: Could not load ETE tree")
            return
            
        leaves = list(tree.iter_leaves())
        print(f"Tree has {len(leaves)} leaves")
        print(f"First 10 leaf names: {[leaf.name for leaf in leaves[:10]]}")
        
        # Test some species codes that should be in orthogroup OG0000003
        test_species = ["Ac", "Aco", "Ath", "Osa", "Zma", "Bra", "Sly", "Ptr", "Gma"]
        
        print(f"\nTesting species matching for common codes:")
        for species_code in test_species:
            matched_leaf = ete_service._find_tree_leaf_for_species(species_code)
            if matched_leaf:
                print(f"  {species_code} -> {matched_leaf.name} ✅")
            else:
                print(f"  {species_code} -> No match ❌")
                
        # Show the leaf node cache
        print(f"\nLeaf node cache has {len(ete_service.leaf_node_cache)} entries")
        print(f"First 10 cached names: {list(ete_service.leaf_node_cache.keys())[:10]}")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_species_matching() 