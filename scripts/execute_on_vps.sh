#!/bin/bash
#
# Execute Remote Scripts on VPS via SSH
# 
# Usage: 
#   ./scripts/execute_on_vps.sh <script_path> [args...]
#   Example: ./scripts/execute_on_vps.sh scripts/deploy.sh arg1 arg2
#

set -e

# Configuration
VPS_HOST="147.79.82.234"
VPS_USER="root"
SSH_KEY="$HOME/.ssh/mcp_vps"
REMOTE_SCRIPTS_DIR="/root/atc-cap-v2/scripts"
LOCAL_SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$LOCAL_SCRIPTS_DIR")"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check arguments
if [ $# -lt 1 ]; then
    echo -e "${RED}Error: No script specified${NC}"
    echo "Usage: $0 <script_path> [args...]"
    echo ""
    echo "Examples:"
    echo "  $0 scripts/deploy.sh"
    echo "  $0 scripts/backup.sh --compress"
    exit 1
fi

SCRIPT_NAME="$1"
shift
SCRIPT_ARGS="$@"

# Validate script exists locally
if [ ! -f "$SCRIPT_NAME" ]; then
    echo -e "${RED}Error: Script not found: $SCRIPT_NAME${NC}"
    exit 1
fi

# Validate SSH key exists
if [ ! -f "$SSH_KEY" ]; then
    echo -e "${RED}Error: SSH key not found: $SSH_KEY${NC}"
    echo "Please ensure your SSH key is at $SSH_KEY"
    exit 1
fi

BASENAME=$(basename "$SCRIPT_NAME")

echo -e "${BLUE}=== Remote Script Execution ===${NC}"
echo -e "${YELLOW}Script:${NC} $SCRIPT_NAME"
echo -e "${YELLOW}Remote Host:${NC} $VPS_USER@$VPS_HOST"
echo -e "${YELLOW}Arguments:${NC} $SCRIPT_ARGS"
echo ""

# Step 1: Copy script to VPS
echo -e "${YELLOW}[1/3] Uploading script to VPS...${NC}"
scp -i "$SSH_KEY" -q "$SCRIPT_NAME" "$VPS_USER@$VPS_HOST:$REMOTE_SCRIPTS_DIR/$BASENAME"

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to upload script${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Script uploaded successfully${NC}"

# Step 2: Make script executable
echo -e "${YELLOW}[2/3] Making script executable...${NC}"
ssh -i "$SSH_KEY" -q "$VPS_USER@$VPS_HOST" "chmod +x $REMOTE_SCRIPTS_DIR/$BASENAME"

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to change permissions${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Permissions set${NC}"

# Step 3: Execute script
echo -e "${YELLOW}[3/3] Executing script on VPS...${NC}"
echo -e "${BLUE}----------------------------------------${NC}"

ssh -i "$SSH_KEY" "$VPS_USER@$VPS_HOST" "cd /root/atc-cap-v2 && $REMOTE_SCRIPTS_DIR/$BASENAME $SCRIPT_ARGS"
RESULT=$?

echo -e "${BLUE}----------------------------------------${NC}"

if [ $RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ Script executed successfully${NC}"
    exit 0
else
    echo -e "${RED}✗ Script execution failed (exit code: $RESULT)${NC}"
    exit $RESULT
fi
