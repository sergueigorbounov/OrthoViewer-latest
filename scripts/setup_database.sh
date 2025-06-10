#!/bin/bash

# Database Setup Script using conda
# Sets up PostgreSQL database for OrthoViewer

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up OrthoViewer database with conda...${NC}"

# Check if conda environment exists
ENV_NAME="orthoviewer2"
if ! conda env list | grep -q "$ENV_NAME"; then
    echo -e "${RED}conda environment '$ENV_NAME' not found.${NC}"
    echo -e "${YELLOW}Please run: cd backend && conda env create -f environment.yml${NC}"
    exit 1
fi

# Activate conda environment
source $(conda info --base)/etc/profile.d/conda.sh
conda activate "$ENV_NAME"

# Database configuration
DB_NAME="orthoviewer"
DB_USER="postgres"
DB_PASSWORD="password"
DB_HOST="localhost"
DB_PORT="5432"

# Check if PostgreSQL is running
if ! pg_isready -h "$DB_HOST" -p "$DB_PORT" >/dev/null 2>&1; then
    echo -e "${RED}PostgreSQL is not running on $DB_HOST:$DB_PORT${NC}"
    echo -e "${YELLOW}Please start PostgreSQL first:${NC}"
    echo -e "  sudo systemctl start postgresql   # Linux"
    echo -e "  brew services start postgresql   # macOS"
    echo -e "  Or use Docker: docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=password postgres:13"
    exit 1
fi

# Create database if it doesn't exist
echo -e "${BLUE}Creating database '$DB_NAME'...${NC}"
createdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$DB_NAME" 2>/dev/null || {
    echo -e "${YELLOW}Database '$DB_NAME' already exists or creation failed${NC}"
}

# Navigate to backend directory
cd backend

# Run database migrations using conda environment
echo -e "${BLUE}Running database migrations...${NC}"
conda run -n "$ENV_NAME" alembic upgrade head

# Create initial data (if script exists)
if [ -f "scripts/create_sample_data.py" ]; then
    echo -e "${BLUE}Creating sample data...${NC}"
    conda run -n "$ENV_NAME" python scripts/create_sample_data.py
fi

echo -e "${GREEN}✅ Database setup complete!${NC}"
echo ""
echo -e "${BLUE}Database connection details:${NC}"
echo -e "  Host: $DB_HOST"
echo -e "  Port: $DB_PORT"
echo -e "  Database: $DB_NAME"
echo -e "  User: $DB_USER"
echo ""
echo -e "${BLUE}Connection URL:${NC}"
echo -e "  postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"
echo "" 