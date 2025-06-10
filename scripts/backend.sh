#!/bin/bash

# Backend startup script using conda
# Starts the OrthoViewer FastAPI backend

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Starting OrthoViewer backend with conda...${NC}"

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

# Verify dependencies are installed
python -c "import fastapi, uvicorn" || {
    echo -e "${RED}Missing dependencies. Please check environment.yml${NC}"
    exit 1
}

# Start the backend server
echo -e "${GREEN}Starting FastAPI server...${NC}"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000