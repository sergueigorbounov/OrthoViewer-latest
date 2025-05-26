#!/bin/bash
set -e

# Navigate to project root
cd "$(dirname "$0")/.."

# Start services in background (using docker-compose)
echo "Starting services for E2E testing..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 15

# Run E2E tests
echo "Running E2E tests..."
python -m pytest test_ete.py -v

# Cleanup
echo "Stopping services..."
docker-compose down