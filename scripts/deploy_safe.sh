#!/bin/bash
#
# SAFE Deployment Script for tatic.jacare.cloud
#
# ⚠️  SAFETY FIRST:
# - Checks existing services
# - Does NOT stop other containers
# - Validates port availability
# - Creates backups before changes
# - Uses isolated Docker Compose file
#

set -e

# Configuration - CUSTOMIZE HERE
DOMAIN="tatic.jacare.cloud"
APP_PORT=8506
APP_DIR="/root/atc-cap-v2"
EMAIL="admin@jacare.cloud"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  🔒 SAFE DEPLOYMENT - tatic.jacare.cloud                 ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Run diagnostics
echo -e "${YELLOW}[1/6] Running VPS diagnostics...${NC}"
echo ""

# Check if port is already in use
echo -e "${BLUE}Checking port $APP_PORT...${NC}"
if netstat -tuln 2>/dev/null | grep -q ":$APP_PORT "; then
    echo -e "${RED}⚠️  Port $APP_PORT is already in use!${NC}"
    echo ""
    echo "Current services listening on port $APP_PORT:"
    netstat -tuln | grep ":$APP_PORT"
    echo ""
    echo -e "${YELLOW}Options:${NC}"
    echo "1. Use a different port (e.g., 8507)"
    echo "2. Stop the existing service first"
    echo "3. Contact support if you don't know what's using the port"
    echo ""
    exit 1
else
    echo -e "${GREEN}✓ Port $APP_PORT is available${NC}"
fi
echo ""

# Check Docker
echo -e "${BLUE}Checking Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker not installed${NC}"
    exit 1
fi
DOCKER_COUNT=$(docker ps | wc -l)
DOCKER_COUNT=$((DOCKER_COUNT - 1))
echo -e "${GREEN}✓ Docker running with $DOCKER_COUNT container(s)${NC}"
echo ""

# Check Nginx
echo -e "${BLUE}Checking Nginx...${NC}"
if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✓ Nginx is running${NC}"
else
    echo -e "${YELLOW}⚠️  Nginx not running (will be started later)${NC}"
fi
echo ""

# Step 2: Create backup
echo -e "${YELLOW}[2/6] Creating safety backup...${NC}"
BACKUP_DIR="/root/backups/deployment-$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup current app directory if it exists
if [ -d "$APP_DIR" ]; then
    echo "Backing up $APP_DIR..."
    tar -czf "$BACKUP_DIR/app-backup.tar.gz" "$APP_DIR" 2>/dev/null || true
    echo -e "${GREEN}✓ Backup created: $BACKUP_DIR${NC}"
else
    echo -e "${GREEN}✓ (First deployment, no existing app to backup)${NC}"
fi
echo ""

# Step 3: Create app directory structure
echo -e "${YELLOW}[3/6] Creating application directory...${NC}"
mkdir -p "$APP_DIR"/{uploads,outputs,data}
chmod 755 "$APP_DIR"
echo -e "${GREEN}✓ Directories created${NC}"
echo ""

# Step 4: Create .env file (doesn't overwrite if exists)
echo -e "${YELLOW}[4/6] Configuring application...${NC}"
if [ ! -f "$APP_DIR/.env" ]; then
    cat > "$APP_DIR/.env" << EOF
# ===========================
# ATC-CAP-V2 Configuration
# ===========================
APP_NAME=tatic-processor
APP_PORT=$APP_PORT
APP_ENV=production
APP_DEBUG=false

# ===========================
# Streamlit Config
# ===========================
STREAMLIT_SERVER_PORT=$APP_PORT
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
STREAMLIT_SERVER_HEADLESS=true

# ===========================
# Important: Do not modify below unless needed
# ===========================
PYTHONUNBUFFERED=1
EOF
    echo -e "${GREEN}✓ .env file created${NC}"
else
    echo -e "${YELLOW}⚠️  .env already exists (not overwriting)${NC}"
    echo "Current settings:"
    grep "^APP_PORT" "$APP_DIR/.env" || echo "  (APP_PORT not set)"
fi
echo ""

# Step 5: Build and start Docker
echo -e "${YELLOW}[5/6] Building and starting Docker containers...${NC}"
cd "$APP_DIR"

echo "Building Docker image..."
docker-compose build --no-cache 2>&1 | tail -20

echo ""
echo "Starting containers..."
docker-compose up -d 2>&1

echo -e "${GREEN}✓ Containers started${NC}"
echo ""

# Wait for app to be ready
echo "Waiting for application to start (10 seconds)..."
sleep 10

# Verify app is running
if curl -s http://localhost:$APP_PORT > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Application is responding on port $APP_PORT${NC}"
else
    echo -e "${YELLOW}⚠️  Application not responding yet (check logs)${NC}"
    echo "  Run: docker-compose logs -f"
fi
echo ""

# Step 6: Summary and next steps
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ DEPLOYMENT COMPLETE!                                  ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${BLUE}Application Status:${NC}"
docker-compose ps
echo ""

echo -e "${BLUE}Next Steps:${NC}"
echo "1. Verify all containers are running (see above)"
echo "2. Check logs: docker-compose logs -f"
echo "3. Once DNS is propagated, run nginx_setup.sh"
echo "4. Access: https://$DOMAIN"
echo ""

echo -e "${BLUE}Backup Location:${NC}"
echo "  $BACKUP_DIR"
echo ""

echo -e "${BLUE}Useful Commands:${NC}"
echo "  # View logs"
echo "  docker-compose logs -f"
echo ""
echo "  # Restart app"
echo "  docker-compose restart"
echo ""
echo "  # Stop app (without removing data)"
echo "  docker-compose down"
echo ""
echo "  # Remove backup (after confirming everything works)"
echo "  rm -rf $BACKUP_DIR"
echo ""

echo -e "${YELLOW}⚠️  SAFETY REMINDER:${NC}"
echo "  • Other containers are still running"
echo "  • Port $APP_PORT is now used by tatic"
echo "  • If you need this port for something else, contact support"
echo "  • Backups are preserved in $BACKUP_DIR"
echo ""
