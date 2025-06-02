#!/bin/bash
set -e

# Navigate to project root
cd "$(dirname "$0")/.."

# Check if environment.yml exists in project root
if [ -f "environment.yml" ]; then
    # If conda environment doesn't exist, create it
    if ! conda env list | grep -q "orthoviewer2"; then
        echo "Creating conda environment from environment.yml..."
        conda env create -f environment.yml
    else
        echo "Updating conda environment..."
        echo "Installing Python dependencies..."
        conda env update -f environment.yml || {
            echo "Conda env update failed, trying pip fallback..."
            cd backend
            pip install -r requirements.txt
            cd ..
        }
    fi
    
    # Activate conda environment
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate orthoviewer2
else
    # If environment.yml doesn't exist, use pip
    echo "No conda environment.yml found, using pip..."
    cd backend
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
fi

# Navigate to backend for running the server
cd backend

# Run FastAPI with uvicorn
echo "Starting FastAPI server..."
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8002