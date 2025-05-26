#!/bin/bash
set -e

# Usage message
if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
  echo "Usage: ./tdd.sh [command]"
  echo "Commands:"
  echo "  test     - Run tests in watch mode (default)"
  echo "  coverage - Run tests with coverage report"
  echo "  lint     - Run linting"
  echo "  start    - Start the development server"
  exit 0
fi

# Command selection
COMMAND=${1:-test}

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
  echo "Installing dependencies..."
  npm install
fi

case $COMMAND in
  test)
    echo "Running tests in watch mode..."
    npm test -- --watch
    ;;
  coverage)
    echo "Running tests with coverage..."
    npm test -- --coverage
    ;;
  lint)
    echo "Running linting..."
    npm run lint
    ;;
  start)
    echo "Starting development server..."
    npm run dev
    ;;
  *)
    echo "Unknown command: $COMMAND"
    echo "Use --help to see available commands"
    exit 1
    ;;
esac