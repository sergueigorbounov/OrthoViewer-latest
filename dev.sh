#!/bin/bash

# =============================================
# BioSemanticViz Development Environment Setup
# =============================================

# Color codes for better output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configurable ports
BACKEND_PORT=8003
FRONTEND_PORT=3000
WEBSOCKET_PORT=8004  # WebSocket port

# Print section header
section() {
  echo -e "\n${GREEN}════════════════════════════════════════════════════════════${NC}"
  echo -e "${BLUE}  $1${NC}"
  echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}\n"
}

# Print step info
step() {
  echo -e "${YELLOW}➤ $1${NC}"
}

# Print error and exit
error() {
  echo -e "${RED}ERROR: $1${NC}"
  exit 1
}

# Check if command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Check if port is in use and kill process if needed
check_port() {
  if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
    step "Port $1 is in use. Killing existing process..."
    lsof -ti :$1 | xargs kill -9 || true
    sleep 1
  fi
}

# Setup signal handling
cleanup() {
  section "Shutting Down All Services"
  kill $(jobs -p) 2>/dev/null || true
  step "All services have been stopped."
  exit 0
}
trap cleanup SIGINT SIGTERM

# Check dependencies
section "Checking Dependencies"

# Check for pnpm (preferred) or npm
if command_exists pnpm; then
  PACKAGE_MANAGER="pnpm"
  step "Using pnpm for package management"
elif command_exists npm; then
  PACKAGE_MANAGER="npm"
  step "Using npm for package management (consider switching to pnpm)"
else
  error "Neither pnpm nor npm is installed. Please install pnpm: https://pnpm.io/installation"
fi

# Check for conda (preferred) or python
if command_exists conda; then
  step "Using conda for Python environment management"
  PYTHON_MANAGER="conda"
elif command_exists python3; then
  step "Using venv for Python environment management (consider switching to conda)"
  PYTHON_MANAGER="venv"
else
  error "Neither conda nor python3 is found. Please install miniconda: https://docs.conda.io/en/latest/miniconda.html"
fi

# Check for ports in use
section "Checking Ports"
check_port $BACKEND_PORT
check_port $FRONTEND_PORT
check_port $WEBSOCKET_PORT  # WebSocket port check

# Set up Python environment
section "Setting Up Python Environment"

if [ "$PYTHON_MANAGER" == "conda" ]; then
  # Setup using conda
  if ! conda env list | grep -q "bio-semantic-viz"; then
    step "Creating conda environment 'bio-semantic-viz'..."
    conda create -y -n bio-semantic-viz python=3.10
  fi
  
  step "Activating conda environment..."
  source "$(conda info --base)/etc/profile.d/conda.sh"
  conda activate bio-semantic-viz || error "Failed to activate conda environment"
  
  step "Installing Python dependencies..."
  pip install -r requirements.txt

  # Install WebSocket dependencies
  step "Installing WebSocket dependencies..."
  pip install websockets uvicorn[standard] || error "Failed to install WebSocket dependencies"
  
  # Install ete3 for phylogeny visualization
  step "Installing ete3 for phylogeny visualization..."
  pip install ete3 || error "Failed to install ete3"
else
  # Setup using venv
  if [ ! -d "venv" ]; then
    step "Creating Python virtual environment..."
    python3 -m venv venv || error "Failed to create virtual environment"
  fi
  
  step "Activating virtual environment..."
  source venv/bin/activate || error "Failed to activate virtual environment"
  
  step "Installing Python dependencies..."
  pip install --upgrade pip
  pip install -r requirements.txt

  # Install WebSocket dependencies
  step "Installing WebSocket dependencies..."
  pip install websockets uvicorn[standard] || error "Failed to install WebSocket dependencies"
  
  # Install ete3 for phylogeny visualization
  step "Installing ete3 for phylogeny visualization..."
  pip install ete3 || error "Failed to install ete3"
fi

# Create required directories
step "Creating required directories..."
mkdir -p backend/app/uploads
mkdir -p logs

# Start backend
section "Starting Backend Server"

step "Starting FastAPI backend on port $BACKEND_PORT..."
cd backend
export PYTHONPATH=$PWD

# Create a temporary CORS configuration for the backend
if [ -f "app/fastapi_main.py" ]; then
  step "Configuring CORS for microservice architecture..."
  TEMP_CONFIG=$(cat << 'EOF'
# Temporary CORS configuration for development
from fastapi.middleware.cors import CORSMiddleware

# Add CORS middleware to allow cross-origin requests between services
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        f"http://localhost:{FRONTEND_PORT}", 
        "*"  # Allow all for development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
EOF
)
  
  # Check if CORS config already exists
  if ! grep -q "CORSMiddleware" app/fastapi_main.py; then
    # Find line with FastAPI app instantiation
    APP_LINE=$(grep -n "app = FastAPI" app/fastapi_main.py | cut -d ':' -f 1)
    if [ -n "$APP_LINE" ]; then
      # Add CORS config after the app instantiation
      APP_LINE=$((APP_LINE + 1))
      sed -i "${APP_LINE}i\\${TEMP_CONFIG}" app/fastapi_main.py
      echo "Added CORS middleware configuration to FastAPI"
    fi
  fi
