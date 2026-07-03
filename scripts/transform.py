"""
transform.py — Stage 2: Limpeza e Feature Engineering
Dashboard de Indicadores Económicos — Angola

Responsabilidade deste módulo:
  - Parsing de datas a partir de colunas year + quarter
  - Tratamento de missing values via forward-fill / back-fill
  - Cálculo de moving averages (janela de 4 trimestres)
  - Derivação de métricas: variação QoQ, taxa de juro real, labels de período
  - Normalização min-max para análise de correlação
  - Cálculo do índice de desenvolvimento composto por província
  - Geração da correlation matrix (Pearson) entre os 6 indicadores-chave
"""

import os
import logging
import numpy as np
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")


# ── Transformações macro ──────────────────────────────────────────────────────

def _parsing_datas(df: pd.DataFrame) -> pd.DataFrame:
    """Converte colunas year + quarter numa coluna datetime."""
    mapa_trimestre = {"Q1": "01", "Q2": "04", "Q3": "07", "Q4": "10"}
    df = df.copy()
    df["mes"] = df["quarter"].map(mapa_trimestre)
    df["date"] = pd.to_datetime(df["year"].astype(str) + "-" + df["mes"] + "-01")
    df = df.drop(columns=["mes"]).sort_values("date").reset_index(drop=True)
    logger.info("Coluna 'date' criada via parsing year+quarter")
    return df


def _tratar_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Forward-fill seguido de back-fill em todas as colunas numéricas."""
    colunas_num = df.select_dtypes(include=[np.number]).columns
    antes = df[colunas_num].isna().sum().sum()
    df[colunas_num] = df[colunas_num].ffill().bfill()
    depois = df[colunas_num].isna().sum().sum()
    logger.info(f"Missing values: {antes} → {depois}")
    return df


def _calcular_moving_averages(df: pd.DataFrame) -> pd.DataFrame:
    """Moving average de 4 trimestres (equivalente anual) para indicadores-chave."""
    colunas = ["inflation_pct", "exchange_rate_aoa_usd", "gdp_growth_pct"]
    for col in colunas:
        if col in df.columns:
            df[f"{col}_ma4"] = df[col].rolling(window=4, min_periods=1).mean().round(2)
    logger.info("Moving averages (MA4) calculadas")
    return df


def _calcular_metricas_derivadas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Derivação de métricas adicionais:
      - Variação QoQ do PIB e do câmbio
      - Taxa de juro real = taxa nominal − inflação
    """
    df["gdp_variacao_qoq"]  = df["gdp_usd_billion"].pct_change().mul(100).round(2)
    df["fx_variacao_qoq"]   = df["exchange_rate_aoa_usd"].pct_change().mul(100).round(2)
    df["taxa_juro_real"]    = (df["interest_rate_pct"] - df["inflation_pct"]).round(2)
    logger.info("Métricas derivadas calculadas (QoQ, taxa de juro real)")
    return df


def _rotular_periodos(df: pd.DataFrame) -> pd.DataFrame:
    """Classifica cada observação no respectivo regime económico."""
    condicoes = [
        (df["date"] < "2015-01-01"),
        (df["date"] >= "2015-01-01") & (df["date"] < "2018-01-01"),
        (df["date"] >= "2018-01-01") & (df["date"] < "2020-01-01"),
        (df["date"] >= "2020-01-01") & (df["date"] < "2022-01-01"),
        (df["date"] >= "2022-01-01"),
    ]
    rotulos = [
        "Pré-crise petrolífera",
        "Crise 2015–2017",
        "Recuperação Lourenço",
        "Impacto COVID-19",
        "Estabilização",
    ]
    df["periodo_economico"] = np.select(condicoes, rotulos, default="Indefinido")
    logger.info("Labels de período económico atribuídas")
    return df


