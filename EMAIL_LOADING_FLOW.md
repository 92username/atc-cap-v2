# 📊 Fluxo Completo de Carregamento de E-mails

## 🎯 Resumo Executivo

Os e-mails são armazenados em **GitHub Secrets** e injetados como **variáveis de ambiente** durante o deployment via CI/CD. O app busca nesta ordem:

1. **Arquivo `.env`** (desenvolvimento local)
2. **Variáveis de ambiente** (GitHub Secrets via Docker)

---

## 🔄 Fluxo Passo a Passo

### 📍 PASSO 1: GitHub Secrets
```
GitHub Repository
    ↓
Settings → Secrets and variables → Actions
    ↓
ADMIN_EMAILS = "lvsr9663@gmail.com"
ALLOWED_EMAILS = "leandror1@gmail.com,octavio..."
```

### 📍 PASSO 2: CI/CD Pipeline (`.github/workflows/ci-cd.yml`)
```yaml
env:
  APP_NAME: tatic-processor
  APP_PORT: 8506
  REGISTRY_USER: 92username
  ADMIN_EMAILS: ${{ secrets.ADMIN_EMAILS }}        # ✅ Secret injetado aqui
  ALLOWED_EMAILS: ${{ secrets.ALLOWED_EMAILS }}    # ✅ Secret injetado aqui
```

### 📍 PASSO 3: Docker Container
```bash
# GitHub Actions executa:
docker run \
  -e ADMIN_EMAILS="lvsr9663@gmail.com" \           # ✅ Vem do secret
  -e ALLOWED_EMAILS="leandro..." \                  # ✅ Vem do secret
  ghcr.io/.../tatic-processor:123
```

### 📍 PASSO 4: App Python (`app.py`)

```python
# 1. Tenta carregar .env (não vai encontrar em produção)
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)
    print("✅ Arquivo .env carregado")
else:
    print("⚠️ .env não encontrado, usando variáveis de ambiente")

# 2. Lê variáveis do container (GitHub Secrets)
ADMIN_EMAILS = os.getenv("ADMIN_EMAILS", "")          # ✅ Vem do Docker
ALLOWED_EMAILS = os.getenv("ALLOWED_EMAILS", "")      # ✅ Vem do Docker

# 3. Normaliza e cria lista autorizada
AUTHORIZED_USERS = [
    email.strip().lower() 
    for email in ADMIN_EMAILS.split(",") + ALLOWED_EMAILS.split(",") 
    if email.strip()
]
```

### 📍 PASSO 5: Tela de Login
```
┌─────────────────────────────────────┐
│   🔐 Acesso Restrito               │
├─────────────────────────────────────┤
│ Digite seu e-mail autorizado:      │
│ [lvsr9663@gmail.com           ]    │
│             [Entrar]               │
└─────────────────────────────────────┘
         ↓
    Email está em AUTHORIZED_USERS?
         ↓
    ✅ SIM → Acesso concedido
    ❌ NÃO → Acesso negado
```

---

## 🌍 Ambientes

### 📱 DESENVOLVIMENTO LOCAL

```
.env (arquivo local)
    ↓
load_dotenv()
    ↓
ADMIN_EMAILS = "seu-email@example.com"
ALLOWED_EMAILS = "user@example.com"
    ↓
streamlit run app.py
```

**Verificação:**
```bash
cat .env | grep -E "ADMIN|ALLOWED"
```

### 🚀 PRODUÇÃO (GitHub + VPS)

```
GitHub Secrets (repositório)
    ↓
.github/workflows/ci-cd.yml
    ↓
docker run -e ADMIN_EMAILS=${{ secrets.ADMIN_EMAILS }} ...
    ↓
Container no Docker
    ↓
app.py lê: os.getenv("ADMIN_EMAILS")
    ↓
Tela de login
```

**Verificação (na VPS):**
```bash
docker exec tatic-processor env | grep -i email
# Output: ADMIN_EMAILS=lvsr9663@gmail.com
# Output: ALLOWED_EMAILS=leandror1@gmail.com,octavio...
```

---

## 🔍 Debug: Onde os E-mails Estão?

### ✅ LOCAL (Desenvolvimento)

Os e-mails **DEVEM estar** no arquivo `.env`:

```bash
# Verificar se arquivo existe
ls -la .env

# Ver conteúdo
cat .env | grep -E "ADMIN|ALLOWED"

# Saída esperada:
# ADMIN_EMAILS=lvsr9663@gmail.com
# ALLOWED_EMAILS=leandror1@gmail.com,octavioferreirinha@gmail.com,...
```

### ✅ PRODUÇÃO (GitHub Secrets)

