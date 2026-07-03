"""
visualize.py — Motor de Visualizações Plotly
Dashboard de Indicadores Económicos — Angola

Gera 8 charts interactivos em HTML standalone usando Plotly.
Cada chart é guardado em visuals/ e pode ser aberto directamente no browser
ou embebido numa aplicação web / relatório Power BI via iframe.

Paleta de cores inspirada na bandeira de Angola (vermelho, preto, dourado)
complementada com teal para indicadores positivos e slate para contexto.
"""

import os
import logging
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

VISUALS_DIR = os.path.join(os.path.dirname(__file__), "visuals")

# ── Paleta ────────────────────────────────────────────────────────────────────
CORES = {
    "vermelho":  "#CC0000",
    "preto":     "#0D0D0D",
    "dourado":   "#F5C518",
    "teal":      "#00A693",
    "slate":     "#2C3E50",
    "muted":     "#7F8C8D",
    "fundo":     "#FAFAFA",
    "grid":      "#E8E8E8",
}

CORES_PERIODO = {
    "Pré-crise petrolífera": "#27AE60",
    "Crise 2015–2017":       "#E74C3C",
    "Recuperação Lourenço":  "#3498DB",
    "Impacto COVID-19":      "#E67E22",
    "Estabilização":         "#9B59B6",
}

BASE_LAYOUT = dict(
    font        = dict(family="Georgia, serif", size=13, color=CORES["slate"]),
    paper_bgcolor = "white",
    plot_bgcolor  = CORES["fundo"],
    margin      = dict(t=80, b=60, l=70, r=40),
    legend      = dict(bgcolor="rgba(255,255,255,0.9)",
                       bordercolor=CORES["grid"], borderwidth=1),
)


def _guardar(fig: go.Figure, nome: str):
    os.makedirs(VISUALS_DIR, exist_ok=True)
    caminho = os.path.join(VISUALS_DIR, f"{nome}.html")
    fig.write_html(caminho, include_plotlyjs="cdn")
    logger.info(f"Chart guardado: {caminho}")


# ── Chart 1 — Inflação (série temporal) ──────────────────────────────────────

def chart_inflacao(macro: pd.DataFrame):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=macro["date"], y=macro["inflation_pct"],
        name="Inflação (%)", mode="lines+markers",
        line=dict(color=CORES["vermelho"], width=2.5),
        marker=dict(size=4),
    ))
    fig.add_trace(go.Scatter(
        x=macro["date"], y=macro["inflation_pct_ma4"],
        name="Moving Average 4T", mode="lines",
        line=dict(color=CORES["dourado"], width=2, dash="dash"),
    ))
    fig.add_vrect(
        x0="2020-01-01", x1="2021-01-01",
        fillcolor="#E67E22", opacity=0.08, line_width=0,
        annotation_text="COVID-19", annotation_position="top left",
    )
    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(
            text="<b>Taxa de Inflação — Angola (2014–2024)</b><br>"
                 "<sub>Fonte: INE Angola | Percentagem anual</sub>",
            x=0.02,
        ),
        xaxis=dict(title="", showgrid=True, gridcolor=CORES["grid"]),
        yaxis=dict(title="Inflação (%)", showgrid=True, gridcolor=CORES["grid"]),
        hovermode="x unified",
    )
    _guardar(fig, "01_inflacao_serie_temporal")


# ── Chart 2 — Taxa de câmbio AOA/USD ─────────────────────────────────────────

def chart_cambio(macro: pd.DataFrame):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[0.7, 0.3], vertical_spacing=0.05)
    fig.add_trace(go.Scatter(
        x=macro["date"], y=macro["exchange_rate_aoa_usd"],
        name="AOA/USD", mode="lines",
        line=dict(color=CORES["slate"], width=2.5),
        fill="tozeroy", fillcolor="rgba(44,62,80,0.08)",
    ), row=1, col=1)
    fig.add_trace(go.Bar(
        x=macro["date"], y=macro["fx_variacao_qoq"],
        name="Variação QoQ (%)",
        marker_color=np.where(
            macro["fx_variacao_qoq"] >= 0, CORES["vermelho"], CORES["teal"]
        ),
    ), row=2, col=1)
    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(
            text="<b>Taxa de Câmbio AOA/USD (2014–2024)</b><br>"
                 "<sub>Fonte: BNA — Banco Nacional de Angola</sub>",
            x=0.02,
        ),
        hovermode="x unified",
        showlegend=False,
    )
    fig.update_yaxes(title_text="AOA por 1 USD", row=1, col=1)
    fig.update_yaxes(title_text="Var. QoQ (%)",  row=2, col=1)
    _guardar(fig, "02_taxa_de_cambio")


