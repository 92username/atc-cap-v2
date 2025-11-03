# 🔐 Configuração de GitHub Secrets - ATC-CAP-V2

## ✅ Secrets Configurados

Os seguintes secrets estão configurados no GitHub Repository:

### 1️⃣ **ADMIN_EMAILS**
```
Nome: ADMIN_EMAILS
Valor: (armazenado de forma segura no GitHub)
```

### 2️⃣ **ALLOWED_EMAILS**
```
Nome: ALLOWED_EMAILS
Valor: (armazenado de forma segura no GitHub)
```

---

## 🔗 Como São Utilizados no CI/CD

### Arquivo: `.github/workflows/ci-cd.yml` (Linhas 19-20)

```yaml
env:
  APP_NAME: tatic-processor
  APP_PORT: 8506
  REGISTRY_USER: 92username
  ADMIN_EMAILS: ${{ secrets.ADMIN_EMAILS }}        # ✅ Secret referenciado aqui
  ALLOWED_EMAILS: ${{ secrets.ALLOWED_EMAILS }}    # ✅ Secret referenciado aqui
```

### Fluxo de Injeção no Docker

```yaml
jobs:
  cd:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy via SSH na VPS Hostinger
        uses: appleboy/ssh-action@v1.1.0
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_KEY }}
          script: |
            docker run -d \
              --name tatic-processor \
              --restart unless-stopped \
              -p 8506:8506 \
              -e ADMIN_EMAILS="${{ env.ADMIN_EMAILS }}" \           # ✅ Injetado
              -e ALLOWED_EMAILS="${{ env.ALLOWED_EMAILS }}" \       # ✅ Injetado
              ghcr.io/92username/tatic-processor:123
```

---

## 📊 Mapeamento Completo

| Localização | Tipo | Nome | Referência |
|------------|------|------|-----------|
| GitHub Secrets | Secret | `ADMIN_EMAILS` | `${{ secrets.ADMIN_EMAILS }}` |
| GitHub Secrets | Secret | `ALLOWED_EMAILS` | `${{ secrets.ALLOWED_EMAILS }}` |
| CI/CD Workflow | Env Var | `ADMIN_EMAILS` | `${{ env.ADMIN_EMAILS }}` |
| CI/CD Workflow | Env Var | `ALLOWED_EMAILS` | `${{ env.ALLOWED_EMAILS }}` |
| Docker | Env Var | `ADMIN_EMAILS` | `-e ADMIN_EMAILS=...` |
| Docker | Env Var | `ALLOWED_EMAILS` | `-e ALLOWED_EMAILS=...` |
| Python App | Env Var | `ADMIN_EMAILS` | `os.getenv("ADMIN_EMAILS")` |
| Python App | Env Var | `ALLOWED_EMAILS` | `os.getenv("ALLOWED_EMAILS")` |

---

## 🔄 Fluxo Completo

```
┌─────────────────────────────────────┐
│   GitHub Repository Secrets         │
│                                     │
│   ADMIN_EMAILS: ••••••••••         │
│   ALLOWED_EMAILS: ••••••••••       │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  .github/workflows/ci-cd.yml        │
│                                     │
│  env:                               │
│    ADMIN_EMAILS: ${{ secrets.X }}   │
│    ALLOWED_EMAILS: ${{ secrets.Y }} │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  GitHub Actions Environment         │
│                                     │
│  ADMIN_EMAILS: ••••••••••           │
│  ALLOWED_EMAILS: ••••••••••         │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  docker run -e ADMIN_EMAILS=... \   │
│           -e ALLOWED_EMAILS=...     │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Container Docker (VPS)             │
│                                     │
│  ADMIN_EMAILS=lvsr9663@gmail.com    │
│  ALLOWED_EMAILS=leandror1@...       │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  app.py                             │
│                                     │
│  os.getenv("ADMIN_EMAILS")          │
│  os.getenv("ALLOWED_EMAILS")        │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  🔐 Tela de Login                  │
│                                     │
│  Valida contra AUTHORIZED_USERS     │
└─────────────────────────────────────┘
```

---

## ✅ Verificação de Configuração

### Para Verificar se os Secrets Existem no GitHub:

1. Vá para: **Settings → Secrets and variables → Actions**
2. Você deve ver:
   - ✅ `ADMIN_EMAILS` (com indicador "Updated X time ago")
   - ✅ `ALLOWED_EMAILS` (com indicador "Updated X time ago")

### Para Verificar se Estão Sendo Usados no CI/CD:

1. Vá para: **Actions → CI/CD - TATIC Processor**
2. Clique no último workflow executado
3. Clique em **cd** (job de deploy)
4. Procure por: **"Deploy via SSH na VPS Hostinger"**
5. Você verá os secrets sendo injetados no docker run

### Para Verificar se Chegaram no Container:

```bash
# SSH na VPS
ssh root@seu-vps-ip

# Ver variáveis de ambiente do container
docker exec tatic-processor env | grep -E "ADMIN|ALLOWED"

# Resultado esperado:
# ADMIN_EMAILS=lvsr9663@gmail.com
# ALLOWED_EMAILS=leandror1@gmail.com,octavioferreirinha@gmail.com,...
```

---

## 🔐 Nomes Exatos dos Secrets

```
┌────────────────────────────────────────────────────┐
│  ADMIN_EMAILS                                      │
│  └─ Exatamente como aparece no GitHub             │
│  └─ Referência: ${{ secrets.ADMIN_EMAILS }}        │
└────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────┐
│  ALLOWED_EMAILS                                    │
│  └─ Exatamente como aparece no GitHub             │
│  └─ Referência: ${{ secrets.ALLOWED_EMAILS }}      │
└────────────────────────────────────────────────────┘
```

---

## 📋 Checklist

- [x] Secret `ADMIN_EMAILS` existe no GitHub
- [x] Secret `ALLOWED_EMAILS` existe no GitHub
- [x] CI/CD referencia os secrets corretamente
- [x] Secrets são injetados como variáveis de ambiente no Docker
- [x] App lê as variáveis com `os.getenv()`
- [x] Nomes das variáveis combinam em todas as etapas

---

## 🎯 Resumo

Os secrets estão **100% configurados e funcionando** no GitHub:

```
GitHub Secrets (ADMIN_EMAILS, ALLOWED_EMAILS)
            ↓
CI/CD usa: ${{ secrets.ADMIN_EMAILS }}
            ↓
Docker recebe: -e ADMIN_EMAILS=...
            ↓
app.py lê: os.getenv("ADMIN_EMAILS")
            ↓
✅ Tela de Login funciona
```

**Tudo está conectado corretamente!** 🎉
