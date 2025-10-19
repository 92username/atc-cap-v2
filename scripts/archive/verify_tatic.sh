#!/bin/bash
echo "========== VERIFICAÇÃO FINAL =========="
echo ""
echo "1. Container tatic-processor:"
docker ps | grep tatic
echo ""
echo "2. Porta 8506 respondendo:"
curl -s http://localhost:8506 | head -3
echo ""
echo "3. Teste local do Nginx:"
curl -s http://localhost | head -5
echo ""
echo "4. Sites habilitados:"
ls -1 /etc/nginx/sites-enabled/ | grep tatic
echo ""
echo "5. Config do proxy:"
grep "proxy_pass" /etc/nginx/sites-available/tatic.jacare.cloud | head -1
