#!/bin/bash

# Build script for OrthoViewer Docker images
# Usage: ./build-images.sh [local|prod|all]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to build images for a specific environment
build_images() {
    local env=$1
    local compose_file=""
    
    if [ "$env" = "local" ]; then
        compose_file="docker-compose-local.yml"
        print_status "Building local development images..."
    elif [ "$env" = "prod" ]; then
        compose_file="docker-compose.yml"
        print_status "Building production images..."
    else
        print_error "Invalid environment: $env"
        return 1
    fi
    
    print_status "Using compose file: $compose_file"
    
    # Build backend
    print_status "Building backend image for $env..."
    docker-compose -f "$compose_file" build backend
    print_success "Backend image built successfully"
    
    # Build frontend
    print_status "Building frontend image for $env..."
    docker-compose -f "$compose_file" build frontend
    print_success "Frontend image built successfully"
    
    # Build nginx
    print_status "Building nginx image for $env..."
    docker-compose -f "$compose_file" build nginx
    print_success "Nginx image built successfully"
    
    print_success "All images built successfully for $env environment"
}

# Function to list available images
list_images() {
    print_status "Available OrthoViewer images:"
    docker images | grep "orthoviewer" || print_warning "No OrthoViewer images found"
}

# Function to clean up old images
cleanup_images() {
    print_status "Cleaning up old OrthoViewer images..."
    docker image prune -f --filter "label=org.label-schema.name=orthoviewer*" || true
    print_success "Cleanup completed"
}

# Main script logic
case "${1:-all}" in
    "local")
        build_images "local"
        ;;
    "prod")
        build_images "prod"
        ;;
    "all")
        build_images "local"
        build_images "prod"
        ;;
    "list")
        list_images
        ;;
    "clean")
        cleanup_images
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [local|prod|all|list|clean|help]"
        echo ""
        echo "Commands:"
        echo "  local   Build local development images"
        echo "  prod    Build production images"
        echo "  all     Build both local and production images (default)"
        echo "  list    List available OrthoViewer images"
        echo "  clean   Clean up old images"
        echo "  help    Show this help message"
        ;;
    *)
        print_error "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac 