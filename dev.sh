#!/bin/bash

# =============================================
# OrthoViewer2 Development Environment Script
# Phylogenetic Analysis Platform - Vite Frontend
# =============================================

set -o pipefail

# Colors
INFO='\033[0;36m'
SUCCESS='\033[0;32m'
WARNING='\033[1;33m'
ERROR='\033[0;31m'
RESET='\033[0m'

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --help)
      echo "OrthoViewer2 Development Environment"
      echo "Usage: $0 [--help]"
      echo ""
      echo "This script starts the OrthoViewer2 development environment with:"
      echo "  - Backend FastAPI server on port 8003"
      echo "  - Frontend Vite development server on port 5173"
      echo "  - API documentation at http://localhost:8003/docs"
      echo ""
      echo "Requirements:"
      echo "  - Python 3.9+ (conda/miniforge recommended)"
      echo "  - Node.js 16+ with npm"
      echo "  - frontend-vite/ directory with Vite React app"
      echo "  - backend/ directory with FastAPI app"
      exit 0
      ;;
    *)
      shift
      ;;
  esac
done

info() {
    echo -e "${INFO}→ $1${RESET}"
}

success() {
    echo -e "${SUCCESS}✓ $1${RESET}"
}

warning() {
    echo -e "${WARNING}! $1${RESET}"
}

error() {
    echo -e "${ERROR}✗ $1${RESET}"
}

# Check if a command is available
check_command() {
    if ! command -v $1 &> /dev/null; then
        error "$1 command not found"
        return 1
    else
        success "$1 is available"
        return 0
    fi
}

# Check if port is in use
is_port_in_use() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Kill process using a specific port
kill_port_process() {
    local port=$1
    if is_port_in_use $port; then
        local pid=$(lsof -ti :$port)
        warning "Port $port is in use by PID $pid. Terminating process."
        kill -9 $pid 2>/dev/null || true
        sleep 2
    fi
}

# Install Vite frontend dependencies
install_vite_deps() {
    info "Checking Vite frontend dependencies..."
    cd frontend-vite
    
    # Check if node_modules exists, if not, install dependencies
    if [ ! -d "node_modules" ]; then
        info "Installing frontend dependencies..."
        npm install
    fi
    
    # Check for Vite specifically
    if ! npm list vite >/dev/null 2>&1; then
        info "Installing Vite dependencies..."
        npm install --save-dev vite @vitejs/plugin-react
    fi
    
    success "Vite frontend dependencies ready"
    cd ..
}

# Define ports
BACKEND_PORT=8003
FRONTEND_PORT=5173

# Create logs directory
mkdir -p logs

# Store background process PIDs for cleanup
BACKEND_PID=""
FRONTEND_PID=""

# Cleanup function
cleanup() {
    echo ""
    info "Shutting down development environment..."
    
    if [ ! -z "$BACKEND_PID" ] && kill -0 $BACKEND_PID 2>/dev/null; then
        info "Stopping backend (PID: $BACKEND_PID)"
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$FRONTEND_PID" ] && kill -0 $FRONTEND_PID 2>/dev/null; then
        info "Stopping frontend (PID: $FRONTEND_PID)"
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    # Clean up any remaining processes on our ports
    kill_port_process $BACKEND_PORT
    kill_port_process $FRONTEND_PORT
    
    success "Development environment stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Check basic requirements
echo "Starting OrthoViewer2 Development Environment"
echo "============================================="
info "Using Vite frontend with React"

# Check if we're in the right directory
if [ ! -d "backend" ]; then
    error "Backend directory not found. Please run from project root directory."
    exit 1
fi

if [ ! -d "frontend-vite" ]; then
    error "frontend-vite directory not found."
    error "This script requires a Vite-based React frontend in frontend-vite/"
    exit 1
fi

# Check for Node.js
info "Checking for Node.js..."
if ! check_command node; then
    error "Node.js is required for the frontend. Please install it from https://nodejs.org"
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 16 ]; then
    warning "Node.js version $NODE_VERSION detected. Version 16+ recommended for Vite."
fi

# Check for npm
info "Checking for npm..."
if ! check_command npm; then
    error "npm is required for the frontend. Please install Node.js which includes npm."
    exit 1
fi

