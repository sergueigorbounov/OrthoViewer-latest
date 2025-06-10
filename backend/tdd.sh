#!/bin/bash

# TDD Development Script for Backend
# Uses conda environment for dependency management

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting TDD Development Environment${NC}"

# Check for conda
if ! command -v conda &> /dev/null; then
    echo -e "${RED}Conda is required but not installed. Please install miniforge or miniconda.${NC}"
    exit 1
fi

# Activate conda environment
echo -e "${YELLOW}Setting up conda environment...${NC}"
if conda env list | grep -q "orthoviewer2"; then
    echo -e "${GREEN}Activating existing orthoviewer2 environment${NC}"
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate orthoviewer2
else
    echo -e "${YELLOW}Creating orthoviewer2 environment from environment.yml...${NC}"
    if [ -f "../environment.yml" ]; then
        conda env create -f ../environment.yml
    elif [ -f "environment.yml" ]; then
        conda env create -f environment.yml
    else
        echo -e "${RED}environment.yml not found${NC}"
        exit 1
    fi
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate orthoviewer2
fi

# Update environment with latest dependencies
echo -e "${YELLOW}Updating conda environment...${NC}"
if [ -f "../environment.yml" ]; then
    conda env update -f ../environment.yml
elif [ -f "environment.yml" ]; then
    conda env update -f environment.yml
fi

# Verify required packages are installed
echo -e "${YELLOW}Verifying TDD dependencies...${NC}"
conda list | grep -E "(pytest|black|flake8|mypy)" || {
    echo -e "${YELLOW}Installing additional TDD tools...${NC}"
    conda install -c conda-forge pytest pytest-cov black flake8 mypy -y
}

echo -e "${GREEN}TDD Environment Ready!${NC}"
echo -e "${YELLOW}Available commands:${NC}"
echo "  pytest                    # Run all tests"
echo "  pytest --cov             # Run tests with coverage"
echo "  black .                   # Format code"
echo "  flake8 .                  # Lint code"
echo "  mypy .                    # Type checking"

# Run tests if requested
if [ "$1" = "test" ]; then
    echo -e "${GREEN}Running tests...${NC}"
    pytest --cov=app tests/
elif [ "$1" = "format" ]; then
    echo -e "${GREEN}Formatting code...${NC}"
    black .
elif [ "$1" = "lint" ]; then
    echo -e "${GREEN}Linting code...${NC}"
    flake8 .
elif [ "$1" = "typecheck" ]; then
    echo -e "${GREEN}Type checking...${NC}"
    mypy .
elif [ "$1" = "all" ]; then
    echo -e "${GREEN}Running full TDD cycle...${NC}"
    black .
    flake8 .
    mypy .
    pytest --cov=app tests/
elif [ "$1" = "watch" ]; then
    echo -e "${GREEN}Running tests in watch mode...${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
    conda run -n orthoviewer2 ptw tests/ --runner "python -m pytest tests/ --tb=short -v"
fi