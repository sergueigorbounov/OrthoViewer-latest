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

# Set up environment
if [ -f "../environment.yml" ]; then
  # Check if conda environment exists and activate it
  ENV_NAME=$(grep "name:" ../environment.yml | cut -d' ' -f2)
  if conda info --envs | grep -q "$ENV_NAME"; then
    echo "Activating conda environment: $ENV_NAME"
    eval "$(conda shell.bash hook)" && conda activate "$ENV_NAME"
  else
    echo "Creating conda environment from ../environment.yml..."
    conda env create -f ../environment.yml
    eval "$(conda shell.bash hook)" && conda activate "$ENV_NAME"
  fi
else
  # Use virtual environment with pip fallback
  if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python -m venv .venv
  fi
  echo "Activating virtual environment..."
  source .venv/bin/activate
  
  # Install requirements via pip if no conda environment
  if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
  fi
fi

case $COMMAND in
  test)
    echo "Running tests in watch mode..."
    python -m pytest tests/ -v --color=yes -f
    ;;
  coverage)
    echo "Running tests with coverage..."
    python -m pytest tests/ --cov=app --cov-report=term --cov-report=html:htmlcov
    ;;
  lint)
    echo "Running linting..."
    if command -v black >/dev/null; then
      black app/ tests/
    else
      echo "Installing black..."
      if conda list | grep -q black; then
        echo "Black available via conda"
      else
        pip install black
      fi
      black app/ tests/
    fi
    if command -v flake8 >/dev/null; then
      flake8 app/ tests/
    else
      echo "Installing flake8..."
      if conda list | grep -q flake8; then
        echo "Flake8 available via conda"
      else
        pip install flake8
      fi
      flake8 app/ tests/
    fi
    ;;
  start)
    echo "Starting development server..."
    python -m uvicorn app.main_tdd:app --reload --host 0.0.0.0 --port 8000
    ;;
  *)
    echo "Unknown command: $COMMAND"
    echo "Use --help to see available commands"
    exit 1
    ;;
esac