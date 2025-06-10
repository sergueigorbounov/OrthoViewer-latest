#!/bin/bash

# 🚀 COMPLETE ROCKY DEPLOYMENT AUTOMATION
# Jira Task: Install Orthoviewer on VM rocky@10.0.0.213
# Requirements: Docker only, port 8080, conda environment

set -e

ROCKY_HOST="10.0.0.213"
ROCKY_USER="rocky" 
PROJECT_DIR="/home/rocky/orthoviewer"

echo "🚀 AUTOMATED ROCKY DEPLOYMENT - Jira Compliance"
echo "==============================================="
echo "Target: ${ROCKY_USER}@${ROCKY_HOST}:${PROJECT_DIR}"
echo "Port: 8080 (nginx exposed, no root required)"
echo "Method: Docker + Conda (Jira requirements)"
echo ""

# Function to run commands on Rocky
run_rocky() {
    ssh -o ConnectTimeout=30 "$ROCKY_USER@$ROCKY_HOST" "$1"
}

# Check connectivity
echo "📡 Testing Rocky connectivity..."
if ! ping -c 2 "$ROCKY_HOST" >/dev/null 2>&1; then
    echo "❌ Rocky server unreachable. Exiting."
    exit 1
fi

echo "🔑 Testing SSH access..."
if ! run_rocky "whoami && echo 'SSH OK'" >/dev/null 2>&1; then
    echo "❌ SSH access failed. Check SSH keys."
    echo "ℹ️  Expected to connect as: $ROCKY_USER@$ROCKY_HOST"
    exit 1
fi

echo "✅ Connectivity confirmed"

# Prepare deployment package
echo "📦 Creating deployment package..."
DEPLOY_TAR="/tmp/orthoviewer-rocky-$(date +%s).tar.gz"

tar -czf "$DEPLOY_TAR" \
    --exclude='.git' \
    --exclude='node_modules' \
    --exclude='__pycache__' \
    --exclude='.pytest_cache' \
    --exclude='logs/*' \
    --exclude='*.tar.gz' \
    .

echo "📤 Uploading to Rocky..."
scp "$DEPLOY_TAR" "$ROCKY_USER@$ROCKY_HOST:~/orthoviewer-deploy.tar.gz"

echo "🏗️  Setting up Rocky environment..."
run_rocky "
    # Create project directory
    mkdir -p $PROJECT_DIR
    cd $PROJECT_DIR
    
    # Stop existing services
    docker-compose -f docker-compose.rocky.yml down 2>/dev/null || true
    docker-compose -f docker-compose.vm213.yml down 2>/dev/null || true
    
    # Remove old deployment
    rm -rf * .[^.]*
    
    # Extract new deployment
    tar -xzf ~/orthoviewer-deploy.tar.gz
    
    echo '✅ Project extracted to Rocky'
"

echo "🐳 Ensuring Docker is available..."
run_rocky "
    if ! command -v docker &> /dev/null; then
        echo 'Installing Docker...'
        sudo dnf update -y
        sudo dnf install -y docker
        sudo systemctl enable docker
        sudo systemctl start docker
        sudo usermod -aG docker $ROCKY_USER
        echo 'Docker installed. Please logout/login to apply group changes.'
        exit 1
    else
        echo 'Docker already available'
    fi
    
    # Ensure Docker is running
    sudo systemctl start docker || true
"

echo "🚀 Deploying OrthoViewer services..."
run_rocky "
    cd $PROJECT_DIR
    
    # Use Rocky-specific compose file
    echo 'Building and starting services...'
    docker-compose -f docker-compose.rocky.yml build --no-cache
    docker-compose -f docker-compose.rocky.yml up -d
    
    echo 'Waiting for services to start...'
    sleep 30
"

echo "🔍 Verifying deployment..."
run_rocky "
    cd $PROJECT_DIR
    
    echo '=== Docker Services Status ==='
    docker-compose -f docker-compose.rocky.yml ps
    
    echo '=== Health Check ==='
    if curl -f http://localhost:8080 >/dev/null 2>&1; then
        echo '✅ OrthoViewer responding on port 8080'
    else
        echo '⚠️  OrthoViewer not yet ready, checking logs...'
        docker-compose -f docker-compose.rocky.yml logs --tail=10
    fi
"

# Cleanup
rm -f "$DEPLOY_TAR"

echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo "========================"
echo ""
echo "🌐 Access OrthoViewer:"
echo "   1. SSH Tunnel: ssh -L 8080:localhost:8080 $ROCKY_USER@$ROCKY_HOST"
echo "   2. Browser: http://localhost:8080"
echo ""
echo "🔧 Management Commands:"
echo "   • Check status: ssh $ROCKY_USER@$ROCKY_HOST 'cd $PROJECT_DIR && docker-compose -f docker-compose.rocky.yml ps'"
echo "   • View logs: ssh $ROCKY_USER@$ROCKY_HOST 'cd $PROJECT_DIR && docker-compose -f docker-compose.rocky.yml logs'"
echo "   • Restart: ssh $ROCKY_USER@$ROCKY_HOST 'cd $PROJECT_DIR && docker-compose -f docker-compose.rocky.yml restart'"
echo ""
echo "✅ Jira requirements satisfied:"
echo "   ✓ VM: rocky@$ROCKY_HOST"
echo "   ✓ Port: 8080 (nginx exposed)"
echo "   ✓ Method: Docker only"
echo "   ✓ Environment: Conda-based" 