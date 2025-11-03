#!/bin/bash

# 🧪 Script de Teste - Simula Produção (GitHub Secrets)
# Este script testa se o app funciona com variáveis de ambiente

echo "════════════════════════════════════════════════════════════"
echo "🧪 TESTE: Simulando GitHub Secrets via Variáveis de Ambiente"
echo "════════════════════════════════════════════════════════════"
echo ""

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}CENÁRIO 1: Desenvolvimento Local (com .env)${NC}"
echo "────────────────────────────────────────────────────────────"
echo ""
echo "Executando app com .env local..."
echo ""

cat > /tmp/test_local.py << 'PYTHON_EOF'
import os
from pathlib import Path
from dotenv import load_dotenv

print("✅ Simulando: streamlit run app.py (com .env)")
print("")

env_path = Path("/home/nbx/Projects/jacare/atc-cap-v2/.env")
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)
    print(f"✅ Arquivo .env carregado de: {env_path}")
else:
    print(f"⚠️ Arquivo .env não encontrado")

admin = os.getenv("ADMIN_EMAILS", "")
allowed = os.getenv("ALLOWED_EMAILS", "")

print(f"ADMIN_EMAILS: '{admin}'")
print(f"ALLOWED_EMAILS: '{allowed}'")
print("")

authorized = [
    email.strip().lower() 
    for email in admin.split(",") + allowed.split(",") 
    if email.strip()
]

print(f"✅ Usuários autorizados ({len(authorized)}):")
for email in authorized:
    print(f"   • {email}")
PYTHON_EOF

python /tmp/test_local.py
echo ""

echo -e "${BLUE}CENÁRIO 2: Produção (GitHub Secrets via Docker)${NC}"
echo "────────────────────────────────────────────────────────────"
echo ""
echo "Simulando: docker run -e ADMIN_EMAILS=... -e ALLOWED_EMAILS=..."
echo ""

# Exportar como se viessem do Docker (GitHub Secrets)
export ADMIN_EMAILS="lvsr9663@gmail.com"
export ALLOWED_EMAILS="leandror1@gmail.com,octavioferreirinha@gmail.com,rochajacondino@gmail.com"

cat > /tmp/test_production.py << 'PYTHON_EOF'
import os
from pathlib import Path
from dotenv import load_dotenv

print("✅ Simulando: docker run com variáveis de ambiente (GitHub Secrets)")
print("")

# Nesta simulação, não existe .env no container
env_path = Path("/nonexistent/.env")
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)
    print(f"✅ Arquivo .env carregado")
else:
    print(f"⚠️ Arquivo .env não encontrado (esperado em produção)")
    print(f"   Usando variáveis de ambiente do sistema...")
    # Não fazer load_dotenv(), pois as variáveis já estão no sistema

admin = os.getenv("ADMIN_EMAILS", "")
allowed = os.getenv("ALLOWED_EMAILS", "")

print(f"")
print(f"ADMIN_EMAILS: '{admin}'")
print(f"ALLOWED_EMAILS: '{allowed}'")
print("")

authorized = [
    email.strip().lower() 
    for email in admin.split(",") + allowed.split(",") 
    if email.strip()
]

print(f"✅ Usuários autorizados ({len(authorized)}):")
for email in authorized:
    print(f"   • {email}")
PYTHON_EOF

python /tmp/test_production.py
echo ""

echo -e "${BLUE}CENÁRIO 3: Verificação no Docker Real${NC}"
echo "────────────────────────────────────────────────────────────"
echo ""

if command -v docker &> /dev/null; then
    if docker ps | grep -q "tatic-processor"; then
        echo "✅ Container 'tatic-processor' está rodando"
        echo ""
        echo "Variáveis de ambiente no container:"
        docker exec tatic-processor env | grep -i email || echo "   (nenhuma encontrada)"
    else
        echo "⚠️ Container 'tatic-processor' não está rodando"
        echo ""
        echo "Para verificar em produção:"
        echo "  ssh root@seu-vps-ip"
        echo "  docker exec tatic-processor env | grep -i email"
    fi
else
    echo "⚠️ Docker não está instalado localmente"
    echo ""
    echo "Para verificar em produção na VPS:"
    echo "  ssh root@seu-vps-ip"
    echo "  docker exec tatic-processor env | grep -i email"
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "📊 RESUMO"
echo "════════════════════════════════════════════════════════════"
echo ""
echo -e "${GREEN}✅ CENÁRIO 1 (Local):${NC}"
echo "   E-mails vêm de: .env (arquivo)"
echo ""
echo -e "${GREEN}✅ CENÁRIO 2 (Produção):${NC}"
echo "   E-mails vêm de: GitHub Secrets → Docker env vars"
echo ""
echo -e "${GREEN}✅ CENÁRIO 3 (Verificação Real):${NC}"
echo "   Verifique: docker exec tatic-processor env | grep -i email"
echo ""
echo "════════════════════════════════════════════════════════════"
