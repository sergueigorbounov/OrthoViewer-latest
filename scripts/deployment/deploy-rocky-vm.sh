#!/bin/bash

# Deploy OrthoViewer to Rocky VM (10.0.0.213)
# This script will deploy OrthoViewer using Docker on port 8080

set -e

ROCKY_HOST="10.0.0.213"
ROCKY_USER="rocky"
PROJECT_NAME="orthoviewer"
FORGEMIA_REPO="https://oauth2:S7-G3F8VZrJLKVFdV2Zq@forgemia.inra.fr/pepr-breif/wp2/orthoviewer.git"

echo "🚀 Starting OrthoViewer deployment to Rocky VM..."

# Function to run commands on rocky server
run_on_rocky() {
    ssh "$ROCKY_USER@$ROCKY_HOST" "$1"
}

echo "📋 Checking Rocky VM status..."
run_on_rocky "whoami && pwd && docker --version"

echo "🔄 Setting up project directory..."
run_on_rocky "mkdir -p ~/$PROJECT_NAME && cd ~/$PROJECT_NAME"

echo "📥 Cloning/updating OrthoViewer from forgemia..."
run_on_rocky "cd ~/$PROJECT_NAME && if [ -d .git ]; then git pull origin main; else git clone $FORGEMIA_REPO .; fi"

echo "🐳 Building Docker containers..."
run_on_rocky "cd ~/$PROJECT_NAME && docker-compose -f docker-compose.yml down || true"
run_on_rocky "cd ~/$PROJECT_NAME && docker-compose -f docker-compose.yml build --no-cache"

echo "🔧 Modifying docker-compose for port 8080..."
run_on_rocky "cd ~/$PROJECT_NAME && sed -i 's/80:80/8080:80/g' docker-compose.yml"

echo "🚀 Starting OrthoViewer services..."
run_on_rocky "cd ~/$PROJECT_NAME && docker-compose -f docker-compose.yml up -d"

echo "⏳ Waiting for services to start..."
sleep 10

echo "🔍 Checking service status..."
run_on_rocky "cd ~/$PROJECT_NAME && docker-compose ps"

echo "🌐 Testing OrthoViewer deployment..."
if run_on_rocky "curl -f http://localhost:8080 > /dev/null 2>&1"; then
    echo "✅ SUCCESS! OrthoViewer is running on Rocky VM!"
    echo ""
    echo "🌐 Access OrthoViewer:"
    echo "   SSH Port Forward: ssh -L 8080:localhost:8080 $ROCKY_USER@$ROCKY_HOST"
    echo "   Then open: http://localhost:8080"
    echo ""
    echo "📊 Or access directly (if firewall allows):"
    echo "   http://$ROCKY_HOST:8080"
else
    echo "❌ Deployment completed but service not responding yet"
    echo "🔧 Check logs with: ssh $ROCKY_USER@$ROCKY_HOST 'cd $PROJECT_NAME && docker-compose logs'"
fi

echo "🎉 Deployment script completed!" 