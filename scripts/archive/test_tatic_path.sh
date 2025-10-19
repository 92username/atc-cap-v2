#!/bin/bash
echo "========== TESTE FINAL /tatic =========="
echo ""
echo "1. Teste GET /tatic:"
curl -s http://localhost/tatic | head -10
echo ""
echo "2. Verificar headers:"
curl -i http://localhost/tatic 2>&1 | head -15
echo ""
echo "3. Verificar config Nginx:"
grep -A5 "location /tatic" /etc/nginx/sites-available/tatic.jacare.cloud
