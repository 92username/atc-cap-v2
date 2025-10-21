[![CI/CD - TATIC Processor](https://github.com/92username/atc-cap-v2/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/92username/atc-cap-v2/actions/workflows/ci-cd.yml)

![Python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue) ![Pandas](https://img.shields.io/badge/Pandas-2C2D72?style=for-the-badge&logo=pandas&logoColor=white) ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white) ![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white) ![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white) ![Github Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white) ![Excel](https://img.shields.io/badge/Microsoft_Excel-217346?style=for-the-badge&logo=microsoft-excel&logoColor=white)


# 🛫 TATIC Análise de Dados - Aplicação Web

## 🚀 Visão Geral

Aplicação web para processamento e análise de dados TATIC  com interface Streamlit, classificação de aeronaves e geração automática de relatórios de acordo com a MCA 100-26.

### 🧭 Interface do Usuário
- ✅ **Menu lateral expansível** com guia de uso
- ✅ **Seletor de modo** (Padrão/Helicóptero)
- ✅ **Download de relatórios** em formato ZIP

### 📦 Sistema de Relatórios
- ✅ **Nomes incrementais** - `relatorio_NNNN_DDMMYYYY_MODO.zip`
- ✅ **Identificação por modo** - STD (padrão) ou H (helicóptero)
- ✅ **Numeração sequencial** automática por dia

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

## 🎯 URLs de Acesso

- **Aplicação**: http://localhost:8502 (desenvolvimento)
- **Produção**: 
---
