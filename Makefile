# Bridge GAD Generator — Unified task runner
# Usage: make <target>
# Requires: Python 3.11+, pip, docker (optional)

PYTHON   := python
PIP      := pip
APP      := streamlit_app_ultimate.py
API_HOST := 127.0.0.1
API_PORT := 8000
UI_PORT  := 8501

.PHONY: help dev build test worker docker lint fmt typecheck clean install

help:
	@echo ""
	@echo "  Bridge GAD Generator — available targets"
	@echo "  ─────────────────────────────────────────"
	@echo "  make install    Install all dependencies"
	@echo "  make dev        Run Streamlit UI (dev mode)"
	@echo "  make api        Run FastAPI server"
	@echo "  make worker     Run ARQ async worker"
	@echo "  make build      Build Python package"
	@echo "  make test       Run test suite"
	@echo "  make lint       Run flake8 linter"
	@echo "  make fmt        Run black formatter"
	@echo "  make typecheck  Run mypy type checker"
	@echo "  make docker     Build Docker image"
	@echo "  make clean      Remove build artifacts"
	@echo ""

install:
	$(PIP) install -e ".[dev]"

dev:
	streamlit run $(APP) --server.port=$(UI_PORT) --server.address=0.0.0.0

api:
	uvicorn bridge_gad.api:app --host $(API_HOST) --port $(API_PORT) --reload

worker:
	$(PYTHON) -m bridge_gad.worker

build:
	$(PIP) install build
	$(PYTHON) -m build

test:
	$(PYTHON) -m pytest test_ultimate_app.py -v --tb=short

lint:
	flake8 src/ --max-line-length=120 --ignore=E501,W503,E402 --count

fmt:
	black src/ streamlit_app_ultimate.py app_lean.py test_ultimate_app.py

typecheck:
	mypy src/bridge_gad/ --ignore-missing-imports --no-error-summary

docker:
	docker build -t bridge-gad:latest .

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name dist -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name build -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
