import logging
import os
import secrets
import threading
import uuid
import zipfile
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from aeronaves_dict import atualizar_dicionario
from auth_providers import (
    google_build_auth_url,
    google_exchange_code_for_token,
    google_userinfo,
    ms_build_auth_url,
    ms_exchange_code_for_token,
    ms_userinfo,
)
from tatic_processor import TATICProcessor

load_dotenv()

# Configuração de página
st.set_page_config(
    page_title="TATIC Análise de Dados",
    page_icon="🛫",
    layout="wide",
    initial_sidebar_state="expanded",
)


def handle_auth_callback():
    """
    Handle OAuth callback delivered as query params to the Streamlit app.
    Expected query params (examples):
      ?auth_callback=1&provider=google&name=Fulano&email=fulano@example.com
      ?auth_callback=1&provider=microsoft&displayName=Fulano&mail=fulano@example.com

    When present, save a minimal `st.session_state['user']` and clear the query.
    """
    try:
        params = st.experimental_get_query_params()
    except Exception:
        # If query params API isn't available, skip
        return

    # If there's no query params, nothing to do
    if not params:
        return

    # If provider returned an authorization code (`code`), handle full OAuth exchange
    code = params.get("code", [None])[0]
    state_received = params.get("state", [None])[0]

    if code and state_received:
        # Determine provider from stored map
        state_map = st.session_state.get("oauth_state_map", {})
        provider = state_map.pop(state_received, None)

        # Fallback to explicit provider param if present
        if not provider:
            provider = params.get("provider", [None])[0]

        try:
            if provider == "google":
                token = google_exchange_code_for_token(code)
                access_token = token.get("access_token")
                if not access_token:
                    raise RuntimeError(f"No access_token returned from Google: {token}")
                user = google_userinfo(access_token)
                provider_name = "google"

            elif provider == "microsoft":
                token = ms_exchange_code_for_token(code)
                access_token = token.get("access_token")
                if not access_token:
                    raise RuntimeError(
                        f"No access_token returned from Microsoft: {token}"
                    )
                user = ms_userinfo(access_token)
                provider_name = "microsoft"

            else:
                st.error("Provedor OAuth desconhecido ou estado expirado.")
                return

            # Persist minimal user in session
            st.session_state["user"] = {
                "name": user.get("name") or (user.get("email") or ""),
                "email": user.get("email"),
                "provider": provider_name,
                "raw_user": user.get("raw"),
            }

            # cleanup state_map
            st.session_state["oauth_state_map"] = state_map

            # Clear query params and reload to show protected UI
            try:
                st.experimental_set_query_params()
            except Exception:
                pass
            try:
                st.experimental_rerun()
            except Exception:
                pass

        except Exception as e:
            st.error(f"Erro durante troca de código OAuth: {e}")
            return

    # Older/testing flow: support `auth_callback` with name/email in query params
    if "auth_callback" in params:
        provider = params.get("provider", [None])[0]
        # try multiple common fields
        name = (
            params.get("name", [None])[0]
            or params.get("displayName", [None])[0]
            or params.get("given_name", [None])[0]
        )
        email = (
            params.get("email", [None])[0]
            or params.get("mail", [None])[0]
            or params.get("userPrincipalName", [None])[0]
        )

        if not email:
            return

        st.session_state["user"] = {
            "name": name or email.split("@")[0],
            "email": email,
            "provider": provider or "unknown",
        }

        try:
            st.experimental_set_query_params()
        except Exception:
            pass
        try:
            st.experimental_rerun()
        except Exception:
            pass


# process any auth callback before anything else
handle_auth_callback()


