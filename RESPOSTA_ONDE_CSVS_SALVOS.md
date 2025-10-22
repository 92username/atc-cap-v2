# 📍 RESPOSTA: Onde os CSVs/Relatórios são Salvos

## Localização dos Arquivos

### 1. **Arquivos de Input (Uploads)**
```
uploads/job_YYYYMMDDHHMMSS_XXXXXXXX/
└── DataGrid-sbjr.xlsx  (arquivo TATIC enviado)
```

### 2. **Arquivos de Output (CSVs de Relatório)**
```
outputs/job_YYYYMMDDHHMMSS_XXXXXXXX/
├── tabela1_movimento_percentual_categoria.csv
├── tabela2_resultado_mix_categoria.csv
├── tabela3_movimento_mensal_pista.csv
├── tabela4_percentual_utilizacao_pistas.csv
├── resumo.txt
└── charts_data.json
```

### 3. **Arquivo ZIP Final (Relatório Completo)**
```
outputs/
└── relatorio_NNNN_DDMMYYYY_MODO.zip
    (contém os 6 arquivos acima)
```

---

## Caminhos Completos

### Local (Desenvolvimento)
```
/home/nbx/Projects/jacare/atc-cap-v2/uploads/job_XXXXX/
/home/nbx/Projects/jacare/atc-cap-v2/outputs/job_XXXXX/
/home/nbx/Projects/jacare/atc-cap-v2/outputs/relatorio_NNNN_DDMMYYYY_MODO.zip
```

### Em Docker (Produção)
```
/app/uploads/job_XXXXX/
/app/outputs/job_XXXXX/
/app/outputs/relatorio_NNNN_DDMMYYYY_MODO.zip
```

---

## 🔧 Problema Corrigido

**Antes:** 
- Usava caminho relativo `outputs/job_id/`
- Em Docker, resolvia para lugar errado
- ZIP ficava vazio

**Depois:**
- Usa caminho absoluto `/app/outputs/job_id/`
- Em Docker, sempre funciona
- ZIP contém os 6 arquivos

---

## ✅ Como Confirmar

### Teste Local
```bash
python test_full_flow.py
# Verifica: arquivos CSV são criados + ZIP não está vazio ✅
```

### Em Produção
```bash
# Via Streamlit UI:
# [DEBUG] Output dir: /app/outputs/job_XXXXX
# [DEBUG ZIP] Total de arquivos no ZIP: 6  ← Deve ser 6, não 0
```

---

## 📊 Fluxo Completo

```
1. User upload arquivo.xlsx
   ↓
2. Sistema salva em: uploads/job_XXXXX/arquivo.xlsx
   ↓
3. Processamento (tatic_processor.py)
   ├─ Lê arquivo.xlsx
   └─ Cria 6 arquivos em: outputs/job_XXXXX/
      ├─ tabela1.csv
      ├─ tabela2.csv
      ├─ tabela3.csv
      ├─ tabela4.csv
      ├─ resumo.txt
      └─ charts_data.json
   ↓
4. Sincronização de disco (fsync)
   ↓
5. Criação do ZIP
   ├─ Lê: /app/outputs/job_XXXXX/  ← AGORA COM CAMINHO ABSOLUTO ✅
   └─ Cria: /app/outputs/relatorio_0001_22102025_STD.zip
      (contém os 6 arquivos)
   ↓
6. User baixa o ZIP
```

---

## 🎯 Resumo

| Item | Local | Docker |
|------|-------|--------|
| **Upload** | `./uploads/job_id/` | `/app/uploads/job_id/` |
| **CSVs** | `./outputs/job_id/` | `/app/outputs/job_id/` |
| **ZIP** | `./outputs/nome.zip` | `/app/outputs/nome.zip` |
| **Path Type** | Absoluto ✅ | Absoluto ✅ |
| **Funciona** | SIM | SIM |

