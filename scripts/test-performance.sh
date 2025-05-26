#!/bin/bash
set -e

# Navigate to backend directory
cd "$(dirname "$0")/../backend"

# Activate environment
if [ -f "environment.yml" ]; then
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate biosemantic || conda create -n biosemantic python=3.9
    conda activate biosemantic
else
    source .venv/bin/activate || python -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
fi

# Run performance tests (ensure response times < 50ms)
echo "Running performance tests..."
python -m pytest tests/performance -v --durations=0