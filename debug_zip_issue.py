#!/usr/bin/env python3
"""
Script de debug para rastrear onde os arquivos são salvos
e por que o ZIP fica vazio em produção
"""

import os
import sys
import tempfile
import time
import zipfile
from pathlib import Path
from datetime import datetime
import uuid

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(__file__))

from tatic_processor import TATICProcessor


def debug_file_paths():
    """Debug: Mostrar estrutura de diretórios e caminhos"""
    print("\n" + "=" * 80)
    print("🔍 DEBUG: Verificando Caminhos e Estrutura de Diretórios")
    print("=" * 80 + "\n")

    # Diretório de trabalho
    cwd = os.getcwd()
    print(f"📁 Diretório de trabalho (cwd): {cwd}")
    print(f"   Type: {type(cwd)}")

    # Criar estrutura de diretórios como faz o app.py
    job_id = f"debug_job_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    # Caminhos RELATIVOS (como em app.py)
    uploads_dir_rel = os.path.join("uploads", job_id)
    outputs_dir_rel = os.path.join("outputs", job_id)
    
    # Caminhos ABSOLUTOS
    uploads_dir_abs = os.path.abspath(uploads_dir_rel)
    outputs_dir_abs = os.path.abspath(outputs_dir_rel)
    
    print(f"\n📂 Job ID: {job_id}\n")
    
    print("UPLOADS:")
    print(f"  Relativo: {uploads_dir_rel}")
    print(f"  Absoluto: {uploads_dir_abs}")
    print(f"  Existe? {os.path.exists(uploads_dir_abs)}")
    
    print("\nOUTPUTS:")
    print(f"  Relativo: {outputs_dir_rel}")
    print(f"  Absoluto: {outputs_dir_abs}")
    print(f"  Existe? {os.path.exists(outputs_dir_abs)}")
    
    # Criar os diretórios
    os.makedirs(uploads_dir_rel, exist_ok=True)
    os.makedirs(outputs_dir_rel, exist_ok=True)
    
    print(f"\n✅ Diretórios criados")
    print(f"  Uploads existe? {os.path.exists(uploads_dir_abs)}")
    print(f"  Outputs existe? {os.path.exists(outputs_dir_abs)}")
    
    # Converter para Path como no app.py
    output_dir_path = Path(outputs_dir_rel)
    print(f"\n📍 output_dir como Path:")
    print(f"  Path: {output_dir_path}")
    print(f"  Str: {str(output_dir_path)}")
    print(f"  Absolute: {output_dir_path.absolute()}")
    print(f"  Resolve: {output_dir_path.resolve()}")
    
    return job_id, uploads_dir_rel, outputs_dir_rel, output_dir_path


def debug_file_creation(output_dir_path):
    """Debug: Simular a criação de arquivos como faz o processor"""
    print("\n" + "=" * 80)
    print("🔍 DEBUG: Simular Criação de Arquivos")
    print("=" * 80 + "\n")
    
    # Criar arquivos como o processor faz
    test_files = [
        ("tabela1_movimento_percentual_categoria.csv", "col1,col2\n1,2\n"),
        ("tabela2_resultado_mix_categoria.csv", "data1,data2\n3,4\n"),
        ("tabela3_movimento_mensal_pista.csv", "mes,pista\n1,03\n"),
        ("tabela4_percentual_utilizacao_pistas.csv", "pista,pct\n03,50\n"),
        ("resumo.txt", "Relatório de teste\n"),
        ("charts_data.json", '{"chart":"data"}\n'),
    ]
    
    output_dir = Path(output_dir_path)
    print(f"📁 Criando arquivos em: {output_dir}")
    print(f"   Absoluto: {output_dir.absolute()}\n")
    
    for filename, content in test_files:
        filepath = output_dir / filename
        print(f"  Escrevendo: {filepath}")
        print(f"    Tipo: {type(filepath)}")
        print(f"    Absoluto: {filepath.absolute()}")
        
        with open(filepath, "w") as f:
            f.write(content)
        
        # Sincronizar (como faz o processor)
        try:
            with open(filepath) as f:
                os.fsync(f.fileno())
            print(f"    ✅ Arquivo criado e sincronizado")
        except Exception as e:
            print(f"    ⚠️ Erro ao sincronizar: {e}")
    
    time.sleep(1)
    
    # Verificar arquivos criados
    print(f"\n✅ Verificando arquivos em: {output_dir}")
    files_in_dir = list(os.listdir(str(output_dir)))
    print(f"   Total: {len(files_in_dir)} arquivos\n")
    
    for f in files_in_dir:
        filepath = output_dir / f
        size = os.path.getsize(filepath)
        print(f"   - {f}: {size} bytes")
    
    return output_dir, files_in_dir


