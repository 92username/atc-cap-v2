#!/bin/bash
#
# VPS Diagnostics - Check what's running
#
# Shows:
# - Docker containers and images
# - Running processes
# - Port usage
# - Nginx configuration
# - Disk space
#

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  VPS DIAGNOSTICS - What's Running?                        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🐳 DOCKER CONTAINERS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔌 PORT USAGE - What's listening?"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
netstat -tuln | grep LISTEN
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 NGINX CONFIGURATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if systemctl is-active --quiet nginx; then
    echo "✓ Nginx is running"
    echo ""
    echo "Enabled sites:"
    ls -la /etc/nginx/sites-enabled/ | grep -v "^total\|^d" | awk '{print $NF}'
else
    echo "✗ Nginx is not running"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📂 DIRECTORIES & SPACE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Disk space:"
df -h / | tail -1 | awk '{printf "  %-15s %8s %8s %8s %3s\n", $1, "Used", "Avail", "Total", "Use%"} NR==2 {printf "  %-15s %8s %8s %8s %3s\n", $1, $3, $4, $2, $5}'
echo ""

echo "Root directories:"
du -sh /root/* 2>/dev/null | sort -rh | head -10
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚙️  RUNNING PROCESSES (non-system)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ps aux | grep -E "docker|nginx|python|node|java" | grep -v grep
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔐 SSL CERTIFICATES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -d /etc/letsencrypt/live ]; then
    ls -1 /etc/letsencrypt/live/ | while read domain; do
        expiry=$(certbot certificates -d "$domain" 2>/dev/null | grep "Expiry" | tail -1 | sed 's/.*Expiry Date: //')
        if [ -z "$expiry" ]; then
            expiry="Unknown"
        fi
        printf "  %-30s %s\n" "$domain" "$expiry"
    done
else
    echo "  No SSL certificates found"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
CONTAINER_COUNT=$(docker ps | wc -l)
CONTAINER_COUNT=$((CONTAINER_COUNT - 1))
echo "Docker containers running: $CONTAINER_COUNT"
echo "Nginx status: $(systemctl is-active nginx)"
echo "System uptime: $(uptime -p)"
echo ""
