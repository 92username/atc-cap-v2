#!/bin/bash
#
# View Application Logs
#
# Shows Docker container logs with optional tail option
#

APP_DIR="/root/atc-cap-v2"
COMPOSE_FILE="$APP_DIR/docker-compose.yml"
LINES="${1:-100}"  # Default to last 100 lines, or use first argument

echo "Showing last $LINES lines of Docker logs..."
echo ""

cd "$APP_DIR"
docker-compose -f "$COMPOSE_FILE" logs --tail="$LINES" -f
