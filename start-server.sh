#!/bin/bash

# OrthoViewer Server Startup using conda
# Starts the OrthoViewer application with conda environment

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Starting OrthoViewer server with conda...${NC}"

# Check if conda environment exists
ENV_NAME="orthoviewer2"
if ! conda env list | grep -q "$ENV_NAME"; then
    echo -e "${YELLOW}conda environment '$ENV_NAME' not found. Creating it...${NC}"
    
    # Create conda environment if it doesn't exist
    if [ -f "environment.yml" ]; then
        conda env create -f environment.yml
    else
        echo -e "${RED}environment.yml not found. Please ensure it exists in the project root.${NC}"
        exit 1
    fi
fi

# Activate conda environment
source $(conda info --base)/etc/profile.d/conda.sh
conda activate "$ENV_NAME"

# Verify dependencies are installed
echo -e "${YELLOW}Verifying dependencies...${NC}"
python -c "import fastapi, uvicorn, sqlalchemy" || {
    echo -e "${RED}Missing dependencies. Please check environment.yml${NC}"
    exit 1
}

# Navigate to backend directory
cd backend

# Start the server
echo "🚀 Starting FastAPI backend server..."
echo "   Environment: $ENV_NAME" 
echo "   Port: 8002"
echo "   URL: http://localhost:8002"
echo ""

# Start the server  
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload 