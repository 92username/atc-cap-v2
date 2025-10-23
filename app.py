import io
import os
import time
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile

import streamlit as st

from paths import OUTPUT_DIR, ensure_output_dir
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


def gerar_zip_de_relatorio(job_output_dir: Path, nome_arquivo: str, persist_path: Path | None = None) -> bytes:
    """Generate an in-memory ZIP archive for the given job directory."""
    job_output_dir = Path(job_output_dir)

    if not job_output_dir.exists():
        raise FileNotFoundError(f"Diretório de saída não encontrado: {job_output_dir}")

    buffer = io.BytesIO()
    with ZipFile(buffer, "w") as zip_buffer:
        for file_path in sorted(job_output_dir.rglob("*")):
            if not file_path.is_file():
                continue
            if file_path.suffix.lower() == ".zip":
                # Evita incluir ZIPs previamente gerados
                continue
            rel_path = file_path.relative_to(job_output_dir)
            zip_buffer.writestr(str(rel_path), file_path.read_bytes())

    buffer.seek(0)
    zip_bytes = buffer.getvalue()

    default_path = job_output_dir.parent / nome_arquivo

    persist_targets = [default_path]
    if persist_path is not None:
        persist_targets.append(persist_path)

    for target in persist_targets:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(zip_bytes)

    return zip_bytes


# Inicializar estado da sessão
if "relatorio_gerado" not in st.session_state:
    st.session_state.relatorio_gerado = False
    st.session_state.nome_arquivo = ""
    st.session_state.relatorio_zip_bytes = b""
    st.session_state.output_dir = ""
    st.session_state.job_id = ""
    st.session_state.zip_persist_path = ""

if uploaded_file is not None:
    st.success(f"✅ Arquivo carregado: {uploaded_file.name}")

    # 🚀 Botão para iniciar processamento
    if st.button("🚀 Gerar Relatório"):
        tempo_inicio = time.time()
        st.session_state.relatorio_gerado = False

        base_dir = ensure_output_dir()
        job_id = time.strftime("job_%Y%m%d%H%M%S")
        job_dir = base_dir / job_id
        upload_dir = job_dir / "inputs"
        output_dir = job_dir / "outputs"
        upload_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)

        st.write(f"[DEBUG] OUTPUT_DIR configurado: {os.getenv('OUTPUT_DIR', str(OUTPUT_DIR))}")
        st.write(f"[DEBUG] OUTPUT_DIR efetivo: {base_dir}")
        st.write(f"[DEBUG] Job dir: {job_dir}")

        upload_path = upload_dir / uploaded_file.name
        with open(upload_path, "wb") as uploaded_dest:
            uploaded_dest.write(uploaded_file.getbuffer())

        processor = TATICProcessor(
            usar_categoria_h=usar_categoria_h,
            incluir_finais_de_semana=incluir_finais_de_semana,
            log_callback=st.write,
        )

        try:
            with st.spinner("Processando os dados... pode demorar até 3 minutos."):
                import asyncio

                asyncio.run(processor.process_tatic_data(upload_path, output_dir))

            st.success("Processamento concluído!")

            tempo_total = time.time() - tempo_inicio
            st.info(f"⏳ Tempo decorrido: {tempo_total:.2f} segundos")

            time.sleep(1)

            st.write(f"\n[DEBUG APP] Arquivos gerados em: {output_dir}")
            generated_files = list(output_dir.glob("*"))
            st.write(f"[DEBUG APP] Arquivos encontrados: {len(generated_files)}")
            for generated in generated_files:
                if generated.is_file():
                    st.write(f"[DEBUG APP]   - {generated.name}: {generated.stat().st_size} bytes")

            nome_arquivo = processor.gerar_nome_relatorio(usar_categoria_h)
            persist_path = job_dir / f"{job_id}.zip"
            zip_bytes = gerar_zip_de_relatorio(output_dir, nome_arquivo, persist_path=persist_path)

            st.session_state.relatorio_gerado = True
            st.session_state.nome_arquivo = nome_arquivo
            st.session_state.relatorio_zip_bytes = zip_bytes
            st.session_state.output_dir = str(output_dir)
            st.session_state.job_id = job_id
            st.session_state.zip_persist_path = str(persist_path)

            st.success(f"✅ Relatório gerado: {nome_arquivo}")

        except Exception as e:
            st.error(f"Erro durante o processamento: {e}")
            st.session_state.relatorio_gerado = False

# Botão de download se o relatório estiver pronto
if st.session_state.relatorio_gerado:
    zip_bytes = st.session_state.get("relatorio_zip_bytes", b"")
    if zip_bytes:
        st.download_button(
            label="📥 Baixar Relatório",
            data=zip_bytes,
            file_name=f"{st.session_state.job_id}.zip",
            mime="application/zip",
        )

        st.info(
            f"""
        **💾 Relatório**: {st.session_state.nome_arquivo}

        📊 Conforme especificações MCA 100-26
        🚁 Categoria H para helicópteros: {"Ativada" if usar_categoria_h else "Desativada"}
        📅 Dias analisados na Tabela 1: {"Segunda a Domingo (incluindo finais de semana)" if incluir_finais_de_semana else "Segunda a Sexta (padrão MCA 100-26)"}
        """
        )
    else:
        st.error("⚠️ Dados do relatório não encontrados. Por favor, gere novamente.")
