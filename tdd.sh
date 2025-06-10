#!/bin/bash

# Exit on error
set -e

# Output formatting
BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== BioSemanticViz Enhanced TDD Workflow ===${NC}"

# Parse command line arguments
SPECIFIC_TEST=""
RUN_BACKEND=true
RUN_FRONTEND=true
COVERAGE=false
LINT=false
WATCH_FILES=true
BACKEND_PORT=8002
FRONTEND_PORT=3000

while [[ $# -gt 0 ]]; do
  case $1 in
    --test=*)
      SPECIFIC_TEST="${1#*=}"
      shift
      ;;
    --no-backend)
      RUN_BACKEND=false
      shift
      ;;
    --no-frontend)
      RUN_FRONTEND=false
      shift
      ;;
    --coverage)
      COVERAGE=true
      shift
      ;;
    --lint)
      LINT=true
      shift
      ;;
    --no-watch)
      WATCH_FILES=false
      shift
      ;;
    --backend-port=*)
      BACKEND_PORT="${1#*=}"
      shift
      ;;
    --frontend-port=*)
      FRONTEND_PORT="${1#*=}"
      shift
      ;;
    --help)
      echo "Usage: ./tdd.sh [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  --test=TestName          Run specific test pattern"
      echo "  --no-backend            Skip backend startup"
      echo "  --no-frontend           Skip frontend startup"
      echo "  --coverage              Run tests with coverage report"
      echo "  --lint                  Run linting before tests"
      echo "  --no-watch              Run tests once without watch mode"
      echo "  --backend-port=PORT     Backend port (default: 8002)"
      echo "  --frontend-port=PORT    Frontend port (default: 3000)"
      echo "  --help                  Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help for available options"
      exit 1
      ;;
  esac
done

# Check if ports are in use and kill processes if needed
check_port() {
  if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}Port $1 is in use. Killing existing process...${NC}"
    lsof -ti :$1 | xargs kill -9 2>/dev/null || true
    sleep 1
  fi
}

# Setup conda environment for backend
setup_conda_env() {
  echo -e "${CYAN}Setting up Python environment...${NC}"
  
  # Check for conda
  if command -v conda &> /dev/null; then
    echo -e "${GREEN}Using conda for Python environment management${NC}"
    
    # Create environment if it doesn't exist
    if ! conda env list | grep -q "bio-semantic-viz"; then
      echo -e "${YELLOW}Creating conda environment 'bio-semantic-viz'...${NC}"
      conda create -y -n bio-semantic-viz python=3.10
    fi
    
    # Activate environment
    echo -e "${CYAN}Activating conda environment...${NC}"
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate bio-semantic-viz || {
      echo -e "${RED}Failed to activate conda environment${NC}"
      exit 1
    }
    
    # Install/update dependencies using conda
    echo -e "${CYAN}Updating Python environment from environment.yml...${NC}"
    conda env update -f environment.yml
    
    # Verify key packages are available
    if ! python -c "import ete3, fastapi, pytest" 2>/dev/null; then
      echo -e "${YELLOW}Some packages not found, checking conda environment...${NC}"
      conda list | grep -E "(ete3|fastapi|pytest|uvicorn)"
    fi
    
  elif command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Using venv for Python environment management${NC}"
    
    if [ ! -d "venv" ]; then
      echo -e "${CYAN}Creating Python virtual environment...${NC}"
      python3 -m venv venv
    fi
    
    source venv/bin/activate
    # Prefer conda if available, otherwise use pip
    if command -v conda &> /dev/null; then
        echo -e "${CYAN}Installing packages with conda...${NC}"
        conda install -c conda-forge pip fastapi uvicorn sqlalchemy pytest pytest-cov black flake8 mypy websockets -y || {
            echo -e "${YELLOW}Some packages not available in conda, using pip fallback...${NC}"
            pip install --upgrade pip
            pip install -r requirements.txt
            pip install ete3 pytest pytest-cov black flake8 mypy uvicorn[standard] websockets
        }
    else
        pip install --upgrade pip
        pip install -r requirements.txt
        pip install ete3 pytest pytest-cov black flake8 mypy uvicorn[standard] websockets
    fi
  else
    echo -e "${RED}Neither conda nor python3 found. Please install miniconda.${NC}"
    exit 1
  fi
}

