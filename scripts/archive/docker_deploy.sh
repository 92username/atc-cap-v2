#!/bin/bash
#
# Production Deploy - Step by Step
#
# This is a simplified version to be run on the VPS
# Assumes Docker and Docker Compose are already installed
#

set -e

DOMAIN="tatic.jacare.cloud"
APP_PORT=8506
APP_DIR="/root/atc-cap-v2"
EMAIL="admin@jacare.cloud"

echo "=========================================="
echo "Deploying ATC-CAP-V2 to $DOMAIN"
echo "=========================================="
echo ""

# Step 1: Ensure directories exist
echo "[1/5] Creating necessary directories..."
mkdir -p /var/www/certbot
chmod 755 /var/www/certbot

# Step 2: Create .env file
echo "[2/5] Creating .env file..."
cat > $APP_DIR/.env << 'EOF'
APP_NAME=tatic-processor
APP_PORT=8506
APP_ENV=production
APP_DEBUG=false
STREAMLIT_SERVER_PORT=8506
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
EOF
echo "✓ .env created"

# Step 3: Build and start Docker
echo "[3/5] Building and starting Docker containers..."
cd $APP_DIR
docker-compose build --no-cache
docker-compose up -d
echo "✓ Docker containers started"

# Step 4: Wait for app to be ready
echo "[4/5] Waiting for application to start..."
sleep 10

# Step 5: Verify application is running
echo "[5/5] Verifying application..."
if curl -s http://localhost:8506 > /dev/null; then
    echo "✓ Application is running and responding"
else
    echo "✗ Warning: Application may not be responding yet"
fi

echo ""
echo "=========================================="
echo "✅ Docker deployment complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Configure Nginx (run nginx_setup.sh)"
echo "2. Point DNS records to 147.79.82.234"
echo "3. Access: https://tatic.jacare.cloud"
echo ""
echo "Commands:"
echo "  docker-compose ps          # Check containers"
echo "  docker-compose logs -f     # View logs"
echo "  docker-compose restart     # Restart app"
echo ""
