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

# Set up environment
if [ -f "environment.yml" ]; then
  # Check if conda environment exists and activate it
  ENV_NAME=$(grep "name:" environment.yml | cut -d' ' -f2)
  if conda info --envs | grep -q "$ENV_NAME"; then
    echo -e "${BLUE}Activating conda environment: $ENV_NAME${NC}"
    eval "$(conda shell.bash hook)" && conda activate "$ENV_NAME"
  else
    echo -e "${YELLOW}Creating conda environment from environment.yml...${NC}"
    conda env create -f environment.yml
    eval "$(conda shell.bash hook)" && conda activate "$ENV_NAME"
  fi
else
  # Use virtual environment
  if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python -m venv .venv
  fi
  echo -e "${BLUE}Activating virtual environment...${NC}"
  source .venv/bin/activate
  
  # Install requirements
  echo -e "${BLUE}Installing requirements...${NC}"
  pip install -r requirements.txt
  
  # Install test requirements if they exist
  if [ -f "requirements-test.txt" ]; then
    pip install -r requirements-test.txt
  fi
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