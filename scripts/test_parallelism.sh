#!/bin/bash

# Script para testar paralelismo com pandarallel
# Mede tempo de processamento com e sem paralelismo

set -e

echo "=================================================="
echo "🚀 Teste de Paralelismo - TATIC Processor"
echo "=================================================="
echo ""

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar se pandarallel está instalado
echo -e "${BLUE}📦 Verificando dependências...${NC}"
python3 -c "import pandarallel; print('✅ Pandarallel instalado')" 2>/dev/null || {
    echo -e "${YELLOW}⚠️  Pandarallel não encontrado. Instalando...${NC}"
    pip install pandarallel
}

# Script Python para benchmark
BENCH_SCRIPT=$(cat << 'EOF'
import pandas as pd
import numpy as np
import time
import os

# Desabilitar paralelismo temporariamente
os.environ['PANDAS_PARALLEL'] = '0'

try:
    from pandarallel import pandarallel
    PARALLEL_AVAILABLE = True
except ImportError:
    PARALLEL_AVAILABLE = False
    print("⚠️  Pandarallel não disponível")
    exit(1)

# Gerar dataset de teste
print("\n📊 Gerando dataset de teste...")
np.random.seed(42)
n_records = 50000

data = {
    'equipamento': np.random.choice(['B787', 'A380', 'A320', 'B767', 'R22', 'S76'], n_records),
    'valor1': np.random.rand(n_records),
    'valor2': np.random.randint(1, 100, n_records)
}

df = pd.DataFrame(data)
print(f"✅ Dataset criado: {len(df)} registros")

# Função de teste (simula get_aircraft_category)
def classify_aircraft(equipment):
    """Simula classificação de aeronave (categoria A-E ou H)"""
    classes = {
        'B787': 'D', 'A380': 'E', 'A320': 'C',
        'B767': 'C', 'R22': 'H', 'S76': 'H'
    }
    return classes.get(equipment, 'A')

# Teste 1: Sequential (apply normal)
print("\n" + "="*50)
print("🔄 Teste 1: SEQUENCIAL (apply normal)")
print("="*50)

start = time.time()
result_seq = df['equipamento'].apply(classify_aircraft)
time_seq = time.time() - start

print(f"⏱️  Tempo sequencial: {time_seq:.2f}s")
print(f"✅ Resultados: {len(result_seq)} classificações")

# Teste 2: Parallel (com pandarallel)
print("\n" + "="*50)
print("⚡ Teste 2: PARALELO (pandarallel com 2 workers)")
print("="*50)

pandarallel.initialize(nb_workers=2, progress_bar=True, verbose=1)

start = time.time()
result_par = df['equipamento'].parallel_apply(classify_aircraft)
time_par = time.time() - start

print(f"⏱️  Tempo paralelo: {time_par:.2f}s")
print(f"✅ Resultados: {len(result_par)} classificações")

# Comparação
print("\n" + "="*50)
print("📈 COMPARAÇÃO DE PERFORMANCE")
print("="*50)

improvement = ((time_seq - time_par) / time_seq) * 100
speedup = time_seq / time_par if time_par > 0 else 0

print(f"Tempo sequencial:   {time_seq:.2f}s")
print(f"Tempo paralelo:     {time_par:.2f}s")
print(f"Melhoria:           {improvement:+.1f}%")
print(f"Speedup:            {speedup:.2f}x")

if speedup > 1:
    print(f"\n✅ Paralelismo ATIVOU! Dataset grande beneficia de processamento em 2 cores")
else:
    print(f"\n⚠️  Overhead de paralelismo supera benefício em datasets pequenos")

print(f"\n💾 Memória: {df.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB")
EOF
)

# Executar benchmark
echo -e "\n${BLUE}🔬 Executando benchmark...${NC}\n"
python3 << 'PYTHONEOF'
import pandas as pd
import numpy as np
import time
import os

try:
    from pandarallel import pandarallel
except ImportError:
    print("❌ Pandarallel não instalado")
    exit(1)

print("\n📊 Gerando dataset de teste...")
np.random.seed(42)
n_records = 50000

data = {
    'equipamento': np.random.choice(['B787', 'A380', 'A320', 'B767', 'R22', 'S76'], n_records),
    'valor1': np.random.rand(n_records),
    'valor2': np.random.randint(1, 100, n_records)
}

df = pd.DataFrame(data)
print(f"✅ Dataset criado: {len(df)} registros")

def classify_aircraft(equipment):
    """Simula classificação de aeronave (categoria A-E ou H)"""
    classes = {
        'B787': 'D', 'A380': 'E', 'A320': 'C',
        'B767': 'C', 'R22': 'H', 'S76': 'H'
    }
    return classes.get(equipment, 'A')

# Teste 1: Sequential
print("\n" + "="*50)
print("🔄 Teste 1: SEQUENCIAL (apply normal)")
print("="*50)

start = time.time()
result_seq = df['equipamento'].apply(classify_aircraft)
time_seq = time.time() - start
print(f"⏱️  Tempo sequencial: {time_seq:.2f}s")

# Teste 2: Parallel
print("\n" + "="*50)
print("⚡ Teste 2: PARALELO (pandarallel com 2 workers)")
print("="*50)

pandarallel.initialize(nb_workers=2, progress_bar=False, verbose=0)
start = time.time()
result_par = df['equipamento'].parallel_apply(classify_aircraft)
time_par = time.time() - start
print(f"⏱️  Tempo paralelo: {time_par:.2f}s")

# Comparação
print("\n" + "="*50)
print("📈 COMPARAÇÃO DE PERFORMANCE")
print("="*50)

improvement = ((time_seq - time_par) / time_seq) * 100 if time_seq > 0 else 0
speedup = time_seq / time_par if time_par > 0 else 0

print(f"Tempo sequencial:   {time_seq:.2f}s")
print(f"Tempo paralelo:     {time_par:.2f}s")
print(f"Melhoria:           {improvement:+.1f}%")
print(f"Speedup:            {speedup:.2f}x")

if speedup > 1:
    print(f"\n✅ Paralelismo ATIVO! Operações em 2 cores.")
else:
    print(f"\n⚠️  Overhead > benefício para dataset pequeno")
PYTHONEOF

echo ""
echo -e "${GREEN}=================================================="
echo "✅ Teste de paralelismo concluído!"
echo "==================================================${NC}"
