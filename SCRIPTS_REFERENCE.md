# OrthoViewer Scripts Quick Reference

## 🚀 Getting Started (First Time Setup)

```bash
# 1. Install all dependencies
./scripts/install_dependencies.sh

# 2. Set up database
./scripts/setup_database.sh

# 3. Start development environment
./dev.sh
```

## 🔧 Development Workflow

### Main Development
- **`./dev.sh`** - Start full development environment (backend + frontend + file watching)
- **`./tdd.sh`** - Test-driven development with live testing

### Individual Services
- **`./scripts/backend.sh`** - Backend only
- **`./scripts/frontend.sh`** - Frontend only

### Production/Server
- **`./start-server.sh`** - Production server startup
- **`./fastapi_start.sh`** - FastAPI with automatic frontend startup

## 🧪 Testing

```bash
# All tests
./scripts/test-all.sh

# Specific test types
./scripts/test-unit.sh           # Unit tests
./scripts/test-integration.sh    # Integration tests  
./scripts/test-performance.sh    # Performance tests
./scripts/test-e2e.sh           # End-to-end tests
```

## 🐳 Docker Development

```bash
# Full Docker setup (first time)
./setup-docker.sh

# Start Docker environment
./scripts/docker-start.sh

# Individual Docker services
./scripts/docker-backend.sh     # Backend container only
./scripts/docker-frontend.sh    # Frontend container only
```

## 🚚 Deployment

```bash
# Automated deployment
./scripts/deployment/auto-deploy-rocky.sh

# Manual deployment options
./scripts/deployment/deploy-rocky.sh
./scripts/deployment/local-deploy-rocky.sh
./scripts/deployment/deploy-vm-213.sh
```

## 🛠️ Utilities

```bash
# Fix compatibility issues
./scripts/utilities/fix_biosemantic_issues.sh

# Database setup
./scripts/setup_database.sh

# Dependencies installation
./scripts/install_dependencies.sh
```

## 📁 Script Organization

```
Root Level (Main Scripts)
├── dev.sh                 # 🟢 Main development environment
├── tdd.sh                 # 🟡 Test-driven development
├── start-server.sh        # 🔵 Production server
├── fastapi_start.sh       # 🔵 FastAPI + frontend
└── setup-docker.sh        # 🐳 Docker setup

scripts/                   # Organized utility scripts
├── backend.sh             # Backend only
├── frontend.sh            # Frontend only
├── install_dependencies.sh # Install deps
├── setup_database.sh      # Database setup
├── test-*.sh             # Testing scripts
├── docker-*.sh           # Docker scripts
├── deployment/           # Deployment scripts
│   └── *.sh             # Various deployment options
└── utilities/            # Utility scripts
    └── *.sh             # Maintenance utilities
```

## 🎯 Common Use Cases

### "I want to start developing"
```bash
./dev.sh
```

### "I want to run tests while developing"
```bash
./tdd.sh
```

### "I want to test a specific component"
```bash
./tdd.sh --test=ComponentName
```

### "I want to deploy to Rocky server"
```bash
./scripts/deployment/auto-deploy-rocky.sh
```

### "I want to run only backend"
```bash
./scripts/backend.sh
```

### "I want to run everything in Docker"
```bash
./setup-docker.sh
```

### "Something's broken with dependencies"
```bash
./scripts/install_dependencies.sh
./scripts/utilities/fix_biosemantic_issues.sh
```

## 💡 Pro Tips

1. **Use `./dev.sh` for daily development** - It's the most comprehensive
2. **Use `./tdd.sh` when writing tests** - Live testing with file watching
3. **Check `scripts/README.md`** for detailed documentation
4. **All scripts have `--help`** option for usage information
5. **Scripts use conda by default** with pip fallback
6. **Environment variables** can customize ports and settings

## 🔍 Troubleshooting

### Port conflicts
Scripts automatically kill processes on conflicting ports

### Missing dependencies
```bash
./scripts/install_dependencies.sh
```

### Database issues
```bash
./scripts/setup_database.sh
```

### ETE3/BioSemantic issues
```bash
./scripts/utilities/fix_biosemantic_issues.sh
```

### Docker issues
```bash
./setup-docker.sh
```

---

For detailed documentation, see:
- `scripts/README.md` - Complete scripts documentation
- `CONDA_MIGRATION_SUMMARY.md` - Conda migration details
- Individual script `--help` options 