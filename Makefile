SHELL := /bin/bash

.PHONY: all install lint format test run clean

# Install all Python dependencies using Poetry
install:
	set -euo pipefail; \
	poetry install

# Lint all code with ruff (fail on any style or type errors)
lint:
	set -euo pipefail; \
	poetry run ruff check src tests

# Autofix all safe ruff errors (does NOT fix everything)
fix:
	set -euo pipefail; \
	poetry run ruff check --fix src tests

# Format all code in src and tests using ruff
format:
	set -euo pipefail; \
	poetry run ruff format src tests

# Run all tests with pytest
test:
	set -euo pipefail; \
	poetry run pytest tests

# Run the main evaluation in baseline mode
run:
	set -euo pipefail; \
	poetry run evaluate --mode baseline

# Run the evaluation in prompt-tuned mode
run-prompt-tuned:
	set -euo pipefail; \
	poetry run evaluate --mode prompt-tuned

# Run the evaluation in RAG-assisted mode
run-rag-assisted:
	set -euo pipefail; \
	poetry run evaluate --mode rag-assisted

# Remove virtual environment and Python cache files
clean:
	rm -rf .venv .pytest_cache __pycache__ .mypy_cache

# Install, lint, and test in one go (default if you just type 'make')
all: install lint test
