#!/bin/bash
#
# Application Status Check
#
# Shows status of Docker containers and disk usage
#

APP_DIR="/root/atc-cap-v2"

echo "========== Container Status =========="
docker-compose -f "$APP_DIR/docker-compose.yml" ps
echo ""

echo "========== Disk Usage =========="
du -sh "$APP_DIR/uploads" "$APP_DIR/outputs" "$APP_DIR/data" 2>/dev/null
echo ""

echo "========== Application Health =========="
if docker-compose -f "$APP_DIR/docker-compose.yml" ps | grep -q "Up"; then
    echo "✓ Application is running"
else
    echo "✗ Application is not running"
fi
