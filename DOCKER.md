# Docker Setup for OrthoViewer

This document describes the Docker setup for OrthoViewer with separate environments for development and production.

## Architecture

The OrthoViewer application consists of 3 Docker images:

1. **Backend** (`orthoviewer/backend`): FastAPI Python application
2. **Frontend** (`orthoviewer/frontend`): React/Vite application served by nginx
3. **Nginx** (`orthoviewer/nginx`): Reverse proxy and load balancer

## Environment Configurations

### Local Development (`docker-compose-local.yml`)

- **Purpose**: Testing image builds in development environment
- **Features**:
  - Source code mounted for hot reloading (backend only)
  - Direct port exposure for debugging
  - Development-specific environment variables
  - Separate network namespace (`orthoviewer-local`)

**Ports**:
- Backend: `8003:8002` (direct access)
- Frontend: `3000:80` (direct access)
- Nginx: `8080:80` (reverse proxy)

### Production (`docker-compose.yml`)

- **Purpose**: Production deployment
- **Features**:
  - Read-only data mounts
  - Internal networking only (except nginx)
  - Production-optimized environment variables
  - Health checks for all services
  - Proper restart policies

**Ports**:
- Nginx: `80:80` (only external access point)

## Usage

### Building Images

Use the provided build script:

```bash
# Build all images (local + production)
./build-images.sh

# Build only local development images
./build-images.sh local

# Build only production images
./build-images.sh prod

# List available images
./build-images.sh list

# Clean up old images
./build-images.sh clean

# Show help
./build-images.sh help
```

### Running the Application

#### Local Development

```bash
# Start local development environment
docker-compose -f docker-compose-local.yml up -d

# View logs
docker-compose -f docker-compose-local.yml logs -f

# Stop services
docker-compose -f docker-compose-local.yml down
```

Access points:
- Full application: http://localhost:8080
- Frontend only: http://localhost:3000
- Backend API: http://localhost:8003/api
- Backend docs: http://localhost:8003/docs

#### Production

```bash
# Start production environment
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Access point:
- Application: http://localhost (or your domain)

### Development Workflow

1. **Code Changes**: Make changes to your source code
2. **Backend**: 
   - Local: Changes are reflected via volume mount (restart container if needed)
   - Production: Rebuild image with `./build-images.sh prod`
3. **Frontend**: Rebuild image as it's compiled during build
   ```bash
   ./build-images.sh local  # or prod
   docker-compose -f docker-compose-local.yml up -d frontend
   ```

### Image Tags

Each environment uses specific tags:

- **Local**: `orthoviewer/{service}:local`
- **Production**: `orthoviewer/{service}:prod`
- **Latest**: `orthoviewer/{service}:latest`

## Health Checks

All services include health checks:

- **Backend**: `curl -f http://localhost:8002/health`
- **Frontend**: `curl -f http://localhost:80`
- **Nginx**: `curl -f http://localhost/health`

## Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 8003, 3000, 8080 (local) or 80 (prod) are available
2. **Build failures**: Check Docker logs with `docker-compose logs <service>`
3. **Network issues**: Verify services are in the same Docker network

### Debugging Commands

```bash
# Check container status
docker-compose ps

# View container logs
docker-compose logs <service_name>

# Execute shell in container
docker-compose exec <service_name> /bin/bash

# Check network connectivity
docker-compose exec backend curl -f http://frontend:80
docker-compose exec nginx curl -f http://backend:8002/health
```

### Rebuilding After Changes

```bash
# Rebuild specific service
docker-compose build <service_name>

# Rebuild and restart
docker-compose up -d --build <service_name>

# Full rebuild
./build-images.sh && docker-compose up -d
```

## File Structure

```
├── docker-compose.yml              # Production configuration
├── docker-compose-local.yml        # Local development configuration
├── build-images.sh                 # Image build script
├── backend/
│   └── Dockerfile                  # Backend image definition
├── frontend-vite/
│   └── Dockerfile                  # Frontend image definition
└── nginx/
    ├── Dockerfile                  # Nginx image definition
    └── nginx.conf                  # Nginx configuration
```

## Security Considerations

- Production uses read-only volume mounts where possible
- Internal service communication only (except nginx)
- Health checks ensure service reliability
- Proper user permissions in containers 