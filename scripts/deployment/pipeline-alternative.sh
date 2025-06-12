#!/bin/bash
# Alternative deployment approach when SSH from pipeline fails

set -e

echo "🚀 ALTERNATIVE DEPLOYMENT APPROACH"
echo "=================================="
echo "This script works around SSH connectivity issues in CI/CD pipelines"
echo ""

# Configuration
ROCKY_HOST="10.0.0.213"
ROCKY_USER="rocky"
PROJECT_DIR="/home/rocky/orthoviewer"

echo "📋 Deployment Options:"
echo ""
echo "1. 📦 ARTIFACT-BASED DEPLOYMENT"
echo "   - Pipeline creates deployment artifact"
echo "   - Manual download and deployment on target"
echo ""
echo "2. 🐳 DOCKER REGISTRY DEPLOYMENT"
echo "   - Pipeline builds and pushes to registry"
echo "   - Target pulls from registry"
echo ""
echo "3. 🔄 WEBHOOK-BASED DEPLOYMENT"
echo "   - Pipeline triggers webhook"
echo "   - Target server pulls and deploys"
echo ""

# Option 1: Create deployment artifact
create_deployment_artifact() {
    echo "📦 Creating deployment artifact..."
    
    # Create clean build
    cd frontend-vite
    
    # Check if package-lock.json exists
    if [ -f package-lock.json ]; then
        echo "Using npm ci (lock file exists)"
        npm ci --legacy-peer-deps
    else
        echo "Using npm install (no lock file)"
        npm install --legacy-peer-deps --no-optional
    fi
    
    npm run build
    cd ..
    
    # Create deployment package
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    ARTIFACT_NAME="orthoviewer-${TIMESTAMP}.tar.gz"
    
    tar -czf "${ARTIFACT_NAME}" \
        --exclude='.git' \
        --exclude='node_modules' \
        --exclude='__pycache__' \
        --exclude='.pytest_cache' \
        --exclude='logs' \
        --exclude='*.tar.gz' \
        .
    
    echo "✅ Deployment artifact created: ${ARTIFACT_NAME}"
    echo ""
    echo "📥 Manual deployment instructions:"
    echo "1. Download: ${ARTIFACT_NAME}"
    echo "2. Upload to Rocky VM: scp ${ARTIFACT_NAME} rocky@${ROCKY_HOST}:~/"
    echo "3. Deploy: ssh rocky@${ROCKY_HOST} 'cd ${PROJECT_DIR} && tar -xzf ~/${ARTIFACT_NAME} && docker compose -f docker-compose.rocky.yml up -d'"
    
    return 0
}

# Option 2: Docker registry approach
setup_docker_registry_deployment() {
    echo "🐳 Setting up Docker registry deployment..."
    
    cat > docker-deploy.yml << 'EOF'
# Docker Registry Deployment
# This approach pushes images to a registry and pulls them on target

version: '3.8'
services:
  backend:
    image: ${REGISTRY}/orthoviewer-backend:${TAG}
    # ... rest of config from docker-compose.rocky.yml
  
  frontend:
    image: ${REGISTRY}/orthoviewer-frontend:${TAG}
    # ... rest of config from docker-compose.rocky.yml
EOF

    echo "✅ Docker registry deployment template created"
    echo "Configure your CI/CD to push to a registry accessible from Rocky VM"
}

# Option 3: Webhook-based deployment
setup_webhook_deployment() {
    echo "🔄 Setting up webhook-based deployment..."
    
    cat > webhook-deploy.sh << 'EOF'
#!/bin/bash
# Webhook deployment script for Rocky VM
# This script should run on the Rocky VM and be triggered by CI/CD

PROJECT_DIR="/home/rocky/orthoviewer"
REPO_URL="https://forgemia.inra.fr/pepr-breif/wp2/orthoviewer.git"
BRANCH="feat/GNP-6697-rocky-deployment"

echo "🔄 Webhook deployment triggered"
cd $PROJECT_DIR

# Pull latest changes
git fetch origin
git checkout $BRANCH
git pull origin $BRANCH

# Deploy
docker compose -f docker-compose.rocky.yml down
docker compose -f docker-compose.rocky.yml up --build -d

echo "✅ Webhook deployment complete"
EOF

    chmod +x webhook-deploy.sh
    
    echo "✅ Webhook deployment script created"
    echo "Set up a webhook endpoint on Rocky VM to trigger this script"
}

# Main execution
case "${1:-artifact}" in
    "artifact")
        create_deployment_artifact
        ;;
    "registry")
        setup_docker_registry_deployment
        ;;
    "webhook")
        setup_webhook_deployment
        ;;
    *)
        echo "Usage: $0 [artifact|registry|webhook]"
        exit 1
        ;;
esac

echo ""
echo "🎯 RECOMMENDED IMMEDIATE SOLUTION:"
echo "1. Run: $0 artifact"
echo "2. Download the created tar.gz file"
echo "3. Manually deploy to Rocky VM"
echo "4. Fix network issues for future automated deployments" 