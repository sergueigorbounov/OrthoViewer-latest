#!/bin/bash
set -e

# Navigate to project root
cd "$(dirname "$0")/.."

# Build and run the backend Docker container
echo "Building and running backend Docker container..."
docker build -t biosemantic-backend:latest ./backend
docker run -it --rm \
    -p 8002:8002 \
    -v "$(pwd)/backend:/app" \
    -v "$(pwd)/data:/data" \
    -e PYTHONPATH=/app \
    -e CORS_ORIGINS=http://localhost,http://localhost:80,http://localhost:8001 \
    --name biosemantic-backend \
    biosemantic-backend:latest