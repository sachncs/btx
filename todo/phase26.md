# Phase 26 — Verification

## Goal
Confirm every phase has been completed correctly by running the full verification suite.

## Context
All checks now pass, including the ruff format check (26.5) and the Sphinx docs build (26.9).

## Remaining Tasks

### Task 26.5 — `ruff format` clean — COMPLETE
**Acceptance Criteria:**
- `uv run ruff format --check btx/ tests/` exits 0

**Current state:**
- Passes. `uv run ruff format btx/signature/extraction/helpers.py btx/transaction/parser.py` applied; `uv run ruff format --check btx/ tests/` now exits 0 (105 files already formatted).

### Task 26.9 — Sphinx docs build (per Issue M4) — COMPLETE
**Acceptance Criteria:**
- `cd docs && make html` exits 0
- `docs/build/html/index.html` exists

**Current state:**
- Passes. Added `"sphinx>=7.3.7,<9"` to the dev extras in `pyproject.toml`, installed via `uv sync --all-extras`. `docs/Makefile` default changed to `SPHINXBUILD ?= uv run sphinx-build` so the bare `make html` uses the project venv. `cd docs && make html` now exits 0 with 0 errors (68 pre-existing "duplicate object description" warnings remain). Output lands at `docs/build/html/index.html` (the Makefile's BUILDDIR is `build`; the acceptance text's `docs/_build` path was incorrect). A `Properties:` section in the `BatchResult` docstring broke docutils parsing; reworded to prose.

## Notes
- This phase is the gate. Do not commit until every task passes.
- Verified-complete tasks in the current tree include the formatting, lint,
  type-check, test, coverage, CLI, health, import, and sighash dispatch gates.
  The exact output is intentionally validated by the current `make test-all`
  run rather than copied into this historical phase note.
