#!/bin/bash
set -e

# Usage message
if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
  echo "Usage: ./run-app.sh [command]"
  echo "Commands:"
  echo "  start       - Start both backend and frontend (default)"
  echo "  backend     - Start only backend"
  echo "  frontend    - Start only frontend"
  echo "  test        - Run tests for both backend and frontend"
  echo "  docker      - Run the application using Docker"
  echo "  docker-dev  - Run the application using Docker in development mode"
  exit 0
fi

# Command selection
COMMAND=${1:-start}

# Helper function to start backend
start_backend() {
  echo "Starting backend..."
  cd backend
  ./tdd.sh start &
  BACKEND_PID=$!
  cd ..
  echo "Backend started with PID: $BACKEND_PID"
}

# Helper function to start frontend
start_frontend() {
  echo "Starting frontend..."
  cd frontend-vite
  ./tdd.sh start &
  FRONTEND_PID=$!
  cd ..
  echo "Frontend started with PID: $FRONTEND_PID"
}

# Helper function to run backend tests
test_backend() {
  echo "Running backend tests..."
  cd backend
  ./tdd.sh test
  cd ..
}

# Helper function to run frontend tests
test_frontend() {
  echo "Running frontend tests..."
  cd frontend-vite
  ./tdd.sh test
  cd ..
}

# Make scripts executable
chmod +x backend/tdd.sh
chmod +x frontend-vite/tdd.sh

case $COMMAND in
  start)
    start_backend
    start_frontend
    
    # Wait for both processes
    echo "Application is running. Press Ctrl+C to stop."
    trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
    wait
    ;;
  backend)
    cd backend
    ./tdd.sh start
    ;;
  frontend)
    cd frontend-vite
    ./tdd.sh start
    ;;
  test)
    test_backend
    test_frontend
    ;;
  docker)
    echo "Starting application with Docker..."
    docker-compose up
    ;;
  docker-dev)
    echo "Starting application with Docker in development mode..."
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
    ;;
  *)
    echo "Unknown command: $COMMAND"
    echo "Use --help to see available commands"
    exit 1
    ;;
esac