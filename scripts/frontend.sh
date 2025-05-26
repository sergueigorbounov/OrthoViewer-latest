#!/bin/bash
set -e

# Navigate to frontend directory
cd "$(dirname "$0")/../frontend-vite"

# Install dependencies if needed
if [ ! -d "node_modules" ] || [ "$1" == "--install" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Run development server
echo "Starting frontend development server..."
npm run dev