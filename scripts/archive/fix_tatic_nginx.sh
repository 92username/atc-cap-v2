#!/bin/bash
#
# Fix Tatic Nginx Configuration (WITH SSL CHECK)
#
# Remove all backups and configure tatic.jacare.cloud corretamente
#

set -e

echo "════════════════════════════════════════════════════════════════"
echo "🔧 CORRIGINDO: Configuração de tatic.jacare.cloud"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Step 1: Remover arquivos de backup confusos
echo "1️⃣  Limpando arquivos de backup antigos..."
rm -f /etc/nginx/sites-available/jacare.cloud.*.bak
echo "✓ Arquivos de backup removidos"
echo ""

# Step 2: Verificar certificado SSL
echo "2️⃣  Verificando certificado SSL..."
SSL_CERT="/etc/letsencrypt/live/tatic.jacare.cloud/fullchain.pem"
SSL_KEY="/etc/letsencrypt/live/tatic.jacare.cloud/privkey.pem"

if [ ! -f "$SSL_CERT" ] || [ ! -f "$SSL_KEY" ]; then
    echo "⚠️  Certificado SSL NÃO encontrado!"
    echo ""
    echo "Opções:"
    echo "  A) Usar config com placeholder (vai dar erro até gerar cert)"
    echo "  B) Gerar certificado agora"
    echo ""
    echo "Usando: Versão com HTTP temporário (será atualizado)"
    USE_TEMP_CONFIG=true
else
    echo "✓ Certificado encontrado"
    USE_TEMP_CONFIG=false
fi
echo ""

# Step 3: Criar arquivo tatic.jacare.cloud (temporário ou definitivo)
echo "3️⃣  Criando configuração Nginx..."

if [ "$USE_TEMP_CONFIG" = true ]; then
    # Versão SEM SSL (temporária)
    cat > /etc/nginx/sites-available/tatic.jacare.cloud << 'NGINX_CONFIG_TEMP'
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
        proxy_pass http://streamlit_app;
        
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
NGINX_CONFIG_TEMP
    echo "✓ Config HTTP criada (temporária)"
else
    # Versão COM SSL (definitiva)
    cat > /etc/nginx/sites-available/tatic.jacare.cloud << 'NGINX_CONFIG'
upstream streamlit_app {
    server 127.0.0.1:8506;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name tatic.jacare.cloud;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS configuration
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name tatic.jacare.cloud;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/tatic.jacare.cloud/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tatic.jacare.cloud/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/tatic.access.log;
    error_log /var/log/nginx/tatic.error.log;

    # Proxy to Streamlit on port 8506
    location / {
        proxy_pass http://streamlit_app;
        
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
NGINX_CONFIG
    echo "✓ Config HTTPS criada (com SSL)"
fi
echo ""

# Step 4: Verificar/criar symlink
echo "4️⃣  Configurando sites-enabled..."
if [ ! -L /etc/nginx/sites-enabled/tatic.jacare.cloud ]; then
    ln -sf /etc/nginx/sites-available/tatic.jacare.cloud /etc/nginx/sites-enabled/
    echo "✓ Symlink criado"
else
    echo "✓ Symlink já existe"
fi
echo ""

# Step 5: Teste Nginx
echo "5️⃣  Testando configuração Nginx..."
if nginx -t 2>&1 | grep -q "successful"; then
    echo "✓ Sintaxe OK"
else
    echo "❌ Erro na sintaxe!"
    nginx -t
    exit 1
fi
echo ""

# Step 6: Reload Nginx
echo "6️⃣  Recarregando Nginx..."
systemctl reload nginx
echo "✓ Nginx recarregado"
echo ""

# Step 7: Teste de resposta
echo "7️⃣  Testando resposta..."
sleep 2
if curl -s http://127.0.0.1:8506 | head -1 | grep -q "html\|streamlit\|GET"; then
    echo "✓ Aplicação tatic respondendo"
else
    echo "⚠️  Resposta inesperada da app"
fi
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "✅ CONFIGURAÇÃO APLICADA!"
echo "════════════════════════════════════════════════════════════════"
echo ""

if [ "$USE_TEMP_CONFIG" = true ]; then
    echo "📢 PRÓXIMO PASSO:"
    echo "   Certificado SSL ainda não está gerado."
    echo "   Execute para gerar SSL:"
    echo ""
    echo "   /root/atc-cap-v2/scripts/nginx_setup_safe.sh"
    echo ""
else
    echo "✨ Seu site está correto em:"
    echo "   https://tatic.jacare.cloud"
    echo ""
    echo "Verificar com:"
    echo "   curl -I https://tatic.jacare.cloud"
fi
echo ""
