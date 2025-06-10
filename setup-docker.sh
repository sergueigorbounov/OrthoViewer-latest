#!/bin/bash

# Enhanced Docker Setup Script for OrthoViewer with conda support
# This script sets up Docker containers using conda environments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting OrthoViewer Docker Setup with conda...${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Create a new docker-compose.yml file with conda support
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: orthoviewer
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backend/init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 30s
      timeout: 10s
      retries: 5

  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile.conda
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/orthoviewer
      - PYTHONPATH=/app
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./backend:/app
      - ./data:/app/data
    command: conda run -n orthoviewer2 uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./frontend-vite
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://localhost:8000
    volumes:
      - ./frontend-vite:/app
      - /app/node_modules
    command: npm run dev -- --host 0.0.0.0

volumes:
  postgres_data:
EOF

# Create conda-based Dockerfile for backend
cat > backend/Dockerfile.conda << 'EOF'
FROM condaforge/mambaforge:latest

WORKDIR /app

# Copy environment file
COPY environment.yml .

# Create conda environment
RUN mamba env create -f environment.yml

# Make RUN commands use the new environment
SHELL ["conda", "run", "-n", "orthoviewer2", "/bin/bash", "-c"]

# Copy application code
COPY . .

# Initialize conda for shell commands
RUN echo "conda activate orthoviewer2" >> ~/.bashrc

EXPOSE 8000

CMD ["conda", "run", "-n", "orthoviewer2", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# Create environment.yml in backend directory if it doesn't exist
if [ ! -f backend/environment.yml ]; then
    cat > backend/environment.yml << 'EOF'
name: orthoviewer2
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.9
  - fastapi
  - uvicorn
  - sqlalchemy
  - psycopg2
  - alembic
  - python-multipart
  - python-jose[cryptography]
  - passlib[bcrypt]
  - pytest
  - pytest-cov
  - requests
  - numpy
  - pandas
  - pillow
  - opencv
  - scikit-image
  - matplotlib
  - pip
  - pip:
    - python-dotenv
    - pydicom
    - SimpleITK
EOF
fi

echo -e "${YELLOW}Building Docker containers with conda...${NC}"

# Build the containers
docker-compose build

echo -e "${YELLOW}Starting containers...${NC}"

# Start the containers
docker-compose up -d

echo -e "${GREEN}✅ Docker setup complete!${NC}"
echo ""
echo -e "${GREEN}Services running:${NC}"
echo -e "  🖥️  Frontend: http://localhost:3000"
echo -e "  🔗 Backend API: http://localhost:8000"
echo -e "  🗄️  PostgreSQL: localhost:5432"
echo ""
echo -e "${YELLOW}To view logs: docker-compose logs -f${NC}"
echo -e "${YELLOW}To stop: docker-compose down${NC}"
echo -e "${YELLOW}To rebuild: docker-compose build${NC}" 