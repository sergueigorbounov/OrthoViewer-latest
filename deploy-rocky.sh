#!/bin/bash

# 🚀 OrthoViewer Deployment Script for Rocky (10.0.0.213)
# This script deploys OrthoViewer using only Docker on port 8080

set -e

echo "🚀 Starting OrthoViewer deployment on Rocky..."

# Check if we're on the right server
if [ "$(hostname)" != "rocky" ]; then
    echo "⚠️  Warning: This script is designed for rocky server"
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    echo "✅ Docker installed. Please logout and login again, then re-run this script."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Installing..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Create project directory
PROJECT_DIR="/home/rocky/orthoviewer"
echo "📁 Setting up project directory: $PROJECT_DIR"
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.rocky.yml down || true

# Pull the latest code (you'll need to set this up)
echo "📥 Pulling latest code..."
if [ ! -d ".git" ]; then
    echo "ℹ️  Git repository not found. Please clone the repository first:"
    echo "    git clone https://forgemia.inra.fr/pepr-breif/wp2/orthoviewer.git ."
    exit 1
fi

git pull origin main || git pull forgemia main

# Build and start services
echo "🏗️  Building and starting services..."
docker-compose -f docker-compose.rocky.yml up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check service health
echo "🔍 Checking service health..."
docker-compose -f docker-compose.rocky.yml ps

# Test if the application is accessible
echo "🧪 Testing application..."
if curl -f http://localhost:8080 &> /dev/null; then
    echo "✅ OrthoViewer is successfully deployed on port 8080!"
    echo ""
    echo "🌐 Access the application:"
    echo "   Local: http://localhost:8080"
    echo "   SSH Tunnel: ssh -L 8080:localhost:8080 rocky@10.0.0.213"
    echo ""
    echo "📊 Service status:"
    docker-compose -f docker-compose.rocky.yml ps
else
    echo "❌ Application not responding on port 8080"
    echo "📋 Container logs:"
    docker-compose -f docker-compose.rocky.yml logs --tail=20
    exit 1
fi

echo "🎉 Deployment completed successfully!" 