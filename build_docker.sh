#!/bin/bash

# Script para testar o build do Docker

echo "🔵 Iniciando build da imagem Docker atc-cap-v2:0.0.1..."
docker build -t atc-cap-v2:0.0.1 .

if [ $? -eq 0 ]; then
    echo "✅ Build concluído com sucesso!"
    echo ""
    echo "🚀 Para executar a aplicação:"
    echo "docker run -p 8501:8501 atc-cap-v2:0.0.1"
    echo ""
    echo "🌐 Acesse: http://localhost:8501 quando o container estiver em execução"
else
    echo "❌ Build falhou. Verifique os erros acima."
fi