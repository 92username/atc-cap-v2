#!/bin/bash
#
# Fix Tatic Nginx - Reroute to /tatic path
#

set -e

echo "════════════════════════════════════════════════════════════════"
echo "🔧 CORRIGINDO: Roteamento para /tatic path"
echo "════════════════════════════════════════════════════════════════"
echo ""

echo "1️⃣  Criando configuração corrigida..."

cat > /etc/nginx/sites-available/tatic.jacare.cloud << 'NGINX_CONFIG'
upstream streamlit_app {
    server 127.0.0.1:8506;
}

server {
    listen 80;
    listen [::]:80;
    server_name tatic.jacare.cloud;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        # Redirect all traffic to the /tatic path
        return 301 $scheme://$server_name/tatic;
    }

    access_log /var/log/nginx/tatic.access.log;
    error_log /var/log/nginx/tatic.error.log;
}
NGINX_CONFIG

echo "✓ Config criada"
echo ""

echo "2️⃣  Testando Nginx..."
if nginx -t 2>&1 | grep -q "successful"; then
    echo "✓ Sintaxe OK"
else
    echo "❌ Erro!"
    nginx -t
    exit 1
fi
echo ""

echo "3️⃣  Recarregando Nginx..."
systemctl reload nginx
echo "✓ Recarregado"
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "✅ CORRIGIDO!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Agora acesse:"
echo "  http://tatic.jacare.cloud"
echo ""
echo "Será redirecionado para:"
echo "  http://tatic.jacare.cloud/tatic"
echo ""
echo "Testando..."
sleep 2
curl -s http://127.0.0.1/tatic -H "Host: tatic.jacare.cloud" | head -10
echo ""
echo "[...output truncado...]"
