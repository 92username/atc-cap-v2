# 🛫 TATIC Análise de Dados - Aplicação Web

## 🚀 Visão Geral

Aplicação web para processamento e análise de dados TATIC  com interface Streamlit, classificação de aeronaves e geração automática de relatórios detalhados.

## 🏗️ Arquitetura

- **Interface**: Streamlit - Interface web responsiva
- **Processamento**: Python + Pandas - Motor de análise de dados
- **Deploy**: Docker + Nginx - Deploy containerizado para produção
- **Dados**: Excel (.xlsx) → CSV → Relatórios ZIP

## 🎯 Funcionalidades Principais

### 📊 Processamento de Dados
- ✅ **Upload drag-and-drop** de arquivos Excel (.xlsx)
- ✅ **Processamento rápido** de 155k+ registros em 60 segundos
- ✅ **Validação automática** de estrutura e cabeçalhos TATIC
- ✅ **Logs em tempo real** durante o processamento

### 🚁 Classificação de Aeronaves
- ✅ **Modo Padrão (A-E)** - Categorias tradicionais de wake turbulence
- ✅ **Modo Helicóptero (H)** - Categoria especial para helicópteros
- ✅ **47+ modelos de helicópteros** reconhecidos automaticamente
- ✅ **Suporte a formatos** CODIGO/WAKE e CODIGOWAKE

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
git clone <repository>
cd atc-cap-v2

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
streamlit run app.py
```

### Docker (Produção)
```bash
# Build e execução
docker-compose up --build

# Acesso
# http://localhost (produção)
# http://localhost:8502 (desenvolvimento)
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

### Variáveis de Ambiente
```bash
TATIC_CATEGORIAS_CSV=./assets/categorias-A-E.csv  # Opcional
```

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

## � Helicópteros Suportados

A aplicação reconhece automaticamente **47 modelos** de helicópteros, incluindo:
- **Eurocopter**: EC35, EC120, EC130, EC135, EC145, EC155, EC225, etc.
- **Airbus**: H120, H125, H130, H135, H145, H155, H160, H175, etc.
- **Robinson**: R22, R44, R66
- **Sikorsky**: S76, S92
- **Augusta/Leonardo**: A109, A119, A139, AW109, AW119, AW139, etc.
- **MD Helicopters**: MD500, MD600
- **Outros**: BK117, BO105, OH58, UH1, UH60, etc.

## 🎯 URLs de Acesso

- **Aplicação**: http://localhost:8502 (desenvolvimento)
- **Produção**: http://localhost (Docker)
- **Documentação**: Este README.md

## 📋 Requisitos do Sistema

- **Python**: 3.11+
- **RAM**: 4GB+ (processamento de grandes datasets)
- **Espaço**: 2GB+ (armazenamento de relatórios)
- **Browser**: Chrome, Firefox, Safari, Edge (moderno)

## 🔧 Desenvolvimento

### Stack Tecnológico
- **Streamlit 1.24+** - Interface web
- **Pandas 2.0+** - Processamento de dados
- **OpenPyXL 3.1+** - Leitura de Excel
- **Docker** - Containerização
- **Nginx** - Proxy reverso (produção)

### Contribuição
1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

---

**🛫 Desenvolvido para análise profissional de tráfego aéreo seguindo padrões ICAO e melhores práticas da aviação civil**