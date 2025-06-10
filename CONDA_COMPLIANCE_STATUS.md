# OrthoViewer Conda Compliance Status

## ✅ **FULLY COMPLIANT** with INRAE Conda Recommendations

This project now fully complies with the INRAE recommendations for conda usage as specified in:
https://open-science.inrae.fr/fr/offre-service/fiches-pratiques-et-recommandations/quelles-alternatives-aux-fonctionnalites-payantes-danaconda

## Summary of Compliance Actions

### ✅ **Environment Management**
- **Primary environment**: `environment.yml` with conda-forge and bioconda channels
- **Backend environment**: `backend/environment.yml` for backend-specific setup
- **Environment name**: Standardized to `orthoviewer2` across all scripts
- **No pip fallbacks**: Removed all pip fallback mechanisms for strict conda compliance

### ✅ **Script Updates**
All shell scripts now enforce conda-only usage:
- `dev.sh` - Main development script
- `tdd.sh` - Test-driven development script  
- `fastapi_start.sh` - FastAPI startup script
- `backend/run_tests.sh` - Backend testing
- `backend/run_all_tests_tdd.sh` - Comprehensive backend tests
- `scripts/utilities/fix_biosemantic_issues.sh` - Biosemantic issue fixes

### ✅ **Docker Integration**
- Backend `Dockerfile` uses `condaforge/mambaforge:latest`
- Environment creation via `conda env create -f environment.yml`
- Container activation via `conda run -n orthoviewer2`

### ✅ **CI/CD Pipeline**
- GitLab CI uses conda-forge/mambaforge image
- Tests run in conda environments
- No pip dependencies in CI

### ✅ **Dependencies**
All Python dependencies are available through conda channels:
- **conda-forge**: Primary channel for scientific Python packages
- **bioconda**: For bioinformatics packages like ete3
- **defaults**: Fallback conda channel

### ✅ **Documentation Updates**
- `requirements.txt` files marked as DEPRECATED with conda migration instructions
- Clear conda-first setup instructions
- Reference to INRAE recommendations included

## Quick Start (Conda-Only)

```bash
# Clone the repository
git clone <repository-url>
cd OrthoViewer-latest

# Create conda environment
conda env create -f environment.yml

# Activate environment
conda activate orthoviewer2

# Start development
./dev.sh
```

## Dependency Management

### Primary Command
```bash
# Update environment
conda env update -f environment.yml
```

### Environment Verification
```bash
# List environments
conda env list

# Check active environment
conda info --envs

# Verify dependencies
conda list
```

## File Status

### ✅ **Conda-Compliant Files**
- `environment.yml` - Main conda environment
- `backend/environment.yml` - Backend conda environment
- `backend/Dockerfile` - Uses conda base image
- `.gitlab-ci.yml` - Uses conda in CI
- All shell scripts (*.sh) - Conda-only, no pip fallbacks

### 📋 **Legacy Files (Deprecated)**
- `requirements.txt` - Marked as deprecated, conda migration instructions added
- `backend/requirements.txt` - Marked as deprecated, conda migration instructions added

## Compliance Verification

### Test Conda Environment Creation
```bash
# Test environment creation (dry run)
conda env create -f environment.yml --dry-run

# Test backend environment
cd backend
conda env create -f environment.yml --dry-run
```

### Test Scripts
```bash
# Test main development script
./dev.sh

# Test backend testing
cd backend && ./run_tests.sh

# Test TDD workflow
./tdd.sh
```

## Benefits Achieved

### 1. **Dependency Resolution**
- No more pip/conda conflicts
- Better handling of scientific Python packages
- Optimized binary packages from conda-forge

### 2. **Reproducibility**
- Exact environment specification in `environment.yml`
- Cross-platform compatibility
- Version pinning for critical packages

### 3. **Performance**
- Faster installation with pre-compiled packages
- Better optimized scientific libraries
- Reduced build times

### 4. **Compliance**
- Follows INRAE open science recommendations
- Uses recommended conda-forge channel
- Avoids commercial Anaconda dependencies

## Troubleshooting

### Install Conda (if not available)
```bash
# Download and install Miniforge (recommended)
wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
bash Miniforge3-Linux-x86_64.sh
```

### Environment Issues
```bash
# Remove and recreate environment
conda env remove -n orthoviewer2
conda env create -f environment.yml

# Clear conda cache
conda clean --all
```

### Package Conflicts
```bash
# Use mamba for faster dependency resolution
conda install mamba -c conda-forge
mamba env create -f environment.yml
```

## Compliance Statement

This project is now **100% compliant** with INRAE conda recommendations:

- ✅ Uses conda-forge channel primarily
- ✅ Uses bioconda for bioinformatics packages  
- ✅ No commercial Anaconda dependencies
- ✅ No pip fallback mechanisms
- ✅ Environment specification in `environment.yml`
- ✅ Docker containers use conda base images
- ✅ CI/CD pipelines use conda

**Status**: 🟢 **FULLY COMPLIANT** with INRAE recommendations

---

*Last updated: December 2024*
*Compliance verified against: https://open-science.inrae.fr/fr/offre-service/fiches-pratiques-et-recommandations/quelles-alternatives-aux-fonctionnalites-payantes-danaconda* 