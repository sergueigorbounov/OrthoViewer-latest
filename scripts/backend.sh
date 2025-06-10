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

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "❌ conda is not installed or not in PATH"
    echo "Please install conda first: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

# Check if conda environment exists
ENV_NAME="orthoviewer2"
if ! conda env list | grep -q "^$ENV_NAME "; then
    echo "❌ Conda environment '$ENV_NAME' not found"
    echo "Create it with: conda env create -f environment.yml"
    exit 1
fi

echo "🔧 Activating conda environment: $ENV_NAME"
eval "$(conda shell.bash hook)"
conda activate $ENV_NAME

# Verify we're in the right environment
if [[ "$CONDA_DEFAULT_ENV" != "$ENV_NAME" ]]; then
    echo "❌ Failed to activate conda environment"
    exit 1
fi

# Navigate to backend directory
cd "$(dirname "$0")/../backend" || exit 1

# Verify dependencies are installed
python -c "import fastapi, uvicorn" || {
    echo -e "${RED}Missing dependencies. Please check environment.yml${NC}"
    exit 1
}

# Start the backend server
echo -e "${GREEN}Starting FastAPI server...${NC}"
echo "   Environment: $ENV_NAME"
echo "   Port: 8002"
echo "   URL: http://localhost:8002"
echo ""
uvicorn app.main:app --reload --host 0.0.0.0 --port 8002