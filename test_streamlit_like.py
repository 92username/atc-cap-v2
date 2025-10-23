#!/usr/bin/env python3
import os
import sys
import tempfile
import shutil
import zipfile
from pathlib import Path
import asyncio
import time
import uuid
from datetime import datetime
sys.path.insert(0, '/app')

from tatic_processor import TATICProcessor

async def test_streamlit_like_processing():
    # Simular o que acontece na aplicação Streamlit
    print('Iniciando teste similar ao Streamlit...')

    # Usar Path.cwd() como na aplicação
    base_dir = Path.cwd()
    print(f'Base dir: {base_dir}')

    # Criar job_id como na aplicação
    job_id = f'job_{datetime.now().strftime("%Y%m%d%H%M%S")}_{uuid.uuid4().hex[:8]}'
    print(f'Job ID: {job_id}')

    # Criar diretórios como na aplicação
    upload_dir_rel = os.path.join('uploads', job_id)
    upload_dir = base_dir / upload_dir_rel
    upload_dir.mkdir(parents=True, exist_ok=True)

    output_dir_rel = os.path.join('outputs', job_id)
    output_dir = base_dir / output_dir_rel
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f'Upload dir: {upload_dir}')
    print(f'Output dir: {output_dir}')

    # Copiar arquivo de exemplo para upload_dir
    sample_file = Path('/app/assets/DataGrid-sbjr.xlsx')
    if sample_file.exists():
        file_path = upload_dir / 'uploaded_file.xlsx'
        shutil.copy2(sample_file, file_path)
        print(f'Arquivo copiado para: {file_path}')

        # Criar processador como na aplicação
        processor = TATICProcessor(
            usar_categoria_h=False,
            incluir_finais_de_semana=False,
            log_callback=print
        )

        # Processar dados
        print('Iniciando processamento...')
        resultado = await processor.process_tatic_data(file_path, output_dir)
        print('Processamento concluído!')

        # Pequeno delay como na aplicação
        time.sleep(1)

        # Verificar arquivos gerados
        output_dir_str = str(output_dir)
        print(f'Verificando arquivos em: {output_dir_str}')
        if os.path.exists(output_dir_str):
            files_in_dir = list(os.listdir(output_dir_str))
            print(f'Arquivos encontrados: {len(files_in_dir)}')
            for f in files_in_dir:
                file_path_check = os.path.join(output_dir_str, f)
                file_size = os.path.getsize(file_path_check)
                print(f'   - {f}: {file_size} bytes')
        else:
            print(f'ERRO: Diretório não existe: {output_dir_str}')

        # Gerar nome do relatório
        nome_arquivo = processor.gerar_nome_relatorio(False)
        print(f'Nome do relatório: {nome_arquivo}')

        # Criar ZIP como na aplicação
        def gerar_zip_de_relatorio(job_output_dir: str, nome_arquivo: str):
            job_output_dir = str(job_output_dir).strip()
            parent_dir = str(Path(job_output_dir).parent)
            zip_path = os.path.join(parent_dir, nome_arquivo)

            print(f'[DEBUG ZIP] job_output_dir: {job_output_dir}')
            print(f'[DEBUG ZIP] zip_path: {zip_path}')
            print(f'[DEBUG ZIP] job_output_dir existe? {os.path.exists(job_output_dir)}')

            arquivos_encontrados = 0
            if os.path.exists(job_output_dir):
                for root, _dirs, files in os.walk(job_output_dir):
                    for file in files:
                        full_path = os.path.join(root, file)
                        size = os.path.getsize(full_path)
                        print(f'[DEBUG ZIP] - {file} ({size} bytes)')
                        arquivos_encontrados += 1

            if arquivos_encontrados == 0:
                print('[DEBUG ZIP] Nenhum arquivo encontrado!')
                return zip_path

            files_added = 0
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _dirs, files in os.walk(job_output_dir):
                    for file in files:
                        if not file.endswith('.zip'):
                            abs_path = os.path.join(root, file)
                            rel_path = os.path.relpath(abs_path, job_output_dir)
                            zipf.write(abs_path, arcname=rel_path)
                            print(f'[DEBUG ZIP] Adicionado: {rel_path}')
                            files_added += 1

            print(f'ZIP criado: {zip_path}')
            if os.path.exists(zip_path):
                file_size = os.path.getsize(zip_path)
                print(f'Tamanho do ZIP: {file_size} bytes')

                with zipfile.ZipFile(zip_path, 'r') as zipf:
                    items = zipf.namelist()
                    print(f'Arquivos no ZIP: {len(items)}')
                    for item in items:
                        info = zipf.getinfo(item)
                        print(f'  - {item} ({info.file_size} bytes)')

            return zip_path

        # Gerar ZIP
        relatorio_zip_path = gerar_zip_de_relatorio(str(output_dir), nome_arquivo)
        print(f'ZIP final: {relatorio_zip_path}')

    else:
        print(f'Arquivo de exemplo não encontrado: {sample_file}')

if __name__ == '__main__':
    asyncio.run(test_streamlit_like_processing())</content>
<parameter name="filePath">/home/nbx/Projects/jacare/atc-cap-v2/test_streamlit_like.py