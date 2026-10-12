#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_DIR"

echo "Syncing locked development dependencies via uv..."
uv sync --extra dev --frozen

echo "Installing site dependencies..."
(cd site && npm ci --no-audit --no-fund)

echo "Running tests..."
make test-all

echo "Done."
