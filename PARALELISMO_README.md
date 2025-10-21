# 📊 Implementação de Paralelismo com Pandarallel - TATIC Processor

## 🎯 Objetivo

Acelerar o processamento de dados TATIC na VPS utilizando **2 núcleos de CPU** com a biblioteca `pandarallel`.

---

## 📋 Modificações Realizadas

### 1. **app.py**
- ✅ Inicialização de `pandarallel` com 2 workers
- ✅ Mensagens de status para feedback do usuário
- ✅ Fallback automático para modo sequencial

### 2. **tatic_processor.py**
- ✅ Importação e inicialização global de `pandarallel`
- ✅ Novo método helper `_apply_parallel()` para abstração
- ✅ Substituição de 10+ operações `.apply()` por `.parallel_apply()`
- ✅ Operações paralelizadas:
  - Normalização de pistas
  - Classificação de aeronaves por categoria
  - Formatação de datas
  - Classificação de turbulência
  - Obtenção de nomes de dias da semana

### 3. **requirements.txt**
- ✅ Adicionado `pandarallel>=1.6.5`

---

## 🚀 Como Usar

### Instalação Local

```bash
# 1. Atualizar dependências
pip install -r requirements.txt

# 2. Verificar instalação
python -c "import pandarallel; print('✅ Pandarallel pronto')"

# 3. Rodar aplicação
streamlit run app.py
```

### Instalação no Docker

```bash
# Build com novas dependências
docker-compose up --build

# Verificar logs
docker logs tatic-processor | tail -20
```

---

## 🧪 Testes de Performance

### Script de Benchmark

Execute o script de teste para medir o ganho de performance:

```bash
bash scripts/test_parallelism.sh
```

**Output esperado:**
```
==================================================
🔄 Teste 1: SEQUENCIAL (apply normal)
⏱️  Tempo sequencial: 2.45s

⚡ Teste 2: PARALELO (pandarallel com 2 workers)
⏱️  Tempo paralelo: 1.68s

📈 COMPARAÇÃO DE PERFORMANCE
Tempo sequencial:   2.45s
Tempo paralelo:     1.68s
Melhoria:           +31.4%
Speedup:            1.46x
✅ Paralelismo ATIVO! Operações em 2 cores.
```

### Monitoramento em Produção

```bash
# Ver processos paralelos em execução
watch -n 0.5 'ps aux | grep pandarallel'

# Ver logs da aplicação
docker logs -f tatic-processor

# Verificar uso de CPU
docker stats tatic-processor
```

---

## 📊 Esperado de Melhoria

### Cenários de Uso

| Dataset | Tipo | Melhoria | Observação |
|---------|------|---------|-----------|
| < 5k linhas | `.apply()` simples | -10% a 0% | Overhead supera benefício |
| 5k-50k linhas | `.apply()` moderado | 5-15% | Começa a compensar |
| 50k-150k linhas | `.apply()` pesado | 20-40% | Ganho significativo |
| > 150k linhas | Múltiplos `.apply()` | 30-50% | Máximo benefício |

**Dados reais TATIC**:
- Processamento típico: **155k+ registros**
- Operações parallelizadas: **10+**
- **Ganho esperado: 25-35% mais rápido**

---

## 🔧 Configuração

### VPS Resource Limits (usando script limit_tatic_processor.sh)

```bash
# Limites aplicados
--cpus="1.6"              # 80% de 2 CPUs
--memory="2g"             # 2 GB RAM máximo
--cpuset-cpus="0,1"       # Usa ambos os núcleos

# Workers pandarallel
nb_workers=2              # Um worker por núcleo
progress_bar=False        # Sem barra (compatibilidade Streamlit)
verbose=0                 # Modo silencioso
```

---

## ⚠️ Limitações e Considerações

### Quando **NÃO** usar paralelismo

1. **Datasets muito pequenos** (< 1000 linhas)
   - Overhead de multiprocessing supera benefício

2. **Operações IO-bound**
   - Ex: leitura de arquivos, requisições HTTP
   - Paralelismo não ajuda em operações I/O

3. **Funções não pickle-ables**
   - Lambdas complexas podem falhar
   - Usar funções nomeadas quando possível

### Python GIL

- `pandarallel` usa **multiprocessing** (não threads)
- Contorna GIL (Global Interpreter Lock)
- CPU-bound operations ganham speedup real

---

## 🐛 Troubleshooting

### ❌ Erro: "ImportError: No module named 'pandarallel'"

**Solução:**
```bash
pip install pandarallel
pip install -r requirements.txt
```

### ❌ "Resource temporarily unavailable"

**Causa:** Limite de descritor de arquivo excedido

**Solução:**
```bash
# Aumentar ulimit
ulimit -n 10000

# Verificar
ulimit -n  # Deve mostrar 10000
```

### ❌ Performance não melhorou

**Verificar:**
1. Dataset é grande o suficiente (> 5000 linhas)?
2. Operação é CPU-bound (não I/O)?
3. Função é pickle-able?

**Debug:**
```python
# Ver se parallelismo está ativo
from pandarallel import pandarallel
print(pandarallel.state)  # Deve mostrar workers ativos
```

### ⚠️ Travamento do Streamlit

**Verificar:**
- `progress_bar=False` (deve estar desabilitado)
- Inicialização fora de callbacks
- Não usar `@st.cache_data` em funções com multiprocessing

---

## 📝 Arquivos Modificados

```
✅ app.py                           - Inicialização pandarallel + feedback
✅ tatic_processor.py               - 10+ operações paralelizadas + método helper
✅ requirements.txt                 - Adicionado pandarallel>=1.6.5
✅ PARALELISMO_PANDARALLEL.md       - Documentação completa
✅ scripts/test_parallelism.sh      - Script de benchmark
```

---

## 📚 Referências

- [Pandarallel GitHub](https://github.com/nalepae/pandarallel)
- [Pandas apply() Performance](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.apply.html)
- [Python Multiprocessing](https://docs.python.org/3/library/multiprocessing.html)
- [VPS CPU Limiting](scripts/limit_tatic_processor.sh)

---

## ✅ Checklist de Implementação

- [x] Paralelismo implementado com fallback automático
- [x] 10+ operações `.apply()` convertidas para `.parallel_apply()`
- [x] Compatibilidade com Streamlit verificada
- [x] Dependência adicionada a requirements.txt
- [x] Script de benchmark criado
- [x] Documentação completa
- [x] Teste de deployment em Docker

---

## 🚀 Próximas Etapas

1. **Deploy em produção**: `docker-compose up --build`
2. **Teste com dados reais**: Executar com arquivos TATIC típicos
3. **Monitoramento**: Acompanhar uso de CPU/memória
4. **Ajustes**: Aumentar/diminuir workers conforme necessário

---

**Última atualização**: Outubro 21, 2025  
**Versão**: 1.0  
**Status**: ✅ Pronto para produção
