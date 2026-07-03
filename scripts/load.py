"""
load.py — Stage 3: Carregamento e Persistência
Dashboard de Indicadores Económicos — Angola

Responsabilidade deste módulo:
  - Escrita dos DataFrames processados em CSV (data/processed/)
  - Escrita opcional numa base de dados SQLite (angola_economics.db)
  - Geração de estatísticas descritivas (summary stats)
  - Geração de agregados anuais para consumo pelo Power BI
"""

import os
import sqlite3
import logging
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
DB_PATH       = os.path.join(os.path.dirname(__file__), "..", "data", "angola_economics.db")


# ── Utilitários ───────────────────────────────────────────────────────────────

def _garantir_diretorios():
    os.makedirs(PROCESSED_DIR, exist_ok=True)


def _guardar_csv(df: pd.DataFrame, nome_ficheiro: str):
    caminho = os.path.join(PROCESSED_DIR, nome_ficheiro)
    df.to_csv(caminho, index=False)
    logger.info(f"CSV guardado: {caminho}  ({len(df)} registos)")


def _guardar_sqlite(datasets: dict):
    """Escreve todos os DataFrames numa base de dados SQLite."""
    conn = sqlite3.connect(DB_PATH)
    try:
        for nome_tabela, df in datasets.items():
            if isinstance(df, pd.DataFrame):
                df.to_sql(nome_tabela, conn, if_exists="replace", index=False)
                logger.info(f"Tabela SQLite '{nome_tabela}': {len(df)} registos")
        conn.commit()
        logger.info(f"Base de dados SQLite guardada: {DB_PATH}")
    except Exception as e:
        logger.error(f"Erro SQLite: {e}")
    finally:
        conn.close()


# ── Agregações ────────────────────────────────────────────────────────────────

def _gerar_summary_stats(df_macro: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula estatísticas descritivas para o dataset macro processado.
    Inclui coeficiente de variação (CV%) como métrica de dispersão relativa.
    """
    numericas = df_macro.select_dtypes(include="number")
    stats = numericas.describe().T.round(3)
    stats["cv_pct"] = ((stats["std"] / stats["mean"]) * 100).round(1)
    return stats


def _gerar_agregados_anuais(df_macro: pd.DataFrame) -> pd.DataFrame:
    """Médias anuais de todos os indicadores-chave — formato ideal para Power BI."""
    return df_macro.groupby("year").agg(
        pib_medio_usd_bi    = ("gdp_usd_billion",       "mean"),
        crescimento_medio   = ("gdp_growth_pct",        "mean"),
        inflacao_media      = ("inflation_pct",         "mean"),
        cambio_medio        = ("exchange_rate_aoa_usd", "mean"),
        juro_medio          = ("interest_rate_pct",     "mean"),
        desemprego_medio    = ("unemployment_pct",      "mean"),
        juro_real_medio     = ("taxa_juro_real",        "mean"),
    ).round(2).reset_index()


# ── Pipeline entry point ──────────────────────────────────────────────────────

def load_all(dados_transformados: dict, usar_sqlite: bool = True) -> dict:
    """
    Persiste todos os datasets transformados.
    Retorna o dict de DataFrames finais (incluindo agregados anuais).
    """
    logger.info("=== LOAD — INÍCIO ===")
    _garantir_diretorios()

    macro      = dados_transformados["macro"]
    provincias = dados_transformados["provincias"]
    correlacao = dados_transformados["correlacao"]

    # CSVs principais
    _guardar_csv(macro,                   "macro_processado.csv")
    _guardar_csv(provincias,              "provincias_processadas.csv")
    _guardar_csv(correlacao.reset_index(),"correlation_matrix.csv")

    # Summary stats
    stats = _gerar_summary_stats(macro)
    _guardar_csv(stats.reset_index(), "summary_stats.csv")
    logger.info("Summary statistics geradas")

    # Agregados anuais
    anuais = _gerar_agregados_anuais(macro)
    _guardar_csv(anuais, "agregados_anuais.csv")

    # SQLite (opcional)
    if usar_sqlite:
        _guardar_sqlite({
            "macro":      macro,
            "provincias": provincias,
            "anuais":     anuais,
        })

    logger.info("=== LOAD — CONCLUÍDO ===")
    return {
        "macro":      macro,
        "provincias": provincias,
        "anuais":     anuais,
        "correlacao": correlacao,
    }


# ── Execução directa ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    from extract import extract_all
    from transform import transform_all

    raw          = extract_all()
    transformados = transform_all(raw)
    final        = load_all(transformados)
    print(f"\nPipeline concluído. Ficheiros em: {PROCESSED_DIR}")
