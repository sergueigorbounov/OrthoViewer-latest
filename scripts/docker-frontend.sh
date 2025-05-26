#!/bin/bash
set -e

# Navigate to project root
cd "$(dirname "$0")/.."

# Build and run the frontend Docker container
echo "Building and running frontend Docker container..."
docker build -t biosemantic-frontend:latest ./frontend-vite
docker run -it --rm \
    -p 8001:80 \
    --name biosemantic-frontend \
    biosemantic-frontend:latest