# Check for Python
info "Checking for Python..."
PYTHON_CMD="python"
if ! check_command python; then
    info "Trying python3 instead..."
    if ! check_command python3; then
        error "Python is required for the backend. Please install Python 3.9+ from https://python.org"
        exit 1
    else
        PYTHON_CMD="python3"
    fi
fi

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
if [ "$(printf '%s\n' "3.9" "$PYTHON_VERSION" | sort -V | head -n1)" != "3.9" ]; then
    warning "Python version $PYTHON_VERSION detected. Version 3.9+ recommended."
fi

# Clear any processes using our ports
info "Cleaning up existing processes..."
kill_port_process $BACKEND_PORT
kill_port_process $FRONTEND_PORT

# Check if conda is available
CONDA_AVAILABLE=false
if command -v conda &> /dev/null; then
    CONDA_AVAILABLE=true
    info "Conda is available: $(conda --version)"
    
    # Check for orthoviewer2 environment
    if conda env list | grep -q "orthoviewer2"; then
        info "Activating orthoviewer2 environment"
        source "$(conda info --base)/etc/profile.d/conda.sh"
        conda activate orthoviewer2
        success "Activated orthoviewer2 conda environment"
    else
        warning "orthoviewer2 conda environment not found"
        info "Creating orthoviewer2 environment from environment.yml..."
        if [ -f "environment.yml" ]; then
            conda env create -f environment.yml
            source "$(conda info --base)/etc/profile.d/conda.sh"
            conda activate orthoviewer2
            success "Created and activated orthoviewer2 conda environment"
        else
            error "environment.yml not found. Cannot create environment."
            exit 1
        fi
    fi
else
    warning "Conda not found, using system Python"
    info "For better package management, consider installing Miniforge: https://github.com/conda-forge/miniforge"
fi

# Check backend dependencies
info "Checking backend dependencies..."
if ! $PYTHON_CMD -c "import fastapi, uvicorn" 2>/dev/null; then
    warning "FastAPI or uvicorn not installed."
    if [ "$CONDA_AVAILABLE" = true ] && conda env list | grep -q "orthoviewer2"; then
        info "Installing packages in activated conda environment..."
        # Use conda-run to ensure we're in the right environment
        conda run -n orthoviewer2 python -c "import fastapi, uvicorn; print('Dependencies available')" 2>/dev/null || {
            info "Installing FastAPI and uvicorn in conda environment..."
            conda install -n orthoviewer2 -c conda-forge fastapi uvicorn python-multipart -y
        }
        success "Backend dependencies ready in conda environment"
    else
        warning "Installing required packages with conda (creating basic environment)..."
        
        # Try to create a minimal conda environment if it doesn't exist
        if [ "$CONDA_AVAILABLE" = true ]; then
            info "Creating minimal conda environment for OrthoViewer..."
            
            # Create a temporary environment.yml
            cat > temp_environment.yml << 'EOF'
name: orthoviewer2
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.9
  - fastapi
  - uvicorn
  - python-multipart
  - pip
EOF
            
            conda env create -f temp_environment.yml --force 2>/dev/null || {
                warning "Failed to create conda environment, using pip fallback..."
                cd backend
                if [ -f "requirements.txt" ]; then
                    $PYTHON_CMD -m pip install -r requirements.txt
                else
                    $PYTHON_CMD -m pip install fastapi uvicorn python-multipart
                fi
                cd ..
            }
            
            # Clean up temporary file
            rm -f temp_environment.yml
        else
            # Fallback to pip if conda not available
            cd backend
            if [ -f "requirements.txt" ]; then
                $PYTHON_CMD -m pip install -r requirements.txt
            else
                $PYTHON_CMD -m pip install fastapi uvicorn python-multipart
            fi
            cd ..
        fi
    fi
    
    # Re-check with conda environment
    if [ "$CONDA_AVAILABLE" = true ] && conda env list | grep -q "orthoviewer2"; then
        if conda run -n orthoviewer2 python -c "import fastapi, uvicorn" 2>/dev/null; then
            success "Backend dependencies verified in conda environment"
        else
            error "Failed to install backend dependencies in conda environment"
            exit 1
        fi
    elif ! $PYTHON_CMD -c "import fastapi, uvicorn" 2>/dev/null; then
        error "Failed to install backend dependencies. Try:"
        echo "  conda env create -f environment.yml && conda activate orthoviewer2"
        echo "  OR"
        echo "  cd backend && pip install fastapi uvicorn python-multipart"
        exit 1
    fi
