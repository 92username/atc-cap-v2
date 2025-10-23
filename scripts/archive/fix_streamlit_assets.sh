#!/bin/bash
#
# Fix Tatic - Parar container e restartar SEM /tatic
#

APP_DIR="/root/atc-cap-v2"

echo "========== PARANDO CONTAINER =========="
echo ""
docker stop tatic-processor

echo ""
echo "========== REMOVENDO CONTAINER =========="
docker rm tatic-processor

echo ""
echo "========== INICIANDO NOVO CONTAINER =========="
docker run -d \
  --name tatic-processor \
  --restart unless-stopped \
  -p 8506:8506 \
  -v $APP_DIR/data/uploads:/data/uploads \
  -v $APP_DIR/outputs:/app/outputs \
  -e STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
  -e STREAMLIT_SERVER_ENABLECORS=false \
  -e STREAMLIT_SERVER_PORT=8506 \
  -e STREAMLIT_SERVER_HEADLESS=true \
  ghcr.io/92username/tatic-processor:10 \
  streamlit run app.py --server.port=8506 --server.address=0.0.0.0

echo "✓ Novo container iniciado"
echo ""
echo "Aguardando 5 segundos..."
sleep 5

echo ""
echo "========== TESTE =========="
curl -s http://127.0.0.1:8506 | head -10

echo ""
echo "✅ Pronto!"
echo ""
echo "Container agora rodando em / em vez de /tatic"
