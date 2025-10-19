#!/bin/bash
echo "========== DEBUG: Verificando Streamlit =========="
echo ""
echo "1. Ver logs do container:"
docker logs --tail 30 tatic-processor | tail -20
echo ""
echo "2. Verificar se porta está aberta:"
netstat -tuln | grep 8506
echo ""
echo "3. Testar conectividade:"
curl -v http://127.0.0.1:8506 2>&1 | head -30
echo ""
echo "4. Ver headers da resposta:"
curl -i http://127.0.0.1:8506 2>&1 | head -20