# Configuração de barra lateral
def add_sidebar():
    with st.sidebar:
        # Ajuda: Como exportar do TATIC para o tatic-processor
        st.markdown(
            """
        <div style="background-color: #4B729A; padding: 10px; border-radius: 8px; margin-top: 8px;">
            <p style="margin:0 0 8px 0; font-weight:600;">❓ Como exportar do TATIC para o tatic-processor</p>
            <ol style="margin:0 0 0 18px; padding:0;">
                <li><strong>Login</strong> no TATIC</li>
                <li><strong>Consultas → Pesquisa Operacional → Movimentos</strong></li>
                <li><strong>Escolha o período</strong> (recomendado: 12 meses contíguos para estudos MCA 100-26; para testes, 30 dias)</li>
                <li>Clique em <strong>Executar</strong></li>
                <li><strong>Exportar para Excel</strong> (.xlsx)</li>
            </ol>
        </div>
        """,
            unsafe_allow_html=True,
        )
        st.header("Como usar este app")

        with st.expander("📋 Instruções"):
            st.markdown(
                """
        1. **Selecione** se helicópteros devem ser classificados como categoria H
        2. **Faça upload** do arquivo **TATIC (.xlsx)**
        3. **Clique em "Gerar Relatório"** para processar os dados
        4. **Baixe o relatório** gerado em formato ZIP
        """
            )

        with st.expander("� Formato MCA 100-26"):
            st.markdown(
                """
        O relatório segue as especificações do **Anexo II da MCA 100-26**, com as tabelas:

        - **Tabela 1:** Movimento percentual por categoria
        - **Tabela 2:** Resultado do mix
        - **Tabela 3:** Movimento mensal por pista
        - **Tabela 4:** Percentual de utilização de pistas
        """
            )

        st.markdown("---")

        # Dica amarela colocada ao final da sidebar
        st.warning(
            "⚠️ **Dica:** Exporte os dados diretamente do TATIC em formato bruto, sem aplicar filtros ou fórmulas personalizadas. O aplicativo foi otimizado para processar dados não modificados, garantindo resultados conforme a MCA 100-26."
        )

        # Logout block (shows only when logged)
        if "user" in st.session_state:
            user = st.session_state.get("user") or {}
            st.markdown("---")
            st.info(f"Conectado como: {user.get('name')} ({user.get('email')})")
            if st.button("Sair"):
                # Optionally direct Microsoft users to the global logout endpoint
                provider = user.get("provider")
                st.session_state.pop("user", None)
                if provider and provider.lower() == "microsoft":
                    ms_logout = (
                        "https://login.microsoftonline.com/common/oauth2/v2.0/logout"
                    )
                    # Clear query params and navigate to login by reloading
                    try:
                        st.experimental_set_query_params()
                    except Exception:
                        pass
                    # Open Microsoft logout in a new tab and then reload app to login screen
                    st.markdown(f"[Encerrar sessão no Microsoft]({ms_logout})")
                try:
                    st.experimental_rerun()
                except Exception:
                    pass


add_sidebar()


# If not authenticated, show a centered login screen and stop the app
def debug_oauth_settings():
    """Função de diagnóstico para verificar configurações OAuth."""
    st.subheader("🔧 Diagnóstico OAuth")
    st.write("Variáveis de ambiente (sem segredos):")
    st.json(
        {
            "GOOGLE_CLIENT_ID": bool(os.getenv("GOOGLE_CLIENT_ID")),
            "GOOGLE_REDIRECT_URI": os.getenv("GOOGLE_REDIRECT_URI"),
            "MICROSOFT_CLIENT_ID": bool(os.getenv("MICROSOFT_CLIENT_ID")),
            "MICROSOFT_REDIRECT_URI": os.getenv("MICROSOFT_REDIRECT_URI"),
        }
    )

    # Testar construção de URLs
    state = "test_state"
    try:
        google_uri, _ = google_build_auth_url(state)
        st.write(f"Google URL exemplo: {google_uri}")
    except Exception as e:
        st.error(f"Erro no Google: {e}")

    try:
        ms_uri = ms_build_auth_url(state)
        st.write(f"Microsoft URL exemplo: {ms_uri}")
    except Exception as e:
        st.error(f"Erro no Microsoft: {e}")


# Chame debug_oauth_settings() se quiser testar, mas por enquanto comentado
debug_oauth_settings()


