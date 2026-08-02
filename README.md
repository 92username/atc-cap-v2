[![CI/CD - TATIC Processor](https://github.com/92username/atc-cap-v2/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/92username/atc-cap-v2/actions/workflows/ci-cd.yml)

![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white) ![Streamlit](https://img.shields.io/badge/Streamlit-%23FE4B4B.svg?style=for-the-badge&logo=streamlit&logoColor=white) ![Pandas](https://img.shields.io/badge/Pandas-150458.svg?style=for-the-badge&logo=pandas&logoColor=white) ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white) ![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)

# 🛫 TATIC Análise de Dados - Aplicação Web

## 🚀 Visão Geral

Aplicação web para processamento e análise de dados TATIC  com interface Streamlit, classificação de aeronaves e geração automática de relatórios de acordo com a MCA 100-26.

## 🏗️ Arquitetura

- **Interface**: Streamlit - Interface web
- **Processamento**: Python + Pandas - Motor de análise de dados
- **Deploy**: Docker - Deploy containerizado para produção (em desenvolvimento)
- **Dados**: Excel (.xlsx) → CSV → Relatórios ZIP

## 🎯 Funcionalidades Principais

### 📊 Processamento de Dados
- ✅ **Upload drag-and-drop** de arquivos Excel (.xlsx)
- ✅ **Base interna opcional na VPS** para iniciar o app sem planilha local
- ✅ **Processamento rápido** de 155k+ registros em 70 segundos
- ✅ **Validação automática** de estrutura e cabeçalhos TATIC
- ✅ **Logs em tempo real** durante o processamento

### 🚁 Classificação de Aeronaves
- ✅ **Modo Padrão (A-E)** - Categorias tradicionais de wake turbulence
- ✅ **Modo Helicóptero (H)** - Categoria especial para helicópteros
- ✅ **47+ modelos de helicópteros** reconhecidos automaticamente


### 📋 Relatórios Gerados
1. **Tabela 1 - Movimentos ATC Total** - Estatísticas gerais de tráfego
2. **Tabela 2 - Movimentos por Pista** - Distribuição por cabeceiras
3. **Tabela 3 - Percentual por Pista** - Análise de utilização
4. **Tabela 4 - Mix de Aeronaves** - Classificação por esteira de turbulência

### 🧭 Interface do Usuário
- ✅ **Seletor de modo** (Padrão/Helicóptero)
- ✅ **Seletor de fonte de dados** (base interna ou upload)
- ✅ **Download de relatórios** em formato ZIP

### 📦 Sistema de Relatórios
- ✅ **Nomes incrementais** - `relatorio_NNNN_DDMMYYYY_MODO.zip`
- ✅ **Identificação por modo** - STD (padrão) ou H (helicóptero)
- ✅ **Numeração sequencial** automática por dia
## 🚀 Início Rápido

### Desenvolvimento Local
```bash
# Clone o repositório
git clone https://github.com/92username/atc-cap-v2
cd atc-cap-v2

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac

# Instalar dependências
pip install -r requirements.txt

# Exportar e-mails autorizados para teste local
# Essas variáveis são injetadas em produção via GitHub Actions / container
export ADMIN_EMAILS="seu-email@exemplo.com"
export ALLOWED_EMAILS="seu-email@exemplo.com"

# Executar aplicação
streamlit run app.py
```

Se você não exportar `ADMIN_EMAILS` e `ALLOWED_EMAILS` localmente, o login do app vai negar acesso, porque em produção esses valores chegam ao container via variáveis de ambiente injetadas pelo GitHub Actions.

### Base interna na VPS
Se quiser que o app suba já com uma planilha "embutida" no backend:

```bash
mkdir -p data/internal
cp /caminho/da/sua/base_tatic.xlsx data/internal/base_tatic.xlsx
export INTERNAL_TATIC_FILE=/app/data/internal/base_tatic.xlsx
docker compose up -d
```

Na interface, o usuário poderá escolher:
- `Usar dados internos da VPS`
- `Enviar nova planilha (.xlsx)`

Importante:
- a planilha interna não deve ficar em pasta pública;
- ela não precisa entrar no Git;
- o container só precisa de leitura nesse volume.

## 📋 Formato de Dados TATIC

### Colunas Obrigatórias
- **H.Evento** → Horário UTC do evento (formato: YYYY-mês-DD HH:MM:SS)
- **Indicativo** → Prefixo ou matrícula da aeronave
- **Evento** → Tipo de evento (ARR, DEP, TGL, etc.)
- **Num. Evento** → Número identificador sequencial
- **Origem/Destino** → Aeroportos de origem e destino
- **Equipamento** → Modelo da aeronave (ex: A320L, B738M)
- **TV** → Tipo de voo
- **Pista** → Cabeceira utilizada (ex: 03, 21)
- **RV** → Regra de voo (VFR/IFR)
- **Operador Evento** → Responsável pelo registro

## � Configuração

### Estrutura de Diretórios
```
atc-cap-v2/
├── app.py                    # Interface Streamlit
├── tatic_processor.py        # Motor de processamento
├── requirements.txt          # Dependências Python
├── assets/
│   ├── categorias-A-E.csv   # Tabela de categorias
│   └── DataGrid-sbjr.xlsx   # Arquivo de exemplo
├── data/internal/            # Base interna opcional montada na VPS
├── uploads/                  # Arquivos enviados
├── outputs/                  # Relatórios gerados
└── docker-compose.yml       # Configuração Docker
```

## 🎯 URLs de Acesso

- **Aplicação**: http://localhost:8502 (desenvolvimento)
- **Produção**: https://tatic.jacare.cloud (Produção)

## 🔧 Desenvolvimento

### Stack Tecnológico
- **Streamlit 1.28.0** - Interface web
- **Pandas 2.0+** - Processamento de dados
- **OpenPyXL 3.1.2** - Leitura de Excel
- **Docker** - Containerização
- **Nginx** - Proxy reverso (produção)

## 🔄 CI/CD Pipeline

O projeto utiliza GitHub Actions para automação de CI/CD com os seguintes stages:

### 🧹 Lint

- **Black**
- **Ruff**

### 🧪 Test

- **Pytest**

### 🐳 Build & Deploy

- **Docker**
- **GHCR**
---
