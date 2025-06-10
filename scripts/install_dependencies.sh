#!/bin/bash

# Dependency Installation Script using conda
# Installs all dependencies for OrthoViewer project

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}Installing OrthoViewer dependencies using conda...${NC}"

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo -e "${RED}conda is not installed. Please install Miniconda or Anaconda first.${NC}"
    echo -e "${YELLOW}Download from: https://docs.conda.io/en/latest/miniconda.html${NC}"
    exit 1
fi

# Function to check if conda environment exists
check_conda_env() {
    conda env list | grep -q "^$1 "
}

# Set up backend conda environment
echo -e "${BLUE}Setting up backend conda environment...${NC}"
cd backend

if [ -f "environment.yml" ]; then
    ENV_NAME=$(grep "name:" environment.yml | cut -d' ' -f2)
    
    if check_conda_env "$ENV_NAME"; then
        echo -e "${YELLOW}Conda environment '$ENV_NAME' already exists. Updating...${NC}"
        conda env update -f environment.yml
    else
        echo -e "${YELLOW}Creating conda environment '$ENV_NAME'...${NC}"
        conda env create -f environment.yml
    fi
    
    # Activate environment and verify
    source $(conda info --base)/etc/profile.d/conda.sh
    conda activate "$ENV_NAME"
    
    echo -e "${GREEN}✅ Backend conda environment setup complete!${NC}"
    
    # Verify key packages
    echo -e "${BLUE}Verifying backend installation...${NC}"
    python -c "import fastapi; print(f'FastAPI: {fastapi.__version__}')" || echo -e "${RED}FastAPI not found${NC}"
    python -c "import uvicorn; print(f'Uvicorn: {uvicorn.__version__}')" || echo -e "${RED}Uvicorn not found${NC}"
    
    conda deactivate
else
    echo -e "${RED}backend/environment.yml not found${NC}"
    exit 1
fi

cd ..

# Set up frontend dependencies
echo -e "${BLUE}Setting up frontend dependencies...${NC}"
cd frontend-vite

if [ ! -f "package.json" ]; then
    echo -e "${RED}package.json not found in frontend-vite directory${NC}"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}npm is not installed. Please install Node.js and npm first.${NC}"
    exit 1
fi

# Install frontend dependencies
echo -e "${YELLOW}Installing frontend packages...${NC}"
npm install

echo -e "${GREEN}✅ Frontend dependencies installed!${NC}"

cd ..

# Summary
echo ""
echo -e "${GREEN}🎉 All dependencies installed successfully!${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo -e "  1. Backend: conda activate $ENV_NAME"
echo -e "  2. Frontend: cd frontend-vite && npm run dev"
echo -e "  3. Or use: ./dev.sh to start both services"
echo "" 