#!/bin/bash

echo "🚀 Starting OrthoViewer2 Backend..."

# Navigate to backend directory
cd backend

# Install dependencies if not already installed
echo "📦 Installing dependencies..."
pip install fastapi==0.68.2 uvicorn==0.15.0 python-multipart==0.0.5 requests==2.26.0 python-dotenv==0.19.2 pandas numpy ete3 biopython

# Set environment variables
export PYTHONPATH=/app

echo "✅ Starting API server on http://localhost:8002"
echo "📚 API docs available at http://localhost:8002/docs"

# Start the server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload 