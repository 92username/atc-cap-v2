# 🔍 Depuração: ZIP Vazio em Produção - Passos e Confirmações

## 📋 Resumo do Problema

**Sintoma em Produção:**
- ✅ Processamento TATIC funciona (não há erros)
- ✅ Arquivos CSV individuais (tabela1, tabela2, etc.) são criados
- ❌ ZIP final fica **vazio ou muito pequeno**

**Causa Identificada:**
1. **Problema de caminho relativo em Docker**
   - Localmente: cwd = `/home/nbx/Projects/jacare/atc-cap-v2`
   - Em Docker: cwd = `/app`
   - Caminho relativo `outputs/job_id/` pode resolver diferente

2. **Volumes do docker-compose**
   - `./uploads:/app/uploads` (bind mount)
   - `./outputs:/app/outputs` (bind mount)
   - Se o cwd for diferente, os caminhos quebram

3. **Race condition de sincronização**
   - Archivos criados asincronamente
   - ZIP criado pode encontrar diretório vazio

---

## ✅ Solução Implementada

### 1. **Usar caminhos ABSOLUTOS em `app.py`**

**Antes (quebrado em Docker):**
```python
upload_dir = os.path.join("uploads", job_id)  # ❌ Relativo
output_dir = os.path.join("outputs", job_id)  # ❌ Relativo
output_dir = Path(output_dir)  # Ainda relativo
```

**Depois (funciona em Docker):**
```python
base_dir = Path.cwd()  # Conseguir o cwd do app (será /app em Docker)
upload_dir = base_dir / upload_dir_rel  # ✅ Absoluto
output_dir = base_dir / output_dir_rel  # ✅ Absoluto
```

### 2. **Melhorar `gerar_zip_de_relatorio()`**

**Mudanças:**
- Aceita caminho ABSOLUTO para `job_output_dir`
- ZIP é criado no parent dir (outputs/) em vez de relativo
- Debug detalhado mostra exatamente o que está acontecendo
- Mostra número de arquivos encontrados vs adicionados ao ZIP

**Antes:**
```python
zip_path = os.path.join("outputs", nome_arquivo)  # ❌ Relativo
```

**Depois:**
```python
parent_dir = str(Path(job_output_dir).parent)
zip_path = os.path.join(parent_dir, nome_arquivo)  # ✅ Absoluto
```

### 3. **Debug via Streamlit**

- Mostrar `base_dir` no console
- Mostrar caminhos absolutamente no UI
- Listar arquivos encontrados vs adicionados ao ZIP

---

## 🧪 Passos para Validar a Correção

### Passo 1: Teste Local
```bash
cd /home/nbx/Projects/jacare/atc-cap-v2
python test_full_flow.py
# Verificar: ZIP deve ter 6 arquivos, ~2KB
```

### Passo 2: Teste em Docker Localmente
```bash
docker-compose up --build
# Acessar: http://localhost:8506
# Upload arquivo
# Verificar no UI:
#   - Base dir = /app
#   - Output dir = /app/outputs/job_XXXXX
#   - ZIP deve ter conteúdo
```

### Passo 3: Verificar Volumes
```bash
docker exec tatic-processor ls -lah /app/outputs/
# Deve mostrar diretórios de job e arquivos ZIP
```

### Passo 4: Deploy em Produção
```bash
git add app.py
git commit -m "Fix: usar caminhos absolutos para ZIP em Docker"
git push
./scripts/execute_on_vps.sh scripts/deploy_safe.sh
```

### Passo 5: Validar em Produção
```bash
# Acessar: http://147.79.82.234:8506
# Upload arquivo real
# Verificar:
#   1. Processamento completa
#   2. ZIP é criado (não vazio)
#   3. ZIP contém 6 arquivos
#   4. Download funciona
```

---

## 📍 Confirmações: Onde os CSVs/Relatórios são Salvos

### Estrutura Local
```
/home/nbx/Projects/jacare/atc-cap-v2/
├── uploads/
│   └── job_20251022094329_4ab733d6/
│       └── DataGrid-sbjr.xlsx
└── outputs/
    └── job_20251022094329_4ab733d6/
        ├── tabela1_movimento_percentual_categoria.csv
        ├── tabela2_resultado_mix_categoria.csv
        ├── tabela3_movimento_mensal_pista.csv
        ├── tabela4_percentual_utilizacao_pistas.csv
        ├── resumo.txt
        ├── charts_data.json
        └── relatorio_0001_22102025_STD.zip  ✅ ZIP contém os 6 arquivos
```

### Estrutura em Docker
```
/app/
├── uploads/
│   └── job_XXXXX/
│       └── arquivo.xlsx
└── outputs/
    └── job_XXXXX/
        ├── tabela1...csv
        ├── tabela2...csv
        ├── tabela3...csv
        ├── tabela4...csv
        ├── resumo.txt
        ├── charts_data.json
        └── relatorio_NNNN_DDMMYYYY_MODO.zip  ✅ Deve ter conteúdo

# Bind mounts no host (máquina local):
/home/nbx/Projects/jacare/atc-cap-v2/uploads  → /app/uploads
/home/nbx/Projects/jacare/atc-cap-v2/outputs  → /app/outputs
```