else
    success "Backend dependencies are installed"
fi

# Check for FastAPI app
info "Locating FastAPI application..."
FASTAPI_MAIN=""
if [ -f "backend/app/main.py" ]; then
    FASTAPI_MAIN="app.main:app"
    success "Found FastAPI app: backend/app/main.py"
elif [ -f "backend/app/fastapi_main.py" ]; then
    FASTAPI_MAIN="app.fastapi_main:app"
    success "Found FastAPI app: backend/app/fastapi_main.py"
elif [ -f "backend/main.py" ]; then
    FASTAPI_MAIN="main:app"
    success "Found FastAPI app: backend/main.py"
else
    error "FastAPI app not found. Expected one of:"
    echo "  - backend/app/main.py"
    echo "  - backend/app/fastapi_main.py"
    echo "  - backend/main.py"
    exit 1
fi

# Test FastAPI app import
info "Testing FastAPI app import..."
cd backend
export PYTHONPATH=$PWD
IMPORT_MODULE="${FASTAPI_MAIN%:*}"
IMPORT_APP="${FASTAPI_MAIN#*:}"
if $PYTHON_CMD -c "
import sys
sys.path.insert(0, '.')
try:
    exec('from $IMPORT_MODULE import $IMPORT_APP')
    print('SUCCESS: FastAPI app imported')
except Exception as e:
    print(f'WARNING: Import failed - {e}')
" 2>/dev/null | grep -q "SUCCESS"; then
    success "FastAPI app imports successfully"
else
    warning "FastAPI app import test failed. Continuing anyway - app may still work."
fi
cd ..

# Start the backend
info "Starting backend server on port $BACKEND_PORT..."
cd backend
if [ "$CONDA_AVAILABLE" = true ] && conda env list | grep -q "orthoviewer2"; then
    # Use conda run to ensure proper environment
    (conda run -n orthoviewer2 python -m uvicorn $FASTAPI_MAIN --host 0.0.0.0 --port $BACKEND_PORT --reload > ../logs/backend.log 2>&1) &
else
    # Fallback to regular python
    ($PYTHON_CMD -m uvicorn $FASTAPI_MAIN --host 0.0.0.0 --port $BACKEND_PORT --reload > ../logs/backend.log 2>&1) &
fi
BACKEND_PID=$!
cd ..

# Wait for backend to start
info "Waiting for backend to start..."
BACKEND_STARTED=false
for i in {1..30}; do
    sleep 1
    
    # Multiple health check methods
    if command -v curl >/dev/null 2>&1; then
        # Use curl if available
        if curl -f -s http://localhost:$BACKEND_PORT/ >/dev/null 2>&1; then
            success "Backend is responding on http://localhost:$BACKEND_PORT"
            BACKEND_STARTED=true
            break
        elif curl -f -s http://localhost:$BACKEND_PORT/docs >/dev/null 2>&1; then
            success "Backend docs are available at http://localhost:$BACKEND_PORT/docs"
            BACKEND_STARTED=true
            break
        elif curl -f -s http://localhost:$BACKEND_PORT/api/health >/dev/null 2>&1; then
            success "Backend health endpoint is responding"
            BACKEND_STARTED=true
            break
        fi
    fi
    
    # Fallback: check if port is in use
    if is_port_in_use $BACKEND_PORT; then
        if [ $i -gt 15 ]; then  # Give it more time after port is active
            success "Backend port is active - server appears to be running"
            success "Backend URL: http://localhost:$BACKEND_PORT"
            BACKEND_STARTED=true
            break
        fi
    fi
    
    # Check if process is still running
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        error "Backend process died. Check logs/backend.log for details."
        break
    fi
    
    # Show progress
    if [ $((i % 5)) -eq 0 ]; then
        echo -n " (${i}s)"
    else
        echo -n "."
    fi
done
echo ""  # New line after dots

# Show backend logs if it failed to start
if [ "$BACKEND_STARTED" = false ]; then
    warning "Showing last 20 lines of backend logs:"
    if [ -f "logs/backend.log" ]; then
        tail -n 20 logs/backend.log
    else
        echo "No backend log file found."
    fi
