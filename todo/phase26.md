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
- Verified-complete tasks in the current tree: 26.1 (no stray `bitcoin` refs in product files — remaining hits are the intentional CHANGELOG rename notes, the `pyproject.toml` keyword, and this `todo/` plan), 26.2/26.3 (underscore sweep clean in `btx/` and `tests/`), 26.4 (`ruff check` exits 0), 26.6 (`mypy btx/` clean), 26.7 (pytest: 879 passed, coverage 87.41% ≥ 80%), 26.8 (tests for `Point`/`Tx`/extractor/scheme dispatch exist and coverage ≥ 80%), 26.10 (`btx --help` shows program name `btx`), 26.11 (`btx health` exits 0 and reports `"version": "0.4.0"`), 26.12/26.13 (both env vars work; `BITCOIN_LOG_LEVEL` emits the `DeprecationWarning`), 26.14 (`btx.BtxError` imports), 26.15 (`btx --help` lists `sign`/`verify`/`recover`/`parse-script`), 26.16 (all four subcommands' `--help` succeed), 26.17 (`TestComputeSighashDispatch` taproot test passes).