Os e-mails **DEVEM estar** configurados em:
`Settings → Secrets and variables → Actions`

```
Secret Name: ADMIN_EMAILS
Secret Value: lvsr9663@gmail.com

Secret Name: ALLOWED_EMAILS
Secret Value: leandror1@gmail.com,octavioferreirinha@gmail.com,...
```

**Verificação no Docker:**
```bash
# SSH na VPS
ssh root@seu-vps-ip

# Ver variáveis do container
docker exec tatic-processor env | grep -E "ADMIN|ALLOWED"

# Resultado esperado:
# ADMIN_EMAILS=lvsr9663@gmail.com
# ALLOWED_EMAILS=leandror1@gmail.com,octavioferreirinha@gmail.com,...
```

---

## 📋 Checklist de Verificação

### Para Desenvolvimento Local:

- [ ] Arquivo `.env` existe em `/home/nbx/Projects/jacare/atc-cap-v2/.env`
- [ ] Contém `ADMIN_EMAILS=lvsr9663@gmail.com`
- [ ] Contém `ALLOWED_EMAILS=leandror1@gmail.com,...`
- [ ] Sem espaços extras nas linhas
- [ ] Executar: `streamlit run app.py`
- [ ] Tela de login aparece com ✅
- [ ] Digita `lvsr9663@gmail.com` → Acesso concedido ✅

### Para Produção (GitHub Actions + VPS):

- [ ] GitHub Secrets `ADMIN_EMAILS` configurado
- [ ] GitHub Secrets `ALLOWED_EMAILS` configurado
- [ ] `.github/workflows/ci-cd.yml` tem as variáveis:
  ```yaml
  ADMIN_EMAILS: ${{ secrets.ADMIN_EMAILS }}
  ALLOWED_EMAILS: ${{ secrets.ALLOWED_EMAILS }}
  ```
- [ ] Push para `main` dispara GitHub Actions ✅
- [ ] Deploy bem-sucedido ✅
- [ ] VPS: `docker exec tatic-processor env | grep -i email` mostra valores ✅
- [ ] Acessa `http://vps-ip:8506` → Tela de login ✅
- [ ] Digita email autorizado → Acesso concedido ✅

---

## 🎯 Resumo Visual

```
                    DESENVOLVIMENTO LOCAL
                            ↓
                    ┌──────────────────┐
                    │    .env (arquivo)│
                    │ ADMIN_EMAILS=... │
                    │ ALLOWED_EMAILS...│
                    └────────┬─────────┘
                             ↓
                    streamlit run app.py
                             ↓
                    Tela de Login ✅


                    PRODUÇÃO (VPS)
                            ↓
                    ┌──────────────────────┐
                    │ GitHub Secrets       │
                    │ ADMIN_EMAILS         │
                    │ ALLOWED_EMAILS       │
                    └────────┬─────────────┘
                             ↓
                    .github/workflows/ci-cd.yml
                    env: ADMIN_EMAILS: ${{ secrets.ADMIN_EMAILS }}
                             ↓
                    docker run -e ADMIN_EMAILS=... 
                             ↓
                    Container Docker com variáveis injetadas
                             ↓
                    os.getenv("ADMIN_EMAILS")
                             ↓
                    Tela de Login ✅
```

---

## 🛠️ Solução de Problemas

### ❌ Problema: "Acesso negado" mesmo com e-mail correto

**Diagnóstico:**
```bash
# 1. Verificar se secrets estão no GitHub
# Settings → Secrets → Veja ADMIN_EMAILS e ALLOWED_EMAILS

# 2. Verificar se deploy foi bem-sucedido
# GitHub Actions → Veja se workflow passou

# 3. Ver variáveis no container
docker exec tatic-processor env | grep -i email

# 4. Ver logs do app
docker logs tatic-processor | head -20
```

**Solução:**
1. Verifique se os secrets existem no GitHub
2. Verifique se o deploy foi bem-sucedido
3. Reinicie o container: `docker restart tatic-processor`

### ❌ Problema: Variáveis não estão carregando em desenvolvimento local

**Diagnóstico:**
```bash
# 1. Verificar se .env existe
ls -la .env

# 2. Ver conteúdo
cat .env

# 3. Rodar debug script
python debug_emails_detailed.py
```

**Solução:**
```bash
# 1. Copiar exemplo
cp .env.example .env

# 2. Editar com seus e-mails
nano .env

# 3. Reiniciar app
streamlit run app.py
```

---

## 📞 Referências

- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions)
- [Python dotenv](https://github.com/theskumar/python-dotenv)
- [Streamlit Session State](https://docs.streamlit.io/library/api-reference/session-state)
