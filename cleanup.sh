#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_DIR"

echo "Cleaning up generated and cached artifacts..."

rm -rf .benchmarks/
rm -rf .hypothesis/
rm -f .coverage
rm -rf .mypy_cache/
rm -rf .pytest_cache/
rm -rf .ruff_cache/
rm -rf .tox/
rm -rf .eggs/
rm -rf .venv/
rm -rf btx.egg-info/
rm -rf htmlcov/
rm -rf dist/
rm -rf build/
rm -rf docs/build/
rm -f coverage.xml
rm -f .coverage.*
find . \( -name '*.cover' -o -name '*,cover' \) -delete
find . -name "*.egg" -delete
find . -name "*.pyc" -delete
find . -type d -name "__pycache__" -exec rm -rf {} +

echo "Cleanup complete."