fi

# Install Vite frontend dependencies
install_vite_deps

# Start the frontend
info "Setting up Vite frontend..."
cd frontend-vite

# Create or update environment files
info "Configuring frontend environment..."
echo "VITE_BACKEND_URL=/api" > .env
echo "NODE_ENV=development" >> .env
success "Created/updated .env file with backend URL"

# Start the Vite development server
info "Starting Vite development server on port $FRONTEND_PORT..."
(npm run dev > ../logs/frontend.log 2>&1) &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
info "Waiting for frontend to start..."
FRONTEND_STARTED=false
for i in {1..30}; do
    sleep 1
    if is_port_in_use $FRONTEND_PORT; then
        success "Frontend is running on http://localhost:$FRONTEND_PORT"
        FRONTEND_STARTED=true
        break
    fi
    
    # Check if process is still running
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        error "Frontend process died. Check logs/frontend.log for details."
        break
    fi
    
    # Show progress for frontend
    if [ $((i % 5)) -eq 0 ]; then
        echo -n " (${i}s)"
    else
        echo -n "."
    fi
done
echo ""  # New line after dots

# Show frontend logs if it failed to start
if [ "$FRONTEND_STARTED" = false ]; then
    warning "Showing last 20 lines of frontend logs:"
    if [ -f "logs/frontend.log" ]; then
        tail -n 20 logs/frontend.log
    else
        echo "No frontend log file found."
    fi
fi

# Summary of services
echo ""
echo "Development Environment Status:"
echo "------------------------------"
if [ "$BACKEND_STARTED" = true ]; then
    success "Backend: Running on http://localhost:$BACKEND_PORT (PID: $BACKEND_PID)"
    success "API docs: http://localhost:$BACKEND_PORT/docs"
    success "Health check: http://localhost:$BACKEND_PORT/api/health"
else
    error "Backend: Not running"
fi

if [ "$FRONTEND_STARTED" = true ]; then
    success "Frontend (Vite): Running on http://localhost:$FRONTEND_PORT (PID: $FRONTEND_PID)"
else
    error "Frontend (Vite): Not running"
fi

# Provide log file locations
echo ""
info "Log files:"
info "- Backend: ./logs/backend.log"
info "- Frontend: ./logs/frontend.log"

echo ""
if [ "$FRONTEND_STARTED" = true ] && [ "$BACKEND_STARTED" = true ]; then
    success "Development environment started successfully!"
    echo ""
    success "🧬 OrthoViewer2 Phylogenetic Analysis Platform Ready!"
    echo ""
    info "Available endpoints:"
    info "- Frontend:      http://localhost:$FRONTEND_PORT"
    info "- Backend API:   http://localhost:$BACKEND_PORT"
    info "- API docs:      http://localhost:$BACKEND_PORT/docs"
    info "- Health check:  http://localhost:$BACKEND_PORT/api/health"
    echo ""
    info "Open http://localhost:$FRONTEND_PORT in your browser to start analyzing phylogenetic data"
elif [ "$BACKEND_STARTED" = true ]; then
    warning "Backend is running, but frontend failed to start."
    info "You can still access:"
    info "- Backend API:   http://localhost:$BACKEND_PORT"
    info "- API docs:      http://localhost:$BACKEND_PORT/docs"
    echo ""
    info "To restart frontend only:"
    info "  cd frontend-vite && npm run dev"
elif [ "$FRONTEND_STARTED" = true ]; then
    warning "Frontend is running, but backend failed to start."
    info "Frontend may not function properly without the backend."
else
    error "Both frontend and backend failed to start. Check the logs for details."
fi

echo ""
info "Press Ctrl+C to stop all services"

echo ""
info "Troubleshooting tips:"
info "- If you see WebSocket connection errors: Restart with Ctrl+C then ./dev.sh"
info "- If frontend stops responding: Check logs/frontend.log for errors"
info "- If file watching stops working: increase fs.inotify.max_user_watches"
info "  sudo sysctl fs.inotify.max_user_watches=524288"
info "- For memory issues: close other applications or restart terminal"
info "- Frontend-only restart: cd frontend-vite && npm run dev"

# Wait for user to stop the script
wait