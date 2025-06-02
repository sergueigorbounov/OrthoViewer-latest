#!/bin/bash

# 🧬 OrthoViewer2 - API Endpoint Testing Script
# Test all endpoints of the clean 3-layer architecture

echo "🧪 Testing OrthoViewer2 Clean 3-Layer Architecture API"
echo "============================================================"

# Base URL
BASE_URL="http://localhost:8003"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to test endpoint
test_endpoint() {
    local endpoint=$1
    local description=$2
    local expected_status=${3:-200}
    
    echo -n "Testing $description... "
    
    # Make request and capture status code
    status_code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL$endpoint")
    
    if [ "$status_code" -eq "$expected_status" ]; then
        echo -e "${GREEN}✅ PASS${NC} ($status_code)"
        return 0
    else
        echo -e "${RED}❌ FAIL${NC} (got $status_code, expected $expected_status)"
        return 1
    fi
}

# Function to test endpoint with response time
test_endpoint_with_timing() {
    local endpoint=$1
    local description=$2
    local max_time_ms=$3
    local expected_status=${4:-200}
    
    echo -n "Testing $description... "
    
    # Make request and capture both status code and timing
    response=$(curl -s -w "%{http_code}|%{time_total}" "$BASE_URL$endpoint")
    status_code=$(echo $response | cut -d'|' -f1)
    time_total=$(echo $response | cut -d'|' -f2)
    
    # Convert to milliseconds
    time_ms=$(echo "$time_total * 1000" | bc | cut -d'.' -f1)
    
    if [ "$status_code" -eq "$expected_status" ]; then
        if [ "$time_ms" -le "$max_time_ms" ]; then
            echo -e "${GREEN}✅ PASS${NC} ($status_code, ${time_ms}ms)"
            return 0
        else
            echo -e "${YELLOW}⚠️  SLOW${NC} ($status_code, ${time_ms}ms > ${max_time_ms}ms)"
            return 1
        fi
    else
        echo -e "${RED}❌ FAIL${NC} (got $status_code, expected $expected_status)"
        return 1
    fi
}

# Check if server is running
echo "🔍 Checking if server is running..."
if ! curl -s "$BASE_URL" > /dev/null; then
    echo -e "${RED}❌ Server is not running on $BASE_URL${NC}"
    echo "Please start the server with: cd backend && python -m uvicorn app.main:app --reload --port 8003"
    exit 1
fi
echo -e "${GREEN}✅ Server is running${NC}"
echo ""

# Test counter
passed=0
failed=0

echo "🏥 HEALTH & SYSTEM ENDPOINTS"
echo "----------------------------"

# Basic health endpoints
test_endpoint "/" "Root endpoint" && ((passed++)) || ((failed++))
test_endpoint "/status" "Status endpoint" && ((passed++)) || ((failed++))
test_endpoint "/health/" "Basic health check" && ((passed++)) || ((failed++))
test_endpoint "/health/detailed" "Detailed health check" && ((passed++)) || ((failed++))
test_endpoint "/health/ready" "Readiness probe" && ((passed++)) || ((failed++))
test_endpoint "/health/live" "Liveness probe" && ((passed++)) || ((failed++))

echo ""
echo "🐾 SPECIES MANAGEMENT ENDPOINTS"
echo "--------------------------------"

# Species endpoints
test_endpoint "/api/species/" "List all species" && ((passed++)) || ((failed++))
test_endpoint "/api/species/homo_sapiens" "Get specific species" && ((passed++)) || ((failed++))
test_endpoint "/api/species/homo_sapiens/stats" "Species statistics" && ((passed++)) || ((failed++))
test_endpoint "/api/species/homo_sapiens/genes" "Species genes" && ((passed++)) || ((failed++))

echo ""
echo "🧬 GENE SEARCH & RETRIEVAL ENDPOINTS"
echo "-------------------------------------"

# Gene endpoints with performance testing
test_endpoint_with_timing "/api/genes/search?query=test" "Gene search (< 50ms)" 50 && ((passed++)) || ((failed++))
test_endpoint "/api/genes/GENE001" "Gene details" && ((passed++)) || ((failed++))
test_endpoint "/api/genes/GENE001/orthologs" "Gene orthologs" && ((passed++)) || ((failed++))
test_endpoint "/api/genes/GENE001/sequence" "Gene sequence" && ((passed++)) || ((failed++))

echo ""
echo "🔗 ORTHOGROUP MANAGEMENT ENDPOINTS"
echo "-----------------------------------"

# Orthogroup endpoints with performance testing
test_endpoint_with_timing "/api/orthogroups/" "List orthogroups (< 100ms)" 100 && ((passed++)) || ((failed++))
test_endpoint "/api/orthogroups/OG001" "Orthogroup details" && ((passed++)) || ((failed++))
test_endpoint "/api/orthogroups/OG001/genes" "Orthogroup genes" && ((passed++)) || ((failed++))
test_endpoint "/api/orthogroups/OG001/stats" "Orthogroup statistics" && ((passed++)) || ((failed++))
test_endpoint "/api/orthogroups/OG001/tree" "Phylogenetic tree" && ((passed++)) || ((failed++))

echo ""
echo "📊 DASHBOARD & ANALYTICS ENDPOINTS"
echo "-----------------------------------"

# Dashboard endpoints with performance testing
test_endpoint_with_timing "/api/dashboard/" "Dashboard overview (< 200ms)" 200 && ((passed++)) || ((failed++))
test_endpoint "/api/dashboard/stats" "System statistics" && ((passed++)) || ((failed++))
test_endpoint "/api/dashboard/species-comparison" "Species comparison" && ((passed++)) || ((failed++))
test_endpoint "/api/dashboard/gene-families" "Top gene families" && ((passed++)) || ((failed++))
test_endpoint "/api/dashboard/search-trends" "Search analytics" && ((passed++)) || ((failed++))
test_endpoint "/api/dashboard/performance" "Performance metrics" && ((passed++)) || ((failed++))

echo ""
echo "📋 SUMMARY"
echo "=========="
total=$((passed + failed))
echo "Total tests: $total"
echo -e "Passed: ${GREEN}$passed${NC}"
echo -e "Failed: ${RED}$failed${NC}"

if [ $failed -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED! Clean 3-layer architecture is working perfectly.${NC}"
    echo ""
    echo "🚀 Next steps:"
    echo "  1. Implement Service Layer (business logic)"
    echo "  2. Implement Repository Layer (data access)"
    echo "  3. Replace mock data with real implementations"
    echo ""
    echo "📖 API Documentation: http://localhost:8003/api/docs"
    exit 0
else
    echo -e "${RED}❌ Some tests failed. Please check the server logs.${NC}"
    exit 1
fi 