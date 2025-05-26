# BioSemanticViz Development Guide

This guide provides instructions for setting up and running the BioSemanticViz application in development mode.

## Requirements

- Node.js (v16+)
- npm (v8+)
- Python (v3.9+)
- Conda (recommended)

## Quick Start

The simplest way to start the development environment is to use the provided `dev.sh` script:

```bash
./dev.sh
```

This will:
1. Start the backend server on port 8003
2. Start the Vite frontend on port 5173
3. Set up all necessary environment variables

## Frontend Options

The application has two frontend implementations:

### Vite Frontend (Recommended)

The Vite frontend is the newer, faster implementation:

```bash
# Start with Vite frontend (default)
./dev.sh
# or explicitly
./dev.sh --vite
```

### Webpack Frontend (Legacy)

The Webpack frontend is the older implementation:

```bash
# Start with Webpack frontend
./dev.sh --webpack
```

## Manual Setup

If you prefer to start the services manually:

### Backend

```bash
cd backend
export PYTHONPATH=$PWD
uvicorn app.fastapi_main:app --host 0.0.0.0 --port 8003 --reload
```

### Vite Frontend

```bash
cd frontend-vite
echo "VITE_BACKEND_URL=http://localhost:8003" > .env
npm install
npm run dev
```

### Webpack Frontend

```bash
cd frontend
echo "REACT_APP_BACKEND_URL=http://localhost:8003" > .env
npm install
npm run start
```

## Troubleshooting

If you encounter issues:

1. Check the log files in the `logs/` directory
2. Make sure all required ports (8003, 5173, or 3000) are available
3. Ensure you have the correct Node.js and Python versions
4. Try running the services manually to see detailed error messages

## API Documentation

When the backend is running, API documentation is available at:
- http://localhost:8003/docs
