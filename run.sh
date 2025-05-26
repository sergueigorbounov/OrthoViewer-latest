#!/bin/bash

# Display help message
function show_help {
    echo "Usage: ./run.sh [command]"
    echo ""
    echo "Available commands:"
    echo "  backend             - Start the backend server"
    echo "  frontend            - Start the frontend development server"
    echo "  docker-backend      - Start the backend in Docker"
    echo "  docker-frontend     - Start the frontend in Docker"
    echo "  docker-compose      - Start all services with Docker Compose"
    echo "  test-unit           - Run backend unit tests"
    echo "  test-integration    - Run backend integration tests"
    echo "  test-performance    - Run performance tests"
    echo "  test-e2e            - Run end-to-end tests"
    echo "  test-all            - Run all tests"
    echo "  clean               - Clean temporary files and Docker containers"
    echo "  help                - Show this help message"
    echo ""
}

# Check if scripts directory exists
if [ ! -d "scripts" ]; then
    echo "Error: scripts directory not found. Make sure you are in the project root."
    exit 1
fi

# Execute command based on argument
case "$1" in
    backend)
        ./scripts/backend.sh
        ;;
    frontend)
        ./scripts/frontend.sh
        ;;
    docker-backend)
        ./scripts/docker-backend.sh
        ;;
    docker-frontend)
        ./scripts/docker-frontend.sh
        ;;
    docker-compose)
        docker-compose up
        ;;
    test-unit)
        ./scripts/test-unit.sh
        ;;
    test-integration)
        ./scripts/test-integration.sh
        ;;
    test-performance)
        ./scripts/test-performance.sh
        ;;
    test-e2e)
        ./scripts/test-e2e.sh
        ;;
    test-all)
        ./scripts/test-all.sh
        ;;
    clean)
        # Stop and remove Docker containers
        docker-compose down
        docker rm $(docker ps -a -q -f name=biosemantic) 2>/dev/null || true
        
        # Remove temporary files
        find . -name "*.pyc" -delete
        find . -name "__pycache__" -type d -exec rm -rf {} +
        find . -name ".pytest_cache" -type d -exec rm -rf {} +
        find backend -name "coverage_reports" -type d -exec rm -rf {} +
        
        echo "Cleaned up containers and temporary files."
        ;;
    help|*)
        show_help
        ;;
esac