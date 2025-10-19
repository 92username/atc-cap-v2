# 📋 Scripts Essenciais - ATC-CAP-V2

## 🎯 Scripts para Uso Regular

### 1. **execute_on_vps.sh** ⭐ **BASE**
- **Função**: Executor SSH universal para scripts remotos
- **Uso**: `./execute_on_vps.sh <script_remoto> [args]`
- **Exemplo**: `./execute_on_vps.sh scripts/logs_app.sh 100`
- **Dependência**: Todos os outros scripts usam este como base

### 2. **logs_app.sh** 📊
- **Função**: Ver logs da aplicação tatic-processor em tempo real
- **Uso**: `./execute_on_vps.sh logs_app.sh 50`
- **Argumento**: Número de linhas (default: 50)
- **Caso de uso**: Debug, monitoramento

### 3. **status.sh** 🟢
- **Função**: Ver status de todos os containers
- **Uso**: `./execute_on_vps.sh status.sh`
- **Mostra**: Status, porta, uptime de cada container
- **Caso de uso**: Verificar saúde dos serviços

### 4. **vps_diagnostics.sh** 🔍
- **Função**: Diagnóstico completo da VPS
- **Uso**: `./execute_on_vps.sh vps_diagnostics.sh`
- **Mostra**: Containers, portas, SSL, disco, rede
- **Caso de uso**: Troubleshooting, verificação geral

### 5. **backup.sh** 💾
- **Função**: Fazer backup automático da aplicação
- **Uso**: `./execute_on_vps.sh backup.sh`
- **Salva em**: `/root/backups/`
- **Caso de uso**: Antes de grandes atualizações

### 6. **deploy_safe.sh** 🚀
- **Função**: Deploy seguro com verificações
- **Uso**: `./execute_on_vps.sh deploy_safe.sh`
- **Faz**: Backup, rebuild, restart
- **Caso de uso**: Atualizar aplicação em produção

### 7. **nginx_setup_safe.sh** 🔒
- **Função**: Renovar/reconfigurar SSL e Nginx
- **Uso**: `./execute_on_vps.sh nginx_setup_safe.sh`
- **Faz**: Certbot, validação SSL, reload Nginx
- **Caso de uso**: Problemas com SSL, renovação manual

### 8. **git_commit.sh** 📝
- **Função**: Fazer commit automático (opcional)
- **Uso**: `./git_commit.sh "mensagem"`
- **Caso de uso**: Backup do código no Git

---

## 📁 Estrutura

```
/scripts/
├── execute_on_vps.sh        ⭐ BASE - Infraestrutura
├── logs_app.sh              📊 Logs em tempo real
├── status.sh                🟢 Status containers
├── vps_diagnostics.sh       🔍 Diagnóstico completo
├── backup.sh                💾 Backup automático
├── deploy_safe.sh           🚀 Deploy seguro
├── nginx_setup_safe.sh      🔒 SSL/Nginx
├── git_commit.sh            📝 Git automático
├── README_ESSENCIAL.md      📖 Este arquivo
└── archive/                 📦 Scripts históricos/teste
    ├── debug_streamlit.sh
    ├── fix_tatic_*.sh
    ├── test_*.sh
    └── ... (21 mais)
```

---

## 🚀 Fluxo de Trabalho Típico

### 1️⃣ Verificar Saúde
```bash
./execute_on_vps.sh vps_diagnostics.sh
```

### 2️⃣ Ver Logs
```bash
./execute_on_vps.sh logs_app.sh 100
```

### 3️⃣ Fazer Backup
```bash
./execute_on_vps.sh backup.sh
```

### 4️⃣ Deploy (se houver mudança)
```bash
./execute_on_vps.sh deploy_safe.sh
```

---

## 🔧 Variáveis Globais

Configurar em `~/.bash_profile` ou `.bashrc`:

```bash
export VPS_IP="147.79.82.234"
export VPS_USER="root"
export SSH_KEY="~/.ssh/mcp_vps"
```

---

## 📞 Troubleshooting

| Problema | Solução |
|----------|---------|
| Script não executa | `chmod +x script.sh` |
| SSH connection refused | Verificar VPS_IP e SSH_KEY |
| Port já em uso | `./execute_on_vps.sh status.sh` |
| SSL expirado | `./execute_on_vps.sh nginx_setup_safe.sh` |
| App lenta | `./execute_on_vps.sh logs_app.sh 200` |

---

## 🎓 Histórico & Archive

Os scripts em `/scripts/archive/` foram usados durante:
- Setup inicial da VPS
- Debug de problemas Nginx
- Testes de configuração Streamlit
- Experimentações com Docker

**Podem ser consultados se necessário troubleshooting**, mas não são mais necessários para operação normal.

---

**Last Updated**: 2025-10-19
