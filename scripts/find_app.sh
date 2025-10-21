#!/bin/bash
#
# Find Application Directory
#
# Searches for docker-compose.yml and other key app files on VPS
#

echo "🔍 Procurando arquivos da aplicação na VPS..."
echo ""

echo "📂 Procurando docker-compose.yml..."
find / -name "docker-compose.yml" -type f 2>/dev/null | head -20

echo ""
echo "📂 Procurando diretórios com 'atc' ou 'tatic'..."
find / \( -name "*atc*" -o -name "*tatic*" \) -type d 2>/dev/null | head -20

echo ""
echo "📂 Procurando app.py (arquivo principal do Streamlit)..."
find / -name "app.py" -type f 2>/dev/null | head -20

echo ""
echo "📦 Verificando containers Docker..."
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "📂 Listando diretórios em /root..."
ls -la /root | grep -E "(atc|tatic|app|docker|project)"

echo ""
echo "📂 Listando diretórios em /home..."
ls -la /home 2>/dev/null | grep -E "(atc|tatic|app|project)"
