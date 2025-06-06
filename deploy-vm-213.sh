#!/bin/bash
set -e

# =============================================================================
# OrthoViewer Deployment Script for VM 10.0.0.213
# =============================================================================
# Requirements:
# - Rocky Linux VM at rocky@10.0.0.213
# - Only Docker package installed
# - Nginx exposed on port 8080 (non-root)
# - Compile and launch from git repository
# =============================================================================

echo "🚀 Starting OrthoViewer deployment on VM 10.0.0.213..."

# Configuration
VM_HOST="rocky@10.0.0.213"
NGINX_PORT=8080
PROJECT_DIR="/home/rocky/orthoviewer"
REPO_URL="https://forgemia.inra.fr/pepr-breif/wp2/orthoviewer.git"
BRANCH="docker-infrastructure-complete"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
echo_success() { echo -e "${GREEN}✅ $1${NC}"; }
echo_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
echo_error() { echo -e "${RED}❌ $1${NC}"; }

# Function to run commands on the VM
run_on_vm() {
    echo_info "Running on VM: $1"
    ssh -o StrictHostKeyChecking=no "$VM_HOST" "$1"
}

# Function to copy files to VM
copy_to_vm() {
    echo_info "Copying $1 to VM..."
    scp -o StrictHostKeyChecking=no "$1" "$VM_HOST:$2"
}

echo_info "Connecting to VM $VM_HOST..."

# 1. Prepare the VM environment
echo_info "Step 1: Preparing VM environment..."
run_on_vm "
    # Update system if needed
    sudo dnf update -y

    # Install Docker if not already installed
    if ! command -v docker &> /dev/null; then
        echo 'Installing Docker...'
        sudo dnf install -y docker
        sudo systemctl enable docker
        sudo systemctl start docker
        sudo usermod -aG docker rocky
        echo 'Docker installed successfully'
    else
        echo 'Docker already installed'
    fi

    # Install git if not already installed
    if ! command -v git &> /dev/null; then
        sudo dnf install -y git
    fi

    # Create project directory
    mkdir -p $PROJECT_DIR
"

# 2. Clone/update the repository
echo_info "Step 2: Cloning/updating repository..."
run_on_vm "
    cd $PROJECT_DIR
    if [ -d '.git' ]; then
        echo 'Updating existing repository...'
        git fetch origin
        git checkout $BRANCH
        git pull origin $BRANCH
    else
        echo 'Cloning repository...'
        git clone -b $BRANCH $REPO_URL .
    fi
"

# 3. Create Docker Compose configuration for port 8080
echo_info "Step 3: Creating Docker Compose configuration..."
cat > docker-compose.vm213.yml << 'EOF'
version: '3.8'

services:
  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile
    container_name: orthoviewer_backend
    environment:
      - ENVIRONMENT=production
      - BASE_DIR=/app
      - DATA_DIR=/app/data/orthofinder
    volumes:
      - ./data:/app/data:ro
    ports:
      - "8003:8003"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8003/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./frontend-vite
      dockerfile: Dockerfile
    container_name: orthoviewer_frontend
    depends_on:
      - backend
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: orthoviewer_nginx
    ports:
      - "8080:80"  # Expose on port 8080 instead of 80
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - frontend
      - backend
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  data:
EOF

copy_to_vm docker-compose.vm213.yml "$PROJECT_DIR/"

# 4. Create nginx configuration for the VM
echo_info "Step 4: Creating nginx configuration..."
cat > nginx.vm213.conf << 'EOF'
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    access_log /var/log/nginx/access.log main;

    # Performance settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    client_max_body_size 100M;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1000;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    upstream backend {
        server backend:8003;
    }

    upstream frontend {
        server frontend:5173;
    }

    server {
        listen 80;
        server_name localhost;

        # Frontend routes
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket support for Vite HMR
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }

        # API routes
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts for long-running API calls
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Health check endpoint
        location /health {
            proxy_pass http://backend/health;
            access_log off;
        }

        # Static files with caching
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            proxy_pass http://frontend;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
EOF

copy_to_vm nginx.vm213.conf "$PROJECT_DIR/nginx/"

# 5. Deploy and start the application
echo_info "Step 5: Building and starting OrthoViewer..."
run_on_vm "
    cd $PROJECT_DIR
    
    # Stop any existing containers
    docker-compose -f docker-compose.vm213.yml down 2>/dev/null || true
    
    # Build and start the application
    echo 'Building Docker images...'
    docker-compose -f docker-compose.vm213.yml build --no-cache
    
    echo 'Starting OrthoViewer services...'
    docker-compose -f docker-compose.vm213.yml up -d
    
    # Wait for services to be ready
    echo 'Waiting for services to start...'
    sleep 30
    
    # Check service status
    echo 'Checking service status...'
    docker-compose -f docker-compose.vm213.yml ps
"

# 6. Verify deployment
echo_info "Step 6: Verifying deployment..."
sleep 10

run_on_vm "
    # Test backend health
    if curl -f http://localhost:8003/health &>/dev/null; then
        echo '✅ Backend is responding'
    else
        echo '❌ Backend health check failed'
    fi
    
    # Test nginx
    if curl -f http://localhost:8080 &>/dev/null; then
        echo '✅ Nginx is responding on port 8080'
    else
        echo '❌ Nginx on port 8080 is not responding'
    fi
    
    # Show running containers
    echo '📊 Container status:'
    docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
"

# 7. Provide access information
echo_success "🎉 OrthoViewer deployment completed!"
echo ""
echo "📋 Deployment Summary:"
echo "  • VM: $VM_HOST"
echo "  • Nginx Port: $NGINX_PORT"
echo "  • Project Directory: $PROJECT_DIR"
echo ""
echo "🌐 Access URLs:"
echo "  • Direct VM access: http://10.0.0.213:8080"
echo "  • Port forwarding: ssh -L 8080:localhost:8080 $VM_HOST"
echo "  • Then access: http://localhost:8080"
echo ""
echo "🔧 Useful Commands:"
echo "  • SSH to VM: ssh $VM_HOST"
echo "  • View logs: ssh $VM_HOST 'cd $PROJECT_DIR && docker-compose -f docker-compose.vm213.yml logs -f'"
echo "  • Restart: ssh $VM_HOST 'cd $PROJECT_DIR && docker-compose -f docker-compose.vm213.yml restart'"
echo "  • Stop: ssh $VM_HOST 'cd $PROJECT_DIR && docker-compose -f docker-compose.vm213.yml down'"
echo ""
echo "✅ OrthoViewer is now running on the dedicated VM!" 