#!/usr/bin/env python3

"""
🔍 Script de Debug Detalhado - Rastreamento de E-mails
Simula exatamente o que o app.py faz ao carregar os e-mails
"""

import os
from pathlib import Path

from dotenv import load_dotenv

print("=" * 60)
print("🔍 DEBUG DETALHADO - CARREGAMENTO DE E-MAILS")
print("=" * 60)
print()

# Simular o que app.py faz
print("📍 PASSO 1: Localizar arquivo .env")
print("-" * 60)

env_path = Path(__file__).parent / ".env"
print(f"Procurando em: {env_path}")
print(f"Diretório atual: {Path(__file__).parent}")

if env_path.exists():
    print("✅ Arquivo .env ENCONTRADO!")
    print(f"   Tamanho: {env_path.stat().st_size} bytes")
    print(f"   Caminho absoluto: {env_path.absolute()}")
else:
    print("❌ Arquivo .env NÃO ENCONTRADO!")
    print(f"   Procurando em: {env_path.absolute()}")

print()
print("📍 PASSO 2: Carregar variáveis de ambiente")
print("-" * 60)

# Antes de carregar
print("Antes de load_dotenv():")
print(f"  ADMIN_EMAILS    = '{os.getenv('ADMIN_EMAILS', 'NÃO ENCONTRADO')}'")
print(f"  ALLOWED_EMAILS  = '{os.getenv('ALLOWED_EMAILS', 'NÃO ENCONTRADO')}'")
print()

# Carregar do .env
if env_path.exists():
    print(f"Executando: load_dotenv(dotenv_path='{env_path}', override=True)")
    load_dotenv(dotenv_path=env_path, override=True)
else:
    print("Executando: load_dotenv(override=True)")
    load_dotenv(override=True)

print()
print("Depois de load_dotenv():")
admin_raw = os.getenv("ADMIN_EMAILS", "")
allowed_raw = os.getenv("ALLOWED_EMAILS", "")
print(f"  ADMIN_EMAILS    = '{admin_raw}'")
print(f"  ALLOWED_EMAILS  = '{allowed_raw}'")

print()
print("📍 PASSO 3: Processar e normalizar e-mails")
print("-" * 60)

# Split
admin_list = admin_raw.split(",")
allowed_list = allowed_raw.split(",")

print("Após split(','):")
print(f"  ADMIN_EMAILS    = {admin_list}")
print(f"  ALLOWED_EMAILS  = {allowed_list}")
print()

# Normalizar
authorized_users = [
    email.strip().lower() for email in admin_list + allowed_list if email.strip()
]

print("Após normalização (strip + lower + filter):")
print(f"  AUTHORIZED_USERS = {authorized_users}")
print()

print("📊 RESULTADO FINAL")
print("-" * 60)
print(f"✅ Total de usuários autorizados: {len(authorized_users)}")
print()

if authorized_users:
    print("✅ E-mails autorizados:")
    for i, email in enumerate(authorized_users, 1):
        print(f"   {i}. {email}")
else:
    print("❌ NENHUM E-MAIL AUTORIZADO ENCONTRADO!")
    print()
    print("📋 Checklist de verificação:")
    print("   □ Arquivo .env existe na raiz do projeto?")
    print("   □ .env contém ADMIN_EMAILS=... ?")
    print("   □ .env contém ALLOWED_EMAILS=... ?")
    print("   □ E-mails estão separados por vírgula?")
    print("   □ Sem espaços extras entre os e-mails?")

print()
print("=" * 60)
print("✨ Debug concluído!")
print("=" * 60)
