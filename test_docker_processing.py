#!/usr/bin/env python3
import os
import sys
import tempfile
import shutil
import zipfile
from pathlib import Path
sys.path.insert(0, '/app')

from tatic_processor import TATICProcessor

def test_docker_processing():
    # Criar diretório temporário para teste
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        output_dir = temp_path / 'outputs'
        output_dir.mkdir()

        # Criar processador
        processor = TATICProcessor(usar_categoria_h=False)

        # Simular processamento completo
        print('Iniciando processamento completo no Docker...')

        # Usar dados de teste
        sample_file = Path('/app/assets/DataGrid-sbjr.xlsx')
        if sample_file.exists():
            print(f'Processando arquivo de exemplo: {sample_file}')

            # Processar dados
            job_id = 'test_job_docker_123'
            processor.process_tatic_data(
                str(sample_file),
                str(output_dir),
                job_id,
                lambda msg: print(f'LOG: {msg}')
            )

            # Verificar arquivos gerados
            job_output_dir = output_dir / job_id
            if job_output_dir.exists():
                files = list(job_output_dir.glob('*.csv'))
                print(f'Arquivos CSV gerados: {len(files)}')
                for f in files:
                    print(f'  - {f.name} ({f.stat().st_size} bytes)')

                # Criar ZIP
                zip_path = temp_path / 'test_report.zip'
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for csv_file in files:
                        zipf.write(csv_file, csv_file.name)

                print(f'ZIP criado: {zip_path}')
                print(f'Tamanho do ZIP: {zip_path.stat().st_size} bytes')

                # Verificar conteúdo do ZIP
                with zipfile.ZipFile(zip_path, 'r') as zipf:
                    zip_files = zipf.namelist()
                    print(f'Arquivos no ZIP: {len(zip_files)}')
                    for f in zip_files:
                        print(f'  - {f}')
            else:
                print('Diretório de saída não foi criado')
        else:
            print(f'Arquivo de exemplo não encontrado: {sample_file}')

        print('Teste concluído')

if __name__ == '__main__':
    test_docker_processing()</content>
<parameter name="filePath">/home/nbx/Projects/jacare/atc-cap-v2/test_docker_processing.py