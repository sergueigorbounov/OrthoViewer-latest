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

# Check for conda and orthoviewer2 environment
if command -v conda &> /dev/null; then
  echo -e "${GREEN}Activating conda environment...${NC}"
  if conda env list | grep -q "orthoviewer2"; then
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate orthoviewer2
    echo -e "${GREEN}Activated orthoviewer2 conda environment${NC}"
  else
    echo -e "${YELLOW}Creating orthoviewer2 environment...${NC}"
    if [ -f "environment.yml" ]; then
      conda env create -f environment.yml
      source "$(conda info --base)/etc/profile.d/conda.sh"
      conda activate orthoviewer2
      echo -e "${GREEN}Created and activated orthoviewer2 conda environment${NC}"
    else
      echo -e "${RED}environment.yml not found. Cannot create conda environment.${NC}"
      exit 1
    fi
  fi
else
  echo -e "${YELLOW}Conda not available, using system Python${NC}"
  # Activate virtual environment if it exists
  if [ -d "venv" ]; then
    echo -e "${GREEN}Activating virtual environment...${NC}"
    source venv/bin/activate
  fi
fi

# Install/update requirements using conda
if command -v conda &> /dev/null && conda env list | grep -q "orthoviewer2"; then
  echo -e "${GREEN}Updating conda environment...${NC}"
  conda env update -f environment.yml
else
  echo -e "${YELLOW}Conda not available, using pip as fallback...${NC}"
  if [ -f "requirements.txt" ]; then
    echo -e "${GREEN}Installing requirements...${NC}"
    pip install -r requirements.txt
  fi
fi

# Start backend server
echo -e "${GREEN}Starting FastAPI backend server on port 8002...${NC}"
cd backend
uvicorn app.fastapi_main:app --host 0.0.0.0 --port 8002 --reload &

# Wait for backend to start
echo -e "${YELLOW}Waiting for backend to start...${NC}"
sleep 3

# Start frontend server
echo -e "${GREEN}Starting React frontend on port 3000...${NC}"
cd ../frontend
npm start

# This will keep the script running until the frontend server is stopped
# The backend server runs in the background 