def render_login_screen():
    # Small helper to start OAuth flows and redirect
    def start_oauth_flow(provider: str):
        state = secrets.token_urlsafe(24)
        state_map = st.session_state.get("oauth_state_map", {})

        if provider == "google":
            # Check if GOOGLE_REDIRECT_URI is set
            if not os.getenv("GOOGLE_REDIRECT_URI"):
                st.error(
                    "GOOGLE_REDIRECT_URI não está definido no .env. Defina como http://localhost:8506/"
                )
                return
            try:
                # google_build_auth_url returns (uri, state)
                uri, returned_state = google_build_auth_url(state)
                used_state = returned_state or state
                state_map[used_state] = "google"
                st.session_state["oauth_state_map"] = state_map
                # Debug: show the URL
                st.write(f"Redirecionando para Google: {uri}")
                # redirect the browser to the provider
                st.markdown(
                    f'<script>window.location.href = "{uri}"</script>',
                    unsafe_allow_html=True,
                )
                st.stop()
            except Exception as e:
                st.error(f"Erro ao construir URL do Google: {e}")

        if provider == "microsoft":
            # Check if MICROSOFT_REDIRECT_URI is set
            if not os.getenv("MICROSOFT_REDIRECT_URI"):
                st.error("MICROSOFT_REDIRECT_URI não está definido no .env.")
                return
            try:
                uri = ms_build_auth_url(state)
                state_map[state] = "microsoft"
                st.session_state["oauth_state_map"] = state_map
                # Debug: show the URL
                st.write(f"Redirecionando para Microsoft: {uri}")
                st.markdown(
                    f'<script>window.location.href = "{uri}"</script>',
                    unsafe_allow_html=True,
                )
                st.stop()
            except Exception as e:
                st.error(f"Erro ao construir URL do Microsoft: {e}")

    # Render a simple, centered UI with Streamlit buttons (keeps accessibility)
    st.write("\n")
    cols = st.columns([1, 0.8, 1])
    with cols[1]:
        st.markdown("<div style='text-align:center'>", unsafe_allow_html=True)
        st.markdown(
            "<h1>🚀 TATIC Processor – Acesso Restrito</h1>", unsafe_allow_html=True
        )
        st.markdown(
            "<p style='color:#333; font-size:16px;'>Faça login para continuar.</p>",
            unsafe_allow_html=True,
        )
        if st.button("🔵 Entrar com Google"):
            start_oauth_flow("google")
        if st.button("🟢 Entrar com Microsoft"):
            start_oauth_flow("microsoft")
        st.markdown(
            "<div style='color:#666; font-size:12px; margin-top:12px;'>© 2025 Jacaré.cloud</div>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)


# If user not present in session, render the login screen and stop
if "user" not in st.session_state:
    render_login_screen()
    st.stop()

# Interface principal
# Título com tag "Experimental" e tooltip
st.markdown(
    """
    <div style="display: flex; justify-content: center; align-items: center; gap: 12px; flex-wrap: wrap;">
        <h1 style="margin: 0; text-align: center;">🛫 Análise de Dados TATIC</h1>
        <span style="background-color: #D7D70A; color: #000; padding: 4px 10px; border-radius: 6px; font-weight: 600; font-size: 14px;">
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
    # Mostrar mensagem logo acima do botão, em vermelho e centralizada dentro da coluna do botão
    col_btn, _col_spacer = st.columns([0.18, 0.82])
    with col_btn:
        # Ajuste de alinhamento: usar margin-left em rem para manter responsividade
        st.markdown(
            "<div style='color:#b22222; font-weight:700; font-size:14px; text-align:left; margin-bottom:6px; margin-left:0.6rem;'>Clique apenas uma vez</div>",
            unsafe_allow_html=True,
        )
        gerar_clicked = st.button("🚀 Gerar Relatório")

    if gerar_clicked:
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
            threading.Thread(
                target=atualizar_dicionario, args=(df,), daemon=True
            ).start()
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
