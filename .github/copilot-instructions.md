# 🧠 COPILOT INSTRUCTIONS — Implementação de OAuth (Google + Microsoft)
**Projeto:** ATC-CAP-V2  
**Branch:** feat/oauth  
**Objetivo:** Adicionar autenticação OAuth 2.0 via Google e Microsoft (Outlook), com PKCE, controle de acesso por whitelist e papéis (roles).

---

## 🎯 Objetivos técnicos
- Adicionar login via **Google** e **Microsoft**.
- Utilizar **Authlib** com PKCE (sem servidor adicional).
- Armazenar sessão em `st.session_state`.
- Controlar acesso via whitelist e papéis (`usuario`, `supervisor`, `dev`).
- Proteger app principal de alterações (branch isolada).
- Suporte a **ambientes local e produção (prefixo /tatic ou subdomínio)**.

---

## ⚙️ Passos para o Copilot

### 1️⃣ Dependências
Adicionar a dependência:
```bash
authlib>=1.3
````

ao arquivo `requirements.txt`.

---

### 2️⃣ Estrutura de diretórios

Criar:

```
app/
  auth/
    __init__.py
    oauth.py
```

---

### 3️⃣ Código principal — `app/auth/oauth.py`

Implementar o módulo completo conforme especificação:

* Configurar `GOOGLE_AUTH` e `MS_AUTH` (authorize_url, token_url, userinfo_url, scope).
* Implementar funções:

  * `build_auth_url(provider: str)`
  * `handle_auth_callback()`
  * `is_authenticated()`
  * `current_user()`
  * `logout()`
* Implementar PKCE (code verifier/challenge), validação de state e token exchange.
* Buscar dados do usuário (`email`, `name`).
* Validar se o e-mail está na whitelist.
* Definir role:

  * `dev` → `ADMIN_EMAILS`
  * `supervisor` → `SUPERVISOR_EMAILS`
  * `usuario` → default.

---

### 4️⃣ Integração no `app.py`

Editar o topo do `app.py`:

```python
from app.auth.oauth import build_auth_url, handle_auth_callback, is_authenticated, current_user, logout
```

Logo após `st.set_page_config(...)`, inserir:

```python
handle_auth_callback()
```

Substituir o trecho inicial da UI por:

```python
if not is_authenticated():
    st.info("Faça login para continuar.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Entrar com Google"):
            st.link_button("Continue", build_auth_url("google"))
    with col2:
        if st.button("Entrar com Microsoft"):
            st.link_button("Continue", build_auth_url("microsoft"))
    st.stop()
```

Abaixo disso, inserir:

```python
user = current_user()
st.success(f"Bem-vindo, {user['name']} ({user['email']}) — role: {user['role']}")
if st.button("Sair"):
    logout()
    st.rerun()
```

---

### 5️⃣ Variáveis de ambiente

Usar variáveis armazenadas no GitHub Secrets:

```
GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET
MS_CLIENT_ID
MS_CLIENT_SECRET
OAUTH_REDIRECT_BASE_URL
ALLOWED_EMAILS
ADMIN_EMAILS
SUPERVISOR_EMAILS
```

Em dev, `OAUTH_REDIRECT_BASE_URL=http://localhost:8506`.
Em prod, `https://tatic.jacare.cloud` 
---

### 6️⃣ Docker e CI/CD

Atualizar `docker-compose.yml` para injetar essas envs no serviço principal.
No workflow CI/CD do GitHub Actions, adicionar os secrets correspondentes.

---

### 7️⃣ Testes

1. Rodar localmente (`streamlit run app.py`).
2. Testar login Google → retorno com nome e e-mail.
3. Testar login Microsoft → idem.
4. Verificar bloqueio para e-mail fora da whitelist.
5. Confirmar roles funcionando (`usuario`, `supervisor`, `dev`).
6. Confirmar logout e sessão limpa.

---

### 8️⃣ Merge

Após validação completa e revisão manual:

```bash
git checkout main
git merge feat/oauth
git push origin main
```

Gerar release:

```bash
git tag -a v0.0.X -m "OAuth estável"
git push origin --tags
```

---

## ✅ Resultado esperado

* Login seguro via Google e Microsoft.
* Sessão persistente e validação de e-mail/role.
* Sem quebra na main.
* Preparado para deploy com secrets do GitHub.

---

## 📌 Observações

* Usar `st.link_button` para evitar redirecionamento automático (Streamlit limita isso).
* Garantir que o Nginx preserve `X-Forwarded-Prefix` e `Host` nos headers.
* Se `tatic.jacare.cloud`, incluir `?auth_callback=1&provider=<nome>` nos Redirect URIs.

---

💬 **Nota para o Copilot:**
Seguir estas instruções exatamente, criando arquivos e funções conforme descrito.
Não alterar módulos fora do escopo `auth/` e `app.py`.
Gerar commits claros:

* `feat(auth): add oauth module`
* `feat(ui): integrate oauth login flow`
---

