import streamlit as st
import os
import uuid
from datetime import datetime
from tatic_processor import TATICProcessor
import pandas as pd
from pathlib import Path
import zipfile
import datetime

# Configuração de página
st.set_page_config(
    page_title="TATIC Análise de Dados",
    page_icon="🛫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuração inicial do Streamlit
st.title("TATIC Análise de Dados")
st.write("Faça upload de um arquivo .xlsx para processar os dados TATIC.")

# 🧭 Menu lateral
with st.sidebar:
    menu = st.selectbox("Menu", ["🧭 Como usar o app", "📜 Histórico", "ℹ️ Sobre"])
    
    if menu == "🧭 Como usar o app":
        st.header("🧭 Como usar o app")
        st.markdown("""
        1. **Extraia o relatório do TATIC (.xlsx)**  
           Certifique-se de que as colunas estejam nomeadas assim:

           - **H.Evento** → horário UTC do evento (pouso, decolagem, etc.)  
           - **Indicativo** → prefixo ou matrícula da aeronave  
           - **Evento** → tipo de evento (ARR, DEP, etc.)  
           - **Num. Evento**   
           - **Origem / Destino**   
           - **Equipamento** → modelo ou tipo da aeronave  
           - **TV** → tipo de voo  
           - **Pista** → cabeceira utilizada (ex: 03 ou 21)  
           - **RV** → regra de voo (VFR / IFR)  
           - **Operador Evento** →   

        2. **Não altere os nomes das colunas.**  
           O app depende dessa estrutura para identificar corretamente os dados.

        3. **Faça o upload do arquivo .xlsx** clicando em "Browse files" ou arrastando o arquivo para a área de upload.

        4. **Aguarde o processamento.**  
           O log mostrará o andamento passo a passo.  Pode levar de 1 a 3 minutos, dependendo do tamanho do arquivo.

        5. **Baixe o relatório (.ZIP)** quando o botão estiver disponível.

        ---
        ⚠️ *Dica:* Use sempre o relatório original do TATIC, sem formatações ou filtros no Excel.
        """)
    
    elif menu == "📜 Histórico":
        st.header("📜 Histórico de Relatórios")
        st.info("Esta funcionalidade será implementada em breve!")
    
    elif menu == "ℹ️ Sobre":
        st.header("ℹ️ Sobre o App")
        st.info("Esta funcionalidade será implementada em breve!")

# 🚁 Seletor de classificação de helicópteros
st.write("### Classificação de Helicópteros")
categoria_helicoptero = st.radio(
    "Como classificar helicópteros?",
    options=["Usar categoria original (A-E)", "Usar categoria H (Helicopter)"],
    index=0,
    help="Escolha se helicópteros devem ser classificados em suas categorias originais (A-E) ou em uma categoria especial 'H'."
)
usar_categoria_H = categoria_helicoptero == "Usar categoria H (Helicopter)"

# �📤 Upload do arquivo
uploaded_file = st.file_uploader("Envie o arquivo TATIC (.xlsx)", type=["xlsx"])

# Função para gerar o arquivo ZIP
def gerar_zip_de_relatorio(job_output_dir: str, nome_arquivo: str):
    zip_path = os.path.join("outputs", nome_arquivo)
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for filename in os.listdir(job_output_dir):
            file_path = os.path.join(job_output_dir, filename)
            if os.path.isfile(file_path) and not filename.endswith('.zip'):
                zipf.write(file_path, arcname=filename)
    return zip_path

if uploaded_file is not None:
    # Gerar um job_id único
    job_id = f"job_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
    upload_dir = os.path.join("uploads", job_id)
    os.makedirs(upload_dir, exist_ok=True)

    # Salvar o arquivo enviado
    file_path = os.path.join(upload_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"Arquivo salvo em: {file_path}")

    # ⚙️ Processamento
    # Sistema de logs em tempo real
    log_placeholder = st.empty()
    log_lines = []
    
    def streamlit_logger(msg):
        log_lines.append(msg)
        log_placeholder.code("\n".join(log_lines), language="bash")
    
    processor = TATICProcessor(usar_categoria_H=usar_categoria_H, log_callback=streamlit_logger)
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
        nome_arquivo = processor.gerar_nome_relatorio(usar_categoria_H)
        relatorio_zip_path = gerar_zip_de_relatorio(str(output_dir), nome_arquivo)
        
        # Exibir mensagem de sucesso com o nome do arquivo
        st.success(f"✅ Relatório gerado: {nome_arquivo}")

        # 📊 Exibição de resultados
        st.write("### Resultados")
        for csv_file in os.listdir(output_dir):
            if csv_file.endswith(".csv"):
                st.write(f"#### {csv_file}")
                st.dataframe(pd.read_csv(os.path.join(output_dir, csv_file)))

        # 📥 Download do ZIP
        if os.path.exists(relatorio_zip_path):
            with open(relatorio_zip_path, "rb") as f:
                st.download_button(
                    label="Baixar Relatório (ZIP)",
                    data=f,
                    file_name="relatorio.zip",
                    mime="application/zip"
                )
        else:
            st.error("Relatório não encontrado. Verifique se o processamento foi concluído corretamente.")

    except Exception as e:
        st.error(f"Erro durante o processamento: {e}")