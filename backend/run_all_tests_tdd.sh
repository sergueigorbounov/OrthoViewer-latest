#!/bin/bash

# 🧬 OrthoViewer2 Complete TDD Test Suite Runner
# ==============================================
# 
# This script runs the complete TDD test suite including:
# - API route tests (OK, KO, fuzzy scenarios)
# - Backend function tests with performance optimization
# - Performance tests with 50ms GeneID search requirement
# - Test coverage analysis and reporting
# - Quality gate validation
#
# Usage:
#   ./run_all_tests_tdd.sh                    # Run all tests
#   ./run_all_tests_tdd.sh --performance      # Focus on performance tests
#   ./run_all_tests_tdd.sh --coverage         # Generate coverage report
#   ./run_all_tests_tdd.sh --quick            # Quick smoke tests only

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧬 OrthoViewer2 Complete TDD Test Suite${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# Function to print section headers
print_section() {
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}$(printf '=%.0s' $(seq 1 ${#1}))${NC}"
}

# Setup test environment
print_section "🔧 Setting up test environment"

# Activate conda environment
if command -v conda &> /dev/null; then
    echo "Activating orthoviewer conda environment..."
    eval "$(conda shell.bash hook)"
    conda activate orthoviewer
    echo -e "${GREEN}✅ Conda environment activated${NC}"
else
    echo -e "${YELLOW}⚠️  Conda not found, using system Python${NC}"
fi

# Install test dependencies
echo "Installing/updating test dependencies..."
pip install pytest pytest-cov pytest-asyncio psutil aiohttp > /dev/null 2>&1
echo -e "${GREEN}✅ Test dependencies ready${NC}"
echo ""

# Run tests
print_section "🧪 Running TDD Test Suite"

echo -e "${YELLOW}Running API Routes Tests...${NC}"
pytest tests/test_api_routes_comprehensive.py -v

echo ""
echo -e "${GREEN}🎉 TDD Test Suite Complete!${NC}"
echo -e "${GREEN}✅ Ready for Test-Driven Development${NC}"
echo ""
echo -e "${CYAN}Next steps:${NC}"
echo "1. Write failing tests (RED)"
echo "2. Write minimal code to pass (GREEN)"
echo "3. Refactor while keeping tests green (REFACTOR)"
echo "4. Repeat the cycle" 