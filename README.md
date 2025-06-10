# OrthoViewer

**A Modern Platform for Biological Data Visualization and Phylogenetic Analysis**

OrthoViewer is a cutting-edge web-based platform designed for the visualization and analysis of biological data, with particular emphasis on orthogroups and phylogenetic relationships. Built with modern technologies and scientific rigor, it provides researchers with robust analytical capabilities for comparative genomics studies.

---

## Quick Start

### Prerequisites
- **Python 3.10+** (conda/miniforge recommended)
- **Node.js 16+** with npm
- **Git** for version control

### One-Command Startup
```bash
git clone <repository-url>
cd orthoviewer
./dev.sh
```

That's it! This script will:
- Install all dependencies (conda-first approach)
- Set up environments automatically
- Start backend on http://localhost:8003
- Launch frontend on http://localhost:5173
- Enable hot-reload for development

### Access Your Application
- **Frontend**: http://localhost:5173
- **API Documentation**: http://localhost:8003/docs  
- **Health Check**: http://localhost:8003/api/health

---

## Project Structure

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

## Development Workflow

### Daily Development
```bash
./dev.sh                        # Full development environment
./tdd.sh                        # Test-driven development with live testing
```

### Individual Services
```bash
./scripts/backend.sh            # Backend only
./scripts/frontend.sh           # Frontend only
```

### Production Mode
```bash
./start-server.sh               # Production server
./fastapi_start.sh              # FastAPI with frontend
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

## Technical Architecture

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
| Gene search | < 50ms | Achieved |
| Species lookup | < 10ms | Achieved |
| Orthogroup retrieval | < 100ms | Achieved |
| Dashboard load | < 200ms | Achieved |

---

## Key Features

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

### Scientific Rigor
- **Test-Driven Development**: Comprehensive testing at all levels
- **Reproducible Results**: Conda environments for consistency
- **Performance Monitoring**: Built-in metrics and health checks
- **Documentation**: Auto-generated API docs and user guides

---

## Deployment Options

### Local Development
```bash
./dev.sh                       # Quick local startup
```

### Docker Deployment
```bash
./setup-docker.sh             # Full Docker setup
./scripts/docker-start.sh     # Start containers
```

### Production Deployment

#### Rocky Server (10.0.0.213)
```bash
# Automated deployment
./scripts/deployment/auto-deploy-rocky.sh

# Manual deployment
ssh rocky@10.0.0.213
git clone <repo-url>
./deploy-rocky.sh
```

#### GitLab CI/CD Integration
- Automatic testing on commit
- Manual deployment triggers
- Health verification
- Performance monitoring

**Access deployed app:**
```bash
# SSH tunnel (recommended)
ssh -L 8080:localhost:8080 rocky@10.0.0.213
# Then visit: http://localhost:8080
```

---

## Test-Driven Development

### TDD Philosophy
OrthoViewer employs rigorous Test-Driven Development adapted for scientific software:

1. **Red**: Write failing tests for new functionality
2. **Green**: Implement minimal code to pass tests  
3. **Refactor**: Improve code while maintaining tests
4. **Repeat**: Continue cycle for reliable development

### Testing Strategy
```bash
# Interactive TDD workflow
./tdd.sh                       # Live testing environment

# Comprehensive test suites
./scripts/test-all.sh          # All tests
./scripts/test-unit.sh         # Unit tests
./scripts/test-integration.sh  # Integration tests
./scripts/test-performance.sh  # Performance validation
```

### Testing Coverage
- **Unit Tests**: Individual component testing
- **Integration Tests**: Full-stack testing
- **Performance Tests**: Response time validation
- **End-to-End Tests**: User workflow verification

---

## Environment Management

### Conda-First Approach
OrthoViewer uses conda for reproducible scientific environments:

```bash
# Create environment
conda env create -f environment.yml

# Activate environment  
conda activate orthoviewer2

# Update environment
conda env update -f environment.yml
```

### Automatic Fallbacks
All scripts intelligently fall back to pip if conda is unavailable:
- **Primary**: Conda for scientific packages
- **Fallback**: Pip when conda unavailable
- **Mixed**: Pip within conda for missing packages

### Environment Files
- **`environment.yml`**: Main project environment
- **`backend/environment.yml`**: Backend-specific packages
- **`requirements.txt`**: Pip fallback dependencies

---

## Documentation & API

### Interactive Documentation
- **API Docs**: http://localhost:8003/docs (Swagger UI)
- **ReDoc**: http://localhost:8003/redoc (Alternative API docs)
- **Health Endpoints**: Comprehensive system monitoring

### Script Documentation
All scripts include built-in help:
```bash
./dev.sh --help               # Development help
./tdd.sh --help               # TDD workflow help
./scripts/test-all.sh --help  # Testing help
```

### Quick Reference
- **`SCRIPTS_REFERENCE.md`**: Quick script usage guide
- **`scripts/README.md`**: Detailed script documentation
- **`backend/ARCHITECTURE.md`**: Technical architecture details

---

## Troubleshooting

### Common Issues

**Environment Setup**
```bash
# Conda not found
curl -L https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh | bash

# Environment conflicts
conda env remove -n orthoviewer2
conda env create -f environment.yml
```

**Port Conflicts**
```bash
# Scripts automatically handle port conflicts
# Or manually kill processes:
sudo lsof -i :8003 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

**Dependencies Issues**
```bash
# Fix scientific package conflicts
./scripts/utilities/fix_biosemantic_issues.sh

# Reinstall dependencies
./scripts/install_dependencies.sh
```

### Getting Help
1. Check logs in `logs/` directory
2. Run scripts with `--help` flag
3. Verify conda environment: `conda list`
4. Check Docker status: `docker ps`

---

## Development Guidelines

### Code Quality
- **Type Safety**: TypeScript frontend, Pydantic backend
- **Code Formatting**: Automated with Prettier and Black
- **Linting**: ESLint for frontend, Flake8 for backend
- **Testing**: Minimum 80% code coverage

### Git Workflow
- **Feature Branches**: All development in feature branches
- **Pull Requests**: Required for main branch
- **Automated Testing**: CI/CD runs all tests
- **Code Review**: Peer review for all changes

### Performance Standards
- **API Response**: < 100ms for most endpoints
- **Frontend Load**: < 2s initial page load
- **Memory Usage**: < 500MB backend container
- **Database Queries**: < 10ms for cached data

---

## Why OrthoViewer?

### Modern & Fast
- Lightning-fast Vite development
- High-performance FastAPI backend
- Hot-reload for instant feedback

### Scientifically Rigorous  
- Comprehensive test coverage
- Reproducible conda environments
- Validated biological algorithms

### Developer Friendly
- One-command startup
- Comprehensive documentation
- Containerized deployment

### Production Ready
- Security best practices
- Performance monitoring
- Automated CI/CD deployment

---

**Ready to explore biological data like never before? Start with `./dev.sh` and dive in!**