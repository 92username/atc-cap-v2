#!/bin/bash
#
# Deploy Application
#
# Pulls latest code and rebuilds Docker images on VPS
#

APP_DIR="/root/atc-cap-v2"

echo "Starting deployment..."
echo ""

cd "$APP_DIR"

echo "Step 1: Pulling latest code..."
git pull origin main

echo ""
echo "Step 2: Building Docker images..."
docker-compose build --no-cache

echo ""
echo "Step 3: Restarting containers..."
docker-compose down
docker-compose up -d

echo ""
echo "Deployment completed!"
docker-compose ps
