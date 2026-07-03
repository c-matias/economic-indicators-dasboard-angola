# 📊 Dashboard de Indicadores Económicos — Angola

> Pipeline ETL completo + dashboard interactivo para indicadores macroeconómicos de Angola (2014–2024).
> Construído com Python · Pandas · Plotly · Netlify.

**🔗 Demo ao vivo:** [angola-dashboard.netlify.app](https://angola-dashboard.netlify.app)

---

## Visão geral

Este projecto implementa um pipeline de dados de ponta a ponta:

```
INE / BNA  →  extract.py  →  transform.py  →  load.py  →  visualize.py  →  Netlify
   (raw)        (Stage 1)      (Stage 2)      (Stage 3)    (8 charts)      (deploy)
```

O resultado é um site estático completamente interactivo — sem servidor, sem base de dados em produção — publicado automaticamente via Netlify.

---

## Demo

| Página | Conteúdo |
|--------|----------|
| **Visão Geral** | KPIs · PIB · Inflação vs Juro · Câmbio AOA/USD |
| **Inflação e Câmbio** | Série histórica · MA4 · Scatter · Correlation Matrix |
| **Mercado de Trabalho** | Desemprego · Juro real · Composição PIB |
| **Análise Provincial** | Índice de Desenvolvimento · Bubble Chart · Tabela 18 províncias |
| **Pipeline de Dados** | Arquitectura ETL · Stack · Transformações · Estrutura repo |

---

## Stack

| Camada | Ferramentas |
|--------|-------------|
| Linguagem | Python 3.11 |
| Dados | Pandas · NumPy |
| Estatística | SciPy · StatsModels |
| Visualização | Plotly 5.x |
| Frontend | HTML · CSS · Chart.js |
| Deploy | Netlify (site estático) |
| CI/CD | GitHub Actions |
| Controlo de versões | Git |

---

## Estrutura do repositório

```
angola-dashboard/
├── public/                          ← raiz do site (publicada pelo Netlify)
│   ├── index.html                   ← dashboard interactivo principal
│   └── visuals/
│       ├── index.html               ← galeria de charts
│       ├── 01_inflacao_serie_temporal.html
│       ├── 02_taxa_de_cambio.html
│       ├── 03_pib_crescimento.html
│       ├── 04_multi_indicador.html
│       ├── 05_correlation_heatmap.html
│       ├── 06_bolhas_provinciais.html
│       ├── 07_scatter_inflacao_cambio.html
│       └── 08_indice_desenvolvimento.html
│
├── scripts/
│   ├── extract.py                   ← Stage 1: extracção (INE / BNA)
│   ├── transform.py                 ← Stage 2: limpeza + feature engineering
│   └── load.py                      ← Stage 3: persistência CSV + SQLite
│
├── data/
│   ├── raw/
│   │   ├── macro_angola.csv         ← série trimestral 2014–2024
│   │   └── provinces_angola.csv     ← 18 províncias
│   └── processed/                   ← gerado pelo pipeline
│       ├── macro_processado.csv
│       ├── provincias_processadas.csv
│       ├── agregados_anuais.csv
│       ├── correlation_matrix.csv
│       └── summary_stats.csv
│
├── main.py                          ← orquestrador do pipeline
├── visualize.py                     ← motor de charts Plotly
├── Makefile                         ← automação local
├── netlify.toml                     ← configuração Netlify
├── requirements.txt
└── .github/
    └── workflows/
        └── pipeline.yml             ← GitHub Actions CI
```

---

## Instalação e uso local

```bash
# 1. Clonar
git clone https://github.com/c-matias/angola-dashboard.git
cd angola-dashboard

# 2. Instalar e correr tudo
make instalar
make tudo

# 3. Abrir no browser
make dashboard
```

### Comandos disponíveis

| Comando | Descrição |
|---------|-----------|
| `make instalar` | Cria `.venv` e instala dependências |
| `make pipeline` | Corre Extract → Transform → Load |
| `make charts` | Gera os 8 charts Plotly em `visuals/` |
| `make tudo` | Pipeline + charts completo |
| `make dashboard` | Abre `public/index.html` no browser |
| `make verificar` | Valida dependências e estrutura |
| `make info` | Mostra estado dos ficheiros gerados |
| `make limpar` | Remove ficheiros processados |

---

## Deploy no Netlify

### Opção A — Deploy automático via GitHub (recomendado)

1. Fazer fork ou push deste repositório para o teu GitHub
2. Entrar em [app.netlify.com](https://app.netlify.com) → **Add new site** → **Import from Git**
3. Seleccionar o repositório
4. O Netlify detecta automaticamente o `netlify.toml`:
   - **Publish directory:** `public`
   - **Build command:** *(vazio — site estático)*
5. Clicar **Deploy site** — o site fica online em segundos

### Opção B — Deploy manual (drag & drop)

```bash
# Gerar o site localmente
make tudo

# Arrastar a pasta public/ para app.netlify.com/drop
```

### Domínio personalizado

No painel Netlify: **Domain settings** → **Add custom domain** → `angola-dashboard.netlify.app` ou domínio próprio.

---

## Pipeline de dados

### Stage 1 — Extract (`scripts/extract.py`)
Leitura dos CSV de `data/raw/`. Extensível para APIs REST do INE e BNA.

### Stage 2 — Transform (`scripts/transform.py`)

| Transformação | Descrição |
|---------------|-----------|
| **Parsing de datas** | `year` + `quarter` → `datetime` |
| **Missing values** | Forward-fill + back-fill |
| **MA4** | Moving average de 4 trimestres |
| **Derivadas** | Variação QoQ · Taxa de juro real |
| **Min-max** | Normalização [0, 1] para correlação |
| **IDH proxy** | Índice composto provincial |
| **Pearson** | Correlation matrix 6×6 |
| **Períodos** | Labels de regime económico |

### Stage 3 — Load (`scripts/load.py`)
Persistência em CSV (`data/processed/`) e SQLite (`data/angola_economics.db`).

---

## Principais conclusões (2014–2024)

- **Pico de inflação:** 41,9% em Q4 2016 — crise do preço do petróleo
- **Desvalorização cambial:** AOA 97,6 → 961 por USD — queda de 885%
- **Correlação forte:** câmbio × taxa de juro (Pearson r = 0,748)
- **Juro real negativo em 2024:** −8,8% — poupança das famílias destruída
- **Concentração económica:** Luanda representa 52,4% do PIB
- **Disparidade de desenvolvimento:** Luanda (IDH 85) vs Cunene (IDH 32)

---

## Fontes de dados

| Fonte | Descrição |
|-------|-----------|
| [INE Angola](https://www.ine.gov.ao) | Instituto Nacional de Estatística — PIB, inflação, população |
| [BNA](https://www.bna.ao) | Banco Nacional de Angola — câmbio, taxas de juro |

> Os dados são simulados realisticamente com base em publicações oficiais do INE e BNA para fins de portfólio.

---

## Autor

**Clauder Matias** — Data Analyst & Engineer  
[github.com/c-matias](https://github.com/c-matias) · 42 Luanda / ISPTEC

---

## Licença

MIT — livre para usar, adaptar e distribuir com atribuição.