fi

uvicorn app.fastapi_main:app --host 0.0.0.0 --port $BACKEND_PORT --reload &
cd ..

# Start WebSocket service for communication between services
section "Starting WebSocket Service"
cat > websocket_relay.py << 'EOF'
#!/usr/bin/env python3
import asyncio
import websockets
import json
import logging
import sys
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("websocket_relay")

# Store connected clients
frontend_clients = set()

async def message_relay(websocket, path):
    """Handle WebSocket connections and relay messages between services"""
    client_type = None
    try:
        # Initial handshake to identify the client
        async for message in websocket:
            try:
                data = json.loads(message)
                
                # Register client type on first message
                if not client_type and "client_type" in data:
                    client_type = data["client_type"]
                    if client_type == "frontend":
                        frontend_clients.add(websocket)
                        logger.info(f"Frontend client connected. Total: {len(frontend_clients)}")
                    
                    # Send acknowledgement
                    await websocket.send(json.dumps({
                        "type": "connection_ack",
                        "timestamp": datetime.now().isoformat(),
                        "message": f"Connected as {client_type} client"
                    }))
                    continue
                
                # Broadcast option for messages that should go to all clients
                if "target" in data and data["target"] == "broadcast":
                    if frontend_clients:
                        await asyncio.gather(
                            *[client.send(message) for client in frontend_clients 
                              if client != websocket]  # Don't send back to sender
                        )
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON received: {message[:100]}...")
                
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        # Clean up on disconnect
        if client_type == "frontend" and websocket in frontend_clients:
            frontend_clients.remove(websocket)
            logger.info(f"Frontend client disconnected. Remaining: {len(frontend_clients)}")

async def main():
    # Get port from command line argument
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8004
    logger.info(f"Starting WebSocket relay server on port {port}")
    async with websockets.serve(message_relay, "0.0.0.0", port):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
EOF

# Start WebSocket relay
step "Starting WebSocket relay on port $WEBSOCKET_PORT..."
python websocket_relay.py $WEBSOCKET_PORT &

# Wait for backend to start
step "Waiting for backend to start..."
for i in {1..10}; do
  sleep 2
  if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null; then
    step "Backend server started successfully!"
    break
  fi
  echo -n "."
  if [ $i -eq 10 ]; then
    error "Failed to start backend server after 20 seconds"
  fi
done

# Start frontend
section "Starting Frontend Applications"

# Install and start main frontend with environment variables
step "Setting up main frontend..."
cd frontend

# Check if we need to clean node_modules
if [ -d "node_modules" ] && [ "${CLEAN_INSTALL:-false}" = "true" ]; then
  step "Cleaning existing node_modules for a fresh install..."
  rm -rf node_modules package-lock.json
fi

if [ "$PACKAGE_MANAGER" == "pnpm" ]; then
  step "Installing frontend dependencies using pnpm..."
  pnpm install --no-strict-peer-dependencies

  # Install WebSocket client if needed
  if ! grep -q "socket.io-client" package.json; then
    step "Adding WebSocket client dependency..."
    pnpm add socket.io-client
  fi
  
  step "Starting frontend development server..."
  VITE_BACKEND_URL="http://localhost:$BACKEND_PORT" \
  VITE_WEBSOCKET_URL="ws://localhost:$WEBSOCKET_PORT" \
  pnpm dev --port $FRONTEND_PORT &
else
  step "Installing frontend dependencies using npm..."
  # Use npm ci for a clean install if package-lock.json exists, otherwise use npm install
  if [ -f "package-lock.json" ]; then
    npm ci --legacy-peer-deps
  else
    npm install --legacy-peer-deps
  fi

  # Install WebSocket client if needed
  if ! grep -q "socket.io-client" package.json; then
    step "Adding WebSocket client dependency..."
    npm install --save socket.io-client --legacy-peer-deps
  fi
  
  # Install react-scripts if not already installed
  if ! npm list react-scripts > /dev/null 2>&1; then
    step "Installing react-scripts..."
    npm install --save-dev react-scripts --legacy-peer-deps
  fi
  
  step "Starting frontend development server..."
  REACT_APP_BACKEND_URL="http://localhost:$BACKEND_PORT" \
  REACT_APP_WEBSOCKET_URL="ws://localhost:$WEBSOCKET_PORT" \
  npm start &
fi
cd ..

# Display startup message
section "BioSemanticViz Development Environment Running"
echo -e "${GREEN}▶ Main Frontend:${NC} http://localhost:$FRONTEND_PORT"
echo -e "${GREEN}▶ Backend API:${NC} http://localhost:$BACKEND_PORT"
echo -e "${GREEN}▶ API Documentation:${NC} http://localhost:$BACKEND_PORT/docs"
echo -e "${GREEN}▶ WebSocket Service:${NC} ws://localhost:$WEBSOCKET_PORT"

echo -e "\n${BLUE}Press Ctrl+C to stop all services${NC}"

# Wait for all background processes
wait 