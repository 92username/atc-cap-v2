# 🔐 Guia de Autenticação - ATC-CAP-V2

## Visão Geral

O aplicativo agora utiliza autenticação via **whitelist de e-mails**. Apenas usuários com e-mails cadastrados conseguem acessar a aplicação.

## Configuração

### 1️⃣ **Variáveis de Ambiente Locais (Desenvolvimento)**

Crie um arquivo `.env` na raiz do projeto:

```bash
ADMIN_EMAILS=seu-email@example.com,outro-admin@example.com
ALLOWED_EMAILS=usuario1@example.com,usuario2@example.com
```

- **`ADMIN_EMAILS`**: E-mails de administradores (opcional, ainda não diferencia em lógica de negócio)
- **`ALLOWED_EMAILS`**: E-mails de usuários autorizados

> ⚠️ **Importante**: O arquivo `.env` está no `.gitignore` e nunca será commitado.

### 2️⃣ **Secrets do GitHub (Produção via CI/CD)**

Configure os secrets no repositório GitHub:

1. Vá para **Settings → Secrets and variables → Actions**
2. Crie dois novos secrets:

| Secret | Valor Exemplo | Descrição |
|--------|---------------|-----------|
| `ADMIN_EMAILS` | `admin@example.com,admin2@example.com` | E-mails separados por vírgula |
| `ALLOWED_EMAILS` | `user@example.com,user2@example.com` | E-mails separados por vírgula |

### 3️⃣ **Como Funciona**

1. Quando o app inicia, carrega as variáveis de ambiente
2. Combina `ADMIN_EMAILS` + `ALLOWED_EMAILS` em uma lista `AUTHORIZED_USERS`
3. Normaliza todos os e-mails para **minúsculas**
4. Exibe uma tela de login bloqueante
5. Usuário digita seu e-mail
6. Se o e-mail estiver na whitelist, acesso é concedido
7. A autenticação é armazenada em `st.session_state.authenticated`

## Fluxo de Autenticação

```
┌─────────────────────┐
│   App Iniciado      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────┐
│ Carregar .env e         │
│ AUTHORIZED_USERS        │
└──────────┬──────────────┘
           │
           ▼
┌──────────────────────────┐
│ Verificar               │
│ st.session_state        │
│ .authenticated?         │
└──┬──────────────────┬───┘
   │ NÃO              │ SIM
   ▼                  ▼
┌─────────────────┐ ┌──────────────┐
│ Tela de Login   │ │ App Normal   │
│ (st.stop())     │ │              │
└──────┬──────────┘ └──────────────┘
       │
       ▼
┌──────────────────────┐
│ E-mail na            │
│ AUTHORIZED_USERS?    │
└──┬─────────────┬─────┘
   │ NÃO         │ SIM
   ▼             ▼
┌────────────┐ ┌──────────────────┐
│ Erro ❌    │ │ Sucesso ✅       │
│            │ │ st.rerun()       │
└────────────┘ └──────────────────┘
               │
               ▼
         ┌──────────────┐
         │ App Normal   │
         └──────────────┘
```

## Exemplos de Uso

### Exemplo 1: Desenvolvimento Local

```bash
# 1. Crie o arquivo .env
echo "ADMIN_EMAILS=seu-email@airmail.com" > .env
echo "ALLOWED_EMAILS=colega@airmail.com" >> .env

# 2. Execute o app
streamlit run app.py

# 3. Digite seu e-mail na tela de login
```

### Exemplo 2: Deploy via GitHub Actions

Quando fizer push para `main`:

1. GitHub Actions usa os secrets `ADMIN_EMAILS` e `ALLOWED_EMAILS`
2. Injeta como variáveis de ambiente no container
3. O app automaticamente carrega do `os.getenv()`
4. Usuários se autenticam normalmente

## Troubleshooting

### ❓ **Estou digitando meu e-mail correto, mas recebo "Acesso negado"**

**Causas possíveis:**
- E-mail contém espaços extras
- Maiúsculas diferentes (e.g., `User@Example.com` vs `user@example.com`)
- Variáveis de ambiente não foram carregadas (verifique `.env` ou secrets do GitHub)

**Solução:**
```python
# Debug: adicione temporariamente no app.py
st.write(f"Debug - AUTHORIZED_USERS: {AUTHORIZED_USERS}")
```

### ❓ **Vejo "E-mail não autorizado" mesmo com e-mail correto no .env**

**Verificar:**
1. Arquivo `.env` existe na raiz do projeto?
2. Formatação está correta? `email@example.com,outro@example.com` (sem espaços)
3. Rodou `load_dotenv()`? (automático no app.py)

### ❓ **Como adicionar/remover usuários?**

**Localmente:**
- Edite `.env` e reinicie o app (`Ctrl+C` + `streamlit run app.py`)

**Em Produção (GitHub Actions):**
- Vá a **Settings → Secrets and variables → Actions**
- Clique em editar `ADMIN_EMAILS` ou `ALLOWED_EMAILS`
- Faça um novo push para `main`
- GitHub Actions fará o deploy automático

## Segurança

✅ **Boas práticas implementadas:**
- `.env` está em `.gitignore` (nunca commitado)
- E-mails normalizados para minúsculas (evita duplicatas)
- Espaços em branco removidos
- Validação de lista não vazia (filtra strings vazias)

⚠️ **Limitações atuais:**
- Sem criptografia de senha
- Sem expiração de sessão
- Sem 2FA (autenticação de dois fatores)
- Sem auditoria de login

🔒 **Melhorias futuras sugeridas:**
- Integração com OAuth2/OIDC (Google, GitHub)
- Auditoria de logs de acesso
- Rate limiting de tentativas de login
- Expiração de sessão por inatividade

## Referências

- [Streamlit Session State](https://docs.streamlit.io/library/api-reference/session-state)
- [Python-dotenv Documentation](https://github.com/theskumar/python-dotenv)
- [GitHub Secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions)