# ── Chart 3 — PIB e crescimento ───────────────────────────────────────────────

def chart_pib(macro: pd.DataFrame):
    anuais = macro.groupby("year").agg(
        pib     = ("gdp_usd_billion", "mean"),
        crescimento = ("gdp_growth_pct", "mean"),
    ).reset_index()

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(
        x=anuais["year"], y=anuais["pib"],
        name="PIB (USD Bi)", marker_color=CORES["teal"], opacity=0.85,
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=anuais["year"], y=anuais["crescimento"],
        name="Crescimento (%)", mode="lines+markers",
        line=dict(color=CORES["vermelho"], width=2.5),
        marker=dict(size=8, symbol="diamond"),
    ), secondary_y=True)
    fig.add_hline(y=0, line_dash="dot", line_color=CORES["muted"], secondary_y=True)
    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(
            text="<b>PIB e Crescimento Económico — Angola</b><br>"
                 "<sub>Fonte: BNA / INE Angola | Médias anuais</sub>",
            x=0.02,
        ),
        hovermode="x unified",
    )
    fig.update_yaxes(title_text="PIB (USD Bilhões)", secondary_y=False)
    fig.update_yaxes(title_text="Taxa de Crescimento (%)", secondary_y=True)
    _guardar(fig, "03_pib_crescimento")


# ── Chart 4 — Comparação multi-indicador ─────────────────────────────────────

def chart_multi_indicador(macro: pd.DataFrame):
    anuais = macro.groupby("year").agg(
        inflacao    = ("inflation_pct",     "mean"),
        desemprego  = ("unemployment_pct",  "mean"),
        juro        = ("interest_rate_pct", "mean"),
        juro_real   = ("taxa_juro_real",    "mean"),
    ).reset_index()

    fig = go.Figure()
    series = [
        ("inflacao",   "Inflação",        CORES["vermelho"], "circle"),
        ("desemprego", "Desemprego",      CORES["dourado"],  "square"),
        ("juro",       "Taxa de Juro",    CORES["teal"],     "diamond"),
        ("juro_real",  "Juro Real",       CORES["slate"],    "triangle-up"),
    ]
    for col, rotulo, cor, simbolo in series:
        fig.add_trace(go.Scatter(
            x=anuais["year"], y=anuais[col],
            name=rotulo, mode="lines+markers",
            line=dict(color=cor, width=2),
            marker=dict(size=7, symbol=simbolo),
        ))
    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(
            text="<b>Comparação de Indicadores Macroeconómicos (2014–2024)</b>",
            x=0.02,
        ),
        xaxis=dict(title="Ano",   showgrid=True, gridcolor=CORES["grid"]),
        yaxis=dict(title="Taxa (%)", showgrid=True, gridcolor=CORES["grid"]),
        hovermode="x unified",
    )
    _guardar(fig, "04_multi_indicador")


# ── Chart 5 — Correlation heatmap ────────────────────────────────────────────

def chart_correlation_heatmap(corr_matrix: pd.DataFrame):
    labels_pt = {
        "gdp_growth_pct":        "Crescimento PIB",
        "inflation_pct":         "Inflação",
        "exchange_rate_aoa_usd": "Câmbio AOA/USD",
        "interest_rate_pct":     "Taxa de Juro",
        "unemployment_pct":      "Desemprego",
        "oil_revenue_pct_gdp":   "Receita Petrolífera",
    }
    matrix = corr_matrix.rename(index=labels_pt, columns=labels_pt)

    fig = go.Figure(go.Heatmap(
        z           = matrix.values,
        x           = matrix.columns.tolist(),
        y           = matrix.index.tolist(),
        colorscale  = [[0, "#2980B9"], [0.5, "#FAFAFA"], [1, "#C0392B"]],
        zmid=0, zmin=-1, zmax=1,
        text        = matrix.values.round(2),
        texttemplate= "%{text}",
        textfont    = dict(size=12),
        colorbar    = dict(title="r", tickvals=[-1, -0.5, 0, 0.5, 1]),
    ))
    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(
            text="<b>Correlation Matrix — Indicadores Económicos de Angola</b>",
            x=0.02,
        ),
        xaxis=dict(tickangle=-30),
        height=520,
    )
    _guardar(fig, "05_correlation_heatmap")


