#!/usr/bin/env python3
"""
Teste completo do processamento e geração de ZIP
Simula o fluxo que acontece no Streamlit
"""

import os
import sys
import time
import traceback
import uuid
import zipfile
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

from tatic_processor import TATICProcessor


def gerar_zip_de_relatorio(job_output_dir: str, nome_arquivo: str):
    """
    Função copiada de app.py para testar
    """
    zip_path = os.path.join("outputs", nome_arquivo)

    # DEBUG: Verificar arquivos disponíveis antes de zipar
    print(f"[DEBUG ZIP] Diretório: {job_output_dir}")
    print("[DEBUG ZIP] Arquivos antes de zipar:")
    if os.path.exists(job_output_dir):
        for root, _dirs, files in os.walk(job_output_dir):
            for file in files:
                fpath = os.path.join(root, file)
                fsize = os.path.getsize(fpath)
                print(f"[DEBUG ZIP] - {file}: {fsize} bytes")
    else:
        print(f"[DEBUG ZIP] Diretório {job_output_dir} não existe!")

    # Criar o ZIP com todos os arquivos
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _dirs, files in os.walk(job_output_dir):
            for file in files:
                if not file.endswith(".zip"):
                    abs_path = os.path.join(root, file)
                    rel_path = os.path.relpath(abs_path, job_output_dir)
                    zipf.write(abs_path, arcname=rel_path)
                    print(f"[DEBUG ZIP] Adicionado ao ZIP: {rel_path}")

    # DEBUG: Verificar conteúdo do ZIP
    print(f"\n[DEBUG ZIP] Verificando ZIP {zip_path}:")
    if os.path.exists(zip_path):
        try:
            with zipfile.ZipFile(zip_path, "r") as zipf:
                items = zipf.namelist()
                print(f"[DEBUG ZIP] Arquivos no ZIP: {len(items)}")
                for item in items:
                    info = zipf.getinfo(item)
                    print(f"[DEBUG ZIP] - {item}: {info.file_size} bytes")

            zip_size = os.path.getsize(zip_path)
            print(f"[DEBUG ZIP] Tamanho do ZIP: {zip_size} bytes")

            if zip_size < 100:
                print("[DEBUG ZIP] ⚠️ AVISO: ZIP muito pequeno (possível vazio)")
                return zip_path, False

            return zip_path, True
        except zipfile.BadZipFile:
            print("[DEBUG ZIP] ❌ ERRO: ZIP vazio ou corrompido!")
            return zip_path, False
    else:
        print("[DEBUG ZIP] ❌ ERRO: Arquivo ZIP não foi criado!")
        return zip_path, False


def test_full_processing():
    """Teste completo do fluxo"""
    print("\n" + "=" * 70)
    print("🧪 TESTE COMPLETO: Processamento + ZIP")
    print("=" * 70 + "\n")

    # Verificar arquivo de teste
    test_file = Path("/home/nbx/Projects/jacare/atc-cap-v2/assets/DataGrid-sbjr.xlsx")
    if not test_file.exists():
        print(f"❌ Arquivo de teste não encontrado: {test_file}")
        return False

    print(f"✅ Arquivo de teste encontrado: {test_file}")
    print(f"   Tamanho: {test_file.stat().st_size / 1024 / 1024:.2f} MB\n")

    # Criar IDs como no app.py
    job_id = f"test_job_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"

    # Criar diretórios
    output_dir = os.path.join("outputs", job_id)
    os.makedirs(output_dir, exist_ok=True)

    print(f"📁 Diretório de saída criado: {output_dir}\n")

    # Processar
    print("🚀 Iniciando processamento...")
    tempo_inicio = time.time()

    processor = TATICProcessor(usar_categoria_h=False, incluir_finais_de_semana=False)

    try:
        import asyncio

        resultado = asyncio.run(processor.process_tatic_data(str(test_file), Path(output_dir)))

        tempo_processamento = time.time() - tempo_inicio

        if resultado.get("success"):
            print("\n✅ Processamento concluído com sucesso!")
            print(f"   Tempo: {tempo_processamento:.2f} segundos")
            print(f"   Movimentos ATC: {resultado['statistics']['atc_movements']}")
            print(f"   Movimentos de pista: {resultado['statistics']['runway_movements']}")
        else:
            print(f"\n❌ Erro no processamento: {resultado.get('error')}")
            return False

    except Exception as e:
        print(f"\n❌ Exceção durante processamento: {e}")
        import traceback

        traceback.print_exc()
        return False

    # Aguardar como em app.py
    print("\n⏳ Aguardando 1 segundo para sincronização...")
    time.sleep(1)

    # Verificar arquivos
    print(f"\n✔️ Verificando arquivos em {output_dir}...")
    files_in_dir = list(os.listdir(output_dir))
    print(f"   📊 Arquivos encontrados: {len(files_in_dir)}")

    if len(files_in_dir) == 0:
        print("\n❌ ERRO: Nenhum arquivo foi criado!")
        return False

    for f in sorted(files_in_dir):
        file_path = os.path.join(output_dir, f)
        file_size = os.path.getsize(file_path)
        print(f"   - {f}: {file_size} bytes")

    # Gerar ZIP
    print("\n📦 Gerando ZIP...")
    nome_arquivo = processor.gerar_nome_relatorio(False)
    print(f"   Nome do relatório: {nome_arquivo}")

    zip_path, success = gerar_zip_de_relatorio(output_dir, nome_arquivo)

    if not success:
        print("\n❌ Falha ao criar ZIP")
        return False

    print("\n✅ ZIP criado com sucesso!")

    # Verificar ZIP
    print("\n🔍 Verificando conteúdo final do ZIP...")
    try:
        with zipfile.ZipFile(zip_path, "r") as zipf:
            items = zipf.namelist()
            if len(items) == 0:
                print("❌ ZIP está vazio!")
                return False
            print(f"✅ ZIP contém {len(items)} arquivos")
    except Exception:
        print("❌ Não foi possível abrir o ZIP")
        return False

    print("\n✅ TESTE COMPLETO PASSOU!")
    print("\n📁 Arquivos gerados em:")
    print(f"   Processamento: {output_dir}/")
    print(f"   ZIP: {zip_path}")

    return True


if __name__ == "__main__":
    print("\n🧪 TESTE INTEGRADO: Processamento Real + ZIP\n")

    try:
        success = test_full_processing()

        print("\n" + "=" * 70)
        if success:
            print("🎉 TESTE PASSOU!")
            print("=" * 70)
            sys.exit(0)
        else:
            print("❌ TESTE FALHOU")
            print("=" * 70)
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ Erro crítico: {e}")
        traceback.print_exc()
        sys.exit(1)
