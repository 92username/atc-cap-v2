#!/bin/bash
#
# View Application Logs
#
# Shows Docker container logs with optional tail option
#

CONTAINER_NAME="tatic-processor"
LINES="${1:-100}"  # Default to last 100 lines, or use first argument

echo "Showing last $LINES lines of Docker container logs..."
echo ""

docker logs --tail="$LINES" -f "$CONTAINER_NAME"
