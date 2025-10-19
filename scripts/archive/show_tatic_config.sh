#!/bin/bash
echo "========== CONFIG TATIC COMPLETA =========="
cat /etc/nginx/sites-available/tatic.jacare.cloud
echo ""
echo "========== TESTE DIRETO DO STREAMLIT =========="
curl -s http://127.0.0.1:8506/tatic | head -10
