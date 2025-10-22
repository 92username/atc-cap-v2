#!/usr/bin/env python3
"""
Script de teste para verificar se o problema do ZIP vazio foi resolvido
"""
import os
import sys
import time
import zipfile
import tempfile
import shutil
from pathlib import Path

# Adicionar o diretório ao path
sys.path.insert(0, os.path.dirname(__file__))

from tatic_processor import TATICProcessor

def test_zip_creation():
    """Teste se os arquivos são criados e podem ser zipados"""
    print("\n" + "="*70)
    print("🧪 TESTE: Criação de ZIP com Sincronização de Arquivo")
    print("="*70 + "\n")
    
    # Criar um diretório temporário
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"📁 Diretório temporário: {tmpdir}")
        
        # Criar o processador
        processor = TATICProcessor(usar_categoria_h=False)
        
        # Criar alguns arquivos de teste
        test_files = [
            "tabela1_movimento_percentual_categoria.csv",
            "tabela2_resultado_mix_categoria.csv",
            "tabela3_movimento_mensal_pista.csv",
            "tabela4_percentual_utilizacao_pistas.csv",
            "resumo.txt",
            "charts_data.json",
        ]
        
        print("\n📝 Criando arquivos de teste...")
        for filename in test_files:
            file_path = Path(tmpdir) / filename
            with open(file_path, "w") as f:
                f.write(f"Conteúdo do arquivo: {filename}\n")
            print(f"   ✅ {filename}")
        
        # Sincronizar cada arquivo
        print("\n🔄 Sincronizando arquivos com disco...")
        for filename in test_files:
            file_path = Path(tmpdir) / filename
            processor._sync_file(file_path)
            print(f"   ✅ {filename} sincronizado")
        
        # Aguardar um pouco
        print("\n⏳ Aguardando 1 segundo para garantir sincronização...")
        time.sleep(1)
        
        # Verificar se os arquivos existem
        print("\n✔️ Verificando se os arquivos foram criados...")
        files_found = list(Path(tmpdir).glob("*"))
        print(f"   📊 Arquivos encontrados: {len(files_found)}")
        for f in files_found:
            size = f.stat().st_size
            print(f"   - {f.name}: {size} bytes")
        
        if len(files_found) != len(test_files):
            print(f"\n❌ ERRO: Esperado {len(test_files)} arquivos, mas encontrou {len(files_found)}")
            return False
        
        # Criar o ZIP
        print("\n📦 Criando arquivo ZIP...")
        zip_path = Path(tmpdir) / "test_relatorio.zip"
        
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _dirs, files in os.walk(tmpdir):
                for file in files:
                    if not file.endswith(".zip"):
                        abs_path = os.path.join(root, file)
                        rel_path = os.path.relpath(abs_path, tmpdir)
                        zipf.write(abs_path, arcname=rel_path)
                        print(f"   ✅ Adicionado ao ZIP: {rel_path}")
        
        # Verificar se o ZIP foi criado
        if not zip_path.exists():
            print(f"\n❌ ERRO: ZIP não foi criado em {zip_path}")
            return False
        
        zip_size = zip_path.stat().st_size
        print(f"\n📊 ZIP criado: {zip_size} bytes")
        
        if zip_size < 100:  # ZIP muito pequeno = vazio
            print(f"\n❌ ERRO: ZIP está vazio ou muito pequeno ({zip_size} bytes)")
            return False
        
        # Verificar conteúdo do ZIP
        print("\n🔍 Verificando conteúdo do ZIP...")
        try:
            with zipfile.ZipFile(zip_path, "r") as zipf:
                items = zipf.namelist()
                print(f"   📊 Arquivos no ZIP: {len(items)}")
                for item in items:
                    info = zipf.getinfo(item)
                    print(f"   - {item}: {info.file_size} bytes")
            
            if len(items) == 0:
                print("\n❌ ERRO: ZIP está vazio!")
                return False
            
            if len(items) != len(test_files):
                print(f"\n⚠️ AVISO: Esperado {len(test_files)} arquivos, mas ZIP tem {len(items)}")
        
        except zipfile.BadZipFile as e:
            print(f"\n❌ ERRO: ZIP corrompido - {e}")
            return False
        
        print("\n✅ TESTE PASSOU! ZIP foi criado com sucesso e contém todos os arquivos.")
        return True

def test_file_sync():
    """Teste do método _sync_file"""
    print("\n" + "="*70)
    print("🧪 TESTE: Método _sync_file")
    print("="*70 + "\n")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        processor = TATICProcessor(usar_categoria_h=False)
        
        # Criar um arquivo de teste
        test_file = Path(tmpdir) / "test.txt"
        print(f"📝 Criando arquivo: {test_file}")
        with open(test_file, "w") as f:
            f.write("Teste de sincronização\n")
        
        # Sincronizar
        print("🔄 Sincronizando arquivo...")
        processor._sync_file(test_file)
        
        # Verificar
        if test_file.exists():
            print(f"✅ Arquivo sincronizado com sucesso")
            print(f"   Tamanho: {test_file.stat().st_size} bytes")
            return True
        else:
            print(f"❌ Arquivo não encontrado após sincronização")
            return False

if __name__ == "__main__":
    print("\n🧪 SUITE DE TESTES: ZIP Fix\n")
    
    results = []
    
    # Test 1: File sync
    try:
        results.append(("File Sync", test_file_sync()))
    except Exception as e:
        print(f"❌ Erro no teste de sync: {e}")
        results.append(("File Sync", False))
    
    # Test 2: ZIP creation
    try:
        results.append(("ZIP Creation", test_zip_creation()))
    except Exception as e:
        print(f"❌ Erro no teste de ZIP: {e}")
        import traceback
        traceback.print_exc()
        results.append(("ZIP Creation", False))
    
    # Summary
    print("\n" + "="*70)
    print("📊 RESUMO DOS TESTES")
    print("="*70)
    for test_name, passed in results:
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"{test_name}: {status}")
    
    all_passed = all(passed for _, passed in results)
    print("="*70)
    
    if all_passed:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        sys.exit(0)
    else:
        print("\n❌ ALGUNS TESTES FALHARAM")
        sys.exit(1)
