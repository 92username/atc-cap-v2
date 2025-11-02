#!/bin/bash
# 📋 Checklist de Implementação - Autenticação
# Copie este arquivo para verificar o progresso

echo "════════════════════════════════════════════════════════════"
echo "✅ CHECKLIST - AUTENTICAÇÃO VIA WHITELIST DE E-MAILS"
echo "════════════════════════════════════════════════════════════"
echo ""

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Funções
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅${NC} Arquivo existe: $1"
    else
        echo -e "${RED}❌${NC} Arquivo não existe: $1"
    fi
}

check_content() {
    if grep -q "$2" "$1" 2>/dev/null; then
        echo -e "${GREEN}✅${NC} Conteúdo encontrado em $1: '$2'"
    else
        echo -e "${RED}❌${NC} Conteúdo NÃO encontrado em $1: '$2'"
    fi
}

# Checklist
echo "📝 VERIFICAÇÃO DE ARQUIVOS"
echo "════════════════════════════════════════════════════════════"
echo ""

check_file "app.py"
check_file ".env.example"
check_file ".github/workflows/ci-cd.yml"
check_file "requirements.txt"
check_file ".gitignore"
check_file "AUTHENTICATION.md"
check_file "IMPLEMENTATION_SUMMARY.md"
check_file "GITHUB_SECRETS_SETUP.md"
check_file "tests/test_authentication.py"

echo ""
echo "🔍 VERIFICAÇÃO DE CONTEÚDO"
echo "════════════════════════════════════════════════════════════"
echo ""

check_content "app.py" "from dotenv import load_dotenv"
check_content "app.py" "load_dotenv()"
check_content "app.py" "ADMIN_EMAILS = os.getenv"
check_content "app.py" "AUTHORIZED_USERS"
check_content "app.py" "st.session_state.authenticated"
check_content "app.py" "st.title(\"🔐 Acesso Restrito\")"
check_content "app.py" "st.stop()"

check_content ".github/workflows/ci-cd.yml" "ADMIN_EMAILS: \${{ secrets.ADMIN_EMAILS }}"
check_content ".github/workflows/ci-cd.yml" "ALLOWED_EMAILS: \${{ secrets.ALLOWED_EMAILS }}"

check_content ".env.example" "ADMIN_EMAILS"
check_content ".env.example" "ALLOWED_EMAILS"

check_content "requirements.txt" "python-dotenv"

check_content ".gitignore" ".env"

echo ""
echo "🧪 TESTES"
echo "════════════════════════════════════════════════════════════"
echo ""

if command -v pytest &> /dev/null; then
    echo -e "${GREEN}✅${NC} pytest disponível"
    echo ""
    echo "Executando testes de autenticação..."
    python -m pytest tests/test_authentication.py -v
else
    echo -e "${YELLOW}⚠️${NC} pytest não está instalado"
    echo "   Instalando: pip install pytest"
    pip install pytest > /dev/null 2>&1
    python -m pytest tests/test_authentication.py -v
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "✅ PRÓXIMOS PASSOS"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "1️⃣  DESENVOLVIMENTO LOCAL:"
echo "   $ cp .env.example .env"
echo "   $ nano .env  # Edite com seus e-mails"
echo "   $ streamlit run app.py"
echo ""
echo "2️⃣  PRODUÇÃO (GitHub Secrets):"
echo "   - Vá para Settings → Secrets and variables → Actions"
echo "   - Crie: ADMIN_EMAILS (com seus e-mails)"
echo "   - Crie: ALLOWED_EMAILS (com e-mails de usuários)"
echo ""
echo "3️⃣  DEPLOY:"
echo "   $ git add ."
echo "   $ git commit -m 'feat: add email whitelist authentication'"
echo "   $ git push origin main"
echo ""
echo "4️⃣  VERIFICAR:"
echo "   - Acesse: http://seu-vps-ip:8506"
echo "   - Digite um e-mail autorizado"
echo "   - Clique em 'Entrar'"
echo ""
echo "════════════════════════════════════════════════════════════"
echo "📖 DOCUMENTAÇÃO"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Leia os arquivos de documentação:"
echo "  • AUTHENTICATION.md          - Guia completo de uso"
echo "  • GITHUB_SECRETS_SETUP.md    - Como configurar secrets"
echo "  • IMPLEMENTATION_SUMMARY.md  - Resumo de alterações"
echo ""
echo "════════════════════════════════════════════════════════════"
echo "✨ Autenticação implementada com sucesso!"
echo "════════════════════════════════════════════════════════════"
