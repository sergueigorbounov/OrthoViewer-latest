#!/usr/bin/env python3
"""
Test script for unlimited ETE search functionality
"""
import requests
import json

def test_ete_search():
    """Test the ETE search with unlimited results"""
    url = "http://localhost:8003/api/orthologue/ete/search"
    
    # Test unlimited search
    print("🧬 Testing unlimited ETE search for gene Aco000536.1...")
    
    payload = {
        "query": "Aco000536.1",
        "search_type": "gene", 
        "max_results": 0,  # 0 = unlimited
        "include_tree_image": True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Success: {data.get('success', False)}")
            print(f"📊 Total Results: {data.get('total_results', 0)}")
            print(f"📝 Message: {data.get('message', 'No message')}")
            
            if data.get('results'):
                print(f"🌍 First 5 species found:")
                for i, result in enumerate(data['results'][:5], 1):
                    species = result.get('node_name', 'Unknown').strip("'\"")
                    gene_count = result.get('gene_count', 0)
                    print(f"  {i}. {species} ({gene_count} genes)")
            
            if data.get('tree_image'):
                print(f"🌳 Tree image generated: {len(data['tree_image'])} characters")
            else:
                print("🌳 No tree image in response")
                
            return data.get('total_results', 0) > 50  # Should find many more than 50
            
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_ete_search()
    print(f"\n{'✅ Test PASSED' if success else '❌ Test FAILED'}") 