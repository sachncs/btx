SHELL := /usr/bin/env bash

.PHONY: all setup venv bootstrap lint typecheck test test-verbose test-cov audit site-check site-build test-all docker-test docs clean

all: test-all

setup:
	./setup.sh

venv:
	uv sync --extra dev --frozen

bootstrap:
	uv sync --extra dev --frozen
	cd site && npm ci --no-audit --no-fund

lint:
	uv run ruff format --check btx/ tests/
	uv run ruff check btx/ tests/

typecheck:
	uv run mypy -p btx
	uv run mypy tests/ --ignore-missing-imports

test:
	uv run pytest

test-verbose:
	uv run pytest -v --tb=long

test-cov:
	uv run pytest tests/ --cov=btx --cov-report=term-missing --cov-fail-under=80

audit:
	uv run pip-audit

site-check:
	cd site && npm run check

site-build:
	cd site && npm run build
	@test -f site/dist/404.html || cp site/dist/index.html site/dist/404.html

test-all: lint typecheck test-cov audit site-check site-build

docker-test:
	docker build --tag btx-validation .
	docker run --rm btx-validation

docs:
	uv run sphinx-build -b html docs/source docs/build

clean:
	./cleanup.sh