### Fluxo de Criação de Arquivos

1. **Upload (app.py)**
   ```
   user upload.xlsx
   ↓
   uploads/job_XXXXX/upload.xlsx  (salvo em disco)
   ```

2. **Processamento (tatic_processor.py)**
   ```
   uploads/job_XXXXX/upload.xlsx
   ↓
   asyncio.run(processor.process_tatic_data(...))
   ↓
   outputs/job_XXXXX/
     - tabela1.csv (salvo)
     - tabela2.csv (salvo)
     - tabela3.csv (salvo)
     - tabela4.csv (salvo)
     - resumo.txt (salvo)
     - charts_data.json (salvo)
     [_sync_file() garante fsync]
     [_sync_directory() garante sync]
   ```

3. **ZIP (app.py)**
   ```
   outputs/job_XXXXX/
     ├── tabela1.csv  ✅ Deve existir aqui
     ├── tabela2.csv  ✅ Deve existir aqui
     ├── ...
     └── charts_data.json  ✅ Deve existir aqui
   ↓
   gerar_zip_de_relatorio(
     job_output_dir="/app/outputs/job_XXXXX",  # ✅ ABSOLUTO
     nome_arquivo="relatorio_0001_22102025_STD.zip"
   )
   ↓
   outputs/relatorio_0001_22102025_STD.zip  ✅ Deve conter os 6 arquivos
   ```

---

## 🔧 Checklist de Debug

- [ ] Verificar `Path.cwd()` em Docker é `/app`
- [ ] Verificar arquivos CSV são criados em `/app/outputs/job_XXXXX/`
- [ ] Verificar `gerar_zip_de_relatorio()` recebe caminho ABSOLUTO
- [ ] Verificar ZIP é criado em `/app/outputs/`
- [ ] Verificar ZIP contém 6 arquivos (não vazio)
- [ ] Verificar volumes no docker-compose estão corretos
- [ ] Verificar bind mounts funcionam (arquivo em /app/outputs/ aparece no host)

---

## 📊 Saída de Debug Esperada

### Teste Local
```
[DEBUG] Base dir: /home/nbx/Projects/jacare/atc-cap-v2
[DEBUG] Output dir: /home/nbx/Projects/jacare/atc-cap-v2/outputs/job_XXXXX
[DEBUG ZIP] job_output_dir existe? True
[DEBUG ZIP] job_output_dir é absoluto? True
[DEBUG ZIP] Arquivos antes de zipar:
[DEBUG ZIP] - tabela1_movimento_percentual_categoria.csv (404 bytes)
[DEBUG ZIP] - tabela2_resultado_mix_categoria.csv (58 bytes)
[DEBUG ZIP] - tabela3_movimento_mensal_pista.csv (321 bytes)
[DEBUG ZIP] - tabela4_percentual_utilizacao_pistas.csv (48 bytes)
[DEBUG ZIP] - resumo.txt (250 bytes)
[DEBUG ZIP] - charts_data.json (1574 bytes)
[DEBUG ZIP] Total de arquivos no ZIP: 6
[DEBUG ZIP] Tamanho total do ZIP: 1963 bytes  ✅ NÃO VAZIO
```

### Em Docker (esperado)
```
[DEBUG] Base dir: /app
[DEBUG] Output dir: /app/outputs/job_XXXXX
[DEBUG ZIP] job_output_dir existe? True
[DEBUG ZIP] job_output_dir é absoluto? True
[DEBUG ZIP] Total de arquivos no ZIP: 6  ✅ NÃO VAZIO
```

### Se Quebrado (sintoma atual)
```
[DEBUG ZIP] Total de arquivos no ZIP: 0  ❌ VAZIO
[DEBUG ZIP] Tamanho total do ZIP: 22 bytes  ❌ Só header, sem conteúdo
```

---

## 📝 Logs para Monitorar em Produção

```bash
# Ver logs da aplicação
./scripts/execute_on_vps.sh scripts/logs_app.sh 100

# Procurar por:
grep "DEBUG ZIP" /var/log/docker-compose-app.log
grep "job_output_dir existe?" /var/log/docker-compose-app.log
grep "Total de arquivos no ZIP" /var/log/docker-compose-app.log

# Se vazio:
grep "⚠️ AVISO: ZIP vazio" /var/log/docker-compose-app.log
```

---

## ✨ Próximos Passos

1. ✅ Implementar correção (caminhos absolutos)
2. ✅ Testar localmente
3. 🟡 **Testar em Docker localmente**
4. 🟡 **Deploy em produção**
5. 🟡 **Validar em produção com arquivo real**
6. 🟡 **Remover debug prints (deixar apenas em erro)**
7. 🟡 **Documentar no README**
