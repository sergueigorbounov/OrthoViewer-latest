#!/usr/bin/env python3

import sys
import asyncio

# Add the backend path to sys.path so we can import modules
sys.path.append('backend')

async def check_species_matching():
    print("🔍 Checking species matching between orthogroup and ETE tree...")
    
    try:
        from app.data_access.orthogroups_repository import OrthogroupsRepository
        from app.services.ete_tree_service import ETETreeService
        
        # Create instances
        ortho_repo = OrthogroupsRepository()
        ete_service = ETETreeService()
        
        # Get genes in orthogroup OG0000003
        orthogroup_genes = await ortho_repo.get_orthogroup_genes("OG0000003")
        print(f"Species in orthogroup: {len(orthogroup_genes)}")
        
        # Load ETE tree
        ete_service.load_ete_tree()
        print(f"ETE tree loaded with {len(ete_service.leaf_node_cache)} leaves")
        
        # Check matching
        matched = []
        not_matched = []
        
        for species_code in sorted(orthogroup_genes.keys()):
            leaf_node = ete_service._find_tree_leaf_for_species(species_code)
            if leaf_node:
                matched.append((species_code, leaf_node.name))
            else:
                not_matched.append(species_code)
                
        print(f"\n✅ MATCHED ({len(matched)} species):")
        for species_code, tree_name in matched:
            print(f"  {species_code} -> {tree_name}")
            
        print(f"\n❌ NOT MATCHED ({len(not_matched)} species):")
        for species_code in not_matched:
            print(f"  {species_code}")
            
        print(f"\nSummary: {len(matched)}/{len(orthogroup_genes)} species matched")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_species_matching()) 