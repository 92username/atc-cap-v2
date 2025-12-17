# 🧭 Missão TATIC Processor — Linha de Ataque Prioritária

## 🔰 Etapa 1️⃣ — Infra / Deploy (ação imediata)

Essas são as primeiras tarefas práticas para retomar o projeto e confirmar que o pipeline funciona do início ao fim.

* [X] **Testar o pipeline CI/CD completo** (`git push origin main`)
  → Verificar se o workflow executa **build → push → deploy** corretamente.
* [X] **Validar o container rodando na VPS**:

  ```bash
  docker ps
  docker logs tatic-processor
  ```
* [X] **Confirmar persistência dos relatórios** (`/var/www/streamlit-reports`): gerar e verificar se o diretório é mantido após reinício do container.

---

## ⚙️ Etapa 2️⃣ — Pipeline / Config (ajustes finos pós-deploy)

Essas tarefas otimizam o fluxo de CI/CD após o primeiro deploy bem-sucedido.

* [x] **Revisar o arquivo `.github/workflows/ci-cd.yml`**
  → Garantir que todas as variáveis estão com `92username`.
  → Confirmar dependência `needs: ci` e condição `if: github.ref == 'refs/heads/main'`.
* [x] **Adicionar tag dinâmica no build (opcional)**:
  `${{ github.sha }}` ou `latest` para facilitar versionamento no GHCR.
* [x] **Testar rollback manual**: recriar o container com uma imagem anterior para garantir reversão segura.

---

## 🧠 Etapa 3️⃣ — Qualidade / Documentação (estabilização)

Após o pipeline estar rodando com sucesso, essas tarefas formalizam e registram o processo.

* [x] Criar `README_DEPLOY.md` descrevendo setup, secrets e CI/CD.
* [x] Adicionar seção **“Como atualizar a imagem”** (para orientar futuros devs).
* [x] Tirar print do Actions rodando com sucesso (para registro interno e histórico de release).

---

## 🔮 Etapa 4️⃣ — Evoluções futuras (próximos ciclos)

Essas são as features e melhorias planejadas para fases seguintes do projeto.

* [ ] Integrar autenticação (OAuth whitelist dos 5 usuários).
* [ ] Adicionar controle de permissões (gerente vs. usuário normal).
* [ ] Implementar upload e persistência de relatórios `.zip`.
* [ ] Configurar monitoramento de logs e updates automáticos (ex: healthcheck ou Watchtower).

---

## 📘 Status Geral

| Etapa                   | Status | Observação                                |
| ----------------------- | ------ | ----------------------------------------- |
| Testes locais Streamlit | ✅      | App rodando sem erros                     |
| Definição de porta      | ✅      | Porta **8506** reservada na VPS           |
| `.env.example`          | ✅      | Atualizado com `APP_NAME=tatic-processor` |
| Secrets e GHCR Token    | ✅      | Testado com sucesso (**Login succeeded**) |

---
