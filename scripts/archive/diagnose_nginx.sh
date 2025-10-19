#!/bin/bash
#
# Diagnóstico de Nginx - Verificar roteamento tatic.jacare.cloud
#

echo "════════════════════════════════════════════════════════════════"
echo "🔍 DIAGNÓSTICO: Roteamento tatic.jacare.cloud"
echo "════════════════════════════════════════════════════════════════"
echo ""

echo "1️⃣  Sites habilitados no Nginx:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ls -1 /etc/nginx/sites-enabled/ | sed 's/^/   /'
echo ""

echo "2️⃣  Configuração de tatic.jacare.cloud:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f /etc/nginx/sites-enabled/tatic.jacare.cloud ]; then
    head -30 /etc/nginx/sites-enabled/tatic.jacare.cloud
else
    echo "❌ Arquivo não encontrado!"
    echo "Procurando em sites-available:"
    ls -la /etc/nginx/sites-available/ | grep tatic
fi
echo ""

echo "3️⃣  Teste de sintaxe Nginx:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
nginx -t
echo ""

echo "4️⃣  Qual container está respondendo em 8506:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
curl -s http://localhost:8506 | head -10
echo ""
echo "[...output truncado...]"
echo ""

echo "5️⃣  Logs de erro Nginx:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
tail -20 /var/log/nginx/tatic.error.log 2>/dev/null || echo "Sem logs recentes"
echo ""

echo "6️⃣  Verificar se está direcionando para porta errada:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Procurando 'upstream' no arquivo tatic:"
grep -n "upstream\|proxy_pass" /etc/nginx/sites-available/tatic.jacare.cloud 2>/dev/null || echo "Não encontrado"
echo ""

echo "7️⃣  Todos os upstreams definidos:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
grep -r "upstream\|proxy_pass" /etc/nginx/sites-available/ | grep -v "^#" | head -20
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "✅ Diagnóstico completo acima"
echo "════════════════════════════════════════════════════════════════"
