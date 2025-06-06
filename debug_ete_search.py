#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append('backend')

from app.services.ete_tree_service import ETETreeService
from app.data_access.orthogroups_repository import OrthogroupsRepository
from app.data_access.species_repository import SpeciesRepository

async def debug_ete_search():
    """Debug the ETE search functionality step by step"""
    print("🔍 Starting ETE search debug...")
    
    # Test gene ID
    gene_id = "Aco000536.1"
    
    try:
        # Step 1: Test orthogroups repository
        print("Step 1: Testing orthogroups repository...")
        ortho_repo = OrthogroupsRepository()
        
        orthogroup_id = await ortho_repo.find_gene_orthogroup(gene_id)
        print(f"Orthogroup found: {orthogroup_id}")
        
        if orthogroup_id:
            genes_by_species = await ortho_repo.get_orthogroup_genes(orthogroup_id)
            print(f"Genes by species found: {len(genes_by_species)} species")
            print(f"First 5 species: {list(genes_by_species.keys())[:5]}")
        
        # Step 2: Test species repository
        print("\nStep 2: Testing species repository...")
        species_repo = SpeciesRepository()
        species_mapping = species_repo.load_species_mapping()
        print(f"Species mapping loaded: {len(species_mapping.get('id_to_full', {}))} entries")
        
        # Step 3: Test ETE service
        print("\nStep 3: Testing ETE service...")
        ete_service = ETETreeService()
        
        if ete_service.is_ete_available():
            print("ETE3 is available")
            
            # Try loading the tree
            tree = ete_service.load_ete_tree()
            if tree:
                leaves = list(tree.iter_leaves())
                print(f"ETE tree loaded with {len(leaves)} leaves")
                print(f"First 5 leaf names: {[leaf.name for leaf in leaves[:5]]}")
            else:
                print("ERROR: ETE tree failed to load")
        else:
            print("ERROR: ETE3 not available")
            
        # Step 4: Test the actual search
        print("\nStep 4: Testing actual ETE search...")
        results = await ete_service.search_tree_by_gene(gene_id, max_results=5)
        print(f"ETE search results: {len(results)} found")
        
        for i, result in enumerate(results[:3]):
            print(f"  Result {i+1}: {result.node_name} (genes: {result.gene_count})")
            
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_ete_search()) 