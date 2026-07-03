"""
extract.py — Stage 1: Extracção de Dados
Dashboard de Indicadores Económicos — Angola

Fontes: INE (Instituto Nacional de Estatística), BNA (Banco Nacional de Angola)

Responsabilidade deste módulo:
  - Leitura dos ficheiros raw (CSV) gerados a partir das fontes INE e BNA
  - Validação básica de schema e contagem de registos
  - Retorno de DataFrames prontos para a stage de transformação

Extensibilidade:
  - Para ingestão via API (endpoint BNA ou INE), substituir pd.read_csv()
    por requests.get() + pd.read_json() ou pd.DataFrame(response.json())
  - Para ficheiros Excel, usar pd.read_excel() com o parâmetro sheet_name
"""

import os
import logging
import pandas as pd

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# ── Caminhos ─────────────────────────────────────────────────────────────────
RAW_DIR       = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")


# ── Loaders ──────────────────────────────────────────────────────────────────

def carregar_dados_macro() -> pd.DataFrame:
    """
    Carrega a série temporal macroeconómica trimestral.
    Fonte simulada com base em publicações do INE e BNA (2014–2024).
    Retorna um DataFrame com colunas brutas sem qualquer transformação.
    """
    caminho = os.path.join(RAW_DIR, "macro_angola.csv")
    logger.info(f"A carregar dados macro de: {caminho}")
    df = pd.read_csv(caminho)
    logger.info(f"Carregados {len(df)} registos | {len(df.columns)} colunas")
    return df


def carregar_dados_provincias() -> pd.DataFrame:
    """
    Carrega os indicadores socioeconómicos por província (18 províncias).
    Inclui: população, desemprego, pobreza, literacia, electrificação, PIB regional.
    """
    caminho = os.path.join(RAW_DIR, "provinces_angola.csv")
    logger.info(f"A carregar dados provinciais de: {caminho}")
    df = pd.read_csv(caminho)
    logger.info(f"Carregados {len(df)} registos | {df['province'].nunique()} províncias")
    return df


# ── Pipeline entry point ──────────────────────────────────────────────────────

def extract_all() -> dict:
    """
    Executa a stage completa de extracção.
    Retorna um dict com os DataFrames raw, prontos para transform_all().
    """
    logger.info("=== EXTRACT — INÍCIO ===")
    dados = {
        "macro":     carregar_dados_macro(),
        "provincias": carregar_dados_provincias(),
    }
    logger.info("=== EXTRACT — CONCLUÍDO ===")
    return dados


# ── Execução directa ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    datasets = extract_all()
    for nome, df in datasets.items():
        print(f"\n[{nome}]  shape={df.shape}")
        print(df.head(3).to_string())
