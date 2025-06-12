# OrthoViewer

**A Modern Platform for Biological Data Visualization and Phylogenetic Analysis**

OrthoViewer is a cutting-edge web-based platform designed for the visualization and analysis of biological data, with particular emphasis on orthogroups and phylogenetic relationships. Built with modern technologies and scientific rigor, it provides researchers with robust analytical capabilities for comparative genomics studies.

![Status](https://img.shields.io/badge/status-active%20development-brightgreen)
![Conda](https://img.shields.io/badge/conda-compliant-brightgreen)
![Docker](https://img.shields.io/badge/docker-ready-blue)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![React](https://img.shields.io/badge/react-18+-blue)

---

## Quick Start

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

This script will:
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

## CI/CD Pipeline and Deployment

### Pipeline Overview

OrthoViewer implements an autonomous deployment pipeline using GitLab CI/CD, incorporating comprehensive fallback mechanisms and security-first design principles aligned with institutional requirements.

#### Pipeline Stages

1. **Build Stage**
   - Frontend compilation with Vite
   - Backend dependency resolution
   - Docker image preparation
   - Artifact optimization

2. **Test Stage**
   - Unit tests with pytest
   - Integration testing
   - Frontend component testing
   - API endpoint validation

3. **Package Stage**
   - Docker Compose configuration for Rocky Linux
   - Deployment artifact creation
   - Environment file generation
   - Compression and optimization

4. **Deploy Stage**
   - Autonomous SSH deployment attempt
   - Automatic fallback to artifact creation
   - Manual deployment preparation
   - Post-deployment verification

### Deployment Architecture

#### Security Framework

The deployment system adheres to INRAE institutional security requirements:

- **SSH Key Restrictions**: Deployment keys limited to specific IP addresses
- **Bastion Host Access**: All connections routed through `legolas.versailles.inrae.fr`
- **Network Segmentation**: Rocky VMs accessible only through VPN
- **Manual Override**: Critical deployments require operator intervention

#### Deployment Environments

**Development Environment**
```bash
# Local development setup
./dev.sh
# Access: http://localhost:5173
```

**Rocky Linux Production**
```bash
# Target: Rocky VM at 10.0.0.213
# Port: 8080 (non-root Docker deployment)
# Access: http://localhost:8080 (via SSH tunnel)
```

### SSH Configuration

#### Required SSH Config Entry

Add to `~/.ssh/config`:

```
Host 10.0.0.213
    HostName 10.0.0.213
    User rocky
    ProxyJump legolas.versailles.inrae.fr
    IdentityFile ~/.ssh/your_deployment_key
    StrictHostKeyChecking accept-new
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

#### SSH Tunnel for Access

```bash
# Forward local port 8080 to Rocky VM port 8080
ssh -L 8080:localhost:8080 rocky@10.0.0.213

# Access OrthoViewer at http://localhost:8080
```

### Artifact Management

#### Automated Artifact Creation

When SSH deployment fails, the pipeline automatically creates deployment artifacts:

**Artifact Contents:**
- `orthoviewer-{commit}-{timestamp}.tar.gz` - Complete deployment package
- `deployment.env` - Environment configuration
- `docker-compose.rocky.yml` - Rocky-specific Docker configuration
- Deployment instructions and verification scripts

#### Manual Deployment Process

1. **Download Artifacts**
   ```bash
   # From GitLab pipeline artifacts section
   wget <artifact-url>/orthoviewer-{commit}-{timestamp}.tar.gz
   ```

2. **Transfer to Rocky VM**
   ```bash
   scp orthoviewer-*.tar.gz rocky@10.0.0.213:/home/rocky/
   ```

3. **Deploy on Rocky VM**
   ```bash
   ssh rocky@10.0.0.213
   cd /home/rocky
   mkdir -p orthoviewer
   cd orthoviewer
   tar -xzf ../orthoviewer-*.tar.gz
   docker-compose -f docker-compose.rocky.yml down
   docker-compose -f docker-compose.rocky.yml up -d
   ```

4. **Verify Deployment**
   ```bash
   # On Rocky VM
   docker ps
   curl http://localhost:8080
   
   # From local machine (with SSH tunnel)
   curl http://localhost:8080
   ```

#### Rocky Linux Specific Configuration

**Port Configuration:**
- External port: 8080 (non-privileged)
- Internal port: 80 (nginx container)
- Mapping: `8080:80` in docker-compose.rocky.yml

**Security Considerations:**
- Non-root Docker execution
- Dedicated `/home/rocky/orthoviewer` directory
- No system directory modifications
- Isolated container network

### Network Requirements

#### VPN Access
- **INRAE VPN** connection required for Rocky VM access
- **Bastion host** routing through legolas.versailles.inrae.fr
- **Network segmentation** for security compliance

#### Firewall Configuration
- Port 8080 accessible on Rocky VM
- SSH (port 22) accessible through bastion
- Docker daemon accessible to rocky user

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
├── .gitlab-ci.yml             # CI/CD pipeline configuration
├── docker-compose.rocky.yml   # Rocky Linux deployment config
├── dev.sh                     # Main development startup
├── tdd.sh                     # Test-driven development
├── setup-docker.sh           # Docker environment setup
└── environment.yml           # Conda environment specification
```

---

## Development Workflow

### Quick Commands
| Command | Purpose |
|---------|---------|
| `./dev.sh` | Start full development environment |
| `./tdd.sh` | Test-driven development with live testing |
| `./start-server.sh` | Production server startup |
| `./fastapi_start.sh` | FastAPI with frontend |
| `./setup-docker.sh` | Complete Docker setup |

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

**Frontend Technologies**
- **React 18** with TypeScript for type-safe development
- **Vite** for optimized builds and development server
- **Material-UI (MUI)** for accessible user interface components
- **D3.js** for interactive phylogenetic visualizations
- **Redux Toolkit** for predictable state management

**Backend Technologies**
- **FastAPI** for high-performance API development
- **Python 3.10+** with modern async/await patterns
- **ETE3 Toolkit** for phylogenetic tree manipulation
- **Pandas + NumPy** for scientific data processing
- **Pydantic** for data validation and serialization

**Infrastructure & DevOps**
- **Docker + Compose** for containerized deployment
- **Conda** for reproducible scientific environments
- **Pytest** for comprehensive testing framework
- **OpenAPI/Swagger** for automatic API documentation
- **GitLab CI/CD** for automated deployment pipelines

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
- **Responsive Design**: Cross-platform compatibility
- **Interactive Visualizations**: D3.js-powered charts and trees

---

## Conda Environment Management

### INRAE Conda Compliance

This project is fully compliant with INRAE conda recommendations as specified in:
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
- Uses conda-forge channel primarily
- Uses bioconda for bioinformatics packages
- No commercial Anaconda dependencies
- Environment specification in `environment.yml`
- Docker containers use conda base images
- CI/CD pipelines use conda

---

## Testing Strategy

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

## Docker & Deployment

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

#### Manual Rocky VM Deployment (Alternative)

If you prefer to deploy manually without the CI/CD pipeline, you can use this process:

#### Quick One-Liner Deployment
```bash
# Complete manual deployment in one command chain
tar -czf orthoviewer-deploy.tar.gz --exclude='.git' --exclude='node_modules' --exclude='__pycache__' --exclude='.pytest_cache' --exclude='logs' --exclude='orthoviewer-deploy.tar.gz' . && scp orthoviewer-deploy.tar.gz rocky@10.0.0.213:~/ && ssh rocky@10.0.0.213 "mkdir -p orthoviewer && cd orthoviewer && tar -xzf ~/orthoviewer-deploy.tar.gz --strip-components=1 && docker compose -f docker-compose.rocky.yml down --remove-orphans && docker compose -f docker-compose.rocky.yml up -d && rm ~/orthoviewer-deploy.tar.gz" && rm orthoviewer-deploy.tar.gz && echo "Deployment complete! Access at http://10.0.0.213:8080"
```

#### Prerequisites
- SSH access to Rocky VM: `rocky@10.0.0.213`
- Docker and Docker Compose installed on the target VM
- Git repository with the latest code

#### Manual Deployment Steps

1. **Create and Upload Deployment Package**
```bash
# Create deployment package (from local development machine)
tar -czf orthoviewer-deploy.tar.gz \
    --exclude='.git' \
    --exclude='node_modules' \
    --exclude='__pycache__' \
    --exclude='.pytest_cache' \
    --exclude='logs' \
    --exclude='orthoviewer-deploy.tar.gz' \
    .

# Upload to Rocky VM
scp orthoviewer-deploy.tar.gz rocky@10.0.0.213:~/
```

2. **Deploy on Rocky VM**
```bash
# Connect to Rocky VM and deploy
ssh rocky@10.0.0.213

# Create directory and extract
mkdir -p orthoviewer
cd orthoviewer
tar -xzf ~/orthoviewer-deploy.tar.gz --strip-components=1

# Deploy with Docker Compose
docker compose -f docker-compose.rocky.yml down --remove-orphans
docker compose -f docker-compose.rocky.yml pull
docker compose -f docker-compose.rocky.yml up -d

# Verify deployment
docker compose -f docker-compose.rocky.yml ps
```

3. **Access the Application**
- **Main Application**: http://10.0.0.213:8080 (Nginx proxy)
- **Frontend Direct**: http://10.0.0.213:8001 (React frontend)
- **Backend API**: http://10.0.0.213:8002 (FastAPI backend)

4. **Cleanup**
```bash
# Remove deployment package
rm ~/orthoviewer-deploy.tar.gz
```

#### Container Architecture on Rocky VM
```
┌─────────────────────────────────────────────────────────────┐
│                      Rocky VM (10.0.0.213)                 │
├─────────────────────────────────────────────────────────────┤
│  Docker Network: orthoviewer_orthoviewer-net               │
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐│
│  │ orthoviewer-    │  │ orthoviewer-    │  │ orthoviewer- ││
│  │ nginx           │  │ frontend        │  │ backend      ││
│  │                 │  │                 │  │              ││
│  │ nginx:alpine    │  │ Custom React    │  │ Custom       ││
│  │ Port: 8080      │  │ Port: 8001      │  │ FastAPI      ││
│  │                 │  │                 │  │ Port: 8002   ││
│  └─────────────────┘  └─────────────────┘  └──────────────┘│
└─────────────────────────────────────────────────────────────┘
```

#### Health Monitoring
```bash
# Check container status
docker compose -f docker-compose.rocky.yml ps

# View logs
docker compose -f docker-compose.rocky.yml logs --tail=20

# Test application accessibility
curl -s -o /dev/null -w '%{http_code}' http://localhost:8080
```

#### Configuration Files Used
- `docker-compose.rocky.yml`: Rocky-specific Docker Compose configuration
- `nginx/nginx.conf`: Nginx reverse proxy configuration
- `backend/Dockerfile`: Backend container build instructions
- `frontend-vite/Dockerfile`: Frontend container build instructions

#### CI/CD Pipeline (Automated Alternative)
- **Automated Testing**: Code validated before deployment
- **One-Click Deployment**: Deploy with single button click
- **Health Monitoring**: Automatic verification
- **Secure**: SSH keys managed by GitLab CI/CD

---

## Scripts Reference

### Core Development Scripts
| Script | Purpose |
|--------|---------|
| `./dev.sh` | Main development environment |
| `./tdd.sh` | Test-driven development |
| `./start-server.sh` | Production server |
| `./fastapi_start.sh` | FastAPI + frontend |
| `./setup-docker.sh` | Docker setup |

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

## Environment Configuration

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

## Troubleshooting

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

## Development Guidelines

### API Layer Best Practices
```python
# Good: Thin controllers
@router.get("/species/{species_id}")
async def get_species(species_id: str, service: SpeciesService = Depends()):
    return await service.get_species_by_id(species_id)
```

### Service Layer Best Practices
```python
# Good: Pure business logic
class SpeciesService:
    def __init__(self, repo: SpeciesRepository):
        self.repo = repo
    
    async def get_species_stats(self, species_id: str) -> SpeciesStats:
        species = await self.repo.get_by_id(species_id)
        return self._calculate_stats(species)
```

### Repository Layer Best Practices
```python
# Good: Abstract data access
class SpeciesRepository(ABC):
    @abstractmethod
    async def get_by_id(self, species_id: str) -> Species:
        pass
```

---

## Project Status & Compliance

### Conda Compliance Status
- **Status**: Fully compliant with INRAE recommendations
- **Environment Management**: Standardized conda environments
- **Dependencies**: All available through conda-forge and bioconda
- **CI/CD**: Uses conda in all pipelines
- **Docker**: Conda-based containers

### Deployment Status
- **Development**: Ready with `./dev.sh`
- **Testing**: Comprehensive test suite
- **Docker**: Full containerization
- **Production**: Rocky server deployment ready
- **CI/CD**: GitLab automation configured

---

## Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Setup environment**: `./dev.sh`
4. **Run tests**: `./tdd.sh`
5. **Commit changes**: `git commit -m 'Add amazing feature'`
6. **Push to branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

---

## License

This project is part of the INRAE PEPR-BREIF WP2 initiative for biological data visualization and analysis.

---

## Support

- **Documentation**: Check individual script `--help` options
- **Issues**: Report issues on the project repository
- **INRAE Conda Guide**: https://open-science.inrae.fr/fr/offre-service/fiches-pratiques-et-recommandations/quelles-alternatives-aux-fonctionnalites-payantes-danaconda

---

**Scientific Computing Platform for Comparative Genomics Research**

# OrthoViewer2 Platform

OrthoViewer2 is a comprehensive bioinformatics platform designed for phylogenetic analysis and orthologous gene visualization. The platform integrates advanced computational biology tools with modern web technologies to provide researchers with an intuitive interface for analyzing evolutionary relationships.

## Prerequisites

### System Requirements
- Docker and Docker Compose
- Git
- Modern web browser (Chrome, Firefox, Safari)
- Conda environment manager
- SSH access for remote deployments

### Dependencies
- FastAPI framework for backend services
- React with TypeScript for frontend interface
- PostgreSQL for data persistence
- Nginx for reverse proxy and static file serving
- ETE3 toolkit for phylogenetic computations

## Installation and Startup

### Local Development Environment

```bash
# Clone the repository
git clone <repository-url>
cd orthoviewer

# Initialize the development environment
make setup

# Launch all services
make up

# Access the application
open http://localhost:80
```

### Production Deployment

```bash
# Build deployment artifacts
make build-deployment

# Deploy to production environment
make deploy-production
```

## Rocky VM Connection Management

### Automated Connection Scripts

To prevent SSH tunnel issues when accessing the Rocky VM deployment, use our automated connection management:

```bash
# Quick connection (recommended)
./scripts/quick-rocky.sh

# Full connection manager
./scripts/connect-rocky.sh connect

# Check connection status
./scripts/connect-rocky.sh status

# Stop tunnel
./scripts/connect-rocky.sh stop

# Restart tunnel
./scripts/connect-rocky.sh restart
```

### Manual Connection (Legacy)

```bash
# Establish SSH tunnel
ssh -L 8080:localhost:8080 rocky@10.0.0.213 -N

# Access application
open http://localhost:8080
```

### Connection Troubleshooting

The automated scripts perform comprehensive health checks:
- Rocky VM accessibility verification
- OrthoViewer service status validation
- Port conflict detection
- Tunnel process management
- Connection integrity testing

## CI/CD Pipeline

### Pipeline Architecture

The continuous integration and deployment pipeline consists of four distinct stages:

1. **Source Code Analysis**: Static code analysis and dependency verification
2. **Automated Testing**: Unit tests, integration tests, and functional validation
3. **Artifact Generation**: Docker image construction and deployment package creation
4. **Deployment Orchestration**: Automated deployment with manual security validation

### Pipeline Configuration

```yaml
stages:
  - build
  - test
  - package
  - deploy
```

### Artifact Management

Build artifacts are automatically generated and stored in GitLab:
- `orthoviewer-{commit}-{timestamp}.tar.gz`: Complete deployment package
- `deployment.env`: Environment configuration variables
- Container images tagged with commit identifiers

### Security Framework

- SSH key-based authentication for secure remote access
- Network segmentation through bastion host architecture
- Automated security scanning during build process
- Manual deployment approval for production environments

## Deployment Architecture

### Network Configuration

```
Developer PC → Bastion Host (legolas.versailles.inrae.fr) → Rocky VM (10.0.0.213)
```

### Service Architecture

```
Nginx (Port 8080) → Frontend (React) → Backend (FastAPI) → Database (PostgreSQL)
```

### Container Orchestration

The platform utilizes Docker Compose for service orchestration:
- **Frontend Service**: React application with TypeScript
- **Backend Service**: FastAPI with Conda environment
- **Database Service**: PostgreSQL with persistent storage
- **Proxy Service**: Nginx for request routing and static file serving

## Frontend Technologies

### Technology Stack
- React 18 with TypeScript for type safety
- Vite for optimized build process and development server
- Modern CSS with responsive design principles
- Component-based architecture for maintainability

### Development Workflow
```bash
cd frontend-vite
npm install
npm run dev
```

## Backend Architecture

### Three-Layer Architecture Design

1. **API Layer**: RESTful endpoints and request handling
2. **Service Layer**: Business logic and computational processing
3. **Data Access Layer**: Database operations and data management

### Conda Environment

The backend operates within a specialized Conda environment:
```bash
conda create -n orthoviewer python=3.9
conda activate orthoviewer
conda install -c conda-forge fastapi uvicorn
```

### API Documentation

Interactive API documentation available at:
- Development: `http://localhost:8002/docs`
- Production: `http://localhost:8080/api/docs`

## Performance Specifications

### Target Metrics
- Application startup time: < 30 seconds
- API response time: < 2 seconds for standard queries
- Frontend load time: < 3 seconds
- Database query optimization for large datasets

### Scalability Considerations
- Horizontal scaling through container orchestration
- Database connection pooling
- Caching strategies for frequently accessed data
- Load balancing for high-availability deployments

## Development Guidelines

### Code Quality Standards
- TypeScript strict mode enforcement
- Comprehensive test coverage requirements
- Code review process for all contributions
- Automated linting and formatting

### Testing Framework
```bash
# Backend testing
pytest tests/

# Frontend testing  
npm test
```

## Institutional Compliance

This platform adheres to INRAE (Institut National de Recherche pour l'Agriculture, l'Alimentation et l'Environnement) computational standards and security protocols. All components undergo rigorous validation to ensure compatibility with institutional infrastructure and regulatory requirements.