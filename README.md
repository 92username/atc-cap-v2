![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![Streamlit](https://img.shields.io/badge/Streamlit-%23FE4B4B.svg?style=for-the-badge&logo=streamlit&logoColor=white) ![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white)

![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white) ![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white) ![Docker Compose](https://img.shields.io/badge/Docker%20Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white) ![Hostinger](https://img.shields.io/badge/Hostinger-673DE6?style=for-the-badge&logo=hostinger&logoColor=white) ![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)

![Microsoft Excel](https://img.shields.io/badge/Microsoft_Excel-217346?style=for-the-badge&logo=microsoft-excel&logoColor=white)

[![CI/CD - TATIC Processor](https://github.com/92username/atc-cap-v2/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/92username/atc-cap-v2/actions/workflows/ci-cd.yml)

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
5. **Tabela 5 - Categoria por Dia da Semana** - Padrões semanais
6. **Tabela 6 - Mix por Categoria** - Resumo com percentuais

### 🧭 Interface do Usuário
- ✅ **Menu lateral expansível** com guia de uso
- ✅ **Seletor de modo** (Padrão/Helicóptero)
- ✅ **Visualização de dados**
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
python -m venv venv
source venv/bin/activate  # Linux/Mac

# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
streamlit run app.py
```

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
├── uploads/                  # Arquivos enviados
├── outputs/                  # Relatórios gerados
└── docker-compose.yml       # Configuração Docker
```

## 🎯 URLs de Acesso

- **Aplicação**: http://localhost:8502 (desenvolvimento)
- **Produção**: http://localhost (Docker)

## 🔧 Desenvolvimento

### Stack Tecnológico
- **Streamlit 1.24+** - Interface web
- **Pandas 2.0+** - Processamento de dados
- **OpenPyXL 3.1+** - Leitura de Excel
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
