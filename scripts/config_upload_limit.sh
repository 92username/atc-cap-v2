#!/bin/bash
# Script para configurar limite de upload de arquivos
# Uso: ./execute_on_vps.sh config_upload_limit.sh [size_in_mb]
# Padrão: 200MB

UPLOAD_LIMIT=${1:-200}

echo "🔧 Configurando limite de upload para ${UPLOAD_LIMIT}MB..."
echo ""

# Backup da config Nginx atual
echo "💾 Fazendo backup da config Nginx..."
cp /etc/nginx/sites-available/tatic.jacare.cloud /etc/nginx/sites-available/tatic.jacare.cloud.bak.$(date +%s)

# Atualizar Nginx
echo "Atualizando Nginx..."
sed -i "s/client_max_body_size [0-9]*M;/client_max_body_size ${UPLOAD_LIMIT}M;/g" /etc/nginx/sites-available/tatic.jacare.cloud

# Verificar sintaxe
echo "Testando sintaxe Nginx..."
if nginx -t > /dev/null 2>&1; then
    echo "✅ Sintaxe OK"
    systemctl reload nginx
    echo "✅ Nginx recarregado"
else
    echo "❌ Erro na sintaxe Nginx!"
    exit 1
fi

echo ""
echo "Parando container Streamlit..."
docker stop tatic-processor

echo "Removendo container..."
docker rm tatic-processor

sleep 2

echo "Iniciando container com novo limite..."
docker run -d \
  --name tatic-processor \
  --restart unless-stopped \
  -p 8506:8506 \
  -v /root/atc-cap-v2/data/uploads:/data/uploads \
  -e STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
  -e STREAMLIT_SERVER_ENABLECORS=false \
  -e STREAMLIT_SERVER_PORT=8506 \
  -e STREAMLIT_SERVER_HEADLESS=true \
  -e OUTPUT_DIR=/data/uploads \
  -e STREAMLIT_SERVER_MAXUPLOADSIZE=${UPLOAD_LIMIT} \
  ghcr.io/92username/tatic-processor:10

sleep 3

echo "✅ Container iniciado"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Limite de upload configurado para ${UPLOAD_LIMIT}MB"
echo ""
echo "Verificando..."
grep -n "client_max_body_size" /etc/nginx/sites-available/tatic.jacare.cloud | head -3

echo ""
echo "✅ Pronto! Tatic aceita uploads até ${UPLOAD_LIMIT}MB"
