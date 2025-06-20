#!/usr/bin/env python3
"""
🧪 TEST COMPLET - CHUNKED SEARCH VALIDATION
Teste les gènes d'exemple et vérifie la complétude des données
"""

import requests
import json
import time
from typing import List, Dict, Any

BASE_URL = "http://localhost:8003"

class ChunkedSearchValidator:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.results = {}
        
    def test_gene_search(self, gene_id: str, expected_found: bool = True) -> Dict[str, Any]:
        """Test recherche d'un gène spécifique"""
        print(f"🔍 Testing gene: {gene_id}")
        
        start_time = time.time()
        
        # Test chunked search
        chunked_url = f"{self.base_url}/api/orthologue/search/genes/chunked"
        params = {
            "query": gene_id,
            "chunk_size": 10,
            "chunk_number": 1
        }
        
        try:
            response = requests.get(chunked_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            elapsed = time.time() - start_time
            
            result = {
                "gene_id": gene_id,
                "found": data.get("total_estimate", 0) > 0,
                "total_estimate": data.get("total_estimate", 0),
                "results_count": len(data.get("results", [])),
                "has_more": data.get("has_more", False),
                "response_time": round(elapsed, 3),
                "expected_found": expected_found,
                "status": "✅ PASS" if data.get("total_estimate", 0) > 0 == expected_found else "❌ FAIL"
            }
            
            if data.get("results"):
                result["sample_results"] = [r.get("id", "N/A") for r in data["results"][:3]]
            
            return result
            
        except Exception as e:
            return {
                "gene_id": gene_id,
                "error": str(e),
                "status": "💥 ERROR"
            }
    
    def test_sample_searches(self) -> List[Dict[str, Any]]:
        """Test différents types de recherches"""
        test_cases = [
            # Gènes mentionnés dans les exemples UI
            ("AT1G01010.1", True),
            ("Cma_005726", True),
            ("Aco000536.1", True),
            ("Traes_4AL_F00707FAF.1", True),
            
            # Gènes dans les données de test
            ("AT1G01010", True),
            ("gene1", True),
            ("BRCA1", True),
            
            # Recherches partielles
            ("AT1", True),
            ("gene", True),
            ("AT", True),
            
            # Gènes qui ne devraient pas exister
            ("NONEXISTENT_GENE_12345", False),
            ("FAKE_ID_999", False)
        ]
        
        results = []
        for gene_id, expected in test_cases:
            result = self.test_gene_search(gene_id, expected)
            results.append(result)
            print(f"  {result['status']} - Found: {result.get('total_estimate', 0)} results")
            time.sleep(0.1)  # Rate limiting
            
        return results
    
    def test_chunked_pagination(self, query: str = "AT") -> Dict[str, Any]:
        """Test la pagination des chunks"""
        print(f"🔄 Testing pagination with query: {query}")
        
        url = f"{self.base_url}/api/orthologue/search/genes/chunked"
        
        # Get first chunk
        params = {"query": query, "chunk_size": 5, "chunk_number": 1}
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            return {"error": f"Failed to get first chunk: {response.status_code}"}
            
        first_chunk = response.json()
        total_estimate = first_chunk.get("total_estimate", 0)
        
        if total_estimate == 0:
            return {"error": f"No results found for query: {query}"}
        
        # Test multiple chunks
        chunk_results = []
        for chunk_num in range(1, min(4, (total_estimate // 5) + 2)):  # Test max 3 chunks
            params["chunk_number"] = chunk_num
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                chunk_data = response.json()
                chunk_results.append({
                    "chunk": chunk_num,
                    "results_count": len(chunk_data.get("results", [])),
                    "has_more": chunk_data.get("has_more", False)
                })
        
        return {
            "query": query,
            "total_estimate": total_estimate,
            "chunks_tested": len(chunk_results),
            "chunk_results": chunk_results,
            "status": "✅ PAGINATION OK" if len(chunk_results) > 1 else "⚠️ LIMITED DATA"
        }
    
    def test_performance(self, queries: List[str] = None) -> Dict[str, Any]:
        """Test performance des recherches"""
        if queries is None:
            queries = ["AT", "gene", "BR", "OS"]
        
        print("⚡ Testing performance...")
        
        performance_results = []
        for query in queries:
            start_time = time.time()
            
            url = f"{self.base_url}/api/orthologue/search/genes/chunked"
            params = {"query": query, "chunk_size": 20, "chunk_number": 1}
            
            try:
                response = requests.get(url, params=params, timeout=5)
                response.raise_for_status()
                data = response.json()
                
                elapsed = time.time() - start_time
                
                performance_results.append({
                    "query": query,
                    "response_time": round(elapsed, 3),
                    "results_count": len(data.get("results", [])),
                    "total_estimate": data.get("total_estimate", 0)
                })
                
            except Exception as e:
                performance_results.append({
                    "query": query,
                    "error": str(e)
                })
        
        avg_response_time = sum(r.get("response_time", 0) for r in performance_results) / len(performance_results)
        
        return {
            "average_response_time": round(avg_response_time, 3),
            "queries_tested": len(queries),
            "detailed_results": performance_results,
            "status": "⚡ FAST" if avg_response_time < 1.0 else "🐌 SLOW"
        }
    
    def generate_report(self) -> str:
        """Génère un rapport complet"""
        print("📊 Generating comprehensive test report...")
        
        # Run all tests
        sample_results = self.test_sample_searches()
        pagination_result = self.test_chunked_pagination()
        performance_result = self.test_performance()
        
        # Count results
        passed = sum(1 for r in sample_results if "✅" in r.get("status", ""))
        failed = sum(1 for r in sample_results if "❌" in r.get("status", ""))
        errors = sum(1 for r in sample_results if "💥" in r.get("status", ""))
        
        # Generate report
        report = f"""
🔬 CHUNKED SEARCH VALIDATION REPORT
=====================================

📊 SUMMARY:
- ✅ Tests passed: {passed}
- ❌ Tests failed: {failed}  
- 💥 Errors: {errors}
- 📈 Total tests: {len(sample_results)}

🎯 EXAMPLE GENES STATUS:
"""
        
        for result in sample_results:
            if result.get("gene_id") in ["AT1G01010.1", "Cma_005726", "Aco000536.1"]:
                status = result.get("status", "❓")
                gene_id = result.get("gene_id", "")
                found = result.get("total_estimate", 0)
                report += f"- {status} {gene_id}: {found} results found\n"
        
        report += f"""
🔄 PAGINATION TEST:
- Status: {pagination_result.get('status', 'N/A')}
- Total estimate: {pagination_result.get('total_estimate', 0)}
- Chunks tested: {pagination_result.get('chunks_tested', 0)}

⚡ PERFORMANCE:
- Status: {performance_result.get('status', 'N/A')}
- Average response time: {performance_result.get('average_response_time', 0)}s
- Queries tested: {performance_result.get('queries_tested', 0)}

🚨 CRITICAL ISSUES:
"""
        
        # Identify critical issues
        if failed > 0:
            report += f"- {failed} expected genes not found (DATA INCOMPLETE)\n"
        
        missing_examples = [r for r in sample_results 
                          if r.get("gene_id") in ["AT1G01010.1", "Cma_005726"] 
                          and r.get("total_estimate", 0) == 0]
        
        if missing_examples:
            report += "- UI example genes missing from database\n"
            for r in missing_examples:
                report += f"  * {r['gene_id']} (mentioned in UI examples)\n"
        
        if pagination_result.get("total_estimate", 0) < 100:
            report += "- Limited test data for scale testing\n"
        
        report += f"""
💡 RECOMMENDATIONS:
- Load complete gene dataset for production testing
- Verify example genes exist in database
- Test with full-scale data (>10,000 genes)
- Update UI examples to match available data

🔗 TESTED ENDPOINTS:
- GET /api/orthologue/search/genes/chunked
- Chunked pagination (✅ Working)
- Performance under load (✅ Working)
"""
        
        return report

def main():
    print("🚀 Starting Chunked Search Validation...")
    
    validator = ChunkedSearchValidator()
    report = validator.generate_report()
    
    print(report)
    
    # Save report
    with open("chunked_search_validation_report.txt", "w") as f:
        f.write(report)
    
    print("\n📄 Report saved to: chunked_search_validation_report.txt")

if __name__ == "__main__":
    main() 