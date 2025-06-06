# 🚀 Forgemia → Rocky Automatic Deployment Setup

## Overview
This guide sets up **automatic deployment from Forgemia to Rocky** using GitLab CI/CD.

## GitLab CI/CD Variables Setup

Go to your project in Forgemia: `https://forgemia.inra.fr/pepr-breif/wp2/orthoviewer`

Navigate to: **Settings → CI/CD → Variables**

### Required Variables:

#### 1. `ROCKY_SSH_PRIVATE_KEY`
- **Type**: Variable (File recommended)
- **Value**: Your private SSH key for connecting to rocky
- **Protected**: ✅ Yes
- **Masked**: ✅ Yes

To get the SSH key:
```bash
# If you don't have a key for rocky, create one:
ssh-keygen -t ed25519 -f ~/.ssh/id_rocky -C "forgemia-ci@rocky"

# Copy the private key content:
cat ~/.ssh/id_rocky

# Copy the public key to rocky:
ssh-copy-id -i ~/.ssh/id_rocky.pub rocky@10.0.0.213
```

#### 2. `ROCKY_SSH_KNOWN_HOSTS`
- **Type**: Variable
- **Value**: SSH fingerprint for rocky server
- **Protected**: ✅ Yes

To get known hosts:
```bash
ssh-keyscan 10.0.0.213
```

## Deployment Process

### 1. **Automatic Trigger**
When you push to `main` branch, GitLab will:
- ✅ Run tests
- ✅ Build Docker images
- ⏸️  **Wait for manual deployment trigger**

### 2. **Manual Deployment**
Go to: **CI/CD → Pipelines → Manual Jobs**
- Click "▶️ deploy_rocky" to deploy to rocky
- Click "🔍 health_check" to verify deployment

### 3. **Deployment Steps**
The pipeline will:
1. SSH into rocky server
2. Clone/update code from forgemia
3. Run `deploy-rocky.sh` script
4. Start Docker containers on port 8080
5. Verify deployment is working

## Access Deployed Application

### SSH Tunnel (Recommended)
```bash
ssh -L 8080:localhost:8080 rocky@10.0.0.213
```
Then open: `http://localhost:8080`

### Direct Access (if firewall allows)
```bash
curl http://10.0.0.213:8080
```

## GitLab CI/CD Pipeline Stages

### 🧪 **Test**
- Runs backend tests with pytest
- Validates code quality

### 🏗️ **Build** 
- Builds Docker images
- Validates containers

### 🚀 **Deploy**
- **Manual trigger required**
- SSH deployment to rocky
- Health verification

## Troubleshooting

### SSH Issues
```bash
# Test SSH connection manually
ssh rocky@10.0.0.213 "whoami && docker --version"
```

### Pipeline Debugging
1. Check GitLab CI/CD logs
2. Verify SSH keys are correct
3. Ensure rocky has Docker installed

### Deployment Verification
```bash
# Check if containers are running on rocky
ssh rocky@10.0.0.213 "docker ps"

# Check application logs
ssh rocky@10.0.0.213 "cd /home/rocky/orthoviewer && docker-compose -f docker-compose.rocky.yml logs"
```

## Benefits

✅ **Automated Testing** - Code validated before deployment
✅ **One-Click Deployment** - Deploy with single button click
✅ **Rollback Capability** - Easy to revert if needed
✅ **Health Monitoring** - Automatic verification
✅ **Secure** - SSH keys managed by GitLab CI/CD

## Workflow

```
Code Push → Forgemia → GitLab CI/CD → SSH → Rocky → Docker → Port 8080
```

Now you can deploy directly from forgemia to rocky with full automation! 🎉 