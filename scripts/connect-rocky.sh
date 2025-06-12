#!/bin/bash

# OrthoViewer Rocky VM Connection Manager
# Automatically manages SSH tunnel for accessing Rocky deployment

set -e

ROCKY_HOST="rocky@10.0.0.213"
LOCAL_PORT="8080"
REMOTE_PORT="8080"
TUNNEL_PID_FILE="/tmp/orthoviewer-tunnel.pid"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if tunnel is already running
check_tunnel() {
    if [[ -f "$TUNNEL_PID_FILE" ]]; then
        local pid=$(cat "$TUNNEL_PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0  # Tunnel is running
        else
            rm -f "$TUNNEL_PID_FILE"
            return 1  # PID file exists but process is dead
        fi
    fi
    return 1  # No tunnel
}

# Check if local port is in use
check_port() {
    if ss -tlnp | grep -q ":$LOCAL_PORT "; then
        return 0  # Port in use
    fi
    return 1  # Port free
}

# Test Rocky VM connectivity
test_rocky() {
    log "Testing Rocky VM connectivity..."
    if ssh -o ConnectTimeout=5 "$ROCKY_HOST" "echo 'Rocky VM accessible'" > /dev/null 2>&1; then
        success "Rocky VM is accessible"
        return 0
    else
        error "Cannot connect to Rocky VM"
        return 1
    fi
}

# Test if OrthoViewer is running on Rocky
test_orthoviewer() {
    log "Testing OrthoViewer on Rocky VM..."
    if ssh "$ROCKY_HOST" "curl -s -f http://localhost:$REMOTE_PORT > /dev/null"; then
        success "OrthoViewer is running on Rocky VM"
        return 0
    else
        error "OrthoViewer is not accessible on Rocky VM"
        return 1
    fi
}

# Start SSH tunnel
start_tunnel() {
    log "Starting SSH tunnel: localhost:$LOCAL_PORT → rocky:$REMOTE_PORT"
    
    # Start tunnel in background
    ssh -L "$LOCAL_PORT:localhost:$REMOTE_PORT" "$ROCKY_HOST" -N -f
    
    # Get the PID
    local tunnel_pid=$(ps aux | grep "ssh -L $LOCAL_PORT:localhost:$REMOTE_PORT" | grep -v grep | awk '{print $2}')
    
    if [[ -n "$tunnel_pid" ]]; then
        echo "$tunnel_pid" > "$TUNNEL_PID_FILE"
        success "SSH tunnel started (PID: $tunnel_pid)"
        
        # Test the tunnel
        sleep 2
        if curl -s -f "http://localhost:$LOCAL_PORT" > /dev/null; then
            success "Tunnel is working! Access: http://localhost:$LOCAL_PORT"
        else
            warning "Tunnel started but OrthoViewer not responding"
        fi
    else
        error "Failed to start SSH tunnel"
        return 1
    fi
}

# Stop SSH tunnel
stop_tunnel() {
    if [[ -f "$TUNNEL_PID_FILE" ]]; then
        local pid=$(cat "$TUNNEL_PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            log "Stopping SSH tunnel (PID: $pid)"
            kill "$pid"
            rm -f "$TUNNEL_PID_FILE"
            success "SSH tunnel stopped"
        else
            warning "Tunnel PID file exists but process not found"
            rm -f "$TUNNEL_PID_FILE"
        fi
    else
        warning "No tunnel PID file found"
    fi
}

# Show tunnel status
status() {
    echo -e "\n${BLUE}🔍 OrthoViewer Rocky Connection Status${NC}"
    echo "=================================="
    
    # Check tunnel
    if check_tunnel; then
        local pid=$(cat "$TUNNEL_PID_FILE")
        success "SSH Tunnel: ACTIVE (PID: $pid)"
    else
        warning "SSH Tunnel: INACTIVE"
    fi
    
    # Check port
    if check_port; then
        success "Local Port $LOCAL_PORT: IN USE"
    else
        warning "Local Port $LOCAL_PORT: FREE"
    fi
    
    # Test accessibility
    if curl -s -f "http://localhost:$LOCAL_PORT" > /dev/null 2>&1; then
        success "OrthoViewer: ACCESSIBLE at http://localhost:$LOCAL_PORT"
    else
        warning "OrthoViewer: NOT ACCESSIBLE"
    fi
    
    echo ""
}

# Auto-connect function
connect() {
    log "🚀 Starting OrthoViewer Rocky Connection..."
    
    # Test Rocky VM first
    if ! test_rocky; then
        error "Cannot proceed - Rocky VM not accessible"
        exit 1
    fi
    
    # Test if OrthoViewer is running
    if ! test_orthoviewer; then
        error "OrthoViewer is not running on Rocky VM"
        echo "Try: ssh $ROCKY_HOST 'cd /home/rocky/orthoviewer && docker-compose up -d'"
        exit 1
    fi
    
    # Check if tunnel already exists
    if check_tunnel; then
        success "SSH tunnel already running"
        status
        return 0
    fi
    
    # Check if port is occupied by something else
    if check_port; then
        error "Port $LOCAL_PORT is already in use by another process"
        echo "Kill the process or use a different port"
        exit 1
    fi
    
    # Start the tunnel
    start_tunnel
    status
}

# Main command handling
case "${1:-connect}" in
    "connect"|"start")
        connect
        ;;
    "stop"|"disconnect")
        stop_tunnel
        ;;
    "status"|"check")
        status
        ;;
    "restart")
        stop_tunnel
        sleep 1
        connect
        ;;
    "help"|"--help"|"-h")
        echo "OrthoViewer Rocky Connection Manager"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  connect/start    - Start SSH tunnel to Rocky VM (default)"
        echo "  stop/disconnect  - Stop SSH tunnel"
        echo "  status/check     - Show connection status"
        echo "  restart          - Restart SSH tunnel"
        echo "  help             - Show this help"
        echo ""
        echo "Access URL: http://localhost:$LOCAL_PORT"
        ;;
    *)
        error "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac 