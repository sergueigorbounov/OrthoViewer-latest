#!/bin/bash

# Exit on error
set -e

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Check Docker
check_docker

# Build and start containers
echo "Building and starting containers..."
docker-compose up --build -d

# Check if containers are running
echo "Checking container status..."
if [ "$(docker ps -q -f name=orthoviewer-frontend)" ] && \
   [ "$(docker ps -q -f name=orthoviewer-backend)" ] && \
   [ "$(docker ps -q -f name=orthoviewer-nginx)" ]; then
    echo "All containers are running successfully!"
    echo "Application is available at: http://localhost"
    echo "API documentation is available at: http://localhost/docs"
else
    echo "Error: Some containers failed to start. Check logs with 'docker-compose logs'"
    exit 1
fi 