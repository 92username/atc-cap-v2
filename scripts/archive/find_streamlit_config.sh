#!/bin/bash
#
# Fix Streamlit - Remover configuração de base_url para rodar em /
#

APP_DIR="/root/atc-cap-v2"
COMPOSE_FILE="$APP_DIR/docker-compose.yml"

echo "Verificando docker-compose.yml..."
echo ""

if [ ! -f "$COMPOSE_FILE" ]; then
    echo "✗ arquivo não encontrado: $COMPOSE_FILE"
    exit 1
fi

echo "Conteúdo atual:"
cat "$COMPOSE_FILE"
echo ""
echo "=========="
echo ""
echo "Procurando por STREAMLIT configurações:"
grep -i streamlit "$COMPOSE_FILE" || echo "(nenhuma encontrada)"
echo ""
echo "Procurando por base_url:"
grep -i base_url "$APP_DIR"/* 2>/dev/null | head -10
echo ""
echo "Verificar config Streamlit em .streamlit:"
ls -la "$APP_DIR/.streamlit/" 2>/dev/null || echo "Pasta não existe"
cat "$APP_DIR/.streamlit/config.toml" 2>/dev/null || echo "config.toml não encontrado"
