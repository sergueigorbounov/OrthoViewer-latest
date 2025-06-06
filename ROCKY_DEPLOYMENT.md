# 🚀 OrthoViewer Deployment on Rocky (10.0.0.213)

## Overview
Deploy OrthoViewer on rocky server using only Docker, exposing nginx on port 8080.

## Prerequisites
- Access to rocky@10.0.0.213
- Docker (will be installed automatically)

## Deployment Steps

### 1. Connect to Rocky
```bash
# SSH tunnel for access (as mentioned in JIRA)
ssh -L 8080:localhost:8080 rocky@10.0.0.213

# Or direct SSH
ssh rocky@10.0.0.213
```

### 2. Initial Setup on Rocky
```bash
# Create project directory
mkdir -p /home/rocky/orthoviewer
cd /home/rocky/orthoviewer

# Clone the repository
git clone https://forgemia.inra.fr/pepr-breif/wp2/orthoviewer.git .
```

### 3. Deploy Using Script
```bash
# Run the deployment script
./deploy-rocky.sh
```

### 4. Manual Deployment (Alternative)
```bash
# Install Docker (if not already installed)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker rocky

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Build and run
docker-compose -f docker-compose.rocky.yml up --build -d
```

## Access the Application

### Local Access (on rocky)
```bash
curl http://localhost:8080
```

### Remote Access (from your machine)
```bash
# Set up SSH tunnel
ssh -L 8080:localhost:8080 rocky@10.0.0.213

# Then open in browser
http://localhost:8080
```

## Port Configuration
- **Nginx**: 8080 (external) → 80 (internal container)
- **Backend**: 8002 (FastAPI)
- **Frontend**: 8001 (Vite dev server)

## Useful Commands

### Check Status
```bash
docker-compose -f docker-compose.rocky.yml ps
```

### View Logs
```bash
docker-compose -f docker-compose.rocky.yml logs
```

### Restart Services
```bash
docker-compose -f docker-compose.rocky.yml restart
```

### Stop Services
```bash
docker-compose -f docker-compose.rocky.yml down
```

### Update Deployment
```bash
git pull
docker-compose -f docker-compose.rocky.yml up --build -d
```

## Troubleshooting

### If port 8080 is not accessible:
```bash
# Check if nginx is running
docker ps | grep nginx

# Check port binding
netstat -tlnp | grep 8080

# Check firewall
sudo ufw status
```

### If containers fail to start:
```bash
# Check Docker daemon
sudo systemctl status docker

# Check logs
docker-compose -f docker-compose.rocky.yml logs --tail=50
```

## File Structure on Rocky
```
/home/rocky/orthoviewer/
├── docker-compose.rocky.yml     # Rocky-specific compose file
├── deploy-rocky.sh              # Deployment script
├── frontend-vite/               # Frontend source
├── backend/                     # Backend source
├── nginx/                       # Nginx configuration
└── data/                        # Application data
```

## Security Notes
- Uses port 8080 instead of 80 to avoid requiring root privileges
- Docker runs as non-root user
- SSH tunnel recommended for remote access 