#!/bin/bash
#
# Test Tatic Nginx Access
#

echo "════════════════════════════════════════════════════════════════"
echo "🧪 TESTE: Acessando tatic.jacare.cloud"
echo "════════════════════════════════════════════════════════════════"
echo ""

echo "Teste 1: HTTP direto (localhost:8506)"
curl -s http://127.0.0.1:8506 | head -15
echo ""
echo "[...output truncado...]"
echo ""

echo "Teste 2: HTTP via Nginx (localhost)"
curl -s http://localhost -H "Host: tatic.jacare.cloud" | head -10
echo ""
echo "[...output truncado...]"
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "✅ Testes completos"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Se vir conteúdo Streamlit acima, significa:"
echo "✓ App tatic está rodando"
echo "✓ Nginx está direcionando corretamente"
echo ""
echo "Próximo: Gerar certificado SSL"
echo "Execute: nginx_setup_safe.sh"
echo ""
