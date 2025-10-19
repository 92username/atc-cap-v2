#!/bin/bash
#
# Fix Tatic - Adicionar proxy também na porta 80 (HTTP)

echo "Corrigindo configuração HTTP..."

cp /etc/nginx/sites-available/tatic.jacare.cloud /etc/nginx/sites-available/tatic.jacare.cloud.bak.$(date +%s)

cat > /etc/nginx/sites-available/tatic.jacare.cloud << 'NGINX_CONFIG'
upstream streamlit_app {
    server 127.0.0.1:8506;
}

# HTTP Server
server {
    listen 80;
    listen [::]:80;
    server_name tatic.jacare.cloud;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    # Proxy para /tatic (Streamlit)
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

    # Static assets
    location /_stcore {
        proxy_pass http://streamlit_app/_stcore;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /_ws {
        proxy_pass http://streamlit_app/_ws;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
    }

    # Root redirect para /tatic
    location = / {
        return 301 $scheme://$server_name/tatic;
    }

    access_log /var/log/nginx/tatic.access.log;
    error_log /var/log/nginx/tatic.error.log;
}
NGINX_CONFIG

echo "✓ Config atualizada"
echo ""
nginx -t

if [ $? -eq 0 ]; then
    echo "✓ Sintaxe OK"
    systemctl reload nginx
    echo "✓ Nginx recarregado"
    echo ""
    echo "Testando /tatic:"
    sleep 1
    curl -s http://127.0.0.1/tatic 2>&1 | head -8
    echo ""
    echo "✅ Pronto!"
else
    echo "✗ Erro! Revertendo..."
    cp /etc/nginx/sites-available/tatic.jacare.cloud.bak /etc/nginx/sites-available/tatic.jacare.cloud
    systemctl reload nginx
    exit 1
fi
