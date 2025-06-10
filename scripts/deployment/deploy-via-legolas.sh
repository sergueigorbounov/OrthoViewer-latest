#!/bin/bash

# 🚀 Deploy via Legolas Jump Host
# Since direct SSH to rocky failed, we'll use legolas as intermediary

set -e

LEGOLAS_HOST="legolas"
ROCKY_HOST="10.0.0.213"
ROCKY_USER="rocky"
PROJECT_DIR="/home/rocky/orthoviewer"

echo "🚀 Deploying OrthoViewer via Legolas jump host..."

# Create clean deployment package
echo "📦 Creating deployment package..."
TEMP_DIR="/tmp/orthoviewer-deploy-$(date +%s)"
mkdir -p $TEMP_DIR

# Copy and clean project
cp -r . $TEMP_DIR/
cd $TEMP_DIR

# Remove heavy files
echo "🧹 Cleaning up heavy files..."
rm -rf .git
rm -rf node_modules
rm -rf frontend-vite/node_modules
rm -rf __pycache__
rm -rf .pytest_cache
rm -rf logs/*

echo "📊 Package size after cleanup:"
du -sh .

# Create tarball for transfer
echo "📦 Creating tarball..."
tar -czf orthoviewer.tar.gz .

echo "📤 Transferring via legolas..."

# Transfer tarball to legolas first
scp orthoviewer.tar.gz legolas:~/

# Then from legolas to rocky
ssh legolas "scp orthoviewer.tar.gz rocky@${ROCKY_HOST}:~/"

echo "🚀 Deploying on rocky via legolas..."

# Deploy via legolas SSH tunnel
ssh legolas "ssh rocky@${ROCKY_HOST} '
    echo \"📁 Setting up project directory...\"
    mkdir -p ${PROJECT_DIR}
    cd ${PROJECT_DIR}
    
    echo \"📦 Extracting files...\"
    tar -xzf ~/orthoviewer.tar.gz
    
    echo \"🐳 Setting up Docker...\"
    if ! command -v docker &> /dev/null; then
        echo \"Installing Docker...\"
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker \$USER
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo \"Installing Docker Compose...\"
        sudo curl -L \"https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
    fi
    
    echo \"🚀 Starting deployment...\"
    docker-compose -f docker-compose.rocky.yml down || true
    docker-compose -f docker-compose.rocky.yml up --build -d
    
    echo \"⏳ Waiting for services...\"
    sleep 30
    
    echo \"📊 Service status:\"
    docker-compose -f docker-compose.rocky.yml ps
    
    if curl -f http://localhost:8080 &> /dev/null; then
        echo \"✅ OrthoViewer deployed successfully!\"
        echo \"🌐 Access via SSH tunnel: ssh -L 8080:localhost:8080 rocky@${ROCKY_HOST}\"
    else
        echo \"❌ Application not responding, checking logs...\"
        docker-compose -f docker-compose.rocky.yml logs --tail=20
    fi
'"

# Cleanup
cd /
rm -rf $TEMP_DIR

echo "🎉 Deployment completed!"
echo ""
echo "🌐 To access OrthoViewer:"
echo "   1. Set up SSH tunnel: ssh -L 8080:localhost:8080 rocky@${ROCKY_HOST}"
echo "   2. Open browser: http://localhost:8080" 