# =============================================================================
#  Makefile — Dashboard de Indicadores Económicos — Angola
#  Pipeline ETL: Python · Pandas · Plotly
#
#  Utilização:
#    make instalar     — instala as dependências Python
#    make pipeline     — corre o pipeline completo (extract → transform → load)
#    make charts       — gera os 8 charts Plotly em visuals/
#    make tudo         — pipeline + charts
#    make dashboard    — abre o dashboard interactivo no browser
#    make limpar       — remove ficheiros processados e charts gerados
#    make limpar-tudo  — remove também o ambiente virtual
#    make verificar    — verifica se as dependências estão instaladas
#    make info         — mostra o estado actual do projecto
# =============================================================================

# ── Configuração ──────────────────────────────────────────────────────────────
PYTHON      := python3
VENV        := .venv
PIP         := $(VENV)/bin/pip
PY          := $(VENV)/bin/python
REQUIREMENTS := requirements.txt

# Sistema operativo (para abrir o browser)
UNAME := $(shell uname -s)
ifeq ($(UNAME), Darwin)
    ABRIR := open
else ifeq ($(UNAME), Linux)
    ABRIR := xdg-open
else
    ABRIR := start
endif

# Cores para output no terminal
VERDE  := \033[0;32m
AMARELO:= \033[0;33m
AZUL   := \033[0;34m
RESET  := \033[0m
NEGRITO:= \033[1m

# ── Alvos principais ──────────────────────────────────────────────────────────

.PHONY: ajuda instalar pipeline charts tudo dashboard limpar limpar-tudo verificar info

## Alvo por omissão: mostrar ajuda
ajuda:
	@echo ""
	@echo "$(NEGRITO)Dashboard de Indicadores Económicos — Angola$(RESET)"
	@echo "$(AZUL)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)"
	@echo ""
	@echo "  $(VERDE)make instalar$(RESET)      Instala as dependências em ambiente virtual"
	@echo "  $(VERDE)make pipeline$(RESET)      Corre o pipeline ETL completo"
	@echo "  $(VERDE)make charts$(RESET)        Gera os 8 charts Plotly interactivos"
	@echo "  $(VERDE)make tudo$(RESET)          Pipeline + charts (recomendado)"
	@echo "  $(VERDE)make dashboard$(RESET)     Abre o dashboard no browser"
	@echo "  $(VERDE)make limpar$(RESET)        Remove ficheiros gerados (processed + visuals)"
	@echo "  $(VERDE)make limpar-tudo$(RESET)   Remove tudo incluindo o ambiente virtual"
	@echo "  $(VERDE)make verificar$(RESET)     Verifica dependências e estrutura"
	@echo "  $(VERDE)make info$(RESET)          Estado actual do projecto"
	@echo ""
	@echo "  $(AMARELO)Início rápido:$(RESET)  make instalar && make tudo && make dashboard"
	@echo ""

## Criar ambiente virtual e instalar dependências
instalar: $(VENV)/bin/activate
	@echo "$(VERDE)✓ Dependências instaladas$(RESET)"

$(VENV)/bin/activate: $(REQUIREMENTS)
	@echo "$(AZUL)→ A criar ambiente virtual em $(VENV)/...$(RESET)"
	$(PYTHON) -m venv $(VENV)
	@echo "$(AZUL)→ A instalar dependências de $(REQUIREMENTS)...$(RESET)"
	$(PIP) install --upgrade pip --quiet
	$(PIP) install -r $(REQUIREMENTS) --quiet
	@touch $(VENV)/bin/activate

## Correr o pipeline ETL completo (extract → transform → load)
pipeline: $(VENV)/bin/activate
	@echo ""
	@echo "$(AZUL)$(NEGRITO)▶ A correr o pipeline ETL...$(RESET)"
	@echo "$(AZUL)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)"
	$(PY) main.py --sem-visuals 2>&1 || $(PY) -c "\
import sys; sys.path.insert(0, 'scripts'); \
from extract import extract_all; \
from transform import transform_all; \
from load import load_all; \
raw = extract_all(); \
t = transform_all(raw); \
load_all(t, usar_sqlite=True); \
print('Pipeline concluído.')"
	@echo ""
	@echo "$(VERDE)✓ Pipeline concluído — ficheiros em data/processed/$(RESET)"

## Gerar os 8 charts Plotly interactivos
charts: $(VENV)/bin/activate
	@echo ""
	@echo "$(AZUL)$(NEGRITO)▶ A gerar charts Plotly...$(RESET)"
	@echo "$(AZUL)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)"
	$(PY) visualize.py
	@echo ""
	@echo "$(VERDE)✓ Charts guardados em visuals/$(RESET)"
	@ls visuals/*.html 2>/dev/null | sed 's/^/    /'

## Pipeline completo + charts
tudo: instalar pipeline charts
	@echo ""
	@echo "$(VERDE)$(NEGRITO)✓ Projecto pronto.$(RESET)"
	@echo "  Dashboard:  dashboard.html"
	@echo "  Charts:     visuals/"
	@echo "  Dados:      data/processed/"
	@echo ""
	@echo "  Abrir dashboard:  $(NEGRITO)make dashboard$(RESET)"

## Abrir o dashboard interactivo no browser
dashboard:
	@if [ ! -f "dashboard.html" ]; then \
		echo "$(AMARELO)⚠  dashboard.html não encontrado — a correr 'make tudo' primeiro...$(RESET)"; \
		$(MAKE) tudo; \
	fi
	@echo "$(AZUL)→ A abrir dashboard.html no browser...$(RESET)"
	$(ABRIR) dashboard.html 2>/dev/null || \
		echo "$(AMARELO)⚠  Não foi possível abrir automaticamente. Abra manualmente: dashboard.html$(RESET)"

## Abrir um chart específico (ex: make chart NOME=01_inflacao_serie_temporal)
chart:
	@if [ -z "$(NOME)" ]; then \
		echo "$(AMARELO)Utilização: make chart NOME=01_inflacao_serie_temporal$(RESET)"; \
		echo "Charts disponíveis:"; \
		ls visuals/*.html 2>/dev/null | xargs -n1 basename | sed 's/.html//' | sed 's/^/  /'; \
	else \
		$(ABRIR) visuals/$(NOME).html 2>/dev/null || \
		echo "$(AMARELO)Chart não encontrado: visuals/$(NOME).html$(RESET)"; \
	fi

## Verificar dependências e estrutura do projecto
verificar:
	@echo ""
	@echo "$(AZUL)$(NEGRITO)Verificação do projecto$(RESET)"
	@echo "$(AZUL)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)"
	@echo ""
	@echo "$(NEGRITO)Python:$(RESET)"
	@$(PYTHON) --version 2>&1 | sed 's/^/  /'
	@echo ""
	@echo "$(NEGRITO)Ambiente virtual:$(RESET)"
	@if [ -d "$(VENV)" ]; then \
		echo "  $(VERDE)✓ $(VENV)/ existe$(RESET)"; \
	else \
		echo "  $(AMARELO)✗ não encontrado — correr: make instalar$(RESET)"; \
	fi
	@echo ""
	@echo "$(NEGRITO)Dependências:$(RESET)"
	@for pkg in pandas numpy plotly scipy statsmodels openpyxl; do \
		if $(PY) -c "import $$pkg" 2>/dev/null; then \
			ver=$$($(PY) -c "import $$pkg; print($$pkg.__version__)" 2>/dev/null); \
			echo "  $(VERDE)✓ $$pkg $$ver$(RESET)"; \
		else \
			echo "  $(AMARELO)✗ $$pkg — não instalado$(RESET)"; \
		fi; \
	done 2>/dev/null || \
	for pkg in pandas numpy plotly scipy statsmodels openpyxl; do \
		echo "  ? $$pkg — ambiente virtual não activo"; \
	done
	@echo ""
	@echo "$(NEGRITO)Dados raw:$(RESET)"
	@for f in data/raw/macro_angola.csv data/raw/provinces_angola.csv; do \
		if [ -f "$$f" ]; then \
			linhas=$$(wc -l < $$f); \
			echo "  $(VERDE)✓ $$f ($$linhas linhas)$(RESET)"; \
		else \
			echo "  $(AMARELO)✗ $$f — não encontrado$(RESET)"; \
		fi; \
	done
	@echo ""
	@echo "$(NEGRITO)Scripts:$(RESET)"
	@for f in scripts/extract.py scripts/transform.py scripts/load.py main.py visualize.py; do \
		if [ -f "$$f" ]; then \
			echo "  $(VERDE)✓ $$f$(RESET)"; \
		else \
			echo "  $(AMARELO)✗ $$f — não encontrado$(RESET)"; \
		fi; \
	done
	@echo ""

## Mostrar estado actual do projecto
info:
	@echo ""
	@echo "$(AZUL)$(NEGRITO)Estado do projecto$(RESET)"
	@echo "$(AZUL)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(RESET)"
	@echo ""
	@echo "$(NEGRITO)Dados processados:$(RESET)"
	@if ls data/processed/*.csv 2>/dev/null | grep -q csv; then \
		ls -lh data/processed/*.csv | awk '{print "  " $$5 "  " $$9}'; \
	else \
		echo "  (nenhum — correr: make pipeline)"; \
	fi
	@echo ""
	@echo "$(NEGRITO)Charts gerados:$(RESET)"
	@if ls visuals/*.html 2>/dev/null | grep -q html; then \
		ls visuals/*.html | xargs -n1 basename | sed 's/^/  /'; \
	else \
		echo "  (nenhum — correr: make charts)"; \
	fi
	@echo ""
	@echo "$(NEGRITO)Base de dados SQLite:$(RESET)"
	@if [ -f "data/angola_economics.db" ]; then \
		tam=$$(du -h data/angola_economics.db | cut -f1); \
		echo "  $(VERDE)✓ data/angola_economics.db ($$tam)$(RESET)"; \
	else \
		echo "  (não existe — correr: make pipeline)"; \
	fi
	@echo ""

## Remover ficheiros gerados (manter dados raw)
limpar:
	@echo "$(AMARELO)→ A remover ficheiros processados e charts...$(RESET)"
	rm -f data/processed/*.csv
	rm -f data/angola_economics.db
	rm -f visuals/*.html
	@echo "$(VERDE)✓ Limpeza concluída$(RESET)"
	@echo "  (dados raw em data/raw/ foram preservados)"

## Remover tudo incluindo o ambiente virtual
limpar-tudo: limpar
	@echo "$(AMARELO)→ A remover ambiente virtual...$(RESET)"
	rm -rf $(VENV)
	rm -rf scripts/__pycache__
	rm -rf __pycache__
	@echo "$(VERDE)✓ Limpeza total concluída$(RESET)"

# ── Atalhos ───────────────────────────────────────────────────────────────────

## Alias: executar = tudo
executar: tudo

## Alias: instalar + pipeline numa só linha
configurar: instalar pipeline
	@echo "$(VERDE)✓ Projecto configurado$(RESET)"

# ── Regras de ficheiro ────────────────────────────────────────────────────────

# Regenerar dados processados se os raw mudarem
data/processed/macro_processado.csv: data/raw/macro_angola.csv data/raw/provinces_angola.csv
	@$(MAKE) pipeline

# Regenerar charts se os dados mudarem
visuals/01_inflacao_serie_temporal.html: data/processed/macro_processado.csv
	@$(MAKE) charts
