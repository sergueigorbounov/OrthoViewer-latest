#!/bin/bash

# Backend Environment Setup with conda
# Sets up the conda environment for OrthoViewer backend

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up OrthoViewer backend conda environment...${NC}"

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo -e "${RED}conda is not installed. Please install Miniconda or Anaconda first.${NC}"
    exit 1
fi

# Create conda environment from environment.yml
if [ -f "environment.yml" ]; then
    echo -e "${YELLOW}Creating conda environment from environment.yml...${NC}"
    conda env create -f environment.yml --force
else
    echo -e "${RED}environment.yml not found. Please ensure you're in the backend directory.${NC}"
    exit 1
fi

# Activate environment and verify installation
echo -e "${YELLOW}Activating conda environment...${NC}"
source $(conda info --base)/etc/profile.d/conda.sh
conda activate orthoviewer2

# Verify key packages are installed
echo -e "${YELLOW}Verifying installation...${NC}"
python -c "import fastapi; print(f'FastAPI version: {fastapi.__version__}')"
python -c "import sqlalchemy; print(f'SQLAlchemy version: {sqlalchemy.__version__}')"
python -c "import uvicorn; print(f'Uvicorn version: {uvicorn.__version__}')"

echo -e "${GREEN}✅ Backend conda environment setup complete!${NC}"
echo ""
echo -e "${GREEN}To activate the environment:${NC}"
echo -e "  conda activate orthoviewer2"
echo ""
echo -e "${GREEN}To start the development server:${NC}"
echo -e "  conda activate orthoviewer2"
echo -e "  uvicorn app.main:app --reload"
echo ""
echo -e "${GREEN}To run tests:${NC}"
echo -e "  conda activate orthoviewer2"
echo -e "  pytest tests/" 