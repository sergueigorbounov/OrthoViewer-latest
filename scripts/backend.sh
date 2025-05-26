#!/bin/bash
set -e

# Navigate to backend directory
cd "$(dirname "$0")/../backend"

# Check if environment.yml exists
if [ -f "environment.yml" ]; then
    # If conda environment doesn't exist, create it
    if ! conda env list | grep -q "biosemantic"; then
        echo "Creating conda environment from environment.yml..."
        conda env create -f environment.yml
    else
        echo "Updating conda environment..."
        conda env update -f environment.yml
    fi
    
    # Activate conda environment
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate biosemantic
else
    # If environment.yml doesn't exist, use pip
    echo "No conda environment.yml found, using pip..."
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
fi

# Run FastAPI with uvicorn
echo "Starting FastAPI server..."
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8002