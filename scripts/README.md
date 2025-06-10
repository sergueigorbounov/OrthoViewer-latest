# Scripts Directory

This directory contains all utility scripts for the OrthoViewer project, organized by purpose.

## Directory Structure

```
scripts/
├── README.md                    # This documentation
├── install_dependencies.sh     # Install all project dependencies using conda
├── setup_database.sh          # Set up PostgreSQL database
├── backend.sh                 # Start backend server with conda
├── frontend.sh                # Start frontend development server
├── test-unit.sh               # Run unit tests
├── test-integration.sh        # Run integration tests  
├── test-performance.sh        # Run performance tests
├── test-all.sh                # Run all test suites
├── test-e2e.sh                # Run end-to-end tests
├── docker-backend.sh          # Start backend in Docker
├── docker-frontend.sh         # Start frontend in Docker
├── docker-start.sh            # Start full Docker environment
├── deployment/                # Deployment scripts
│   ├── auto-deploy-rocky.sh   # Automated Rocky deployment
│   ├── deploy-rocky-vm.sh     # Rocky VM deployment
│   ├── deploy-rocky.sh        # Rocky deployment
│   ├── deploy-via-legolas.sh  # Legolas deployment
│   ├── deploy-vm-213*.sh      # VM 213 deployment variants
│   └── local-deploy-rocky.sh  # Local Rocky deployment
└── utilities/                 # Utility scripts
    └── fix_biosemantic_issues.sh # Fix BioSemantic compatibility issues
```

## Core Development Scripts

### Environment Setup
- **`install_dependencies.sh`** - Install all project dependencies using conda
- **`setup_database.sh`** - Set up PostgreSQL database for OrthoViewer
- **`backend.sh`** - Start the backend server using conda environment

### Testing Scripts
- **`test-unit.sh`** - Run unit tests with conda environment
- **`test-integration.sh`** - Run integration tests with conda environment  
- **`test-performance.sh`** - Run performance tests with conda environment
- **`test-all.sh`** - Run all test suites sequentially
- **`test-e2e.sh`** - Run end-to-end tests

### Development Utilities
- **`frontend.sh`** - Start frontend development server only

### Docker Scripts
- **`docker-backend.sh`** - Start backend in Docker container
- **`docker-frontend.sh`** - Start frontend in Docker container
- **`docker-start.sh`** - Start full Docker development environment

### Deployment Scripts (./deployment/)
- **`auto-deploy-rocky.sh`** - Automated deployment to Rocky server
- **`deploy-rocky.sh`** - Manual Rocky deployment
- **`local-deploy-rocky.sh`** - Local deployment to Rocky
- **`deploy-vm-213.sh`** - VM 213 deployment (various variants)
- **`deploy-via-legolas.sh`** - Deployment via Legolas server

### Utility Scripts (./utilities/)
- **`fix_biosemantic_issues.sh`** - Fix BioSemantic compatibility issues

## Usage

### Quick Start
```bash
# Install all dependencies
./scripts/install_dependencies.sh

# Set up database
./scripts/setup_database.sh

# Start development environment (use root script for full environment)
./dev.sh
```

### Testing
```bash
# Run all tests
./scripts/test-all.sh

# Run specific test types
./scripts/test-unit.sh
./scripts/test-integration.sh
./scripts/test-performance.sh
./scripts/test-e2e.sh
```

### Individual Services
```bash
# Backend only
./scripts/backend.sh

# Frontend only
./scripts/frontend.sh
```

### Docker Development
```bash
# Full Docker environment
./scripts/docker-start.sh

# Individual containers
./scripts/docker-backend.sh
./scripts/docker-frontend.sh
```

### Deployment
```bash
# Automated Rocky deployment
./scripts/deployment/auto-deploy-rocky.sh

# Manual Rocky deployment
./scripts/deployment/deploy-rocky.sh

# Local deployment
./scripts/deployment/local-deploy-rocky.sh
```

### Utilities
```bash
# Fix BioSemantic issues
./scripts/utilities/fix_biosemantic_issues.sh
```

## Root Level Scripts

The following scripts remain in the project root for convenience:

- **`dev.sh`** - Main development environment startup (comprehensive)
- **`tdd.sh`** - Test-driven development workflow
- **`start-server.sh`** - Production server startup
- **`fastapi_start.sh`** - FastAPI server with frontend
- **`setup-docker.sh`** - Complete Docker environment setup

## Script Conventions

### All scripts follow these conventions:
1. **Conda-first approach** - Use conda environments when available
2. **Graceful fallbacks** - Fall back to pip/venv if conda unavailable
3. **Error handling** - Exit on errors with clear messages
4. **Color output** - Use colored output for better UX
5. **Documentation** - Include help/usage information

### Environment Variables
Scripts respect these environment variables:
- `CONDA_ENV_NAME` - Override default conda environment name
- `BACKEND_PORT` - Override default backend port (8000)
- `FRONTEND_PORT` - Override default frontend port (3000)

## Migration Summary

### Removed redundant scripts:
- `test.sh` → Use `scripts/test-all.sh`
- `e2e.sh` → Use `scripts/test-e2e.sh`  
- `docker-start.sh` → Use `scripts/docker-start.sh`
- `tdd-helpers.sh` → Integrated into `tdd.sh`
- `tdd-setup.sh` → Integrated into installation scripts
- `scripts/dev.sh` → Use root `dev.sh`

### Organized into subdirectories:
- All deployment scripts → `scripts/deployment/`
- Utility scripts → `scripts/utilities/`
- Core scripts remain in `scripts/`

### Cleaned up root directory:
- Removed debug/test files (`debug_*.py`, `test_*.py`, etc.)
- Removed temporary files (`*.json`, `*.png`, etc.)
- Kept only essential root-level scripts 