"""
main.py — Orquestrador do Pipeline ETL
Dashboard de Indicadores Económicos — Angola

Execução: python main.py

Stages executadas em sequência:
  1. Extract  — leitura dos ficheiros raw (INE / BNA)
  2. Transform — limpeza, feature engineering, normalização
  3. Load      — persistência em CSV + SQLite
  4. Visualize — geração dos charts Plotly (HTML interactivos)
"""

import os
import sys
import logging
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts"))

from extract   import extract_all
from transform import transform_all
from load      import load_all

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def executar_pipeline():
    inicio = time.time()
    logger.info("══════════════════════════════════════════════════════")
    logger.info("   Dashboard de Indicadores Económicos — Angola       ")
    logger.info("   Pipeline ETL  ·  Python · Pandas · Plotly          ")
    logger.info("══════════════════════════════════════════════════════")

    # Stage 1 — Extract
    dados_raw = extract_all()

    # Stage 2 — Transform
    dados_transformados = transform_all(dados_raw)

    # Stage 3 — Load
    dados_finais = load_all(dados_transformados, usar_sqlite=True)

    # Stage 4 — Visualize
    logger.info("A gerar visualizações Plotly...")
    try:
        from visualize import gerar_todos_os_charts
        gerar_todos_os_charts(dados_finais)
        logger.info("Charts guardados em /visuals/")
    except Exception as e:
        logger.warning(f"Passo de visualização ignorado: {e}")

    duracao = round(time.time() - inicio, 2)
    logger.info(f"Pipeline concluído em {duracao}s")
    logger.info("══════════════════════════════════════════════════════")

    return dados_finais


if __name__ == "__main__":
    executar_pipeline()
