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

# Start development environment
echo "Starting development environment..."
docker-compose -f docker-compose.dev.yml up --build

# Trap SIGINT and SIGTERM signals and forward them to the child processes
trap "docker-compose -f docker-compose.dev.yml down" SIGINT SIGTERM

# Wait for any process to exit
wait 