# Run backend linting if requested
run_backend_lint() {
  if [ "$LINT" = true ]; then
    echo -e "${CYAN}Running backend linting...${NC}"
    cd backend
    
    echo -e "${YELLOW}Running black (code formatting)...${NC}"
    black --check app/ || {
      echo -e "${YELLOW}Code formatting issues found. Auto-fixing...${NC}"
      black app/
    }
    
    echo -e "${YELLOW}Running flake8 (style checking)...${NC}"
    flake8 app/ --max-line-length=88 --extend-ignore=E203,W503 || true
    
    echo -e "${YELLOW}Running mypy (type checking)...${NC}"
    mypy app/ --ignore-missing-imports || true
    
    cd ..
  fi
}

# Start backend with proper error handling
start_backend() {
  if [ "$RUN_BACKEND" = true ]; then
    echo -e "${YELLOW}Starting FastAPI backend on port $BACKEND_PORT...${NC}"
    check_port $BACKEND_PORT
    
    cd backend
    export PYTHONPATH=$PWD
    
    # Check if FastAPI main file exists
    if [ -f "app/fastapi_main.py" ]; then
      echo -e "${GREEN}Detected FastAPI application${NC}"
      
      # Add development-specific CORS configuration
      cat > app/dev_cors.py << 'EOF'
# Development CORS configuration
from fastapi.middleware.cors import CORSMiddleware

def add_dev_cors(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:3001", 
            f"http://localhost:{FRONTEND_PORT}",
            "*"  # Allow all for development
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
EOF
      
      # Start with uvicorn
      uvicorn app.fastapi_main:app --host 0.0.0.0 --port $BACKEND_PORT --reload &
      BACKEND_PID=$!
      echo -e "${GREEN}Backend started with PID: $BACKEND_PID${NC}"
      
      # Wait for backend to be ready
      echo -e "${CYAN}Waiting for backend to be ready...${NC}"
      for i in {1..10}; do
        if curl -s http://localhost:$BACKEND_PORT/status > /dev/null 2>&1; then
          echo -e "${GREEN}Backend is ready!${NC}"
          break
        fi
        if [ $i -eq 10 ]; then
          echo -e "${YELLOW}Backend taking longer than expected to start${NC}"
        fi
        sleep 1
      done
      
    else
      echo -e "${RED}FastAPI main file not found at backend/app/fastapi_main.py${NC}"
      exit 1
    fi
    
    cd ..
  else
    echo -e "${YELLOW}Skipping backend startup (--no-backend specified)${NC}"
  fi
}

# Run frontend linting if requested
run_frontend_lint() {
  if [ "$LINT" = true ]; then
    echo -e "${CYAN}Running frontend linting...${NC}"
if [ ! -d "frontend" ]; then
    echo "Frontend directory not found, skipping frontend tests..."
    exit 0
fi
    cd frontend
    
    # Run ESLint if available
    if npm list eslint > /dev/null 2>&1; then
      echo -e "${YELLOW}Running ESLint...${NC}"
      npm run lint || true
    fi
    
    # Run TypeScript check
    if [ -f "tsconfig.json" ]; then
      echo -e "${YELLOW}Running TypeScript check...${NC}"
      npx tsc --noEmit || true
    fi
    
    cd ..
  fi
}

# Start tests with enhanced options
start_tests() {
  echo -e "${CYAN}Starting tests...${NC}"
if [ ! -d "frontend" ]; then
    echo "Frontend directory not found, skipping frontend tests..."
    exit 0
fi
  cd frontend
  
  # Build test command
  if [ "$COVERAGE" = true ]; then
    TEST_CMD="npm run test -- --coverage --watchAll=${WATCH_FILES}"
  elif [ "$WATCH_FILES" = false ]; then
    TEST_CMD="npm test -- --watchAll=false"
  else
    TEST_CMD="npm test"
  fi
  
  # Add specific test pattern if provided
  if [ -n "$SPECIFIC_TEST" ]; then
    echo -e "${YELLOW}Testing only: $SPECIFIC_TEST${NC}"
    TEST_CMD="$TEST_CMD -- --testNamePattern=\"$SPECIFIC_TEST\""
  fi
  
  # Try to open in a new terminal, fallback to background
  if command -v gnome-terminal &> /dev/null; then
    echo -e "${GREEN}Opening tests in gnome-terminal...${NC}"
    gnome-terminal --title="BioSemanticViz Tests" -- bash -c "cd $(pwd) && $TEST_CMD; exec bash" &
    TESTS_PID=$!
  elif command -v xterm &> /dev/null; then
    echo -e "${GREEN}Opening tests in xterm...${NC}"
    xterm -title "BioSemanticViz Tests" -e "cd $(pwd) && $TEST_CMD" &
    TESTS_PID=$!
  elif command -v konsole &> /dev/null; then
    echo -e "${GREEN}Opening tests in konsole...${NC}"
    konsole --title "BioSemanticViz Tests" -e bash -c "cd $(pwd) && $TEST_CMD; exec bash" &
    TESTS_PID=$!
  else
    echo -e "${YELLOW}No terminal emulator found, running tests in background...${NC}"
    eval $TEST_CMD &
    TESTS_PID=$!
  fi
  
  cd ..
}

# Start frontend development server
start_frontend() {
  if [ "$RUN_FRONTEND" = true ]; then
    echo -e "${CYAN}Setting up frontend...${NC}"
    check_port $FRONTEND_PORT
    
if [ ! -d "frontend" ]; then
    echo "Frontend directory not found, skipping frontend tests..."
    exit 0
fi
    cd frontend
    
    # Install dependencies if node_modules doesn't exist
    if [ ! -d "node_modules" ]; then
      echo -e "${YELLOW}Installing frontend dependencies...${NC}"
      npm install --legacy-peer-deps
    fi
    
    # Sleep to allow test terminal to initialize
    sleep 2
    
    echo -e "${YELLOW}Starting frontend development server on port $FRONTEND_PORT...${NC}"
    
    # Set environment variables
    export REACT_APP_BACKEND_URL="http://localhost:$BACKEND_PORT"
    export PORT=$FRONTEND_PORT
    
    npm start &
    FRONTEND_PID=$!
    echo -e "${GREEN}Frontend started with PID: $FRONTEND_PID${NC}"
    
    cd ..
  else
    echo -e "${YELLOW}Skipping frontend startup (--no-frontend specified)${NC}"
  fi
}

# Enhanced cleanup function
cleanup() {
  echo -e "\n${YELLOW}Shutting down TDD environment...${NC}"
  
  # Kill processes if they exist
  [ -n "$FRONTEND_PID" ] && kill $FRONTEND_PID 2>/dev/null && echo -e "${GREEN}Frontend stopped${NC}"
  [ -n "$TESTS_PID" ] && kill $TESTS_PID 2>/dev/null && echo -e "${GREEN}Tests stopped${NC}"
  [ -n "$BACKEND_PID" ] && kill $BACKEND_PID 2>/dev/null && echo -e "${GREEN}Backend stopped${NC}"
  
  # Clean up any remaining processes on the ports
  lsof -ti :$BACKEND_PORT 2>/dev/null | xargs kill -9 2>/dev/null || true
  lsof -ti :$FRONTEND_PORT 2>/dev/null | xargs kill -9 2>/dev/null || true
  
  echo -e "${GREEN}TDD environment cleanup complete!${NC}"
  exit 0
}

# Set up signal handling
trap cleanup SIGINT SIGTERM

# Main execution flow
echo -e "${CYAN}Initializing TDD environment...${NC}"

# Setup Python environment
setup_conda_env

# Run linting if requested
run_backend_lint
run_frontend_lint

# Start services
start_backend
start_tests
start_frontend

# Display status
echo -e "\n${GREEN}=== TDD Environment is Running ===${NC}"
echo -e "${CYAN}Services:${NC}"
[ -n "$BACKEND_PID" ] && echo -e "  ${GREEN}✓${NC} Backend: http://localhost:$BACKEND_PORT (PID: $BACKEND_PID)"
[ -n "$TESTS_PID" ] && echo -e "  ${GREEN}✓${NC} Tests: Running in watch mode (PID: $TESTS_PID)"
[ -n "$FRONTEND_PID" ] && echo -e "  ${GREEN}✓${NC} Frontend: http://localhost:$FRONTEND_PORT (PID: $FRONTEND_PID)"

echo -e "\n${CYAN}Quick Commands:${NC}"
echo -e "  ${YELLOW}Backend API Docs:${NC} http://localhost:$BACKEND_PORT/docs"
echo -e "  ${YELLOW}Test Coverage:${NC} Run with --coverage flag"
echo -e "  ${YELLOW}Specific Test:${NC} Use --test=TestName"
echo -e "  ${YELLOW}Linting:${NC} Use --lint flag"

echo -e "\n${BLUE}Press Ctrl+C to stop all services${NC}"
echo -e "${GREEN}Happy Test-Driven Development! 🧬✨${NC}"

# Wait for user interrupt
wait