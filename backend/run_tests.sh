#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Usage message
if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
  echo "Usage: ./run_tests.sh [type]"
  echo "Types:"
  echo "  all         - Run all tests (default)"
  echo "  unit        - Run unit tests"
  echo "  integration - Run integration tests"
  echo "  api         - Run API tests"
  echo "  performance - Run performance tests"
  echo "  fuzzing     - Run fuzzing tests"
  exit 0
fi

# Test type selection
TEST_TYPE=${1:-all}

# Use conda only (no pip fallback for compliance)
if command -v conda >/dev/null 2>&1; then
    if conda env list | grep -q "orthoviewer2"; then
        echo "✓ Using existing conda environment 'orthoviewer2'"
        source "$(conda info --base)/etc/profile.d/conda.sh"
        conda activate orthoviewer2
        # Update environment to ensure all dependencies are installed
        conda env update -f environment.yml
    else
        echo "Creating conda environment 'orthoviewer2' from environment.yml..."
        conda env create -f environment.yml
        source "$(conda info --base)/etc/profile.d/conda.sh"
        conda activate orthoviewer2
    fi
else
    echo "❌ Conda not found. Please install conda/miniconda first."
    echo "Visit: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

# Run tests based on type
case $TEST_TYPE in
  all)
    echo -e "${GREEN}Running all tests...${NC}"
    python -m pytest
    ;;
  unit)
    echo -e "${GREEN}Running unit tests...${NC}"
    python -m pytest tests/unit -m unit
    ;;
  integration)
    echo -e "${GREEN}Running integration tests...${NC}"
    python -m pytest tests/integration -m integration
    ;;
  api)
    echo -e "${GREEN}Running API tests...${NC}"
    python -m pytest tests/api -m api
    ;;
  performance)
    echo -e "${GREEN}Running performance tests...${NC}"
    python -m pytest tests/performance -m performance
    ;;
  fuzzing)
    echo -e "${GREEN}Running fuzzing tests...${NC}"
    python -m pytest tests/api -m fuzzing
    ;;
  *)
    echo -e "${RED}Unknown test type: $TEST_TYPE${NC}"
    echo "Use --help to see available test types"
    exit 1
    ;;
esac

# Show success message
echo -e "${GREEN}Tests completed successfully!${NC}"