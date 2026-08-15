# Phase 26 — Verification

## Goal
Confirm every phase has been completed correctly by running the full verification suite.

## Context
Depends on all previous phases. If any check fails, return to the relevant phase and fix.

## Tasks

### Task 26.1 — No stray `bitcoin` references (excluding `bitcoin-cli` and `github.com/bitcoin/bips/`)
**Acceptance Criteria:**
- `grep -rE '\bbitcoin\b' . --include='*.py' --include='*.md' --include='*.toml' --include='*.yml' --include='*.json' --include='*.rst' | grep -v 'bitcoin-cli\|github.com/bitcoin/bips'` returns no matches

**Steps:**
1. Run the grep
2. Fix any hits

### Task 26.2 — No single-underscore semi-private names (per Phase 19)
**Acceptance Criteria:**
- `grep -rE '\b_[a-z][a-zA-Z]*\b' btx/ --include='*.py' | grep -v '^\s*"""\|__\|#'` returns only standard dunders and `__infinity`

**Steps:**
1. Run the grep
2. Fix any hits

### Task 26.3 — Same for tests
**Acceptance Criteria:**
- Same grep against `tests/` returns no hits

### Task 26.4 — `ruff check` clean
**Acceptance Criteria:**
- `uv run ruff check btx/ tests/` exits 0

### Task 26.5 — `ruff format` clean
**Acceptance Criteria:**
- `uv run ruff format --check btx/ tests/` exits 0

### Task 26.6 — `mypy` clean
**Acceptance Criteria:**
- `uv run mypy btx/` exits 0

### Task 26.7 — `pytest` passes with coverage ≥ 80%
**Acceptance Criteria:**
- `uv run pytest tests/ -v --cov=btx --cov-report=term-missing --cov-fail-under=80` exits 0
- TOTAL coverage ≥ 80%

**Steps:**
1. Run the command
2. Note the coverage number for the changelog

### Task 26.8 — Add tests if coverage dropped below 80%
**Acceptance Criteria:**
- New unit tests exist for:
  - `Point.negate()`, `Point.add()`, `Point.double()`, `Point.multiply()`, `Point.is_on_curve()`
  - Operator overloading: `p1 + p2`, `k * p`, `-p`
  - `Tx.serialize()`, `Tx.serialize_legacy()`, `Tx.is_opt_in_rbf()`, `Tx.sighash_*()`
  - `Tx.__len__`, `Tx.__iter__`, `Tx.to_dict()`
  - `BaseExtractor` subclasses (instance-method convention)
  - `SighashScheme` dispatch (legacy, segwit, taproot)
- Coverage now ≥ 80%

**Steps:**
1. If Task 26.7 failed on coverage, add the missing tests
2. Re-run Task 26.7

### Task 26.9 — Sphinx docs build (per Issue M4)
**Acceptance Criteria:**
- `cd docs && make html` exits 0
- `docs/_build/html/index.html` exists

**Steps:**
1. Run the build
2. Fix any broken cross-references (e.g. `:exc:`BitcoinError`` → `:exc:`BtxError``)

### Task 26.10 — `btx --help` shows new branding
**Acceptance Criteria:**
- `btx --help` shows program name as `btx`

### Task 26.11 — `btx health` works
**Acceptance Criteria:**
- `btx health` exits 0
- Output JSON contains `"version": "0.4.0"`

### Task 26.12 — New env var works
**Acceptance Criteria:**
- `BTX_LOG_LEVEL=DEBUG btx health` increases verbosity

### Task 26.13 — Old env var backward-compat (per Phase 04 / Issue M1)
**Acceptance Criteria:**
- `BITCOIN_LOG_LEVEL=DEBUG btx health` increases verbosity
- A `DeprecationWarning` is emitted to stderr

### Task 26.14 — Top-level `BtxError` import works
**Acceptance Criteria:**
- `python -c "import btx; print(btx.BtxError)"` succeeds

### Task 26.15 — Auto-completion works (per Phase 23 / F15)
**Acceptance Criteria:**
- `btx --help` lists `sign`, `verify`, `recover`, `parse-script` as subcommands

### Task 26.16 — New CLI subcommands work
**Acceptance Criteria:**
- `btx sign --help`, `btx verify --help`, `btx recover --help`, `btx parse-script --help` all succeed and show reasonable help text

### Task 26.17 — Taproot sighash dispatch works (per Phase 16 / C5)
**Acceptance Criteria:**
- A test exists that calls `compute_sighash` on a taproot script-path input and gets the expected sighash bytes
- The test passes

## End-of-Phase Verification
- All 17 tasks pass
- The codebase is in a known-good state

## Notes
- This phase is the gate. Do not commit until every task passes.