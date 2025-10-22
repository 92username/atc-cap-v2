"""
TATIC Processor Service - Versão Web
Adaptado do script otimizado que funcionava localmente
"""

import asyncio
import json
import os
import re
import time
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

# ============================================================================
# PARALELISMO COM PANDARALLEL
# ============================================================================
# Tentar importar e inicializar pandarallel para processamento paralelo
try:
    from pandarallel import pandarallel

    pandarallel.initialize(nb_workers=2, progress_bar=False, verbose=0)
    PARALLEL_ENABLED = True
except ImportError:
    PARALLEL_ENABLED = False


class TATICProcessor:
    """
    Processador TATIC otimizado para aplicação web
    Baseado no código que funcionava perfeitamente localmente
    """

    def __init__(self, usar_categoria_h=False, incluir_finais_de_semana=False, log_callback=None):
        self.usar_categoria_H = usar_categoria_h
        self.incluir_finais_de_semana = incluir_finais_de_semana
        self.log_callback = log_callback or (lambda msg: None)
        self.output_dir = Path("outputs")
        self.output_dir.mkdir(exist_ok=True)
        self.categorias_df = self._load_categorias()

        # Configurações do processador
        self.EVENTOS_PISTA = {"ARR", "DEP", "TGL"}
        self.EVENTOS_ATC_TOTAL = {
            "ARR",
            "DEP",
            "TGL",
            "QAY",
            "QAF",
            "ABA",
            "ABD",
            "ACD",
            "ATN",
            "LOW",
            "QRF",
            "QSO",
        }
        self.EVENTOS_EXCLUIR = {"ALTN", "NAN"}
        self.EVENTOS_REQUER_PISTA = {"ARR", "DEP", "TGL"}

        # Mapeamento de meses PT -> número
        self.MESES_PT = {
            "janeiro": 1,
            "jan": 1,
            "fevereiro": 2,
            "fev": 2,
            "março": 3,
            "mar": 3,
            "abril": 4,
            "abr": 4,
            "maio": 5,
            "mai": 5,
            "junho": 6,
            "jun": 6,
            "julho": 7,
            "jul": 7,
            "agosto": 8,
            "ago": 8,
            "setembro": 9,
            "set": 9,
            "outubro": 10,
            "out": 10,
            "novembro": 11,
            "nov": 11,
            "dezembro": 12,
            "dez": 12,
        }

        # Regex para parsing de timestamps
        self._TS_RE = re.compile(
            r"^\s*(\d{4})-([A-Za-zçãáâéêíóôõúü\-]+)-(\d{1,2})\s+(\d{2}:\d{2}:\d{2})\s*$",
            re.IGNORECASE,
        )

    def _apply_parallel(self, series, func, axis=None):
        """
        Aplica uma função a uma Series ou DataFrame com suporte a paralelismo.
        Se pandarallel estiver disponível, usa parallel_apply; caso contrário, usa apply normal.

        Args:
            series: pandas Series ou DataFrame
            func: função a aplicar
            axis: eixo para apply (0 ou 1), usado apenas para DataFrames

        Returns:
            Series ou DataFrame com resultado da aplicação
        """
        if PARALLEL_ENABLED and hasattr(series, "parallel_apply"):
            # Usar parallelização
            if axis is not None:
                return series.parallel_apply(func, axis=axis)
            else:
                return series.parallel_apply(func)
        else:
            # Fallback para apply normal
            if axis is not None:
                return series.apply(func, axis=axis)
            else:
                return series.apply(func)

    def _sync_file(self, file_path):
        """
        Sincroniza um arquivo com o disco para garantir que foi escrito.
        Essencial quando usando asyncio para evitar race conditions.

        Args:
            file_path: Path ou string do arquivo a sincronizar
        """
        try:
            file_path = Path(file_path)
            if file_path.exists():
                # Fazer fsync no arquivo aberto
                with open(file_path, "r") as f:
                    os.fsync(f.fileno())
        except Exception:
            # Silenciosamente ignorar erros de sync
            # (nem todos os filesystems suportam fsync)
            pass

    def _sync_directory(self, dir_path):
        """
        Sincroniza um diretório inteiro com o disco.
        Garante que todos os arquivos dentro foram de fato escritos.

        Args:
            dir_path: Path ou string do diretório a sincronizar
        """
        try:
            dir_path = Path(dir_path)
            if dir_path.exists():
                # Sincronizar cada arquivo no diretório
                for file in dir_path.iterdir():
                    if file.is_file():
                        self._sync_file(file)

                # Sincronizar o próprio diretório
                # Abrir e fazer fsync para garantir metadados
                try:
                    fd = os.open(str(dir_path), os.O_RDONLY)
                    os.fsync(fd)
                    os.close(fd)
                except Exception:
                    # Em alguns sistemas, pode não ser possível fazer fsync em diretório
                    pass
        except Exception as e:
            self.log(f"⚠️ Aviso ao sincronizar diretório {dir_path}: {e}")

    def gerar_nome_relatorio(self, usar_categoria_h=None):
        """Gera nome de relatório incremental e datado"""
        if usar_categoria_h is None:
            usar_categoria_h = self.usar_categoria_H

        data = datetime.now().strftime("%d%m%Y")
        pattern = re.compile(r"relatorio_(\d+)_\d{8}_(H|STD)\.zip")

        os.makedirs("outputs", exist_ok=True)
        existing_files = os.listdir("outputs")

        nums = []
        for f in existing_files:
            if match := pattern.match(f):
                nums.append(int(match.group(1)))

        next_num = max(nums) + 1 if nums else 1

        modo = "H" if usar_categoria_h else "STD"
        return f"relatorio_{next_num:04d}_{data}_{modo}.zip"

    def lista_helicopteros(self):
        """Lista de códigos de aeronaves identificadas como helicópteros"""
        return [
            "R22",
            "R44",
            "R66",
            "S76",
            "S92",
            "A109",
            "A119",
            "A139",
            "A189",
            "B206",
            "B407",
            "B412",
            "B429",
            "EC120",
            "EC130",
            "EC135",
            "EC145",
            "EC155",
            "EC35",
            "EC225",
            "EC350",
            "EC635",
            "EC725",  # Modelos Eurocopter adicionais
            "H120",
            "H125",
            "H130",
            "H135",
            "H145",
            "H155",
            "H160",
            "H175",
            "H215",
            "H225",
            "AS350",
            "AS355",
            "AS365",
            "AS532",
            "AS565",  # Modelos Airbus adicionais
            "AW109",
            "AW119",
            "AW139",
            "AW169",
            "AW189",
            "AW609",
            "MD500",
            "MD600",
            "OH58",
            "UH1",
            "UH60",  # Modelos MD e militares comuns
            "BK117",
            "BO105",
            "SA315",
            "SA330",
            "SA341",
            "SA342",  # Outros modelos
        ]

    def log(self, msg):
        """Log message to both console and callback if provided"""
        print(msg)
        self.log_callback(msg)

    def _load_categorias(self) -> pd.DataFrame:
        """Carrega tabela de categorias de aeronaves"""
        candidates = []

        env_override = os.getenv("TATIC_CATEGORIAS_CSV")
        if env_override:
            candidates.append(Path(env_override))

        module_dir = Path(__file__).resolve().parent
        candidates.extend(
            [
                module_dir / "categorias-A-E.csv",
                module_dir / "assets" / "categorias-A-E.csv",
                module_dir.parent / "categorias-A-E.csv",
                module_dir.parent / "assets" / "categorias-A-E.csv",
                module_dir.parent.parent / "assets" / "categorias-A-E.csv",
                module_dir.parent.parent.parent / "assets" / "categorias-A-E.csv",
                Path.cwd() / "assets" / "categorias-A-E.csv",
            ]
        )

        seen_paths = set()
        for candidate in candidates:
            try:
                resolved = candidate.resolve()
            except FileNotFoundError:
                continue

            if resolved in seen_paths or not resolved.exists():
                continue

            seen_paths.add(resolved)
            try:
                return pd.read_csv(resolved)
            except Exception as exc:
                self.log(f"Erro ao carregar categorias em {resolved}: {exc}")

        self.log("Arquivo de categorias não encontrado, usando classificação básica")
        return pd.DataFrame(columns=["Aeronave", "Categoria"])

    async def excel_to_csv(self, excel_path: Path) -> Path:
        """Converte arquivo Excel para CSV de forma assíncrona"""
        return await asyncio.to_thread(self._excel_to_csv_sync, Path(excel_path))

    def _excel_to_csv_sync(self, excel_path: Path) -> Path:
        csv_path = excel_path.with_suffix(".csv")
        try:
            df = pd.read_excel(excel_path)
            df.to_csv(csv_path, index=False, encoding="utf-8")
            self.log(f"Excel convertido para CSV: {csv_path}")
            return csv_path
        except Exception as exc:
            self.log(f"Erro na conversão Excel->CSV ({excel_path}): {exc}")
            raise

    def strip_accents(self, s: str) -> str:
        """Remove acentos de strings"""
        return "".join(
            c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn"
        )

    def detect_and_read_csv(self, file_path: Path) -> pd.DataFrame:
        """Detecta encoding e lê arquivo CSV/Excel"""
        self.log(f"🔍 Lendo arquivo: {file_path}")

        # Se for Excel, ler diretamente
        if file_path.suffix.lower() in [".xlsx", ".xls"]:
            try:
                df = pd.read_excel(file_path)
                self.log(f"✅ Excel lido. Shape: {df.shape}")
                self.log(f"📋 Colunas: {list(df.columns)}")
                return df
            except Exception as e:
                self.log(f"Erro ao ler Excel: {e}")
                raise

        # Para CSV, tentar diferentes encodings
        encodings = ["utf-8", "latin-1", "cp1252", "iso-8859-1"]
        for encoding in encodings:
            try:
                df = pd.read_csv(file_path, sep=None, engine="python", encoding=encoding)
                self.log(f"✅ CSV lido com {encoding}. Shape: {df.shape}")
                return df
            except UnicodeDecodeError:
                continue
            except Exception as e:
                self.log(f"Erro com {encoding}: {e}")
                continue

        raise ValueError("Não foi possível ler o arquivo")

    def normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normaliza nomes das colunas"""
        self.log("🔄 Normalizando colunas...")

        # Mapeamento de colunas
        col_map = {
            "h.evento": "timestamp_utc",
            "hevento": "timestamp_utc",
            "hora evento": "timestamp_utc",
            "evento": "evento",
            "pista": "pista",
            "equipamento": "equipamento",
        }

        lower_map = {c.lower(): c for c in df.columns}
        rename = {}

        for k, v in col_map.items():
            if k in lower_map:
                rename[lower_map[k]] = v

        dfn = df.rename(columns=rename).copy()
        self.log(f"📋 Colunas após renomeação: {list(dfn.columns)}")

        # Verificar colunas obrigatórias
        required_cols = ["timestamp_utc", "evento", "pista"]
        missing = [c for c in required_cols if c not in dfn.columns]
        if missing:
            raise ValueError(f"Colunas faltantes: {missing}")

        return dfn

    def parse_timestamps_vectorized(self, series: pd.Series) -> pd.Series:
        """Parsing vetorizado de timestamps portugueses"""
        self.log(f"📅 Parsing de {len(series):,} timestamps...")

        # Converter para string
        str_series = series.astype(str).str.strip()

        # Substituir meses portugueses
        meses_map = {
            "janeiro": "01",
            "fevereiro": "02",
            "março": "03",
            "abril": "04",
            "maio": "05",
            "junho": "06",
            "julho": "07",
            "agosto": "08",
            "setembro": "09",
            "outubro": "10",
            "novembro": "11",
            "dezembro": "12",
        }

        for mes_nome, mes_num in meses_map.items():
            str_series = str_series.str.replace(f"-{mes_nome}-", f"-{mes_num}-", regex=False)

        # Parse com pandas
        result = pd.to_datetime(str_series, format="%Y-%m-%d %H:%M:%S", errors="coerce")
        result = result.dt.tz_localize("UTC")

        valid_count = result.notna().sum()
        self.log(f"📅 Parsing: {valid_count:,}/{len(series):,} sucessos")

        return result

    def normalize_pista(self, s):
        """Normaliza valores de pista"""
        if pd.isna(s):
            return np.nan

        s_str = str(s).strip()
        if not s_str or s_str.lower() == "nan":
            return np.nan

        # Remove .0 se for float
        if s_str.endswith(".0"):
            s_str = s_str[:-2]

        # Normalizar para 03 ou 21
        if s_str in ["3", "03", "030"]:
            return "03"
        elif s_str in ["21", "210"]:
            return "21"
        else:
            return s_str  # Retorna original para debug

    def extract_wake_turbulence_category(self, equipamento):
        """Extrai categoria de esteira do equipamento"""
        if pd.isna(equipamento):
            return "UNKNOWN"

        equipamento_str = str(equipamento).strip().upper()

        if "/" in equipamento_str:
            parts = equipamento_str.split("/")
            if len(parts) >= 2:
                wake = parts[1].strip().upper()
                if wake in ["H", "M", "L"]:
                    return wake

        return "UNKNOWN"

    def get_aircraft_category(self, aircraft_code: str) -> str:
        """Classifica aeronave usando tabela de categorias"""
        if pd.isna(aircraft_code) or aircraft_code == "":
            return "UNKNOWN"

        aircraft_str = str(aircraft_code).strip().upper()

        # Processar formato CODIGO/WAKE ou CODIGOWAKE
        if "/" in aircraft_str:
            aircraft_type = aircraft_str.split("/")[0]
            wake_part = aircraft_str.split("/")[1] if len(aircraft_str.split("/")) > 1 else ""
        elif aircraft_str[-1] in ["L", "M", "H"] and len(aircraft_str) > 1:
            # Formato CODIGOL, CODIGOM, CODIGOH
            aircraft_type = aircraft_str[:-1]
            wake_part = aircraft_str[-1]
        else:
            aircraft_type = aircraft_str
            wake_part = ""

        # Verificar se deve usar categoria H para helicópteros
        if self.usar_categoria_H and aircraft_type in self.lista_helicopteros():
            return "H"

        # Tentar na tabela de categorias
        if not self.categorias_df.empty:
            match = self.categorias_df[self.categorias_df["Aeronave"].str.upper() == aircraft_type]
            if not match.empty:
                categoria = match.iloc[0]["Categoria"]
                return categoria.replace("CAT ", "") if "CAT" in categoria else categoria

        # Fallback para esteira de turbulência
        if wake_part:
            wake = wake_part.strip().upper()
            wake_to_category = {"L": "A", "M": "B", "H": "C"}
            if wake in wake_to_category:
                return wake_to_category[wake]

        return "UNKNOWN"

    def get_weekday_name(self, weekday_num: int) -> str:
        """Nome do dia da semana"""
        weekday_names = {
            0: "Segunda",
            1: "Terça",
            2: "Quarta",
            3: "Quinta",
            4: "Sexta",
            5: "Sábado",
            6: "Domingo",
        }
        return weekday_names.get(weekday_num, "Desconhecido")

    async def process_tatic_data(self, file_path, output_dir: Path) -> dict[str, Any]:
        """Processa dados TATIC - método principal"""
        try:
            start_time = time.time()
            file_path = Path(file_path)
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            self.log(f"🚀 Iniciando processamento: {file_path}")
            self.log(f"[DEBUG] Diretório de saída: {output_dir}")
            self.log(f"[DEBUG] Arquivo de entrada: {file_path}")

            # 1. Ler dados
            df_raw = self.detect_and_read_csv(file_path)

            # 2. Normalizar colunas
            d = self.normalize_columns(df_raw)

            # 3. Normalizações básicas
            self.log("🔧 Aplicando normalizações...")
            d["evento"] = d["evento"].astype(str).str.strip().str.upper()
            # Usar paralelismo para normalizar pistas
            d["pista"] = self._apply_parallel(d["pista"], self.normalize_pista)

            self.log(f"📊 Eventos únicos: {sorted(d['evento'].unique())}")
            pistas_unicas = [x for x in d["pista"].unique() if pd.notna(x)]
            self.log(f"🛬 Pistas únicas: {sorted(pistas_unicas)}")

            # 4. Parse timestamps
            self.log("🕐 Processando timestamps...")
            d["timestamp_utc"] = self.parse_timestamps_vectorized(d["timestamp_utc"])
            d = (
                d.dropna(subset=["timestamp_utc"])
                .sort_values("timestamp_utc")
                .reset_index(drop=True)
            )

            # 5. Forward-fill seletivo em pistas
            self.log("🛬 Aplicando forward-fill...")
            mask_requer_pista = d["evento"].isin(self.EVENTOS_REQUER_PISTA)
            d.loc[mask_requer_pista, "pista"] = d.loc[mask_requer_pista, "pista"].ffill()

            # 6. Excluir eventos desnecessários
            d_clean = d[~d["evento"].isin(self.EVENTOS_EXCLUIR)].copy()

            # 7. Separar por categorias
            d_total = d_clean[d_clean["evento"].isin(self.EVENTOS_ATC_TOTAL)].copy()
            d_rwy = d_clean[
                (d_clean["evento"].isin(self.EVENTOS_PISTA)) & (d_clean["pista"].isin({"03", "21"}))
            ].copy()

            self.log(f"📊 Movimentos ATC total: {len(d_total)}")
            self.log(f"🛬 Movimentos de pista: {len(d_rwy)}")

            # 8. Extrair ano/mês/dia da semana
            d_rwy["ano"] = d_rwy["timestamp_utc"].dt.year
            d_rwy["mes"] = d_rwy["timestamp_utc"].dt.month
            d_rwy["weekday"] = d_rwy["timestamp_utc"].dt.dayofweek  # Adicionando dia da semana
            d_total["ano"] = d_total["timestamp_utc"].dt.year
            d_total["mes"] = d_total["timestamp_utc"].dt.month

            # 9. Gerar tabelas conforme Anexo II – MCA 100-26 (2025)
            results = {}

            # Garantir que o diretório de saída existe
            os.makedirs(output_dir, exist_ok=True)

            # Tabela 1: Movimento percentual por categoria de aeronaves
            table1 = self.generate_table1_mca(d_rwy)
            table1_path = output_dir / "tabela1_movimento_percentual_categoria.csv"
            table1.to_csv(table1_path, index=False)
            self._sync_file(table1_path)
            self.log("💾 [SALVO] Tabela 1 – Movimento percentual por categoria")
            results["table1"] = table1.to_dict("records")

            # Tabela 2: Resultado do mix
            table2 = self.generate_table2_mca(d_rwy)
            table2_path = output_dir / "tabela2_resultado_mix_categoria.csv"
            table2.to_csv(table2_path, index=False)
            self._sync_file(table2_path)
            self.log("💾 [SALVO] Tabela 2 – Resultado do mix")
            results["table2"] = table2.to_dict("records")

            # Tabela 3: Movimento mensal por pista
            table3 = self.generate_table3_mca(d_rwy)
            table3_path = output_dir / "tabela3_movimento_mensal_pista.csv"
            table3.to_csv(table3_path, index=False)
            self._sync_file(table3_path)
            self.log("💾 [SALVO] Tabela 3 – Movimento mensal por pista")
            results["table3"] = table3.to_dict("records")

            # Tabela 4: Percentual de utilização de pistas
            table4 = self.generate_table4_mca(d_rwy)
            table4_path = output_dir / "tabela4_percentual_utilizacao_pistas.csv"
            table4.to_csv(table4_path, index=False)
            self._sync_file(table4_path)
            self.log("💾 [SALVO] Tabela 4 – Percentuais de utilização de pistas")
            results["table4"] = table4.to_dict("records")

            # Gerar arquivo resumo conforme MCA 100-26
            resumo_path = output_dir / "resumo.txt"
            with open(resumo_path, "w", encoding="utf-8") as f:
                f.write("Relatório conforme Anexo II – MCA 100-26 (2025)\n")
                f.write("Inclui Tabelas 1 a 4 conforme formato normativo.\n")
                f.write(f"\nProcessado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(
                    f"Modo helicópteros: {'Ativado (categoria H)' if self.usar_categoria_H else 'Desativado (categorias A-E)'}\n"
                )
                f.write(
                    f"Dias analisados na Tabela 1: {'Segunda a Domingo' if self.incluir_finais_de_semana else 'Segunda a Sexta (padrão MCA 100-26)'}\n"
                )
            self._sync_file(resumo_path)
            self.log("💾 [SALVO] Resumo do relatório")

            # Gerar dados de gráficos (apenas tabelas MCA)
            charts_data = self._build_charts_data_mca(table1, table2, table3, table4)
            try:
                with open(output_dir / "charts_data.json", "w", encoding="utf-8") as chart_file:
                    json.dump(charts_data, chart_file, ensure_ascii=False, indent=2)
                self._sync_file(output_dir / "charts_data.json")
            except Exception as chart_exc:
                self.log(f"Erro ao escrever charts_data.json: {chart_exc}")

            # Estatísticas
            end_time = time.time()
            processing_time = end_time - start_time
            self.log("✅ Processamento concluído conforme MCA 100-26!")
            # Registrar tempo decorrido em Português
            self.log(f"⏳ Tempo decorrido: {processing_time:.2f} segundos")

            # 🔧 CRÍTICO: Sincronizar diretório com o disco
            # Isso garante que todos os arquivos foram de fato escritos ao disco
            # Essencial quando usando asyncio para evitar race conditions
            self._sync_directory(output_dir)

            # Pequeno delay para garantir que o SO completou todas as operações
            import time as time_module

            time_module.sleep(0.5)

            return {
                "success": True,
                "message": f"Processamento concluído. {len(d_total)} movimentos ATC, {len(d_rwy)} movimentos de pista.",
                "tables": results,
                "charts": charts_data,
                "statistics": {
                    "total_records": len(df_raw),
                    "atc_movements": len(d_total),
                    "runway_movements": len(d_rwy),
                    "processing_time_seconds": processing_time,
                    "records_per_second": len(df_raw) / processing_time
                    if processing_time > 0
                    else 0,
                },
                "output_dir": str(output_dir),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Erro no processamento: {e}",
            }

    def generate_table1_mca(self, d_rwy: pd.DataFrame) -> pd.DataFrame:
        """Tabela 1: Movimento percentual por categoria de aeronaves (MCA 100-26)"""
        if len(d_rwy) == 0 or "equipamento" not in d_rwy.columns:
            return pd.DataFrame([{"CAT": "SEM DADOS"}])

        # Adicionar categoria e dia da semana
        d_rwy = d_rwy.copy()
        # Usar paralelismo para classificar aeronaves por categoria
        d_rwy["categoria"] = self._apply_parallel(d_rwy["equipamento"], self.get_aircraft_category)

        # Selecionar dias conforme configuração
        if self.incluir_finais_de_semana:
            # Incluir todos os dias da semana
            self.log("📅 Incluindo Sábado e Domingo na análise.")
            dias_semana = [0, 1, 2, 3, 4, 5, 6]  # Segunda a Domingo
            dias = [
                "Segunda",
                "Terça",
                "Quarta",
                "Quinta",
                "Sexta",
                "Sábado",
                "Domingo",
            ]
        else:
            # Filtrar apenas dias úteis (segunda a sexta) conforme MCA 100-26
            self.log("📅 Considerando apenas Segunda a Sexta (MCA 100-26).")
            dias_semana = [0, 1, 2, 3, 4]  # Segunda a Sexta
            dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]

        # Filtrar os dias selecionados
        d_rwy = d_rwy[d_rwy["weekday"].isin(dias_semana)].copy()

        if len(d_rwy) == 0:
            return pd.DataFrame([{"CAT": "SEM DADOS"}])

        categorias = ["A", "B", "C", "D", "E"]
        if self.usar_categoria_H:
            categorias = ["A", "B", "C", "H"]

        tabela = []

        # Calcular para cada categoria
        for cat in categorias:
            linha = {"CAT": cat}
            for i, dia in enumerate(dias):
                df_dia = d_rwy[d_rwy["weekday"] == i]
                total_dia = len(df_dia)
                qtd = len(df_dia[df_dia["categoria"] == cat])
                perc = (qtd / total_dia * 100) if total_dia > 0 else 0
                linha[dia.upper()] = f"{qtd} / {perc:.1f}%"
            tabela.append(linha)

        # Linha TOTAL
        linha_total = {"CAT": "TOTAL"}
        for i, dia in enumerate(dias):
            df_dia = d_rwy[d_rwy["weekday"] == i]
            total_dia = len(df_dia)
            linha_total[dia.upper()] = f"{total_dia} / 100.0%"
        tabela.append(linha_total)

        return pd.DataFrame(tabela)

    def generate_table1(self, d_total: pd.DataFrame) -> pd.DataFrame:
        """Tabela 1: Movimentos ATC Total (versão legada)"""
        if len(d_total) == 0:
            return pd.DataFrame([{"MES": "SEM DADOS", "TOTAL": 0}])

        # Agrupar por ano/mês
        g = d_total.groupby(["ano", "mes"]).size().reset_index(name="TOTAL")

        # Criar label do mês
        multi_year = d_total["ano"].nunique() > 1
        if multi_year:
            g["MES"] = g.apply(lambda x: f"{x['mes']:02d}/{x['ano']}", axis=1)
        else:
            meses_abrev = {
                1: "JAN",
                2: "FEV",
                3: "MAR",
                4: "ABR",
                5: "MAI",
                6: "JUN",
                7: "JUL",
                8: "AGO",
                9: "SET",
                10: "OUT",
                11: "NOV",
                12: "DEZ",
            }
            g["MES"] = g["mes"].map(meses_abrev)

        return g[["MES", "TOTAL"]]

    def generate_table2(self, d_rwy: pd.DataFrame) -> pd.DataFrame:
        """Tabela 2: Movimentos por Pista"""
        if len(d_rwy) == 0:
            return pd.DataFrame([{"MES": "SEM DADOS", "RWY 03": 0, "RWY 21": 0, "TOTAL": 0}])

        # Agrupar por ano, mês, pista
        g = (
            d_rwy.groupby(["ano", "mes", "pista"])
            .size()
            .unstack(fill_value=0)
            .rename(columns={"03": "RWY 03", "21": "RWY 21"})
        )

        # Garantir colunas
        for col in ["RWY 03", "RWY 21"]:
            if col not in g.columns:
                g[col] = 0

        g = g.reset_index()

        # Label do mês
        multi_year = d_rwy["ano"].nunique() > 1
        if multi_year:
            g["MES"] = g.apply(lambda x: f"{x['mes']:02d}/{x['ano']}", axis=1)
        else:
            meses_abrev = {
                1: "JAN",
                2: "FEV",
                3: "MAR",
                4: "ABR",
                5: "MAI",
                6: "JUN",
                7: "JUL",
                8: "AGO",
                9: "SET",
                10: "OUT",
                11: "NOV",
                12: "DEZ",
            }
            g["MES"] = g["mes"].map(meses_abrev)

        g["TOTAL"] = g["RWY 03"] + g["RWY 21"]

        return g[["MES", "RWY 03", "RWY 21", "TOTAL"]]

    def generate_table2_mca(self, d_rwy: pd.DataFrame) -> pd.DataFrame:
        """Tabela 2: Resultado do mix (MCA 100-26)"""
        if len(d_rwy) == 0 or "equipamento" not in d_rwy.columns:
            return pd.DataFrame([{"CAT": "SEM DADOS", "MIX": "0%"}])

        d_rwy = d_rwy.copy()
        # Usar paralelismo para classificar aeronaves por categoria
        d_rwy["categoria"] = self._apply_parallel(d_rwy["equipamento"], self.get_aircraft_category)

        # Filtrar categorias válidas
        categorias = ["A", "B", "C", "D", "E"]
        if self.usar_categoria_H:
            categorias = ["A", "B", "C", "H"]
        d_filtered = d_rwy[d_rwy["categoria"].isin(categorias)].copy()

        if len(d_filtered) == 0:
            return pd.DataFrame([{"CAT": "SEM DADOS", "MIX": "0%"}])

        # Calcular média aritmética dos percentuais por categoria
        category_counts = d_filtered["categoria"].value_counts()
        total = len(d_filtered)

        table_data = []
        for cat in sorted(categorias):
            count = category_counts.get(cat, 0)
            percentage = (count / total * 100) if total > 0 else 0
            table_data.append({"CAT": cat, "MIX": f"{percentage:.1f}%"})

        # Adicionar total
        table_data.append({"CAT": "TOTAL", "MIX": "100.0%"})

        return pd.DataFrame(table_data)

    def generate_table3_mca(self, d_rwy: pd.DataFrame) -> pd.DataFrame:
        """Tabela 3: Movimento mensal por pista (MCA 100-26)"""
        if len(d_rwy) == 0:
            return pd.DataFrame([{"MES": "SEM DADOS", "RWY 03": 0, "RWY 21": 0, "TOTAL": 0}])

        # Agrupar por ano, mês, pista
        g = (
            d_rwy.groupby(["ano", "mes", "pista"])
            .size()
            .unstack(fill_value=0)
            .rename(columns={"03": "RWY 03", "21": "RWY 21"})
        )

        # Garantir colunas
        for col in ["RWY 03", "RWY 21"]:
            if col not in g.columns:
                g[col] = 0

        g = g.reset_index()

        # Label do mês
        multi_year = d_rwy["ano"].nunique() > 1
        if multi_year:
            # Usar paralelismo para formatar meses
            g["MES"] = self._apply_parallel(g, lambda x: f"{x['mes']:02d}/{x['ano']}", axis=1)
        else:
            meses_abrev = {
                1: "JAN",
                2: "FEV",
                3: "MAR",
                4: "ABR",
                5: "MAI",
                6: "JUN",
                7: "JUL",
                8: "AGO",
                9: "SET",
                10: "OUT",
                11: "NOV",
                12: "DEZ",
            }
            g["MES"] = g["mes"].map(meses_abrev)

        g["TOTAL"] = g["RWY 03"] + g["RWY 21"]

        return g[["MES", "RWY 03", "RWY 21", "TOTAL"]]

    def generate_table4_mca(self, d_rwy: pd.DataFrame) -> pd.DataFrame:
        """Tabela 4: Percentual de utilização de pistas (MCA 100-26)"""
        if len(d_rwy) == 0:
            return pd.DataFrame(
                [
                    {"PISTA": "03", "PERCENTUAL": "0.0%"},
                    {"PISTA": "21", "PERCENTUAL": "0.0%"},
                ]
            )

        # Calcular totais por pista
        total_03 = len(d_rwy[d_rwy["pista"] == "03"])
        total_21 = len(d_rwy[d_rwy["pista"] == "21"])
        total_geral = total_03 + total_21

        if total_geral == 0:
            perc_03 = perc_21 = 0.0
        else:
            perc_03 = total_03 / total_geral * 100
            perc_21 = total_21 / total_geral * 100

        return pd.DataFrame(
            [
                {"PISTA": "03", "PERCENTUAL": f"{perc_03:.1f}%"},
                {"PISTA": "21", "PERCENTUAL": f"{perc_21:.1f}%"},
                {"PISTA": "TOTAL", "PERCENTUAL": "100.0%"},
            ]
        )

    def generate_table3(self, d_rwy: pd.DataFrame) -> pd.DataFrame:
        """Tabela 3: Percentual de Utilização das Pistas"""
        if len(d_rwy) == 0:
            return pd.DataFrame(
                [
                    {"PISTA": "03", "PERCENTUAL": "0%"},
                    {"PISTA": "21", "PERCENTUAL": "0%"},
                ]
            )

        # Calcular totais por pista
        total_03 = len(d_rwy[d_rwy["pista"] == "03"])
        total_21 = len(d_rwy[d_rwy["pista"] == "21"])
        total_geral = total_03 + total_21

        if total_geral == 0:
            perc_03 = perc_21 = 0
        else:
            perc_03 = round(total_03 / total_geral * 100)
            perc_21 = 100 - perc_03

        return pd.DataFrame(
            [
                {"PISTA": "03", "PERCENTUAL": f"{perc_03}%"},
                {"PISTA": "21", "PERCENTUAL": f"{perc_21}%"},
                {"PISTA": "TOTAL", "PERCENTUAL": "100%"},
            ]
        )

    def generate_table4(self, d_rwy: pd.DataFrame) -> pd.DataFrame:
        """Tabela 4: Classificação de Esteira de Turbulência"""
        if len(d_rwy) == 0:
            return pd.DataFrame([{"CATEGORIA": "SEM DADOS", "MOVIMENTOS": 0, "PERCENTUAL": "0%"}])

        # Extrair categorias
        if "equipamento" not in d_rwy.columns:
            d_rwy["wake_category"] = "UNKNOWN"
        else:
            d_rwy = d_rwy.copy()
            # Usar paralelismo para extrair categorias de esteira de turbulência
            d_rwy["wake_category"] = self._apply_parallel(
                d_rwy["equipamento"], self.extract_wake_turbulence_category
            )

        # Contar por categoria
        wake_counts = d_rwy["wake_category"].value_counts()
        total_movements = len(d_rwy)

        # Criar tabela
        table_data = []
        for category in ["H", "M", "L"]:
            count = wake_counts.get(category, 0)
            percentage = (count / total_movements * 100) if total_movements > 0 else 0
            table_data.append(
                {
                    "CATEGORIA": category,
                    "MOVIMENTOS": count,
                    "PERCENTUAL": f"{percentage:.1f}%",
                }
            )

        # Adicionar UNKNOWN se existir
        unknown_count = wake_counts.get("UNKNOWN", 0)
        if unknown_count > 0:
            unknown_pct = unknown_count / total_movements * 100
            table_data.append(
                {
                    "CATEGORIA": "UNKNOWN",
                    "MOVIMENTOS": unknown_count,
                    "PERCENTUAL": f"{unknown_pct:.1f}%",
                }
            )

        return pd.DataFrame(table_data)

    def generate_table5(self, d_rwy: pd.DataFrame) -> pd.DataFrame:
        """Tabela 5: Categoria por Dia da Semana"""
        if len(d_rwy) == 0 or "equipamento" not in d_rwy.columns:
            return pd.DataFrame([{"CATEGORIA": "SEM DADOS"}])

        d_rwy = d_rwy.copy()
        # Usar paralelismo para classificar aeronaves por categoria
        d_rwy["categoria"] = self._apply_parallel(d_rwy["equipamento"], self.get_aircraft_category)

        # Log específico para modo helicóptero
        if self.usar_categoria_H:
            qtd_heli = len(d_rwy[d_rwy["categoria"] == "H"])
            self.log(f"🚁 Modo H ativo — {qtd_heli} helicópteros reclassificados como Categoria H.")

        d_rwy["weekday"] = d_rwy["timestamp_utc"].dt.dayofweek
        # Usar paralelismo para obter nomes dos dias da semana
        d_rwy["weekday_name"] = self._apply_parallel(d_rwy["weekday"], self.get_weekday_name)

        # Filtrar categorias válidas (incluindo H quando aplicável)
        categorias_validas = ["A", "B", "C"]
        if self.usar_categoria_H:
            categorias_validas.append("H")
        d_filtered = d_rwy[d_rwy["categoria"].isin(categorias_validas)].copy()

        if len(d_filtered) == 0:
            return pd.DataFrame([{"CATEGORIA": "SEM DADOS"}])

        # Agrupar por categoria e dia da semana
        grouped = d_filtered.groupby(["categoria", "weekday_name"]).size().reset_index(name="count")
        pivot_table = grouped.pivot(
            index="categoria", columns="weekday_name", values="count"
        ).fillna(0)

        # Garantir todas as colunas
        all_weekdays = [
            "Segunda",
            "Terça",
            "Quarta",
            "Quinta",
            "Sexta",
            "Sábado",
            "Domingo",
        ]
        for day in all_weekdays:
            if day not in pivot_table.columns:
                pivot_table[day] = 0

        return pivot_table[all_weekdays].reset_index()

    def generate_table6(self, d_rwy: pd.DataFrame) -> pd.DataFrame:
        """Tabela 6: Mix por Categoria"""
        if len(d_rwy) == 0 or "equipamento" not in d_rwy.columns:
            return pd.DataFrame([{"CAT": "SEM DADOS", "MIX": "0%"}])

        d_rwy = d_rwy.copy()
        # Usar paralelismo para classificar aeronaves por categoria
        d_rwy["categoria"] = self._apply_parallel(d_rwy["equipamento"], self.get_aircraft_category)

        # Filtrar categorias válidas (incluindo H quando aplicável)
        categorias_validas = ["A", "B", "C"]
        if self.usar_categoria_H:
            categorias_validas.append("H")
        d_filtered = d_rwy[d_rwy["categoria"].isin(categorias_validas)].copy()

        # Log das categorias únicas antes do mix
        self.log(f"Categorias únicas antes do mix: {d_filtered['categoria'].unique().tolist()}")

        if len(d_filtered) == 0:
            return pd.DataFrame([{"CAT": "SEM DADOS", "MIX": "0%"}])

        # Calcular mix
        category_counts = d_filtered["categoria"].value_counts()
        total = len(d_filtered)

        table_data = []
        # Usar as categorias válidas ao invés de hardcode ['A', 'B', 'C']
        for cat in sorted(categorias_validas):
            count = category_counts.get(cat, 0)
            percentage = (count / total * 100) if total > 0 else 0
            table_data.append({"CAT": cat, "MIX": f"{percentage:.2f}%"})

        # Adicionar total
        table_data.append({"CAT": "TOTAL", "MIX": "100%"})

        return pd.DataFrame(table_data)

    def _build_charts_data_mca(
        self,
        table1: pd.DataFrame,
        table2: pd.DataFrame,
        table3: pd.DataFrame,
        table4: pd.DataFrame,
    ) -> dict[str, Any]:
        """Gera dicionário com dados dos gráficos MCA a partir das tabelas."""

        def _col_values(df: pd.DataFrame, column: str) -> list[Any]:
            return df[column].tolist() if column in df.columns else []

        charts_data: dict[str, Any] = {
            "percentual_categoria": {
                "labels": ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"],
                "datasets": [],
                "description": "Movimento percentual por categoria (Tabela 1)",
            },
            "mix_categoria": {
                "labels": _col_values(table2, "CAT"),
                "data": [
                    float(x.replace("%", "")) for x in _col_values(table2, "MIX") if x != "100.0%"
                ],
                "description": "Resultado do mix (Tabela 2)",
            },
            "movimento_mensal": {
                "labels": _col_values(table3, "MES"),
                "datasets": [
                    {"label": "RWY 03", "data": _col_values(table3, "RWY 03")},
                    {"label": "RWY 21", "data": _col_values(table3, "RWY 21")},
                ],
                "description": "Movimento mensal por pista (Tabela 3)",
            },
            "utilizacao_pistas": {
                "labels": ["RWY 03", "RWY 21"],
                "data": [
                    float(x.replace("%", ""))
                    for x in _col_values(table4, "PERCENTUAL")
                    if x != "100.0%"
                ],
                "description": "Percentual de utilização de pistas (Tabela 4)",
            },
        }

        return charts_data

    def _build_charts_data(
        self,
        table1: pd.DataFrame,
        table2: pd.DataFrame,
        table3: pd.DataFrame,
        table4: pd.DataFrame,
        table5: pd.DataFrame,
        table6: pd.DataFrame,
    ) -> dict[str, Any]:
        """Gera dicionário com dados dos gráficos a partir das tabelas."""

        def _col_values(df: pd.DataFrame, column: str) -> list[Any]:
            return df[column].tolist() if column in df.columns else []

        charts_data: dict[str, Any] = {
            "movimentos_mensais": {
                "labels": _col_values(table1, "MES"),
                "data": _col_values(table1, "TOTAL"),
            },
            "movimentos_pista": {
                "labels": _col_values(table2, "MES"),
                "datasets": [],
            },
            "percentual_pistas": {
                "labels": _col_values(table3, "MES"),
                "datasets": [],
            },
            "esteira_turbulencia": {
                "labels": _col_values(table4, "CATEGORIA"),
                "data": _col_values(table4, "MOVIMENTOS"),
            },
            "categoria_weekday": {
                "labels": table5.iloc[:, 0].tolist() if not table5.empty else [],
                "datasets": [],
            },
            "mix_categoria": {
                "labels": _col_values(table6, "CAT") or _col_values(table6, "CATEGORIA"),
                "data": _col_values(table6, "TOTAL"),
            },
        }

        if "RWY 03" in table2.columns:
            charts_data["movimentos_pista"]["datasets"].append(
                {
                    "label": "RWY 03",
                    "data": table2["RWY 03"].tolist(),
                }
            )
        if "RWY 21" in table2.columns:
            charts_data["movimentos_pista"]["datasets"].append(
                {
                    "label": "RWY 21",
                    "data": table2["RWY 21"].tolist(),
                }
            )

        if {"PISTA", "PERCENTUAL"}.issubset(table3.columns):
            charts_data["percentual_pistas"]["labels"] = table3["PISTA"].tolist()
            charts_data["percentual_pistas"]["datasets"].append(
                {
                    "label": "Utilização",
                    "data": [
                        float(str(value).replace("%", ""))
                        for value in table3["PERCENTUAL"].tolist()
                    ],
                }
            )

        if not table5.empty and table5.shape[1] > 1:
            weekday_labels = table5.iloc[:, 0].tolist()
            charts_data["categoria_weekday"]["labels"] = weekday_labels
            for column in table5.columns[1:]:
                charts_data["categoria_weekday"]["datasets"].append(
                    {
                        "label": column,
                        "data": table5[column].tolist(),
                    }
                )

        return charts_data

    async def generate_charts_data(self, output_dir: Path) -> dict[str, Any]:
        """Carrega dados dos gráficos a partir do diretório de saída."""
        return await asyncio.to_thread(self._load_charts_data_sync, Path(output_dir))

    def _load_charts_data_sync(self, output_dir: Path) -> dict[str, Any]:
        json_path = output_dir / "charts_data.json"
        if json_path.exists():
            try:
                with open(json_path, encoding="utf-8") as chart_file:
                    return json.load(chart_file)
            except Exception as exc:
                self.log(f"Erro ao ler charts_data.json: {exc}")

        table_map = {
            "table1": output_dir / "tabela1_movimentos_atc_total.csv",
            "table2": output_dir / "tabela2_movimentos_pista.csv",
            "table3": output_dir / "tabela3_percentual_pistas.csv",
            "table4": output_dir / "tabela4_mix_aeronaves.csv",
            "table5": output_dir / "tabela5_categoria_weekday.csv",
            "table6": output_dir / "tabela6_mix_categoria.csv",
        }

        loaded_tables = {}
        for key, path in table_map.items():
            if path.exists():
                try:
                    loaded_tables[key] = pd.read_csv(path)
                except Exception as exc:
                    self.log(f"Erro ao ler {path}: {exc}")
                    loaded_tables[key] = pd.DataFrame()
            else:
                loaded_tables[key] = pd.DataFrame()

        return self._build_charts_data(
            loaded_tables.get("table1", pd.DataFrame()),
            loaded_tables.get("table2", pd.DataFrame()),
            loaded_tables.get("table3", pd.DataFrame()),
            loaded_tables.get("table4", pd.DataFrame()),
            loaded_tables.get("table5", pd.DataFrame()),
            loaded_tables.get("table6", pd.DataFrame()),
        )
