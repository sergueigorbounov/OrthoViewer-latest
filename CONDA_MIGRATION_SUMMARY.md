# OrthoViewer Conda Migration Summary

## Overview
This document summarizes the complete migration of the OrthoViewer project from pip-based dependency management to conda-based environments, making the project fully conda-compliant while maintaining backward compatibility.

## Files Modified

### 1. Core Environment Configuration
- **`environment.yml`** - Main conda environment specification for the project
- **`backend/environment.yml`** - Backend-specific conda environment with scientific Python packages

### 2. Main Scripts
- **`dev.sh`** - Updated to prefer conda environments with pip fallback
- **`fastapi_start.sh`** - Already conda-aware, enhanced conda preference  
- **`setup-docker.sh`** - Added conda-based Docker container setup
- **`start-server.sh`** - Converted to conda environment activation
- **`tdd.sh`** - Updated to use conda for package installation

### 3. Backend Scripts
- **`backend/setup-env.sh`** - Converted to conda environment creation
- **`backend/tdd.sh`** - Updated for conda environment usage
- **`backend/run_tests.sh`** - Already conda-aware, maintained good structure
- **`backend/run_all_tests_tdd.sh`** - Updated to prefer conda package installation

### 4. Scripts Directory
- **`scripts/install_dependencies.sh`** - Complete rewrite for conda-based installation
- **`scripts/setup_database.sh`** - Updated to use conda environment for database operations
- **`scripts/backend.sh`** - Converted to conda environment activation
- **`scripts/test-unit.sh`** - Updated for conda environment usage
- **`scripts/test-integration.sh`** - Updated for conda environment usage  
- **`scripts/test-performance.sh`** - Updated for conda environment usage

### 5. CI/CD Configuration
- **`.gitlab-ci.yml`** - Updated to use conda in GitLab CI pipelines

### 6. Specialized Scripts
- **`fix_biosemantic_issues.sh`** - Updated to prefer conda for ete3 installation

## Key Changes Made

### Environment Setup
1. **Created comprehensive `environment.yml`** with all project dependencies
2. **Added `backend/environment.yml`** for backend-specific conda environment
3. **Environment name standardized** to `orthoviewer2` across all scripts

### Dependency Management Strategy
- **Primary**: Use conda for package installation
- **Fallback**: Use pip when conda packages are unavailable
- **Mixed environments**: Allow pip within conda environments for unavailable packages

### Script Updates Pattern
All scripts now follow this pattern:
1. Check if conda is available
2. Check if `orthoviewer2` environment exists
3. Create environment from `environment.yml` if missing
4. Activate conda environment
5. Fall back to pip/venv if conda unavailable

### Docker Integration
- **New `Dockerfile.conda`** for backend using conda base image
- **Updated `docker-compose.yml`** to use conda-based containers
- **Maintained compatibility** with existing Docker workflows

## Benefits of Migration

### 1. Improved Dependency Resolution
- Conda's dependency solver handles complex scientific Python packages better
- Reduced conflicts between packages like NumPy, SciPy, OpenCV
- Better handling of system libraries and dependencies

### 2. Reproducible Environments
- `environment.yml` provides exact environment specification
- Cross-platform compatibility improved
- Version pinning for critical packages

### 3. Scientific Python Ecosystem
- Access to conda-forge channel with optimized scientific packages
- Better binary package distribution
- Improved performance for numerical computations

### 4. Development Workflow
- Faster environment setup with pre-compiled packages
- Better isolation between development and production environments
- Easier environment sharing and reproduction

## Backward Compatibility

The migration maintains full backward compatibility:
- **Pip fallback**: All scripts fall back to pip if conda is unavailable
- **Existing workflows**: Existing pip-based workflows continue to work
- **Docker compatibility**: Both pip and conda Docker builds supported
- **CI/CD flexibility**: Can use either conda or pip in CI environments

## Usage Instructions

### Quick Start with Conda
```bash
# Install dependencies
conda env create -f environment.yml

# Activate environment
conda activate orthoviewer2

# Start development
./dev.sh
```

### Environment Management
```bash
# Update environment
conda env update -f environment.yml

# List environments
conda env list

# Remove environment
conda env remove -n orthoviewer2
```

### Docker with Conda
```bash
# Use conda-based Docker setup
./setup-docker.sh

# Or build manually
docker-compose up --build
```

## Testing

All testing scripts have been updated:
- `backend/run_tests.sh` - Full test suite with conda
- `scripts/test-unit.sh` - Unit tests with conda
- `scripts/test-integration.sh` - Integration tests with conda
- `scripts/test-performance.sh` - Performance tests with conda

## Files Still Using Pip (As Fallback Only)

These files retain pip commands only as fallback mechanisms:
- `backend/run_tests.sh` - Lines 50, 55 (fallback if conda fails)
- `backend/run_all_tests_tdd.sh` - Line 62, 66 (fallback installation)
- `dev.sh` - Lines 253, 255, 272 (fallback and help text)
- `tdd.sh` - Lines 132-134 (fallback installation)
- `fastapi_start.sh` - Line 72 (fallback if conda env update fails)
- `fix_biosemantic_issues.sh` - Lines 91, 95 (fallback for ete3)

All of these are intentional fallback mechanisms and not primary installation methods.

## Next Steps

1. **Test the migration** in different environments (Linux, macOS, Windows)
2. **Update documentation** to reflect conda-first approach
3. **Train team members** on conda environment management
4. **Monitor performance** improvements from conda packages
5. **Consider** adding conda environment.lock files for exact reproducibility

## Troubleshooting

### Common Issues and Solutions

1. **Conda not found**
   ```bash
   # Install Miniconda
   wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
   bash Miniconda3-latest-Linux-x86_64.sh
   ```

2. **Environment creation fails**
   ```bash
   # Clear conda cache and retry
   conda clean --all
   conda env create -f environment.yml --force
   ```

3. **Package conflicts**
   ```bash
   # Use mamba for faster dependency resolution
   conda install mamba -c conda-forge
   mamba env create -f environment.yml
   ```

4. **Mixed pip/conda issues**
   ```bash
   # Recreate environment cleanly
   conda env remove -n orthoviewer2
   conda env create -f environment.yml
   ```

This migration ensures OrthoViewer is fully conda-compliant while maintaining the flexibility to work in any Python environment. 