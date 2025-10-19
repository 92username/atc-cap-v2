#!/bin/bash
#
# SAFE Nginx Setup - tatic.jacare.cloud
#
# ⚠️  SAFETY CHECKS:
# - Verifies DNS is configured
# - Checks tatic app is running
# - Backs up existing Nginx config
# - Does NOT remove other sites
# - Creates new config only for tatic domain
#

set -e

DOMAIN="tatic.jacare.cloud"
EMAIL="admin@jacare.cloud"
APP_PORT=8506

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  🔒 SAFE NGINX + SSL Setup - $DOMAIN ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Pre-flight checks
echo -e "${YELLOW}[1/5] Running pre-flight checks...${NC}"
echo ""

# Check if tatic app is running
echo -e "${BLUE}Checking if tatic app is running on port $APP_PORT...${NC}"
if curl -s http://localhost:$APP_PORT > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Tatic application is running${NC}"
else
    echo -e "${RED}✗ Tatic application is NOT running!${NC}"
    echo "  Please run deploy_safe.sh first"
    exit 1
fi
echo ""

# Check DNS
echo -e "${BLUE}Checking DNS for $DOMAIN...${NC}"
DNS_IP=$(dig +short $DOMAIN @8.8.8.8 2>/dev/null | tail -1)
if [ -z "$DNS_IP" ]; then
    echo -e "${RED}✗ DNS is not configured!${NC}"
    echo "  Please add DNS A record:"
    echo "    $DOMAIN → 147.79.82.234"
    echo "  Wait 15-30 minutes for propagation"
    echo "  Then retry this script"
    exit 1
elif [ "$DNS_IP" = "147.79.82.234" ]; then
    echo -e "${GREEN}✓ DNS is correctly configured: $DNS_IP${NC}"
else
    echo -e "${YELLOW}⚠️  DNS points to $DNS_IP (expected 147.79.82.234)${NC}"
    echo "  Check your DNS configuration"
    exit 1
fi
echo ""

# Check if Nginx exists
echo -e "${BLUE}Checking Nginx...${NC}"
if ! command -v nginx &> /dev/null; then
    echo -e "${YELLOW}Installing Nginx...${NC}"
    apt-get update
    apt-get install -y nginx
    systemctl enable nginx
    echo -e "${GREEN}✓ Nginx installed${NC}"
else
    echo -e "${GREEN}✓ Nginx is installed${NC}"
fi
echo ""

# Step 2: Backup existing config
echo -e "${YELLOW}[2/5] Backing up Nginx configuration...${NC}"
BACKUP_DIR="/root/backups/nginx-$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r /etc/nginx "$BACKUP_DIR/"
echo -e "${GREEN}✓ Backup: $BACKUP_DIR${NC}"
echo ""

# Step 3: Create Nginx config for tatic
echo -e "${YELLOW}[3/5] Creating Nginx configuration...${NC}"

mkdir -p /var/www/certbot

cat > /etc/nginx/sites-available/tatic.jacare.cloud << 'NGINX_CONFIG'
upstream streamlit_app {
    server localhost:8506;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name tatic.jacare.cloud;

    # Allow Let's Encrypt validation
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    # Redirect all HTTP to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS configuration
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name tatic.jacare.cloud;

    # SSL certificates (Let's Encrypt)
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
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Logging (check these if debugging)
    access_log /var/log/nginx/tatic.access.log;
    error_log /var/log/nginx/tatic.error.log;

    # Streamlit reverse proxy
    location / {
        proxy_pass http://streamlit_app;
        
        # Pass headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Streamlit specific (WebSocket support)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
NGINX_CONFIG

# Enable site
ln -sf /etc/nginx/sites-available/tatic.jacare.cloud /etc/nginx/sites-enabled/

# Test Nginx config
if nginx -t; then
    echo -e "${GREEN}✓ Nginx configuration is valid${NC}"
else
    echo -e "${RED}✗ Nginx configuration has errors!${NC}"
    echo "Restoring from backup..."
    rm -rf /etc/nginx
    cp -r "$BACKUP_DIR/nginx" /etc/nginx
    exit 1
fi
echo ""

# Step 4: Obtain SSL certificate
echo -e "${YELLOW}[4/5] Obtaining SSL certificate from Let's Encrypt...${NC}"

# Start Nginx to validate domain
systemctl restart nginx
sleep 2

if [ ! -f /etc/letsencrypt/live/tatic.jacare.cloud/fullchain.pem ]; then
    echo "Running Certbot..."
    certbot certonly \
        --nginx \
        --non-interactive \
        --agree-tos \
        --email "$EMAIL" \
        -d "$DOMAIN" 2>&1 | grep -E "^(Congratulations|ERROR)" || true
    
    if [ ! -f /etc/letsencrypt/live/tatic.jacare.cloud/fullchain.pem ]; then
        echo -e "${RED}✗ Certificate acquisition failed!${NC}"
        echo ""
        echo "This usually means:"
        echo "  1. DNS not fully propagated yet (wait 15-30 minutes)"
        echo "  2. DNS doesn't point to this server"
        echo "  3. Port 80 or 443 is blocked"
        echo ""
        echo "Verify with:"
        echo "  nslookup tatic.jacare.cloud"
        echo "  dig tatic.jacare.cloud"
        echo ""
        echo "Retry when DNS is ready:"
        echo "  ./scripts/execute_on_vps.sh scripts/nginx_setup_safe.sh"
        echo ""
        exit 1
    fi
else
    echo -e "${GREEN}✓ Certificate already exists${NC}"
fi

echo -e "${GREEN}✓ SSL certificate obtained${NC}"
echo ""

# Step 5: Final configuration
echo -e "${YELLOW}[5/5] Finalizing configuration...${NC}"

# Reload Nginx with SSL
systemctl restart nginx

# Verify it's working
if curl -s https://$DOMAIN -k > /dev/null 2>&1; then
    echo -e "${GREEN}✓ HTTPS is working${NC}"
else
    echo -e "${YELLOW}⚠️  HTTPS not responding yet (may take a moment)${NC}"
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ NGINX + SSL SETUP COMPLETE!                           ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${BLUE}Your application is now available at:${NC}"
echo -e "${YELLOW}https://tatic.jacare.cloud${NC}"
echo ""

echo -e "${BLUE}SSL Certificate Info:${NC}"
openssl x509 -in /etc/letsencrypt/live/tatic.jacare.cloud/fullchain.pem -text -noout | grep -A2 "Validity"
echo ""

echo -e "${BLUE}Configuration Backup:${NC}"
echo "  $BACKUP_DIR"
echo ""

echo -e "${BLUE}Useful Commands:${NC}"
echo "  # View Nginx logs"
echo "  tail -f /var/log/nginx/tatic.*.log"
echo ""
echo "  # Check SSL certificate"
echo "  certbot certificates"
echo ""
echo "  # Renew SSL (automatic in 30 days)"
echo "  certbot renew --dry-run"
echo ""
echo "  # Reload Nginx (if config changes)"
echo "  systemctl reload nginx"
echo ""

echo -e "${YELLOW}⚠️  SECURITY REMINDER:${NC}"
echo "  • SSL certificate auto-renews 30 days before expiry"
echo "  • Your other applications remain untouched"
echo "  • Port 8506 is used only by tatic (app runs in Docker)"
echo "  • Ports 80 and 443 are handled by Nginx (shared)"
echo ""
