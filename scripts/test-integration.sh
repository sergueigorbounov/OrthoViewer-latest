#!/bin/bash

# Integration Test Runner using conda
# Runs integration tests for OrthoViewer backend

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Running OrthoViewer integration tests with conda...${NC}"

# Check if conda environment exists
ENV_NAME="orthoviewer2"
if ! conda env list | grep -q "$ENV_NAME"; then
    echo -e "${RED}conda environment '$ENV_NAME' not found.${NC}"
    echo -e "${YELLOW}Please run: cd backend && conda env create -f environment.yml${NC}"
    exit 1
fi

# Activate conda environment
source $(conda info --base)/etc/profile.d/conda.sh
conda activate "$ENV_NAME"

# Navigate to backend directory
cd backend

# Run integration tests
echo -e "${YELLOW}Running integration tests...${NC}"
pytest tests/integration/ -v --tb=short

echo -e "${GREEN}✅ Integration tests completed!${NC}"