def debug_zip_creation(output_dir):
    """Debug: Simular a criação do ZIP como em app.py"""
    print("\n" + "=" * 80)
    print("🔍 DEBUG: Simular Criação do ZIP")
    print("=" * 80 + "\n")
    
    # Converter output_dir para string como em app.py
    job_output_dir = str(output_dir)
    nome_arquivo = "debug_relatorio_test.zip"
    
    print(f"Parâmetros da função gerar_zip_de_relatorio:")
    print(f"  job_output_dir: {job_output_dir}")
    print(f"  Type: {type(job_output_dir)}")
    print(f"  Existe? {os.path.exists(job_output_dir)}")
    print(f"  Absoluto? {os.path.isabs(job_output_dir)}")
    print(f"  nome_arquivo: {nome_arquivo}\n")
    
    # Simular a função gerar_zip_de_relatorio
    zip_path = os.path.join("outputs", nome_arquivo)
    
    print(f"Criando ZIP em: {zip_path}")
    print(f"  Tipo: {type(zip_path)}")
    print(f"  Absoluto: {os.path.abspath(zip_path)}")
    print(f"  Existe diretório? {os.path.exists(os.path.dirname(zip_path))}\n")
    
    # Verificar arquivos antes de zipar
    print(f"Arquivos antes de zipar em {job_output_dir}:")
    if os.path.exists(job_output_dir):
        for root, _dirs, files in os.walk(job_output_dir):
            for file in files:
                abs_path = os.path.join(root, file)
                size = os.path.getsize(abs_path)
                print(f"  - {file}: {size} bytes")
    else:
        print(f"  ❌ ERRO: Diretório não existe!")
    
    print()
    
    # Criar o ZIP
    files_added = 0
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _dirs, files in os.walk(job_output_dir):
            for file in files:
                if not file.endswith(".zip"):
                    abs_path = os.path.join(root, file)
                    rel_path = os.path.relpath(abs_path, job_output_dir)
                    zipf.write(abs_path, arcname=rel_path)
                    print(f"  ✅ Adicionado ao ZIP: {rel_path}")
                    files_added += 1
    
    # Verificar ZIP criado
    print(f"\n✅ ZIP criado em: {zip_path}")
    print(f"   Absoluto: {os.path.abspath(zip_path)}")
    print(f"   Existe? {os.path.exists(zip_path)}")
    
    if os.path.exists(zip_path):
        file_size = os.path.getsize(zip_path)
        print(f"   Tamanho: {file_size} bytes")
        
        # Verificar conteúdo
        with zipfile.ZipFile(zip_path, "r") as zipf:
            items = zipf.namelist()
            print(f"   Arquivos no ZIP: {len(items)}")
            for item in items:
                info = zipf.getinfo(item)
                print(f"     - {item}: {info.file_size} bytes")
        
        if file_size < 100:
            print(f"\n⚠️ AVISO: ZIP muito pequeno ou vazio!")
            print(f"   Arquivos adicionados: {files_added}")
    else:
        print(f"   ❌ ZIP não foi criado!")


def debug_docker_volumes():
    """Debug: Mostrar estrutura de volumes como em Docker"""
    print("\n" + "=" * 80)
    print("🔍 DEBUG: Estrutura de Volumes em Docker")
    print("=" * 80 + "\n")
    
    print("Quando rodando em Docker:")
    print("  Working directory (app): /app")
    print("  Volume uploads: /app/uploads (bind mount)")
    print("  Volume outputs: /app/outputs (bind mount)")
    print("")
    print("Quando rodando localmente:")
    print(f"  Working directory: {os.getcwd()}")
    print("  Diretório uploads: ./uploads (relativo ao cwd)")
    print("  Diretório outputs: ./outputs (relativo ao cwd)")
    print("")
    print("⚠️ Possível Problema:")
    print("  Se em Docker o cwd for diferente, os caminhos relativos quebram!")
    print("  Solução: Usar caminhos absolutos ou garantir que cwd é /app")


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " DEBUG: Rastreamento de Arquivos e ZIP".center(78) + "║")
    print("╚" + "=" * 78 + "╝")
    
    # 1. Debug de caminhos
    job_id, uploads_dir, outputs_dir, output_dir_path = debug_file_paths()
    
    # 2. Debug de criação de arquivos
    output_dir, files_created = debug_file_creation(output_dir_path)
    
    # 3. Debug de criação de ZIP
    debug_zip_creation(output_dir)
    
    # 4. Debug de volumes Docker
    debug_docker_volumes()
    
    print("\n" + "=" * 80)
    print("✅ Debug Completo")
    print("=" * 80 + "\n")
