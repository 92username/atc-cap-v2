#!/bin/bash
#
# Setup VPS for Remote Script Execution
#
# Run this once on the VPS to create necessary directories
#

VPS_HOST="147.79.82.234"
SSH_KEY="$HOME/.ssh/mcp_vps"

echo "Setting up VPS for remote script execution..."
echo ""

ssh -i "$SSH_KEY" root@$VPS_HOST << 'EOF'
    echo "[1/3] Creating scripts directory..."
    mkdir -p /root/atc-cap-v2/scripts
    
    echo "[2/3] Setting permissions..."
    chmod 755 /root/atc-cap-v2/scripts
    
    echo "[3/3] Verifying setup..."
    ls -la /root/atc-cap-v2/scripts
    
    echo ""
    echo "✓ VPS setup completed!"
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "Setup successful! You can now run remote scripts."
else
    echo ""
    echo "Setup failed. Check SSH connection."
    exit 1
fi
