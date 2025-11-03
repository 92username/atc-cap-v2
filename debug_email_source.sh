#!/bin/bash

# 🔍 DEBUG SCRIPT - Rastreamento de Origem dos E-mails
# Este script mostra de onde o app está buscando os emails

echo "════════════════════════════════════════════════════════════"
echo "🔍 DEBUG: RASTREAMENTO DE ORIGEM DOS E-MAILS"
echo "════════════════════════════════════════════════════════════"
echo ""

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo "📍 LOCAL DE BUSCA DOS E-MAILS NO app.py"
echo "════════════════════════════════════════════════════════════"
echo ""

echo -e "${BLUE}1. Carregamento do .env${NC}"
echo "   Linha 13: load_dotenv()"
echo "   ↳ Busca arquivo .env na RAIZ do projeto"
echo ""

echo -e "${BLUE}2. Leitura de ADMIN_EMAILS${NC}"
echo "   Linha 16: ADMIN_EMAILS = os.getenv('ADMIN_EMAILS', '')"
echo "   ↳ Procura variável de ambiente ADMIN_EMAILS"
echo "   ↳ Se não encontrar, usa string vazia ''"
echo "   ↳ Split por vírgula: .split(',')"
echo ""

echo -e "${BLUE}3. Leitura de ALLOWED_EMAILS${NC}"
echo "   Linha 17: ALLOWED_EMAILS = os.getenv('ALLOWED_EMAILS', '')"
echo "   ↳ Procura variável de ambiente ALLOWED_EMAILS"
echo "   ↳ Se não encontrar, usa string vazia ''"
echo "   ↳ Split por vírgula: .split(',')"
echo ""

echo -e "${BLUE}4. Normalização dos E-mails${NC}"
echo "   Linhas 18-20: AUTHORIZED_USERS = ["
echo "       email.strip().lower()"
echo "       for email in ADMIN_EMAILS + ALLOWED_EMAILS"
echo "       if email.strip()"
echo "   ]"
echo "   ↳ Remove espaços em branco (strip)"
echo "   ↳ Converte para minúsculas (lower)"
echo "   ↳ Filtra strings vazias (if email.strip())"
echo ""

echo "════════════════════════════════════════════════════════════"
echo "🔎 VERIFICAÇÃO: DE ONDE OS E-MAILS VÊM?"
echo "════════════════════════════════════════════════════════════"
echo ""

echo "Os emails podem vir de 3 fontes (em ordem de prioridade):"
echo ""

echo -e "${GREEN}✅ FONTE 1: Variáveis de Ambiente do Sistema${NC}"
echo "   Definidas em:"
echo "   • .env (arquivo local na raiz)"
echo "   • GitHub Secrets (CI/CD)"
echo "   • Docker environment variables"
echo ""

if [ ! -f ".env" ]; then
    echo -e "${RED}❌${NC} Arquivo .env NÃO encontrado"
else
    echo -e "${GREEN}✅${NC} Arquivo .env encontrado"
    echo ""
    echo "Conteúdo do .env:"
    echo "───────────────────────────────────────────────────────────"
    cat .env 2>/dev/null | head -20
    echo "───────────────────────────────────────────────────────────"
fi

echo ""
echo -e "${GREEN}✅ FONTE 2: GitHub Secrets (quando via CI/CD)${NC}"
echo "   Em .github/workflows/ci-cd.yml:"
echo ""
grep -A 5 "env:" .github/workflows/ci-cd.yml | grep -E "ADMIN|ALLOWED" || echo "   (não encontrado)"

echo ""
echo -e "${GREEN}✅ FONTE 3: Docker Environment${NC}"
echo "   No Dockerfile ou docker-compose.yml:"
echo ""
grep -E "ADMIN_EMAILS|ALLOWED_EMAILS" docker-compose.yml Dockerfile 2>/dev/null || echo "   (não configurado)"

echo ""
echo "════════════════════════════════════════════════════════════"
echo "🧪 TESTE: VERIFICAR VALORES ATUAIS"
echo "════════════════════════════════════════════════════════════"
echo ""

cat > /tmp/test_emails.py << 'PYTHON_EOF'
import os
from dotenv import load_dotenv

# Carregar .env
load_dotenv()

# Ler variáveis
admin_emails_raw = os.getenv("ADMIN_EMAILS", "")
allowed_emails_raw = os.getenv("ALLOWED_EMAILS", "")

print("📊 VALORES BRUTOS (conforme obtidos):")
print(f"   ADMIN_EMAILS    = '{admin_emails_raw}'")
print(f"   ALLOWED_EMAILS  = '{allowed_emails_raw}'")
print("")

# Processar
admin_list = admin_emails_raw.split(",") if admin_emails_raw else []
allowed_list = allowed_emails_raw.split(",") if allowed_emails_raw else []

print("📊 APÓS SPLIT POR VÍRGULA:")
print(f"   ADMIN_EMAILS    = {admin_list}")
print(f"   ALLOWED_EMAILS  = {allowed_list}")
print("")

# Normalizar
authorized_users = [
    email.strip().lower() 
    for email in admin_list + allowed_list 
    if email.strip()
]

print("📊 APÓS NORMALIZAÇÃO (strip + lower + filter):")
print(f"   AUTHORIZED_USERS = {authorized_users}")
print(f"   Total de usuários autorizados: {len(authorized_users)}")
print("")

print("✅ Se vazio, significa que as variáveis não foram encontradas!")
PYTHON_EOF

python /tmp/test_emails.py

echo ""
echo "════════════════════════════════════════════════════════════"
echo "🛠️ COMO CORRIGIR (se vazio)"
echo "════════════════════════════════════════════════════════════"
echo ""

echo -e "${YELLOW}1. DESENVOLVIMENTO LOCAL:${NC}"
echo "   $ cp .env.example .env"
echo "   $ nano .env  # Edite e adicione seus e-mails"
echo "   $ streamlit run app.py"
echo ""

echo -e "${YELLOW}2. PRODUÇÃO (GitHub Actions):${NC}"
echo "   a) Vá para: Settings → Secrets and variables → Actions"
echo "   b) Clique 'New repository secret'"
echo "   c) Name: ADMIN_EMAILS"
echo "   d) Value: seu-email@example.com,outro@example.com"
echo "   e) Repita para ALLOWED_EMAILS"
echo "   f) Faça push para main"
echo ""

echo -e "${YELLOW}3. DOCKER:${NC}"
echo "   $ docker run -e ADMIN_EMAILS='user@example.com' app"
echo ""

echo "════════════════════════════════════════════════════════════"
echo "✨ Debug concluído!"
echo "════════════════════════════════════════════════════════════"
