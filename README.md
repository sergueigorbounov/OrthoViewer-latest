# OrthoViewer 🧬

**A Modern Platform for Biological Data Visualization and Phylogenetic Analysis**

OrthoViewer is a cutting-edge web-based platform designed for the visualization and analysis of biological data, with particular emphasis on orthogroups and phylogenetic relationships. Built with modern technologies and scientific rigor, it provides researchers with robust analytical capabilities for comparative genomics studies.

![Status](https://img.shields.io/badge/status-active%20development-brightgreen)
![Conda](https://img.shields.io/badge/conda-compliant-brightgreen)
![Docker](https://img.shields.io/badge/docker-ready-blue)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![React](https://img.shields.io/badge/react-18+-blue)

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+** (conda/miniforge recommended)
- **Node.js 16+** with npm
- **Git** for version control

### One-Command Startup
```bash
git clone <repository-url>
cd OrthoViewer-latest
./dev.sh
```

That's it! This script will:
- ✅ Install all dependencies (conda-first approach)
- ✅ Set up environments automatically
- ✅ Start backend on http://localhost:8003
- ✅ Launch frontend on http://localhost:5173
- ✅ Enable hot-reload for development

### Access Your Application
- **Frontend**: http://localhost:5173
- **API Documentation**: http://localhost:8003/docs  
- **Health Check**: http://localhost:8003/api/health

---

## 📁 Project Structure

```
orthoviewer/
├── frontend-vite/              # Modern React + TypeScript frontend
├── backend/                    # FastAPI backend with 3-layer architecture
├── docker/                     # Containerization configs
├── scripts/                    # Organized utility scripts
├── tests/                      # Comprehensive test suites
├── docs/                       # Documentation
├── dev.sh                      # Main development startup
├── tdd.sh                      # Test-driven development
├── setup-docker.sh             # Docker environment setup
└── environment.yml             # Conda environment specification
```

---

## 🛠️ Development Workflow

### Quick Commands
| Command | Purpose |
|---------|---------|
| `./dev.sh` | 🚀 Start full development environment |
| `./tdd.sh` | 🧪 Test-driven development with live testing |
| `./start-server.sh` | 🌐 Production server startup |
| `./fastapi_start.sh` | ⚡ FastAPI with frontend |
| `./setup-docker.sh` | 🐳 Complete Docker setup |

### Individual Services
```bash
./scripts/backend.sh            # Backend only
./scripts/frontend.sh           # Frontend only
```

### Testing Suite
```bash
./scripts/test-all.sh           # Run all tests
./scripts/test-unit.sh          # Unit tests only
./scripts/test-integration.sh   # Integration tests
./scripts/test-performance.sh   # Performance testing
./scripts/test-e2e.sh          # End-to-end tests
```

### Docker Development
```bash
./setup-docker.sh              # Complete Docker setup
./scripts/docker-start.sh      # Start Docker environment
```

---

## 🏗️ Technical Architecture

### System Overview
OrthoViewer employs a modern 3-layer architecture designed for scalability and maintainability:

```
┌─────────────────────────────────────────────────────────────────┐
│                    OrthoViewer Architecture                     │
├─────────────────────────────────────────────────────────────────┤
│  Presentation Layer                                             │
│  ┌─────────────────┐    ┌─────────────────┐                   │
│  │   React Client  │    │   TypeScript    │                   │
│  │   + Vite        │◄──►│   + Material-UI │                   │
│  └─────────────────┘    └─────────────────┘                   │
├─────────────────────────────────────────────────────────────────┤
│  API Gateway Layer                                              │
│  ┌─────────────────┐    ┌─────────────────┐                   │
│  │   FastAPI       │    │   OpenAPI       │                   │
│  │   + Pydantic    │    │   Documentation │                   │
│  └─────────────────┘    └─────────────────┘                   │
├─────────────────────────────────────────────────────────────────┤
│  Business Logic Layer                                           │
│  ┌─────────────────┐    ┌─────────────────┐                   │
│  │ Phylogenetic    │    │ Orthogroup      │                   │
│  │ Services        │    │ Analysis        │                   │
│  └─────────────────┘    └─────────────────┘                   │
├─────────────────────────────────────────────────────────────────┤
│  Data Access Layer                                              │
│  ┌─────────────────┐    ┌─────────────────┐                   │
│  │ ETE3 Toolkit    │    │ File System     │                   │
│  │ Integration     │    │ + Caching       │                   │
│  └─────────────────┘    └─────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Frontend Excellence**
- **React 18** with TypeScript for type-safe development
- **Vite** for lightning-fast builds and hot-reload
- **Material-UI (MUI)** for beautiful, accessible components
- **D3.js** for interactive phylogenetic visualizations
- **Redux Toolkit** for predictable state management

**Backend Power**
- **FastAPI** for high-performance API development
- **Python 3.10+** with modern async/await patterns
- **ETE3 Toolkit** for phylogenetic tree manipulation
- **Pandas + NumPy** for scientific data processing
- **Pydantic** for data validation and serialization

**Infrastructure & DevOps**
- **Docker + Compose** for containerized deployment
- **Conda** for reproducible scientific environments
- **Pytest** for comprehensive testing
- **OpenAPI/Swagger** for automatic API documentation
- **GitLab CI/CD** for automated deployment

### 3-Layer Backend Architecture

```
backend/app/
├── api/                       # API Layer
│   ├── routes/                # HTTP route handlers
│   ├── middleware/            # Request/response middleware  
│   └── dependencies/          # FastAPI dependency injection
├── services/                  # Service Layer
│   ├── biological/           # Core business logic
│   ├── analysis/             # Data analysis services
│   └── visualization/        # Chart generation
├── repositories/              # Data Access Layer
│   ├── file/                 # File-based data access
│   ├── database/             # Database repositories
│   └── cache/                # Caching implementations
└── models/                    # Shared Models
    ├── domain/               # Business domain models
    ├── dto/                  # Data transfer objects
    └── entities/             # Database entities
```

**Layer Responsibilities:**
- **API Layer**: HTTP handling, validation, serialization
- **Service Layer**: Business logic, orchestration, transactions
- **Data Layer**: Data persistence, file I/O, caching

### Performance Targets
| Operation | Target | Status |
|-----------|--------|--------|
| Gene search | < 50ms | ✅ Achieved |
| Species lookup | < 10ms | ✅ Achieved |
| Orthogroup retrieval | < 100ms | ✅ Achieved |
| Dashboard load | < 200ms | ✅ Achieved |

---

## 🔬 Key Features

### Biological Data Analysis
- **Orthogroup Management**: Comprehensive orthogroup visualization and analysis
- **Phylogenetic Trees**: Interactive tree rendering with ETE3 integration
- **Species Comparison**: Multi-species comparative genomics
- **Gene Search**: High-performance gene lookup and filtering

### Modern User Experience
- **Responsive Design**: Beautiful UI that works on all devices
- **Interactive Visualizations**: D3.js-powered charts and trees
- **Real-time Updates**: Live data updates and collaboration
- **Accessibility**: WCAG-compliant interface design

---

## 🐍 Conda Environment Management

### ✅ **FULLY COMPLIANT** with INRAE Conda Recommendations

This project is **100% compliant** with INRAE conda recommendations as specified in:
https://open-science.inrae.fr/fr/offre-service/fiches-pratiques-et-recommandations/quelles-alternatives-aux-fonctionnalites-payantes-danaconda

### Quick Setup
```bash
# Create conda environment
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

# Verify dependencies
conda list
```

### Compliance Benefits
- ✅ Uses conda-forge channel primarily
- ✅ Uses bioconda for bioinformatics packages  
- ✅ No commercial Anaconda dependencies
- ✅ Environment specification in `environment.yml`
- ✅ Docker containers use conda base images
- ✅ CI/CD pipelines use conda

---

## 🧪 Testing Strategy

### Comprehensive Test Suite
- **Unit Tests**: Test individual components and functions
- **Integration Tests**: Test service interactions
- **Performance Tests**: Validate response times and resource usage
- **End-to-End Tests**: Full user workflow testing

### Test Commands
```bash
# All tests
./scripts/test-all.sh

# Specific test types
./scripts/test-unit.sh           # Unit tests
./scripts/test-integration.sh    # Integration tests  
./scripts/test-performance.sh    # Performance tests
./scripts/test-e2e.sh           # End-to-end tests
```

### Test-Driven Development
```bash
./tdd.sh                        # TDD workflow with live testing
```

---

## 🐳 Docker & Deployment

### Docker Development
```bash
# Complete Docker setup
./setup-docker.sh

# Start Docker environment
./scripts/docker-start.sh

# Individual containers
./scripts/docker-backend.sh     # Backend container only
./scripts/docker-frontend.sh    # Frontend container only
```

### Production Deployment

#### Rocky Server (10.0.0.213)
```bash
# Automated deployment
./scripts/deployment/auto-deploy-rocky.sh

# Manual deployment
./scripts/deployment/deploy-rocky.sh

# Access via SSH tunnel
ssh -L 8080:localhost:8080 rocky@10.0.0.213
# Then open: http://localhost:8080
```

#### CI/CD Pipeline
- **Automated Testing**: Code validated before deployment
- **One-Click Deployment**: Deploy with single button click
- **Health Monitoring**: Automatic verification
- **Secure**: SSH keys managed by GitLab CI/CD

---

## 📚 Scripts Reference

### Core Development Scripts
| Script | Purpose |
|--------|---------|
| `./dev.sh` | 🚀 Main development environment |
| `./tdd.sh` | 🧪 Test-driven development |
| `./start-server.sh` | 🌐 Production server |
| `./fastapi_start.sh` | ⚡ FastAPI + frontend |
| `./setup-docker.sh` | 🐳 Docker setup |

### Organized Script Directory
```
scripts/
├── install_dependencies.sh     # Install all dependencies
├── setup_database.sh          # Database setup
├── backend.sh                 # Backend only
├── frontend.sh                # Frontend only
├── test-*.sh                  # Testing scripts
├── docker-*.sh                # Docker scripts
├── deployment/                # Deployment scripts
│   └── *.sh                  # Various deployment options
└── utilities/                 # Utility scripts
    └── fix_biosemantic_issues.sh
```

### Common Use Cases
```bash
# Start developing
./dev.sh

# Run tests while developing
./tdd.sh

# Deploy to Rocky server
./scripts/deployment/auto-deploy-rocky.sh

# Run only backend
./scripts/backend.sh

# Run everything in Docker
./setup-docker.sh

# Fix dependencies
./scripts/install_dependencies.sh
./scripts/utilities/fix_biosemantic_issues.sh
```

---

## 🔧 Environment Configuration

### Primary Environment Files
- `environment.yml` - Main conda environment
- `backend/environment.yml` - Backend-specific environment
- `frontend-vite/package.json` - Frontend dependencies

### Environment Variables
| Variable | Default | Purpose |
|----------|---------|---------|
| `CONDA_ENV_NAME` | `orthoviewer2` | Conda environment name |
| `BACKEND_PORT` | `8003` | Backend server port |
| `FRONTEND_PORT` | `5173` | Frontend dev server port |

---

## 🚨 Troubleshooting

### Common Issues

#### Conda Environment Issues
```bash
# Remove and recreate environment
conda env remove -n orthoviewer2
conda env create -f environment.yml

# Clear conda cache
conda clean --all
```

#### Port Conflicts
Scripts automatically kill processes on conflicting ports

#### Missing Dependencies
```bash
./scripts/install_dependencies.sh
```

#### ETE3/BioSemantic Issues
```bash
./scripts/utilities/fix_biosemantic_issues.sh
```

#### Docker Issues
```bash
./setup-docker.sh
```

### Install Conda (if not available)
```bash
# Download and install Miniforge (recommended)
wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
bash Miniforge3-Linux-x86_64.sh
```

---

## 📈 Development Guidelines

### API Layer Best Practices
```python
# ✅ Good: Thin controllers
@router.get("/species/{species_id}")
async def get_species(species_id: str, service: SpeciesService = Depends()):
    return await service.get_species_by_id(species_id)
```

### Service Layer Best Practices
```python
# ✅ Good: Pure business logic
class SpeciesService:
    def __init__(self, repo: SpeciesRepository):
        self.repo = repo
    
    async def get_species_stats(self, species_id: str) -> SpeciesStats:
        species = await self.repo.get_by_id(species_id)
        return self._calculate_stats(species)
```

### Repository Layer Best Practices
```python
# ✅ Good: Abstract data access
class SpeciesRepository(ABC):
    @abstractmethod
    async def get_by_id(self, species_id: str) -> Species:
        pass
```

---

## 📊 Project Status & Compliance

### ✅ Conda Compliance Status
- **Status**: 🟢 **FULLY COMPLIANT** with INRAE recommendations
- **Environment Management**: Standardized conda environments
- **Dependencies**: All available through conda-forge and bioconda
- **CI/CD**: Uses conda in all pipelines
- **Docker**: Conda-based containers

### 🚀 Deployment Status
- **Development**: ✅ Ready with `./dev.sh`
- **Testing**: ✅ Comprehensive test suite
- **Docker**: ✅ Full containerization
- **Production**: ✅ Rocky server deployment ready
- **CI/CD**: ✅ GitLab automation configured

---

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Setup environment**: `./dev.sh`
4. **Run tests**: `./tdd.sh`
5. **Commit changes**: `git commit -m 'Add amazing feature'`
6. **Push to branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

---

## 📄 License

This project is part of the INRAE PEPR-BREIF WP2 initiative for biological data visualization and analysis.

---

## 🆘 Support

- **Documentation**: Check individual script `--help` options
- **Issues**: Report issues on the project repository
- **INRAE Conda Guide**: https://open-science.inrae.fr/fr/offre-service/fiches-pratiques-et-recommandations/quelles-alternatives-aux-fonctionnalites-payantes-danaconda

---

**Happy Coding! 🧬✨**