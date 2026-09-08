VENV = venv
PYTHON := $(VENV)/bin/python3
PIP := $(VENV)/bin/pip
CONFIG := config.txt

YELLOW = \033[33m
BOLD   := \033[1m

.PHONY: venv install run debug clean lint

.DEFAULT_GOAL := help

venv:
	@python3 -m venv $(VENV)
	@echo "Virtual environment created"

install: venv
	@echo "Installing project dependencies..."
	@UV_SKIP_WHEEL_FILENAME_CHECK=1 uv sync --all-groups

run:
	@UV_SKIP_WHEEL_FILENAME_CHECK=1 PYGAME_HIDE_SUPPORT_PROMPT=1 uv run pac-man.py data/settings/settings.json

dist:
	@UV_SKIP_WHEEL_FILENAME_CHECK=1  uv run cxfreeze --script pac-man.py --target-dir dist
	@cp -r data dist/data
	@cd dist && tar -c -f ../pac-man .

debug: install
	@echo "Launching Pac-Man in debug mode..."
	@UV_SKIP_WHEEL_FILENAME_CHECK=1 uv run -m pdb pac-man.py data/settings/settings.json

clean:
	@echo "Cleaning temporary files and caches..."
	@if [ -d "venv" ]; then rm -rf venv && echo " - Removed venv/"; fi
	@if [ -d ".venv" ]; then rm -rf .venv; fi
	@rm -rf dist/ build/ 2>/dev/null || true
	@find . -type d -name "__pycache__" -prune -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "pac-man*" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.lock" -delete 2>/dev/null || true
	@find . -type f -name "pac-man" -delete 2>/dev/null || true
	@echo "Cleanup complete!"

lint:
	@echo "Running flake8..."
	@UV_SKIP_WHEEL_FILENAME_CHECK=1 uv run flake8 --extend-exclude=venv/,.venv/ 
	@echo "Running mypy..."
	@UV_SKIP_WHEEL_FILENAME_CHECK=1 uv run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
	@echo "Lint complete!"

help:
	@echo ""
	@echo "$(YELLOW)$(BOLD)Pac Man $(RESET)"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "make venv		- Setup virtual environment"
	@echo "make install		- Install project dependecies"
	@echo "make run		- Run the game"
	@echo "make dist		- Create executable"
	@echo "make clean		- Clean temp files"
	@echo "make lint"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
