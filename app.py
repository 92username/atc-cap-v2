import os
import uuid
import zipfile
from datetime import datetime
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from tatic_processor import TATICProcessor

# Carregar variáveis de ambiente
load_dotenv()


def parse_emails(raw_env):
    """
    Função robusta para parsear e-mails de variáveis de ambiente.
    - Remove espaços indevidos
    - Faz split com segurança
    - Normaliza (lowercase + strip)
    - Retorna lista limpa
    """
    if not raw_env:
        return []
    # Garante separação correta mesmo que GitHub secrets inclua espaços
    parts = [
        email.strip().lower() for email in raw_env.replace(" ", "").split(",") if email
    ]
    return parts


ADMIN_EMAILS = parse_emails(os.getenv("ADMIN_EMAILS"))
ALLOWED_EMAILS = parse_emails(os.getenv("ALLOWED_EMAILS"))

AUTHORIZED_USERS = list(set(ADMIN_EMAILS + ALLOWED_EMAILS))


class GlobalLock:
    """Implementação simples de lock global baseada em arquivo"""

    LOCK_FILE = "tatic_processing.lock"
    TIMEOUT_SECONDS = 3600  # 1 hora de timeout para locks órfãos

    @classmethod
    def acquire(cls) -> bool:
        """Tenta adquirir o lock. Retorna True se sucesso, False se já existe."""
        if os.path.exists(cls.LOCK_FILE):
            # Verificar se é um lock antigo (stale)
            try:
                creation_time = os.path.getctime(cls.LOCK_FILE)
                if (datetime.now().timestamp() - creation_time) > cls.TIMEOUT_SECONDS:
                    # Lock expirado, remover e tentar adquirir novamente
                    os.remove(cls.LOCK_FILE)
                else:
                    return False
            except OSError:
                # Arquivo pode ter sido removido concorrentemente
                pass

        # Criar arquivo de lock
        try:
            with open(cls.LOCK_FILE, "w") as f:
                f.write(str(datetime.now().timestamp()))
            return True
        except OSError:
            return False

    @classmethod
    def release(cls):
        """Libera o lock removendo o arquivo."""
        try:
            if os.path.exists(cls.LOCK_FILE):
                os.remove(cls.LOCK_FILE)
        except OSError:
            pass

    @classmethod
    def is_locked(cls) -> bool:
        """Verifica se existe lock ativo (não expirado)"""
        if not os.path.exists(cls.LOCK_FILE):
            return False

        try:
            creation_time = os.path.getctime(cls.LOCK_FILE)
            if (datetime.now().timestamp() - creation_time) > cls.TIMEOUT_SECONDS:
                return False
            return True
        except OSError:
            return False


# Configuração de página
st.set_page_config(
    page_title="TATIC Análise de Dados",
    page_icon="🛫",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 🔐 Sistema de autenticação

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Acesso Restrito")
    user_email = st.text_input("Digite seu e-mail autorizado:")
    if st.button("Entrar"):
        if user_email.strip().lower() in AUTHORIZED_USERS:
            st.session_state.authenticated = True
            st.success("Acesso permitido. Bem-vindo!")
            st.rerun()
        else:
            st.error("Acesso negado. E-mail não autorizado.")
    st.stop()


# Configuração de barra lateral
def add_sidebar():
    with st.sidebar:
        st.title("📊 TATIC - MCA 100-26")

        # 🔍 DEBUG: Mostrar usuários autorizados
        st.subheader("🔍 DEBUG - Autenticação")
        st.write(f"**Total de usuários autorizados:** {len(AUTHORIZED_USERS)}")
        with st.expander("Ver lista completa"):
            if AUTHORIZED_USERS:
                for i, email in enumerate(AUTHORIZED_USERS, 1):
                    st.write(f"{i}. {email}")
            else:
                st.warning("⚠️ Nenhum usuário autorizado carregado!")
        st.divider()

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

# State para chave do uploader (para permitir reset)
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

# 📤 Upload do arquivo
uploaded_file = st.file_uploader(
    "Envie o arquivo TATIC (.xlsx)",
    type=["xlsx"],
    key=f"uploader_{st.session_state.uploader_key}",
)


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

    # Verificar lock global
    is_system_busy = GlobalLock.is_locked()
    if is_system_busy:
        st.warning("⚠️ O sistema está processando outro relatório. Aguarde...")

    # State para controlar o botão via callback
    if "processing" not in st.session_state:
        st.session_state.processing = False

    def start_processing():
        st.session_state.processing = True

    # Botão desabilitado se já estiver processando ou sistema ocupado
    button_disabled = st.session_state.processing or is_system_busy

    if st.button(
        "🚀 Gerar Relatório", disabled=button_disabled, on_click=start_processing
    ):
        # O processamento real acontece APÓS o rerun desencadeado pelo callback
        pass

    # Se estiver marcado como processando, executa a lógica
    if st.session_state.processing:
        if not GlobalLock.acquire():
            st.error("⚠️ O sistema está ocupado por outro usuário.")
            st.session_state.processing = False
        else:
            try:
                # Criar container para feedback visual enquanto processa
                status_container = st.empty()
                with status_container.container():
                    with st.spinner("Processando os dados..."):
                        # Criar job
                        job_id = f"job_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
                        upload_dir = os.path.join("uploads", job_id)
                        os.makedirs(upload_dir, exist_ok=True)

                        # Salvar arquivo
                        file_path = os.path.join(upload_dir, uploaded_file.name)
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())

                        # Inicializar e rodar processador
                        processor = TATICProcessor(
                            usar_categoria_h=usar_categoria_h,
                            incluir_finais_de_semana=incluir_finais_de_semana,
                            log_callback=st.write,
                        )

                        output_dir = Path(os.path.join("outputs", job_id))
                        import asyncio

                        asyncio.run(processor.process_tatic_data(file_path, output_dir))

                        # Gerar ZIP
                        nome_arquivo = processor.gerar_nome_relatorio(usar_categoria_h)
                        relatorio_zip_path = gerar_zip_de_relatorio(
                            str(output_dir), nome_arquivo
                        )

                        # Atualizar state com resultados
                        st.session_state.relatorio_gerado = True
                        st.session_state.nome_arquivo = nome_arquivo
                        st.session_state.relatorio_zip_path = relatorio_zip_path
                        st.session_state.output_dir = str(output_dir)

                st.success(f"✅ Relatório gerado: {st.session_state.nome_arquivo}")

                # Resetar para estado inicial (Step 0) forçando limpeza do uploader
                st.session_state.uploader_key += 1
                st.session_state.processing = False

                # Rerun para atualizar a tela (uploader vai sumir/resetar)
                st.rerun()

            except Exception as e:
                st.error(f"Erro: {e}")
                st.session_state.processing = False
            finally:
                GlobalLock.release()

# Botão de download (exibido fora do fluxo principal se existir relatório)
if st.session_state.relatorio_gerado and os.path.exists(
    st.session_state.relatorio_zip_path
):
    st.divider()
    st.subheader("📥 Download Disponível")
    # DEBUG: Mostrar o nome do arquivo que será baixado (removido para prod)
    # st.write(f"**Arquivo pronto:** `{st.session_state.nome_arquivo}`")

    with open(st.session_state.relatorio_zip_path, "rb") as file:
        file_bytes = file.read()

    st.download_button(
        label="Baixar Relatório ZIP",
        data=file_bytes,
        file_name=st.session_state.nome_arquivo,
        mime="application/zip",
    )
    st.info("Para gerar um novo relatório, envie uma nova planilha acima.")