def _normalizar_indicadores(df: pd.DataFrame) -> pd.DataFrame:
    """Normalização min-max [0, 1] para os indicadores usados na correlation matrix."""
    colunas = [
        "inflation_pct", "exchange_rate_aoa_usd", "gdp_growth_pct",
        "unemployment_pct", "interest_rate_pct",
    ]
    for col in colunas:
        if col in df.columns:
            mn, mx = df[col].min(), df[col].max()
            df[f"{col}_norm"] = ((df[col] - mn) / (mx - mn)).round(4)
    logger.info("Normalização min-max aplicada")
    return df


def transformar_macro(df: pd.DataFrame) -> pd.DataFrame:
    """Pipeline completo de transformação da série macroeconómica."""
    logger.info("--- A transformar dados macro ---")
    df = _parsing_datas(df)
    df = _tratar_missing_values(df)
    df = _calcular_moving_averages(df)
    df = _calcular_metricas_derivadas(df)
    df = _rotular_periodos(df)
    df = _normalizar_indicadores(df)
    logger.info(f"Transformação macro concluída: {df.shape}")
    return df


# ── Transformações provinciais ────────────────────────────────────────────────

def transformar_provincias(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enriquecimento do dataset provincial:
      - Índice de desenvolvimento composto (proxy IDH)
      - Coluna população em milhões
      - Índice de PIB per capita relativo
      - Classificação por região geográfica
    """
    logger.info("--- A transformar dados provinciais ---")
    df = df.copy()

    df["indice_desenvolvimento"] = (
        (df["literacy_rate_pct"]      * 0.35) +
        (df["electrification_pct"]    * 0.35) +
        ((100 - df["poverty_rate_pct"]) * 0.30)
    ).round(2)

    df["populacao_milhoes"]      = (df["population_2024"] / 1_000_000).round(3)
    df["indice_pib_per_capita"]  = (df["gdp_contribution_pct"] / df["populacao_milhoes"]).round(3)

    mapa_regioes = {
        "Luanda": "Norte",    "Bengo": "Norte",     "Cuanza Norte": "Norte",
        "Uíge": "Norte",      "Zaire": "Norte",     "Cabinda": "Norte",
        "Malanje": "Centro",  "Cuanza Sul": "Centro","Benguela": "Centro",
        "Huambo": "Centro",   "Bié": "Centro",
        "Huíla": "Sul",       "Namibe": "Sul",      "Cunene": "Sul",
        "Cuando Cubango": "Sul",
        "Moxico": "Leste",    "Lunda Norte": "Leste","Lunda Sul": "Leste",
    }
    df["regiao"] = df["province"].map(mapa_regioes).fillna("Centro")
    logger.info(f"Transformação provincial concluída: {df.shape}")
    return df


# ── Correlation matrix ────────────────────────────────────────────────────────

def calcular_correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula a correlation matrix de Pearson para os 6 indicadores-chave.
    Retorna um DataFrame quadrado 6×6.
    """
    colunas = [
        "gdp_growth_pct", "inflation_pct", "exchange_rate_aoa_usd",
        "interest_rate_pct", "unemployment_pct", "oil_revenue_pct_gdp",
    ]
    corr = df[colunas].corr().round(3)
    logger.info("Correlation matrix calculada")
    return corr


# ── Pipeline entry point ──────────────────────────────────────────────────────

def transform_all(dados_raw: dict) -> dict:
    """Executa todas as stages de transformação e retorna datasets enriquecidos."""
    logger.info("=== TRANSFORM — INÍCIO ===")
    macro_transf = transformar_macro(dados_raw["macro"])
    transformados = {
        "macro":       macro_transf,
        "provincias":  transformar_provincias(dados_raw["provincias"]),
        "correlacao":  calcular_correlation_matrix(macro_transf),
    }
    logger.info("=== TRANSFORM — CONCLUÍDO ===")
    return transformados


# ── Execução directa ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    from extract import extract_all

    raw = extract_all()
    transformados = transform_all(raw)
    for nome, df in transformados.items():
        print(f"\n[{nome}]  shape={df.shape}")
        print(df.head(3).to_string())
