#!/bin/bash
#
# Final Fix: Nginx proxy para /tatic
#

set -e

echo "════════════════════════════════════════════════════════════════"
echo "🔧 FIX FINAL: Proxy correto para /tatic"
echo "════════════════════════════════════════════════════════════════"
echo ""

echo "1️⃣  Configurando proxy para /tatic..."

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

    # Root redirection
    location = / {
        return 301 https://$server_name/tatic;
    }

    # Proxy /tatic
    location /tatic {
        proxy_pass http://streamlit_app/tatic;
        
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }

    access_log /var/log/nginx/tatic.access.log;
    error_log /var/log/nginx/tatic.error.log;
}
NGINX_CONFIG

echo "✓ Config criada"
echo ""

echo "2️⃣  Testando..."
nginx -t
echo ""

echo "3️⃣  Recarregando..."
systemctl reload nginx
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "✅ CONFIGURADO!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Acesse:"
echo "  http://tatic.jacare.cloud/tatic"
echo ""
echo "Testando..."
sleep 2
RESPONSE=$(curl -s http://127.0.0.1/tatic -H "Host: tatic.jacare.cloud" | head -1)
echo "Resposta: $RESPONSE"
echo ""

if echo "$RESPONSE" | grep -q "html\|<!doctype\|<title>"; then
    echo "✓ APP RESPONDENDO CORRETAMENTE!"
else
    echo "⚠️  Verifique logs"
fi
echo ""
