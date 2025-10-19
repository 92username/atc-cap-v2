#!/bin/bash
#
# Find Tatic Container Location
#

echo "Procurando container tatic-processor..."
echo ""

# Get container ID
CONTAINER_ID=$(docker ps | grep tatic-processor | awk '{print $1}')

if [ -z "$CONTAINER_ID" ]; then
    echo "❌ Container não encontrado!"
    exit 1
fi

echo "Container ID: $CONTAINER_ID"
echo ""

echo "Informações do container:"
docker inspect $CONTAINER_ID | grep -E "Image|WorkingDir|Command" | head -10
echo ""

echo "Logs do container (últimas 30 linhas):"
docker logs --tail 30 $CONTAINER_ID
echo ""

echo "Arquivos no container (/app):"
docker exec $CONTAINER_ID ls -la /app/ | head -20
