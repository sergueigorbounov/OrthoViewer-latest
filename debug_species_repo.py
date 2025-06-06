#!/usr/bin/env python3

import sys
import asyncio

# Add the backend path to sys.path so we can import modules
sys.path.append('backend')

async def debug_species_repo():
    print("🔍 Debugging SpeciesRepository...")
    
    try:
        from app.repositories.species_repository import SpeciesRepository
        
        # Create repository instance
        species_repo = SpeciesRepository()
        
        # Load species mappings
        await species_repo.load_species_mappings()
        
        print(f"Species mappings loaded: {len(species_repo.species_mappings)}")
        
        # Show first 10 mappings
        print("\nFirst 10 species mappings:")
        for i, (code, name) in enumerate(species_repo.species_mappings.items()):
            if i < 10:
                print(f"  {code} -> {name}")
                
        # Check if specific species codes are mapped
        test_codes = ['Ac', 'Aet', 'Ah', 'Al', 'Amt']
        print(f"\nTesting specific codes:")
        for code in test_codes:
            if code in species_repo.species_mappings:
                print(f"  ✅ {code} -> {species_repo.species_mappings[code]}")
            else:
                print(f"  ❌ {code} -> NOT FOUND")
                
        print(f"\nAll mapped species codes:")
        print(sorted(species_repo.species_mappings.keys()))
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_species_repo()) 