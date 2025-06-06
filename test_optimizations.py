#!/usr/bin/env python3
"""
Test script to verify ETE Tree Search optimizations
"""

import time
import requests
import json

BASE_URL = "http://localhost:8003"

def test_cache_stats():
    """Test cache statistics endpoint"""
    print("🔍 Testing cache statistics...")
    try:
        response = requests.get(f"{BASE_URL}/api/orthologue/cache/stats")
        if response.status_code == 200:
            stats = response.json()
            print("✅ Cache stats retrieved successfully:")
            print(f"  - ETE Service: indices_built={stats['ete_service']['indices_built']}")
            print(f"  - Total genes: {stats['ete_service']['total_genes']}")
            print(f"  - Orthogroups: data_loaded={stats['orthogroups_repository']['data_loaded']}")
            return True
        else:
            print(f"❌ Cache stats failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cache stats error: {e}")
        return False

def test_cache_warming():
    """Test cache warming endpoint"""
    print("\n🔥 Testing cache warming...")
    try:
        response = requests.post(f"{BASE_URL}/api/orthologue/cache/warm")
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Cache warming successful")
                return True
            else:
                print(f"❌ Cache warming failed: {result.get('message')}")
                return False
        else:
            print(f"❌ Cache warming failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cache warming error: {e}")
        return False

def test_ete_search_performance():
    """Test ETE search performance"""
    print("\n⚡ Testing ETE search performance...")
    
    # Test gene search
    gene_id = "Aco000536.1"
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/orthologue/ete/search",
            json={
                "search_type": "gene",
                "query": gene_id,
                "max_results": 50,
                "include_tree_image": False  # Skip image for performance test
            }
        )
        
        end_time = time.time()
        search_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ Gene search successful in {search_time:.0f}ms")
                print(f"  - Query: {result['query']}")
                print(f"  - Results: {result['total_results']}")
                return search_time
            else:
                print(f"❌ Gene search failed: {result.get('message')}")
                return None
        else:
            print(f"❌ Gene search failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Gene search error: {e}")
        return None

def test_species_search_performance():
    """Test species search performance"""
    print("\n🌱 Testing species search performance...")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/orthologue/ete/search",
            json={
                "search_type": "species",
                "query": "Arabidopsis",
                "max_results": 10,
                "include_tree_image": False
            }
        )
        
        end_time = time.time()
        search_time = (end_time - start_time) * 1000
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ Species search successful in {search_time:.0f}ms")
                print(f"  - Query: {result['query']}")
                print(f"  - Results: {result['total_results']}")
                return search_time
            else:
                print(f"❌ Species search failed: {result.get('message')}")
                return None
        else:
            print(f"❌ Species search failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Species search error: {e}")
        return None

def main():
    """Run all optimization tests"""
    print("🚀 Testing ETE Tree Search Optimizations")
    print("=" * 50)
    
    # Test cache endpoints
    cache_stats_ok = test_cache_stats()
    cache_warm_ok = test_cache_warming()
    
    # Test search performance
    gene_time = test_ete_search_performance()
    species_time = test_species_search_performance()
    
    # Summary
    print("\n📊 OPTIMIZATION TEST SUMMARY")
    print("=" * 50)
    print(f"Cache Stats Endpoint: {'✅' if cache_stats_ok else '❌'}")
    print(f"Cache Warming: {'✅' if cache_warm_ok else '❌'}")
    print(f"Gene Search: {'✅' if gene_time else '❌'} {f'({gene_time:.0f}ms)' if gene_time else ''}")
    print(f"Species Search: {'✅' if species_time else '❌'} {f'({species_time:.0f}ms)' if species_time else ''}")
    
    if gene_time and gene_time < 1000:
        print("\n🎉 Performance looks good! Gene search under 1 second.")
    elif gene_time and gene_time < 5000:
        print("\n⚠️  Performance is acceptable but could be improved.")
    elif gene_time:
        print("\n🔧 Performance needs optimization - search taking too long.")
    
    if cache_stats_ok and cache_warm_ok and gene_time and species_time:
        print("\n✅ All optimizations are working correctly!")
        return True
    else:
        print("\n❌ Some optimizations need attention.")
        return False

if __name__ == "__main__":
    main() 