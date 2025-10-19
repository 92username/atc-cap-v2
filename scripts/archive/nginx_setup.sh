#!/bin/bash
#
# Nginx & SSL Setup for tatic.jacare.cloud
#
# Configures Nginx as reverse proxy with Let's Encrypt SSL
#

set -e

DOMAIN="tatic.jacare.cloud"
EMAIL="admin@jacare.cloud"

echo "=========================================="
echo "Setting up Nginx + SSL for $DOMAIN"
echo "=========================================="
echo ""

# Step 1: Install Nginx and Certbot
echo "[1/4] Installing Nginx and Certbot..."
apt-get update
apt-get install -y nginx certbot python3-certbot-nginx
systemctl enable nginx

# Step 2: Create Nginx config
echo "[2/4] Configuring Nginx..."
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

    # SSL certificates
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
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
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

# Test Nginx
nginx -t
echo "✓ Nginx configured"

# Step 3: Obtain SSL certificate
echo "[3/4] Obtaining SSL certificate..."
systemctl start nginx

certbot certonly \
    --nginx \
    --non-interactive \
    --agree-tos \
    --email "$EMAIL" \
    -d "$DOMAIN" || echo "Note: Certificate may already exist or DNS not configured yet"

# Step 4: Start Nginx with SSL
echo "[4/4] Starting Nginx..."
systemctl restart nginx

echo ""
echo "=========================================="
echo "✅ Nginx & SSL setup complete!"
echo "=========================================="
echo ""
echo "Next: Make sure DNS points to 147.79.82.234"
echo ""
echo "Check DNS with:"
echo "  nslookup tatic.jacare.cloud"
echo "  dig tatic.jacare.cloud"
echo ""
echo "Verify SSL:"
echo "  curl https://tatic.jacare.cloud"
echo "  openssl s_client -connect tatic.jacare.cloud:443"
echo ""
echo "View Nginx logs:"
echo "  tail -f /var/log/nginx/tatic.*.log"
echo ""
echo "SSL renewal:"
echo "  certbot renew --dry-run    # Test renewal"
echo "  certbot renew              # Actual renewal"
echo ""
