#!/bin/sh
# start.sh - Script de inicialização para container Docker do aplicativo TATIC

# Configuração de ambiente
echo "Iniciando serviços do ATC-CAP-V2..."

# Garantir que os diretórios necessários existam
mkdir -p /app/uploads
mkdir -p /app/outputs
chmod 777 /app/uploads
chmod 777 /app/outputs

# Iniciar o serviço Nginx em background
echo "Iniciando Nginx..."
nginx -g "daemon off;" &

# Iniciar o backend Python em background
echo "Iniciando backend Python..."
cd /app && python3 app.py &

# Manter o container em execução
echo "Todos os serviços iniciados!"
tail -f /dev/null