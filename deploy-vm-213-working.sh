#!/bin/bash

# Deploy OrthoViewer to Rocky VM with proper SSH agent handling
set -e

echo "🚀 Deploying OrthoViewer to rocky VM..."

# Start SSH agent and add key
echo "🔑 Setting up SSH agent..."
eval $(ssh-agent -s)
ssh-add ~/.ssh/id_ed25519

echo "✅ SSH agent ready, testing connection..."
ssh rocky 'whoami && hostname && echo "SSH connection successful!"'

echo "🚀 Starting deployment..."
ssh rocky "
    echo '📁 Setting up project directory...'
    mkdir -p /home/rocky/orthoviewer
    cd /home/rocky/orthoviewer
    
    echo '📦 Cloning repository...'
    if [ -d '.git' ]; then
        git pull origin docker-infrastructure-complete
    else
        git clone https://forgemia.inra.fr/pepr-breif/wp2/orthoviewer.git .
        git checkout docker-infrastructure-complete
    fi
    
    echo '🐳 Installing Docker if needed...'
    if ! command -v docker &> /dev/null; then
        sudo dnf update -y
        sudo dnf install -y docker docker-compose
        sudo systemctl enable docker
        sudo systemctl start docker
        sudo usermod -aG docker rocky
        echo 'Docker installed!'
    else
        echo 'Docker already available'
    fi
    
    echo '🛑 Stopping existing containers...'
    docker-compose down 2>/dev/null || true
    
    echo '🔨 Building and starting OrthoViewer...'
    docker-compose build --no-cache
    docker-compose up -d
    
    echo '⏳ Waiting for services to start...'
    sleep 30
    
    echo '📊 Checking deployment status...'
    docker-compose ps
    
    echo '🌐 Testing application...'
    if curl -f http://localhost:8080 &>/dev/null; then
        echo '✅ OrthoViewer is running successfully!'
        echo '🌐 Access URL: http://10.0.0.213:8080'
    else
        echo '⚠️  Application not responding yet, checking logs...'
        docker-compose logs --tail=10
    fi
"

echo "🎉 Deployment script completed!"
echo ""
echo "🌐 Access OrthoViewer at: http://10.0.0.213:8080"
echo "🔧 Or via SSH tunnel: ssh -L 8080:localhost:8080 rocky" 