#!/bin/bash

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if a port is in use
function is_port_in_use() {
  if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
    return 0
  else
    return 1
  fi
}

echo -e "${GREEN}Starting BioSemanticViz FastAPI backend...${NC}"

# Check if backend port is already in use
if is_port_in_use 8002; then
  echo -e "${YELLOW}Port 8002 is already in use. Killing existing process...${NC}"
  lsof -ti :8002 | xargs kill -9
  sleep 1
fi

# Check if frontend port is already in use
if is_port_in_use 3000; then
  echo -e "${YELLOW}Port 3000 is already in use. Killing existing process...${NC}"
  lsof -ti :3000 | xargs kill -9
  sleep 1
fi

# Create directories if they don't exist
mkdir -p backend/app/uploads

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

# Start backend server
echo -e "${GREEN}Starting FastAPI backend server on port 8002...${NC}"
cd backend || exit_with_error "Failed to change to backend directory"
echo_info "Starting backend on port $BACKEND_PORT..."
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload &

# Wait for backend to start
echo -e "${YELLOW}Waiting for backend to start...${NC}"
sleep 3

# Start frontend server
echo -e "${GREEN}Starting React frontend on port 3000...${NC}"
cd ../frontend
npm start

# This will keep the script running until the frontend server is stopped
# The backend server runs in the background 