#!/usr/bin/env python3

import sys
import asyncio
import pandas as pd
from pathlib import Path

# Add the backend path to sys.path so we can import modules
sys.path.append('backend')

async def debug_ete_search():
    print("🔍 Debugging ETE search step by step...")
    
    try:
        # Import the repositories
        from app.data_access.orthogroups_repository import OrthogroupsRepository
        from app.services.ete_tree_service import ETETreeService
        
        # Create repository instance
        ortho_repo = OrthogroupsRepository()
        ete_service = ETETreeService()
        
        print("✅ Repositories created")
        
        # Step 1: Find orthogroup for gene
        gene_id = "Aco000536.1"
        print(f"\n🔍 Step 1: Finding orthogroup for {gene_id}")
        
        orthogroup_id = await ortho_repo.find_gene_orthogroup(gene_id)
        print(f"Orthogroup found: {orthogroup_id}")
        
        if not orthogroup_id:
            print("❌ No orthogroup found")
            return
            
        # Step 2: Get genes in orthogroup  
        print(f"\n🔍 Step 2: Getting genes in orthogroup {orthogroup_id}")
        
        orthogroup_genes = await ortho_repo.get_orthogroup_genes(orthogroup_id)
        print(f"Genes data type: {type(orthogroup_genes)}")
        
        if isinstance(orthogroup_genes, dict):
            print(f"Species in orthogroup: {len(orthogroup_genes)}")
            print("First 10 species:")
            for i, (species, genes) in enumerate(orthogroup_genes.items()):
                if i < 10:
                    print(f"  {species}: {len(genes) if isinstance(genes, list) else 'Unknown'} genes")
        else:
            print(f"Unexpected orthogroup_genes format: {orthogroup_genes}")
            return
            
        # Step 3: Check ETE tree availability
        print(f"\n🔍 Step 3: Checking ETE tree availability")
        
        if not ete_service.is_ete_available():
            print("❌ ETE not available")
            return
        else:
            print("✅ ETE available")
            
        # Load tree if needed
        if not hasattr(ete_service, 'tree') or ete_service.tree is None:
            print("Loading ETE tree...")
            ete_service.load_ete_tree()
            print("✅ ETE tree loaded")
        else:
            print("✅ ETE tree already loaded")
            
        # Step 4: Check species matching
        print(f"\n🔍 Step 4: Testing species matching")
        
        if hasattr(ete_service, 'leaf_node_cache'):
            print(f"Leaf node cache size: {len(ete_service.leaf_node_cache)}")
        
        # Test a few species codes
        test_species = list(orthogroup_genes.keys())[:5]
        print(f"Testing species matching for: {test_species}")
        
        for species_code in test_species:
            matched_node = ete_service._find_tree_leaf_for_species(species_code)
            if matched_node:
                print(f"  {species_code} -> {matched_node.name}")
            else:
                print(f"  {species_code} -> NO MATCH")
                
        # Step 5: Full search simulation
        print(f"\n🔍 Step 5: Simulating full search")
        
        found_species = set(orthogroup_genes.keys())
        print(f"Species from orthogroup: {len(found_species)}")
        
        matched_species = []
        for species_code in found_species:
            leaf_node = ete_service._find_tree_leaf_for_species(species_code)
            if leaf_node:
                matched_species.append(species_code)
                
        print(f"Successfully matched species: {len(matched_species)}")
        print(f"First 10 matched: {matched_species[:10]}")
        
        # Step 6: Check what the actual method would return
        print(f"\n🔍 Step 6: Testing actual search_tree_by_gene method")
        
        results = await ete_service.search_tree_by_gene(gene_id, max_results=50)
        print(f"Actual method returned: {len(results)} results")
        
        if results:
            print("First 5 results:")
            for i, result in enumerate(results[:5]):
                print(f"  {i+1}. {result.species_name} (code: {result.species_code})")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_ete_search()) 