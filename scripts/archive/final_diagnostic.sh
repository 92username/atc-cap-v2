#!/bin/bash
#
# Final Diagnostic
#

echo "════════════════════════════════════════════════════════════════"
echo "📊 DIAGNÓSTICO FINAL"
echo "════════════════════════════════════════════════════════════════"
echo ""

echo "1. Resposta direta da app (localhost:8506/tatic):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
curl -s http://127.0.0.1:8506/tatic -I
echo ""

echo "2. Resposta via Nginx (localhost/tatic com header Host):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
curl -s http://127.0.0.1/tatic -H "Host: tatic.jacare.cloud" -I
echo ""

echo "3. Teste com curl verbose:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
curl -v http://127.0.0.1/tatic -H "Host: tatic.jacare.cloud" 2>&1 | head -30
echo ""

echo "4. Configuração Nginx atual:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat /etc/nginx/sites-enabled/tatic.jacare.cloud | head -30
echo ""

echo "5. Logs do Nginx (últimas 20 linhas):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
tail -20 /var/log/nginx/tatic.error.log
echo ""
