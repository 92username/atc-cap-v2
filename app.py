import os
import time
import uuid
import zipfile
from datetime import datetime
from pathlib import Path

import streamlit as st

from tatic_processor import TATICProcessor

# Configuração de página (DEVE SER PRIMEIRO)
st.set_page_config(
    page_title="TATIC Análise de Dados",
    page_icon="🛫",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================================
# PARALELISMO COM PANDARALLEL
# ============================================================================
# Inicializar pandarallel para usar os 2 núcleos disponíveis da VPS
try:
    from pandarallel import pandarallel

    pandarallel.initialize(nb_workers=2, progress_bar=True, verbose=0)
    parallel_enabled = True
except ImportError:
    parallel_enabled = False
    # Pandarallel não disponível — fallback para modo sequencial


# Configuração de barra lateral
def add_sidebar():
    with st.sidebar:
        st.title("📊 TATIC - MCA 100-26")

        # Bloco fixo com dica importante em destaque amarelo âmbar
        st.markdown(
            """
            <div style="
                background-color: rgba(255, 193, 7, 0.15);
                border: 2px solid rgba(255, 193, 7, 0.5);
                border-radius: 8px;
                padding: 16px;
                margin-bottom: 8px;
            ">
                <h4 style="margin-top: 0; color: #ffa025;">💡 Dica:</h4>
                <p style="margin-bottom: 0;">
                    Exporte os dados <strong>diretamente do TATIC</strong> em formato bruto, sem aplicar filtros ou fórmulas.
                    O aplicativo foi otimizado para processar dados não modificados, garantindo resultados conforme a <strong>MCA 100-26</strong>.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        # Dropdown 1: Como exportar o arquivo do TATIC
        with st.expander("📂 Como exportar o arquivo do TATIC"):
            st.markdown(
                """
                ### No Saipher – TATIC (Módulo Supervisor):

                **1️⃣ Abra o menu principal**
                🧭 *Consultas → Pesquisa Operacional → Movimentos*

                **2️⃣ Selecione o período de análise**
                📅 Escolha o intervalo que cubra **12 meses**, conforme a **MCA 100-26**.

                **3️⃣ Execute a consulta**
                ▶️ Clique em **EXECUTAR** e aguarde o processamento do relatório.

                **4️⃣ Exporte o resultado**
                ⋮ No canto **superior direito**, clique nos **três pontinhos (⋮)**
                e escolha **"Exportar para Excel"**.

                ⚠️ **Observação:** Você pode alterar o nome do arquivo gerado, por ex.: SBJR_Dez2024_Dez2025.xlsx.
                """
            )

        # Dropdown 2: Como usar este app
        with st.expander("🧭 Como usar este app"):
            st.markdown(
                """
                ### 📋 Instruções de uso:

                1. **Selecione** se helicópteros devem ser classificados como categoria H
                2. **Faça upload** do arquivo TATIC (.xlsx)
                3. **Clique em "Gerar Relatório"** para processar os dados
                4. **Baixe o relatório** gerado em formato ZIP

                ### 📊 Formato MCA 100-26

                O relatório segue as especificações do **Anexo II da MCA 100-26** com as tabelas:
                - **Tabela 1:** Movimento percentual por categoria
                - **Tabela 2:** Resultado do mix
                - **Tabela 3:** Movimento mensal por pista
                - **Tabela 4:** Percentual de utilização de pistas
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
    
    Args:
        job_output_dir: Caminho ABSOLUTO para o diretório de saída
        nome_arquivo: Nome do arquivo ZIP (ex: relatorio_0001_15102025_STD.zip)
    
    Returns:
        Caminho ABSOLUTO para o arquivo ZIP criado
    """
    # 🔧 CRÍTICO: Garantir que job_output_dir é um caminho válido
    job_output_dir = str(job_output_dir).strip()
    
    # Criar ZIP no mesmo diretório que os arquivos de saída
    # Pegar o parent dir (remover job_id) para colocar ZIP em outputs/
    parent_dir = str(Path(job_output_dir).parent)
    zip_path = os.path.join(parent_dir, nome_arquivo)
    
    print(f"[DEBUG ZIP] job_output_dir: {job_output_dir}")
    print(f"[DEBUG ZIP] zip_path: {zip_path}")
    print(f"[DEBUG ZIP] job_output_dir existe? {os.path.exists(job_output_dir)}")
    print(f"[DEBUG ZIP] job_output_dir é absoluto? {os.path.isabs(job_output_dir)}")

    # DEBUG: Verificar arquivos disponíveis antes de zipar
    print("[DEBUG ZIP] Arquivos antes de zipar:")
    arquivos_encontrados = 0
    if os.path.exists(job_output_dir):
        for root, _dirs, files in os.walk(job_output_dir):
            for file in files:
                full_path = os.path.join(root, file)
                size = os.path.getsize(full_path)
                print(f"[DEBUG ZIP] - {file} ({size} bytes)")
                arquivos_encontrados += 1
    else:
        print(f"[DEBUG ZIP] ❌ ERRO: Diretório {job_output_dir} não existe!")
        return zip_path

    if arquivos_encontrados == 0:
        print("[DEBUG ZIP] ⚠️ AVISO: Nenhum arquivo encontrado no diretório!")

    # Criar o ZIP com todos os arquivos
    files_added = 0
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _dirs, files in os.walk(job_output_dir):
            for file in files:
                if not file.endswith(".zip"):  # Evita incluir outros ZIPs
                    abs_path = os.path.join(root, file)
                    rel_path = os.path.relpath(abs_path, job_output_dir)
                    zipf.write(abs_path, arcname=rel_path)
                    print(f"[DEBUG ZIP] ✅ Adicionado ao ZIP: {rel_path}")
                    files_added += 1

    # DEBUG: Verificar conteúdo do ZIP
    print(f"\n[DEBUG ZIP] Verificando ZIP {zip_path}:")
    if os.path.exists(zip_path):
        try:
            with zipfile.ZipFile(zip_path, "r") as zipf:
                items = zipf.namelist()
                print(f"[DEBUG ZIP] Total de arquivos no ZIP: {len(items)}")
                for item in items:
                    info = zipf.getinfo(item)
                    print(f"[DEBUG ZIP] - {item} ({info.file_size} bytes)")
            
            file_size = os.path.getsize(zip_path)
            print(f"[DEBUG ZIP] Tamanho total do ZIP: {file_size} bytes")

            # ⚠️ AVISO: Se ZIP tem menos de 100 bytes, está praticamente vazio
            if file_size < 100:
                print(f"[DEBUG ZIP] ⚠️ AVISO: ZIP vazio ou quase vazio!")
                print(f"[DEBUG ZIP]    Arquivos adicionados: {files_added}")
                print(f"[DEBUG ZIP]    Arquivos encontrados no diretório: {arquivos_encontrados}")
        except zipfile.BadZipFile:
            print("[DEBUG ZIP] ❌ ERRO: ZIP vazio ou corrompido!")
    else:
        print("[DEBUG ZIP] ❌ ERRO: Arquivo ZIP não foi criado!")

    print(f"[DEBUG ZIP] Retornando: {zip_path}\n")
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
        # ⏱️ Iniciar cronômetro do clique do usuário
        tempo_inicio = time.time()

        st.session_state.relatorio_gerado = False

        # Criar pasta temporária para o upload
        job_id = f"job_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        # 🔧 CRÍTICO: Usar caminhos ABSOLUTOS para evitar problemas em Docker
        base_dir = Path.cwd()  # Diretório de trabalho do app
        upload_dir_rel = os.path.join("uploads", job_id)
        upload_dir = base_dir / upload_dir_rel
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        st.write(f"[DEBUG] Base dir: {base_dir}")
        st.write(f"[DEBUG] Upload dir: {upload_dir}")

        # Salvar o arquivo para processamento
        file_path = upload_dir / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Inicializar processador
        processor = TATICProcessor(
            usar_categoria_h=usar_categoria_h,  # Corrected argument name
            incluir_finais_de_semana=incluir_finais_de_semana,
            log_callback=st.write,
        )

        # Criar diretório de saída com caminho ABSOLUTO
        output_dir_rel = os.path.join("outputs", job_id)
        output_dir = base_dir / output_dir_rel
        output_dir.mkdir(parents=True, exist_ok=True)
        
        st.write(f"[DEBUG] Output dir: {output_dir}")

        # Substituir o método de processamento para usar `process_tatic_data`
        try:
            with st.spinner("Processando os dados... pode demorar até 3 minutos."):
                import asyncio

                resultado = asyncio.run(processor.process_tatic_data(file_path, output_dir))

            st.success("Processamento concluído!")

            # ⏱️ Calcular tempo total desde o clique do usuário
            tempo_total = time.time() - tempo_inicio
            st.info(f"⏳ Tempo decorrido: {tempo_total:.2f} segundos")

            # 🔧 CRÍTICO: Pequeno delay para garantir que todos os arquivos foram
            # sincronizados com o disco pelo sistema operacional
            time.sleep(1)

            # 🔍 DEBUG: Verificar se os arquivos foram realmente criados
            output_dir_str = str(output_dir)
            st.write(f"\n[DEBUG APP] Verificando arquivos em: {output_dir_str}")
            if os.path.exists(output_dir_str):
                files_in_dir = list(os.listdir(output_dir_str))
                st.write(f"[DEBUG APP] Arquivos encontrados: {len(files_in_dir)}")
                for f in files_in_dir:
                    file_path_check = os.path.join(output_dir_str, f)
                    file_size = os.path.getsize(file_path_check)
                    st.write(f"[DEBUG APP]   - {f}: {file_size} bytes")
            else:
                st.write(f"[DEBUG APP] ERRO: Diretório não existe: {output_dir_str}")

            # Gerar nome do relatório e arquivo ZIP
            nome_arquivo = processor.gerar_nome_relatorio(usar_categoria_h)
            st.write(f"[DEBUG] Chamando gerar_zip_de_relatorio com: {output_dir_str}")
            relatorio_zip_path = gerar_zip_de_relatorio(str(output_dir), nome_arquivo)
            st.write(f"[DEBUG] ZIP criado em: {relatorio_zip_path}")

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
