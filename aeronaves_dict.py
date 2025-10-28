import json
import logging
import os
import threading
from logging.handlers import RotatingFileHandler

import pandas as pd

# Configurar logging rotativo (substituir se >1MB)
logs_dir = "logs"
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

log_file = os.path.join(logs_dir, "aeronaves_dict.log")
handler = RotatingFileHandler(
    log_file, maxBytes=1024 * 1024, backupCount=0
)  # 1MB, substituir
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger = logging.getLogger("aeronaves_dict")
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# Lock para evitar escrita simultânea
lock = threading.Lock()

# Valores padrão para novas aeronaves
DEFAULT_PARAMS = {
    "classe_operacional": "desconhecida",
    "tipos": [],  # Será preenchido com o tipo
    "cat_vel": "A",
    "wake": "L",
    "Vi_aprox_kt": 80,
    "TOPP_s": 60,
    "TOPD_s": 70,
    "estimado": True,
}


def carregar_config():
    """Carrega o arquivo aeronaves_config.json."""
    config_path = "aeronaves_config.json"
    if os.path.exists(config_path):
        with open(config_path, encoding="utf-8") as f:
            return json.load(f)
    else:
        # Criar estrutura inicial se não existir
        config = {"helicopteros": [], "avioes": [], "novos": []}
        salvar_config(config)
        return config


def salvar_config(config):
    """Salva o arquivo aeronaves_config.json."""
    config_path = "aeronaves_config.json"
    with lock:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)


def registrar_nova_aeronave(config, tipo):
    """Registra uma nova aeronave na seção 'novos'."""
    nova_entrada = DEFAULT_PARAMS.copy()
    nova_entrada["tipos"] = [tipo]
    config["novos"].append(nova_entrada)
    logger.info(
        f"Nova aeronave detectada: {tipo} (entrada criada com valores estimados)"
    )


def obter_parametros(tipo):
    """Obtém os parâmetros de uma aeronave pelo tipo."""
    config = carregar_config()
    # Buscar em helicopteros
    for item in config.get("helicopteros", []):
        if tipo in item.get("tipos", []):
            return item
    # Buscar em avioes
    for item in config.get("avioes", []):
        if tipo in item.get("tipos", []):
            return item
    # Buscar em novos
    for item in config.get("novos", []):
        if tipo in item.get("tipos", []):
            return item
    return None  # Não encontrado


def atualizar_dicionario(df):
    """Atualiza o dicionário com novos tipos de aeronave do DataFrame."""
    col_nome = None
    for col in df.columns:
        if col.lower() in ["tipoaeronave", "equipamento"]:
            col_nome = col
            break

    if not col_nome:
        logger.error(
            "Nenhuma coluna de tipo de aeronave encontrada (esperado: 'TipoAeronave' ou 'Equipamento')."
        )
        return

    config = carregar_config()
    tipos_unicos = df[col_nome].dropna().unique()
    novos_adicionados = False

    for tipo in tipos_unicos:
        if obter_parametros(tipo) is None:
            registrar_nova_aeronave(config, tipo)
            novos_adicionados = True

    if novos_adicionados:
        salvar_config(config)
        logger.info("Dicionário atualizado com sucesso.")
    else:
        logger.info("Nenhuma nova aeronave detectada.")


if __name__ == "__main__":
    # Teste rápido manual (isolado)
    df = pd.DataFrame({"TipoAeronave": ["R44", "AW109", "S92"]})
    atualizar_dicionario(df)