# ── Chart 6 — Bubble chart provincial ────────────────────────────────────────

def chart_bolhas_provinciais(provincias: pd.DataFrame):
    fig = px.scatter(
        provincias,
        x="unemployment_pct", y="literacy_rate_pct",
        size="populacao_milhoes", color="regiao",
        text="province",
        size_max=60,
        color_discrete_map={
            "Norte":  CORES["teal"],
            "Centro": CORES["slate"],
            "Sul":    CORES["vermelho"],
            "Leste":  CORES["dourado"],
        },
        labels={
            "unemployment_pct":  "Taxa de Desemprego (%)",
            "literacy_rate_pct": "Taxa de Literacia (%)",
            "regiao":            "Região",
        },
    )
    fig.update_traces(textposition="top center", textfont_size=10)
    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(
            text="<b>Desemprego vs Literacia por Província — Angola</b><br>"
                 "<sub>Tamanho = população | Cor = região</sub>",
            x=0.02,
        ),
    )
    _guardar(fig, "06_bolhas_provinciais")


# ── Chart 7 — Scatter inflação × câmbio ──────────────────────────────────────

def chart_scatter_inflacao_cambio(macro: pd.DataFrame):
    fig = px.scatter(
        macro,
        x="exchange_rate_aoa_usd", y="inflation_pct",
        color="periodo_economico",
        trendline="ols",
        color_discrete_map=CORES_PERIODO,
        labels={
            "exchange_rate_aoa_usd": "Taxa de Câmbio (AOA/USD)",
            "inflation_pct":         "Inflação (%)",
            "periodo_economico":     "Período",
        },
        hover_data=["year", "quarter"],
    )
    fig.update_layout(
        **BASE_LAYOUT,
        title=dict(
            text="<b>Correlação: Inflação × Taxa de Câmbio AOA/USD</b>",
            x=0.02,
        ),
    )
    _guardar(fig, "07_scatter_inflacao_cambio")


# ── Chart 8 — Índice de desenvolvimento provincial ───────────────────────────

def chart_indice_desenvolvimento(provincias: pd.DataFrame):
    df = provincias.sort_values("indice_desenvolvimento", ascending=True)
    fig = go.Figure(go.Bar(
        x=df["indice_desenvolvimento"], y=df["province"],
        orientation="h",
        marker=dict(
            color=df["indice_desenvolvimento"],
            colorscale=[[0, CORES["vermelho"]], [0.5, CORES["dourado"]], [1, CORES["teal"]]],
            showscale=True,
            colorbar=dict(title="Índice"),
        ),
        text=df["indice_desenvolvimento"].round(1),
        textposition="outside",
    ))
    layout = {**BASE_LAYOUT}
    layout["margin"] = dict(t=80, b=60, l=160, r=40)
    fig.update_layout(
        **layout,
        title=dict(
            text="<b>Índice de Desenvolvimento por Província — Angola</b><br>"
                 "<sub>Proxy IDH: Literacia 35% · Electrificação 35% · (100−Pobreza) 30%</sub>",
            x=0.02,
        ),
        xaxis=dict(title="Índice (0–100)", showgrid=True, gridcolor=CORES["grid"]),
        yaxis=dict(title=""),
        height=620,
    )
    _guardar(fig, "08_indice_desenvolvimento")


# ── Função principal ──────────────────────────────────────────────────────────

def gerar_todos_os_charts(dados: dict):
    logger.info("A gerar todos os charts Plotly...")
    macro      = dados["macro"]
    provincias = dados["provincias"]
    correlacao = dados["correlacao"]

    chart_inflacao(macro)
    chart_cambio(macro)
    chart_pib(macro)
    chart_multi_indicador(macro)
    chart_correlation_heatmap(correlacao)
    chart_bolhas_provinciais(provincias)
    chart_scatter_inflacao_cambio(macro)
    chart_indice_desenvolvimento(provincias)

    logger.info(f"Todos os charts guardados em: {VISUALS_DIR}")


# ── Execução directa ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts"))
    from extract   import extract_all
    from transform import transform_all
    from load      import load_all

    raw           = extract_all()
    transformados = transform_all(raw)
    final         = load_all(transformados, usar_sqlite=False)
    gerar_todos_os_charts(final)
