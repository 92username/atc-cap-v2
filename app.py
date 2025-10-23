import os
import uuid
import zipfileimport logging
import threading
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from tatic_processor import TATICProcessor
from aeronaves_dict import atualizar_dicionario

# Configuração de página
st.set_page_config(
    page_title="TATIC Análise de Dados",
    page_icon="🛫",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Configuração de barra lateral
def add_sidebar():
    with st.sidebar:
        st.title("📊 TATIC - MCA 100-26")
        st.warning(
            "⚠️ **Dica:** Exporte os dados diretamente do TATIC em formato bruto, sem aplicar filtros ou fórmulas personalizadas. O aplicativo foi otimizado para processar dados não modificados, garantindo resultados conforme a MCA 100-26."
        )
        st.subheader("Como usar este app")

        st.markdown(
            """
        ### 📋 Instruções:
        1. **Selecione** se helicópteros devem ser classificados como categoria H
        2. **Faça upload** do arquivo TATIC (.xlsx)
        3. **Clique em "Gerar Relatório"** para processar os dados
        4. **Baixe o relatório** gerado em formato ZIP

        ### 📊 Formato MCA 100-26
        O relatório segue as especificações do **Anexo II da MCA 100-26** com as tabelas:
        - Tabela 1: Movimento percentual por categoria
        - Tabela 2: Resultado do mix
        - Tabela 3: Movimento mensal por pista
        - Tabela 4: Percentual de utilização de pistas
        """
        )

        st.divider()
        st.caption("© 2025 Tamanduas.dev")


add_sidebar()

# Interface principal
# Título com tag "Experimental" e tooltip
st.markdown(
    """
    <div style="display: flex; justify-content: center; align-items: center; gap: 12px; flex-wrap: wrap;">
        <h1 style="margin: 0; text-align: center;">🛫 Análise de Dados TATIC</h1>
        <span style="background-color: #fbdd41; color: #000; padding: 4px 10px; border-radius: 6px; font-weight: 600; font-size: 14px;">
            Experimental
        </span>
    </div>
""",
    unsafe_allow_html=True,
)

st.subheader("Processador de Dados de Movimento Aéreo")

st.info(
    """
Este aplicativo processa dados TATIC conforme as especificações do **Anexo II da MCA 100-26**.
Faça upload do arquivo Excel exportado do TATIC e obtenha as tabelas de análise.
"""
)

# 📊 Configurações
st.subheader("Configurações")
categoria_helicoptero = st.radio(
    "Classificação de Helicópteros:",
    ["Usar categorias padrão (A-E)", "Classificar como categoria H (Helicopter)"],
    index=1,
    help="Escolha como helicópteros devem ser classificados nas tabelas",
)

usar_categoria_h = categoria_helicoptero == "Classificar como categoria H (Helicopter)"

# Nova opção para incluir ou não finais de semana
incluir_finais_de_semana = (
    st.radio(
        "Quais dias incluir no relatório?",
        (
            "Listar apenas Segunda a Sexta (padrão da MCA 100-26)",
            "Listar Segunda a Domingo (incluir Sábado e Domingo)",
        ),
        index=0,
        help="Escolha se deseja incluir finais de semana na Tabela 1",
    )
    == "Listar Segunda a Domingo (incluir Sábado e Domingo)"
)

# �📤 Upload do arquivo
uploaded_file = st.file_uploader("Envie o arquivo TATIC (.xlsx)", type=["xlsx"])


# Função para gerar o arquivo ZIP
def gerar_zip_de_relatorio(job_output_dir: str, nome_arquivo: str):
    """
    Gera ZIP com todos os arquivos do job_output_dir
    Corrigido: cria o ZIP fora do diretório para evitar conflitos
    """
    zip_path = os.path.join("outputs", nome_arquivo)

    # DEBUG: Verificar arquivos disponíveis antes de zipar
    print(f"[DEBUG ZIP] Diretório: {job_output_dir}")
    print("[DEBUG ZIP] Arquivos antes de zipar:")
    if os.path.exists(job_output_dir):
        for root, _dirs, files in os.walk(job_output_dir):
            for file in files:
                print(f"[DEBUG ZIP] - {os.path.join(root, file)}")
    else:
        print(f"[DEBUG ZIP] Diretório {job_output_dir} não existe!")

    # Criar o ZIP com todos os arquivos
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _dirs, files in os.walk(job_output_dir):
            # Directory structure is traversed automatically by os.walk
            for file in files:
                if not file.endswith(".zip"):  # Evita incluir outros ZIPs
                    abs_path = os.path.join(root, file)
                    rel_path = os.path.relpath(abs_path, job_output_dir)
                    zipf.write(abs_path, arcname=rel_path)
                    print(f"[DEBUG ZIP] Adicionado ao ZIP: {rel_path}")

    # DEBUG: Verificar conteúdo do ZIP
    print(f"[DEBUG ZIP] Verificando ZIP {zip_path}:")
    if os.path.exists(zip_path):
        try:
            with zipfile.ZipFile(zip_path, "r") as zipf:
                for item in zipf.namelist():
                    print(f"[DEBUG ZIP] - {item}")
            print(f"[DEBUG ZIP] Tamanho do ZIP: {os.path.getsize(zip_path)} bytes")
        except zipfile.BadZipFile:
            print("[DEBUG ZIP] ERRO: ZIP vazio ou corrompido!")
    else:
        print("[DEBUG ZIP] ERRO: Arquivo ZIP não foi criado!")

    return zip_path


# Inicializar estado da sessão
if "relatorio_gerado" not in st.session_state:
    st.session_state.relatorio_gerado = False
    st.session_state.nome_arquivo = ""
    st.session_state.relatorio_zip_path = ""
    st.session_state.output_dir = ""

if uploaded_file is not None:
    st.success(f"✅ Arquivo carregado: {uploaded_file.name}")

    # 🚀 Botão para iniciar processamento
    if st.button("🚀 Gerar Relatório"):
        st.session_state.relatorio_gerado = False

        # Criar pasta temporária para o upload
        job_id = f"job_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
        upload_dir = os.path.join("uploads", job_id)
        os.makedirs(upload_dir, exist_ok=True)

        # Salvar o arquivo para processamento
        file_path = os.path.join(upload_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Ler DataFrame para atualização do dicionário
        df = pd.read_excel(file_path)

        # Atualiza o dicionário de aeronaves em background
        try:
            threading.Thread(target=atualizar_dicionario, args=(df,), daemon=True).start()
            logging.info("Thread de atualização do dicionário iniciada.")
        except Exception as e:
            logging.error(f"Falha ao iniciar thread de atualização do dicionário: {e}")

        # Inicializar processador
        processor = TATICProcessor(
            usar_categoria_h=usar_categoria_h,  # Corrected argument name
            incluir_finais_de_semana=incluir_finais_de_semana,
            log_callback=st.write,
        )

        # Criar diretório de saída
        output_dir = os.path.join("outputs", job_id)
        os.makedirs(output_dir, exist_ok=True)

        # Converter output_dir para Path
        output_dir = Path(output_dir)

        # Substituir o método de processamento para usar `process_tatic_data`
        try:
            with st.spinner("Processando os dados..."):
                import asyncio

                asyncio.run(processor.process_tatic_data(file_path, output_dir))

            st.success("Processamento concluído!")

            # Gerar nome do relatório e arquivo ZIP
            nome_arquivo = processor.gerar_nome_relatorio(usar_categoria_h)
            relatorio_zip_path = gerar_zip_de_relatorio(str(output_dir), nome_arquivo)

            # Salvar no estado da sessão
            st.session_state.relatorio_gerado = True
            st.session_state.nome_arquivo = nome_arquivo
            st.session_state.relatorio_zip_path = relatorio_zip_path
            st.session_state.output_dir = str(output_dir)

            # Exibir mensagem de sucesso com o nome do arquivo
            st.success(f"✅ Relatório gerado: {nome_arquivo}")

        except Exception as e:
            st.error(f"Erro durante o processamento: {e}")
            st.session_state.relatorio_gerado = False

# Botão de download se o relatório estiver pronto
if st.session_state.relatorio_gerado:
    # Verificar se o arquivo ainda existe
    if os.path.exists(st.session_state.relatorio_zip_path):
        with open(st.session_state.relatorio_zip_path, "rb") as file:
            st.download_button(
                label="📥 Baixar Relatório",
                data=file,
                file_name=st.session_state.nome_arquivo,
                mime="application/zip",
            )

        # Adicionar informações sobre o relatório
        st.info(
            f"""
        **💾 Relatório**: {st.session_state.nome_arquivo}

        📊 Conforme especificações MCA 100-26
        🚁 Categoria H para helicópteros: {"Ativada" if usar_categoria_h else "Desativada"}
        📅 Dias analisados na Tabela 1: {"Segunda a Domingo (incluindo finais de semana)" if incluir_finais_de_semana else "Segunda a Sexta (padrão MCA 100-26)"}
        """
        )
    else:
        st.error("⚠️ Arquivo de relatório não encontrado. Por favor, gere novamente.")
