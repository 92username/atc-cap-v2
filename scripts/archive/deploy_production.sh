#!/bin/bash
#
# Complete Deployment Script for tatic.jacare.cloud
#
# This script:
# 1. Updates system packages
# 2. Installs Docker and Docker Compose
# 3. Installs Nginx and Certbot
# 4. Configures SSL certificate with Let's Encrypt
# 5. Configures Nginx reverse proxy
# 6. Starts the application
#

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="tatic.jacare.cloud"
APP_PORT=8506
APP_DIR="/root/atc-cap-v2"
APP_USER="root"
APP_GROUP="root"
EMAIL="admin@jacare.cloud"  # Change this to your email

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  ATC-CAP-V2 Deployment for ${DOMAIN}  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Update system
echo -e "${YELLOW}[1/7] Updating system packages...${NC}"
apt-get update
apt-get upgrade -y

# Step 2: Install Docker
echo -e "${YELLOW}[2/7] Installing Docker and Docker Compose...${NC}"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    bash get-docker.sh
    rm get-docker.sh
    echo -e "${GREEN}✓ Docker installed${NC}"
else
    echo -e "${GREEN}✓ Docker already installed${NC}"
fi

# Ensure docker-compose
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Step 3: Install Nginx
echo -e "${YELLOW}[3/7] Installing Nginx...${NC}"
if ! command -v nginx &> /dev/null; then
    apt-get install -y nginx
    systemctl enable nginx
    echo -e "${GREEN}✓ Nginx installed${NC}"
else
    echo -e "${GREEN}✓ Nginx already installed${NC}"
fi

# Step 4: Install Certbot for SSL
echo -e "${YELLOW}[4/7] Installing Certbot for SSL...${NC}"
apt-get install -y certbot python3-certbot-nginx

# Step 5: Create Nginx configuration
echo -e "${YELLOW}[5/7] Configuring Nginx reverse proxy...${NC}"
cat > /etc/nginx/sites-available/tatic.jacare.cloud << 'NGINX_CONFIG'
upstream streamlit_app {
    server localhost:8506;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name tatic.jacare.cloud;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS configuration
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name tatic.jacare.cloud;

    # SSL certificates (will be updated by Certbot)
    ssl_certificate /etc/letsencrypt/live/tatic.jacare.cloud/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tatic.jacare.cloud/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/tatic.access.log;
    error_log /var/log/nginx/tatic.error.log;

    # Proxy to Streamlit
    location / {
        proxy_pass http://streamlit_app;
        
        # Proxy headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Streamlit specific
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
NGINX_CONFIG

# Enable site
ln -sf /etc/nginx/sites-available/tatic.jacare.cloud /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t

echo -e "${GREEN}✓ Nginx configured${NC}"

# Step 6: Obtain SSL certificate
echo -e "${YELLOW}[6/7] Obtaining SSL certificate from Let's Encrypt...${NC}"

# First start Nginx to validate domain
systemctl restart nginx

# Check if certificate already exists
if [ ! -f /etc/letsencrypt/live/tatic.jacare.cloud/fullchain.pem ]; then
    certbot certonly \
        --nginx \
        --non-interactive \
        --agree-tos \
        --email "$EMAIL" \
        -d "$DOMAIN" || {
        echo -e "${RED}Failed to obtain certificate. Continuing anyway...${NC}"
    }
else
    echo -e "${GREEN}✓ Certificate already exists${NC}"
fi

# Step 7: Start application
echo -e "${YELLOW}[7/7] Starting Docker application...${NC}"
cd "$APP_DIR"

# Create .env file if not exists
if [ ! -f .env ]; then
    cat > .env << ENV_CONFIG
APP_NAME=tatic-processor
APP_PORT=$APP_PORT
APP_ENV=production
APP_DEBUG=false
STREAMLIT_SERVER_PORT=$APP_PORT
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV_CONFIG
fi

# Build and start containers
docker-compose build
docker-compose up -d

echo -e "${GREEN}✓ Application started${NC}"

# Restart Nginx with SSL
systemctl restart nginx

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ DEPLOYMENT COMPLETE!                                  ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Application is now available at:${NC}"
echo -e "${YELLOW}https://tatic.jacare.cloud${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo -e "1. Verify DNS points to this server (147.79.82.234)"
echo -e "2. Check: ${YELLOW}curl https://tatic.jacare.cloud${NC}"
echo -e "3. View logs: ${YELLOW}docker-compose logs -f${NC}"
echo -e "4. SSL renews automatically with Certbot"
echo ""
echo -e "${BLUE}Useful commands:${NC}"
echo -e "• View app logs: ${YELLOW}docker-compose logs -f${NC}"
echo -e "• Check SSL status: ${YELLOW}certbot status${NC}"
echo -e "• Renew SSL manually: ${YELLOW}certbot renew --dry-run${NC}"
echo -e "• Nginx logs: ${YELLOW}tail -f /var/log/nginx/tatic.*.log${NC}"
echo ""
