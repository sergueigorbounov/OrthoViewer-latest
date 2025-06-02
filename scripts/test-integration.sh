#!/bin/bash
set -e

# Navigate to project root  
cd "$(dirname "$0")/.."

# Activate conda environment if available
if conda env list | grep -q "orthoviewer2"; then
    echo "Activating conda environment..."
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate orthoviewer2
else
    echo "Conda environment not found, using pip fallback..."
    cd backend
    pip install -r requirements.txt
    cd ..
fi

# Navigate to backend for testing
cd backend

# Run integration tests
echo "Running integration tests..."
python -m pytest tests/integration/ -v --tb=short