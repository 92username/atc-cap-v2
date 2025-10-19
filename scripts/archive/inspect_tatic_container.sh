#!/bin/bash
echo "========== INSPECIONAR CONTAINER =========="
echo ""
echo "1. Detalhes do container:"
docker inspect tatic-processor | grep -E "Cmd|Args|Env|Image" | head -30
echo ""
echo "2. Full command do container:"
docker inspect -f '{{.Config.Cmd}}' tatic-processor
echo ""
echo "3. Entrypoint:"
docker inspect -f '{{.Config.Entrypoint}}' tatic-processor
echo ""
echo "4. Variáveis de ambiente:"
docker exec tatic-processor env | grep -i streamlit
echo ""
echo "5. Verificar se há arquivo .streamlit dentro do container:"
docker exec tatic-processor ls -la /.streamlit/ 2>/dev/null || docker exec tatic-processor ls -la /app/.streamlit/ 2>/dev/null || echo "Nenhuma config encontrada"
