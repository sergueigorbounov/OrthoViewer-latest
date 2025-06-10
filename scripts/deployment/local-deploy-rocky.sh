#!/bin/bash

# 🚀 Local Deployment Script for Rocky
# This deploys OrthoViewer to rocky using local resources when SSH keys aren't working

set -e

ROCKY_HOST="10.0.0.213"
ROCKY_USER="rocky"
PROJECT_DIR="/home/rocky/orthoviewer"

echo "🚀 Starting local deployment to Rocky..."

# Check if sshpass is available for password automation
if ! command -v sshpass &> /dev/null; then
    echo "📦 Installing sshpass for password automation..."
    sudo apt-get update && sudo apt-get install -y sshpass
fi

# Prompt for password (will be used for all SSH commands)
echo "🔑 Rocky SSH password required for deployment:"
read -s ROCKY_PASSWORD

echo "📦 Creating deployment package..."

# Create temporary deployment directory
TEMP_DIR="/tmp/orthoviewer-deploy-$(date +%s)"
mkdir -p $TEMP_DIR

# Copy all necessary files
cp -r . $TEMP_DIR/
cd $TEMP_DIR

# Remove unnecessary files to speed up transfer
rm -rf .git
rm -rf node_modules
rm -rf __pycache__
rm -rf .pytest_cache
rm -rf logs/*

echo "📤 Transferring files to rocky..."

# Function to run SSH commands with password
ssh_cmd() {
    sshpass -p "$ROCKY_PASSWORD" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 $ROCKY_USER@$ROCKY_HOST "$@"
}

# Function to copy files with password
scp_cmd() {
    sshpass -p "$ROCKY_PASSWORD" scp -o StrictHostKeyChecking=no -r "$@"
}

# Test connection
echo "🔍 Testing rocky connection..."
ssh_cmd "whoami && hostname && echo 'Connection successful!'"

# Create project directory
echo "📁 Creating project directory on rocky..."
ssh_cmd "mkdir -p $PROJECT_DIR"

# Transfer files
echo "📤 Transferring project files..."
scp_cmd . $ROCKY_USER@$ROCKY_HOST:$PROJECT_DIR/

# Install Docker if needed
echo "🐳 Setting up Docker on rocky..."
ssh_cmd "
if ! command -v docker &> /dev/null; then
    echo 'Installing Docker...'
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    echo 'Docker installed!'
fi
"

# Install Docker Compose if needed
ssh_cmd "
if ! command -v docker-compose &> /dev/null; then
    echo 'Installing Docker Compose...'
    sudo curl -L \"https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo 'Docker Compose installed!'
fi
"

# Deploy the application
echo "🚀 Deploying OrthoViewer on rocky..."
ssh_cmd "
cd $PROJECT_DIR
chmod +x deploy-rocky.sh

# Stop any existing containers
docker-compose -f docker-compose.rocky.yml down || true

# Build and start services
echo '🏗️ Building and starting services...'
docker-compose -f docker-compose.rocky.yml up --build -d

# Wait for services
echo '⏳ Waiting for services to start...'
sleep 30

# Check status
echo '📊 Service status:'
docker-compose -f docker-compose.rocky.yml ps

# Test application
if curl -f http://localhost:8080 &> /dev/null; then
    echo '✅ OrthoViewer deployed successfully on port 8080!'
    echo '🌐 Access via SSH tunnel: ssh -L 8080:localhost:8080 rocky@10.0.0.213'
else
    echo '❌ Application not responding, checking logs...'
    docker-compose -f docker-compose.rocky.yml logs --tail=20
fi
"

# Cleanup
cd /
rm -rf $TEMP_DIR

echo "🎉 Deployment completed!"
echo ""
echo "🌐 To access OrthoViewer:"
echo "   1. Set up SSH tunnel: ssh -L 8080:localhost:8080 rocky@10.0.0.213"
echo "   2. Open browser: http://localhost:8080"
echo ""
echo "🔧 To manage the deployment:"
echo "   ssh rocky@10.0.0.213"
echo "   cd /home/rocky/orthoviewer"
echo "   docker-compose -f docker-compose.rocky.yml ps" 